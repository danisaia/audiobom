import os
import sys
import platform
import zipfile
import shutil
import urllib.request
import warnings
import numpy as np
from tqdm import tqdm

# Função para verificar e configurar o FFmpeg antes de importar pydub
def setup_ffmpeg():
    """Configura o caminho do FFmpeg no PATH antes de importar pydub"""
    ffmpeg_dir = "ffmpeg/"
    
    # Define o nome do executável com base no sistema operacional
    if platform.system() == "Windows":
        ffmpeg_exe = os.path.join(ffmpeg_dir, "bin/ffmpeg.exe")
    else:
        ffmpeg_exe = os.path.join(ffmpeg_dir, "bin/ffmpeg")
    
    # Verifica se o executável do FFmpeg existe
    if os.path.exists(ffmpeg_exe):
        # Adiciona ao PATH para que a pydub possa encontrá-lo
        bin_path = os.path.abspath(os.path.join(ffmpeg_dir, "bin"))
        os.environ["PATH"] += os.pathsep + bin_path
        return True
    
    return False

# Configura o FFmpeg antes de importar pydub
setup_ffmpeg()

# Suprime o aviso específico do pydub sobre FFmpeg
warnings.filterwarnings("ignore", category=RuntimeWarning, 
                       message="Couldn't find ffmpeg or avconv - defaulting to ffmpeg, but may not work")

# Agora importamos pydub após configurar o ambiente
from pydub import AudioSegment
from pydub.effects import normalize, high_pass_filter, low_pass_filter

import pyloudnorm as pyln

def check_ffmpeg():
    """Verifica se o FFmpeg está disponível na pasta ffmpeg/"""
    ffmpeg_dir = "ffmpeg/"
    
    # Define o nome do executável com base no sistema operacional
    if platform.system() == "Windows":
        ffmpeg_exe = os.path.join(ffmpeg_dir, "bin/ffmpeg.exe")
    else:
        ffmpeg_exe = os.path.join(ffmpeg_dir, "bin/ffmpeg")
    
    # Verifica se o executável do FFmpeg existe
    if os.path.exists(ffmpeg_exe):
        # Já configurado pelo setup_ffmpeg, apenas retorna True
        return True
    
    return False

class DownloadProgressBar(tqdm):
    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)

def download_ffmpeg():
    """Baixa e instala o FFmpeg na pasta ffmpeg/"""
    ffmpeg_dir = "ffmpeg/"
    
    # Cria o diretório se não existir
    os.makedirs(ffmpeg_dir, exist_ok=True)
    
    # Define a URL de download baseado no sistema operacional
    system = platform.system()
    if system == "Windows":
        ffmpeg_url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
        zip_filename = os.path.join(ffmpeg_dir, "ffmpeg.zip")
    else:
        print("Sistema operacional não suportado para download automático do FFmpeg.")
        print("Por favor, instale o FFmpeg manualmente e coloque na pasta ffmpeg/bin/")
        return False
    
    try:
        print(f"Baixando FFmpeg de {ffmpeg_url}...")
        with DownloadProgressBar(unit='B', unit_scale=True, miniters=1, desc="FFmpeg") as t:
            urllib.request.urlretrieve(ffmpeg_url, zip_filename, reporthook=t.update_to)
        
        print("Extraindo FFmpeg...")
        with zipfile.ZipFile(zip_filename, 'r') as zip_ref:
            zip_ref.extractall(ffmpeg_dir)
        
        # Reorganiza os arquivos (no Windows, os arquivos estão em uma subpasta)
        if system == "Windows":
            extracted_dir = None
            for item in os.listdir(ffmpeg_dir):
                if os.path.isdir(os.path.join(ffmpeg_dir, item)) and item.startswith("ffmpeg"):
                    extracted_dir = os.path.join(ffmpeg_dir, item)
                    break
            
            if extracted_dir:
                # Move o conteúdo para a pasta ffmpeg/
                for item in os.listdir(extracted_dir):
                    shutil.move(os.path.join(extracted_dir, item), os.path.join(ffmpeg_dir, item))
                # Remove a pasta vazia
                shutil.rmtree(extracted_dir)
        
        # Remove o arquivo zip
        os.remove(zip_filename)
        
        print("FFmpeg baixado e instalado com sucesso!")
        return check_ffmpeg()
    
    except Exception as e:
        print(f"Erro ao baixar FFmpeg: {e}")
        return False

