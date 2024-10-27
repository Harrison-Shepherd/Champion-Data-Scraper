CREATE TABLE afl_womens_period (
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
    kickEfficiency              INT               DEFAULT NULL,
    kicks                       INT               DEFAULT NULL,
    kicksEffective              INT               DEFAULT NULL,
    kicksIneffective            INT               DEFAULT NULL,
    marks                       INT               DEFAULT NULL,
    marksContested              INT               DEFAULT NULL,
    marksInside50               INT               DEFAULT NULL,
    marksUncontested            INT               DEFAULT NULL,
    penalty50sAgainst           INT               DEFAULT NULL,
    possessionsContested        INT               DEFAULT NULL,
    possessionsUncontested      INT               DEFAULT NULL,
    tackles                     INT               DEFAULT NULL,

    -- Player Information
    jumperNumber                INT               DEFAULT NULL,
    playerId                    VARCHAR(50)       NOT NULL,
    positionCode                VARCHAR(50)       DEFAULT NULL,


    -- Match Information
    matchId                     VARCHAR(50)       NOT NULL,
    period                      VARCHAR(50)       NOT NULL,
    periodId                    VARCHAR(50)       NOT NULL,

    -- Precomputed Columns (calculated in the application layer)
    uniqueMatchId               VARCHAR(255)      NOT NULL,
    uniquePeriodId              VARCHAR(255)      NOT NULL,
    uniquePlayerId              VARCHAR(255)      NOT NULL,

    -- Primary Key
    PRIMARY KEY (uniquePeriodId),

    -- Foreign Keys
    FOREIGN KEY (uniqueMatchId)        REFERENCES afl_womens_match(uniqueMatchId),  
    FOREIGN KEY (uniquePlayerId)       REFERENCES player_info(uniquePlayerId)
);
