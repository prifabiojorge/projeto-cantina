#!/usr/bin/env python3
"""
Script de inicialização do Sistema Cantina Escolar.

Verifica dependências, executa seed de dados (opcional) e inicia o servidor Flask.
"""

import sys
import subprocess
import os
from pathlib import Path

def verificar_python():
    """Verifica versão do Python."""
    print("🔍 Verificando versão do Python...")
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 ou superior é necessário.")
        print(f"   Versão atual: {sys.version}")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    return True

def verificar_dependencias():
    """Verifica e instala dependências do requirements.txt."""
    print("\n🔍 Verificando dependências...")
    
    requirements_path = Path(__file__).parent / "requirements.txt"
    if not requirements_path.exists():
        print("❌ Arquivo requirements.txt não encontrado.")
        return False
    
    try:
        # Tentar importar todas as dependências
        import flask
        import qrcode
        import PIL
        import apscheduler
        import pywhatkit
        import dotenv
        import reportlab
        import fpdf
        print("✅ Todas as dependências já estão instaladas.")
        return True
    except ImportError as e:
        print(f"⚠️  Dependências faltando: {e}")
        print("📦 Instalando dependências...")
        
        # Instalar via pip
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "-r", str(requirements_path)
            ])
            print("✅ Dependências instaladas com sucesso.")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Falha ao instalar dependências: {e}")
            return False

def executar_seed():
    """Executa o script de seed de dados."""
    print("\n🌱 Executando seed de dados...")
    
    seed_path = Path(__file__).parent / "seed.py"
    if not seed_path.exists():
        print("❌ Arquivo seed.py não encontrado.")
        return False
    
    try:
        import seed
        seed.main()
        return True
    except Exception as e:
        print(f"❌ Erro ao executar seed: {e}")
        print("⚠️  Continuando sem dados de teste...")
        return False

def iniciar_servidor():
    """Inicia o servidor Flask."""
    print("\n🚀 Iniciando servidor Flask...")
    
    # Mudar para o diretório do projeto
    os.chdir(Path(__file__).parent)
    
    # Importar app após garantir que dependências estão instaladas
    try:
        from app import app
    except ImportError as e:
        print(f"❌ Erro ao importar app Flask: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("SISTEMA CANTINA ESCOLAR")
    print("=" * 60)
    print("\n📊 URLs de acesso:")
    print("   • Local: http://localhost:5000")
    print("   • Rede: http://SEU_IP:5000")
    print("\n📋 Recursos disponíveis:")
    print("   • Portaria: /portaria")
    print("   • Cantina: /cantina")
    print("   • Dashboard: /dashboard")
    print("   • Alunos: /alunos")
    print("   • Relatórios: /relatorios")
    print("   • Configurações: /configuracoes")
    print("   • Backup: /backup")
    print("\n🛑 Para parar o servidor: Ctrl+C")
    print("=" * 60)
    print("\n📝 Logs do servidor:\n")
    
    # Iniciar servidor Flask
    try:
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n\n👋 Servidor interrompido pelo usuário.")
        return True
    except Exception as e:
        print(f"\n❌ Erro ao iniciar servidor: {e}")
        return False

def main():
    """Função principal."""
    print("=" * 60)
    print("INICIALIZAÇÃO DO SISTEMA CANTINA ESCOLAR")
    print("=" * 60)
    
    # Verificar Python
    if not verificar_python():
        sys.exit(1)
    
    # Verificar dependências
    if not verificar_dependencias():
        sys.exit(1)
    
    # Perguntar sobre seed
    resposta = input("\n🌱 Deseja executar o seed de dados? (s/N): ").strip().lower()
    if resposta == 's':
        executar_seed()
    else:
        print("⚠️  Seed não executado. O sistema iniciará sem dados de teste.")
    
    # Iniciar servidor
    iniciar_servidor()

if __name__ == '__main__':
    main()