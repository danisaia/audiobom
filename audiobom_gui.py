import os
import json
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import warnings
import urllib.request
from datetime import datetime
import time

# Suprime os avisos específicos do pydub sobre FFmpeg
warnings.filterwarnings("ignore", category=RuntimeWarning, 
                       message="Couldn't find ffmpeg or avconv - defaulting to ffmpeg, but may not work")

# Importa o audiobom após configurar os avisos
import audiobom

class AudioBomGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AudioBom 1.0 - Processador de voz para emissoras de rádio")
        # Aumentando o tamanho inicial da janela para acomodar todos os elementos
        self.root.geometry("750x730")
        self.root.minsize(750, 730)  # Define um tamanho mínimo para a janela
        self.root.resizable(True, True)
        
        # Define o caminho do arquivo de configuração
        self.config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audiobom_config.json")
        
        # Valores padrão para diretórios
        self.input_dir = tk.StringVar(value=os.path.join(os.getcwd(), "brutos"))
        self.output_dir = tk.StringVar(value=os.path.join(os.getcwd(), "tratados"))
        
        # Carrega configurações salvas anteriormente
        self.load_config()
        
        # Ajuste para centralizar a janela na tela
        self.center_window()
        
        self.setup_ui()
        self.update_file_list()
        
        # Configura o evento de fechamento da janela
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def center_window(self):
        """Centraliza a janela na tela"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    
    def setup_ui(self):
        # Frame principal com padding adequado
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Texto informativo
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill=tk.X, pady=8)
        
        info_text = (
            "Tratamento simples e completo de áudios de VOZ (offs, sonoras, entrevistas) para serem veiculados em qualidade de rádio FM."
        )
        
        info_label = ttk.Label(info_frame, text=info_text, justify=tk.CENTER, wraplength=750, anchor="center")
        info_label.pack(fill=tk.X, padx=5, pady=5)
        
        # Adiciona um separador após o texto informativo
        separator = ttk.Separator(main_frame, orient='horizontal')
        separator.pack(fill=tk.X, pady=8)
        
        # Diretório de entrada
        input_frame = ttk.LabelFrame(main_frame, text="Pasta de áudios brutos", padding="10")
        input_frame.pack(fill=tk.X, pady=8)
        
        ttk.Entry(input_frame, textvariable=self.input_dir).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(input_frame, text="Procurar...", command=self.browse_input_dir).pack(side=tk.RIGHT, padx=5)
        
        # Lista de arquivos - altura reduzida para metade
        files_frame = ttk.LabelFrame(main_frame, text="Arquivos disponíveis", padding="10")
        files_frame.pack(fill=tk.X, pady=8)  # Mudado de fill=tk.BOTH para fill=tk.X e removido expand=True
        
        # Define uma altura fixa para a lista de arquivos (metade do tamanho original)
        list_container = ttk.Frame(files_frame, height=180)  # Altura fixa de 180 pixels
        list_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        list_container.pack_propagate(False)  # Impede que o frame seja redimensionado pelos filhos
        
        # Scrollbar para a lista de arquivos
        scrollbar = ttk.Scrollbar(list_container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview para lista de arquivos com checkbox
        self.files_tree = ttk.Treeview(
            list_container, 
            columns=("select", "filename", "date"),
            show="headings",
            yscrollcommand=scrollbar.set
        )
        self.files_tree.heading("select", text="✓", command=self.toggle_all)
        self.files_tree.heading("filename", text="Nome do arquivo", command=lambda: self.sort_column("filename", False))
        self.files_tree.heading("date", text="Data", command=lambda: self.sort_column("date", False))
        self.files_tree.column("select", width=40, anchor=tk.CENTER, stretch=False)
        self.files_tree.column("filename", width=450, anchor=tk.W)
        self.files_tree.column("date", width=150, anchor=tk.CENTER)
        self.files_tree.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.files_tree.yview)
        
        # Armazena o estado atual de ordenação das colunas
        self.sort_states = {"filename": False, "date": False}
        
        # Eventos para a árvore de arquivos
        self.files_tree.bind("<ButtonRelease-1>", self.toggle_selection)
        
        # Diretório de saída
        output_frame = ttk.LabelFrame(main_frame, text="Pasta de destino", padding="10")
        output_frame.pack(fill=tk.X, pady=8)
        
        ttk.Entry(output_frame, textvariable=self.output_dir).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(output_frame, text="Procurar...", command=self.browse_output_dir).pack(side=tk.RIGHT, padx=5)
        
        # Barra de progresso com mais espaço
        progress_frame = ttk.Frame(main_frame)
        progress_frame.pack(fill=tk.X, pady=8)
        
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
        self.progress.pack(fill=tk.X)
        
        # Status com mais espaço
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=5)
        
        self.status_var = tk.StringVar(value="Pronto")
        status_label = ttk.Label(status_frame, textvariable=self.status_var, anchor=tk.W)
        status_label.pack(fill=tk.X)
        
        # Botões centralizados e lado a lado
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=20)
        
        # Frame centralizado para os botões
        center_frame = ttk.Frame(buttons_frame)
        center_frame.pack(anchor=tk.CENTER)
        
        # Estilo personalizado para destacar o botão Executar
        style = ttk.Style()
        style.configure("Accent.TButton", font=("Arial", 10, "bold"))
        
        # Botão Executar com destaque
        execute_btn = ttk.Button(
            center_frame, 
            text="Executar", 
            command=self.process_files, 
            width=20,
            style="Accent.TButton"
        )
        execute_btn.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Botão Fechar ao lado - alterado para chamar on_close
        close_btn = ttk.Button(
            center_frame, 
            text="Fechar", 
            command=self.on_close, 
            width=20
        )
        close_btn.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Adiciona um separador antes do rodapé
        footer_separator = ttk.Separator(main_frame, orient='horizontal')
        footer_separator.pack(fill=tk.X, pady=10)
        
        # Rodapé com informações sobre o autor
        footer_frame = ttk.Frame(main_frame)
        footer_frame.pack(fill=tk.X, pady=5)
        
        footer_text = ttk.Label(
            footer_frame, 
            text="Aplicativo Python de código aberto. Programado por Daniel Ito Isaia em 2025.",
            justify=tk.CENTER,
            foreground="#666666",  # Cor de texto cinza
            font=("Arial", 8)  # Fonte pequena
        )
        footer_text.pack(anchor=tk.CENTER)
    
    def save_config(self):
        """Salva as configurações atuais em um arquivo JSON"""
        config = {
            "input_dir": self.input_dir.get(),
            "output_dir": self.output_dir.get()
        }
        
        try:
            with open(self.config_file, "w") as f:
                json.dump(config, f)
        except Exception as e:
            print(f"Erro ao salvar configurações: {e}")
    
    def load_config(self):
        """Carrega configurações salvas de um arquivo JSON"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, "r") as f:
                    config = json.load(f)
                
                if "input_dir" in config and os.path.exists(config["input_dir"]):
                    self.input_dir.set(config["input_dir"])
                
                if "output_dir" in config and os.path.exists(config["output_dir"]):
                    self.output_dir.set(config["output_dir"])
        except Exception as e:
            print(f"Erro ao carregar configurações: {e}")
    
    def on_close(self):
        """Método chamado quando o usuário fecha o programa"""
        self.save_config()
        self.root.destroy()
    
    def browse_input_dir(self):
        directory = filedialog.askdirectory(initialdir=self.input_dir.get())
        if directory:
            self.input_dir.set(directory)
            self.update_file_list()
            self.save_config()  # Salva a configuração após a alteração
    
    def browse_output_dir(self):
        directory = filedialog.askdirectory(initialdir=self.output_dir.get())
        if directory:
            self.output_dir.set(directory)
            self.save_config()  # Salva a configuração após a alteração
    
    def update_file_list(self):
        # Limpa a árvore atual
        for item in self.files_tree.get_children():
            self.files_tree.delete(item)
        
        # Lista arquivos de áudio no diretório
        audio_files = audiobom.list_audio_files(self.input_dir.get())
        
        for filename in audio_files:
            # Obtém a data de modificação do arquivo
            file_path = os.path.join(self.input_dir.get(), filename)
            mod_time = os.path.getmtime(file_path)
            date_str = datetime.fromtimestamp(mod_time).strftime("%d/%m/%Y %H:%M")
            
            # Insere o item com três colunas: seleção, nome do arquivo, data
            self.files_tree.insert("", tk.END, values=("☐", filename, date_str))
    
    def toggle_selection(self, event):
        region = self.files_tree.identify_region(event.x, event.y)
        if region == "cell":
            column = self.files_tree.identify_column(event.x)
            if column == "#1":  # Coluna de seleção
                item = self.files_tree.identify_row(event.y)
                if not item:
                    return
                    
                current_values = self.files_tree.item(item, "values")
                
                # Alterna entre marcado e desmarcado
                if current_values[0] == "☐":
                    self.files_tree.item(item, values=("☑", current_values[1], current_values[2]))
                else:
                    self.files_tree.item(item, values=("☐", current_values[1], current_values[2]))
    
    def toggle_all(self):
        """Seleciona ou desmarca todos os arquivos"""
        # Verifica se todos os itens estão marcados
        items = self.files_tree.get_children()
        if not items:
            return
            
        # Verifica se todos os itens estão marcados
        all_checked = True
        for item in items:
            values = self.files_tree.item(item, "values")
            if values[0] != "☑":
                all_checked = False
                break
        
        # Inverte o estado de todos os itens
        new_state = "☐" if all_checked else "☑"
        for item in items:
            values = self.files_tree.item(item, "values")
            self.files_tree.item(item, values=(new_state, values[1], values[2]))
    
    def sort_column(self, column, reverse):
        """Ordena a coluna clicada em ordem crescente ou decrescente"""
        # Invertemos o estado de ordenação
        self.sort_states[column] = not self.sort_states[column]
        reverse = self.sort_states[column]
        
        # Obtém todos os itens e seus valores
        items = [(self.files_tree.set(child, column), child) for child in self.files_tree.get_children('')]
        
        # Ordenação especial para datas
        if column == "date":
            # Convertemos as datas para timestamps para ordenação
            items = [(time.mktime(datetime.strptime(item[0], "%d/%m/%Y %H:%M").timetuple()), item[1]) 
                    for item in items]
        
        # Ordena os itens
        items.sort(reverse=reverse)
        
        # Reorganiza os itens na árvore
        for index, (_, child) in enumerate(items):
            self.files_tree.move(child, '', index)
    
    def process_files(self):
        selected_files = []
        for item in self.files_tree.get_children():
            values = self.files_tree.item(item, "values")
            if values[0] == "☑":
                selected_files.append(values[1])
        
        if not selected_files:
            messagebox.showinfo("Seleção", "Por favor, selecione pelo menos um arquivo para processar.")
            return
        
        # Inicia o processamento em uma thread separada para não congelar a interface
        threading.Thread(target=self._process_files_thread, args=(selected_files,), daemon=True).start()
    
    def progress_callback(self, step, total_steps, description=""):
        """Atualiza a barra de progresso da GUI com o progresso interno do processamento"""
        # Calcula a porcentagem para uma única etapa de arquivo (normalizada para o intervalo do arquivo atual)
        if total_steps > 0:
            # Obtém o progresso atual e total de arquivos da variável de instância
            current_file_idx = getattr(self, 'current_file_idx', 0)
            total_files = getattr(self, 'total_files', 1)
            
            # Calcula a porcentagem de um único arquivo do total
            single_file_percent = 100 / total_files
            
            # Calcula a porcentagem da etapa atual dentro do arquivo atual
            step_percent = (step / total_steps) * single_file_percent
            
            # Calcula a porcentagem total (arquivos anteriores + progresso atual)
            total_percent = (current_file_idx * single_file_percent) + step_percent
            
            # Atualiza a barra de progresso
            self.progress_var.set(total_percent)
            
            # Atualiza o status se uma descrição for fornecida
            if description:
                self.status_var.set(f"Processando {current_file_idx+1}/{total_files}: {description}")
            
            # Força atualização da interface
            self.root.update_idletasks()
    
    def _process_files_thread(self, selected_files):
        self.status_var.set("Verificando FFmpeg...")
        self.root.update_idletasks()
        
        # Verificação do FFmpeg foi movida para o início do programa
        # Aqui apenas continuamos o processamento normal dos arquivos
        
        # Armazena o número total de arquivos para cálculo de progresso
        self.total_files = len(selected_files)
        
        for i, filename in enumerate(selected_files):
            try:
                # Armazena o índice do arquivo atual para o callback de progresso
                self.current_file_idx = i
                
                # Atualiza status
                self.status_var.set(f"Processando {i+1}/{self.total_files}: {filename}")
                self.root.update_idletasks()
                
                # Caminhos completos
                input_path = os.path.join(self.input_dir.get(), filename)
                output_path = os.path.join(self.output_dir.get(), os.path.splitext(filename)[0] + ".mp3")
                
                # Processa o arquivo passando o callback de progresso
                audiobom.process_audio(input_path, output_path, show_progress=False, 
                                     progress_callback=self.progress_callback)
                
            except Exception as e:
                self.status_var.set(f"Erro ao processar {filename}: {str(e)}")
                self.root.update_idletasks()
        
        # Finaliza
        self.progress_var.set(100)
        self.status_var.set(f"Concluído! {self.total_files} arquivos processados.")
        messagebox.showinfo("Concluído", f"Processamento concluído com sucesso!\n{self.total_files} arquivos processados.")

