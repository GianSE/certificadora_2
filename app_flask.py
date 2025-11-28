# Arquivo: app_flask.py
from flask import Flask, render_template, jsonify, request
from datetime import datetime
from model import GerenciadorDados
from service import ServicoMQTT

app = Flask(__name__)

dados = GerenciadorDados()
mqtt = ServicoMQTT(dados)
mqtt.iniciar()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/historico')
def page_historico():
    return render_template('historico.html')

@app.route('/api/dados')
def api_dados():
    dados.processar_fila()
    if not dados.historico.empty:
        ultimo = dados.historico.iloc[-1]
        return jsonify({
            "tempo": str(ultimo['Tempo'].strftime('%H:%M:%S')),
            "temperatura": float(ultimo['Temperatura']),
            "umidade": float(ultimo['Umidade']),
            "luminosidade": int(ultimo['Luminosidade']), # <--- NOVO
            "bomba": bool(ultimo['Bomba']),
            "fan": bool(ultimo['Fan']),
            "luz_painel": bool(ultimo['Luz_Painel'])
        })
    else:
        return jsonify({
            "tempo": "--", "temperatura": 0, "umidade": 0, "luminosidade": 0,
            "bomba": False, "fan": False, "luz_painel": False
        })

@app.route('/api/historico')
def api_historico():
    inicio_str = request.args.get('inicio')
    fim_str = request.args.get('fim')
    if not inicio_str or not fim_str: return jsonify([])

    try:
        dt_inicio = datetime.strptime(inicio_str, '%Y-%m-%dT%H:%M')
        dt_fim = datetime.strptime(fim_str, '%Y-%m-%dT%H:%M')
        
        lista = dados.consultar_historico(dt_inicio, dt_fim)
        
        resultado = []
        for l in lista:
            resultado.append({
                "tempo": l.data_hora.strftime('%d/%m %H:%M'),
                "temperatura": l.temperatura,
                "umidade": l.umidade,
                "luminosidade": l.luminosidade,  # <--- ADICIONADO
                "bomba": l.bomba,
                "fan": l.fan,
                "luz_painel": l.luz_painel       # <--- ADICIONADO
            })
        return jsonify(resultado)
    except Exception as e:
        print(e)
        return jsonify([])

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)