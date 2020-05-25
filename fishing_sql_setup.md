CREATE DATABASE IF NOT EXISTS fishing;

# Creates raw fishing data table

CREATE TABLE IF NOT EXISTS FishingRaw (
    id                      SERIAL,
    mmsi                    NUMERIC     NOT NULL,
    timestamp               NUMERIC     NOT NULL,
    distance_from_shore     NUMERIC     NOT NULL,
    distance_from_port      NUMERIC     NOT NULL,
    speed                   NUMERIC     NOT NULL,
    course                  NUMERIC     NOT NULL,
    lat                     NUMERIC     NOT NULL,
    lon                     NUMERIC     NOT NULL,
    is_fishing              NUMERIC     NOT NULL,
    source                  VARCHAR(20) NOT NULL,
    gear_type               VARCHAR(20) NOT NULL,
    PRIMARY KEY (id)
);

# Creates feature-laden fishing data table (first pass)

CREATE TABLE IF NOT EXISTS FishingTest (
    index                   SERIAL,
    mmsi                    NUMERIC     NOT NULL,
    timestamp               TIMESTAMP   NOT NULL,
    distance_from_shore     NUMERIC     NOT NULL,
    distance_from_port      NUMERIC     NOT NULL,
    speed                   NUMERIC,
    course                  NUMERIC,
    lat                     NUMERIC     NOT NULL,
    lon                     NUMERIC     NOT NULL,
    is_fishing              NUMERIC     NOT NULL,
    source                  VARCHAR(20) NOT NULL,
    gear_type               VARCHAR(20) NOT NULL,

    year                    INTEGER     NOT NULL,
    month                   INTEGER     NOT NULL,
    day                     INTEGER     NOT NULL,
    hour                    INTEGER     NOT NULL,
    minute                  INTEGER     NOT NULL,

    is_new_mmsi             BOOLEAN     NOT NULL,

    prev_speed              NUMERIC,
    prev_lat                NUMERIC,
    prev_lon                NUMERIC,

    dist_moved              NUMERIC,
    time_taken              NUMERIC,

    PRIMARY KEY (index)
);

# Postgre 11 chokes on large files, this is the workaround

COPY FishingFeatures FROM PROGRAM 'cmd /c "type ./data/fishing boats/fishing_with_features.csv"' DELIMITER ',' CSV HEADER;