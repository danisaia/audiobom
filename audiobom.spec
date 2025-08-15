# -*- mode: python ; coding: utf-8 -*-

import os
import sys
import zlib

# Usa o diretório atual em vez de __file__, que pode não estar definido
project_dir = os.getcwd()

# Cria as pastas necessárias se não existirem
for folder in ['brutos', 'tratados']:
    folder_path = os.path.join(project_dir, folder)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    # Cria um arquivo .gitkeep vazio se necessário
    gitkeep_path = os.path.join(folder_path, '.gitkeep')
    if not os.path.exists(gitkeep_path):
        with open(gitkeep_path, 'w') as f:
            pass
    
    print(f"Created/verified directory: {folder_path} with .gitkeep file")

block_cipher = None

# Define o caminho absoluto para o ícone
icon_path = os.path.join(project_dir, 'audiobom.ico')
icon_exists = os.path.exists(icon_path)
if icon_exists:
    print(f"Ícone encontrado em: {icon_path}")
else:
    print("Ícone não encontrado!")

a = Analysis(
    ['audiobom.py'],
    pathex=[],
    binaries=[
        # Adiciona explicitamente os binários do FFmpeg
        ('ffmpeg/bin/ffmpeg.exe', 'ffmpeg/bin'),
        ('ffmpeg/bin/ffprobe.exe', 'ffmpeg/bin'),
    ],
    datas=[
        ('src', 'src'),  # Inclui todo o pacote src
        ('ffmpeg/LICENSE.txt', 'ffmpeg'),  # Licença do FFmpeg
        # Garantimos que essas pastas existam e sejam incluídas
        ('brutos/.gitkeep', 'brutos'), 
        ('tratados/.gitkeep', 'tratados'),
        ('audiobom.ico', '.'),  # Incluir o ícone nos dados
        ('README.md', '.'),     # Inclui o README.md
        ('MANUAL.txt', '.'),    # Inclui o MANUAL.txt
    ],
    hiddenimports=[
        'numpy',
        'pydub',
        'pyloudnorm',
        'tqdm',
        'pygame',
        'urllib',
        'urllib.request',
        'json',
        'threading',
        'warnings',
        'datetime',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Numpy - mantenha apenas o essencial
        'numpy.f2py', 'numpy.matrixlib', 'numpy.polynomial', 'numpy.random',
        'numpy.testing', 'numpy.tests', 'numpy.typing', 'numpy.distutils',
        
        # Scipy - remova completamente, já que não é importado
        'scipy', 'scipy.*',
        
        # PyGame - mantenha apenas pygame.mixer que é o único usado
        'pygame.__pyinstaller', 'pygame._camera*', 'pygame._freetype', 
        'pygame._sdl2', 'pygame._sprite', 'pygame.camera', 'pygame.display',
        'pygame.draw', 'pygame.event', 'pygame.examples', 'pygame.font',
        'pygame.freetype', 'pygame.image', 'pygame.joystick', 'pygame.key',
        'pygame.locals', 'pygame.mask', 'pygame.midi', 'pygame.mixer_music',
        'pygame.sprite', 'pygame.surface', 'pygame.tests', 'pygame.time',
        
        # Multiprocessing - remova completamente
        'multiprocessing', 'multiprocessing.*',
        
        # Setuptools - remova completamente
        'setuptools', 'setuptools.*',
        
        # Future - remova completamente
        'future', 'future.*',
        
        # Outros módulos padrão não utilizados
        'matplotlib', 'pandas', 'unittest', 'html', 'http',
        'distutils', 'lib2to3', 'pydoc', 'xmlrpc', 'PIL', 
        'PySide2', 'PyQt5', 'PyQt6', 'IPython', 'notebook', 'tcl', 'tk',
        'sqlite3', 'test', 'curses', 'asyncio', 'argparse',
        
        # Módulos de desenvolvimento
        'pip', 'nose', 'pytest', 'coverage', 'black',
        
        # Módulos web e rede
        'urllib.robotparser', 'xml.dom.domreg', 'xml.sax.saxutils',
        'ssl', 'ftplib',
        
        # Para pydub, exclua componentes não utilizados
        'pydub.playback', 'pydub.scipy_effects', 'pydub.silence',
        
        # Para pyloudnorm, exclua submódulos não usados diretamente
        'pyloudnorm.iirfilter', 'pyloudnorm.meter', 'pyloudnorm.util',
        
        # Biblioteca json do Python apenas para partes específicas
        'json.tool', 'json.scanner',
    ],
    collect_all = [
        'pygame.mixer',
        'pyloudnorm',
        'pydub',
    ]
)

pyz = PYZ(
    a.pure, 
    a.zipped_data, 
    cipher=block_cipher,
    compress=True
)

# Configuração para distribuição em pasta (COLLECT)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='AudioBom',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # UPX ativado conforme solicitado
    console=False,  # Importante: mantenha como False
    icon=icon_path,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    upx_exclude=['vcruntime140.dll', 'python*.dll', 'VCRUNTIME140.dll'],
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,  # UPX desativado conforme solicitado
    upx_exclude=[],
    name='AudioBom',
)