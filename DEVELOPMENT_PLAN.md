# 🚀 StockSense Agent - Complete Development Plan
## Production-Grade Implementation with Security & Hackathon Optimizations

**Version:** 2.0 (Modified with Security Enhancements)
**Last Updated:** February 17, 2026
**Target:** Fetch.ai Hackathon Submission

---

## 📚 Table of Contents

1. [Master Context](#master-context)
2. [Phase 1: Enhanced Database Schema](#phase-1)
3. [Phase 2: Secure Authentication](#phase-2)
4. [Phase 3: Core Inventory API](#phase-3)
5. [Phase 4: Analytics Engine](#phase-4)
6. [Phase 5: Fetch.ai Agent (MVP)](#phase-5)
7. [Phase 6: Internal API for Agent](#phase-6)
8. [Phase 7: Deployment & Monitoring](#phase-7)
9. [Security Checklist](#security)
10. [Hackathon Demo Strategy](#demo)

---

## 🎯 Master Context Prompt <a name="master-context"></a>

**Use this prompt to set context for any LLM/Copilot before starting development:**

```
PROMPT: You are an expert backend software engineer and solutions architect. We are building "StockSense Agent," a B2B SaaS product for pharmacies.

The Goal: An autonomous backend system that monitors pharmacy inventory databases, predicts medicine expiry, calculates sales velocity to recommend restocking quantities, and uses Fetch.ai uAgents to autonomously create purchase recommendations (supplier negotiation is Phase 2 roadmap).

The Stack: Python 3.10+, FastAPI for REST API, PostgreSQL for database, SQLAlchemy AsyncIO for ORM, Fetch.ai uAgents for autonomous monitoring, Docker for deployment.

Security Priority: Multi-tenant isolation, JWT authentication, agent access via internal API (not direct DB access), audit logging for all autonomous actions.

Hackathon Focus: Build a working demo showing autonomous monitoring + smart recommendations. Supplier negotiation shown as roadmap feature.

I need you to act as my Lead Developer. I will give you instructions in phases. Focus on robust, secure, scalable backend infrastructure. Wait for my Phase 1 instructions.
```

---

## 📦 Phase 1: Enhanced Database Schema & Project Structure <a name="phase-1"></a>

### Objective
Define secure, multi-tenant database architecture with audit capabilities.

### Prompt for LLM

```
PROMPT: Phase 1: Database Design and Project Structure with Security Enhancements

Let's define the core setup with multi-tenancy isolation and audit capabilities.

Project Structure: Create a scalable directory structure:
```
stocksense-agent/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app entry
│   ├── core/
│   │   ├── config.py           # Settings (from .env)
│   │   ├── database.py         # AsyncIO DB session
│   │   ├── dependencies.py     # Common dependencies
│   │   └── validators.py       # Input validation
│   ├── models/
│   │   ├── __init__.py
│   │   ├── pharmacy.py         # Pharmacy/Tenant model
│   │   ├── user.py            # User & Subscription
│   │   ├── inventory.py       # InventoryItem, SalesTransaction
│   │   └── agent.py           # Agent audit/recommendations
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py            # Authentication endpoints
│   │   ├── inventory.py       # CRUD operations
│   │   ├── sales.py           # Transaction recording
│   │   ├── analytics.py       # Analytics endpoints
│   │   └── internal.py        # Agent-only endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   ├── analytics.py       # Business logic
│   │   ├── inventory_service.py
│   │   └── agent_service.py
│   └── auth/
│       ├── __init__.py
│       ├── security.py        # JWT & password hashing
│       ├── dependencies.py    # Auth dependencies
│       └── feature_gate.py    # Subscription enforcement
├── agent/
│   ├── __init__.py
│   ├── agent.py               # Fetch.ai uAgent worker
│   ├── protocols.py           # Agent communication
│   └── config.py
├── tests/
│   ├── test_auth.py
│   ├── test_inventory.py
│   └── test_agent.py
├── alembic/                   # DB migrations
├── docker/
│   ├── Dockerfile.api
│   └── Dockerfile.agent
├── .env.example
├── requirements.txt
├── docker-compose.yml
└── README.md
```

Database Schema (PostgreSQL + SQLAlchemy AsyncIO):

**CRITICAL SECURITY NOTE:** All tables must include pharmacy_id for tenant isolation.

### Core Tables:

#### 1. Pharmacy (Tenant Table)
- id: UUID (Primary Key)
- name: String(255) (indexed)
- email: String(255) (unique)
- phone: String(20)
- address: Text
- created_at: DateTime
- is_active: Boolean (default=True)

#### 2. Subscription
- id: UUID (Primary Key)
- pharmacy_id: UUID (Foreign Key → Pharmacy.id)
- tier: Enum('silver', 'gold', 'platinum')
- started_at: DateTime
- expires_at: DateTime
- auto_renew: Boolean (default=True)
- monthly_price: Decimal(10, 2)

#### 3. User
- id: UUID (Primary Key)
- pharmacy_id: UUID (Foreign Key → Pharmacy.id) ← TENANT ISOLATION
- email: String(255) (unique)
- hashed_password: String(255)
- full_name: String(255)
- role: Enum('owner', 'manager', 'viewer')
- is_active: Boolean (default=True)
- created_at: DateTime

#### 4. InventoryItem
- id: UUID (Primary Key)
- pharmacy_id: UUID (Foreign Key → Pharmacy.id) ← TENANT ISOLATION
- medicine_name: String(255) (indexed)
- batch_number: String(100)
- sku: String(100) (unique per pharmacy)
- quantity: Integer
- expiry_date: Date (indexed) ← CRITICAL FIELD
- cost_price: Decimal(10, 2)
- selling_price: Decimal(10, 2)
- category: String(100) (nullable) ← For seasonal analysis
- is_recalled: Boolean (default=False) ← Safety feature
- created_at: DateTime
- updated_at: DateTime

#### 5. SalesTransaction
- id: UUID (Primary Key)
- pharmacy_id: UUID (Foreign Key → Pharmacy.id) ← TENANT ISOLATION
- item_id: UUID (Foreign Key → InventoryItem.id)
- quantity_sold: Integer
- sale_price: Decimal(10, 2)
- transaction_date: Date (indexed)
- created_at: DateTime

#### 6. RestockRecommendation (NEW - Agent Audit Trail)
- id: UUID (Primary Key)
- pharmacy_id: UUID (Foreign Key → Pharmacy.id)
- item_id: UUID (Foreign Key → InventoryItem.id)
- recommended_quantity: Integer
- current_stock: Integer
- days_until_expiry: Integer (nullable)
- sales_velocity: Decimal(10, 3) ← Units per day
- reason: Enum('expiry_risk', 'low_stock', 'high_velocity')
- status: Enum('pending', 'approved', 'rejected', 'ordered')
- created_by_agent: Boolean (default=True)
- agent_run_id: String(100) ← Links to agent execution
- created_at: DateTime
- reviewed_at: DateTime (nullable)
- reviewed_by_user_id: UUID (nullable, FK → User.id)

#### 7. AgentAuditLog (NEW - Compliance)
- id: UUID (Primary Key)
- agent_address: String(255) ← Fetch.ai wallet address
- pharmacy_id: UUID (nullable, FK → Pharmacy.id)
- action_type: Enum('health_check', 'inventory_scan', 'recommendation_created', 'error')
- payload: JSON
- error_message: Text (nullable)
- timestamp: DateTime (indexed)

#### 8. AgentHealthStatus (NEW - Monitoring)
- id: UUID (Primary Key)
- agent_address: String(255) (unique)
- last_successful_run: DateTime
- last_error: Text (nullable)
- status: Enum('healthy', 'degraded', 'failed')
- wallet_balance: Decimal(18, 8) ← FET token balance
- updated_at: DateTime

### Environment Configuration (.env.example):
```
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/stocksense
SECRET_KEY=your-secret-key-minimum-32-characters-long
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
INTERNAL_AGENT_API_KEY=secure-random-key-for-agent-api-auth
AGENT_WALLET_PRIVATE_KEY=your-fetch-wallet-private-key
AGENT_RUN_INTERVAL=86400
REDIS_URL=redis://localhost:6379
CORS_ORIGINS=["http://localhost:3000"]
```

### Expected Output:
1. Complete SQLAlchemy models with AsyncIO support
2. Alembic migration files
3. Database initialization script
4. Model relationship diagrams
```

---

## 🔐 Phase 2: Secure Authentication & API Foundation <a name="phase-2"></a>

### Objective
Implement JWT-based auth with multi-tenant isolation and role-based access control.

### Prompt for LLM

```
PROMPT: Phase 2: JWT Authentication System with Multi-tenant Isolation

Based on Phase 1 models, implement secure authentication with strict tenant boundaries.

### Authentication Utilities (app/auth/security.py):

1. Password Hashing:
   - Use passlib with bcrypt backend
   - Min cost factor: 12
   - Functions: hash_password(password: str) → str
   - verify_password(plain: str, hashed: str) → bool

2. JWT Token Management:
   - Library: python-jose[cryptography]
   - create_access_token(data: dict, expires_delta: Optional[timedelta]) → str
   - verify_token(token: str) → dict
   
3. Token Payload Structure:
```python
{
  "sub": "user_uuid",
  "pharmacy_id": "pharmacy_uuid",  # CRITICAL for tenant isolation
  "role": "owner",
  "exp": 1234567890
}
```

### Security Dependencies (app/auth/dependencies.py):

1. get_current_user(token: str = Depends(oauth2_scheme)) → User:
   - Decode JWT token
   - Extract user_id from 'sub' claim
   - Query database for user
   - Verify user.is_active = True
   - Verify user.pharmacy.is_active = True
   - Return User object with relationships loaded

2. get_current_active_pharmacy(current_user: User = Depends(get_current_user)) → Pharmacy:
   - Return current_user.pharmacy
   - Used for explicit tenant context

3. require_role(allowed_roles: List[str]):
   - Dependency factory for role-based access
   - Usage: @app.get(..., dependencies=[Depends(require_role(["owner"]))])

4. verify_internal_agent_key(x_agent_key: str = Header(...)) → bool:
   - Validate x-agent-key header matches INTERNAL_AGENT_API_KEY
   - Used for /internal/* endpoints
   - Raise HTTP 403 if invalid

### Feature Gate System (app/auth/feature_gate.py):

```python
class FeatureGate:
    TIER_FEATURES = {
        "silver": ["expiry_alerts"],
        "gold": ["expiry_alerts", "smart_restocking", "sales_analytics"],
        "platinum": ["expiry_alerts", "smart_restocking", "sales_analytics", 
                     "agent_monitoring", "advanced_reports"]
    }
    
    @staticmethod
    async def check_feature_access(pharmacy_id: UUID, feature: str):
        # Query Subscription table
        # Check if feature in TIER_FEATURES[subscription.tier]
        # Raise HTTPException(403) if not allowed
        # Return subscription if allowed
```

### Authentication Routes (app/routes/auth.py):

1. POST /auth/register:
   - Create new Pharmacy + Owner User + Default Subscription (silver tier, 30-day trial)
   - Hash password before storing
   - Return JWT access_token
   - Validate email uniqueness

2. POST /auth/login:
   - Accept email + password
   - Verify credentials
   - Return JWT with pharmacy_id embedded

3. GET /auth/me:
   - Protected endpoint
   - Return current user + pharmacy + subscription details

### Security Requirements:
- Rate limiting: 10 login attempts per hour per IP
- CORS: Restrict to production domains
- Token expiry: 30 minutes
```

---

## 📊 Phase 3-7: Remaining Implementation (Summary)

Due to file length, here are the key prompts for remaining phases:

### Phase 3: Core Inventory API
- CSV upload with validation (10MB limit, schema validation)
- CRUD operations with strict tenant isolation
- Input sanitization for all string fields

### Phase 4: Analytics Engine
- Sales velocity calculation with edge case handling
- Expiry risk identification
- Seasonal adjustment factors
- Insufficient data fallback strategies

### Phase 5: Fetch.ai Agent (MVP)
- Standalone agent worker process
- Periodic inventory scanning (@agent.on_interval)
- Internal API communication (NOT direct DB access)
- Agent audit logging for all actions

### Phase 6: Internal API for Agent
- Protected /internal/* endpoints
- Agent-only authentication via API key header
- Pharmacy data isolation enforced

### Phase 7: Deployment & Monitoring
- Docker Compose setup (API + Agent + PostgreSQL)
- Health check endpoints
- Agent status monitoring
- Production deployment guide

---

## ✅ Security Checklist <a name="security"></a>

### 🔒 Must-Have Security Features:

- [ ] **Multi-Tenancy Isolation**
  - All queries filtered by pharmacy_id
  - JWT tokens embed pharmacy_id
  - No cross-tenant data access possible

- [ ] **Agent Access Control**
  - Agent uses internal API (not direct DB)
  - Internal endpoints require API key header
  - Agent cannot access other pharmacies' data

- [ ] **Input Validation**
  - CSV upload: file size, MIME type, schema validation
  - Expiry date: must be future date, <10 years
  - Price fields: must be positive numbers
  - String sanitization: strip, max length

- [ ] **Authentication Security**
  - Bcrypt password hashing (cost factor 12)
  - JWT with 30-minute expiry
  - Rate limiting on login endpoint
  - Secure password requirements

- [ ] **Audit Trail**
  - All agent actions logged to AgentAuditLog
  - User actions tracked (who updated what)
  - Recommendation review history

- [ ] **Error Handling**
  - No sensitive data in error messages
  - Generic error responses to users
  - Detailed logging for debugging

---

## 🎯 Hackathon Demo Strategy <a name="demo"></a>

### What to Build (Priority Order):

**MUST HAVE (Demo Core):**
1. ✅ Phase 1: Database models
2. ✅ Phase 2: Authentication API
3. ✅ Phase 3: Inventory CSV upload + CRUD
4. ✅ Phase 4: Analytics service (velocity calculation)
5. ✅ Phase 5: Basic Fetch.ai agent (monitoring only)
6. ✅ Phase 6: Internal API for agent

**NICE TO HAVE (If Time Permits):**
7. Phase 7: Docker deployment
8. Simple dashboard UI (even basic HTML)
9. Real-time notifications

**SKIP FOR MVP (Roadmap Features):**
- Supplier negotiation protocol
- Advanced ML forecasting
- Mobile app
- Barcode scanner integration

### Demo Flow:

1. **Setup** (2 minutes)
   - Show deployed system (Docker running)
   - Show GitHub Pages UI

2. **Onboarding** (3 minutes)
   - Register new pharmacy via API
   - Upload sample inventory CSV (50 items, some expiring soon)
   - Show data in database

3. **Agent in Action** (5 minutes)
   - Trigger agent run manually
   - Show agent scanning inventory
   - Agent creates recommendations in RestockRecommendation table
   - Show audit log entries

4. **Business Value** (3 minutes)
   - Show recommendations dashboard
   - Highlight expiry risks detected
   - Show calculated restock quantities
   - Explain cost savings (₹20-30K/month waste prevention)

5. **Technical Deep Dive** (2 minutes)
   - Show agent code (uAgents library usage)
   - Explain multi-tenancy isolation
   - Show subscription tier enforcement

### Judging Criteria Alignment:

| Criteria | How We Address It |
|----------|------------------|
| **Idea Quality** | Solves real ₹20-30K/month problem for pharmacies |
| **ASI: One Integration** | Fetch.ai uAgent autonomously monitors inventory |
| **Business Thinking** | Clear tier pricing, ROI calculation shown |
| **Feasibility** | MVP scope realistic, supplier integration in roadmap |
| **Presentation** | GitHub Pages UI + live demo + clear pitch |

---

## 📝 Implementation Checklist

### Week 1: Foundation
- [ ] Set up project structure
- [ ] Create all SQLAlchemy models
- [ ] Set up Alembic migrations
- [ ] Implement authentication system
- [ ] Write unit tests for auth

### Week 2: Core Features
- [ ] Build inventory CRUD API
- [ ] Implement CSV upload with validation
- [ ] Create analytics service
- [ ] Test sales velocity calculation

### Week 3: Agent Development
- [ ] Set up Fetch.ai uAgent
- [ ] Implement internal API endpoints
- [ ] Create agent monitoring logic
- [ ] Test end-to-end agent workflow

### Week 4: Polish & Deploy
- [ ] Docker setup
- [ ] Deploy to cloud
- [ ] Update GitHub Pages
- [ ] Prepare demo script
- [ ] Record demo video

---

## 🚀 Quick Start Commands

```bash
# Clone repository
git clone https://github.com/ayushjhaa1187-spec/stocksense-agent.git
cd stocksense-agent

# Set up environment
cp .env.example .env
# Edit .env with your values

# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start API server
uvicorn app.main:app --reload --port 8000

# In separate terminal: Start agent
python agent/agent.py

# Or use Docker
docker-compose up --build
```

---

## 📚 Resources

- [Fetch.ai uAgents Documentation](https://docs.fetch.ai/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy AsyncIO](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [Alembic Migrations](https://alembic.sqlalchemy.org/)

---

## 💬 Support

For questions or issues:
- GitHub Issues: https://github.com/ayushjhaa1187-spec/stocksense-agent/issues
- Email: ayushjhaa1187@gmail.com

---

**Last Updated:** February 17, 2026
**Author:** Ayush Jha
**License:** MIT
