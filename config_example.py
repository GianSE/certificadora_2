# Arquivo de Exemplo - Renomeie para config.py
# --- BANCO DE DADOS (MariaDB) ---
DB_HOST = "localhost"
DB_PORT = 3306           # Porta padrão
DB_USER = "root"         # Seu usuário (geralmente 'root' no XAMPP)
DB_PASS = "senha"             # Sua senha (deixe vazio "" se não tiver)
DB_NAME = "database"

MQTT_BROKER = "test.mosquitto.org"
MQTT_PORT = 1883
MQTT_TOPIC = "seu_nome/projeto/sensor"
FLASK_HOST = "0.0.0.0"
FLASK_PORT = 5000
FLASK_DEBUG = True