import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from model import GerenciadorDados
from service import ServicoMQTT

class AplicacaoDesktop:
    def __init__(self, root):
        self.root = root
        self.root.title("Monitor IoT - Versão Desktop (Tkinter)")
        self.root.geometry("800x600")

        # --- 1. Instancia o Cérebro (Model e Service) ---
        self.dados = GerenciadorDados()
        self.mqtt = ServicoMQTT(self.dados)
        self.mqtt.iniciar()

        # --- 2. Configura a Interface (View) ---
        self.setup_ui()

        # --- 3. Inicia o Loop de Atualização ---
        # No Tkinter, não usamos while True, usamos .after()
        self.root.after(1000, self.atualizar_dados)

    def setup_ui(self):
        # Frame de Cima (Métricas)
        frame_metricas = ttk.Frame(self.root, padding="10")
        frame_metricas.pack(fill=tk.X)

        self.lbl_temp = ttk.Label(frame_metricas, text="Temp: -- °C", font=("Arial", 20, "bold"))
        self.lbl_temp.pack(side=tk.LEFT, padx=20)

        self.lbl_hum = ttk.Label(frame_metricas, text="Umid: -- %", font=("Arial", 20, "bold"))
        self.lbl_hum.pack(side=tk.RIGHT, padx=20)

        # Frame de Baixo (Gráfico)
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(6, 5), dpi=100)
        self.fig.tight_layout(pad=3.0)
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def atualizar_dados(self):
        # Processa a fila do MQTT
        self.dados.processar_fila()
        
        df = self.dados.historico
        if not df.empty:
            # Pega últimos dados
            ult_temp = df.iloc[-1]['Temperatura']
            ult_hum = df.iloc[-1]['Umidade']

            # Atualiza textos
            self.lbl_temp.config(text=f"Temp: {ult_temp:.1f} °C")
            self.lbl_hum.config(text=f"Umid: {ult_hum:.1f} %")

            # Atualiza Gráficos
            self.ax1.clear()
            self.ax1.plot(df['Tempo'], df['Temperatura'], 'r-o')
            self.ax1.set_ylabel('Temperatura (°C)')
            self.ax1.grid(True)

            self.ax2.clear()
            self.ax2.plot(df['Tempo'], df['Umidade'], 'b-o')
            self.ax2.set_ylabel('Umidade (%)')
            self.ax2.grid(True)

            self.canvas.draw()

        # Reageda essa função para rodar de novo em 1000ms (1 segundo)
        self.root.after(1000, self.atualizar_dados)

if __name__ == "__main__":
    root = tk.Tk()
    app = AplicacaoDesktop(root)
    root.mainloop()