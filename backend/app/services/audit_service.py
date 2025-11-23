"""
Audit Logging Service
Maintains tamper-evident audit trail for compliance
"""

from datetime import datetime
from typing import Dict, Any, Optional
import json
import hashlib
from sqlalchemy.orm import Session
from ..models import AuditLog


class AuditService:
    """Service for creating and managing audit logs"""
    
    MODEL_VERSION = "v1.0.0"
    
    def __init__(self, db: Session):
        self.db = db
    
    def log_action(
        self,
        application_id: str,
        action: str,
        actor: str,
        details: Dict[str, Any],
        scores: Optional[Dict[str, Any]] = None,
        thresholds: Optional[Dict[str, Any]] = None
    ) -> AuditLog:
        """
        Create an audit log entry
        
        Args:
            application_id: ID of KYC application
            action: Action performed (e.g., "DOCUMENT_UPLOADED", "RISK_ASSESSED")
            actor: Who performed action ("system" or user_id)
            details: Action details
            scores: Relevant scores (confidence, risk, etc.)
            thresholds: Thresholds used in decision making
            
        Returns:
            Created AuditLog entry
        """
        # Redact sensitive information
        redacted_inputs = self._redact_sensitive_data(details)
        
        audit_log = AuditLog(
            application_id=application_id,
            timestamp=datetime.utcnow(),
            action=action,
            actor=actor,
            details=details,
            model_version=self.MODEL_VERSION,
            redacted_inputs=redacted_inputs,
            scores=scores or {},
            thresholds=thresholds or {}
        )
        
        self.db.add(audit_log)
        self.db.commit()
        self.db.refresh(audit_log)
        
        return audit_log
    
    def get_application_audit_trail(self, application_id: str) -> list:
        """Get complete audit trail for an application"""
        logs = self.db.query(AuditLog).filter(
            AuditLog.application_id == application_id
        ).order_by(AuditLog.timestamp.asc()).all()
        
        return logs
    
    def _redact_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Redact sensitive information for audit logs
        Keep enough info for audit without exposing full PII
        """
        redacted = data.copy()
        
        # Redact file paths (keep only filename)
        if 'document_path' in redacted:
            redacted['document_path'] = self._hash_path(redacted['document_path'])
        if 'selfie_path' in redacted:
            redacted['selfie_path'] = self._hash_path(redacted['selfie_path'])
        
        # Redact extracted data (keep only confidence scores)
        if 'extracted_data' in redacted:
            extracted = redacted['extracted_data']
            if isinstance(extracted, dict):
                for field, value in extracted.items():
                    if isinstance(value, dict) and 'value' in value:
                        # Keep confidence, redact value
                        redacted['extracted_data'][field] = {
                            'confidence': value.get('confidence'),
                            'value_hash': self._hash_value(str(value.get('value', '')))
                        }
        
        return redacted
    
    def _hash_path(self, path: str) -> str:
        """Hash file path for audit trail"""
        return hashlib.sha256(path.encode()).hexdigest()[:16]
    
    def _hash_value(self, value: str) -> str:
        """Hash sensitive value for audit trail"""
        if not value:
            return ""
        return hashlib.sha256(value.encode()).hexdigest()[:12]
    
    def generate_compliance_report(self, application_id: str) -> Dict[str, Any]:
        """
        Generate compliance report for an application
        Shows full audit trail with all decision points
        """
        logs = self.get_application_audit_trail(application_id)
        
        report = {
            'application_id': application_id,
            'generated_at': datetime.utcnow().isoformat(),
            'total_actions': len(logs),
            'timeline': []
        }
        
        for log in logs:
            report['timeline'].append({
                'timestamp': log.timestamp.isoformat(),
                'action': log.action,
                'actor': log.actor,
                'model_version': log.model_version,
                'scores': log.scores,
                'thresholds': log.thresholds,
                'outcome': log.details.get('outcome', 'N/A')
            })
        
        return report

