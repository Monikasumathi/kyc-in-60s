"""
Image Quality Service
Performs real-time quality checks on uploaded documents:
- Blur detection
- Glare detection
- Crop/frame detection
"""

import cv2
import numpy as np
from typing import Tuple
from ..models import ImageQualityCheck
import os

# Demo mode: Set to "true" to always pass quality checks
USE_MOCK_QUALITY = os.getenv("USE_MOCK_QUALITY", "false").lower() == "true"


class ImageQualityService:
    """Service for checking image quality and providing nudges"""
    
    # Thresholds (very lenient for hackathon demo)
    BLUR_THRESHOLD = 30.0   # Laplacian variance (very lenient)
    GLARE_THRESHOLD = 255   # Brightness threshold (maximum lenient)
    MIN_DOCUMENT_AREA_RATIO = 0.02  # Document should cover at least 2% of image (ultra lenient)
    
    def check_quality(self, image_path: str) -> ImageQualityCheck:
        """
        Perform comprehensive quality check on document image
        
        Args:
            image_path: Path to the image file
            
        Returns:
            ImageQualityCheck with scores and actionable suggestions
        """
        
        # Mock mode for demo - always return perfect quality
        if USE_MOCK_QUALITY:
            print("ℹ️  Using mock image quality (demo mode) - guaranteed pass")
            return ImageQualityCheck(
                is_acceptable=True,
                blur_score=150.0,  # Well above threshold
                glare_score=180.0,  # Well below threshold
                crop_score=0.55,    # Well above threshold
                issues=[],
                suggestions=[]
            )
        
        image = cv2.imread(image_path)
        if image is None:
            return ImageQualityCheck(
                is_acceptable=False,
                blur_score=0.0,
                glare_score=0.0,
                crop_score=0.0,
                issues=["Unable to read image file"],
                suggestions=["Please upload a valid image file (JPG, PNG)"]
            )
        
        # Check blur
        blur_score = self._check_blur(image)
        
        # Check glare
        glare_score = self._check_glare(image)
        
        # Check crop/framing
        crop_score = self._check_crop(image)
        
        # Compile issues and suggestions
        issues = []
        suggestions = []
        
        if blur_score < self.BLUR_THRESHOLD:
            issues.append("Image appears blurry")
            suggestions.append("Hold your device steady and ensure good focus")
        
        if glare_score > self.GLARE_THRESHOLD:
            issues.append("Glare or reflection detected")
            suggestions.append("Avoid direct light sources and reflections")
        
        if crop_score < self.MIN_DOCUMENT_AREA_RATIO:
            issues.append("Document not properly framed")
            suggestions.append("Move closer or zoom in to fill the frame with the document")
        
        is_acceptable = (
            blur_score >= self.BLUR_THRESHOLD and
            glare_score <= self.GLARE_THRESHOLD and
            crop_score >= self.MIN_DOCUMENT_AREA_RATIO
        )
        
        return ImageQualityCheck(
            is_acceptable=is_acceptable,
            blur_score=float(blur_score),
            glare_score=float(glare_score),
            crop_score=float(crop_score),
            issues=issues,
            suggestions=suggestions
        )
    
    def _check_blur(self, image: np.ndarray) -> float:
        """
        Detect blur using Laplacian variance
        Higher values = sharper image
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        return laplacian_var
    
    def _check_glare(self, image: np.ndarray) -> float:
        """
        Detect glare by checking for overexposed regions
        Returns max brightness value in potential glare regions
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Find very bright regions (potential glare)
        _, bright_regions = cv2.threshold(gray, 220, 255, cv2.THRESH_BINARY)
        
        # Calculate percentage of bright pixels
        bright_pixel_count = np.sum(bright_regions > 0)
        total_pixels = gray.shape[0] * gray.shape[1]
        bright_ratio = bright_pixel_count / total_pixels
        
        # If more than 10% of image is very bright, likely has glare
        if bright_ratio > 0.1:
            return 250.0  # Over threshold
        
        # Return max brightness value
        return float(np.max(gray))
    
    def _check_crop(self, image: np.ndarray) -> float:
        """
        Check if document is properly framed/cropped
        Returns ratio of document area to total image area
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Edge detection
        edges = cv2.Canny(gray, 50, 150)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return 0.0
        
        # Find largest contour (likely the document)
        largest_contour = max(contours, key=cv2.contourArea)
        document_area = cv2.contourArea(largest_contour)
        
        # Calculate ratio
        total_area = image.shape[0] * image.shape[1]
        area_ratio = document_area / total_area
        
        return area_ratio