if __name__ == "__main__":
    # Assegura que o diretório de trabalho seja o diretório do script
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Configura FFmpeg antes de qualquer outra importação que possa usar pydub
    audiobom.setup_ffmpeg()
    
    # Verifica dependências
    try:
        import numpy
        import pydub
        import pyloudnorm
        import tqdm
    except ImportError as e:
        tk.messagebox.showerror("Erro de dependência", 
                               f"Biblioteca necessária não encontrada: {str(e)}\n"
                               "Execute 'pip install numpy pydub pyloudnorm tqdm' para instalar as dependências.")
        exit(1)
    
    # Inicia a GUI apenas para exibir diálogos iniciais
    root = tk.Tk()
    root.withdraw()  # Esconde a janela principal temporariamente
    
    # Verifica se o FFmpeg está disponível
    if not audiobom.check_ffmpeg():
        # Obter informações sobre o tamanho do download
        ffmpeg_url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
        try:
            site = urllib.request.urlopen(ffmpeg_url)
            size = site.info().get('Content-Length')
            size_str = f"{int(size) / (1024*1024):.1f} MB" if size else "desconhecido"
        except:
            size_str = "desconhecido"
        
        message = (f"O FFmpeg não foi encontrado. Este componente é necessário para o processamento de áudio.\n\n"
                  f"Deseja fazer o download agora? (Tamanho estimado: {size_str})")
                 
        download = messagebox.askyesno("FFmpeg não encontrado", message)
        
        if download:
            # Informar ao usuário que o download está em andamento
            messagebox.showinfo("Download em andamento", 
                              "O FFmpeg será baixado agora. Uma janela de terminal mostrará "
                              "o progresso. Por favor, aguarde até que o download seja concluído.")
            
            # Fazer o download
            downloaded = audiobom.download_ffmpeg()
            
            if not downloaded:
                messagebox.showerror("Erro", "Não foi possível baixar o FFmpeg. Por favor, instale-o manualmente.")
                root.destroy()
                exit(0)
            
            messagebox.showinfo("Download Concluído", "O FFmpeg foi baixado e instalado com sucesso!")
        else:
            # Usuário optou por não fazer o download
            messagebox.showinfo("Programa Encerrado", "O programa será encerrado, pois o FFmpeg é necessário para o processamento de áudio.")
            root.destroy()
            exit(0)
    
    # Mostra a janela principal e inicia a GUI
    root.deiconify()  # Torna a janela principal visível novamente
    app = AudioBomGUI(root)
    root.mainloop()