def list_audio_files(directory):
    """Lista todos os arquivos de áudio no diretório especificado"""
    audio_extensions = ['.mp3', '.wav', '.flac', '.ogg', '.aac', '.m4a']
    audio_files = []
    
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Pasta '{directory}' criada.")
        return []
    
    for filename in os.listdir(directory):
        if any(filename.lower().endswith(ext) for ext in audio_extensions):
            audio_files.append(filename)
    
    return sorted(audio_files)

def filter_band(audio, low_freq, high_freq):
    """Filtra o áudio para obter apenas a banda de frequência especificada"""
    # Aplica um filtro passa-alta e depois um passa-baixa para isolar a banda
    return high_pass_filter(low_pass_filter(audio, high_freq), low_freq)

def audio_eq_boost(audio, low_freq, high_freq, gain_db):
    """Aplica um boost de EQ em uma banda de frequência específica"""
    # Isola a banda de frequência desejada
    filtered = filter_band(audio, low_freq, high_freq)
    # Aplica ganho à banda isolada
    boosted = filtered.apply_gain(gain_db)
    # Combina o áudio original com a banda reforçada
    return audio.overlay(boosted)

def audio_eq_cut(audio, low_freq, high_freq, cut_db):
    """Corta uma banda de frequência específica"""
    # Obtém tudo abaixo da banda (passa-baixa)
    low_part = low_pass_filter(audio, low_freq)
    # Obtém tudo acima da banda (passa-alta)
    high_part = high_pass_filter(audio, high_freq)
    # Isola a banda que queremos atenuar
    mid_band = filter_band(audio, low_freq, high_freq)
    # Aplica a atenuação na banda
    attenuated_band = mid_band.apply_gain(-cut_db)
    # Combina as partes
    result = low_part.overlay(attenuated_band).overlay(high_part)
    return result

def enhance_speech(audio):
    """Aprimora o áudio de voz com filtros de frequência e EQ"""
    # Filtro passa-alta para remover frequências graves desnecessárias
    audio = high_pass_filter(audio, 80)  # Remove frequências abaixo de 80Hz
    
    # Aplica EQ simples para melhorar clareza da voz
    # Boost nas médias (presença de voz)
    audio = audio_eq_boost(audio, 1000, 3000, 2)
    
    # Pequeno corte nas baixas-médias para reduzir "muddy" sound
    audio = audio_eq_cut(audio, 200, 400, 1)
    
    # Pequeno boost nas altas para brilho
    audio = audio_eq_boost(audio, 5000, 8000, 1)
    
    return audio

def multiband_compression(audio):
    """Aplica compressão multibanda otimizada para voz"""
    # Parâmetros para voz - compressão mais agressiva no midrange
    audio_low = low_pass_filter(audio, 250)
    audio_mid = filter_band(audio, 250, 5000)
    audio_high = high_pass_filter(audio, 5000)
    
    # Compressão mais leve para graves
    if audio_low.max_dBFS > -20:
        reduction = (-20 - audio_low.max_dBFS) * 0.6  # Ratio ~2.5:1
        audio_low = audio_low.apply_gain(reduction)
        # Ganho de maquiagem conservador
        audio_low = audio_low.apply_gain(min(6, abs(reduction) * 0.5))
    
    # Compressão mais forte para médias (onde está a voz)
    if audio_mid.max_dBFS > -18:
        reduction = (-18 - audio_mid.max_dBFS) * 0.75  # Ratio ~4:1
        audio_mid = audio_mid.apply_gain(reduction)
        # Ganho de maquiagem mais agressivo para voz
        audio_mid = audio_mid.apply_gain(min(8, abs(reduction) * 0.8))
    
    # Compressão média para agudos
    if audio_high.max_dBFS > -22:
        reduction = (-22 - audio_high.max_dBFS) * 0.7  # Ratio ~3:1
        audio_high = audio_high.apply_gain(reduction)
        # Ganho de maquiagem moderado
        audio_high = audio_high.apply_gain(min(5, abs(reduction) * 0.6))
    
    # Recombinam as bandas
    compressed = audio_low.overlay(audio_mid).overlay(audio_high)
    
    return compressed

