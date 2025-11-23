"""
KYC Orchestration Service
Coordinates all AI services to process KYC applications
"""

from sqlalchemy.orm import Session
from typing import Dict, Any, List
from datetime import datetime
import json
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables (for LLM configuration)
# Find .env file in backend directory
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path, override=True)

from ..models import (
    KYCApplication, ApplicationStatus, KYCDecision, 
    RiskLevel, ExtractedData, ImageQualityCheck, FaceMatchResult
)
from .ocr_service import OCRService
from .image_quality import ImageQualityService
from .face_match import FaceMatchService
from .risk_engine import RiskEngine
from .audit_service import AuditService
from .ai_agents import KYCAgentSystem


class KYCResult:
    """Container for KYC processing results"""
    def __init__(
        self,
        application_id: str,
        quality_check: ImageQualityCheck,
        extracted_data: ExtractedData,
        face_match: FaceMatchResult,
        decision: KYCDecision
    ):
        self.application_id = application_id
        self.quality_check = quality_check
        self.extracted_data = extracted_data
        self.face_match = face_match
        self.decision = decision
        self.agent_review = None  # Will be set by orchestrator


class KYCOrchestrator:
    """
    Main orchestrator for KYC processing
    Coordinates all AI services and makes final decisions
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.ocr_service = OCRService()
        self.quality_service = ImageQualityService()
        self.face_service = FaceMatchService()
        self.risk_engine = RiskEngine()
        self.audit_service = AuditService(db)
        self.ai_agents = KYCAgentSystem()  # Initialize AI agents
    
    def process_application(
        self,
        application_id: str,
        customer_id: str,
        document_path: str,
        selfie_path: str
    ) -> KYCResult:
        """
        Process complete KYC application through all stages
        
        Args:
            application_id: Unique application ID
            customer_id: Customer identifier
            document_path: Path to document image
            selfie_path: Path to selfie image
            
        Returns:
            KYCResult with all processing outcomes and final decision
        """
        
        # Step 1: Image Quality Check
        self._log_step(application_id, "IMAGE_QUALITY_CHECK_STARTED", customer_id)
        quality_check = self.quality_service.check_quality(document_path)
        
        self.audit_service.log_action(
            application_id=application_id,
            action="IMAGE_QUALITY_CHECK_COMPLETED",
            actor="system",
            details={
                "is_acceptable": quality_check.is_acceptable,
                "issues": quality_check.issues
            },
            scores={
                "blur_score": quality_check.blur_score,
                "glare_score": quality_check.glare_score,
                "crop_score": quality_check.crop_score
            },
            thresholds={
                "blur_threshold": self.quality_service.BLUR_THRESHOLD,
                "glare_threshold": self.quality_service.GLARE_THRESHOLD
            }
        )
        
        # Step 2: OCR and Data Extraction
        self._log_step(application_id, "OCR_EXTRACTION_STARTED", customer_id)
        extracted_data = self.ocr_service.extract_data(document_path)
        
        self.audit_service.log_action(
            application_id=application_id,
            action="OCR_EXTRACTION_COMPLETED",
            actor="system",
            details={
                "fields_extracted": [
                    extracted_data.full_name.field_name,
                    extracted_data.date_of_birth.field_name,
                    extracted_data.id_number.field_name,
                    extracted_data.address.field_name
                ]
            },
            scores={
                "name_confidence": extracted_data.full_name.confidence,
                "dob_confidence": extracted_data.date_of_birth.confidence,
                "id_confidence": extracted_data.id_number.confidence,
                "address_confidence": extracted_data.address.confidence
            }
        )
        
        # Step 3: Face Matching
        self._log_step(application_id, "FACE_MATCHING_STARTED", customer_id)
        face_match = self.face_service.match_faces(selfie_path, document_path)
        
        self.audit_service.log_action(
            application_id=application_id,
            action="FACE_MATCHING_COMPLETED",
            actor="system",
            details={
                "is_match": face_match.is_match
            },
            scores={
                "confidence": face_match.confidence
            },
            thresholds={
                "match_threshold": face_match.threshold
            }
        )
        
        # Step 4: Risk Assessment
        self._log_step(application_id, "RISK_ASSESSMENT_STARTED", customer_id)
        risk_assessment = self.risk_engine.assess_risk(
            extracted_data=extracted_data,
            quality_check=quality_check,
            face_match=face_match
        )
        
        self.audit_service.log_action(
            application_id=application_id,
            action="RISK_ASSESSMENT_COMPLETED",
            actor="system",
            details={
                "risk_level": risk_assessment.risk_level.value,
                "reason_codes": risk_assessment.reason_codes
            },
            scores={
                "risk_score": risk_assessment.score,
                "confidence": risk_assessment.confidence
            },
            thresholds={
                "low_risk_threshold": self.risk_engine.LOW_RISK_THRESHOLD,
                "medium_risk_threshold": self.risk_engine.MEDIUM_RISK_THRESHOLD
            }
        )
        
        # Step 5: AI Agent Review (NEW!)
        self._log_step(application_id, "AI_AGENT_REVIEW_STARTED", customer_id)
        
        agent_review = self.ai_agents.review_application(
            extracted_data=json.loads(extracted_data.model_dump_json()),
            quality_check=json.loads(quality_check.model_dump_json()),
            face_match=json.loads(face_match.model_dump_json()),
            risk_assessment=json.loads(risk_assessment.model_dump_json())
        )
        
        self.audit_service.log_action(
            application_id=application_id,
            action="AI_AGENT_REVIEW_COMPLETED",
            actor="ai_agent_system",
            details=agent_review  # Store the COMPLETE agent review with all fields
        )
        
        # Step 6: Make Decision
        decision = self._make_decision(risk_assessment, quality_check, face_match)
        
        self.audit_service.log_action(
            application_id=application_id,
            action="DECISION_MADE",
            actor="system",
            details={
                "decision": decision.decision.value,
                "auto_approved": decision.auto_approved,
                "requires_review": decision.requires_review,
                "ai_agent_recommendation": agent_review['recommendation']
            }
        )
        
        # Step 6: Save to Database
        self._save_application(
            application_id=application_id,
            customer_id=customer_id,
            document_path=document_path,
            selfie_path=selfie_path,
            quality_check=quality_check,
            extracted_data=extracted_data,
            face_match=face_match,
            risk_assessment=risk_assessment,
            decision=decision
        )
        
        result = KYCResult(
            application_id=application_id,
            quality_check=quality_check,
            extracted_data=extracted_data,
            face_match=face_match,
            decision=decision
        )
        
        # Attach agent review to result
        result.agent_review = agent_review
        
        return result
    
    def _make_decision(
        self,
        risk_assessment,
        quality_check: ImageQualityCheck,
        face_match: FaceMatchResult
    ) -> KYCDecision:
        """
        Make final KYC decision based on all assessments
        """
        
        # Auto-approve if:
        # - Low risk
        # - High quality image
        # - Face match successful
        # - High confidence in all extractions
        
        can_auto_approve = (
            risk_assessment.risk_level == RiskLevel.LOW and
            quality_check.is_acceptable and
            face_match.is_match and
            risk_assessment.confidence > 0.7
        )
        
        # High risk = reject or manual review
        if risk_assessment.risk_level == RiskLevel.HIGH:
            decision = ApplicationStatus.UNDER_REVIEW
            requires_review = True
            auto_approved = False
        
        # Medium risk = manual review
        elif risk_assessment.risk_level == RiskLevel.MEDIUM:
            decision = ApplicationStatus.UNDER_REVIEW
            requires_review = True
            auto_approved = False
        
        # Low risk = auto-approve if all checks pass
        elif can_auto_approve:
            decision = ApplicationStatus.APPROVED
            requires_review = False
            auto_approved = True
        
        # Low risk but quality/face issues = manual review
        else:
            decision = ApplicationStatus.UNDER_REVIEW
            requires_review = True
            auto_approved = False
        
        return KYCDecision(
            decision=decision,
            risk_assessment=risk_assessment,
            requires_review=requires_review,
            auto_approved=auto_approved,
            timestamp=datetime.utcnow()
        )
    
    def _save_application(
        self,
        application_id: str,
        customer_id: str,
        document_path: str,
        selfie_path: str,
        quality_check: ImageQualityCheck,
        extracted_data: ExtractedData,
        face_match: FaceMatchResult,
        risk_assessment,
        decision: KYCDecision
    ):
        """Save application to database"""
        
        application = KYCApplication(
            id=application_id,
            customer_id=customer_id,
            status=decision.decision.value,
            document_path=document_path,
            selfie_path=selfie_path,
            extracted_data=json.loads(extracted_data.model_dump_json()),
            quality_checks=json.loads(quality_check.model_dump_json()),
            face_match_result=json.loads(face_match.model_dump_json()),
            risk_assessment=json.loads(risk_assessment.model_dump_json()),
            decision=json.loads(decision.model_dump_json())
        )
        
        self.db.add(application)
        self.db.commit()
    
    def get_application(self, application_id: str) -> KYCApplication:
        """Retrieve application from database"""
        return self.db.query(KYCApplication).filter(
            KYCApplication.id == application_id
        ).first()
    
    def _log_step(self, application_id: str, action: str, actor: str):
        """Log processing step"""
        self.audit_service.log_action(
            application_id=application_id,
            action=action,
            actor=actor,
            details={}
        )
    
    def get_user_message(self, result: KYCResult) -> str:
        """Generate user-friendly message based on result"""
        if result.decision.auto_approved:
            return "🎉 Congratulations! Your KYC verification is complete. Your account is approved."
        
        if result.decision.decision == ApplicationStatus.UNDER_REVIEW:
            reasons = []
            if not result.quality_check.is_acceptable:
                reasons.append("document image quality")
            if not result.face_match.is_match:
                reasons.append("identity verification")
            if result.decision.risk_assessment.risk_level == RiskLevel.HIGH:
                reasons.append("additional verification required")
            
            reason_text = " and ".join(reasons) if reasons else "standard procedure"
            return f"Your application is under review due to {reason_text}. We'll get back to you within 24 hours."
        
        return "Application submitted successfully."
    
    def get_next_steps(self, result: KYCResult) -> List[str]:
        """Generate next steps for user"""
        if result.decision.auto_approved:
            return [
                "Your account is now active",
                "You can start using all banking services",
                "Check your email for welcome details"
            ]
        
        steps = ["Our team is reviewing your application"]
        
        if not result.quality_check.is_acceptable:
            steps.extend(result.quality_check.suggestions)
        
        steps.extend([
            "You'll receive an email update within 24 hours",
            "Keep your phone nearby for possible verification call"
        ])
        
        return steps

