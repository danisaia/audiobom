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

    # Converte para NumPy array
    arr = np.array(audio.get_array_of_samples()).astype(np.float32)
    arr_db = 20 * np.log10(np.abs(arr) / 32768.0 + 1e-10)

    # Máscaras para regiões
    mask_silence = arr_db < -50
    mask_strong = arr_db > high_threshold
    mask_weak = (arr_db < low_threshold) & (arr_db > -40)

    # Compressão para sílabas fortes
    arr_out = arr.copy()
    if np.any(mask_strong):
        diff = arr_db[mask_strong] - high_threshold
        reduction = diff * (1 - 1/compress_ratio)
        arr_out[mask_strong] *= 10 ** (-reduction / 20)
        # Make-up gain
        makeup_gain = np.minimum(reduction * 0.5, 3)
        arr_out[mask_strong] *= 10 ** (makeup_gain / 20)

    # Expansão para sílabas fracas
    if np.any(mask_weak):
        diff = low_threshold - arr_db[mask_weak]
        boost = diff * (1 - 1/expand_ratio)
        boost = np.minimum(boost, 6)
        arr_out[mask_weak] *= 10 ** (boost / 20)

    # Silêncio permanece igual
    arr_out[mask_silence] = arr[mask_silence]

    # Clipping
    arr_out = np.clip(arr_out, -32768, 32767)

    # Cria novo AudioSegment
    processed_audio = audio._spawn(arr_out.astype(np.int16).tobytes())

    # Normalização suave para manter o volume percebido
    final_level = processed_audio.dBFS
    if abs(final_level - avg_level) > 2:
        makeup_gain = avg_level - final_level
        makeup_gain = max(min(makeup_gain, 4), -4)
        processed_audio = processed_audio.apply_gain(makeup_gain)
        if not silent:
            print(f"Ajuste final de nível: {makeup_gain:.1f} dB")

    # Estatísticas finais
    if not silent:
        print(f"Dinâmica antes: {audio.max_dBFS - audio.dBFS:.1f} dB, depois: {processed_audio.max_dBFS - processed_audio.dBFS:.1f} dB")

    return processed_audio
