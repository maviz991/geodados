#!/usr/bin/env python3
"""
ETL: CSV -> linhas de arrasto no PostGIS
Cada linha do CSV gera um LineString do ponto inicial ao final.

Uso:
    python etl_linhas.py                   # processa todos os CSVs em etl/
    python etl_linhas.py --only dados_costa_norte
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

TABELAS = {
    "dados_costa_norte": "hidrografia.linhas_arrasto",
}

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


def fazer_linha(lat_i, lon_i, lat_f, lon_f):
    try:
        lat_i, lon_i = float(lat_i), float(lon_i)
        lat_f, lon_f = float(lat_f), float(lon_f)
        if any(pd.isna(v) for v in [lat_i, lon_i, lat_f, lon_f]):
            return None
        return f"SRID=4674;LINESTRING({lon_i} {lat_i},{lon_f} {lat_f})"
    except (TypeError, ValueError):
        return None


def carregar_csv(path, nome, engine):
    schema_tabela = TABELAS.get(nome, f"staging.{nome}_linhas")
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

    # Normaliza nomes de colunas para o banco
    col_map = {c: c.lower().replace(" ", "_") for c in df.columns}
    df_pg = df.rename(columns=col_map)

    c_id_pg    = col_map.get(c_id, c_id.lower())
    c_data_pg  = col_map.get(c_data, c_data.lower())
    c_lat_i_pg = col_map.get(c_lat_i, c_lat_i.lower())
    c_lon_i_pg = col_map.get(c_lon_i, c_lon_i.lower())
    c_lat_f_pg = col_map.get(c_lat_f, c_lat_f.lower())
    c_lon_f_pg = col_map.get(c_lon_f, c_lon_f.lower())

    df_pg["geom_wkt"] = df_pg.apply(
        lambda r: fazer_linha(r[c_lat_i_pg], r[c_lon_i_pg], r[c_lat_f_pg], r[c_lon_f_pg]),
        axis=1
    )

    validas = df_pg["geom_wkt"].notna().sum()
    nulas   = df_pg["geom_wkt"].isna().sum()
    print(f"  Linhas geradas  : {validas} válidas, {nulas} sem coordenada final (ignoradas)")

    df_pg.to_sql(tabela, engine, schema=schema, if_exists=IF_EXISTS, index=False, chunksize=1000)

    with engine.begin() as conn:
        conn.execute(text(f"""
            ALTER TABLE {schema}.{tabela}
            ADD COLUMN IF NOT EXISTS geom geometry(LineString, 4674);
        """))
        conn.execute(text(f"""
            UPDATE {schema}.{tabela}
            SET geom = ST_GeomFromEWKT(geom_wkt)
            WHERE geom_wkt IS NOT NULL;
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
    parser = argparse.ArgumentParser(description="ETL: CSV -> linhas de arrasto PostGIS")
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
