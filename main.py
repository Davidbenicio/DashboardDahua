from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
import os
from datetime import datetime
from threading import Lock

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'chave-desenvolvimento')

# Lock para thread safety
file_lock = Lock()

DATA_FILE = 'veiculos.json'

def carregar_dados():
    """Carrega os dados do arquivo JSON"""
    try:
        with file_lock:
            if os.path.exists(DATA_FILE):
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # Cria arquivo vazio se não existir
                salvar_dados([])
                return []
    except Exception as e:
        print(f"❌ Erro ao carregar dados: {e}")
        return []

def salvar_dados(veiculos):
    """Salva os dados no arquivo JSON"""
    try:
        with file_lock:
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(veiculos, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"❌ Erro ao salvar dados: {e}")
        return False

@app.route('/')
def dashboard():
    """Página principal do dashboard"""
    veiculos = carregar_dados()
    
    # Estatísticas gerais
    total = len(veiculos)
    concluidos = len([v for v in veiculos if v['status'] == 'Concluído'])
    andamento = len([v for v in veiculos if v['status'] == 'Em Andamento'])
    pendentes = len([v for v in veiculos if v['status'] == 'Pendente'])
    percentual = (concluidos / total * 100) if total > 0 else 0
    
    # Agrupar por garagem
    garagens = {
        'M.E OSASCO': [],
        'M.E SANTANA': [], 
        'MEGACAM OSASCO': []
    }
    
    for veiculo in veiculos:
        if veiculo['garagem'] in garagens:
            garagens[veiculo['garagem']].append(veiculo)
    
    # Estatísticas por garagem
    stats_garagens = {}
    for garagem_nome, veiculos_garagem in garagens.items():
        total_garagem = len(veiculos_garagem)
        concluidos_garagem = len([v for v in veiculos_garagem if v['status'] == 'Concluído'])
        andamento_garagem = len([v for v in veiculos_garagem if v['status'] == 'Em Andamento'])
        pendentes_garagem = len([v for v in veiculos_garagem if v['status'] == 'Pendente'])
        percentual_garagem = (concluidos_garagem / total_garagem * 100) if total_garagem > 0 else 0
        
        stats_garagens[garagem_nome] = {
            'total': total_garagem,
            'concluidos': concluidos_garagem,
            'andamento': andamento_garagem,
            'pendentes': pendentes_garagem,
            'percentual': percentual_garagem,
            'veiculos': veiculos_garagem
        }
    
    return render_template('dashboard.html',
                         veiculos=veiculos,
                         total=total,
                         concluidos=concluidos,
                         andamento=andamento,
                         pendentes=pendentes,
                         percentual=percentual,
                         garagens=stats_garagens,
                         agora=datetime.now())

@app.route('/adicionar', methods=['POST'])
def adicionar_veiculo():
    """Adiciona um novo veículo"""
    prefixo = request.form.get('prefixo', '').strip()
    garagem = request.form.get('garagem', '').strip()
    status = request.form.get('status', '').strip()
    comentario = request.form.get('comentario', '').strip()
    
    if prefixo and garagem and status:
        veiculos = carregar_dados()
        
        # Verifica se já existe
        if any(v['prefixo'] == prefixo for v in veiculos):
            return redirect(url_for('dashboard', erro='veiculo_existente'))
        
        novo_veiculo = {
            'prefixo': prefixo,
            'garagem': garagem,
            'status': status,
            'comentario': comentario,
            'data': datetime.now().strftime('%d/%m/%Y %H:%M')
        }
        
        veiculos.append(novo_veiculo)
        salvar_dados(veiculos)
    
    return redirect(url_for('dashboard'))

@app.route('/atualizar', methods=['POST'])
def atualizar_veiculo():
    """Atualiza um veículo existente"""
    prefixo = request.form.get('prefixo', '').strip()
    novo_status = request.form.get('status', '').strip()
    nova_garagem = request.form.get('garagem', '').strip()
    novo_comentario = request.form.get('comentario', '').strip()
    
    if prefixo:
        veiculos = carregar_dados()
        atualizado = False
        
        for veiculo in veiculos:
            if veiculo['prefixo'] == prefixo:
                if novo_status:
                    veiculo['status'] = novo_status
                    atualizado = True
                if nova_garagem:
                    veiculo['garagem'] = nova_garagem
                    atualizado = True
                if novo_comentario is not None:
                    veiculo['comentario'] = novo_comentario
                    atualizado = True
                
                if atualizado:
                    veiculo['data'] = datetime.now().strftime('%d/%m/%Y %H:%M')
                break
        
        if atualizado:
            salvar_dados(veiculos)
    
    return redirect(url_for('dashboard'))

@app.route('/excluir', methods=['POST'])
def excluir_veiculo():
    """Exclui um veículo"""
    prefixo = request.form.get('prefixo', '').strip()
    
    if prefixo:
        veiculos = carregar_dados()
        veiculos = [v for v in veiculos if v['prefixo'] != prefixo]
        salvar_dados(veiculos)
    
    return redirect(url_for('dashboard'))

@app.route('/api/veiculos', methods=['GET'])
def api_veiculos():
    """API para obter dados dos veículos (para AJAX)"""
    veiculos = carregar_dados()
    return jsonify(veiculos)

@app.route('/health')
def health_check():
    """Endpoint de health check"""
    return jsonify({
        'status': 'healthy', 
        'timestamp': datetime.now().isoformat(),
        'veiculos_count': len(carregar_dados())
    })

def get_port():
    return int(os.environ.get('PORT', 5000))

if __name__ == '__main__':
    port = get_port()
    print(f"🚀 Iniciando servidor Flask na porta {port}...")
    app.run(host='0.0.0.0', port=port, debug=False)
