from flask import Flask, render_template, jsonify
from model import GerenciadorDados
from service import ServicoMQTT
import time

app = Flask(__name__)

# --- INSTANCIAÇÃO DO SISTEMA (SINGLETON) ---
# Instanciamos o modelo e o serviço MQTT assim que o servidor sobe
dados = GerenciadorDados()
mqtt = ServicoMQTT(dados)
mqtt.iniciar()

@app.route('/')
def index():
    """Rota principal que entrega a página HTML"""
    return render_template('index.html')

@app.route('/api/dados')
def api_dados():
    """Rota API que retorna JSON para o JavaScript"""
    # Processa a fila MQTT antes de responder
    dados.processar_fila()
    
    # Se tiver dados, retorna o último. Se não, retorna zeros.
    if not dados.historico.empty:
        ultimo = dados.historico.iloc[-1]
        return jsonify({
            "tempo": str(ultimo['Tempo'].strftime('%H:%M:%S')),
            "temperatura": ultimo['Temperatura'],
            "umidade": ultimo['Umidade']
        })
    else:
        return jsonify({"tempo": "--", "temperatura": 0, "umidade": 0})

if __name__ == '__main__':
    # host='0.0.0.0' permite acesso pelo celular
    app.run(debug=True, host='0.0.0.0', port=5000)