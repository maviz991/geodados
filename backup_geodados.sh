#!/bin/bash
# =============================================================
#  backup_geodados.sh (WSL)
#  Faz dump do banco e salva no Google Drive e/ou OneDrive
# =============================================================

# --- Configuração ---
CONTAINER="geodados_db"
DB_USER="geo"
DB_NAME="geodados"
KEEP_LAST=7
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Detecta usuário Windows automaticamente
WIN_USER=$(powershell.exe -Command "echo \$env:USERNAME" 2>/dev/null | tr -d '\r')

# --- Detecta destinos disponíveis ---
DESTINATIONS=()

# Google Drive
if [ -d "/mnt/c/Users/$WIN_USER/Google Drive/Meu Drive" ]; then
    DESTINATIONS+=("/mnt/c/Users/$WIN_USER/Google Drive/Meu Drive/geodados_backups")
elif [ -d "/mnt/c/Users/$WIN_USER/Google Drive/My Drive" ]; then
    DESTINATIONS+=("/mnt/c/Users/$WIN_USER/Google Drive/My Drive/geodados_backups")
elif [ -d "/mnt/c/Users/$WIN_USER/GoogleDrive/MyDrive" ]; then
    DESTINATIONS+=("/mnt/c/Users/$WIN_USER/GoogleDrive/MyDrive/geodados_backups")
fi

# OneDrive
if [ -d "/mnt/c/Users/$WIN_USER/OneDrive" ]; then
    DESTINATIONS+=("/mnt/c/Users/$WIN_USER/OneDrive/geodados_backups")
elif [ -d "/mnt/c/Users/$WIN_USER/OneDrive - Personal" ]; then
    DESTINATIONS+=("/mnt/c/Users/$WIN_USER/OneDrive - Personal/geodados_backups")
fi

# Fallback: WSL local
if [ ${#DESTINATIONS[@]} -eq 0 ]; then
    DESTINATIONS+=("$HOME/geodados_backups")
    echo "⚠️  Google Drive e OneDrive não encontrados. Salvando em: $HOME/geodados_backups"
    echo "   Instale o Google Drive ou OneDrive, ou ajuste BACKUP_DIR manualmente."
fi

# Verifica se o container está rodando
if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER}$"; then
    echo "❌ Container '$CONTAINER' não está rodando. Suba com: docker compose up -d"
    exit 1
fi

echo "🗄️  Iniciando backup: $TIMESTAMP"

# Gera dump uma vez
TMP_FILE="/tmp/${DB_NAME}_${TIMESTAMP}.sql.gz"
docker exec "$CONTAINER" pg_dump -U "$DB_USER" "$DB_NAME" | gzip > "$TMP_FILE"

if [ $? -ne 0 ]; then
    echo "❌ Erro no dump!"
    rm -f "$TMP_FILE"
    exit 1
fi

# Copia para cada destino
for DIR in "${DESTINATIONS[@]}"; do
    mkdir -p "$DIR"
    cp "$TMP_FILE" "$DIR/${DB_NAME}_${TIMESTAMP}.sql.gz"
    SIZE=$(du -sh "$DIR/${DB_NAME}_${TIMESTAMP}.sql.gz" | cut -f1)
    echo "✅ Salvo em: $DIR ($SIZE)"

    # Remove backups antigos neste destino
    echo "🧹 Mantendo últimos $KEEP_LAST backups em: $DIR"
    ls -t "$DIR"/${DB_NAME}_*.sql.gz 2>/dev/null | tail -n +$((KEEP_LAST + 1)) | xargs -r rm --
done

rm -f "$TMP_FILE"

echo ""
echo "📦 Backups disponíveis:"
for DIR in "${DESTINATIONS[@]}"; do
    ls -lh "$DIR"/${DB_NAME}_*.sql.gz 2>/dev/null
done
