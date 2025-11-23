# System Architecture - KYC-in-60s

## 📐 Overview

KYC-in-60s is built with a modern, scalable architecture that separates concerns between the frontend presentation layer, backend API layer, and AI processing services.

---

## 🏗️ High-Level Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                        Client Layer                           │
│  ┌────────────────────────────────────────────────────────┐  │
│  │         React SPA (Single Page Application)            │  │
│  │  - Customer Portal (KYC Submission & Status)           │  │
│  │  - Admin Dashboard (Review & Analytics)                │  │
│  └────────────────────────────────────────────────────────┘  │
└────────────────────────┬─────────────────────────────────────┘
                         │ HTTPS / REST API
                         ▼
┌──────────────────────────────────────────────────────────────┐
│                       API Gateway Layer                       │
│  ┌────────────────────────────────────────────────────────┐  │
│  │              FastAPI Application                       │  │
│  │  - Authentication & Authorization                      │  │
│  │  - Request Validation (Pydantic)                       │  │
│  │  - Rate Limiting & CORS                                │  │
│  │  - Error Handling & Logging                            │  │
│  └────────────────────────────────────────────────────────┘  │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│                   Orchestration Layer                         │
│  ┌────────────────────────────────────────────────────────┐  │
│  │              KYC Orchestrator Service                  │  │
│  │  - Workflow Coordination                               │  │
│  │  - Service Integration                                 │  │
│  │  - Business Logic                                      │  │
│  │  - Decision Making                                     │  │
│  └────────────────────────────────────────────────────────┘  │
└───┬─────────┬──────────┬─────────────┬──────────────┬────────┘
    │         │          │             │              │
    ▼         ▼          ▼             ▼              ▼
┌────────┐ ┌──────┐ ┌─────────┐ ┌──────────┐ ┌──────────────┐
│  OCR   │ │ Face │ │  Image  │ │   Risk   │ │    Audit     │
│Service │ │Match │ │ Quality │ │  Engine  │ │   Service    │
└────────┘ └──────┘ └─────────┘ └──────────┘ └──────────────┘
                                       │              │
                                       ▼              ▼
                            ┌──────────────────────────────┐
                            │    Persistence Layer         │
                            │  - Applications DB           │
                            │  - Audit Logs DB             │
                            │  - File Storage              │
                            └──────────────────────────────┘
```

---

## 🔧 Component Details

### 1. Frontend Layer

**Technology**: React 18 + TypeScript + Vite

**Responsibilities**:
- User interface rendering
- Form validation
- Real-time feedback
- API communication
- State management

**Key Components**:
```
src/
├── pages/
│   ├── HomePage.tsx              # Landing page
│   ├── KYCSubmissionPage.tsx     # Customer submission flow
│   ├── StatusPage.tsx            # Application status tracker
│   ├── AdminDashboard.tsx        # Admin overview
│   └── ReviewPage.tsx            # Manual review interface
├── components/                   # Reusable UI components
├── services/
│   └── api.ts                    # API client
└── App.tsx                       # Root component & routing
```

**Data Flow**:
1. User interacts with React components
2. Components call API service methods
3. API service makes HTTP requests to backend
4. Responses update component state
5. UI re-renders with new data

---

### 2. API Gateway Layer

**Technology**: FastAPI + Uvicorn

**Responsibilities**:
- HTTP request handling
- Input validation
- Authentication/authorization
- CORS management
- Error handling
- API documentation

**Key Endpoints**:
```
POST   /api/kyc/submit           # Submit KYC application
GET    /api/kyc/status/{id}      # Get application status
GET    /api/kyc/audit/{id}       # Get audit trail
GET    /api/kyc/pending          # List pending applications
POST   /api/kyc/review           # Submit review decision
GET    /api/stats                # Get statistics
```

**Request Flow**:
```
1. Request arrives → CORS check
2. Input validation → Pydantic models
3. Authentication → JWT/API key
4. Business logic → Orchestrator
5. Response formatting → JSON
6. Error handling → Structured errors
```

---

### 3. Orchestration Layer

**Technology**: Python + Async/Await

**Component**: `KYCOrchestrator`

**Responsibilities**:
- Coordinate AI services
- Implement business logic
- Make final decisions
- Manage workflow state
- Handle errors gracefully

**Processing Pipeline**:
```python
1. Receive application
   ↓
