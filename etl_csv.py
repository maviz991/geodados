#!/usr/bin/env python3
"""
ETL: CSV -> PostGIS (geodados)
Uso:
    python etl_csv.py                  # processa todos os CSVs em etl/
    python etl_csv.py --only municipios # processa apenas etl/municipios.csv
"""

# =============================================================
#  CONFIGURAÇÃO — ajuste aqui
# =============================================================

DB = {
    "host":     "localhost",
    "port":     5434,
    "dbname":   "geodados",
    "user":     "geo",
    "password": "geo@1234",
}

ETL_DIR = "etl"

# Comportamento se a tabela já existir: "replace" | "append" | "fail"
IF_EXISTS = "replace"

# Mapeamento CSV -> esquema.tabela
# Se omitido, usa staging.<nome_arquivo>
TABELAS = {
    "dados_costa_norte": "hidrografia.costa_norte",
    # "municipios":        "administrativo.municipios",
    # "rodovias":          "infraestrutura.rodovias",
}

# Configuração por CSV
# "separator"  — separador de colunas (padrão: ",")
# "geom"       — tipo de geometria:
#                "point_decimal"  → colunas lat/lon em graus decimais
#                "bbox_dms"       → 4 colunas em DMS (graus°minutos') → Polygon
#                None             → sem geometria
# "lat_ini", "lat_fim", "lon_ini", "lon_fim" — nomes das colunas para bbox_dms
# "lat_col", "lon_col"                       — nomes das colunas para point_decimal
# "lat_hem", "lon_hem" — hemisfério: "S"/"N" e "W"/"E"
CSV_CONFIG = {
    "dados_costa_norte": {
        "separator": ";",
        "geom":      "bbox_misto",
        "col1":      "LATITUDE INICIAL",
        "col2":      "LATITUDE FINAL",
        "col3":      "LONGITUDE INICIAL",
        "col4":      "LONGITUDE FINAL",
        "lat_hem":   "N",
        "lon_hem":   "W",
        "lat_range": (-5, 10),    # lats esperadas para costa norte do Brasil
        "lon_range": (-60, -40),  # lons esperadas
    },
    # Exemplo ponto decimal:
    # "estacoes": {
    #     "separator": ",",
    #     "geom":      "point_decimal",
    #     "lat_col":   "latitude",
    #     "lon_col":   "longitude",
    #     "lat_hem":   "S",
    #     "lon_hem":   "W",
    # },
}

# Colunas auto-detectadas como lat/lon decimal (quando geom não configurado)
LAT_COLS = ["lat", "latitude", "y"]
LON_COLS = ["lon", "lng", "longitude", "x"]

# =============================================================

import argparse
import os
import re
import sys

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL


def get_engine():
    url = URL.create(
        drivername="postgresql+psycopg2",
        username=DB["user"],
        password=DB["password"],
        host=DB["host"],
        port=DB["port"],
        database=DB["dbname"],
    )
    return create_engine(url)


def normalizar_coord(val, hemisfério):
    """
    Normaliza coordenada para graus decimais.
    Aceita:
      - Decimal já pronto (float ou string numérica)
      - DMS: 'Dº M'FFF"' — se FFF > 60 trata como decimal minutes (M.FFF),
        senão trata como segundos reais
    Aplica sinal negativo se hemisfério for 'S' ou 'W' e valor for positivo.
    Retorna None se não conseguir converter.
    """
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return None
    s = str(val).strip()

    # Tenta decimal direto
    try:
        decimal = float(s.replace(",", "."))
        if hemisfério.upper() in ("S", "W") and decimal > 0:
            decimal = -decimal
        return decimal
    except ValueError:
        pass

    # Tenta DMS
    m = re.match(r"(\d+)[º°](\d+)['\u2019](\d+)?[\"\u201d]*", s)
    if not m:
        return None
    graus = int(m.group(1))
    mins  = int(m.group(2))
    frac  = int(m.group(3) or 0)
    if frac > 60:
        minutos_decimal = float(f"{mins}.{frac}")
    else:
        minutos_decimal = mins + frac / 60
    decimal = graus + minutos_decimal / 60
    if hemisfério.upper() in ("S", "W"):
        decimal = -decimal
    return decimal


def detectar_geom_auto(df):
    cols = {c.lower(): c for c in df.columns}
    lat = next((cols[c] for c in LAT_COLS if c in cols), None)
    lon = next((cols[c] for c in LON_COLS if c in cols), None)
    return lat, lon