def deess(audio):
    """Remove sibilância excessiva do áudio de voz"""
    # Extrai a banda de frequência de sibilância (aproximadamente 5-9kHz)
    sibilance_band = filter_band(audio, 5000, 9000)
    
    # Aplica compressão forte apenas nas frequências de sibilância
    threshold = -25
    if sibilance_band.max_dBFS > threshold:
        reduction = (sibilance_band.max_dBFS - threshold) * 0.8  # Ratio muito alto ~5:1
        sibilance_band = sibilance_band.apply_gain(-reduction)
    
    # Obtém o áudio original sem a banda de sibilância
    low_part = low_pass_filter(audio, 5000)
    high_part = high_pass_filter(audio, 9000)
    
    # Combina o áudio sem sibilância com a banda de sibilância comprimida
    deessed_audio = low_part.overlay(sibilance_band).overlay(high_part)
    
    return deessed_audio

def normalize_loudness(audio, target_lufs=-16, silent=False):
    """Normaliza o loudness para o padrão de broadcast (EBU R128)"""
    # Converte para numpy array para usar com pyloudnorm
    samples = np.array(audio.get_array_of_samples()).astype(float) / 32768.0  # Normaliza para float
    
    if audio.channels == 2:
        samples = samples.reshape(-1, 2)
    else:
        samples = samples.reshape(-1, 1)
    
    # Mede o loudness atual
    meter = pyln.Meter(audio.frame_rate)  # Cria um medidor
    current_loudness = meter.integrated_loudness(samples)
    
    if not silent:
        print(f"Loudness atual: {current_loudness:.1f} LUFS")
    
    # Calcula e aplica o ganho necessário
    gain = target_lufs - current_loudness
    if not silent:
        print(f"Aplicando ajuste de ganho: {gain:.1f} dB")
    audio = audio.apply_gain(gain)
    
    return audio

def dynamics_processor(audio, silent=False):
    """Processa a dinâmica da voz para reduzir a variação entre sílabas fortes e fracas"""
    if not silent:
        print("Aplicando compressão de dinâmica para voz...")
    
    # Análise inicial do áudio para determinar níveis
    avg_level = audio.dBFS
    if not silent:
        print(f"Nível médio do áudio: {avg_level:.1f} dB")
    
    # Thresholds para compressão e expansão
    high_threshold = avg_level + 6  # 6dB acima da média para compressão
    low_threshold = avg_level - 8   # 8dB abaixo da média para expansão
    
    # Parâmetros de processamento
    compress_ratio = 2.5      # Ratio moderado para compressão (sílabas fortes)
    expand_ratio = 1.5        # Ratio para expansão (sílabas fracas)
    segment_length = 50       # ms - tamanho dos segmentos para processamento granular
    
    if not silent:
        print(f"Aplicando processamento com threshold superior: {high_threshold:.1f} dB, threshold inferior: {low_threshold:.1f} dB")
    
    # Processamos o áudio em pequenos pedaços para aplicar processamento com mais controle
    segments = []
    for i in range(0, len(audio), segment_length):
        segment = audio[i:i+segment_length]
        segment_level = segment.dBFS
        
        # Pula segmentos muito silenciosos (podem ser pausas naturais)
        if segment_level < -50:
            segments.append(segment)
            continue
        
        # 1. Compressão para sílabas fortes
        if segment_level > high_threshold:
            diff = segment_level - high_threshold
            reduction = diff * (1 - 1/compress_ratio)
            segment = segment.apply_gain(-reduction)
            
            # Aplicamos um pouco de ganho de make-up para manter o volume percebido
            makeup_gain = min(reduction * 0.5, 3)  # No máximo 3dB de makeup
            segment = segment.apply_gain(makeup_gain)
        
        # 2. Expansão para sílabas fracas (novo!)
        elif segment_level < low_threshold and segment_level > -40:  # Não processamos partes muito silenciosas
            diff = low_threshold - segment_level
            boost = diff * (1 - 1/expand_ratio)
            boost = min(boost, 6)  # Limitamos o boost a 6dB para evitar artefatos
            segment = segment.apply_gain(boost)
        
        segments.append(segment)
    
    # Concatenamos todos os segmentos processados
    processed_audio = segments[0]
    for segment in segments[1:]:
        processed_audio += segment
    
    # Normalização suave para manter o volume percebido
    final_level = processed_audio.dBFS
    if abs(final_level - avg_level) > 2:
        # Trazemos o nível médio de volta para perto do nível original
        makeup_gain = avg_level - final_level
        # Limitamos o ganho para evitar distorções
        makeup_gain = max(min(makeup_gain, 4), -4)
        processed_audio = processed_audio.apply_gain(makeup_gain)
        if not silent:
            print(f"Ajuste final de nível: {makeup_gain:.1f} dB")
    
    # Estatísticas finais
    if not silent:
        print(f"Dinâmica antes: {audio.max_dBFS - audio.dBFS:.1f} dB, depois: {processed_audio.max_dBFS - processed_audio.dBFS:.1f} dB")
    
    return processed_audio

