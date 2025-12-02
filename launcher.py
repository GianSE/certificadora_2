import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
import socket
import os
import webbrowser
import time

class Launcher:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema IoT Gian - Server Manager")
        self.root.geometry("450x250") # Ajustei a altura pois tem menos botões
        
        self.processo_web = None

        # Garante que o servidor fecha ao fechar a janela
        self.root.protocol("WM_DELETE_WINDOW", self.ao_fechar)

        # 1. Descobre o IP
        self.meu_ip = self.pegar_ip_local()

        # Título
        lbl = ttk.Label(root, text="Painel de Controle IoT", font=("Arial", 16, "bold"))
        lbl.pack(pady=15)

        # --- SEÇÃO WEB (FLASK) ---
        frame_web = ttk.LabelFrame(root, text="Servidor Web (Acesso Remoto)", padding=10)
        frame_web.pack(fill=tk.X, padx=20, pady=5)

        self.btn_web = ttk.Button(frame_web, text="🌍 Iniciar Servidor Flask", command=self.alternar_servidor)
        self.btn_web.pack(fill=tk.X, pady=5)
        
        self.lbl_status = ttk.Label(frame_web, text="Status: Parado", foreground="red")
        self.lbl_status.pack()

        # Link clicável (simulado)
        self.lbl_link = ttk.Label(frame_web, text=f"http://{self.meu_ip}:5000", 
                                  font=("Consolas", 12, "underline"), foreground="blue", cursor="hand2")
        self.lbl_link.pack(pady=5)
        self.lbl_link.bind("<Button-1>", lambda e: webbrowser.open(f"http://{self.meu_ip}:5000"))

    def pegar_ip_local(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # Tenta conectar ao Google DNS (não envia dados, apenas descobre a rota)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"

    def alternar_servidor(self):
        if self.processo_web is None:
            self.iniciar_web()
        else:
            self.matar_servidor()

    def iniciar_web(self):
        if not os.path.exists("app_flask.py"):
            messagebox.showerror("Erro", "O arquivo 'app_flask.py' não foi encontrado na pasta!")
            return

        print("Iniciando Flask...")
        cmd = [sys.executable, "app_flask.py"]
        
        # Inicia o servidor em background
        # CREATE_NO_WINDOW impede que abra uma tela preta extra no Windows
        creationflags = 0
        if sys.platform == "win32":
            creationflags = subprocess.CREATE_NO_WINDOW

        self.processo_web = subprocess.Popen(cmd, creationflags=creationflags)
        
        # Atualiza Interface
        self.btn_web.config(text="🛑 Parar Servidor Flask")
        self.lbl_status.config(text="Status: Rodando...", foreground="green")
        
        # Abre o navegador após 2 segundos
        self.root.after(5000, lambda: webbrowser.open(f"http://{self.meu_ip}:5000"))

    def matar_servidor(self):
        if self.processo_web:
            print("Encerrando Flask...")
            
            # Método Cross-Platform (funciona em Windows, Linux e Mac)
            self.processo_web.terminate()
            self.processo_web = None
            
            # Atualiza Interface
            self.btn_web.config(text="🌍 Iniciar Servidor Flask")
            self.lbl_status.config(text="Status: Parado", foreground="red")

    def ao_fechar(self):
        self.matar_servidor()
        self.root.destroy()
        sys.exit()

if __name__ == "__main__":
    root = tk.Tk()
    app = Launcher(root)
    root.mainloop()