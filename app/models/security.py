from pydantic import BaseModel, IPvAnyAddress, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ReputationLevel(str, Enum):
    SAFE = "safe"
    SUSPICIOUS = "suspicious"
    MALICIOUS = "malicious"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class IPCheckRequest(BaseModel):
    ip: IPvAnyAddress
    context: Optional[str] = None
    check_sources: Optional[List[str]] = None


class CallerCheckRequest(BaseModel):
    phone_number: str = Field(..., min_length=10, max_length=15)
    ip: Optional[IPvAnyAddress] = None
    context: Optional[str] = None


class SecurityScore(BaseModel):
    ip: str
    score: int = Field(..., ge=0, le=100)
    reputation: ReputationLevel
    sources: List[str]
    last_updated: datetime
    details: Dict[str, Any] = {}
    confidence: float = Field(..., ge=0.0, le=1.0)


class CallerInfo(BaseModel):
    phone_number: str
    risk_level: RiskLevel
    spam_reports: int = 0
    location: Optional[str] = None
    carrier: Optional[str] = None
    last_seen: Optional[datetime] = None
    reputation_score: float = Field(..., ge=0.0, le=1.0)
    blocked_count: int = 0


class ApiResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
