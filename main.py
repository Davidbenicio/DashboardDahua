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

# Dados iniciais padrão
DADOS_INICIAIS = [
  {
    "prefixo": "257",
    "garagem": "M.E OSASCO",
    "status": "Pendente",
    "data": "15/10/2025 10:44"
  },
  {
    "prefixo": "258",
    "garagem": "M.E OSASCO",
    "status": "Pendente",
    "data": "15/10/2025 10:44"
  },
  {
    "prefixo": "259",
    "garagem": "M.E OSASCO",
    "status": "Pendente",
    "data": "15/10/2025 10:44"
  },
  {
    "prefixo": "260",
    "garagem": "M.E OSASCO",
    "status": "Pendente",
    "data": "15/10/2025 09:59"
  },
  {
    "prefixo": "261",
    "garagem": "M.E OSASCO",
    "status": "Pendente",
    "data": "15/10/2025 09:59"
  },
  {
    "prefixo": "262",
    "garagem": "M.E OSASCO",
    "status": "Pendente",
    "data": "15/10/2025 09:59"
  },
  {
    "prefixo": "263",
    "garagem": "M.E OSASCO",
    "status": "Pendente",
    "data": "15/10/2025 10:00"
  },
  {
    "prefixo": "264",
    "garagem": "M.E OSASCO",
    "status": "Pendente",
    "data": "15/10/2025 10:00"
  },
  {
    "prefixo": "265",
    "garagem": "M.E OSASCO",
    "status": "Pendente",
    "data": "15/10/2025 10:00"
  },
  {
    "prefixo": "266",
    "garagem": "M.E OSASCO",
    "status": "Pendente",
    "data": "15/10/2025 10:00"
  },
  {
    "prefixo": "267",
    "garagem": "M.E OSASCO",
    "status": "Pendente",
    "data": "15/10/2025 10:00"
  },
  {
    "prefixo": "268",
    "garagem": "M.E OSASCO",
    "status": "Pendente",
    "data": "15/10/2025 10:00"
  },
  {
    "prefixo": "269",
    "garagem": "M.E OSASCO",
    "status": "Pendente",
    "data": "15/10/2025 10:00"
  },
  {
    "prefixo": "270",
    "garagem": "M.E OSASCO",
    "status": "Pendente",
    "data": "15/10/2025 10:00"
  },
  {
    "prefixo": "20011",
    "garagem": "M.E OSASCO",
    "status": "Pendente",
    "data": "15/10/2025 14:49"
  },
  {
    "prefixo": "20012",
    "garagem": "M.E OSASCO",
    "status": "Pendente",
    "data": "15/10/2025 10:00"
  },
  {
    "prefixo": "20013",
    "garagem": "M.E OSASCO",
    "status": "Pendente",
    "data": "15/10/2025 10:00"
  },
  {
    "prefixo": "20014",
    "garagem": "M.E OSASCO",
    "status": "Pendente",
    "data": "15/10/2025 10:01"
  },
  {
    "prefixo": "20015",
    "garagem": "M.E OSASCO",
    "status": "Pendente",
    "data": "15/10/2025 10:01"
  },
  {
    "prefixo": "20016",
    "garagem": "M.E OSASCO",
    "status": "Pendente",
    "data": "15/10/2025 10:02"
  },
  {
    "prefixo": "20017",
    "garagem": "M.E OSASCO",
    "status": "Pendente",
    "data": "15/10/2025 10:02"
  },
  {
    "prefixo": "20018",
    "garagem": "M.E OSASCO",
    "status": "Pendente",
    "data": "15/10/2025 10:02"
  },
  {
    "prefixo": "20019",
    "garagem": "M.E OSASCO",
    "status": "Pendente",
    "data": "15/10/2025 10:02"
  },
  {
    "prefixo": "20020",
    "garagem": "M.E OSASCO",
    "status": "Pendente",
    "data": "15/10/2025 10:02"
  },
  {
    "prefixo": "20021",
    "garagem": "M.E OSASCO",
    "status": "Pendente",
    "data": "15/10/2025 10:02"
  },
  {
    "prefixo": "20022",
    "garagem": "M.E OSASCO",
    "status": "Pendente",
    "data": "15/10/2025 10:02"
  },
  {
    "prefixo": "20023",
    "garagem": "M.E OSASCO",
    "status": "Pendente",
    "data": "15/10/2025 10:02"
  },
  {
    "prefixo": "20024",
    "garagem": "M.E OSASCO",
    "status": "Pendente",
    "data": "15/10/2025 10:03"
  },
  {
    "prefixo": "20025",
    "garagem": "M.E OSASCO",
    "status": "Pendente",
    "data": "15/10/2025 10:03"
  },
  {
    "prefixo": "20026",
    "garagem": "M.E OSASCO",
    "status": "Pendente",
    "data": "15/10/2025 10:03"
  },
  {
    "prefixo": "20027",
    "garagem": "M.E OSASCO",
    "status": "Pendente",
    "data": "15/10/2025 10:03"
  },
  {
    "prefixo": "20028",
    "garagem": "M.E OSASCO",
    "status": "Pendente",
    "data": "15/10/2025 10:03"
  },
  {
    "prefixo": "20029",
    "garagem": "M.E OSASCO",
    "status": "Pendente",
    "data": "15/10/2025 10:03"
  },
  {
    "prefixo": "20030",
    "garagem": "M.E OSASCO",
    "status": "Pendente",
    "data": "15/10/2025 10:03"
  },
  {
    "prefixo": "20031",
    "garagem": "M.E OSASCO",
    "status": "Pendente",
    "data": "15/10/2025 10:04"
  },
  {
    "prefixo": "20032",
    "garagem": "M.E OSASCO",
    "status": "Pendente",
    "data": "15/10/2025 10:04"
  },
  {
    "prefixo": "20033",
    "garagem": "M.E OSASCO",
    "status": "Pendente",
    "data": "15/10/2025 10:04"
  },
  {
    "prefixo": "20034",
    "garagem": "M.E OSASCO",
    "status": "Concluído",
    "data": "21/10/2025 11:08",
    "comentario": ""
  },
  {
    "prefixo": "20035",
    "garagem": "M.E OSASCO",
    "status": "Em Andamento",
    "data": "21/10/2025 11:08",
    "comentario": "Faltando instalar câmera de ré"
  },
  {
    "prefixo": "20036",
    "garagem": "M.E OSASCO",
    "status": "Em Andamento",
    "data": "21/10/2025 11:09",
    "comentario": "Faltando câmera de ré"
  },
  {
    "prefixo": "20037",
    "garagem": "M.E OSASCO",
    "status": "Em Andamento",
    "data": "21/10/2025 11:09",
    "comentario": "Faltando configuração"
  },
  {
    "prefixo": "20038",
    "garagem": "M.E OSASCO",
    "status": "Em Andamento",
    "data": "21/10/2025 11:10",
    "comentario": ""
  },
  {
    "prefixo": "20039",
    "garagem": "M.E OSASCO",
    "status": "Pendente",
    "data": "15/10/2025 10:04"
  },
  {
    "prefixo": "20040",
    "garagem": "M.E OSASCO",
    "status": "Pendente",
    "data": "15/10/2025 10:04"
  },
  {
    "prefixo": "20520",
    "garagem": "M.E SANTANA",
    "status": "Pendente",
    "data": "15/10/2025 10:05"
  },
  {
    "prefixo": "20524",
    "garagem": "M.E SANTANA",
    "status": "Pendente",
    "data": "15/10/2025 10:05"
  },
  {
    "prefixo": "20531",
    "garagem": "M.E SANTANA",
    "status": "Pendente",
    "data": "15/10/2025 10:05"
  },
  {
    "prefixo": "20532",
    "garagem": "M.E SANTANA",
    "status": "Pendente",
    "data": "15/10/2025 10:05"
  },
  {
    "prefixo": "20533",
    "garagem": "M.E SANTANA",
    "status": "Pendente",
    "data": "15/10/2025 10:05"
  },
  {
    "prefixo": "20534",
    "garagem": "M.E SANTANA",
    "status": "Pendente",
    "data": "15/10/2025 10:06"
  },
  {
    "prefixo": "20535",
    "garagem": "M.E SANTANA",
    "status": "Pendente",
    "data": "15/10/2025 10:06"
  },
  {
    "prefixo": "20536",
    "garagem": "M.E SANTANA",
    "status": "Pendente",
    "data": "15/10/2025 10:06"
  },
  {
    "prefixo": "20537",
    "garagem": "M.E SANTANA",
    "status": "Pendente",
    "data": "15/10/2025 10:06"
  },
  {
    "prefixo": "20538",
    "garagem": "M.E SANTANA",
    "status": "Pendente",
    "data": "15/10/2025 10:06"
  },
  {
    "prefixo": "20539",
    "garagem": "M.E SANTANA",
    "status": "Pendente",
    "data": "15/10/2025 10:06"
  },
  {
    "prefixo": "20540",
    "garagem": "M.E SANTANA",
    "status": "Pendente",
    "data": "15/10/2025 10:06"
  },
  {
    "prefixo": "20541",
    "garagem": "M.E SANTANA",
    "status": "Pendente",
    "data": "15/10/2025 10:06"
  },
  {
    "prefixo": "20543",
    "garagem": "M.E SANTANA",
    "status": "Pendente",
    "data": "15/10/2025 10:06"
  },
  {
    "prefixo": "20544",
    "garagem": "M.E SANTANA",
    "status": "Pendente",
    "data": "15/10/2025 10:06"
  },
  {
    "prefixo": "20545",
    "garagem": "M.E SANTANA",
    "status": "Pendente",
    "data": "15/10/2025 10:06"
  },
  {
    "prefixo": "20542",
    "garagem": "M.E SANTANA",
    "status": "Pendente",
    "data": "15/10/2025 10:07"
  }
]

