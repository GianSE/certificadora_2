@echo off

REM Este script ativa o ambiente virtual e executa o launcher_app.py

REM 1. Ativa o ambiente virtual (venv).
REM Assume que a pasta do venv está na raiz do projeto.
call venv\Scripts\activate.bat

REM Verifica se a ativação foi bem sucedida
if exist venv\Scripts\activate.bat (
echo Ambiente virtual ativado.
) else (
echo ERRO: Pasta 'venv' ou arquivo de ativacao nao encontrado.
echo Certifique-se de que o venv esta criado e nomeado como 'venv'.
goto :fim
)

REM 2. Executa o script Python
echo Executando o Painel de Controle IoT...
python launcher.py

REM O comando 'pause' mantem a janela do terminal aberta apos o script fechar
REM Remova se nao quiser que a janela fique aberta
:fim