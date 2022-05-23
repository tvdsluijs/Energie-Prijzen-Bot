PRAGMA foreign_keys = 0;

CREATE TABLE sqlitestudio_temp_table AS SELECT *
                                          FROM users;

DROP TABLE users;

CREATE TABLE users (
    user_id           INTEGER PRIMARY KEY,
    datetime          INTEGER,
    kaal_opslag_allin INTEGER DEFAULT (1),
    ochtend           INTEGER,
    opslag            DOUBLE,
    melding_lager_dan DECIMAL DEFAULT (0.001),
    melding_hoger_dan DECIMAL,
    middag            INTEGER
);

INSERT INTO users (
                      user_id,
                      datetime,
                      kaal_opslag_allin,
                      ochtend,
                      opslag,
                      melding_lager_dan,
                      melding_hoger_dan
                  )
                  SELECT user_id,
                         datetime,
                         kaal_opslag_allin,
                         ochtend,
                         opslag,
                         melding_lager_dan,
                         melding_hoger_dan
                    FROM sqlitestudio_temp_table;

DROP TABLE sqlitestudio_temp_table;

PRAGMA foreign_keys = 1;