2. Image Quality Check
   ├─ Pass → Continue
   └─ Fail → Flag for review
   ↓
3. OCR Extraction
   ├─ High confidence → Continue
   └─ Low confidence → Flag fields
   ↓
4. Face Matching
   ├─ Match → Continue
   └─ No match → Flag for review
   ↓
5. Risk Assessment
   ├─ Low risk → Auto-approve
   ├─ Medium risk → Manual review
   └─ High risk → Manual review
   ↓
6. Save to database
   ↓
7. Log to audit trail
   ↓
8. Return decision
```

**Decision Logic**:
```python
Auto-Approve IF:
  - risk_level == LOW
  AND image_quality.is_acceptable == True
  AND face_match.is_match == True
  AND risk_assessment.confidence > 0.7

Else:
  - Queue for manual review
```

---

### 4. AI Service Layer

#### A. OCR Service

**Technology**: Tesseract OCR + OpenCV

**Process**:
```
1. Read image file
2. Preprocess image
   - Convert to grayscale
   - Adaptive thresholding
   - Denoise
3. Extract text with Tesseract
4. Parse structured fields
   - Name (first 10 lines, 2-4 words)
   - DOB (date patterns with context)
   - ID number (alphanumeric patterns)
   - Address (keyword-based)
   - Document type (keyword matching)
5. Calculate confidence per field
6. Return ExtractedData
```

**Confidence Calculation**:
- Name: 0.85 if in first 5 lines, else 0.75
- DOB: 0.9 if valid date format, else 0.6
- ID Number: 0.85 if matches pattern
- Address: 0.75 if keywords found
- Document Type: 0.9 if keywords match

#### B. Face Matching Service

**Technology**: face-recognition (dlib)

**Process**:
```
1. Load selfie image
2. Load document image
3. Detect faces in both
   - If no face → confidence = 0.0
4. Extract face encodings (128-d vectors)
5. Calculate Euclidean distance
6. Convert to confidence score
   confidence = 1.0 - distance
7. Compare to threshold (0.6)
8. Return FaceMatchResult
```

**Thresholds**:
- High confidence: distance < 0.6
- Medium confidence: 0.6-0.7
- Low confidence: > 0.7

#### C. Image Quality Service

**Technology**: OpenCV

**Checks**:

1. **Blur Detection**
   - Method: Laplacian variance
   - Threshold: 100.0
   - Higher = sharper

2. **Glare Detection**
   - Method: Brightness analysis
   - Threshold: 240 (max brightness)
   - Check: % of very bright pixels

3. **Crop/Framing Check**
   - Method: Edge detection + contour finding
   - Calculate: document area / total area
   - Threshold: 30% (MIN_DOCUMENT_AREA_RATIO)

#### D. Risk Engine

**Technology**: Hybrid Rule-Based + ML

**Scoring Model**:
```
Risk Score = (
  data_quality * 0.4 +
  image_quality * 0.2 +
  identity_verification * 0.3 +
  data_consistency * 0.1
)

Risk Level:
  < 0.3 → LOW
  0.3-0.6 → MEDIUM
  > 0.6 → HIGH
