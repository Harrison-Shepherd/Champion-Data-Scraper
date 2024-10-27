CREATE TABLE afl_womens_match (
    -- Match Statistics
    behinds                     INT               DEFAULT NULL,
    blocks                      INT               DEFAULT NULL,
    clangers                    INT               DEFAULT NULL,
    clearances                  INT               DEFAULT NULL,
    disposalEfficiency          INT               DEFAULT NULL,
    disposals                   INT               DEFAULT NULL,
    freesAgainst                INT               DEFAULT NULL,
    freesFor                    INT               DEFAULT NULL,
    goalAssists                 INT               DEFAULT NULL,
    goals                       INT               DEFAULT NULL,
    handballs                   INT               DEFAULT NULL,
    hitouts                     INT               DEFAULT NULL,
    hitoutsToAdvantage          INT               DEFAULT NULL,
    inside50s                   INT               DEFAULT NULL,
    jumperNumber                INT               DEFAULT NULL,
    kickEfficiency              INT               DEFAULT NULL,
    kicks                       INT               DEFAULT NULL,
    kicksEffective              INT               DEFAULT NULL,
    kicksIneffective            INT               DEFAULT NULL,
    marks                       INT               DEFAULT NULL,
    marksContested              INT               DEFAULT NULL,
    marksInside50               INT               DEFAULT NULL,
    marksUncontested            INT               DEFAULT NULL,
    penalty50sAgainst           INT               DEFAULT NULL,
    playerId                    VARCHAR(50)       NOT NULL,
    possessionsContested        INT               DEFAULT NULL,
    possessionsUncontested      INT               DEFAULT NULL,
    squadId                     VARCHAR(50)       NOT NULL,
    tackles                     INT               DEFAULT NULL,

    -- Player Information
    debut                       YEAR              DEFAULT NULL,
    displayName                 VARCHAR(50)       DEFAULT NULL,
    dob                         DATE              DEFAULT NULL,
    firstname                   VARCHAR(50)       DEFAULT NULL,
    height                      INT               DEFAULT NULL,
    mainPlayingPosition         VARCHAR(50)       DEFAULT NULL,
    positionCode                VARCHAR(50)       DEFAULT NULL,
    positionId                  VARCHAR(50)       DEFAULT NULL,
    positionName                VARCHAR(50)       DEFAULT NULL,
    recruitedFrom               VARCHAR(50)       DEFAULT NULL,
    shortDisplayName            VARCHAR(50)       DEFAULT NULL,
    surname                     VARCHAR(50)       DEFAULT NULL,
    fixtureYear                 VARCHAR(50)       NOT NULL,

    -- Team Information
    awayId                      VARCHAR(50)       NOT NULL,
    homeId                      VARCHAR(50)       NOT NULL,
    opponent                    VARCHAR(50)       DEFAULT NULL,
    squadName                   VARCHAR(50)       DEFAULT NULL,
    squadShortName              VARCHAR(50)       DEFAULT NULL,

    -- Match Information
    fixtureId                   VARCHAR(50)       NOT NULL,
    matchId                     VARCHAR(50)       NOT NULL,
    round                       INT               DEFAULT NULL,
    sportId                     VARCHAR(50)       NOT NULL,

    -- Precomputed Columns (calculated in the application layer)
    uniqueFixtureId             VARCHAR(255)      NOT NULL,
    uniqueMatchId               VARCHAR(255)      NOT NULL,
    uniquePlayerId              VARCHAR(255)      NOT NULL,
    uniqueSquadId               VARCHAR(255)      NOT NULL,
    uniqueSportId               VARCHAR(255)      NOT NULL,

    -- Primary Key
    PRIMARY KEY (uniqueMatchId),

    -- Foreign Keys
    FOREIGN KEY (uniqueFixtureId)        REFERENCES afl_womens_fixture(uniqueFixtureId),
    FOREIGN KEY (uniquePlayerId)         REFERENCES player_info(uniquePlayerId),
    FOREIGN KEY (uniqueSquadId)          REFERENCES squad_info(uniqueSquadId),
    FOREIGN KEY (uniqueSportId)          REFERENCES sport_info(uniqueSportId)
);
