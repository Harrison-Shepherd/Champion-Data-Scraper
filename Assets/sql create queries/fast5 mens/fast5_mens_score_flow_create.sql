CREATE TABLE fast5_mens_score_flow (
    -- Period and Timing Information
    period                      INT               DEFAULT NULL,
    periodSeconds               INT               DEFAULT NULL,

    -- Scoring Information
    distanceCode                INT               DEFAULT NULL,
    scorepoints                 INT               DEFAULT NULL,
    scoreName                   VARCHAR(50)       DEFAULT NULL,

    -- Player and Position Information
    playerId                    VARCHAR(50)       NOT NULL,
    positionCode                VARCHAR(50)       DEFAULT NULL,
    squadId                     VARCHAR(50)       NOT NULL,

    -- Match Information
    matchId                     VARCHAR(50)       NOT NULL,

    -- Unique Identifier
    scoreFlowId                 VARCHAR(50)       NOT NULL,   -- Precomputed from matchId and index (or other unique logic)

    -- Precomputed Columns (calculated in the application layer)
    uniqueMatchId               VARCHAR(255)      NOT NULL,
    uniquePlayerId              VARCHAR(255)      NOT NULL,

    -- Primary Key
    PRIMARY KEY (scoreFlowId),

    -- Foreign Key
    FOREIGN KEY (uniqueMatchId)        REFERENCES fast5_mens_match(uniqueMatchId),

    -- Info Foreign Keys
    FOREIGN KEY (uniquePlayerId)       REFERENCES player_info(uniquePlayerId)
);