```

**Risk Factors**:

1. **Data Quality (40%)**
   - Missing fields: +0.3 each
   - Low confidence: +0.15 each
   - Uncertain doc type: +0.1

2. **Image Quality (20%)**
   - Blur: +0.5
   - Glare: +0.5
   - Poor framing: +0.5

3. **Identity Verification (30%)**
   - Face match fail: +1.0
   - Low confidence: +0.4

4. **Data Consistency (10%)**
   - Age out of range: +0.5
   - Document expired: +0.5
   - Suspicious ID pattern: +0.3

**Reason Codes**:
- `MISSING_FIELD_*`: Required field not extracted
- `LOW_CONFIDENCE_*`: Field confidence below threshold
- `IMAGE_BLURRY`: Image quality issues
- `FACE_MATCH_FAILED`: Face verification failed
- `DOCUMENT_EXPIRED`: ID past expiry date
- `AGE_OUT_OF_RANGE`: DOB indicates age < 18 or > 100

---

### 5. Audit Service

**Technology**: Python + SQLAlchemy

**Responsibilities**:
- Log every action
- Maintain tamper-evident trail
- Redact PII for compliance
- Generate compliance reports

**Log Structure**:
```python
{
  "id": auto_increment,
  "application_id": "uuid",
  "timestamp": "ISO 8601",
  "action": "ACTION_NAME",
  "actor": "system | user_id",
  "details": { ... },
  "model_version": "v1.0.0",
  "scores": { ... },
  "thresholds": { ... },
  "redacted_inputs": { ... }
}
```

**Actions Logged**:
- `APPLICATION_SUBMITTED`
- `IMAGE_QUALITY_CHECK_COMPLETED`
- `OCR_EXTRACTION_COMPLETED`
- `FACE_MATCHING_COMPLETED`
- `RISK_ASSESSMENT_COMPLETED`
- `DECISION_MADE`
- `MANUAL_REVIEW_COMPLETED`

---

### 6. Persistence Layer

**Technology**: SQLAlchemy + SQLite (PostgreSQL-ready)

**Schema**:

#### KYCApplication Table
```sql
CREATE TABLE kyc_applications (
  id VARCHAR PRIMARY KEY,
  customer_id VARCHAR NOT NULL,
  status VARCHAR NOT NULL,
  created_at TIMESTAMP,
  updated_at TIMESTAMP,
  document_path VARCHAR,
  selfie_path VARCHAR,
  extracted_data JSON,
  quality_checks JSON,
  face_match_result JSON,
  risk_assessment JSON,
  decision JSON,
  reviewer_id VARCHAR,
  reviewer_notes TEXT,
  reviewed_at TIMESTAMP
);
```

#### AuditLog Table
```sql
CREATE TABLE audit_logs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  application_id VARCHAR NOT NULL,
  timestamp TIMESTAMP,
  action VARCHAR NOT NULL,
  actor VARCHAR NOT NULL,
  details JSON,
  model_version VARCHAR,
  redacted_inputs JSON,
  scores JSON,
  thresholds JSON
);
```

---

## 🔄 Data Flow Diagrams

### Customer Submission Flow

```
User                Frontend            Backend                 AI Services
 │                     │                   │                         │
 │  Upload Files       │                   │                         │
 │────────────────────>│                   │                         │
 │                     │  POST /submit     │                         │
 │                     │──────────────────>│                         │
 │                     │                   │  Quality Check          │
 │                     │                   │────────────────────────>│
 │                     │                   │<────────────────────────│
 │                     │                   │  OCR Extract            │
 │                     │                   │────────────────────────>│
 │                     │                   │<────────────────────────│
 │                     │                   │  Face Match             │
 │                     │                   │────────────────────────>│
 │                     │                   │<────────────────────────│
 │                     │                   │  Risk Assessment        │
 │                     │                   │────────────────────────>│
 │                     │                   │<────────────────────────│
 │                     │  Decision         │                         │
 │  Display Result     │<──────────────────│                         │
 │<────────────────────│                   │                         │