def inicializar_arquivo():
    """Inicializa o arquivo com dados padrão se não existir"""
    try:
        if not os.path.exists(DATA_FILE):
            print("📁 Criando arquivo veiculos.json com dados iniciais...")
            with file_lock:
                with open(DATA_FILE, 'w', encoding='utf-8') as f:
                    json.dump(DADOS_INICIAIS, f, ensure_ascii=False, indent=2)
            return True
        return True
    except Exception as e:
        print(f"❌ Erro ao inicializar arquivo: {e}")
        return False

def carregar_dados():
    """Carrega os dados do arquivo JSON"""
    try:
        # Garante que o arquivo existe
        inicializar_arquivo()
        
        with file_lock:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                dados = json.load(f)
                print(f"📊 Dados carregados: {len(dados)} veículos")
                return dados
    except Exception as e:
        print(f"❌ Erro ao carregar dados: {e}")
        # Retorna dados iniciais em caso de erro
        return DADOS_INICIAIS

def salvar_dados(veiculos):
    """Salva os dados no arquivo JSON"""
    try:
        with file_lock:
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(veiculos, f, ensure_ascii=False, indent=2)
            print(f"💾 Dados salvos: {len(veiculos)} veículos")
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

@app.route('/debug')
def debug():
    """Endpoint para debug"""
    info = {
        'diretorio_atual': os.getcwd(),
        'arquivos': os.listdir('.'),
        'existe_veiculos_json': os.path.exists(DATA_FILE),
        'tamanho_veiculos_json': os.path.getsize(DATA_FILE) if os.path.exists(DATA_FILE) else 0,
        'dados_carregados': len(carregar_dados())
    }
    return jsonify(info)

@app.route('/resetar-dados', methods=['POST'])
def resetar_dados():
    """Rota para resetar dados para os iniciais"""
    try:
        salvar_dados(DADOS_INICIAIS)
        return redirect(url_for('dashboard'))
    except Exception as e:
        return f"Erro ao resetar dados: {e}", 500

def get_port():
    return int(os.environ.get('PORT', 5000))

if __name__ == '__main__':
    # Inicializa o arquivo ao iniciar o servidor
    inicializar_arquivo()
    port = get_port()
    print(f"🚀 Iniciando servidor Flask na porta {port}...")
    print(f"📁 Diretório atual: {os.getcwd()}")
    print(f"📁 Arquivos no diretório: {os.listdir('.')}")
    app.run(host='0.0.0.0', port=port, debug=False)