def process_audio(audio_path, output_path, show_progress=True, progress_callback=None):
    """Processa o arquivo de áudio para transmissão em rádio
    
    Args:
        audio_path: Caminho para o arquivo de entrada
        output_path: Caminho para o arquivo de saída
        show_progress: Se True, mostra a barra de progresso no terminal
        progress_callback: Função de callback para atualizar o progresso na GUI
                          Formato: callback(step, total_steps, description)
    """
    import io
    from contextlib import redirect_stdout
    
    print(f"Processando: {os.path.basename(audio_path)}")
    
    # Define as etapas do processamento
    processing_steps = [
        "Carregando arquivo",
        "Aplicando configurações básicas",
        "Processando dinâmica da voz",
        "Aprimorando voz",
        "Reduzindo sibilância",
        "Aplicando compressão multibanda",
        "Normalizando loudness",
        "Limitando picos",
        "Exportando arquivo"
    ]
    
    total_steps = len(processing_steps)
    
    # Cria uma única barra de progresso simplificada se solicitado
    if show_progress:
        progress_bar = tqdm(
            total=total_steps, 
            desc=processing_steps[0],
            leave=True,
            position=0,
            ncols=100,
            bar_format="{desc:<30} |{bar}| {percentage:3.0f}%"
        )
    else:
        progress_bar = None
    
    # Notifica o callback sobre o início do processamento
    if progress_callback:
        progress_callback(0, total_steps, processing_steps[0])
        
    # Buffer para capturar saídas das funções
    log_output = io.StringIO()
    
    # Carrega o arquivo de áudio
    try:
        with redirect_stdout(log_output):
            audio = AudioSegment.from_file(audio_path)
        if progress_bar:
            progress_bar.update(1)
            progress_bar.set_description_str(f"{processing_steps[1]:<30}")
        if progress_callback:
            progress_callback(1, total_steps, processing_steps[1])
    except Exception as e:
        print(f"Erro ao carregar o arquivo: {e}")
        if progress_bar:
            progress_bar.close()
        return False
    
    # Extrai informações do arquivo original para exibir depois
    original_info = f"Original: canais={audio.channels}, taxa={audio.frame_rate}Hz, pico={audio.max_dBFS:.2f}dB"
    
    # 1. Converte para estéreo se estiver em mono
    with redirect_stdout(log_output):
        if audio.channels == 1:
            audio = audio.set_channels(2)
    
        # 2. Define taxa de amostragem para 44100 Hz
        if audio.frame_rate != 44100:
            audio = audio.set_frame_rate(44100)
    
    if progress_bar:
        progress_bar.update(1)
        progress_bar.set_description_str(f"{processing_steps[2]:<30}")
    if progress_callback:
        progress_callback(2, total_steps, processing_steps[2])
    
    # 3. Processamento de dinâmica
    with redirect_stdout(log_output):
        audio = dynamics_processor(audio, silent=False)
    if progress_bar:
        progress_bar.update(1)
        progress_bar.set_description_str(f"{processing_steps[3]:<30}")
    if progress_callback:
        progress_callback(3, total_steps, processing_steps[3])
    
    # 4. Processamento de voz
    with redirect_stdout(log_output):
        audio = enhance_speech(audio)
    if progress_bar:
        progress_bar.update(1)
        progress_bar.set_description_str(f"{processing_steps[4]:<30}")
    if progress_callback:
        progress_callback(4, total_steps, processing_steps[4])
    
    # 5. De-essing
    with redirect_stdout(log_output):
        audio = deess(audio)
    if progress_bar:
        progress_bar.update(1)
        progress_bar.set_description_str(f"{processing_steps[5]:<30}")
    if progress_callback:
        progress_callback(5, total_steps, processing_steps[5])
    
    # 6. Compressão multibanda
    with redirect_stdout(log_output):
        audio = multiband_compression(audio)
    if progress_bar:
        progress_bar.update(1)
        progress_bar.set_description_str(f"{processing_steps[6]:<30}")
    if progress_callback:
        progress_callback(6, total_steps, processing_steps[6])
    
    # 7. Normalização de loudness
    with redirect_stdout(log_output):
        audio = normalize_loudness(audio, target_lufs=-16, silent=False)
    if progress_bar:
        progress_bar.update(1)
        progress_bar.set_description_str(f"{processing_steps[7]:<30}")
    if progress_callback:
        progress_callback(7, total_steps, processing_steps[7])
    
    # 8. Limitador de pico
    peak_info = ""
    with redirect_stdout(log_output):
        if audio.max_dBFS > -6.0:
            reduction = -6.0 - audio.max_dBFS
            audio = audio.apply_gain(reduction)
            peak_info = f"Picos limitados a -6 dB (redução de {-reduction:.1f} dB)"
    
    if progress_bar:
        progress_bar.update(1)
        progress_bar.set_description_str(f"{processing_steps[8]:<30}")
    if progress_callback:
        progress_callback(8, total_steps, processing_steps[8])
    
    # Informações do arquivo processado
    processed_info = f"Processado: canais={audio.channels}, taxa={audio.frame_rate}Hz, pico={audio.max_dBFS:.2f}dB"
    
    # 9. Exportação
    with redirect_stdout(log_output):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        audio.export(output_path, format="mp3", bitrate="192k",
                    tags={"title": os.path.basename(output_path), 
                         "artist": "Audio Processor"},
                    parameters=["-q:a", "0"])
    
    if progress_bar:
        progress_bar.update(1)
        progress_bar.close()
    if progress_callback:
        progress_callback(9, total_steps, "Concluído")
    
    # Exibir informações relevantes após o processamento
    print(original_info)
    if peak_info:
        print(peak_info)
    print(processed_info)
    
    return True

