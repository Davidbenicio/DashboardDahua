from flask import Flask, render_template, request, redirect, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)

# Funções para manipular dados
def carregar_dados():
    try:
        with open('veiculos.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def salvar_dados(veiculos):
    with open('veiculos.json', 'w', encoding='utf-8') as f:
        json.dump(veiculos, f, ensure_ascii=False, indent=2)

def adicionar_veiculo(prefixo, garagem, status, comentario=""):
    veiculos = carregar_dados()
    
    if any(v['prefixo'] == prefixo for v in veiculos):
        return False
    
    novo_veiculo = {
        'prefixo': prefixo,
        'garagem': garagem,
        'status': status,
        'comentario': comentario,
        'data': datetime.now().strftime('%d/%m/%Y %H:%M')
    }
    
    veiculos.append(novo_veiculo)
    salvar_dados(veiculos)
    return True

def atualizar_status(prefixo, novo_status):
    veiculos = carregar_dados()
    for veiculo in veiculos:
        if veiculo['prefixo'] == prefixo:
            veiculo['status'] = novo_status
            veiculo['data'] = datetime.now().strftime('%d/%m/%Y %H:%M')
            break
    salvar_dados(veiculos)

def atualizar_garagem(prefixo, nova_garagem):
    veiculos = carregar_dados()
    for veiculo in veiculos:
        if veiculo['prefixo'] == prefixo:
            veiculo['garagem'] = nova_garagem
            veiculo['data'] = datetime.now().strftime('%d/%m/%Y %H:%M')
            break
    salvar_dados(veiculos)

def atualizar_comentario(prefixo, novo_comentario):
    veiculos = carregar_dados()
    for veiculo in veiculos:
        if veiculo['prefixo'] == prefixo:
            veiculo['comentario'] = novo_comentario
            veiculo['data'] = datetime.now().strftime('%d/%m/%Y %H:%M')
            break
    salvar_dados(veiculos)

def excluir_veiculo(prefixo):
    veiculos = carregar_dados()
    veiculos = [v for v in veiculos if v['prefixo'] != prefixo]
    salvar_dados(veiculos)

# Rotas
@app.route('/')
def index():
    veiculos = carregar_dados()
    
    total = len(veiculos)
    concluidos = len([v for v in veiculos if v['status'] == 'Concluído'])
    andamento = len([v for v in veiculos if v['status'] == 'Em Andamento'])
    pendentes = len([v for v in veiculos if v['status'] == 'Pendente'])
    percentual = (concluidos / total * 100) if total > 0 else 0
    
    # Agrupa por garagem
    garagens = {
        'M.E OSASCO': [],
        'M.E SANTANA': [], 
        'MEGACAM OSASCO': []
    }
    
    for veiculo in veiculos:
        if veiculo['garagem'] in garagens:
            garagens[veiculo['garagem']].append(veiculo)
    
    return render_template('index.html', 
                         veiculos=veiculos,
                         garagens=garagens,
                         total=total,
                         concluidos=concluidos,
                         andamento=andamento,
                         pendentes=pendentes,
                         percentual=percentual,
                         agora=datetime.now())

@app.route('/adicionar', methods=['POST'])
def adicionar():
    prefixo = request.form.get('prefixo', '')
    garagem = request.form.get('garagem', '')
    status = request.form.get('status', '')
    comentario = request.form.get('comentario', '')
    
    if prefixo and garagem and status:
        adicionar_veiculo(prefixo, garagem, status, comentario)
    
    return redirect('/')

@app.route('/atualizar', methods=['POST'])
def atualizar():
    prefixo = request.form.get('prefixo', '')
    novo_status = request.form.get('status', '')
    nova_garagem = request.form.get('garagem', '')
    novo_comentario = request.form.get('comentario', '')
    
    if prefixo:
        if novo_status:
            atualizar_status(prefixo, novo_status)
        if nova_garagem:
            atualizar_garagem(prefixo, nova_garagem)
        if novo_comentario is not None:
            atualizar_comentario(prefixo, novo_comentario)
    
    return redirect('/')

@app.route('/excluir', methods=['POST'])
def excluir():
    prefixo = request.form.get('prefixo', '')
    
    if prefixo:
        excluir_veiculo(prefixo)
    
    return redirect('/')

@app.route('/dados')
def dados():
    veiculos = carregar_dados()
    return jsonify(veiculos)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8001))
    app.run(host='0.0.0.0', port=port, debug=True)