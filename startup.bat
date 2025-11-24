@echo off
cd /d "C:\Users\david.oliveira\Documents\InstalacoesDahua"

echo ========================================
echo    INICIANDO DASHBOARD DAHUA - PORTA 8001
echo ========================================
echo.

echo [1/5] Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Python nao encontrado!
    pause
    exit /b 1
)

echo [2/5] Parando processos anteriores...
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im pythonw.exe >nul 2>&1
timeout /t 3 /nobreak >nul

echo [3/5] Limpando reservas de porta...
netsh int ipv4 delete excludedportrange protocol=tcp startport=8001 numberofports=1 >nul 2>&1

echo [4/5] Instalando dependencias...
pip install -r requirements.txt >nul 2>&1

echo [5/5] Iniciando servidor em BACKGROUND...
echo.
echo ========================================
echo    ACESSE: http://localhost:8001
echo    Servidor rodando em SEGUNDO PLANO!
echo    Esta janela pode ser FECHADA!
echo ========================================
echo.

start pythonw app_final.py

echo Servidor iniciado em segundo plano!
echo Feche esta janela - o site continua rodando!
timeout /t 5