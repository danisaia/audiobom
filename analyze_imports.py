import os
import sys
import importlib
import inspect
import pkgutil
import importlib.util
from collections import defaultdict

def check_if_module_is_used(main_file, module_name):
    """Verifica se um módulo é usado em um arquivo Python"""
    with open(main_file, 'r', encoding='utf-8') as f:
        content = f.read()
    return module_name in content

def analyze_package(package_name, used_modules=None):
    """Analisa os submódulos de um pacote"""
    if used_modules is None:
        used_modules = []
    
    try:
        # Tenta importar o pacote
        package = importlib.import_module(package_name)
        
        # Verifica se o pacote tem uma localização de arquivo (alguns módulos internos não têm)
        if hasattr(package, '__file__'):
            pkg_path = os.path.dirname(package.__file__)
            all_modules = []
            
            # Lista todos os submódulos
            for _, name, is_pkg in pkgutil.iter_modules([pkg_path]):
                full_name = f"{package_name}.{name}"
                all_modules.append((full_name, is_pkg))
                
            return package_name, all_modules, used_modules
        else:
            return package_name, [], used_modules
    except (ImportError, AttributeError):
        return package_name, [], used_modules

def analyze_imports():
    """Analisa as importações do projeto"""
    # Grandes bibliotecas para analisar
    big_packages = ['numpy', 'scipy', 'pygame', 'multiprocessing', 'setuptools', 'future', 'pyloudnorm', 'pydub']
    
    # Arquivo principal
    main_file = 'audiobom.py'
    
    # Resultado
    results = {}
    
    print(f"Analisando importações em {main_file}...")
    
    with open('unused_modules.txt', 'w', encoding='utf-8') as f:
        f.write(f"Análise de importações para {main_file}\n\n")
        
        for package_name in big_packages:
            f.write(f"\n\n{'='*50}\n{package_name.upper()} SUBMÓDULOS\n{'='*50}\n")
            
            # Verifica se o pacote básico é usado
            is_used = check_if_module_is_used(main_file, package_name)
            f.write(f"\nPacote base '{package_name}' é importado: {is_used}\n")
            
            # Analisa o pacote e seus submódulos
            _, all_modules, _ = analyze_package(package_name)
            
            if all_modules:
                f.write("\nSubmódulos disponíveis:\n")
                for module_name, is_pkg in all_modules:
                    # Verifica se o submódulo é usado
                    submod_used = check_if_module_is_used(main_file, module_name)
                    module_type = "pacote" if is_pkg else "módulo"
                    status = "USADO" if submod_used else "não usado"
                    f.write(f"  {module_name} ({module_type}): {status}\n")
                    
                f.write("\nSubmódulos potencialmente não utilizados (excluir de PyInstaller):\n")
                for module_name, is_pkg in all_modules:
                    if not check_if_module_is_used(main_file, module_name):
                        f.write(f"  {module_name}\n")
            else:
                f.write("  Não foi possível analisar submódulos automaticamente\n")
        
        # Verificação adicional para src/ files
        f.write("\n\n{'='*50}\nMÓDULOS LOCAIS\n{'='*50}\n")
        src_path = 'src'
        
        if os.path.exists(src_path) and os.path.isdir(src_path):
            f.write("\nMódulos locais em 'src/':\n")
            for filename in os.listdir(src_path):
                if filename.endswith('.py') and not filename.startswith('__'):
                    module_name = filename[:-3]  # Remove .py
                    full_name = f"src.{module_name}"
                    is_used = check_if_module_is_used(main_file, module_name)
                    status = "USADO" if is_used else "não usado"
                    f.write(f"  {full_name}: {status}\n")
    
    print(f"Análise concluída! Resultados salvos em 'unused_modules.txt'")

if __name__ == "__main__":
    analyze_imports()