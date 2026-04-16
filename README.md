# 🗺️ geodados — PostGIS no WSL com backup no Google Drive

## Estrutura

```
geodados/
├── setup_wsl.sh              # Instala tudo do zero (rode uma vez)
├── docker-compose.yml        # Sobe o banco
├── backup_geodados.sh        # Backup → Google Drive
├── importar_shapefile.sh     # Importa .shp para o banco
├── init/
│   └── 01_init.sql           # Cria esquemas automático na 1ª vez
└── README.md
```

---

## Primeira vez — setup completo

```bash
bash setup_wsl.sh
```

O script instala Docker Engine, GDAL, configura auto-start e permissões.

Depois feche e reabra o WSL:
```bash
# Ou sem fechar:
newgrp docker
```

---

## Subir o banco

```bash
docker compose up -d

# Verificar se está saudável
docker ps
```

Na primeira vez cria automaticamente os esquemas:
`administrativo` · `hidrografia` · `uso_solo` · `infraestrutura` · `relevo` · `staging`

---

## Conectar no QGIS

**Camada → Adicionar Camada → PostGIS**

| Campo | Valor |
|---|---|
| Host | `localhost` |
| Porta | `5434` |
| Banco | `geodados` |
| Usuário | `geo` |
| Senha | `geo@1234` |

> O QGIS roda no Windows e conecta normalmente em `localhost` — o WSL expõe a porta automaticamente.

---

## Importar shapefiles

```bash
# Arquivo já no WSL
./importar_shapefile.sh municipios_br.shp administrativo municipios

# Arquivo ainda no Windows (use o caminho /mnt/c/...)
./importar_shapefile.sh /mnt/c/Users/USUARIO/Downloads/rios.shp hidrografia rios_sp
```

O script reprojeta automaticamente para **EPSG:4674 (SIRGAS 2000)**.

---

## Backup para o Google Drive

```bash
./backup_geodados.sh
```

O script detecta automaticamente o caminho do Google Drive no Windows.

### Automatizar com cron

```bash
crontab -e
# Adicione — backup todo dia às 22h:
0 22 * * * /home/SEU_USUARIO/geodados/backup_geodados.sh >> /tmp/backup_geo.log 2>&1
```

---

## Restaurar backup

```bash
gunzip -c geodados_20240115_220000.sql.gz | \
  docker exec -i geodados_db psql -U geo -d geodados
```

---

## Comandos do dia a dia

```bash
# Iniciar
docker compose up -d

# Parar (dados preservados)
docker compose stop

# Ver logs
docker compose logs -f postgis

# Acessar banco pelo terminal
docker exec -it geodados_db psql -U geo -d geodados

# Dentro do psql — listar tabelas por esquema
\dt administrativo.*
\dt hidrografia.*

# Ver todas as tabelas espaciais
SELECT schemaname, tablename FROM pg_tables
WHERE schemaname NOT IN ('pg_catalog','information_schema')
ORDER BY schemaname, tablename;
```

---

## ⚠️ Dica WSL

O volume do banco fica em `~/geodados/pgdata` — **dentro do filesystem WSL**, não no `/mnt/c/...`. Isso garante performance e evita corrupção.

O backup é que vai para o Windows/Google Drive.

Antes de desligar o PC:
1. Feche QGIS / Python
2. `./backup_geodados.sh`
3. Aguarde sync do Google Drive ✅

git commit -m "feat: setup inicial do geodados — PostGIS no WSL com Docker"
gh repo create geodados --public --source=. --remote=origin --push