CREATE TABLE netball_womens_australia_fixture (
    -- Fixture Information
    fixtureId                     VARCHAR(50)          NOT NULL,
    matchId                       VARCHAR(50)          NOT NULL,
    matchNumber                   INT                  DEFAULT NULL,
    matchStatus                   VARCHAR(50)          DEFAULT NULL,
    matchType                     VARCHAR(50)          DEFAULT NULL,
    sportId                       VARCHAR(50)          NOT NULL,

    -- Time Information
    localStartTime                VARCHAR(50)          DEFAULT NULL,
    period                        INT                  DEFAULT NULL,
    periodCompleted               INT                  DEFAULT NULL,
    periodSecs                    INT                  DEFAULT NULL,
    utcStartTime                  VARCHAR(50)          DEFAULT NULL,

    -- Home Squad Information
    homeSquadCode                 VARCHAR(50)          DEFAULT NULL,
    homeSquadId                   VARCHAR(50)          NOT NULL,
    homeSquadName                 VARCHAR(50)          DEFAULT NULL,
    homeSquadNickname             VARCHAR(50)          DEFAULT NULL,
    homeSquadScore                INT                  DEFAULT NULL,
    homeSquadShortCode            VARCHAR(50)          DEFAULT NULL,

    -- Away Squad Information
    awaySquadCode                 VARCHAR(50)          DEFAULT NULL,
    awaySquadId                   VARCHAR(50)          NOT NULL,
    awaySquadName                 VARCHAR(50)          DEFAULT NULL,
    awaySquadNickname             VARCHAR(50)          DEFAULT NULL,
    awaySquadScore                INT                  DEFAULT NULL,
    awaySquadShortCode            VARCHAR(50)          DEFAULT NULL,

    -- Venue Information
    venueCode                     VARCHAR(50)          DEFAULT NULL,
    venueId                       VARCHAR(50)          NOT NULL,
    venueName                     VARCHAR(50)          DEFAULT NULL,

    -- Round and Final Information
    finalCode                     VARCHAR(50)          DEFAULT NULL,
    finalShortCode                VARCHAR(50)          DEFAULT NULL,
    roundNumber                   INT                  DEFAULT NULL,

    -- Precomputed Columns (calculated in the application layer)
    matchName                     VARCHAR(255)         NOT NULL,
    uniqueAwaySquadId             VARCHAR(255)         NOT NULL,
    uniqueFixtureId               VARCHAR(255)         NOT NULL,
    uniqueHomeSquadId             VARCHAR(255)         NOT NULL,
    uniqueSportId                 VARCHAR(255)         NOT NULL,

    -- Primary Key
    PRIMARY KEY (uniqueFixtureId),

    -- Foreign Keys
    FOREIGN KEY (uniqueHomeSquadId)            REFERENCES squad_info(uniqueSquadId),
    FOREIGN KEY (uniqueAwaySquadId)            REFERENCES squad_info(uniqueSquadId),
    FOREIGN KEY (uniqueSportId)                REFERENCES sport_info(uniqueSportId)
);

