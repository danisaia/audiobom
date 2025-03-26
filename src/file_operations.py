import os
import sys

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
