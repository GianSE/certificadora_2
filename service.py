import paho.mqtt.client as mqtt
import json
# IMPORTAÇÃO NOVA
import config

class ServicoMQTT:
    def __init__(self, gerenciador_dados):
        self.dados = gerenciador_dados
        # USA AS VARIÁVEIS DO CONFIG
        self.broker = config.MQTT_BROKER
        self.port = config.MQTT_PORT
        self.topico = config.MQTT_TOPIC
        
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_message = self._ao_receber_mensagem

    def _ao_receber_mensagem(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
            self.dados.receber_dado(payload)
        except Exception as e:
            print(f"Erro: {e}")

    def iniciar(self):
        print(f"Conectando ao broker {self.broker}...")
        self.client.connect(self.broker, self.port, 60)
        self.client.subscribe(self.topico)
        self.client.loop_start()