```

### Manual Review Flow

```
Reviewer            Frontend            Backend              Database
 │                     │                   │                     │
 │  View Queue         │                   │                     │
 │────────────────────>│  GET /pending     │                     │
 │                     │──────────────────>│  Query DB           │
 │                     │                   │────────────────────>│
 │                     │                   │<────────────────────│
 │  Display List       │  Applications     │                     │
 │<────────────────────│<──────────────────│                     │
 │                     │                   │                     │
 │  Click Review       │                   │                     │
 │────────────────────>│  GET /status/id   │                     │
 │                     │──────────────────>│  Fetch Details      │
 │                     │                   │────────────────────>│
 │                     │                   │<────────────────────│
 │  Show Details       │  Full Data        │                     │
 │<────────────────────│<──────────────────│                     │
 │                     │                   │                     │
 │  Submit Decision    │                   │                     │
 │────────────────────>│  POST /review     │                     │
 │                     │──────────────────>│  Update Status      │
 │                     │                   │────────────────────>│
 │                     │                   │  Log Audit          │
 │                     │                   │────────────────────>│
 │  Confirmation       │  Success          │                     │
 │<────────────────────│<──────────────────│                     │
```

---

## 🔐 Security Architecture

### Authentication (Future Enhancement)
```
- JWT tokens for API access
- Role-based access control (RBAC)
- API key for service-to-service
```

### Data Security
```
- TLS/HTTPS for all communication
- Encrypted storage for sensitive data
- PII redaction in logs
- Secure file storage with access controls
```

### Input Validation
```
- Pydantic models validate all inputs
- File type and size restrictions
- SQL injection prevention (SQLAlchemy ORM)
- XSS prevention (React escaping)
```

---

## 📈 Scalability Considerations

### Horizontal Scaling
```
- Stateless API servers (scale with load balancer)
- Shared database (PostgreSQL with read replicas)
- Distributed file storage (S3, MinIO)
- Redis for session management
```

### Performance Optimization
```
- Async/await for non-blocking I/O
- Database connection pooling
- Image processing in worker processes
- CDN for frontend assets
- API response caching
```

### Monitoring
```
- Application logs → ELK stack
- Metrics → Prometheus + Grafana
- Error tracking → Sentry
- APM → New Relic / DataDog
```

---

## 🔧 Configuration Management

### Environment Variables
```bash
# Database
DATABASE_URL=postgresql://user:pass@host/db

# API
API_HOST=0.0.0.0
API_PORT=8000

# AI Thresholds
BLUR_THRESHOLD=100.0
FACE_MATCH_THRESHOLD=0.6
LOW_RISK_THRESHOLD=0.3
```

### Feature Flags
```python
ENABLE_AUTO_APPROVAL = True
ENABLE_FACE_MATCHING = True
REQUIRE_ADDRESS_PROOF = False
```

---

## 🧪 Testing Strategy

### Unit Tests
- Individual service methods
- Data validation logic
- Risk scoring calculations

### Integration Tests
- API endpoint responses
- Database operations
- Service interactions

### E2E Tests
- Complete user flows
- Admin workflows
- Error scenarios

---

## 📚 Design Patterns Used

1. **Service Layer Pattern**: Separation of business logic
2. **Repository Pattern**: Database abstraction
3. **Factory Pattern**: Creating AI service instances
4. **Strategy Pattern**: Configurable risk thresholds
5. **Observer Pattern**: Audit logging
6. **Chain of Responsibility**: Processing pipeline

---

## 🚀 Deployment Architecture (Production)

```
                          ┌─────────────┐
                          │  CloudFlare │
                          │     CDN     │
                          └──────┬──────┘
                                 │
                   ┌─────────────┴─────────────┐
                   ▼                           ▼
            ┌─────────────┐            ┌─────────────┐
            │   Frontend  │            │     API     │
            │  (Vercel/   │            │  (AWS ECS/  │
            │   Netlify)  │            │   K8s Pod)  │
            └─────────────┘            └──────┬──────┘
                                              │
                           ┌──────────────────┼──────────────────┐
                           ▼                  ▼                  ▼
                    ┌───────────┐      ┌──────────┐      ┌──────────┐
                    │ PostgreSQL│      │   Redis  │      │    S3    │
                    │    RDS    │      │  Cache   │      │  Files   │
                    └───────────┘      └──────────┘      └──────────┘
```

---

This architecture provides a solid foundation for a production-ready KYC platform that can scale to millions of users while maintaining security, compliance, and performance.

