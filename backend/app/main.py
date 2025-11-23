"""
KYC-in-60s FastAPI Application
AI-powered KYC automation platform
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, BackgroundTasks, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import uuid
from datetime import datetime

from .database import get_db, engine
from .models import Base
from .models import (
    KYCSubmissionRequest, KYCSubmissionResponse, 
    ApplicationStatus, ReviewerDecision
)
from .services.kyc_orchestrator import KYCOrchestrator
from .services.audit_service import AuditService

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="KYC-in-60s",
    description="AI-powered KYC automation platform",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure upload directory exists
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "KYC-in-60s",
        "version": "1.0.0",
        "message": "AI-powered KYC automation platform is running"
    }


@app.post("/api/kyc/submit", response_model=KYCSubmissionResponse)
async def submit_kyc(
    customer_id: str = Form(...),
    document: UploadFile = File(...),
    selfie: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db)
):
    """
    Submit KYC application with document and selfie
    Returns instant decision for low-risk cases, or queues for review
    """
    try:
        # Generate application ID
        application_id = str(uuid.uuid4())
        
        # Save uploaded files
        document_path = os.path.join(UPLOAD_DIR, f"{application_id}_document.jpg")
        selfie_path = os.path.join(UPLOAD_DIR, f"{application_id}_selfie.jpg")
        
        with open(document_path, "wb") as f:
            f.write(await document.read())
        
        with open(selfie_path, "wb") as f:
            f.write(await selfie.read())
        
        # Initialize services
        orchestrator = KYCOrchestrator(db)
        audit_service = AuditService(db)
        
        # Log submission
        audit_service.log_action(
            application_id=application_id,
            action="APPLICATION_SUBMITTED",
            actor=customer_id,
            details={
                "document_filename": document.filename,
                "selfie_filename": selfie.filename,
                "submission_time": datetime.utcnow().isoformat()
            }
        )
        
        # Process KYC application
        result = orchestrator.process_application(
            application_id=application_id,
            customer_id=customer_id,
            document_path=document_path,
            selfie_path=selfie_path
        )
        
        # Prepare response with AI agent insights
        # Use AI agent message if available, otherwise use default
        user_message = result.agent_review.get('customer_message') if result.agent_review else orchestrator.get_user_message(result)
        
        response = KYCSubmissionResponse(
            application_id=application_id,
            status=result.decision.decision,
            message=user_message,
            next_steps=orchestrator.get_next_steps(result),
            decision=result.decision if result.decision.auto_approved else None,
            estimated_time="Under review" if result.decision.requires_review else None
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")


@app.get("/api/kyc/status/{application_id}")
async def get_application_status(
    application_id: str,
    db: Session = Depends(get_db)
):
    """Get current status of KYC application"""
    orchestrator = KYCOrchestrator(db)
    application = orchestrator.get_application(application_id)
    
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    # Get AI agent review from audit logs
    audit_service = AuditService(db)
    audit_logs = audit_service.get_application_audit_trail(application_id)
    
    agent_review = None
    for log in audit_logs:
        if log.action == "AI_AGENT_REVIEW_COMPLETED":
            agent_review = log.details
            break
    
    return {
        "application_id": application_id,
        "status": application.status,
        "created_at": application.created_at.isoformat(),
        "updated_at": application.updated_at.isoformat(),
        "risk_assessment": application.risk_assessment,
        "decision": application.decision,
        "reviewer_notes": application.reviewer_notes,
        "ai_agent_insights": agent_review  # NEW: Include AI agent analysis
    }


@app.get("/api/kyc/audit/{application_id}")
async def get_audit_trail(
    application_id: str,
    db: Session = Depends(get_db)
):
    """Get complete audit trail for application"""
    audit_service = AuditService(db)
    
    try:
        report = audit_service.generate_compliance_report(application_id)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating audit trail: {str(e)}")


@app.get("/api/kyc/pending")
async def get_pending_applications(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get all applications pending manual review"""
    from .models import KYCApplication
    
    applications = db.query(KYCApplication).filter(
        KYCApplication.status == ApplicationStatus.UNDER_REVIEW.value
    ).offset(skip).limit(limit).all()
    
    return {
        "total": len(applications),
        "applications": [
            {
                "id": app.id,
                "customer_id": app.customer_id,
                "status": app.status,
                "created_at": app.created_at.isoformat(),
                "risk_assessment": app.risk_assessment,
                "extracted_data": app.extracted_data
            }
            for app in applications
        ]
    }


@app.post("/api/kyc/review")
async def submit_review(
    review: ReviewerDecision,
    db: Session = Depends(get_db)
):
    """Submit manual review decision"""
    orchestrator = KYCOrchestrator(db)
    audit_service = AuditService(db)
    
    # Get application
    application = orchestrator.get_application(review.application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    # Update application
    application.status = review.decision.value
    application.reviewer_id = review.reviewer_id
    application.reviewer_notes = review.notes
    application.reviewed_at = datetime.utcnow()
    
    db.commit()
    
    # Log review decision
    audit_service.log_action(
        application_id=review.application_id,
        action="MANUAL_REVIEW_COMPLETED",
        actor=review.reviewer_id,
        details={
            "decision": review.decision.value,
            "notes": review.notes,
            "reviewed_at": datetime.utcnow().isoformat()
        }
    )
    
    return {
        "success": True,
        "application_id": review.application_id,
        "status": review.decision.value,
        "message": "Review submitted successfully"
    }


@app.get("/api/stats")
async def get_statistics(db: Session = Depends(get_db)):
    """Get overall KYC statistics"""
    from .models import KYCApplication
    from sqlalchemy import func
    
    total = db.query(func.count(KYCApplication.id)).scalar()
    approved = db.query(func.count(KYCApplication.id)).filter(
        KYCApplication.status == ApplicationStatus.APPROVED.value
    ).scalar()
    rejected = db.query(func.count(KYCApplication.id)).filter(
        KYCApplication.status == ApplicationStatus.REJECTED.value
    ).scalar()
    pending = db.query(func.count(KYCApplication.id)).filter(
        KYCApplication.status == ApplicationStatus.UNDER_REVIEW.value
    ).scalar()
    
    # Calculate auto-approval rate
    from sqlalchemy import cast, String
    auto_approved = db.query(func.count(KYCApplication.id)).filter(
        cast(KYCApplication.decision['auto_approved'], String) == 'true'
    ).scalar()
    
    auto_approval_rate = (auto_approved / total * 100) if total > 0 else 0
    
    return {
        "total_applications": total,
        "approved": approved,
        "rejected": rejected,
        "under_review": pending,
        "auto_approval_rate": round(auto_approval_rate, 2),
        "manual_review_rate": round(100 - auto_approval_rate, 2)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

