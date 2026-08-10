# database/postgres_repository.py
"""
PostgreSQL repository.
Compatible with Supabase, AWS RDS, Neon, Cloud SQL, local PG.
Install: pip install psycopg2-binary
"""
import os
import psycopg2
import psycopg2.extras
from database.base_repository import BaseRepository
from database.models import (
    AssessmentSession, AttackResult, RetestResult, MitigationLog,
)


class PostgreSQLRepository(BaseRepository):

    def __init__(self, connection_url: str, ssl_mode: str = "require"):
        self.connection_url = connection_url
        self.ssl_mode       = ssl_mode
        self.conn           = None

    def connect(self) -> None:
        self.conn = psycopg2.connect(
            self.connection_url,
            sslmode=self.ssl_mode,
            cursor_factory=psycopg2.extras.RealDictCursor,
        )
        self.conn.autocommit = False
        print("  PostgreSQL connected")

    def disconnect(self) -> None:
        if self.conn:
            self.conn.close()
            self.conn = None

    def initialise_schema(self) -> None:
        schema_path = os.path.join(
            os.path.dirname(__file__), "migrations", "postgres_schema.sql"
        )
        with open(schema_path) as f:
            sql = f.read()
        with self.conn.cursor() as cur:
            cur.execute(sql)
        self.conn.commit()
        print("  PostgreSQL schema initialised")

    def create_session(self, session: AssessmentSession) -> str:
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO assessment_sessions
                (id,created_at,target_model,total_attacks,succeeded,blocked,success_rate,notes,git_sha)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (session.id, session.created_at, session.target_model,
                  session.total_attacks, session.succeeded, session.blocked,
                  session.success_rate, session.notes, session.git_sha))
        self.conn.commit()
        return session.id

    def update_session(self, session: AssessmentSession) -> None:
        with self.conn.cursor() as cur:
            cur.execute("""
                UPDATE assessment_sessions
                SET total_attacks=%s,succeeded=%s,blocked=%s,success_rate=%s,notes=%s
                WHERE id=%s
            """, (session.total_attacks, session.succeeded, session.blocked,
                  session.success_rate, session.notes, session.id))
        self.conn.commit()

    def get_session(self, session_id: str) -> dict:
        with self.conn.cursor() as cur:
            cur.execute("SELECT * FROM assessment_sessions WHERE id=%s", (session_id,))
            row = cur.fetchone()
        return dict(row) if row else None

    def list_sessions(self, limit: int = 20) -> list:
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM assessment_sessions ORDER BY created_at DESC LIMIT %s",
                (limit,))
            return [dict(r) for r in cur.fetchall()]

    def save_attack_result(self, result: AttackResult) -> str:
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO attack_results
                (id,session_id,attack_id,attack_name,attack_type,
                 prompt,response,success,reason,owasp,mitre_atlas,risk_rating,timestamp)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (result.id, result.session_id, result.attack_id, result.attack_name,
                  result.attack_type, result.prompt, result.response, result.success,
                  result.reason, result.owasp, result.mitre_atlas,
                  result.risk_rating, result.timestamp))
        self.conn.commit()
        return result.id

    def save_attack_results(self, results: list) -> None:
        with self.conn.cursor() as cur:
            psycopg2.extras.execute_batch(cur, """
                INSERT INTO attack_results
                (id,session_id,attack_id,attack_name,attack_type,
                 prompt,response,success,reason,owasp,mitre_atlas,risk_rating,timestamp)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, [(r.id, r.session_id, r.attack_id, r.attack_name, r.attack_type,
                   r.prompt, r.response, r.success, r.reason,
                   r.owasp, r.mitre_atlas, r.risk_rating, r.timestamp)
                  for r in results])
        self.conn.commit()
        print(f"  Saved {len(results)} attack results to PostgreSQL")

    def get_attack_results(self, session_id: str) -> list:
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM attack_results WHERE session_id=%s ORDER BY timestamp",
                (session_id,))
            return [dict(r) for r in cur.fetchall()]

    def get_successful_attacks(self, session_id: str) -> list:
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM attack_results WHERE session_id=%s AND success=TRUE",
                (session_id,))
            return [dict(r) for r in cur.fetchall()]

    def save_retest_result(self, result: RetestResult) -> str:
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO retest_results
                (id,session_id,original_attack_id,attack_name,attack_type,
                 prompt,mitigation_applied,retest_success,mitigation_effective,retest_reason,timestamp)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (result.id, result.session_id, result.original_attack_id,
                  result.attack_name, result.attack_type, result.prompt,
                  result.mitigation_applied, result.retest_success,
                  result.mitigation_effective, result.retest_reason, result.timestamp))
        self.conn.commit()
        return result.id

    def save_retest_results(self, results: list) -> None:
        with self.conn.cursor() as cur:
            psycopg2.extras.execute_batch(cur, """
                INSERT INTO retest_results
                (id,session_id,original_attack_id,attack_name,attack_type,
                 prompt,mitigation_applied,retest_success,mitigation_effective,retest_reason,timestamp)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, [(r.id, r.session_id, r.original_attack_id, r.attack_name,
                   r.attack_type, r.prompt, r.mitigation_applied,
                   r.retest_success, r.mitigation_effective,
                   r.retest_reason, r.timestamp) for r in results])
        self.conn.commit()

    def get_retest_results(self, session_id: str) -> list:
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM retest_results WHERE session_id=%s ORDER BY timestamp",
                (session_id,))
            return [dict(r) for r in cur.fetchall()]

    def log_mitigation(self, log: MitigationLog) -> str:
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO mitigation_logs
                (id,session_id,filter_type,trigger,original_text,filtered_text,blocked,timestamp)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            """, (log.id, log.session_id, log.filter_type, log.trigger,
                  log.original_text, log.filtered_text, log.blocked, log.timestamp))
        self.conn.commit()
        return log.id

    def get_mitigation_logs(self, session_id: str) -> list:
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM mitigation_logs WHERE session_id=%s ORDER BY timestamp",
                (session_id,))
            return [dict(r) for r in cur.fetchall()]

    def get_attack_stats_by_type(self, session_id: str) -> list:
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT attack_type,
                       COUNT(*) AS total,
                       SUM(CASE WHEN success THEN 1 ELSE 0 END) AS succeeded,
                       SUM(CASE WHEN NOT success THEN 1 ELSE 0 END) AS blocked
                FROM attack_results WHERE session_id=%s
                GROUP BY attack_type ORDER BY succeeded DESC
            """, (session_id,))
            return [dict(r) for r in cur.fetchall()]

    def get_historical_trend(self, limit: int = 10) -> list:
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT id,created_at,target_model,total_attacks,succeeded,blocked,success_rate
                FROM assessment_sessions ORDER BY created_at DESC LIMIT %s
            """, (limit,))
            return [dict(r) for r in cur.fetchall()]
