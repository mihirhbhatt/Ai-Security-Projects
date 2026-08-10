# database/mongodb_repository.py
"""
MongoDB Atlas repository.
Install: pip install pymongo dnspython
"""
from pymongo        import MongoClient, ASCENDING, DESCENDING
from database.base_repository import BaseRepository
from database.models import (
    AssessmentSession, AttackResult, RetestResult, MitigationLog,
)


class MongoDBRepository(BaseRepository):

    def __init__(self, connection_url: str, db_name: str = "redteam_db"):
        self.connection_url = connection_url
        self.db_name        = db_name
        self.client         = None
        self.db             = None

    def connect(self) -> None:
        self.client = MongoClient(self.connection_url, serverSelectionTimeoutMS=5000)
        self.client.admin.command("ping")
        self.db = self.client[self.db_name]
        print(f"  MongoDB connected: {self.db_name}")

    def disconnect(self) -> None:
        if self.client:
            self.client.close()
            self.client = None
            self.db     = None

    def initialise_schema(self) -> None:
        self.db.assessment_sessions.create_index([("created_at", DESCENDING)])
        self.db.attack_results.create_index([("session_id", ASCENDING), ("success", ASCENDING)])
        self.db.retest_results.create_index([("session_id", ASCENDING)])
        self.db.mitigation_logs.create_index([("session_id", ASCENDING)])
        print("  MongoDB indexes initialised")

    def _to_doc(self, obj) -> dict:
        d = obj.to_dict()
        d["_id"] = d.pop("id")
        return d

    def _from_doc(self, doc: dict) -> dict:
        if doc:
            doc["id"] = doc.pop("_id")
        return doc

    def create_session(self, session: AssessmentSession) -> str:
        self.db.assessment_sessions.insert_one(self._to_doc(session))
        return session.id

    def update_session(self, session: AssessmentSession) -> None:
        self.db.assessment_sessions.update_one(
            {"_id": session.id},
            {"$set": {
                "total_attacks": session.total_attacks,
                "succeeded":     session.succeeded,
                "blocked":       session.blocked,
                "success_rate":  session.success_rate,
                "notes":         session.notes,
            }}
        )

    def get_session(self, session_id: str) -> dict:
        doc = self.db.assessment_sessions.find_one({"_id": session_id})
        return self._from_doc(doc) if doc else None

    def list_sessions(self, limit: int = 20) -> list:
        return [self._from_doc(d) for d in
                self.db.assessment_sessions.find({}, sort=[("created_at", DESCENDING)], limit=limit)]

    def save_attack_result(self, result: AttackResult) -> str:
        self.db.attack_results.insert_one(self._to_doc(result))
        return result.id

    def save_attack_results(self, results: list) -> None:
        if results:
            self.db.attack_results.insert_many([self._to_doc(r) for r in results])
            print(f"  Saved {len(results)} attack results to MongoDB")

    def get_attack_results(self, session_id: str) -> list:
        return [self._from_doc(d) for d in
                self.db.attack_results.find({"session_id": session_id},
                                             sort=[("timestamp", ASCENDING)])]

    def get_successful_attacks(self, session_id: str) -> list:
        return [self._from_doc(d) for d in
                self.db.attack_results.find({"session_id": session_id, "success": True})]

    def save_retest_result(self, result: RetestResult) -> str:
        self.db.retest_results.insert_one(self._to_doc(result))
        return result.id

    def save_retest_results(self, results: list) -> None:
        if results:
            self.db.retest_results.insert_many([self._to_doc(r) for r in results])

    def get_retest_results(self, session_id: str) -> list:
        return [self._from_doc(d) for d in
                self.db.retest_results.find({"session_id": session_id},
                                             sort=[("timestamp", ASCENDING)])]

    def log_mitigation(self, log: MitigationLog) -> str:
        self.db.mitigation_logs.insert_one(self._to_doc(log))
        return log.id

    def get_mitigation_logs(self, session_id: str) -> list:
        return [self._from_doc(d) for d in
                self.db.mitigation_logs.find({"session_id": session_id},
                                              sort=[("timestamp", ASCENDING)])]

    def get_attack_stats_by_type(self, session_id: str) -> list:
        pipeline = [
            {"$match": {"session_id": session_id}},
            {"$group": {
                "_id":       "$attack_type",
                "total":     {"$sum": 1},
                "succeeded": {"$sum": {"$cond": ["$success", 1, 0]}},
                "blocked":   {"$sum": {"$cond": ["$success", 0, 1]}},
            }},
            {"$project": {"attack_type": "$_id", "total": 1, "succeeded": 1, "blocked": 1, "_id": 0}},
            {"$sort": {"succeeded": -1}},
        ]
        return list(self.db.attack_results.aggregate(pipeline))

    def get_historical_trend(self, limit: int = 10) -> list:
        return [self._from_doc(d) for d in
                self.db.assessment_sessions.find({},
                    sort=[("created_at", DESCENDING)], limit=limit)]
