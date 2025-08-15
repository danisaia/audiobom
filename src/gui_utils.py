import os
import json
import threading
import tkinter as tk
from tkinter import messagebox, filedialog
from datetime import datetime
import time

def center_window(root):
    """Centraliza a janela na tela"""
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry('{}x{}+{}+{}'.format(width, height, x, y))

def save_config(config_file, input_dir, output_dir):
    """Salva as configurações atuais em um arquivo JSON"""
    config = {
        "input_dir": input_dir,
        "output_dir": output_dir
    }
    
    try:
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Erro ao salvar configurações: {e}")

def load_config(config_file):
    """Carrega configurações salvas de um arquivo JSON"""
    input_dir = ""
    output_dir = ""

    try:
        if os.path.exists(config_file):
            with open(config_file, "r") as f:
                config = json.load(f)
            
            if "input_dir" in config and os.path.exists(config["input_dir"]):
                input_dir = config["input_dir"]
            
            if "output_dir" in config and os.path.exists(config["output_dir"]):
                output_dir = config["output_dir"]
    except Exception as e:
        print(f"Erro ao carregar configurações: {e}")
    
    return input_dir, output_dir

def browse_directory(current_dir):
    """Abre um diálogo para selecionar diretório"""
    directory = filedialog.askdirectory(initialdir=current_dir)
    if directory:
        return directory
    return current_dir

def sort_tree_column(tree, column, sort_states):
    """Ordena a coluna clicada em ordem crescente ou decrescente"""
    # Invertemos o estado de ordenação
    sort_states[column] = not sort_states[column]
    reverse = sort_states[column]
    
    # Obtém todos os itens e seus valores
    items = [(tree.set(child, column), child) for child in tree.get_children('')]
    
    # Ordenação especial para datas
    if column == "date":
        # Convertemos as datas para timestamps para ordenação
        items = [(time.mktime(datetime.strptime(item[0], "%d/%m/%Y %H:%M").timetuple()), item[1]) 
                for item in items]
    
    # Ordena os itens
    items.sort(reverse=reverse)
    
    # Reorganiza os itens na árvore
    for index, (_, child) in enumerate(items):
        tree.move(child, '', index)
