# Dashboard de Instalações - Frota de Ônibus

## 1. Sobre o Projeto
Sistema web para controle de instalações de kits de monitoramento em 150 ônibus.

## 2. Instalação

### Pré-requisitos
- Python 3.7+
- Acesso à porta 8001

### Instalação Rápida
1. Copie a pasta com os arquivos para o servidor
2. Execute: `python app.py`
3. Acesse: `http://servidor:8001`

## 3. Configuração

### Porta Personalizada
Para alterar a porta, edite o arquivo `app.py`:

```python
def main():
    PORT = 8001  # Altere este número para a porta desejada