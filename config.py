import os

# Configurações do servidor
SERVER_CONFIG = {
    'host': '0.0.0.0',  # Escuta em todas as interfaces
    'port': 8000,
    'debug': False
}

# Configurações da aplicação
APP_CONFIG = {
    'data_file': 'data/veiculos.json',
    'backup_interval': 3600  # Backup a cada 1 hora
}

# Configurações de segurança
SECURITY_CONFIG = {
    'allowed_hosts': ['*'],  # Em produção, defina os IPs específicos
    'cors_enabled': True
}