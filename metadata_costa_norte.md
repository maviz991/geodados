# Cartographic Product Metadata
**Bottom Trawl Tracks on the Northern Coast of Brazil**

**Compliance:** ISO 19115 — Core Metadata Set

---

## 1. Resource Identification

| Field | Value |
|---|---|
| File Identifier | trawl_tracks_northern_coast_brazil_2026 |
| Title | Bottom Trawl Tracks on the Northern Coast of Brazil |
| Language | eng |
| Character Set | UTF-8 |
| Hierarchy Level | dataset |
| Spatial Rep. Type | vector |
| Date | 2026-04-21 |
| Date Type | creation |

**Abstract:**
Cartographic product developed through the integration of bathymetric data from the General Bathymetric Chart of the Oceans (GEBCO 2025), official administrative boundaries from the Brazilian Institute of Geography and Statistics (IBGE 2024), and georeferenced bottom trawl records collected along the northern coast of Brazil. The map represents trawling tracks, state boundaries, and bathymetric gradients of the study area, spanning from the mouth of the Oiapoque River to the Pará shelf. Intended for fisheries research, environmental impact assessment, and marine spatial planning.

**Keywords:** Bottom trawl, Fisheries, Northern Coast, Amazon shelf, Bathymetry, GEBCO, IBGE, GIS, SIRGAS 2000

**Topic Category:** oceans, biota

**Spatial Extent:** Northern Coast of Brazil — Amapá and Pará shelf

| | |
|---|---|
| Northern Latitude | 6.000000° |
| Southern Latitude | 0.000000° |
| Western Longitude | -54.000000° |
| Eastern Longitude | -43.000000° |

**Point of Contact:**

| Field | Value |
|---|---|
| Name | [AUTHOR PLACEHOLDER] |
| Institution | [INSTITUTION PLACEHOLDER] |
| E-mail | [EMAIL PLACEHOLDER] |

---

## 2. Spatial Reference System

| Field | Value |
|---|---|
| Reference System | SIRGAS 2000 |
| Coordinate Type | Geographic |
| Unit of Measurement | Decimal degrees (°) |
| EPSG Code | 4674 |
| Cartographic Scale | 1:3,000,000 |

---

## 3. Data Sources (Lineage / Source)

### Bathymetry

| Field | Value |
|---|---|
| Source | *GEBCO 2025 Grid* |
| Provider | GEBCO Compilation Group, British Oceanographic Data Centre (BODC), National Oceanography Centre, NERC |
| Year | 2025 |
| Available at | https://www.gebco.net/data_and_products/gridded_bathymetry_data/ |
| Accessed on | 2026-04-21 |

### Administrative Boundaries

| Field | Value |
|---|---|
| Source | *Territorial Meshes: State and National Boundaries — Official Shapefiles* |
| Provider | Instituto Brasileiro de Geografia e Estatística (IBGE), Directorate of Geosciences |
| Year | 2024 |
| Available at | https://www.ibge.gov.br/geociencias/organizacao-do-territorio/malhas-territoriais.html |
| Accessed on | 2026-04-21 |

### Trawl Data

| Field | Value |
|---|---|
| Source | Bottom trawl survey records — Northern Coast of Brazil |
| Provider | [INSTITUTION PLACEHOLDER] |
| Period | 2017–2022 |
| Format | Tabular CSV (georeferenced start and end coordinates) |
| CRS | SIRGAS 2000 / EPSG:4674 |

---

## 4. Data Quality and Lineage

**Scope:** dataset

**Process Description:**

1. **Data acquisition:** Download of GEBCO 2025 GeoTIFF (extent: N 6°, S 0°, W -54°, E -43°) and IBGE 2024 state boundary shapefiles.
2. **Standardization:** Reprojection of all layers to SIRGAS 2000 (EPSG:4674) and coordinate normalization of trawl records (DMS and decimal degrees, mixed format) using a custom Python ETL pipeline.
3. **Spatial integration:** Overlay of bathymetry, administrative boundaries, and trawl tracks in a GIS environment (QGIS 3.x / PostGIS 16).
4. **Editing and validation:** Topological verification, symbology adjustments, contour line generation (-50 m, -100 m, -200 m isobaths), and geographic consistency checks.
5. **Final product:** Exported in PDF and PNG at multiple resolutions for digital and printed use.

---

## 5. Distribution

| Field | Value |
|---|---|
| Available Formats | PDF, PNG |
| Distributor | [INSTITUTION PLACEHOLDER] |

---

## 6. Metadata Information

| Field | Value |
|---|---|
| Metadata Language | eng |
| Metadata Standard | ISO 19115:2003 — Geographic Information — Metadata |
| Standard Version | 2003 |
| Metadata Date | 2026-04-21 |
| Metadata Contact | [AUTHOR PLACEHOLDER] / [INSTITUTION PLACEHOLDER] |

---

## References

- GEBCO Compilation Group. (2025). *GEBCO 2025 Grid*. British Oceanographic Data Centre, National Oceanography Centre, NERC. Retrieved 2026-04-21, from https://www.gebco.net/data_and_products/gridded_bathymetry_data/

- Instituto Brasileiro de Geografia e Estatística (IBGE). (2024). *Malhas territoriais: limites estaduais e nacionais — official shapefiles*. Rio de Janeiro: IBGE, Directorate of Geosciences. Retrieved 2026-04-21, from https://www.ibge.gov.br/geociencias/organizacao-do-territorio/malhas-territoriais.html
