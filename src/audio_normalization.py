import numpy as np
import pyloudnorm as pyln

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
