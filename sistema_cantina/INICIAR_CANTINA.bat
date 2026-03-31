@echo off
title Sistema da Cantina
color 0A
echo.
echo  ================================================
echo       SISTEMA DA CANTINA ESCOLAR
echo       CISEB Celso Rodrigues
echo       Santo Antonio do Taua - PA
echo  ================================================
echo.
echo  Iniciando servidor...
echo.
cd /d E:\Documents\DEGOO\CANTINA\sistema_cantina

echo  Verificando dependencias...
pip install -r requirements.txt --quiet

echo.
echo  Iniciando Flask com HTTPS...
echo.
echo  Acesse no navegador:
echo    Dashboard:  https://localhost:5000
echo    Portaria:   https://localhost:5000/portaria
echo    Cantina:    https://localhost:5000/cantina
echo.
echo  Para outros computadores na rede, use:
echo    https://SEU-IP:5000/portaria
echo.
echo  Para descobrir seu IP, digite ipconfig no CMD.
echo.
echo  NAO FECHE ESTA JANELA.
echo  ================================================
echo.
python app.py

echo.
echo  Servidor encerrado.
pause