def main():
    # Verifica se o FFmpeg está disponível
    if not check_ffmpeg():
        print("FFmpeg não encontrado. Tentando baixar automaticamente...")
        if not download_ffmpeg():
            print("Não foi possível baixar o FFmpeg. Por favor, instale-o manualmente.")
            print("Coloque-o na pasta 'ffmpeg/bin/' e execute o script novamente.")
            return
    
    input_dir = "brutos/"
    output_dir = "tratados/"
    
    # Cria os diretórios se não existirem
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    
    # Lista os arquivos de áudio
    audio_files = list_audio_files(input_dir)
    
    if not audio_files:
        print(f"Nenhum arquivo de áudio encontrado em '{input_dir}'")
        print("Por favor, adicione alguns arquivos de áudio e execute o script novamente.")
        return
    
    # Mostra os arquivos para o usuário
    print("\n=== PROCESSADOR DE ÁUDIO PARA RÁDIO ===")
    print(f"\nEncontrados {len(audio_files)} arquivos de áudio em '{input_dir}':")
    for idx, filename in enumerate(audio_files, 1):
        print(f"{idx}. {filename}")
    
    # Obtém a seleção do usuário
    while True:
        try:
            selection = int(input("\nDigite o número do arquivo a processar (0 para sair): "))
            if selection == 0:
                print("Saindo do programa.")
                return
            if selection < 1 or selection > len(audio_files):
                print(f"Por favor, digite um número entre 1 e {len(audio_files)}.")
                continue
            break
        except ValueError:
            print("Por favor, digite um número válido.")
    
    selected_file = audio_files[selection - 1]
    input_path = os.path.join(input_dir, selected_file)
    
    # Obtém o nome do arquivo de saída (mesmo nome, mas em outro diretório)
    filename_base = os.path.splitext(selected_file)[0]
    output_path = os.path.join(output_dir, f"{filename_base}.mp3")
    
    # Processa o áudio
    print(f"\nProcessando '{selected_file}'...")
    success = process_audio(input_path, output_path)
    
    if success:
        print("\nProcessamento concluído com sucesso!")
        print(f"Arquivo salvo em: {output_path}")
    else:
        print("\nProcessamento falhou.")

if __name__ == "__main__":
    main()