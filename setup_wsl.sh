#!/bin/bash
# =============================================================
#  setup_wsl.sh
#  Instala Docker Engine e GDAL no WSL e configura tudo
#  Execute uma vez: bash setup_wsl.sh
# =============================================================

echo "================================================"
echo "  Setup geodados — WSL + Docker + PostGIS"
echo "================================================"

# --- Docker Engine ---
if command -v docker &> /dev/null; then
    echo "✅ Docker já instalado: $(docker --version)"
else
    echo "📦 Instalando Docker Engine..."
    sudo apt-get update -qq
    sudo apt-get install -y ca-certificates curl gnupg lsb-release

    # Repositório oficial Docker
    sudo install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
        sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    sudo chmod a+r /etc/apt/keyrings/docker.gpg

    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
        https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | \
        sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

    sudo apt-get update -qq
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

    # Usuário no grupo docker (sem sudo)
    sudo usermod -aG docker $USER
    echo "✅ Docker instalado"
fi

# --- GDAL (ogr2ogr para importar shapefiles) ---
if command -v ogr2ogr &> /dev/null; then
    echo "✅ GDAL já instalado: $(ogr2ogr --version 2>&1 | head -1)"
else
    echo "📦 Instalando GDAL..."
    sudo apt-get install -y gdal-bin python3-gdal
    echo "✅ GDAL instalado"
fi

# --- Inicia Docker ---
echo "🐳 Iniciando Docker..."
sudo service docker start

# --- Auto-start no .bashrc ---
BASHRC="$HOME/.bashrc"
MARKER="# geodados: auto-start docker"

if ! grep -q "$MARKER" "$BASHRC"; then
    echo "" >> "$BASHRC"
    echo "$MARKER" >> "$BASHRC"
    echo 'if ! service docker status > /dev/null 2>&1; then' >> "$BASHRC"
    echo '    sudo service docker start > /dev/null 2>&1' >> "$BASHRC"
    echo 'fi' >> "$BASHRC"
    echo "✅ Auto-start do Docker adicionado ao .bashrc"
fi

# --- Permissões nos scripts ---
chmod +x backup_geodados.sh importar_shapefile.sh 2>/dev/null

# --- Cria pasta do banco no WSL ---
mkdir -p ~/geodados/pgdata

echo ""
echo "================================================"
echo "  Tudo pronto! Próximos passos:"
echo "================================================"
echo ""
echo "1. Feche e reabra o WSL (para aplicar grupo docker)"
echo "   ou execute: newgrp docker"
echo ""
echo "2. Suba o banco:"
echo "   docker compose up -d"
echo ""
echo "3. Importe um shapefile:"
echo "   ./importar_shapefile.sh arquivo.shp administrativo municipios"
echo ""
echo "4. Conecte no QGIS:"
echo "   Host: localhost | Porta: 5434 | Banco: geodados"
echo "   Usuário: geo | Senha: geo@1234"
echo ""
echo "5. Configure backup automático (cron):"
echo "   crontab -e"
echo "   Adicione: 0 22 * * * $(pwd)/backup_geodados.sh"
echo ""
