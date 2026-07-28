#!/bin/bash
echo "=========================================="
echo "  EDS NeverLost - Setup para Desktop"
echo "=========================================="
echo ""

# Verificar se esta no WSL2
if ! grep -q "microsoft" /proc/version 2>/dev/null; then
    echo "⚠️  Atenção: Este script deve rodar dentro do WSL2"
    echo "   Se voce esta no Windows, abra o Ubuntu primeiro."
fi

echo "📦 Atualizando sistema..."
sudo apt update -qq

echo "🐍 Verificando Python..."
python3 --version || sudo apt install -y python3 python3-pip

echo "📚 Instalando bibliotecas..."
pip3 install psycopg2-binary 2>/dev/null || sudo apt install -y python3-psycopg2

echo "🐳 Verificando Docker..."
docker --version || echo "❌ Docker nao encontrado. Instale o Docker Desktop com WSL2 primeiro."

echo "🔗 Clonando repositorio..."
if [ ! -d "EDS-Workspace" ]; then
    git clone https://github.com/Srdarth/EDS-Workspace.git
fi

cd EDS-Workspace

echo "🗄️  Subindo PostgreSQL..."
docker-compose -f infra/docker/docker-compose.yml up -d postgres

echo "⏳ Aguardando banco iniciar..."
sleep 5

echo "🧪 Testando conexao..."
docker exec -it eddy-postgres psql -U postgres -d eddydb -c "SELECT 'OK' as status;" 2>/dev/null || echo "⚠️  Banco ainda iniciando, tente daqui a pouco."

echo ""
echo "✅ Setup concluido"
echo "   Proximo passo: python3 apps/scanner/scanner_db.py /mnt/c/Users/SeuUsuario/Documents"
