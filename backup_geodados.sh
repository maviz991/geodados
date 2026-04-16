#!/bin/bash
# =============================================================
#  backup_geodados.sh (WSL)
#  Faz dump do banco e salva no Google Drive ou OneDrive
# =============================================================

# --- Configuração ---
CONTAINER="geodados_db"
DB_USER="geo"
DB_NAME="geodados"
KEEP_LAST=7
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Detecta usuário Windows automaticamente
WIN_USER=$(powershell.exe -Command "echo \$env:USERNAME" 2>/dev/null | tr -d '\r')

# Caminhos Google Drive (português e inglês, cliente novo)
GDRIVE_PT="/mnt/c/Users/$WIN_USER/Google Drive/Meu Drive/geodados_backups"
GDRIVE_EN="/mnt/c/Users/$WIN_USER/Google Drive/My Drive/geodados_backups"
GDRIVE_NEW="/mnt/c/Users/$WIN_USER/GoogleDrive/MyDrive/geodados_backups"

# Caminhos OneDrive (português e inglês)
ONEDRIVE_PT="/mnt/c/Users/$WIN_USER/OneDrive/geodados_backups"
ONEDRIVE_EN="/mnt/c/Users/$WIN_USER/OneDrive - Personal/geodados_backups"

if [ -d "/mnt/c/Users/$WIN_USER/Google Drive/Meu Drive" ]; then
    BACKUP_DIR="$GDRIVE_PT"
elif [ -d "/mnt/c/Users/$WIN_USER/Google Drive/My Drive" ]; then
    BACKUP_DIR="$GDRIVE_EN"
elif [ -d "/mnt/c/Users/$WIN_USER/GoogleDrive/MyDrive" ]; then
    BACKUP_DIR="$GDRIVE_NEW"
elif [ -d "/mnt/c/Users/$WIN_USER/OneDrive" ]; then
    BACKUP_DIR="$ONEDRIVE_PT"
elif [ -d "/mnt/c/Users/$WIN_USER/OneDrive - Personal" ]; then
    BACKUP_DIR="$ONEDRIVE_EN"
else
    # Fallback: salva no WSL mesmo e avisa
    BACKUP_DIR="$HOME/geodados_backups"
    echo "⚠️  Google Drive e OneDrive não encontrados. Salvando em: $BACKUP_DIR"
    echo "   Instale o Google Drive ou OneDrive, ou ajuste BACKUP_DIR manualmente."
fi

BACKUP_FILE="$BACKUP_DIR/${DB_NAME}_${TIMESTAMP}.sql.gz"

mkdir -p "$BACKUP_DIR"

echo "🗄️  Iniciando backup: $TIMESTAMP"
echo "📂 Destino: $BACKUP_DIR"

# Verifica se o container está rodando
if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER}$"; then
    echo "❌ Container '$CONTAINER' não está rodando. Suba com: docker compose up -d"
    exit 1
fi

# Dump comprimido
docker exec "$CONTAINER" pg_dump -U "$DB_USER" "$DB_NAME" | gzip > "$BACKUP_FILE"

if [ $? -eq 0 ]; then
    SIZE=$(du -sh "$BACKUP_FILE" | cut -f1)
    echo "✅ Backup salvo: $(basename $BACKUP_FILE) ($SIZE)"
else
    echo "❌ Erro no backup!"
    rm -f "$BACKUP_FILE"
    exit 1
fi

# Remove backups antigos
echo "🧹 Mantendo últimos $KEEP_LAST backups..."
ls -t "$BACKUP_DIR"/${DB_NAME}_*.sql.gz 2>/dev/null | tail -n +$((KEEP_LAST + 1)) | xargs -r rm --

echo ""
echo "📦 Backups disponíveis:"
ls -lh "$BACKUP_DIR"/${DB_NAME}_*.sql.gz 2>/dev/null
