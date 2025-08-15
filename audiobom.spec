# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['audiobom.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('audiobom.ico', '.'),
        ('MANUAL.txt', '.'),
        ('README.md', '.'),
        ('ffmpeg/bin/ffmpeg.exe', 'ffmpeg'),
    ],
    hiddenimports=[
        'scipy._cyutility',
        'scipy.linalg._cythonized_array_utils',
        # Adicione outros submódulos do scipy aqui se necessário
    ],
    hookspath=['.'],  # Garante que hooks locais sejam usados
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='AudioBom',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
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
    upx=True,
    upx_exclude=[],
    name='AudioBom',
)
