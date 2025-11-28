# Arquivo: model.py
import pandas as pd
import queue
from database import RepositorioSensor

class GerenciadorDados:
    def __init__(self):
        self.fila_entrada = queue.Queue()
        # Adicionamos 'Luminosidade' ao DataFrame
        self.historico = pd.DataFrame(columns=['Tempo', 'Temperatura', 'Umidade', 'Luminosidade', 'Bomba', 'Fan', 'Luz_Painel'])
        self.db = RepositorioSensor()

    def receber_dado(self, payload_json):
        self.fila_entrada.put(payload_json)

    def processar_fila(self):
        mudou_algo = False
        while not self.fila_entrada.empty():
            payload = self.fila_entrada.get()
            
            temp = payload.get('temp', 0.0)
            hum = payload.get('hum', 0.0)
            lum = payload.get('luminosidade', 0) # <--- Lê valor novo
            
            st_bomba = payload.get('bomba', False)
            st_fan = payload.get('fan', False)
            st_luz = payload.get('luz_painel', False)

            nova_linha = {
                'Tempo': pd.Timestamp.now(),
                'Temperatura': temp,
                'Umidade': hum,
                'Luminosidade': lum, # <--- Salva na RAM
                'Bomba': st_bomba,
                'Fan': st_fan,
                'Luz_Painel': st_luz
            }
            self.historico = pd.concat([self.historico, pd.DataFrame([nova_linha])], ignore_index=True)
            
            # Salva no Banco com o novo campo
            self.db.salvar_leitura(temp, hum, lum, st_bomba, st_fan, st_luz)

            mudou_algo = True
            
        if len(self.historico) > 50:
            self.historico = self.historico.iloc[1:]
            
        return mudou_algo
    
    def consultar_historico(self, inicio, fim):
        return self.db.buscar_historico(inicio, fim)