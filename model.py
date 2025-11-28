# Arquivo: model.py
import pandas as pd
import queue
# Importa a nossa classe blindada
from database import RepositorioSensor

class GerenciadorDados:
    def __init__(self):
        # 1. Dados em Memória (Gráfico Tempo Real)
        # Isso SEMPRE vai funcionar, independente do banco
        self.fila_entrada = queue.Queue()
        self.historico = pd.DataFrame(columns=['Tempo', 'Temperatura', 'Umidade'])
        
        # 2. Banco de Dados
        # Instanciamos o repositório. Ele se vira para conectar ou ficar offline.
        self.db = RepositorioSensor()

    def receber_dado(self, payload_json):
        self.fila_entrada.put(payload_json)

    def processar_fila(self):
        mudou_algo = False
        while not self.fila_entrada.empty():
            payload = self.fila_entrada.get()
            
            # Dados crus
            temp = payload['temperatura']
            umid = payload['umidade']

            # A. Atualiza memória RAM (Vital para o App funcionar)
            nova_linha = {
                'Tempo': pd.Timestamp.now(),
                'Temperatura': temp,
                'Umidade': umid
            }
            self.historico = pd.concat([self.historico, pd.DataFrame([nova_linha])], ignore_index=True)
            
            # B. Tenta salvar no Banco (Opcional)
            # Se o banco estiver offline, esse método não faz nada e não trava o app.
            self.db.salvar_leitura(temp, umid)

            mudou_algo = True
            
        # Limpeza da RAM (Mantém apenas os últimos 50 para o gráfico)
        if len(self.historico) > 50:
            self.historico = self.historico.iloc[1:]
            
        return mudou_algo