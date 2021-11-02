CREATE TABLE IF NOT EXISTS Migrations (
    id          SERIAL PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS Users (
    id              BIGINT PRIMARY KEY,
    username        VARCHAR(255) NOT NULL,
    dm_id           BIGINT NOT NULL,
    blocked_until   TIMESTAMP DEFAULT NULL
);

CREATE TABLE IF NOT EXISTS Threads (
    id              VARCHAR(255) PRIMARY KEY,
    channel_id      BIGINT NOT NULL UNIQUE,
    member_id       BIGINT NOT NULL REFERENCES Users(id) ON DELETE CASCADE,
    created_at      TIMESTAMP NOT NULL,
    active          BOOLEAN NOT NULL DEFAULT TRUE,
    closed          BOOLEAN NOT NULL DEFAULT FALSE,
    alerts          VARCHAR(255) NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS ThreadMessages (
    id              SERIAL PRIMARY KEY,
    thread_id       VARCHAR(255) NOT NULL REFERENCES Threads(id) ON DELETE CASCADE,
    message_id      BIGINT NOT NULL,
    dm_message_id   BIGINT DEFAULT NULL,
    created_at      TIMESTAMP NOT NULL,
    content         TEXT NOT NULL,
    deleted         BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS ModeratorConfigs (
    id              BIGINT PRIMARY KEY,
    config          TEXT NOT NULL DEFAULT '{}'
);
