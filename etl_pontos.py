#!/usr/bin/env python3
"""
ETL: CSV -> pontos iniciais e finais de arrasto no PostGIS
Cada linha do CSV gera 2 pontos (inicial e final) linkados por arrasto_id.

Uso:
    python etl_pontos.py                   # processa todos os CSVs em etl/
    python etl_pontos.py --only dados_costa_norte
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

IF_EXISTS = "replace"

# Mapeamento CSV -> esquema.tabela
TABELAS = {
    "dados_costa_norte": "hidrografia.pontos_arrasto",
}

# Configuração por CSV
CSV_CONFIG = {
    "dados_costa_norte": {
        "separator":  ";",
        "arrasto_id": "ARRASTO",
        "data":       "DATA",
        "lat_ini":    "LATITUDE INICIAL",
        "lon_ini":    "LONGITUDE INICIAL",
        "lat_fim":    "LATITUDE FINAL",
        "lon_fim":    "LONGITUDE FINAL",
        "extras":     [],   # outras colunas a preservar
    },
}

# =============================================================

import argparse
import os
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


def fazer_ponto(lat, lon):
    try:
        lat, lon = float(lat), float(lon)
        if pd.isna(lat) or pd.isna(lon):
            return None
        return f"SRID=4674;POINT({lon} {lat})"
    except (TypeError, ValueError):
        return None


def carregar_csv(path, nome, engine):
    schema_tabela = TABELAS.get(nome, f"staging.{nome}_pontos")
    schema, tabela = schema_tabela.split(".", 1)
    cfg     = CSV_CONFIG.get(nome, {})
    sep     = cfg.get("separator", ",")
    c_id    = cfg.get("arrasto_id", "ARRASTO")
    c_data  = cfg.get("data", "DATA")
    c_lat_i = cfg.get("lat_ini", "LATITUDE INICIAL")
    c_lon_i = cfg.get("lon_ini", "LONGITUDE INICIAL")
    c_lat_f = cfg.get("lat_fim", "LATITUDE FINAL")
    c_lon_f = cfg.get("lon_fim", "LONGITUDE FINAL")
    extras  = cfg.get("extras", [])

    print(f"\n{'='*50}")
    print(f"  Arquivo : {path}")
    print(f"  Destino : {schema_tabela}")

    df = pd.read_csv(path, sep=sep, encoding="utf-8", low_memory=False)
    df = df.dropna(how="all", axis=1)
    print(f"  Linhas  : {len(df):,}")

    registros = []
    for _, row in df.iterrows():
        base = {"arrasto_id": row[c_id], "data": row[c_data]}
        for col in extras:
            if col in row:
                base[col.lower().replace(" ", "_")] = row[col]

        wkt_ini = fazer_ponto(row.get(c_lat_i), row.get(c_lon_i))
        wkt_fim = fazer_ponto(row.get(c_lat_f), row.get(c_lon_f))

        if wkt_ini:
            registros.append({**base, "tipo": "inicial", "geom_wkt": wkt_ini})
        if wkt_fim:
            registros.append({**base, "tipo": "final", "geom_wkt": wkt_fim})

    df_out = pd.DataFrame(registros)
    contagem = df_out["tipo"].value_counts().to_dict()
    print(f"  Pontos gerados: {len(df_out)} {contagem}")

    # Sobe com geom_wkt para usar no UPDATE
    df_out.to_sql(tabela, engine, schema=schema, if_exists=IF_EXISTS, index=False, chunksize=1000)

    with engine.begin() as conn:
        conn.execute(text(f"""
            ALTER TABLE {schema}.{tabela}
            ADD COLUMN IF NOT EXISTS geom geometry(Point, 4674);
        """))
        conn.execute(text(f"""
            UPDATE {schema}.{tabela}
            SET geom = ST_GeomFromEWKT(geom_wkt);
        """))
        conn.execute(text(f"""
            ALTER TABLE {schema}.{tabela} DROP COLUMN geom_wkt;
        """))
        conn.execute(text(f"""
            CREATE INDEX IF NOT EXISTS {tabela}_geom_idx
            ON {schema}.{tabela} USING GIST (geom);
        """))

    print(f"  ✅ {schema_tabela} importado com sucesso.")


def main():
    parser = argparse.ArgumentParser(description="ETL: CSV -> pontos inicial/final PostGIS")
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
