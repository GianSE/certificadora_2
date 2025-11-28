import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
import socket
import os
import signal
import webbrowser  # <--- IMPORT NOVO

class Launcher:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema IoT Gian - Launcher (Flask Edition)")
        self.root.geometry("450x350")
        
        self.processo_web = None

        # Protocolo de encerramento seguro
        self.root.protocol("WM_DELETE_WINDOW", self.ao_fechar)

        # 1. Descobre o IP
        self.meu_ip = self.pegar_ip_local()

        # Título
        lbl = ttk.Label(root, text="Painel de Controle IoT", font=("Arial", 16, "bold"))
        lbl.pack(pady=15)

        # --- SEÇÃO WEB (FLASK) ---
        frame_web = ttk.LabelFrame(root, text="Acesso Remoto (Celular/Web)", padding=10)
        frame_web.pack(fill=tk.X, padx=20, pady=5)

        self.btn_web = ttk.Button(frame_web, text="🌍 Iniciar Servidor Flask (+ Navegador)", command=self.abrir_web)
        self.btn_web.pack(fill=tk.X, pady=5)
        
        lbl_info = ttk.Label(frame_web, text=f"No celular, digite:\nhttp://{self.meu_ip}:5000", 
                             font=("Consolas", 12), foreground="blue", justify="center")
        lbl_info.pack(pady=5)

        # --- SEÇÃO LOCAL (DESKTOP) ---
        frame_local = ttk.LabelFrame(root, text="Acesso Local (Desktop)", padding=10)
        frame_local.pack(fill=tk.X, padx=20, pady=10)

        btn_desk = ttk.Button(frame_local, text="💻 Abrir Interface Tkinter", command=self.abrir_desktop)
        btn_desk.pack(fill=tk.X, pady=5)

    def pegar_ip_local(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"

    def abrir_web(self):
        if self.processo_web is None:
            print("Iniciando Flask...")
            cmd = [sys.executable, "app_flask.py"]
            
            # Inicia o servidor em background
            self.processo_web = subprocess.Popen(cmd)
            self.btn_web.config(text="🛑 Parar Servidor Flask (Rodando...)")
            
            # --- A MÁGICA ACONTECE AQUI ---
            # Espera 2 segundos (2000ms) para o Flask subir e então abre o navegador
            print("Abrindo navegador...")
            url = f"http://{self.meu_ip}:5000"
            self.root.after(3000, lambda: webbrowser.open(url))
            
        else:
            self.matar_servidor()

    def matar_servidor(self):
        if self.processo_web:
            print("Encerrando Flask...")
            
            subprocess.call(['taskkill', '/F', '/T', '/PID', str(self.processo_web.pid)])
            
            self.processo_web = None
            self.btn_web.config(text="🌍 Iniciar Servidor Flask (+ Navegador)")

    def abrir_desktop(self):
        print("Iniciando Desktop App...")
        self.matar_servidor() 
        self.root.destroy()
        
        from desktop_app import AplicacaoDesktop
        novo_root = tk.Tk()
        app = AplicacaoDesktop(novo_root)
        novo_root.mainloop()

    def ao_fechar(self):
        try:
            self.matar_servidor()
        except:
            pass
        self.root.destroy()
        sys.exit()

if __name__ == "__main__":
    root = tk.Tk()
    app = Launcher(root)
    root.mainloop()