import os

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
