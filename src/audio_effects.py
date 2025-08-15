
import numpy as np
from pydub.effects import normalize
from scipy.signal import butter, lfilter
from pydub import AudioSegment

def filter_band(audio, low_freq, high_freq):
    """Filtra o áudio para obter apenas a banda de frequência especificada usando scipy.signal"""
    arr = np.array(audio.get_array_of_samples()).astype(np.float32)
    sr = audio.frame_rate
    # Design bandpass filter
    nyq = 0.5 * sr
    low = low_freq / nyq
    high = high_freq / nyq
    b, a = butter(N=4, Wn=[low, high], btype='band')
    arr_filt = lfilter(b, a, arr)
    arr_filt = np.clip(arr_filt, -32768, 32767)
    return audio._spawn(arr_filt.astype(np.int16).tobytes())

def audio_eq_boost(audio, low_freq, high_freq, gain_db):
    """Aplica um boost de EQ em uma banda de frequência específica usando scipy.signal"""
    arr_orig = np.array(audio.get_array_of_samples()).astype(np.float32)
    arr_band = np.array(filter_band(audio, low_freq, high_freq).get_array_of_samples()).astype(np.float32)
    arr_band *= 10 ** (gain_db / 20)
    arr_out = arr_orig + arr_band
    arr_out = np.clip(arr_out, -32768, 32767)
    return audio._spawn(arr_out.astype(np.int16).tobytes())

def audio_eq_cut(audio, low_freq, high_freq, cut_db):
    """Corta uma banda de frequência específica usando scipy.signal"""
    arr_orig = np.array(audio.get_array_of_samples()).astype(np.float32)
    sr = audio.frame_rate
    # Low part
    nyq = 0.5 * sr
    low = low_freq / nyq
    b_low, a_low = butter(N=4, Wn=low, btype='low')
    arr_low = lfilter(b_low, a_low, arr_orig)
    # High part
    high = high_freq / nyq
    b_high, a_high = butter(N=4, Wn=high, btype='high')
    arr_high = lfilter(b_high, a_high, arr_orig)
    # Mid band
    arr_mid = np.array(filter_band(audio, low_freq, high_freq).get_array_of_samples()).astype(np.float32)
    arr_mid *= 10 ** (-cut_db / 20)
    arr_out = arr_low + arr_mid + arr_high
    arr_out = np.clip(arr_out, -32768, 32767)
    return audio._spawn(arr_out.astype(np.int16).tobytes())

def enhance_speech(audio):
    """Aprimora o áudio de voz com filtros de frequência e EQ usando scipy.signal"""
    # Filtro passa-alta para remover frequências abaixo de 80Hz
    arr = np.array(audio.get_array_of_samples()).astype(np.float32)
    sr = audio.frame_rate
    nyq = 0.5 * sr
    hp = 80 / nyq
    b, a = butter(N=4, Wn=hp, btype='high')
    arr_hp = lfilter(b, a, arr)
    audio = audio._spawn(arr_hp.astype(np.int16).tobytes())
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
    arr_orig = np.array(audio.get_array_of_samples()).astype(np.float32)
    audio_low = low_pass_filter(audio, 250)
    arr_low = np.array(audio_low.get_array_of_samples()).astype(np.float32)
    audio_mid = filter_band(audio, 250, 5000)
    arr_mid = np.array(audio_mid.get_array_of_samples()).astype(np.float32)
    audio_high = high_pass_filter(audio, 5000)
    arr_high = np.array(audio_high.get_array_of_samples()).astype(np.float32)

    # Compressão mais leve para graves
    if audio_low.max_dBFS > -20:
        reduction = (-20 - audio_low.max_dBFS) * 0.6  # Ratio ~2.5:1
        arr_low *= 10 ** (reduction / 20)
        arr_low *= 10 ** (min(6, abs(reduction) * 0.5) / 20)

    # Compressão mais forte para médias (onde está a voz)
    if audio_mid.max_dBFS > -18:
        reduction = (-18 - audio_mid.max_dBFS) * 0.75  # Ratio ~4:1
        arr_mid *= 10 ** (reduction / 20)
        arr_mid *= 10 ** (min(8, abs(reduction) * 0.8) / 20)

    # Compressão média para agudos
    if audio_high.max_dBFS > -22:
        reduction = (-22 - audio_high.max_dBFS) * 0.7  # Ratio ~3:1
        arr_high *= 10 ** (reduction / 20)
        arr_high *= 10 ** (min(5, abs(reduction) * 0.6) / 20)

    # Recombinam as bandas
    arr_out = arr_low + arr_mid + arr_high
    arr_out = np.clip(arr_out, -32768, 32767)
    return audio._spawn(arr_out.astype(np.int16).tobytes())

def deess(audio):
    """Remove sibilância excessiva do áudio de voz"""
    # Extrai a banda de frequência de sibilância (aproximadamente 5-9kHz)
    arr_orig = np.array(audio.get_array_of_samples()).astype(np.float32)
    sibilance_band = filter_band(audio, 5000, 9000)
    arr_sib = np.array(sibilance_band.get_array_of_samples()).astype(np.float32)
    threshold = -25
    if sibilance_band.max_dBFS > threshold:
        reduction = (sibilance_band.max_dBFS - threshold) * 0.8
        arr_sib *= 10 ** (-reduction / 20)
    low_part = low_pass_filter(audio, 5000)
    arr_low = np.array(low_part.get_array_of_samples()).astype(np.float32)
    high_part = high_pass_filter(audio, 9000)
    arr_high = np.array(high_part.get_array_of_samples()).astype(np.float32)
    arr_out = arr_low + arr_sib + arr_high
    arr_out = np.clip(arr_out, -32768, 32767)
    return audio._spawn(arr_out.astype(np.int16).tobytes())
