# database/models.py
from dataclasses import dataclass, field, asdict
from datetime    import datetime
from typing      import Optional
import uuid


def new_uuid() -> str:
    return str(uuid.uuid4())


def now_iso() -> str:
    return datetime.utcnow().isoformat()


@dataclass
class AssessmentSession:
    id:            str   = field(default_factory=new_uuid)
    created_at:    str   = field(default_factory=now_iso)
    target_model:  str   = "llama2"
    total_attacks: int   = 0
    succeeded:     int   = 0
    blocked:       int   = 0
    success_rate:  float = 0.0
    notes:         str   = ""
    git_sha:       str   = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class AttackResult:
    id:           str  = field(default_factory=new_uuid)
    session_id:   str  = ""
    attack_id:    str  = ""
    attack_name:  str  = ""
    attack_type:  str  = ""
    prompt:       str  = ""
    response:     str  = ""
    success:      bool = False
    reason:       str  = ""
    owasp:        str  = ""
    mitre_atlas:  str  = ""
    risk_rating:  str  = ""
    timestamp:    str  = field(default_factory=now_iso)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class RetestResult:
    id:                   str  = field(default_factory=new_uuid)
    session_id:           str  = ""
    original_attack_id:   str  = ""
    attack_name:          str  = ""
    attack_type:          str  = ""
    prompt:               str  = ""
    mitigation_applied:   str  = ""
    retest_success:       bool = False
    mitigation_effective: bool = False
    retest_reason:        str  = ""
    timestamp:            str  = field(default_factory=now_iso)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class MitigationLog:
    id:            str  = field(default_factory=new_uuid)
    session_id:    str  = ""
    filter_type:   str  = ""
    trigger:       str  = ""
    original_text: str  = ""
    filtered_text: str  = ""
    blocked:       bool = False
    timestamp:     str  = field(default_factory=now_iso)

    def to_dict(self) -> dict:
        return asdict(self)
