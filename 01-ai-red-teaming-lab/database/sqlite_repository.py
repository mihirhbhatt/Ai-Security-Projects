# database/sqlite_repository.py
import sqlite3
import os
from database.base_repository import BaseRepository
from database.models import (
    AssessmentSession, AttackResult, RetestResult, MitigationLog,
)


class SQLiteRepository(BaseRepository):

    def __init__(self, db_path: str = "results/redteam.db"):
        self.db_path = db_path
        self.conn    = None

    def connect(self) -> None:
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA foreign_keys=ON")
        print(f"  SQLite connected: {self.db_path}")

    def disconnect(self) -> None:
        if self.conn:
            self.conn.close()
            self.conn = None

    def initialise_schema(self) -> None:
        schema_path = os.path.join(
            os.path.dirname(__file__), "migrations", "sqlite_schema.sql"
        )
        with open(schema_path) as f:
            self.conn.executescript(f.read())
        self.conn.commit()

    # ── Sessions ──────────────────────────────────────────────
    def create_session(self, session: AssessmentSession) -> str:
        self.conn.execute("""
            INSERT INTO assessment_sessions
            (id,created_at,target_model,total_attacks,succeeded,blocked,success_rate,notes,git_sha)
            VALUES (?,?,?,?,?,?,?,?,?)
        """, (session.id, session.created_at, session.target_model,
              session.total_attacks, session.succeeded, session.blocked,
              session.success_rate, session.notes, session.git_sha))
        self.conn.commit()
        return session.id

    def update_session(self, session: AssessmentSession) -> None:
        self.conn.execute("""
            UPDATE assessment_sessions
            SET total_attacks=?,succeeded=?,blocked=?,success_rate=?,notes=?
            WHERE id=?
        """, (session.total_attacks, session.succeeded, session.blocked,
              session.success_rate, session.notes, session.id))
        self.conn.commit()

    def get_session(self, session_id: str) -> dict:
        row = self.conn.execute(
            "SELECT * FROM assessment_sessions WHERE id=?", (session_id,)
        ).fetchone()
        return dict(row) if row else None

    def list_sessions(self, limit: int = 20) -> list:
        rows = self.conn.execute(
            "SELECT * FROM assessment_sessions ORDER BY created_at DESC LIMIT ?",
            (limit,)
        ).fetchall()
        return [dict(r) for r in rows]

    # ── Attack Results ────────────────────────────────────────
    def save_attack_result(self, result: AttackResult) -> str:
        self.conn.execute("""
            INSERT INTO attack_results
            (id,session_id,attack_id,attack_name,attack_type,
             prompt,response,success,reason,owasp,mitre_atlas,risk_rating,timestamp)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (result.id, result.session_id, result.attack_id, result.attack_name,
              result.attack_type, result.prompt, result.response,
              1 if result.success else 0, result.reason, result.owasp,
              result.mitre_atlas, result.risk_rating, result.timestamp))
        self.conn.commit()
        return result.id

    def save_attack_results(self, results: list) -> None:
        self.conn.executemany("""
            INSERT INTO attack_results
            (id,session_id,attack_id,attack_name,attack_type,
             prompt,response,success,reason,owasp,mitre_atlas,risk_rating,timestamp)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, [(r.id, r.session_id, r.attack_id, r.attack_name, r.attack_type,
               r.prompt, r.response, 1 if r.success else 0, r.reason,
               r.owasp, r.mitre_atlas, r.risk_rating, r.timestamp)
              for r in results])
        self.conn.commit()
        print(f"  Saved {len(results)} attack results to SQLite")

    def get_attack_results(self, session_id: str) -> list:
        rows = self.conn.execute(
            "SELECT * FROM attack_results WHERE session_id=? ORDER BY timestamp",
            (session_id,)
        ).fetchall()
        out = []
        for r in rows:
            d = dict(r)
            d["success"] = bool(d["success"])
            out.append(d)
        return out

    def get_successful_attacks(self, session_id: str) -> list:
        rows = self.conn.execute(
            "SELECT * FROM attack_results WHERE session_id=? AND success=1",
            (session_id,)
        ).fetchall()
        out = []
        for r in rows:
            d = dict(r)
            d["success"] = True
            out.append(d)
        return out

    # ── Retest Results ────────────────────────────────────────
    def save_retest_result(self, result: RetestResult) -> str:
        self.conn.execute("""
            INSERT INTO retest_results
            (id,session_id,original_attack_id,attack_name,attack_type,
             prompt,mitigation_applied,retest_success,mitigation_effective,retest_reason,timestamp)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """, (result.id, result.session_id, result.original_attack_id,
              result.attack_name, result.attack_type, result.prompt,
              result.mitigation_applied,
              1 if result.retest_success else 0,
              1 if result.mitigation_effective else 0,
              result.retest_reason, result.timestamp))
        self.conn.commit()
        return result.id

    def save_retest_results(self, results: list) -> None:
        self.conn.executemany("""
            INSERT INTO retest_results
            (id,session_id,original_attack_id,attack_name,attack_type,
             prompt,mitigation_applied,retest_success,mitigation_effective,retest_reason,timestamp)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """, [(r.id, r.session_id, r.original_attack_id, r.attack_name,
               r.attack_type, r.prompt, r.mitigation_applied,
               1 if r.retest_success else 0,
               1 if r.mitigation_effective else 0,
               r.retest_reason, r.timestamp)
              for r in results])
        self.conn.commit()
        print(f"  Saved {len(results)} retest results to SQLite")

    def get_retest_results(self, session_id: str) -> list:
        rows = self.conn.execute(
            "SELECT * FROM retest_results WHERE session_id=? ORDER BY timestamp",
            (session_id,)
        ).fetchall()
        out = []
        for r in rows:
            d = dict(r)
            d["retest_success"]       = bool(d["retest_success"])
            d["mitigation_effective"] = bool(d["mitigation_effective"])
            out.append(d)
        return out

    # ── Mitigation Logs ───────────────────────────────────────
    def log_mitigation(self, log: MitigationLog) -> str:
        self.conn.execute("""
            INSERT INTO mitigation_logs
            (id,session_id,filter_type,trigger,original_text,filtered_text,blocked,timestamp)
            VALUES (?,?,?,?,?,?,?,?)
        """, (log.id, log.session_id, log.filter_type, log.trigger,
              log.original_text, log.filtered_text,
              1 if log.blocked else 0, log.timestamp))
        self.conn.commit()
        return log.id

    def get_mitigation_logs(self, session_id: str) -> list:
        rows = self.conn.execute(
            "SELECT * FROM mitigation_logs WHERE session_id=? ORDER BY timestamp",
            (session_id,)
        ).fetchall()
        out = []
        for r in rows:
            d = dict(r)
            d["blocked"] = bool(d["blocked"])
            out.append(d)
        return out

    # ── Analytics ─────────────────────────────────────────────
    def get_attack_stats_by_type(self, session_id: str) -> list:
        rows = self.conn.execute("""
            SELECT
                attack_type,
                COUNT(*)                AS total,
                SUM(success)            AS succeeded,
                COUNT(*)-SUM(success)   AS blocked
            FROM attack_results
            WHERE session_id=?
            GROUP BY attack_type
            ORDER BY succeeded DESC
        """, (session_id,)).fetchall()
        return [dict(r) for r in rows]

    def get_historical_trend(self, limit: int = 10) -> list:
        rows = self.conn.execute("""
            SELECT id,created_at,target_model,total_attacks,succeeded,blocked,success_rate
            FROM assessment_sessions
            ORDER BY created_at DESC LIMIT ?
        """, (limit,)).fetchall()
        return [dict(r) for r in rows]
