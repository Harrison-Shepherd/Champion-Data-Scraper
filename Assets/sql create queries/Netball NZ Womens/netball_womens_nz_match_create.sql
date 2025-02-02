CREATE TABLE netball_womens_nz_match (
    -- Match Statistics
    rebounds                    INT             DEFAULT NULL,
    turnoverHeld                INT             DEFAULT NULL,
    centrePassToGoalPerc        INT             DEFAULT NULL,
    penalties                   INT             DEFAULT NULL,
    deflectionWithNoGain        INT             DEFAULT NULL,
    generalPlayTurnovers        INT             DEFAULT NULL,
    interceptPassThrown         INT             DEFAULT NULL,
    gain                        INT             DEFAULT NULL,
    points                      INT             DEFAULT NULL,
    netPoints                   INT             DEFAULT NULL,
    goalMisses                  INT             DEFAULT NULL,
    blocked                     INT             DEFAULT NULL,
    deflectionWithGain          INT             DEFAULT NULL,
    deflections                 INT             DEFAULT NULL,
    defensiveRebounds           INT             DEFAULT NULL,
    offensiveRebounds           INT             DEFAULT NULL,
    goalAssists                 INT             DEFAULT NULL,
    tossUpWin                   INT             DEFAULT NULL,
    centrePassReceives          INT             DEFAULT NULL,
    obstructionPenalties        INT             DEFAULT NULL,
    feeds                       INT             DEFAULT NULL,
    passes                      INT             DEFAULT NULL,
    playerId                    VARCHAR(50)     NOT NULL,
    goals                       INT             DEFAULT NULL,
    offsides                    INT             DEFAULT NULL,
    secondPhaseReceive          INT             DEFAULT NULL,
    badPasses                   INT             DEFAULT NULL,
    breaks                      INT             DEFAULT NULL,
    blocks                      INT             DEFAULT NULL,
    badHands                    INT             DEFAULT NULL,
    missedGoalTurnover          INT             DEFAULT NULL,
    turnovers                   INT             DEFAULT NULL,
    squadId                     VARCHAR(50)     NOT NULL,
    deflectionPossessionGain    INT             DEFAULT NULL,
    possessionChanges           INT             DEFAULT NULL,
    possessions                 INT             DEFAULT NULL,
    startingPositionCode        VARCHAR(50)     NOT NULL,
    goalAttempts                INT             DEFAULT NULL,
    contactPenalties            INT             DEFAULT NULL,
    quartersPlayed              INT             DEFAULT NULL,
    minutesPlayed               INT             DEFAULT NULL,
    feedWithAttempt             INT             DEFAULT NULL,
    unforcedTurnovers           INT             DEFAULT NULL,
    pickups                     INT             DEFAULT NULL,
    currentPositionCode         VARCHAR(50)     NOT NULL,
    gainToGoalPerc              INT             DEFAULT NULL,
    intercepts                  INT             DEFAULT NULL,

    -- Player Information
    shortDisplayName            VARCHAR(45)     NOT NULL,
    firstname                   VARCHAR(45)     NOT NULL,
    surname                     VARCHAR(45)     NOT NULL,
    displayName                 VARCHAR(45)     NOT NULL,
    squadName                   VARCHAR(45)     NOT NULL,
    fixtureYear                 VARCHAR(50)     NOT NULL,

    -- Match Information
    homeId                      VARCHAR(50)     NOT NULL,
    awayId                      VARCHAR(50)     NOT NULL,
    opponent                    VARCHAR(50)     NOT NULL,
    round                       INT             NOT NULL,
    fixtureId                   VARCHAR(50)     NOT NULL,
    sportId                     VARCHAR(50)     NOT NULL,
    matchId                     VARCHAR(50)     NOT NULL,

    -- Precomputed Columns (calculated in the application layer)
    uniqueFixtureId             VARCHAR(255)    NOT NULL,
    uniquePlayerId              VARCHAR(255)    NOT NULL,
    uniqueSquadId               VARCHAR(255)    NOT NULL,
    uniqueSportId               VARCHAR(255)    NOT NULL,

    -- Composite Primary Key
    uniqueMatchId               VARCHAR(255)    NOT NULL,
    PRIMARY KEY (uniqueMatchId),

    -- Foreign Keys
    FOREIGN KEY (uniqueFixtureId)    REFERENCES netball_womens_nz_fixture(uniqueFixtureId),
    FOREIGN KEY (uniquePlayerId)     REFERENCES player_info(uniquePlayerId),
    FOREIGN KEY (uniqueSquadId)      REFERENCES squad_info(uniqueSquadId),
    FOREIGN KEY (uniqueSportId)      REFERENCES sport_info(uniqueSportId)
);
