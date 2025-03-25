import os
import io
from contextlib import redirect_stdout
from tqdm import tqdm
from pydub import AudioSegment

from .audio_effects import enhance_speech, deess, multiband_compression
from .audio_normalization import dynamics_processor, normalize_loudness

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
