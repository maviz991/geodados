-- ============================================================
--  Inicialização do banco geodados
--  Executado automaticamente na primeira vez que o container sobe
-- ============================================================

-- Habilita PostGIS
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;
CREATE EXTENSION IF NOT EXISTS fuzzystrmatch;
CREATE EXTENSION IF NOT EXISTS postgis_tiger_geocoder;

-- ============================================================
--  Esquemas — ajuste conforme sua realidade
-- ============================================================

CREATE SCHEMA IF NOT EXISTS administrativo;   -- limites, municípios, estados
CREATE SCHEMA IF NOT EXISTS hidrografia;      -- rios, lagos, bacias
CREATE SCHEMA IF NOT EXISTS uso_solo;         -- cobertura e uso da terra
CREATE SCHEMA IF NOT EXISTS infraestrutura;   -- rodovias, ferrovias, energia
CREATE SCHEMA IF NOT EXISTS relevo;           -- curvas de nível, MDT, declividade
CREATE SCHEMA IF NOT EXISTS staging;          -- área temporária para importação

-- ============================================================
--  Comentários nos esquemas
-- ============================================================

COMMENT ON SCHEMA administrativo  IS 'Limites administrativos: municípios, estados, regiões';
COMMENT ON SCHEMA hidrografia     IS 'Rede hidrográfica: rios, lagos, bacias hidrográficas';
COMMENT ON SCHEMA uso_solo        IS 'Cobertura e uso da terra por ano';
COMMENT ON SCHEMA infraestrutura  IS 'Infraestrutura: rodovias, ferrovias, linhas de energia';
COMMENT ON SCHEMA relevo          IS 'Dados de relevo: curvas de nível, MDT, declividade';
COMMENT ON SCHEMA staging         IS 'Área de trabalho temporária para importação e processamento';

-- ============================================================
--  search_path padrão para o usuário geo
-- ============================================================

ALTER USER geo SET search_path TO public, administrativo, hidrografia, uso_solo, infraestrutura, relevo, staging;

-- Confirma
SELECT postgis_version();
