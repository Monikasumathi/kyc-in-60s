from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from sqlalchemy import Column, String, DateTime, JSON, Float, Integer, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ApplicationStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    UNDER_REVIEW = "under_review"


class ImageQualityCheck(BaseModel):
    """Image quality assessment result"""
    is_acceptable: bool
    blur_score: float
    glare_score: float
    crop_score: float
    issues: List[str]
    suggestions: List[str]


class ExtractedField(BaseModel):
    """Extracted field with confidence"""
    value: str
    confidence: float
    field_name: str


class ExtractedData(BaseModel):
    """All extracted data from document"""
    full_name: ExtractedField
    date_of_birth: ExtractedField
    id_number: ExtractedField
    address: ExtractedField
    document_type: ExtractedField
    expiry_date: Optional[ExtractedField] = None


class FaceMatchResult(BaseModel):
    """Face matching result"""
    is_match: bool
    confidence: float
    threshold: float = 0.6


class RiskAssessment(BaseModel):
    """Risk assessment with explainability"""
    risk_level: RiskLevel
    confidence: float
    reason_codes: List[str]
    factors: Dict[str, Any]
    score: float


class KYCDecision(BaseModel):
    """Final KYC decision"""
    decision: ApplicationStatus
    risk_assessment: RiskAssessment
    requires_review: bool
    auto_approved: bool
    timestamp: datetime


class KYCApplication(Base):
    """Database model for KYC applications"""
    __tablename__ = "kyc_applications"

    id = Column(String, primary_key=True)
    customer_id = Column(String, nullable=False)
    status = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Document data
    document_path = Column(String)
    selfie_path = Column(String)
    
    # Extracted data
    extracted_data = Column(JSON)
    
    # Quality checks
    quality_checks = Column(JSON)
    
    # Face match
    face_match_result = Column(JSON)
    
    # Risk assessment
    risk_assessment = Column(JSON)
    
    # Decision
    decision = Column(JSON)
    
    # Reviewer info
    reviewer_id = Column(String, nullable=True)
    reviewer_notes = Column(String, nullable=True)
    reviewed_at = Column(DateTime, nullable=True)


class AuditLog(Base):
    """Audit trail for compliance"""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    application_id = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    action = Column(String, nullable=False)
    actor = Column(String, nullable=False)  # system or user_id
    details = Column(JSON)
    model_version = Column(String, nullable=True)
    
    # Redacted inputs for compliance
    redacted_inputs = Column(JSON)
    
    # Scores and thresholds
    scores = Column(JSON)
    thresholds = Column(JSON)


class KYCSubmissionRequest(BaseModel):
    """API request for KYC submission"""
    customer_id: str


class KYCSubmissionResponse(BaseModel):
    """API response for KYC submission"""
    application_id: str
    status: ApplicationStatus
    message: str
    next_steps: List[str]
    decision: Optional[KYCDecision] = None
    estimated_time: Optional[str] = None


class ReviewerDecision(BaseModel):
    """Reviewer decision on application"""
    application_id: str
    reviewer_id: str
    decision: ApplicationStatus
    notes: str

