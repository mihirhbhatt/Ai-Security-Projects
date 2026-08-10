# database/base_repository.py
from abc      import ABC, abstractmethod
from database.models import (
    AssessmentSession, AttackResult, RetestResult, MitigationLog,
)


class BaseRepository(ABC):

    @abstractmethod
    def connect(self) -> None: ...

    @abstractmethod
    def disconnect(self) -> None: ...

    @abstractmethod
    def initialise_schema(self) -> None: ...

    @abstractmethod
    def create_session(self, session: AssessmentSession) -> str: ...

    @abstractmethod
    def update_session(self, session: AssessmentSession) -> None: ...

    @abstractmethod
    def get_session(self, session_id: str) -> dict: ...

    @abstractmethod
    def list_sessions(self, limit: int = 20) -> list: ...

    @abstractmethod
    def save_attack_result(self, result: AttackResult) -> str: ...

    @abstractmethod
    def save_attack_results(self, results: list) -> None: ...

    @abstractmethod
    def get_attack_results(self, session_id: str) -> list: ...

    @abstractmethod
    def get_successful_attacks(self, session_id: str) -> list: ...

    @abstractmethod
    def save_retest_result(self, result: RetestResult) -> str: ...

    @abstractmethod
    def save_retest_results(self, results: list) -> None: ...

    @abstractmethod
    def get_retest_results(self, session_id: str) -> list: ...

    @abstractmethod
    def log_mitigation(self, log: MitigationLog) -> str: ...

    @abstractmethod
    def get_mitigation_logs(self, session_id: str) -> list: ...

    @abstractmethod
    def get_attack_stats_by_type(self, session_id: str) -> list: ...

    @abstractmethod
    def get_historical_trend(self, limit: int = 10) -> list: ...

    def __enter__(self):
        self.connect()
        self.initialise_schema()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
        return False
