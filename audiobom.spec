# -*- mode: python ; coding: utf-8 -*-

import os
import sys

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
        ('ffmpeg/bin/ffplay.exe', 'ffmpeg/bin'),
    ],
    datas=[
        ('src', 'src'),  # Inclui todo o pacote src
        ('ffmpeg/LICENSE.txt', 'ffmpeg'),  # Licença do FFmpeg
        # Garantimos que essas pastas existam e sejam incluídas
        ('brutos/.gitkeep', 'brutos'), 
        ('tratados/.gitkeep', 'tratados'),
        ('audiobom.ico', '.'),  # Incluir o ícone nos dados
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
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

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
    upx=False,  # UPX desativado conforme solicitado
    console=False,  # Importante: mantenha como False
    icon=icon_path,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
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