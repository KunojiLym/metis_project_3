CREATE DATABASE fishing;

# Creates raw fishing data table

CREATE TABLE IF NOT EXISTS FishingRaw (
    mmsi                    NUMERIC     NOT NULL,
    timestamp               TIMESTAMP   NOT NULL,
    distance_from_shore     NUMERIC     NOT NULL,
    distance_from_port      NUMERIC     NOT NULL,
    speed                   NUMERIC     NOT NULL,
    course                  NUMERIC     NOT NULL,
    lat                     NUMERIC     NOT NULL,
    lon                     NUMERIC     NOT NULL,
    is_fishing              NUMERIC     NOT NULL,
    source                  VARCHAR(20) NOT NULL,
    gear_type               VARCHAR(20) NOT NULL,
    PRIMARY KEY (mmsi, timestamp)
);

# Creates feature-laden fishing data table (first pass)

CREATE TABLE IF NOT EXISTS FishingFeatures (
    index                   INTEGER     NOT NULL,
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
    time_taken              VARCHAR(25),

    PRIMARY KEY (index)
);

COPY FishingFeatures FROM './data/fishing boats/fishing_with_features.csv' DELIMITER ',' CSV HEADER;