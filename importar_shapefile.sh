#!/bin/bash
# =============================================================
#  importar_shapefile.sh (WSL)
#  Importa shapefile para o banco geodados
#
#  Uso: ./importar_shapefile.sh <arquivo.shp> <esquema> <tabela>
#  Ex:  ./importar_shapefile.sh municipios_br.shp administrativo municipios
#
#  Dica: se o arquivo estiver no Windows, use o caminho WSL:
#  /mnt/c/Users/USUARIO/Downloads/municipios_br.shp
# =============================================================

SHP="$1"
SCHEMA="$2"
TABELA="$3"

DB_HOST="localhost"
DB_PORT="5434"
DB_NAME="geodados"
DB_USER="geo"
DB_PASS="geo@1234"

ESQUEMAS_VALIDOS="administrativo hidrografia uso_solo infraestrutura relevo staging"

# --- Validações ---
if [ -z "$SHP" ] || [ -z "$SCHEMA" ] || [ -z "$TABELA" ]; then
    echo "Uso: $0 <arquivo.shp> <esquema> <nome_tabela>"
    echo ""
    echo "Esquemas disponíveis:"
    for e in $ESQUEMAS_VALIDOS; do echo "  - $e"; done
    exit 1
fi

if [ ! -f "$SHP" ]; then
    echo "❌ Arquivo não encontrado: $SHP"
    echo ""
    echo "Se o arquivo está no Windows, use o caminho WSL. Exemplo:"
    WIN_USER=$(powershell.exe -Command "echo \$env:USERNAME" 2>/dev/null | tr -d '\r')
    echo "  /mnt/c/Users/$WIN_USER/Downloads/$(basename $SHP)"
    exit 1
fi

# Verifica se ogr2ogr está instalado
if ! command -v ogr2ogr &> /dev/null; then
    echo "❌ ogr2ogr não encontrado. Instale com:"
    echo "   sudo apt update && sudo apt install gdal-bin"
    exit 1
fi

# Verifica se o container está rodando
if ! docker ps --format '{{.Names}}' | grep -q "^geodados_db$"; then
    echo "❌ Banco não está rodando. Suba com: docker compose up -d"
    exit 1
fi

echo "📥 Importando: $SHP"
echo "   → $SCHEMA.$TABELA"

# Detecta SRID
SRID=$(ogrinfo -al -so "$SHP" 2>/dev/null | grep "AUTHORITY" | grep -oP '"\K[0-9]+(?=")' | tail -1)
SRID=${SRID:-4326}
echo "📐 SRID detectado: EPSG:$SRID"

# Importa e reprojeta para SIRGAS 2000 (padrão Brasil)
PGPASSWORD="$DB_PASS" ogr2ogr \
    -f "PostgreSQL" \
    PG:"host=$DB_HOST port=$DB_PORT dbname=$DB_NAME user=$DB_USER password=$DB_PASS" \
    "$SHP" \
    -nln "$SCHEMA.$TABELA" \
    -nlt PROMOTE_TO_MULTI \
    -lco GEOMETRY_NAME=geom \
    -lco FID=id \
    -t_srs EPSG:4674 \
    -overwrite \
    --config PG_USE_COPY YES

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Importado com sucesso: $SCHEMA.$TABELA"
    echo ""
    echo "┌─ Conexão QGIS ──────────────────────────┐"
    echo "│  Host:    localhost                      │"
    echo "│  Porta:   5432                           │"
    echo "│  Banco:   geodados                       │"
    echo "│  Usuário: geo                            │"
    echo "│  Esquema: $SCHEMA"
    echo "│  Tabela:  $TABELA"
    echo "└──────────────────────────────────────────┘"
else
    echo "❌ Erro na importação"
    exit 1
fi
