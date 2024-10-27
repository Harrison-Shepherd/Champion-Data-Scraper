CREATE TABLE netball_womens_nz_score_flow (
    -- Period and Timing Information
    period                 INT             DEFAULT NULL,
    periodSeconds          INT             DEFAULT NULL,

    -- Scoring Information
    distanceCode           INT             DEFAULT NULL,
    scorepoints            INT             DEFAULT NULL,
    scoreName              VARCHAR(50)     DEFAULT NULL,

    -- Player and Position Information
    positionCode           VARCHAR(50)     DEFAULT NULL,
    squadId                VARCHAR(50)     NOT NULL,
    playerId               VARCHAR(50)     NOT NULL,

    -- Match Information
    matchId                VARCHAR(50)     NOT NULL,

    -- Unique Identifier
    scoreFlowId            VARCHAR(50)     NOT NULL,

    -- Precomputed Columns (calculated in the application layer)
    uniquePlayerId         VARCHAR(255)    NOT NULL,
    uniqueMatchId          VARCHAR(255)    NOT NULL,

    -- Primary Key
    PRIMARY KEY (scoreFlowId),

    -- Foreign Key
    FOREIGN KEY (uniqueMatchId)  REFERENCES netball_womens_nz_match(uniqueMatchId),

    -- Info Foreign Keys
    FOREIGN KEY (uniquePlayerId) REFERENCES player_info(uniquePlayerId)
);
