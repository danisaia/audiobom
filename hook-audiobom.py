from PyInstaller.utils.hooks import collect_submodules, collect_data_files

# Coletar apenas os submódulos específicos necessários
hiddenimports = [
    'numpy.core', 
    'pygame.mixer',
    'pyloudnorm',
    'pydub',
]

# Excluir bytecode e outros arquivos desnecessários
datas = [(d[0], d[1]) for d in collect_data_files('pyloudnorm') if not d[0].endswith('.pyc')]

# Adicionar esse hook ao excludes do spec
excludes = [
    'scipy', 
    'matplotlib',
    'pandas',
    'setuptools',
    'wheel',
    'pip',
    'future',
]
