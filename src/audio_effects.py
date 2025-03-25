from pydub.effects import normalize, high_pass_filter, low_pass_filter

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
