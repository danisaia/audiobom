# audiobom.spec
block_cipher = None

a = Analysis(
    ['audiobom_gui.py'],  # Script principal
    pathex=[],
    binaries=[],
    datas=[
        ('audiobom_config.json', '.'),  # Inclui o arquivo de configuração
        ('ffmpeg/bin/*.exe', 'ffmpeg/bin'),  # Inclui os executáveis do FFmpeg
    ],
    hiddenimports=['numpy', 'pydub', 'pyloudnorm', 'tqdm'],
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

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='AudioBom',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,  # False para aplicativo sem console
    # Remova ou comente a linha do ícone
    # icon='path/to/icon.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='AudioBom',
)