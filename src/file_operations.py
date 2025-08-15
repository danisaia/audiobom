import os
import sys

def list_audio_files(directory):
    """Lista arquivos de áudio (MP3/WAV) no diretório especificado"""
    if not directory:
        return []
    if not os.path.exists(directory):
        os.makedirs(directory)
    files = [f for f in os.listdir(directory) if f.lower().endswith(('.mp3', '.wav'))]
    return files

def setup_logging():
    """Configura o sistema de log para o aplicativo"""
    import logging
    
    # Detecta se está rodando a partir do executável do PyInstaller
    if getattr(sys, 'frozen', False):
        log_path = os.path.join(os.path.dirname(sys.executable), "audiobom.log")
    else:
        log_path = "audiobom.log"
    
    # Configuração básica do logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_path, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger("AudioBom")