def carregar_csv(path, nome, engine):
    schema_tabela = TABELAS.get(nome, f"staging.{nome}")
    schema, tabela = schema_tabela.split(".", 1)
    cfg = CSV_CONFIG.get(nome, {})
    sep = cfg.get("separator", ",")
    geom_tipo = cfg.get("geom")

    print(f"\n{'='*50}")
    print(f"  Arquivo : {path}")
    print(f"  Destino : {schema_tabela}")

    df = pd.read_csv(path, sep=sep, encoding="utf-8", low_memory=False)
    print(f"  Linhas  : {len(df):,}  |  Colunas: {len(df.columns)}")

    geom_wkt_series = None

    if geom_tipo in ("bbox_dms", "bbox_misto"):
        lat_hem   = cfg.get("lat_hem", "N")
        lon_hem   = cfg.get("lon_hem", "W")
        lat_range = cfg.get("lat_range")
        lon_range = cfg.get("lon_range")
        cols = [cfg["col1"], cfg["col2"], cfg["col3"], cfg["col4"]]
        print(f"  Geometria: bbox (DMS/decimal/misto) → Polygon EPSG:4674")

        def fazer_bbox(row):
            # Parseia os 4 valores sem aplicar hemisfério ainda
            vals = [normalizar_coord(row[c], "N") for c in cols]
            if None in vals:
                return None

            if lat_range and lon_range:
                # Separa lats e lons pelos ranges esperados
                lats = [v for v in vals if lat_range[0] <= v <= lat_range[1]]
                lons = [v for v in vals if lon_range[0] <= v <= lon_range[1]]
                if len(lats) != 2 or len(lons) != 2:
                    return None
            else:
                # Sem range: assume ordem col1=lat_ini, col2=lat_fim, col3=lon_ini, col4=lon_fim
                lats = [vals[0], vals[1]]
                lons = [vals[2], vals[3]]

            # Aplica hemisfério
            if lat_hem.upper() == "S":
                lats = [-abs(v) for v in lats]
            if lon_hem.upper() == "W":
                lons = [-abs(v) for v in lons]

            xmin, xmax = min(lons), max(lons)
            ymin, ymax = min(lats), max(lats)
            return f"SRID=4674;POLYGON(({xmin} {ymin},{xmax} {ymin},{xmax} {ymax},{xmin} {ymax},{xmin} {ymin}))"

        geom_wkt_series = df.apply(fazer_bbox, axis=1)

    elif geom_tipo == "point_decimal":
        lat_col = cfg.get("lat_col")
        lon_col = cfg.get("lon_col")
        lat_hem = cfg.get("lat_hem", "N")
        lon_hem = cfg.get("lon_hem", "W")
        print(f"  Geometria: ponto decimal → Point EPSG:4674")
        df = df.dropna(subset=[lat_col, lon_col])
        sinal_lat = -1 if lat_hem.upper() == "S" else 1
        sinal_lon = -1 if lon_hem.upper() == "W" else 1

        geom_wkt_series = df.apply(
            lambda r: f"SRID=4674;POINT({sinal_lon * r[lon_col]} {sinal_lat * r[lat_col]})", axis=1
        )

    else:
        # Auto-detecção por nome de coluna
        lat_col, lon_col = detectar_geom_auto(df)
        if lat_col and lon_col:
            print(f"  Geometria: auto-detectada ({lat_col}, {lon_col}) → Point EPSG:4674")
            df = df.dropna(subset=[lat_col, lon_col])
            geom_wkt_series = df.apply(
                lambda r: f"SRID=4674;POINT({r[lon_col]} {r[lat_col]})", axis=1
            )
        else:
            print("  Geometria: não detectada — importando como tabela tabular")

    df_pg = df.copy()
    if geom_wkt_series is not None:
        df_pg["geom_wkt"] = geom_wkt_series.values

    # Normaliza nomes de colunas
    df_pg.columns = [c.lower().replace(" ", "_").replace("-", "_") for c in df_pg.columns]

    df_upload = df_pg.drop(columns=["geom_wkt"], errors="ignore") if geom_wkt_series is None else df_pg
    df_upload.to_sql(tabela, engine, schema=schema, if_exists=IF_EXISTS, index=False, chunksize=1000)

    if geom_wkt_series is not None:
        geom_type_pg = "Polygon" if geom_tipo in ("bbox_dms", "bbox_misto") else "Point"
        with engine.begin() as conn:
            conn.execute(text(f"""
                ALTER TABLE {schema}.{tabela}
                ADD COLUMN IF NOT EXISTS geom geometry({geom_type_pg}, 4674);
            """))
            conn.execute(text(f"""
                UPDATE {schema}.{tabela}
                SET geom = ST_GeomFromEWKT(geom_wkt);
            """))
            conn.execute(text(f"""
                ALTER TABLE {schema}.{tabela} DROP COLUMN IF EXISTS geom_wkt;
            """))
            conn.execute(text(f"""
                CREATE INDEX IF NOT EXISTS {tabela}_geom_idx
                ON {schema}.{tabela} USING GIST (geom);
            """))
        print("  Índice espacial criado.")

    print(f"  ✅ {schema_tabela} importado com sucesso.")


def main():
    parser = argparse.ArgumentParser(description="ETL: CSV -> PostGIS geodados")
    parser.add_argument("--only", metavar="TABELA", help="Processa apenas etl/<TABELA>.csv")
    args = parser.parse_args()

    if not os.path.isdir(ETL_DIR):
        print(f"❌ Pasta '{ETL_DIR}' não encontrada.")
        sys.exit(1)

    engine = get_engine()

    if args.only:
        path = os.path.join(ETL_DIR, f"{args.only}.csv")
        if not os.path.isfile(path):
            print(f"❌ Arquivo não encontrado: {path}")
            sys.exit(1)
        arquivos = [(path, args.only)]
    else:
        arquivos = [
            (os.path.join(ETL_DIR, f), os.path.splitext(f)[0])
            for f in sorted(os.listdir(ETL_DIR))
            if f.endswith(".csv")
        ]
        if not arquivos:
            print(f"❌ Nenhum CSV encontrado em '{ETL_DIR}/'")
            sys.exit(1)

    print(f"🗄️  Conectando em {DB['host']}:{DB['port']}/{DB['dbname']}")
    print(f"📂 {len(arquivos)} arquivo(s) para processar")

    erros = []
    for path, nome in arquivos:
        try:
            carregar_csv(path, nome, engine)
        except Exception as e:
            print(f"  ❌ Erro em {nome}: {e}")
            erros.append(nome)

    print(f"\n{'='*50}")
    print(f"✅ Concluído. {len(arquivos) - len(erros)}/{len(arquivos)} importados.")
    if erros:
        print(f"❌ Erros em: {', '.join(erros)}")


if __name__ == "__main__":
    main()
