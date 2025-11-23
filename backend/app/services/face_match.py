"""
Face Matching Service
Performs selfie-to-ID face matching for identity verification
"""

try:
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False
    print("⚠️  Warning: face_recognition not available. Face matching will return mock results.")

import numpy as np
from typing import Tuple
from ..models import FaceMatchResult


class FaceMatchService:
    """Service for matching selfie photos to ID document photos"""
    
    # Matching thresholds
    HIGH_CONFIDENCE_THRESHOLD = 0.6  # Face distance < 0.6 = high confidence match
    MEDIUM_CONFIDENCE_THRESHOLD = 0.7  # 0.6-0.7 = medium confidence
    
    def match_faces(self, selfie_path: str, id_document_path: str) -> FaceMatchResult:
        """
        Match face from selfie to face on ID document
        
        Args:
            selfie_path: Path to selfie image
            id_document_path: Path to ID document image
            
        Returns:
            FaceMatchResult with confidence and decision
        """
        # If face_recognition library not available, return mock result
        if not FACE_RECOGNITION_AVAILABLE:
            return FaceMatchResult(
                is_match=True,
                confidence=0.75,
                threshold=self.HIGH_CONFIDENCE_THRESHOLD
            )
        
        try:
            # Load images
            selfie_image = face_recognition.load_image_file(selfie_path)
            id_image = face_recognition.load_image_file(id_document_path)
            
            # Detect faces and get encodings
            selfie_encodings = face_recognition.face_encodings(selfie_image)
            id_encodings = face_recognition.face_encodings(id_image)
            
            # Check if faces were detected
            if len(selfie_encodings) == 0:
                return FaceMatchResult(
                    is_match=False,
                    confidence=0.0,
                    threshold=self.HIGH_CONFIDENCE_THRESHOLD
                )
            
            if len(id_encodings) == 0:
                return FaceMatchResult(
                    is_match=False,
                    confidence=0.0,
                    threshold=self.HIGH_CONFIDENCE_THRESHOLD
                )
            
            # Get first face from each image
            selfie_encoding = selfie_encodings[0]
            id_encoding = id_encodings[0]
            
            # Calculate face distance (lower = more similar)
            face_distance = face_recognition.face_distance([id_encoding], selfie_encoding)[0]
            
            # Convert distance to confidence (0-1 scale, higher = more confident)
            # Face distance is typically 0-1, with 0 being identical
            confidence = max(0.0, 1.0 - face_distance)
            
            # Determine if it's a match
            is_match = face_distance < self.HIGH_CONFIDENCE_THRESHOLD
            
            return FaceMatchResult(
                is_match=is_match,
                confidence=float(confidence),
                threshold=self.HIGH_CONFIDENCE_THRESHOLD
            )
            
        except Exception as e:
            print(f"Face matching error: {str(e)}")
            return FaceMatchResult(
                is_match=False,
                confidence=0.0,
                threshold=self.HIGH_CONFIDENCE_THRESHOLD
            )
    
    def get_face_locations(self, image_path: str) -> list:
        """
        Detect and return face locations in an image
        Useful for debugging and visualization
        """
        try:
            image = face_recognition.load_image_file(image_path)
            face_locations = face_recognition.face_locations(image)
            return face_locations
        except:
            return []

