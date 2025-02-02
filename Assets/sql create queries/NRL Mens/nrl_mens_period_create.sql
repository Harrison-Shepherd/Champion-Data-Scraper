CREATE TABLE NRL_mens_period (
    -- Match and Squad Information
    matchId                     VARCHAR(50)     NOT NULL,  -- Reference to the match
    squadId                     VARCHAR(50)     NOT NULL,
    periodId                    VARCHAR(50)     NOT NULL,

    -- Player Information
    playerId                    VARCHAR(50)     NOT NULL,
    jumperNumber                INT             DEFAULT NULL,
    position                    VARCHAR(50)     DEFAULT NULL,

    -- Performance Statistics
    tries                       INT             DEFAULT NULL,
    tryAssists                  INT             DEFAULT NULL,
    trySaves                    INT             DEFAULT NULL,
    conversions                 INT             DEFAULT NULL,
    conversionsUnsuccessful     INT             DEFAULT NULL,
    conversionAttempts          INT             DEFAULT NULL,
    penaltyGoals                INT             DEFAULT NULL,
    penaltyGoalAttempts         INT             DEFAULT NULL,
    fieldGoals                  INT             DEFAULT NULL,
    fieldGoalAttempts           INT             DEFAULT NULL,

    -- Runs and Metres Gained
    runs                        INT             DEFAULT NULL,
    runMetres                   INT             DEFAULT NULL,
    metresGained                INT             DEFAULT NULL,
    runsNormal                  INT             DEFAULT NULL,
    runsNormalMetres            INT             DEFAULT NULL,
    runsKickReturn              INT             DEFAULT NULL,
    runsKickReturnMetres        INT             DEFAULT NULL,
    runsHitup                   INT             DEFAULT NULL,
    runsHitupMetres             INT             DEFAULT NULL,
    runsDummyHalf               INT             DEFAULT NULL,
    runsDummyHalfMetres         INT             DEFAULT NULL,
    postContactMetres           INT             DEFAULT NULL,

    -- Tackles and Defensive Actions
    tackles                     INT             DEFAULT NULL,
    tackleds                    INT             DEFAULT NULL,
    tackleBreaks                INT             DEFAULT NULL,
    tacklesIneffective          INT             DEFAULT NULL,
    missedTackles               INT             DEFAULT NULL,
    lineBreaks                  INT             DEFAULT NULL,
    lineBreakAssists            INT             DEFAULT NULL,
    offloads                    INT             DEFAULT NULL,
    ineffectiveTackles          INT             DEFAULT NULL,
    tacklesMissed               INT             DEFAULT NULL,
    incompleteSets              INT             DEFAULT NULL,

    -- Kicking
    kickMetres                  INT             DEFAULT NULL,
    kicksGeneralPlay            INT             DEFAULT NULL,
    kicksCaught                 INT             DEFAULT NULL,
    bombKicksCaught             INT             DEFAULT NULL,
    fortyTwenty                 INT             DEFAULT NULL,

    -- Errors and Penalties
    handlingErrors              INT             DEFAULT NULL,
    penaltiesConceded           INT             DEFAULT NULL,
    errors                      INT             DEFAULT NULL,

    -- Miscellaneous
    passes                      INT             DEFAULT NULL,
    goalLineDropouts            INT             DEFAULT NULL,
    sentOffs                    INT             DEFAULT NULL,
    sinBins                     INT             DEFAULT NULL,
    onReports                   INT             DEFAULT NULL,
    scrumWins                   INT             DEFAULT NULL,
    score                       INT             DEFAULT NULL,
    period                      VARCHAR(50)     NOT NULL,

    -- Precomputed Columns (calculated in the application layer)
    uniqueMatchId               VARCHAR(255)    NOT NULL,
    uniquePlayerId              VARCHAR(255)    NOT NULL,
    uniquePeriodId              VARCHAR(255)    NOT NULL,

    -- Primary Key
    PRIMARY KEY (uniquePeriodId),

    -- Foreign Keys
    FOREIGN KEY (uniqueMatchId)  REFERENCES NRL_mens_match(uniqueMatchId),

    -- Info Foreign Keys
    FOREIGN KEY (uniquePlayerId) REFERENCES player_info(uniquePlayerId)
);
