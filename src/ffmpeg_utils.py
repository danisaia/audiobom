import os
import sys
import platform
import zipfile
import shutil
import urllib.request
import warnings
from tqdm import tqdm

class DownloadProgressBar(tqdm):
    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)

def setup_ffmpeg():
    """Configura o caminho do FFmpeg no PATH antes de importar pydub"""
    # Detecta se está rodando a partir do executável do PyInstaller
    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
        ffmpeg_dir = os.path.join(application_path, "ffmpeg")
    else:
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
        print(f"FFmpeg configurado em: {bin_path}")
        return True
    
    print(f"FFmpeg não encontrado em: {ffmpeg_exe}")
    return False

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
