# Arquivo: model.py
import pandas as pd
import queue
from database import RepositorioSensor

class GerenciadorDados:
    def __init__(self):
        self.fila_entrada = queue.Queue()
        # Adicionamos as novas colunas no DataFrame da memória também
        self.historico = pd.DataFrame(columns=['Tempo', 'Temperatura', 'Umidade', 'Bomba', 'Fan', 'Luz'])
        self.db = RepositorioSensor()

    def receber_dado(self, payload_json):
        self.fila_entrada.put(payload_json)

    def processar_fila(self):
        mudou_algo = False
        while not self.fila_entrada.empty():
            payload = self.fila_entrada.get()
            
            # 1. Extrai dados do JSON novo (chaves do ESP32)
            # Usa .get() para evitar erro se a chave não existir
            temp = payload.get('temp', 0.0)
            hum = payload.get('hum', 0.0)
            
            # Status (Vêm como true/false do ESP32)
            st_bomba = payload.get('bomba', False)
            st_fan = payload.get('fan', False)
            st_luz = payload.get('luz', False)

            # 2. Atualiza Memória RAM
            nova_linha = {
                'Tempo': pd.Timestamp.now(),
                'Temperatura': temp,
                'Umidade': hum,
                'Bomba': st_bomba,
                'Fan': st_fan,
                'Luz': st_luz
            }
            self.historico = pd.concat([self.historico, pd.DataFrame([nova_linha])], ignore_index=True)
            
            # 3. Salva no Banco
            self.db.salvar_leitura(temp, hum, st_bomba, st_fan, st_luz)

            mudou_algo = True
            
        if len(self.historico) > 50:
            self.historico = self.historico.iloc[1:]
            
        return mudou_algo

    def consultar_historico(self, inicio, fim):
        return self.db.buscar_historico(inicio, fim)