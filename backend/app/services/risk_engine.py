"""
Risk Assessment Engine
Transparent, explainable risk scoring with rule-based and ML components
"""

from typing import Dict, Any, List
import numpy as np
from ..models import (
    RiskLevel, RiskAssessment, ExtractedData, 
    ImageQualityCheck, FaceMatchResult
)


class RiskEngine:
    """
    Hybrid risk engine combining explicit rules with lightweight ML
    All decisions are explainable with reason codes
    """
    
    # Risk score thresholds
    LOW_RISK_THRESHOLD = 0.3
    MEDIUM_RISK_THRESHOLD = 0.6
    
    # Confidence thresholds for extracted data
    MIN_FIELD_CONFIDENCE = 0.7
    
    def assess_risk(
        self,
        extracted_data: ExtractedData,
        quality_check: ImageQualityCheck,
        face_match: FaceMatchResult
    ) -> RiskAssessment:
        """
        Assess risk level for KYC application
        
        Args:
            extracted_data: Extracted fields from document
            quality_check: Image quality assessment
            face_match: Face matching result
            
        Returns:
            RiskAssessment with explainable risk level and reasons
        """
        risk_factors = {}
        reason_codes = []
        
        # 1. Data Quality Factors (40% weight)
        data_quality_score = self._assess_data_quality(extracted_data, reason_codes)
        risk_factors['data_quality'] = data_quality_score
        
        # 2. Image Quality Factors (20% weight)
        image_quality_score = self._assess_image_quality(quality_check, reason_codes)
        risk_factors['image_quality'] = image_quality_score
        
        # 3. Identity Verification Factors (30% weight)
        identity_score = self._assess_identity_verification(face_match, reason_codes)
        risk_factors['identity_verification'] = identity_score
        
        # 4. Data Consistency Factors (10% weight)
        consistency_score = self._assess_data_consistency(extracted_data, reason_codes)
        risk_factors['data_consistency'] = consistency_score
        
        # Calculate weighted risk score
        total_risk_score = (
            data_quality_score * 0.4 +
            image_quality_score * 0.2 +
            identity_score * 0.3 +
            consistency_score * 0.1
        )
        
        # Determine risk level
        if total_risk_score < self.LOW_RISK_THRESHOLD:
            risk_level = RiskLevel.LOW
        elif total_risk_score < self.MEDIUM_RISK_THRESHOLD:
            risk_level = RiskLevel.MEDIUM
        else:
            risk_level = RiskLevel.HIGH
        
        # Calculate confidence in risk assessment
        confidence = self._calculate_assessment_confidence(risk_factors)
        
        return RiskAssessment(
            risk_level=risk_level,
            confidence=confidence,
            reason_codes=reason_codes,
            factors=risk_factors,
            score=total_risk_score
        )
    
    def _assess_data_quality(self, data: ExtractedData, reason_codes: List[str]) -> float:
        """Assess quality of extracted data"""
        risk_score = 0.0
        
        # Check each required field
        required_fields = [data.full_name, data.date_of_birth, data.id_number, data.address]
        
        for field in required_fields:
            if not field.value:
                risk_score += 0.3
                reason_codes.append(f"MISSING_FIELD_{field.field_name.upper()}")
            elif field.confidence < self.MIN_FIELD_CONFIDENCE:
                risk_score += 0.15
                reason_codes.append(f"LOW_CONFIDENCE_{field.field_name.upper()}")
        
        # Check document type
        if data.document_type.confidence < 0.7:
            risk_score += 0.1
            reason_codes.append("UNCERTAIN_DOCUMENT_TYPE")
        
        return min(risk_score, 1.0)
    
    def _assess_image_quality(self, quality: ImageQualityCheck, reason_codes: List[str]) -> float:
        """Assess image quality risk"""
        if not quality.is_acceptable:
            risk_score = 0.5
            for issue in quality.issues:
                if "blurry" in issue.lower():
                    reason_codes.append("IMAGE_BLURRY")
                elif "glare" in issue.lower():
                    reason_codes.append("IMAGE_GLARE")
                elif "framed" in issue.lower():
                    reason_codes.append("IMAGE_POORLY_FRAMED")
            return risk_score
        
        return 0.0
    
    def _assess_identity_verification(self, face_match: FaceMatchResult, reason_codes: List[str]) -> float:
        """Assess identity verification risk"""
        if not face_match.is_match:
            reason_codes.append("FACE_MATCH_FAILED")
            return 1.0
        
        # Low confidence match
        if face_match.confidence < 0.7:
            reason_codes.append("LOW_FACE_MATCH_CONFIDENCE")
            return 0.4
        
        return 0.0
    
    def _assess_data_consistency(self, data: ExtractedData, reason_codes: List[str]) -> float:
        """Check for data consistency issues"""
        risk_score = 0.0
        
        # Check if DOB indicates unrealistic age
        if data.date_of_birth.value:
            age = self._calculate_age(data.date_of_birth.value)
            if age < 18 or age > 100:
                risk_score += 0.5
                reason_codes.append("AGE_OUT_OF_RANGE")
        
        # Check if expiry date is in the past
        if data.expiry_date and data.expiry_date.value:
            if self._is_expired(data.expiry_date.value):
                risk_score += 0.5
                reason_codes.append("DOCUMENT_EXPIRED")
        
        # Check for suspicious patterns (all same digits, etc.)
        if data.id_number.value:
            if self._is_suspicious_pattern(data.id_number.value):
                risk_score += 0.3
                reason_codes.append("SUSPICIOUS_ID_PATTERN")
        
        return min(risk_score, 1.0)
    
    def _calculate_assessment_confidence(self, factors: Dict[str, float]) -> float:
        """Calculate confidence in the risk assessment itself"""
        # Higher variance in factors = lower confidence
        scores = list(factors.values())
        variance = np.var(scores)
        
        # Lower variance = higher confidence
        confidence = max(0.5, 1.0 - variance)
        return confidence
    
    def _calculate_age(self, dob_str: str) -> int:
        """Calculate age from date of birth string"""
        from datetime import datetime
        
        formats = ['%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d']
        for fmt in formats:
            try:
                dob = datetime.strptime(dob_str, fmt)
                age = (datetime.now() - dob).days // 365
                return age
            except:
                continue
        return 0
    
    def _is_expired(self, expiry_str: str) -> bool:
        """Check if document is expired"""
        from datetime import datetime
        
        formats = ['%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d']
        for fmt in formats:
            try:
                expiry = datetime.strptime(expiry_str, fmt)
                return expiry < datetime.now()
            except:
                continue
        return False
    
    def _is_suspicious_pattern(self, id_number: str) -> bool:
        """Detect suspicious patterns in ID number"""
        # All same digit
        if len(set(id_number.replace('-', '').replace(' ', ''))) == 1:
            return True
        
        # Sequential numbers
        digits = ''.join(c for c in id_number if c.isdigit())
        if len(digits) >= 5:
            for i in range(len(digits) - 4):
                if digits[i:i+5] in '0123456789' or digits[i:i+5] in '9876543210':
                    return True
        
        return False

