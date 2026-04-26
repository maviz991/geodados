#!/usr/bin/env python3
"""
Normaliza CSVs de coordenadas misturadas (DMS + decimal, colunas trocadas).
Uso: python limpar_csv.py etl/dados_costa_norte.csv
"""

import re
import sys
import pandas as pd


LAT_RANGE = (-5, 10)   # latitude esperada para costa norte do Brasil
LON_RANGE = (-60, -40) # longitude esperada


def dms_para_decimal(s):
    s = str(s).strip()
    m = re.match(r"(\d+)[º°](\d+)['\u2019](\d+)?", s)
    if not m:
        return None
    graus = int(m.group(1))
    mins  = int(m.group(2))
    frac  = int(m.group(3) or 0)
    minutos = float(f"{mins}.{frac}") if frac > 60 else mins + frac / 60
    return graus + minutos / 60


def normalizar(val):
    if pd.isna(val):
        return None
    s = str(val).strip()
    try:
        return float(s.replace(",", "."))
    except ValueError:
        return dms_para_decimal(s)


def extrair_coords(vals):
    lat_min, lat_max = LAT_RANGE
    lon_abs_min, lon_abs_max = abs(LON_RANGE[1]), abs(LON_RANGE[0])
    lats = [v for v in vals if v is not None and lat_min <= v <= lat_max]
    lons = [v for v in vals if v is not None and lon_abs_min <= abs(v) <= lon_abs_max]
    lons = [-abs(v) for v in lons]
    return lats, lons


def corrigir_linha(row, c1, c2, c3, c4):
    v1 = normalizar(row[c1])
    v2 = normalizar(row[c2])
    v3 = normalizar(row[c3])
    v4 = normalizar(row[c4])

    lats, lons = extrair_coords([v1, v2, v3, v4])

    # Bbox completo
    if len(lats) == 2 and len(lons) == 2:
        return lats[0], lats[1], lons[0], lons[1], "bbox"

    # Só coordenada inicial (ponto)
    lats1, lons1 = extrair_coords([v1, v3])
    if len(lats1) == 1 and len(lons1) == 1:
        return lats1[0], None, lons1[0], None, "point"

    return None, None, None, None, None


def limpar(path):
    df = pd.read_csv(path, sep=";", encoding="utf-8", low_memory=False)

    # Remove colunas vazias
    df = df.dropna(how="all", axis=1)

    c1, c2, c3, c4 = "LATITUDE INICIAL", "LATITUDE FINAL", "LONGITUDE INICIAL", "LONGITUDE FINAL"

    resultados = df.apply(lambda r: corrigir_linha(r, c1, c2, c3, c4), axis=1)
    df[[c1, c2, c3, c4, "GEOM_TIPO"]] = pd.DataFrame(resultados.tolist(), index=df.index)

    antes = len(df)
    df = df.dropna(subset=[c1, c3])  # lat_ini e lon_ini obrigatórios
    for col in [c1, c2, c3, c4]:
        df[col] = pd.to_numeric(df[col], errors="coerce").round(6)
    df = df.drop_duplicates(subset=["ARRASTO", "DATA"])
    depois = len(df)

    n_bbox  = (df["GEOM_TIPO"] == "bbox").sum()
    n_point = (df["GEOM_TIPO"] == "point").sum()
    print(f"  Bbox (arrasto completo) : {n_bbox}")
    print(f"  Point (coord. parcial)  : {n_point}")

    print(f"  Linhas originais : {antes}")
    print(f"  Após limpeza     : {depois}")
    print(f"  Removidas        : {antes - depois}")

    saida = path.replace(".csv", "_limpo.csv")
    df.to_csv(saida, sep=";", index=False, encoding="utf-8")
    print(f"  Salvo em         : {saida}")
    print(f"\nAmostra:")
    print(df[[c1, c2, c3, c4, "GEOM_TIPO"]].head(3).to_string())


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "etl/dados_costa_norte.csv"
    limpar(path)
