-- SQLite Schema for AI Red Teaming Lab

CREATE TABLE IF NOT EXISTS assessment_sessions (
    id            TEXT PRIMARY KEY,
    created_at    TEXT NOT NULL,
    target_model  TEXT NOT NULL DEFAULT 'llama2',
    total_attacks INTEGER NOT NULL DEFAULT 0,
    succeeded     INTEGER NOT NULL DEFAULT 0,
    blocked       INTEGER NOT NULL DEFAULT 0,
    success_rate  REAL    NOT NULL DEFAULT 0.0,
    notes         TEXT    DEFAULT '',
    git_sha       TEXT    DEFAULT ''
);

CREATE TABLE IF NOT EXISTS attack_results (
    id            TEXT PRIMARY KEY,
    session_id    TEXT NOT NULL,
    attack_id     TEXT NOT NULL,
    attack_name   TEXT NOT NULL,
    attack_type   TEXT NOT NULL,
    prompt        TEXT NOT NULL,
    response      TEXT NOT NULL,
    success       INTEGER NOT NULL DEFAULT 0,
    reason        TEXT NOT NULL DEFAULT '',
    owasp         TEXT NOT NULL DEFAULT '',
    mitre_atlas   TEXT NOT NULL DEFAULT '',
    risk_rating   TEXT NOT NULL DEFAULT 'MEDIUM',
    timestamp     TEXT NOT NULL,
    FOREIGN KEY (session_id) REFERENCES assessment_sessions(id)
);

CREATE TABLE IF NOT EXISTS retest_results (
    id                   TEXT PRIMARY KEY,
    session_id           TEXT NOT NULL,
    original_attack_id   TEXT NOT NULL,
    attack_name          TEXT NOT NULL,
    attack_type          TEXT NOT NULL,
    prompt               TEXT NOT NULL,
    mitigation_applied   TEXT NOT NULL DEFAULT '',
    retest_success       INTEGER NOT NULL DEFAULT 0,
    mitigation_effective INTEGER NOT NULL DEFAULT 0,
    retest_reason        TEXT NOT NULL DEFAULT '',
    timestamp            TEXT NOT NULL,
    FOREIGN KEY (session_id) REFERENCES assessment_sessions(id)
);

CREATE TABLE IF NOT EXISTS mitigation_logs (
    id            TEXT PRIMARY KEY,
    session_id    TEXT NOT NULL,
    filter_type   TEXT NOT NULL,
    trigger       TEXT NOT NULL,
    original_text TEXT NOT NULL,
    filtered_text TEXT NOT NULL DEFAULT '',
    blocked       INTEGER NOT NULL DEFAULT 0,
    timestamp     TEXT NOT NULL,
    FOREIGN KEY (session_id) REFERENCES assessment_sessions(id)
);

CREATE INDEX IF NOT EXISTS idx_ar_session ON attack_results(session_id);
CREATE INDEX IF NOT EXISTS idx_ar_success ON attack_results(session_id, success);
CREATE INDEX IF NOT EXISTS idx_ar_type    ON attack_results(attack_type);
CREATE INDEX IF NOT EXISTS idx_rr_session ON retest_results(session_id);
CREATE INDEX IF NOT EXISTS idx_ml_session ON mitigation_logs(session_id);
