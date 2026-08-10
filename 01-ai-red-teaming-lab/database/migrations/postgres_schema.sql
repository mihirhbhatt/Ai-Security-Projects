-- PostgreSQL Schema for AI Red Teaming Lab

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS assessment_sessions (
    id            TEXT        PRIMARY KEY,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    target_model  TEXT        NOT NULL DEFAULT 'llama2',
    total_attacks INTEGER     NOT NULL DEFAULT 0,
    succeeded     INTEGER     NOT NULL DEFAULT 0,
    blocked       INTEGER     NOT NULL DEFAULT 0,
    success_rate  NUMERIC(5,2) NOT NULL DEFAULT 0.0,
    notes         TEXT        DEFAULT '',
    git_sha       TEXT        DEFAULT ''
);

CREATE TABLE IF NOT EXISTS attack_results (
    id            TEXT        PRIMARY KEY,
    session_id    TEXT        NOT NULL REFERENCES assessment_sessions(id) ON DELETE CASCADE,
    attack_id     TEXT        NOT NULL,
    attack_name   TEXT        NOT NULL,
    attack_type   TEXT        NOT NULL,
    prompt        TEXT        NOT NULL,
    response      TEXT        NOT NULL,
    success       BOOLEAN     NOT NULL DEFAULT FALSE,
    reason        TEXT        NOT NULL DEFAULT '',
    owasp         TEXT        NOT NULL DEFAULT '',
    mitre_atlas   TEXT        NOT NULL DEFAULT '',
    risk_rating   TEXT        NOT NULL DEFAULT 'MEDIUM',
    timestamp     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS retest_results (
    id                   TEXT        PRIMARY KEY,
    session_id           TEXT        NOT NULL REFERENCES assessment_sessions(id) ON DELETE CASCADE,
    original_attack_id   TEXT        NOT NULL,
    attack_name          TEXT        NOT NULL,
    attack_type          TEXT        NOT NULL,
    prompt               TEXT        NOT NULL,
    mitigation_applied   TEXT        NOT NULL DEFAULT '',
    retest_success       BOOLEAN     NOT NULL DEFAULT FALSE,
    mitigation_effective BOOLEAN     NOT NULL DEFAULT FALSE,
    retest_reason        TEXT        NOT NULL DEFAULT '',
    timestamp            TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS mitigation_logs (
    id            TEXT        PRIMARY KEY,
    session_id    TEXT        NOT NULL REFERENCES assessment_sessions(id) ON DELETE CASCADE,
    filter_type   TEXT        NOT NULL,
    trigger       TEXT        NOT NULL,
    original_text TEXT        NOT NULL,
    filtered_text TEXT        NOT NULL DEFAULT '',
    blocked       BOOLEAN     NOT NULL DEFAULT FALSE,
    timestamp     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ar_session ON attack_results(session_id);
CREATE INDEX IF NOT EXISTS idx_ar_success ON attack_results(session_id, success);
CREATE INDEX IF NOT EXISTS idx_ar_type    ON attack_results(attack_type);
CREATE INDEX IF NOT EXISTS idx_rr_session ON retest_results(session_id);
CREATE INDEX IF NOT EXISTS idx_ml_session ON mitigation_logs(session_id);
