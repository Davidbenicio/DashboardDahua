import http.server
import socketserver
import json
import os
from datetime import datetime
from urllib.parse import parse_qs

class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            veiculos = self.carregar_dados()
            html = self.gerar_dashboard(veiculos)
            self.wfile.write(html.encode('utf-8'))
            
        elif self.path == '/dados':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            veiculos = self.carregar_dados()
            self.wfile.write(json.dumps(veiculos).encode('utf-8'))
            
        else:
            super().do_GET()
    
    def do_POST(self):
        if self.path == '/adicionar':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            data = parse_qs(post_data)
            
            prefixo = data.get('prefixo', [''])[0]
            garagem = data.get('garagem', [''])[0]
            status = data.get('status', [''])[0]
            comentario = data.get('comentario', [''])[0]
            
            print(f"📝 Novo veículo: {prefixo} | {garagem} | {status} | {comentario}")
            
            if prefixo and garagem and status:
                success = self.adicionar_veiculo(prefixo, garagem, status, comentario)
                if success:
                    print(f"✅ Veículo {prefixo} adicionado com sucesso!")
                else:
                    print(f"⚠️ Veículo {prefixo} já existe!")
            
            self.send_response(303)
            self.send_header('Location', '/')
            self.end_headers()
            
        elif self.path == '/atualizar':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            data = parse_qs(post_data)
            
            prefixo = data.get('prefixo', [''])[0]
            novo_status = data.get('status', [''])[0]
            nova_garagem = data.get('garagem', [''])[0]
            novo_comentario = data.get('comentario', [''])[0]
            
            if prefixo:
                if novo_status:
                    self.atualizar_status(prefixo, novo_status)
                    print(f"🔄 Status atualizado: {prefixo} -> {novo_status}")
                if nova_garagem:
                    self.atualizar_garagem(prefixo, nova_garagem)
                    print(f"🏭 Garagem atualizada: {prefixo} -> {nova_garagem}")
                if novo_comentario is not None:
                    self.atualizar_comentario(prefixo, novo_comentario)
                    print(f"📝 Comentário atualizado para o veículo {prefixo}")
            
            self.send_response(303)
            self.send_header('Location', '/')
            self.end_headers()
            
        elif self.path == '/excluir':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            data = parse_qs(post_data)
            
            prefixo = data.get('prefixo', [''])[0]
            
            if prefixo:
                self.excluir_veiculo(prefixo)
                print(f"🗑️ Veículo excluído: {prefixo}")
            
            self.send_response(303)
            self.send_header('Location', '/')
            self.end_headers()
    
    def carregar_dados(self):
        try:
            with open('veiculos.json', 'r', encoding='utf-8') as f:
                dados = json.load(f)
                print(f"📂 Dados carregados: {len(dados)} veículos")
                return dados
        except Exception as e:
            print(f"❌ Erro ao carregar: {e}")
            # Se não existe, cria dados iniciais
            dados_iniciais = []
            self.salvar_dados(dados_iniciais)
            return dados_iniciais
    
    def salvar_dados(self, veiculos):
        print(f"💾 Salvando {len(veiculos)} veículos no JSON...")
        try:
            with open('veiculos.json', 'w', encoding='utf-8') as f:
                json.dump(veiculos, f, ensure_ascii=False, indent=2)
            print("✅ Dados salvos com sucesso!")
        except Exception as e:
            print(f"❌ Erro ao salvar: {e}")
    
    def adicionar_veiculo(self, prefixo, garagem, status, comentario=""):
        veiculos = self.carregar_dados()
        
        # Verifica se já existe
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
        self.salvar_dados(veiculos)
        return True
    
    def atualizar_status(self, prefixo, novo_status):
        veiculos = self.carregar_dados()
        
        for veiculo in veiculos:
            if veiculo['prefixo'] == prefixo:
                veiculo['status'] = novo_status
                veiculo['data'] = datetime.now().strftime('%d/%m/%Y %H:%M')
                break
        
        self.salvar_dados(veiculos)
    
    def atualizar_garagem(self, prefixo, nova_garagem):
        veiculos = self.carregar_dados()
        
        for veiculo in veiculos:
            if veiculo['prefixo'] == prefixo:
                veiculo['garagem'] = nova_garagem
                veiculo['data'] = datetime.now().strftime('%d/%m/%Y %H:%M')
                break
        
        self.salvar_dados(veiculos)
    
    def atualizar_comentario(self, prefixo, novo_comentario):
        veiculos = self.carregar_dados()
        
        for veiculo in veiculos:
            if veiculo['prefixo'] == prefixo:
                veiculo['comentario'] = novo_comentario
                veiculo['data'] = datetime.now().strftime('%d/%m/%Y %H:%M')
                break
        
        self.salvar_dados(veiculos)
    
    def excluir_veiculo(self, prefixo):
        veiculos = self.carregar_dados()
        veiculos = [v for v in veiculos if v['prefixo'] != prefixo]
        self.salvar_dados(veiculos)
    
    def gerar_dashboard(self, veiculos):
        # HTML COMPLETO com dados injetados
        total = len(veiculos)
        concluidos = len([v for v in veiculos if v['status'] == 'Concluído'])
        andamento = len([v for v in veiculos if v['status'] == 'Em Andamento'])
        pendentes = len([v for v in veiculos if v['status'] == 'Pendente'])
        percentual = (concluidos / total * 100) if total > 0 else 0
        
        print(f"📊 Estatísticas: Total={total}, Concluídos={concluidos}, Progresso={percentual:.1f}%")
        
        # Agrupa por garagem
        garagens = {
            'M.E OSASCO': [],
            'M.E SANTANA': [], 
            'MEGACAM OSASCO': []
        }
        
        for veiculo in veiculos:
            if veiculo['garagem'] in garagens:
                garagens[veiculo['garagem']].append(veiculo)
        
        # GERA HTML COMPLETO
        html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard Instalações - Frota COMPARTILHADA</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        /* TODO O CSS ORIGINAL AQUI */
        :root {{
            --cinza-escuro: #1a202c;
            --cinza-medio: #2d3748;
            --cinza-claro: #4a5568;
            --cinza-mais-claro: #718096;
            --cinza-bem-claro: #a0aec0;
            --cinza-super-claro: #edf2f7;
            --cinza-ultra-claro: #f7fafc;
            
            --verde: #38a169;
            --laranja: #dd6b20;
            --vermelho: #e53e3e;
            --azul: #3182ce;
            --roxo: #805ad5;
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif;
            background: linear-gradient(135deg, var(--cinza-escuro) 0%, var(--cinza-medio) 100%);
            min-height: 100vh;
            color: var(--cinza-ultra-claro);
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            background: rgba(45, 55, 72, 0.9);
            backdrop-filter: blur(20px);
            padding: 2.5rem;
            border-radius: 20px;
            box-shadow: 0 25px 50px rgba(0, 0, 0, 0.3);
            margin-bottom: 2rem;
            text-align: center;
            border: 1px solid rgba(255, 255, 255, 0.1);
            position: relative;
            overflow: hidden;
        }}
        
        .header::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, var(--azul), var(--roxo));
        }}
        
        .header h1 {{
            color: var(--cinza-ultra-claro);
            font-size: 2.8rem;
            margin-bottom: 0.5rem;
            font-weight: 800;
            letter-spacing: -0.5px;
        }}
        
        .header p {{
            color: var(--cinza-bem-claro);
            font-size: 1.2rem;
            opacity: 0.9;
            font-weight: 500;
        }}
        
        .timestamp {{
            color: var(--cinza-bem-claro);
            font-size: 0.9rem;
            font-weight: 500;
            margin-top: 1rem;
        }}
        
        .main-grid {{
            display: grid;
            grid-template-columns: 380px 1fr;
            gap: 2rem;
            align-items: start;
        }}
        
        @media (max-width: 1200px) {{
            .main-grid {{
                grid-template-columns: 1fr;
            }}
        }}
        
        .sidebar {{
            background: rgba(45, 55, 72, 0.9);
            backdrop-filter: blur(20px);
            padding: 2rem;
            border-radius: 20px;
            box-shadow: 0 25px 50px rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(255, 255, 255, 0.1);
            position: sticky;
            top: 20px;
        }}
        
        .content {{
            display: flex;
            flex-direction: column;
            gap: 2rem;
        }}
        
        .form-container {{
            background: rgba(45, 55, 72, 0.9);
            backdrop-filter: blur(20px);
            padding: 2rem;
            border-radius: 20px;
            box-shadow: 0 25px 50px rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }}
        
        .form-title {{
            color: var(--cinza-ultra-claro);
            margin-bottom: 1.5rem;
            font-size: 1.4rem;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }}
        
        .form-group {{
            margin-bottom: 1.5rem;
        }}
        
        .form-label {{
            display: block;
            margin-bottom: 0.75rem;
            color: var(--cinza-bem-claro);
            font-weight: 600;
            font-size: 0.95rem;
        }}
        
        .form-input, .form-select {{
            width: 100%;
            padding: 1rem 1.25rem;
            border: 2px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            font-size: 1rem;
            transition: all 0.3s ease;
            background: rgba(26, 32, 44, 0.8);
            color: var(--cinza-ultra-claro);
            font-weight: 500;
        }}
        
        .form-input::placeholder {{
            color: var(--cinza-mais-claro);
        }}
        
        .form-input:focus, .form-select:focus {{
            outline: none;
            border-color: var(--azul);
            box-shadow: 0 0 0 3px rgba(49, 130, 206, 0.2);
            background: rgba(26, 32, 44, 0.9);
        }}
        
        .btn {{
            width: 100%;
            background: linear-gradient(135deg, var(--azul), var(--roxo));
            color: white;
            padding: 1.125rem 1.5rem;
            border: none;
            border-radius: 12px;
            font-size: 1.05rem;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.75rem;
            letter-spacing: 0.5px;
        }}
        
        .btn:hover {{
            transform: translateY(-3px);
            box-shadow: 0 15px 30px rgba(0, 0, 0, 0.4);
        }}
        
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 1.5rem;
            margin-bottom: 1rem;
        }}
        
        .metric-card {{
            background: rgba(45, 55, 72, 0.9);
            backdrop-filter: blur(20px);
            padding: 2rem;
            border-radius: 16px;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.3);
            text-align: center;
            border: 1px solid rgba(255, 255, 255, 0.1);
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
            cursor: pointer;
        }}
        
        .metric-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: var(--cinza-claro);
        }}
        
        .metric-card:hover {{
            transform: translateY(-8px);
            box-shadow: 0 25px 50px rgba(0, 0, 0, 0.4);
        }}
        
        .metric-card.active {{
            border: 2px solid var(--roxo);
            transform: translateY(-8px);
        }}
        
        .metric-icon {{
            font-size: 2.8rem;
            margin-bottom: 1.25rem;
            opacity: 0.9;
        }}
        
        .metric-number {{
            font-size: 3rem;
            font-weight: 800;
            margin-bottom: 0.5rem;
            line-height: 1;
            background: linear-gradient(135deg, var(--cinza-ultra-claro), var(--cinza-bem-claro));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        
        .metric-label {{
            color: var(--cinza-bem-claro);
            font-size: 0.95rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .garagem-section {{
            background: rgba(45, 55, 72, 0.9);
            backdrop-filter: blur(20px);
            padding: 2.5rem;
            border-radius: 20px;
            box-shadow: 0 25px 50px rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(255, 255, 255, 0.1);
            position: relative;
            overflow: hidden;
        }}
        
        .garagem-section::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, var(--azul), var(--roxo));
        }}
        
        .garagem-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2rem;
            padding-bottom: 1.5rem;
            border-bottom: 2px solid rgba(255, 255, 255, 0.1);
        }}
        
        .garagem-title {{
            color: var(--cinza-ultra-claro);
            font-size: 1.6rem;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 1rem;
        }}
        
        .garagem-stats {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 1.25rem;
            margin-bottom: 2rem;
        }}
        
        .stat {{
            background: rgba(26, 32, 44, 0.6);
            padding: 1.5rem 1rem;
            border-radius: 12px;
            text-align: center;
            border: 1px solid rgba(255, 255, 255, 0.05);
            transition: transform 0.3s ease;
        }}
        
        .stat:hover {{
            transform: translateY(-3px);
            background: rgba(26, 32, 44, 0.8);
        }}
        
        .veiculo-card.filtered {{
            display: none !important;
        }}
        
        .stat-value {{
            font-size: 2rem;
            font-weight: 800;
            margin-bottom: 0.5rem;
            line-height: 1;
        }}
        
        .stat-label {{
            font-size: 0.85rem;
            color: var(--cinza-bem-claro);
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .veiculos-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 1.5rem;
            margin-top: 2rem;
        }}
        
        .veiculo-card {{
            background: rgba(26, 32, 44, 0.8);
            padding: 1.75rem;
            border-radius: 16px;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
            text-align: center;
            transition: all 0.3s ease;
            border: 1px solid rgba(255, 255, 255, 0.05);
            position: relative;
            overflow: hidden;
        }}
        
        .veiculo-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
        }}
        
        .veiculo-card.concluido::before {{ background: var(--verde); }}
        .veiculo-card.andamento::before {{ background: var(--laranja); }}
        .veiculo-card.pendente::before {{ background: var(--vermelho); }}
        
        .veiculo-card:hover {{
            transform: translateY(-8px);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
            background: rgba(26, 32, 44, 0.9);
        }}
        
        .veiculo-prefixo {{
            font-size: 1.8rem;
            font-weight: 800;
            color: var(--cinza-ultra-claro);
            margin-bottom: 0.75rem;
            font-family: 'Courier New', monospace;
        }}
        
        .veiculo-status {{
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 1rem;
            display: inline-block;
        }}
        
        .status-concluido {{ background: var(--verde); color: white; }}
        .status-andamento {{ background: var(--laranja); color: white; }}
        .status-pendente {{ background: var(--vermelho); color: white; }}
        
        .veiculo-data {{
            font-size: 0.8rem;
            color: var(--cinza-bem-claro);
            margin-bottom: 1.25rem;
            font-weight: 500;
        }}
        
        .veiculo-actions {{
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
        }}
        
        .action-select {{
            width: 100%;
            padding: 0.75rem;
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            font-size: 0.85rem;
            background: rgba(45, 55, 72, 0.8);
            color: var(--cinza-ultra-claro);
            cursor: pointer;
            transition: all 0.3s ease;
        }}
        
        .action-select:hover {{
            background: rgba(45, 55, 72, 1);
            border-color: rgba(255, 255, 255, 0.2);
        }}
        
        .btn-excluir {{
            background: rgba(229, 62, 62, 0.2);
            color: var(--vermelho);
            border: 1px solid rgba(229, 62, 62, 0.3);
            padding: 0.75rem;
            border-radius: 8px;
            font-size: 0.85rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
        }}
        
        .btn-excluir:hover {{
            background: var(--vermelho);
            color: white;
            transform: translateY(-2px);
        }}
        
        .empty-state {{
            text-align: center;
            padding: 4rem 2rem;
            color: var(--cinza-bem-claro);
        }}
        
        .empty-icon {{
            font-size: 4rem;
            margin-bottom: 1.5rem;
            opacity: 0.3;
        }}
        
        .progress-bar {{
            width: 100%;
            height: 10px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            overflow: hidden;
            margin: 1.5rem 0;
        }}
        
        .progress-fill {{
            height: 100%;
            border-radius: 10px;
            transition: width 0.5s ease;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
        }}
        
        .progress-success {{ background: linear-gradient(90deg, var(--verde), #48bb78); }}
        
        .sidebar-stats {{
            margin-top: 2.5rem;
            padding-top: 2.5rem;
            border-top: 2px solid rgba(255, 255, 255, 0.1);
        }}
        
        .sidebar-stat {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1rem 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            font-weight: 600;
        }}
        
        .sidebar-stat:last-child {{
            border-bottom: none;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1><i class="fas fa-bus"></i> Dashboard de Instalações</h1>
            <p>Controle profissional • Dados COMPARTILHADOS • Frota de 150 ônibus</p>
            <div class="timestamp">
                <i class="fas fa-sync-alt"></i> Atualizado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}
            </div>
        </div>
        
        <div class="main-grid">
            <!-- Sidebar -->
            <div class="sidebar">
                <div style="margin-bottom: 2.5rem;">
                    <h2 class="form-title"><i class="fas fa-plus-circle"></i> Cadastrar Veículo</h2>
                    <form action="/adicionar" method="POST">
                        <div class="form-group">
                            <label class="form-label">Número do Prefixo</label>
                            <input type="number" name="prefixo" class="form-input" placeholder="Ex: 257, 20520, 221" required min="1">
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label">Garagem</label>
                            <select name="garagem" class="form-select" required>
                                <option value="">Selecione a garagem</option>
                                <option value="M.E OSASCO">M.E OSASCO</option>
                                <option value="M.E SANTANA">M.E SANTANA</option>
                                <option value="MEGACAM OSASCO">MEGACAM OSASCO</option>
                            </select>
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label">Status da Instalação</label>
                            <select name="status" class="form-select" required>
                                <option value="Pendente">Pendente</option>
                                <option value="Em Andamento">Em Andamento</option>
                                <option value="Concluído">Concluído</option>
                            </select>
                        </div>
                        
                        <button type="submit" class="btn">
                            <i class="fas fa-plus"></i> Adicionar Veículo
                        </button>
                    </form>
                </div>
                
                <div class="sidebar-stats">
                    <h3 style="color: var(--cinza-ultra-claro); margin-bottom: 1.5rem; font-size: 1.2rem; font-weight: 700;">
                        <i class="fas fa-chart-pie"></i> Estatísticas do Projeto
                    </h3>
                    <div class="sidebar-stat">
                        <span>Total de Veículos</span>
                        <strong style="color: var(--azul);">{total}</strong>
                    </div>
                    <div class="sidebar-stat">
                        <span>Concluídos</span>
                        <strong style="color: var(--verde);">{concluidos}</strong>
                    </div>
                    <div class="sidebar-stat">
                        <span>Em Andamento</span>
                        <strong style="color: var(--laranja);">{andamento}</strong>
                    </div>
                    <div class="sidebar-stat">
                        <span>Pendentes</span>
                        <strong style="color: var(--vermelho);">{pendentes}</strong>
                    </div>
                    <div class="sidebar-stat">
                        <span>Percentual Geral</span>
                        <strong style="color: var(--roxo);">{percentual:.1f}%</strong>
                    </div>
                </div>
            </div>
            
            <!-- Conteúdo Principal -->
            <div class="content">
                <!-- Métricas -->
                <div class="metrics-grid">
                    <div class="metric-card active" onclick="filtrarVeiculos('todos')" id="card-todos">
                        <div class="metric-icon" style="color: var(--azul);">
                            <i class="fas fa-tachometer-alt"></i>
                        </div>
                        <div class="metric-number">{total}</div>
                        <div class="metric-label">Total de Veículos</div>
                    </div>
                    <div class="metric-card" onclick="filtrarVeiculos('Concluído')" id="card-concluidos">
                        <div class="metric-icon" style="color: var(--verde);">
                            <i class="fas fa-check-circle"></i>
                        </div>
                        <div class="metric-number">{concluidos}</div>
                        <div class="metric-label">Instalações Concluídas</div>
                    </div>
                    <div class="metric-card" onclick="filtrarVeiculos('Em Andamento')" id="card-andamento">
                        <div class="metric-icon" style="color: var(--laranja);">
                            <i class="fas fa-spinner"></i>
                        </div>
                        <div class="metric-number">{andamento}</div>
                        <div class="metric-label">Em Andamento</div>
                    </div>
                    <div class="metric-card" onclick="filtrarVeiculos('Pendente')" id="card-pendentes">
                        <div class="metric-icon" style="color: var(--vermelho);">
                            <i class="fas fa-clock"></i>
                        </div>
                        <div class="metric-number">{pendentes}</div>
                        <div class="metric-label">Instalações Pendentes</div>
                    </div>
                </div>

                <script>
                    function filtrarVeiculos(status) {{
                        // Remove a classe active de todos os cards
                        document.querySelectorAll('.metric-card').forEach(card => {{
                            card.classList.remove('active');
                        }});
                        
                        // Adiciona a classe active no card clicado
                        if (status === 'todos') {{
                            document.getElementById('card-todos').classList.add('active');
                        }} else if (status === 'Concluído') {{
                            document.getElementById('card-concluidos').classList.add('active');
                        }} else if (status === 'Em Andamento') {{
                            document.getElementById('card-andamento').classList.add('active');
                        }} else if (status === 'Pendente') {{
                            document.getElementById('card-pendentes').classList.add('active');
                        }}
                        
                        // Filtra os veículos
                        document.querySelectorAll('.veiculo-card').forEach(card => {{
                            if (status === 'todos') {{
                                card.classList.remove('filtered');
                            }} else {{
                                const cardStatus = card.querySelector('.veiculo-status').textContent.trim();
                                if (cardStatus === status) {{
                                    card.classList.remove('filtered');
                                }} else {{
                                    card.classList.add('filtered');
                                }}
                            }}
                        }});
                    }}

                    // Inicializa mostrando todos os veículos
                    document.addEventListener('DOMContentLoaded', function() {{
                        document.getElementById('card-todos').classList.add('active');
                    }});
                </script>
                
                <!-- Barra de Progresso -->
                <div class="form-container">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 1rem;">
                        <span style="font-weight: 700; color: var(--cinza-ultra-claro); font-size: 1.1rem;">
                            Progresso Geral do Projeto
                        </span>
                        <span style="color: var(--cinza-bem-claro); font-weight: 600;">{percentual:.1f}%</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill progress-success" style="width: {percentual}%"></div>
                    </div>
                </div>
"""

        # Adiciona as seções das garagens
        for garagem_nome, veiculos_garagem in garagens.items():
            total_garagem = len(veiculos_garagem)
            concluidos_garagem = len([v for v in veiculos_garagem if v['status'] == 'Concluído'])
            andamento_garagem = len([v for v in veiculos_garagem if v['status'] == 'Em Andamento'])
            pendentes_garagem = len([v for v in veiculos_garagem if v['status'] == 'Pendente'])
            percentual_garagem = (concluidos_garagem / total_garagem * 100) if total_garagem > 0 else 0
            
            html += f"""
                <!-- {garagem_nome} -->
                <div class="garagem-section">
                    <div class="garagem-header">
                        <h2 class="garagem-title">
                            <i class="fas fa-warehouse"></i> {garagem_nome}
                        </h2>
                        <div style="color: var(--cinza-bem-claro); font-weight: 700; font-size: 1.1rem;">
                            {total_garagem} veículos • {percentual_garagem:.1f}% concluído
                        </div>
                    </div>
                    
                    <div class="garagem-stats">
                        <div class="stat">
                            <div class="stat-value" style="color: var(--azul);">{total_garagem}</div>
                            <div class="stat-label">Total</div>
                        </div>
                        <div class="stat">
                            <div class="stat-value" style="color: var(--verde);">{concluidos_garagem}</div>
                            <div class="stat-label">Concluídos</div>
                        </div>
                        <div class="stat">
                            <div class="stat-value" style="color: var(--laranja);">{andamento_garagem}</div>
                            <div class="stat-label">Em Andamento</div>
                        </div>
                        <div class="stat">
                            <div class="stat-value" style="color: var(--vermelho);">{pendentes_garagem}</div>
                            <div class="stat-label">Pendentes</div>
                        </div>
                    </div>
                    
                    <div style="display: flex; justify-content: space-between; margin-bottom: 1rem;">
                        <span style="font-weight: 700; color: var(--cinza-ultra-claro);">
                            Progresso da Garagem
                        </span>
                        <span style="color: var(--cinza-bem-claro); font-weight: 600;">{percentual_garagem:.1f}%</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill progress-success" style="width: {percentual_garagem}%"></div>
                    </div>
"""
            
            if veiculos_garagem:
                html += """
                    <div class="veiculos-grid">
"""
                
                for veiculo in veiculos_garagem:
                    status_class = veiculo['status'].lower().replace(' ', '')
                    html += f"""
                        <div class="veiculo-card {status_class}">
                            <div class="veiculo-prefixo">{veiculo['prefixo']}</div>
                            <div class="veiculo-status status-{status_class}">
                                {veiculo['status']}
                            </div>
                            <div class="veiculo-data">
                                <i class="far fa-clock"></i> {veiculo['data']}
                            </div>
                            <div class="veiculo-actions">
                                <form action="/atualizar" method="POST">
                                    <input type="hidden" name="prefixo" value="{veiculo['prefixo']}">
                                    <select name="status" class="action-select" onchange="this.form.submit()">
                                        <option value="Pendente" {"selected" if veiculo['status'] == "Pendente" else ""}>🟡 Pendente</option>
                                        <option value="Em Andamento" {"selected" if veiculo['status'] == "Em Andamento" else ""}>🟠 Em Andamento</option>
                                        <option value="Concluído" {"selected" if veiculo['status'] == "Concluído" else ""}>🟢 Concluído</option>
                                    </select>
                                </form>
                                
                                <form action="/atualizar" method="POST">
                                    <input type="hidden" name="prefixo" value="{veiculo['prefixo']}">
                                    <select name="garagem" class="action-select" onchange="this.form.submit()">
                                        <option value="M.E OSASCO" {"selected" if veiculo['garagem'] == "M.E OSASCO" else ""}>🏭 M.E OSASCO</option>
                                        <option value="M.E SANTANA" {"selected" if veiculo['garagem'] == "M.E SANTANA" else ""}>🏭 M.E SANTANA</option>
                                        <option value="MEGACAM OSASCO" {"selected" if veiculo['garagem'] == "MEGACAM OSASCO" else ""}>🏭 MEGACAM OSASCO</option>
                                    </select>
                                </form>

                                <form action="/atualizar" method="POST">
                                    <input type="hidden" name="prefixo" value="{veiculo['prefixo']}">
                                    <textarea 
                                        name="comentario" 
                                        class="action-select" 
                                        placeholder="Adicione um comentário..."
                                        style="min-height: 60px; resize: vertical;"
                                        onchange="this.form.submit()"
                                    >{veiculo.get('comentario', '')}</textarea>
                                </form>
                                
                                <form action="/excluir" method="POST" onsubmit="return confirm('Tem certeza que deseja excluir o veículo {veiculo['prefixo']}?')">
                                    <input type="hidden" name="prefixo" value="{veiculo['prefixo']}">
                                    <button type="submit" class="btn-excluir">
                                        <i class="fas fa-trash"></i> Excluir
                                    </button>
                                </form>
                            </div>
                        </div>
"""
                
                html += """
                    </div>
"""
            else:
                html += f"""
                    <div class="empty-state">
                        <div class="empty-icon">
                            <i class="fas fa-bus"></i>
                        </div>
                        <h3 style="color: var(--cinza-bem-claro); margin-bottom: 1rem; font-size: 1.3rem;">
                            Nenhum veículo cadastrado
                        </h3>
                        <p style="color: var(--cinza-mais-claro); font-size: 1rem;">
                            Use o formulário ao lado para adicionar veículos
                        </p>
                    </div>
"""
            
            html += """
                </div>
"""
        
        # Fecha o HTML
        html += """
            </div>
        </div>
    </div>
    
    <script>
        // Apenas animações
        document.addEventListener('DOMContentLoaded', function() {
            const animateElements = document.querySelectorAll('.metric-card, .veiculo-card, .garagem-section');
            animateElements.forEach((el, index) => {
                el.style.opacity = '0';
                el.style.transform = 'translateY(30px)';
                
                setTimeout(() => {
                    el.style.transition = 'all 0.6s cubic-bezier(0.25, 0.46, 0.45, 0.94)';
                    el.style.opacity = '1';
                    el.style.transform = 'translateY(0)';
                }, index * 100);
            });
        });
        
        // Auto-refresh a cada 30 segundos para ver atualizações de outros usuários
        setTimeout(() => {
            window.location.reload();
        }, 30000);
    </script>
</body>
</html>
"""
        
        return html

    def log_message(self, format, *args):
        # Ignora mensagens de erro SSL
        if '400' in format and 'Bad request version' in format:
            return
        super().log_message(format, *args)

def get_port():
    """Obtém a porta do ambiente (Railway) ou usa 8001 localmente"""
    return int(os.environ.get('PORT', 8001))

def main():
    PORT = get_port()
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    print(f"🚀 Iniciando servidor na porta {PORT}...")
    
    with socketserver.TCPServer(("0.0.0.0", PORT), DashboardHandler) as httpd:
        print(f"✅ Servidor ONLINE!")
        print(f"📍 URL: https://seu-app.railway.app")
        print(f"🕐 {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        print("⏹️  Pressione CTRL+C para parar")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Servidor parado")

if __name__ == "__main__":
    main()