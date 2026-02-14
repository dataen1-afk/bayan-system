from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.responses import FileResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone, timedelta
from passlib.context import CryptContext
import jwt
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Import audit calculator
from audit_calculator import calculate_total_audit_time

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
JWT_SECRET = os.environ.get('JWT_SECRET', 'your-secret-key-change-in-production')
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# Security
security = HTTPBearer()

# Ensure contracts directory exists
CONTRACTS_DIR = ROOT_DIR / "contracts"
CONTRACTS_DIR.mkdir(exist_ok=True)

# ================= MODELS =================

class UserRole:
    ADMIN = "admin"
    CLIENT = "client"

class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str = Field(default=UserRole.CLIENT)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: EmailStr
    role: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class TokenResponse(BaseModel):
    token: str
    user: User

class FormField(BaseModel):
    label: str
    type: str  # text, textarea, number, email, etc.
    required: bool = True
    options: Optional[List[str]] = None

class FormCreate(BaseModel):
    client_id: str
    fields: List[FormField]

class Form(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_id: str
    fields: List[FormField]
    responses: Optional[Dict[str, Any]] = None
    status: str = "pending"  # pending, submitted
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class FormSubmission(BaseModel):
    responses: Dict[str, Any]

# ================= QUOTATION/PROPOSAL MODELS =================

class AuditDuration(BaseModel):
    stage_1: float = 0
    stage_2: float = 0
    surveillance_1: float = 0
    surveillance_2: float = 0
    recertification: float = 0

class ServiceFees(BaseModel):
    initial_certification: float = 0
    surveillance_1: float = 0
    surveillance_2: float = 0
    recertification: float = 0
    currency: str = "SAR"

class ProposalCreate(BaseModel):
    application_form_id: str
    # Organization details (pre-filled from application)
    organization_name: str
    organization_address: str
    organization_phone: str
    contact_person: str
    contact_position: str
    contact_email: EmailStr
    # Service details
    standards: List[str]
    scope: str
    total_employees: int
    number_of_sites: int
    # Audit duration
    audit_duration: AuditDuration
    # Pricing
    service_fees: ServiceFees
    # Additional notes
    notes: str = ""
    # Validity
    validity_days: int = 30

class Proposal(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    access_token: str = Field(default_factory=lambda: str(uuid.uuid4()))  # For client access
    application_form_id: str
    # Organization details
    organization_name: str
    organization_address: str
    organization_phone: str
    contact_person: str
    contact_position: str
    contact_email: EmailStr
    # Service details
    standards: List[str]
    scope: str
    total_employees: int
    number_of_sites: int
    # Audit duration
    audit_duration: AuditDuration
    # Pricing
    service_fees: ServiceFees
    total_amount: float = 0
    # Additional
    notes: str = ""
    validity_days: int = 30
    # Status
    status: str = "pending"  # pending, accepted, rejected, expired
    # Signatures
    issuer_name: str = ""
    issuer_designation: str = ""
    issued_date: Optional[datetime] = None
    # Client response
    client_response_date: Optional[datetime] = None
    client_signatory_name: str = ""
    client_signatory_designation: str = ""
    rejection_reason: str = ""
    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ProposalResponse(BaseModel):
    status: str  # accepted or rejected
    signatory_name: str = ""
    signatory_designation: str = ""
    rejection_reason: str = ""

class PublicProposalResponse(BaseModel):
    id: str
    organization_name: str
    organization_address: str = ""
    contact_person: str
    contact_email: str
    standards: List[str]
    scope: str
    total_employees: int
    number_of_sites: int
    audit_duration: AuditDuration
    service_fees: ServiceFees
    total_amount: float
    notes: str
    validity_days: int
    status: str
    issuer_name: str
    issuer_designation: str
    issued_date: Optional[datetime]

# ================= CERTIFICATION AGREEMENT MODELS =================

class AgreementAcknowledgements(BaseModel):
    certificationRules: bool = False
    publicDirectory: bool = False
    certificationCommunication: bool = False
    surveillanceSchedule: bool = False
    nonconformityResolution: bool = False
    feesAndPayment: bool = False

class CertificationAgreementSubmit(BaseModel):
    organization_name: str
    organization_address: str
    selected_standards: List[str]
    other_standard: str = ""
    scope_of_services: str
    sites: List[str]
    signatory_name: str
    signatory_position: str
    signatory_date: str
    acknowledgements: AgreementAcknowledgements

class CertificationAgreement(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    proposal_id: str
    proposal_access_token: str
    organization_name: str
    organization_address: str
    selected_standards: List[str]
    other_standard: str = ""
    scope_of_services: str
    sites: List[str]
    signatory_name: str
    signatory_position: str
    signatory_date: str
    acknowledgements: Dict[str, bool] = {}
    status: str = "submitted"  # submitted, contract_generated
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Legacy models (kept for backward compatibility)
class QuotationCreate(BaseModel):
    form_id: str
    client_id: str
    client_email: EmailStr
    price: float
    details: str

class Quotation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    form_id: str
    client_id: str
    price: float
    details: str
    status: str = "pending"  # pending, approved, rejected
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class QuotationResponse(BaseModel):
    status: str  # approved or rejected

class Contract(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    quotation_id: str
    proposal_id: str = ""  # Link to new proposal system
    client_id: str
    pdf_path: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# ================= APPLICATION FORM MODELS =================

class CurrentCertification(BaseModel):
    system: str = ""
    body: str = ""
    validUntil: str = ""

class ApplicationFormData(BaseModel):
    # Step 1: Company Information
    dateOfApplication: str = ""
    companyName: str = ""
    address: str = ""
    phoneNumber: str = ""
    website: str = ""
    email: str = ""
    contactPerson: str = ""
    designation: str = ""
    mobileNumber: str = ""
    contactEmail: str = ""
    legalStatus: str = ""
    
    # Step 2: Certification Selection
    certificationSchemes: List[str] = []
    certificationProgram: str = ""
    combinedAudit: str = ""
    combinedAuditSpecification: str = ""
    isInternalAuditCombined: str = ""
    isMRMCombined: str = ""
    isManualProceduresCombined: str = ""
    isSystemIntegrated: str = ""
    
    # Step 3: Sites & Employees
    numberOfSites: int = 1
    site1Address: str = ""
    site2Address: str = ""
    totalEmployees: str = ""
    locationShifts: str = ""
    fullTimeEmployees: str = ""
    partTimeEmployees: str = ""
    temporaryEmployees: str = ""
    unskilledWorkers: str = ""
    remoteEmployees: str = ""
    
    # Step 4: Existing Certifications
    isAlreadyCertified: str = ""
    currentCertifications: List[CurrentCertification] = []
    isConsultantInvolved: str = ""
    consultantName: str = ""
    transferReason: str = ""
    currentCertificateExpiry: str = ""
    keyBusinessProcesses: str = ""
    
    # Step 5: Management System Requirements
    # EMS
    hasEnvironmentAspectRegister: str = ""
    hasEnvironmentalManual: str = ""
    hasEnvironmentalAuditProgram: str = ""
    
    # FSMS
    numberOfHACCPStudies: str = ""
    numberOfProcessLines: str = ""
    processingType: str = ""
    
    # OHSMS
    hazardsIdentified: str = ""
    criticalRisks: str = ""
    
    # EnMS
    annualEnergyConsumption: str = ""
    numberOfEnergySources: str = ""
    numberOfSEUs: str = ""
    
    # Medical Devices
    productsInRange: str = ""
    medicalDeviceTypes: List[str] = []
    sterilizationType: str = ""
    numberOfDeviceFiles: str = ""
    applicableLegislations: str = ""
    exportCountries: str = ""
    productStandards: str = ""
    intendedUse: str = ""
    outsourceProcesses: str = ""
    
    # ISMS
    businessComplexity: str = ""
    processStandard: str = ""
    managementSystemLevel: str = ""
    itEnvironmentComplexity: str = ""
    outsourcingDependency: str = ""
    systemDevelopment: str = ""
    
    # Step 6: Declaration
    declarationName: str = ""
    declarationDesignation: str = ""
    declarationAgreed: bool = False

class ClientInfo(BaseModel):
    name: str
    company_name: str
    email: EmailStr
    phone: str

class AuditCalculationResult(BaseModel):
    certifications: Dict[str, Any] = {}
    total_md: float = 0
    reduction: float = 0
    final_total_md: float = 0
    phases: Dict[str, float] = {}

class ApplicationFormCreate(BaseModel):
    client_info: ClientInfo

class ApplicationForm(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    access_token: str = Field(default_factory=lambda: str(uuid.uuid4()))  # Public access token
    client_info: ClientInfo
    company_data: Optional[ApplicationFormData] = None
    audit_calculation: Optional[AuditCalculationResult] = None  # Auto-calculated on submit
    status: str = "pending"  # pending, submitted, under_review, approved, rejected
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    submitted_at: Optional[datetime] = None

class ApplicationFormUpdate(BaseModel):
    company_data: ApplicationFormData

class PublicApplicationFormResponse(BaseModel):
    id: str
    client_info: ClientInfo
    company_data: Optional[ApplicationFormData] = None
    status: str

# ================= HELPER FUNCTIONS =================

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_jwt_token(user_id: str, role: str) -> str:
    payload = {
        "user_id": user_id,
        "role": role,
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_jwt_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def send_email(to: str, subject: str, body: str):
    """Send email using SMTP (mock implementation - logs to console)"""
    # For production, configure SMTP settings
    smtp_host = os.environ.get('SMTP_HOST', '')
    smtp_port = int(os.environ.get('SMTP_PORT', 587))
    smtp_user = os.environ.get('SMTP_USER', '')
    smtp_pass = os.environ.get('SMTP_PASS', '')
    
    if smtp_host and smtp_user and smtp_pass:
        # Real email sending
        message = MIMEMultipart()
        message["From"] = smtp_user
        message["To"] = to
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain", "utf-8"))
        
        try:
            await aiosmtplib.send(
                message,
                hostname=smtp_host,
                port=smtp_port,
                username=smtp_user,
                password=smtp_pass,
                start_tls=True
            )
            logging.info(f"Email sent successfully to {to}")
        except Exception as e:
            logging.error(f"Failed to send email: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")
    else:
        # Mock email - just log it
        logging.info(f"[MOCK EMAIL] To: {to}, Subject: {subject}")
        logging.info(f"[MOCK EMAIL] Body: {body[:200]}...")

def calculate_audit_from_form_data(company_data: ApplicationFormData) -> Dict:
    """
    Calculate audit time based on form data.
    Extracts employees, certifications, and risk info from the form.
    """
    # Get number of employees
    try:
        employees = int(company_data.totalEmployees) if company_data.totalEmployees else 10
    except (ValueError, TypeError):
        employees = 10  # Default
    
    # Get certifications selected
    certifications = company_data.certificationSchemes or []
    
    # Map form certification values to calculator format
    cert_mapping = {
        "ISO9001": "ISO9001",
        "ISO14001": "ISO14001",
        "ISO45001": "ISO45001",
        "ISO22000": "ISO22000",
        "ISO13485": "ISO13485",
        "ISO22301": "ISO22301",
        "ISO27001": "ISO27001",
        "ISO50001": "ISO50001",
    }
    
    mapped_certs = [cert_mapping.get(c, c) for c in certifications if c in cert_mapping]
    
    if not mapped_certs:
        return {
            "certifications": {},
            "total_md": 0,
            "reduction": 0,
            "final_total_md": 0,
            "phases": {}
        }
    
    # Get risk category (default to medium)
    risk_category = "medium"
    
    # Get food safety category if ISO 22000 is selected
    food_safety_category = company_data.processingType if company_data.processingType else "AI"
    
    # Check if integrated with ISO 9001
    integrated_with_9001 = "ISO9001" in mapped_certs
    
    # Get HACCP studies count
    try:
        haccp_studies = int(company_data.numberOfHACCPStudies) if company_data.numberOfHACCPStudies else 1
    except (ValueError, TypeError):
        haccp_studies = 1
    
    # Calculate
    result = calculate_total_audit_time(
        certifications=mapped_certs,
        employees=employees,
        risk_category=risk_category,
        food_safety_category=food_safety_category,
        haccp_studies=haccp_studies,
        integrated_with_9001=integrated_with_9001
    )
    
    return result

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    token = credentials.credentials
    payload = decode_jwt_token(token)
    return payload

async def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    if current_user.get("role") != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

async def send_email(to: str, subject: str, body: str):
    """Send email using SMTP"""
    try:
        smtp_host = os.environ.get('SMTP_HOST')
        smtp_port = int(os.environ.get('SMTP_PORT', 587))
        smtp_user = os.environ.get('SMTP_USER')
        smtp_pass = os.environ.get('SMTP_PASS')
        
        if not all([smtp_host, smtp_user, smtp_pass]):
            logging.warning("SMTP not configured, email not sent")
            return
        
        message = MIMEMultipart()
        message['From'] = smtp_user
        message['To'] = to
        message['Subject'] = subject
        message.attach(MIMEText(body, 'plain'))
        
        await aiosmtplib.send(
            message,
            hostname=smtp_host,
            port=smtp_port,
            username=smtp_user,
            password=smtp_pass,
            start_tls=True
        )
        logging.info(f"Email sent to {to}")
    except Exception as e:
        logging.error(f"Failed to send email: {e}")

def generate_contract_pdf(quotation: Quotation, user: dict) -> str:
    """Generate PDF contract"""
    filename = f"contract_{quotation.id}_{int(datetime.now().timestamp())}.pdf"
    filepath = CONTRACTS_DIR / filename
    
    c = canvas.Canvas(str(filepath), pagesize=letter)
    width, height = letter
    
    # Header
    c.setFont("Helvetica-Bold", 24)
    c.drawString(1 * inch, height - 1 * inch, "SERVICE CONTRACT")
    
    # Contract details
    c.setFont("Helvetica", 12)
    y = height - 2 * inch
    
    c.drawString(1 * inch, y, f"Contract ID: {quotation.id}")
    y -= 0.3 * inch
    
    c.drawString(1 * inch, y, f"Date: {datetime.now().strftime('%Y-%m-%d')}")
    y -= 0.3 * inch
    
    c.drawString(1 * inch, y, f"Client ID: {quotation.client_id}")
    y -= 0.5 * inch
    
    # Price
    c.setFont("Helvetica-Bold", 14)
    c.drawString(1 * inch, y, f"Total Price: ${quotation.price:,.2f}")
    y -= 0.5 * inch
    
    # Details
    c.setFont("Helvetica", 12)
    c.drawString(1 * inch, y, "Service Details:")
    y -= 0.3 * inch
    
    # Wrap text for details
    detail_lines = quotation.details.split('\n')
    for line in detail_lines[:10]:  # Limit to 10 lines
        if y < 2 * inch:
            break
        c.drawString(1.2 * inch, y, line[:80])  # Limit line length
        y -= 0.25 * inch
    
    # Footer
    c.setFont("Helvetica", 10)
    c.drawString(1 * inch, 1 * inch, "This contract is legally binding upon approval by both parties.")
    
    c.save()
    return str(filepath)

# ================= ROUTES =================

@api_router.get("/")
async def root():
    return {"message": "Service Contract Management API"}

# Authentication routes
@api_router.post("/auth/register", response_model=User)
async def register(user_data: UserRegister):
    # Check if user exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Validate role
    if user_data.role not in [UserRole.ADMIN, UserRole.CLIENT]:
        raise HTTPException(status_code=400, detail="Invalid role")
    
    # Create user
    user = User(
        name=user_data.name,
        email=user_data.email,
        role=user_data.role
    )
    
    user_doc = user.model_dump()
    user_doc['password'] = hash_password(user_data.password)
    user_doc['created_at'] = user_doc['created_at'].isoformat()
    
    await db.users.insert_one(user_doc)
    return user

@api_router.post("/auth/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    # Find user
    user_doc = await db.users.find_one({"email": credentials.email})
    if not user_doc:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Verify password
    if not verify_password(credentials.password, user_doc['password']):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Create token
    token = create_jwt_token(user_doc['id'], user_doc['role'])
    
    # Return user info (without password)
    user = User(
        id=user_doc['id'],
        name=user_doc['name'],
        email=user_doc['email'],
        role=user_doc['role'],
        created_at=datetime.fromisoformat(user_doc['created_at']) if isinstance(user_doc['created_at'], str) else user_doc['created_at']
    )
    
    return TokenResponse(token=token, user=user)

@api_router.get("/auth/me", response_model=User)
async def get_me(current_user: dict = Depends(get_current_user)):
    user_doc = await db.users.find_one({"id": current_user['user_id']})
    if not user_doc:
        raise HTTPException(status_code=404, detail="User not found")
    
    return User(
        id=user_doc['id'],
        name=user_doc['name'],
        email=user_doc['email'],
        role=user_doc['role'],
        created_at=datetime.fromisoformat(user_doc['created_at']) if isinstance(user_doc['created_at'], str) else user_doc['created_at']
    )

# Form routes
@api_router.post("/forms", response_model=Form)
async def create_form(form_data: FormCreate, current_user: dict = Depends(require_admin)):
    form = Form(
        client_id=form_data.client_id,
        fields=form_data.fields
    )
    
    form_doc = form.model_dump()
    form_doc['created_at'] = form_doc['created_at'].isoformat()
    
    await db.forms.insert_one(form_doc)
    return form

@api_router.get("/forms", response_model=List[Form])
async def get_forms(current_user: dict = Depends(get_current_user)):
    query = {}
    # If client, only show their forms
    if current_user['role'] == UserRole.CLIENT:
        query = {"client_id": current_user['user_id']}
    
    forms = await db.forms.find(query, {"_id": 0}).to_list(1000)
    
    for form in forms:
        if isinstance(form['created_at'], str):
            form['created_at'] = datetime.fromisoformat(form['created_at'])
    
    return forms

@api_router.get("/forms/{form_id}", response_model=Form)
async def get_form(form_id: str, current_user: dict = Depends(get_current_user)):
    form = await db.forms.find_one({"id": form_id}, {"_id": 0})
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    
    # Check access
    if current_user['role'] == UserRole.CLIENT and form['client_id'] != current_user['user_id']:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if isinstance(form['created_at'], str):
        form['created_at'] = datetime.fromisoformat(form['created_at'])
    
    return Form(**form)

@api_router.post("/forms/{form_id}/submit", response_model=Form)
async def submit_form(form_id: str, submission: FormSubmission, current_user: dict = Depends(get_current_user)):
    form = await db.forms.find_one({"id": form_id})
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    
    # Check access
    if current_user['role'] == UserRole.CLIENT and form['client_id'] != current_user['user_id']:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Update form
    await db.forms.update_one(
        {"id": form_id},
        {"$set": {"responses": submission.responses, "status": "submitted"}}
    )
    
    updated_form = await db.forms.find_one({"id": form_id}, {"_id": 0})
    if isinstance(updated_form['created_at'], str):
        updated_form['created_at'] = datetime.fromisoformat(updated_form['created_at'])
    
    return Form(**updated_form)

# Quotation routes
@api_router.post("/quotations", response_model=Quotation)
async def create_quotation(quotation_data: QuotationCreate, current_user: dict = Depends(require_admin)):
    quotation = Quotation(
        form_id=quotation_data.form_id,
        client_id=quotation_data.client_id,
        price=quotation_data.price,
        details=quotation_data.details
    )
    
    quotation_doc = quotation.model_dump()
    quotation_doc['created_at'] = quotation_doc['created_at'].isoformat()
    
    await db.quotations.insert_one(quotation_doc)
    
    # Send email notification
    await send_email(
        quotation_data.client_email,
        "New Quotation Received",
        f"You have received a new quotation for ${quotation_data.price}.\n\nDetails:\n{quotation_data.details}\n\nPlease log in to your account to review and respond."
    )
    
    return quotation

@api_router.get("/quotations", response_model=List[Quotation])
async def get_quotations(current_user: dict = Depends(get_current_user)):
    query = {}
    # If client, only show their quotations
    if current_user['role'] == UserRole.CLIENT:
        query = {"client_id": current_user['user_id']}
    
    quotations = await db.quotations.find(query, {"_id": 0}).to_list(1000)
    
    for quotation in quotations:
        if isinstance(quotation['created_at'], str):
            quotation['created_at'] = datetime.fromisoformat(quotation['created_at'])
    
    return quotations

@api_router.get("/quotations/{quotation_id}", response_model=Quotation)
async def get_quotation(quotation_id: str, current_user: dict = Depends(get_current_user)):
    quotation = await db.quotations.find_one({"id": quotation_id}, {"_id": 0})
    if not quotation:
        raise HTTPException(status_code=404, detail="Quotation not found")
    
    # Check access
    if current_user['role'] == UserRole.CLIENT and quotation['client_id'] != current_user['user_id']:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if isinstance(quotation['created_at'], str):
        quotation['created_at'] = datetime.fromisoformat(quotation['created_at'])
    
    return Quotation(**quotation)

@api_router.post("/quotations/{quotation_id}/respond")
async def respond_to_quotation(quotation_id: str, response: QuotationResponse, current_user: dict = Depends(get_current_user)):
    quotation_doc = await db.quotations.find_one({"id": quotation_id})
    if not quotation_doc:
        raise HTTPException(status_code=404, detail="Quotation not found")
    
    # Check access
    if current_user['role'] == UserRole.CLIENT and quotation_doc['client_id'] != current_user['user_id']:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Validate status
    if response.status not in ["approved", "rejected", "modifications_requested"]:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    # Update quotation
    await db.quotations.update_one(
        {"id": quotation_id},
        {"$set": {"status": response.status}}
    )
    
    # If approved, generate contract
    if response.status == "approved":
        quotation_obj = Quotation(**{
            **quotation_doc,
            'created_at': datetime.fromisoformat(quotation_doc['created_at']) if isinstance(quotation_doc['created_at'], str) else quotation_doc['created_at']
        })
        
        pdf_path = generate_contract_pdf(quotation_obj, current_user)
        
        contract = Contract(
            quotation_id=quotation_id,
            client_id=quotation_doc['client_id'],
            pdf_path=pdf_path
        )
        
        contract_doc = contract.model_dump()
        contract_doc['created_at'] = contract_doc['created_at'].isoformat()
        
        await db.contracts.insert_one(contract_doc)
        
        return {
            "message": "Quotation approved and contract generated",
            "contract": contract
        }
    
    return {"message": f"Quotation {response.status}"}

# Contract routes
@api_router.get("/contracts", response_model=List[Contract])
async def get_contracts(current_user: dict = Depends(get_current_user)):
    query = {}
    # If client, only show their contracts
    if current_user['role'] == UserRole.CLIENT:
        query = {"client_id": current_user['user_id']}
    
    contracts = await db.contracts.find(query, {"_id": 0}).to_list(1000)
    
    for contract in contracts:
        if isinstance(contract['created_at'], str):
            contract['created_at'] = datetime.fromisoformat(contract['created_at'])
    
    return contracts

@api_router.get("/contracts/{contract_id}/download")
async def download_contract(contract_id: str, current_user: dict = Depends(get_current_user)):
    contract = await db.contracts.find_one({"id": contract_id})
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    
    # Check access
    if current_user['role'] == UserRole.CLIENT and contract['client_id'] != current_user['user_id']:
        raise HTTPException(status_code=403, detail="Access denied")
    
    pdf_path = Path(contract['pdf_path'])
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="Contract file not found")
    
    return FileResponse(
        path=pdf_path,
        filename=pdf_path.name,
        media_type='application/pdf'
    )

# ================= USER ROUTES =================

@api_router.get("/users/clients")
async def get_clients(current_user: dict = Depends(require_admin)):
    """Get all client users (admin only)"""
    clients = await db.users.find({"role": UserRole.CLIENT}, {"_id": 0, "password": 0}).to_list(1000)
    return clients

# ================= APPLICATION FORM ROUTES =================

@api_router.post("/application-forms", response_model=ApplicationForm)
async def create_application_form(form_data: ApplicationFormCreate, current_user: dict = Depends(require_admin)):
    """Admin creates an application form for a client (no login required for client)"""
    form = ApplicationForm(
        client_info=form_data.client_info
    )
    
    form_doc = form.model_dump()
    form_doc['created_at'] = form_doc['created_at'].isoformat()
    if form_doc.get('submitted_at'):
        form_doc['submitted_at'] = form_doc['submitted_at'].isoformat()
    
    await db.application_forms.insert_one(form_doc)
    return form

@api_router.get("/application-forms", response_model=List[ApplicationForm])
async def get_application_forms(current_user: dict = Depends(require_admin)):
    """Get all application forms (admin only)"""
    # Only return forms that have client_info (new format)
    forms = await db.application_forms.find({"client_info": {"$exists": True}}, {"_id": 0}).to_list(1000)
    
    for form in forms:
        if isinstance(form.get('created_at'), str):
            form['created_at'] = datetime.fromisoformat(form['created_at'])
        if form.get('submitted_at') and isinstance(form['submitted_at'], str):
            form['submitted_at'] = datetime.fromisoformat(form['submitted_at'])
    
    return forms

@api_router.get("/application-forms/{form_id}", response_model=ApplicationForm)
async def get_application_form(form_id: str, current_user: dict = Depends(require_admin)):
    """Get a specific application form (admin only)"""
    form = await db.application_forms.find_one({"id": form_id}, {"_id": 0})
    if not form:
        raise HTTPException(status_code=404, detail="Application form not found")
    
    if isinstance(form.get('created_at'), str):
        form['created_at'] = datetime.fromisoformat(form['created_at'])
    if form.get('submitted_at') and isinstance(form['submitted_at'], str):
        form['submitted_at'] = datetime.fromisoformat(form['submitted_at'])
    
    return ApplicationForm(**form)

@api_router.post("/application-forms/{form_id}/send-email")
async def send_form_email(form_id: str, current_user: dict = Depends(require_admin)):
    """Send the form link to the client via email"""
    form = await db.application_forms.find_one({"id": form_id})
    if not form:
        raise HTTPException(status_code=404, detail="Application form not found")
    
    # Get frontend URL from environment or use default
    frontend_url = os.environ.get('FRONTEND_URL', 'https://bayan-contracts.preview.emergentagent.com')
    form_link = f"{frontend_url}/form/{form['access_token']}"
    
    client_info = form['client_info']
    email_body = f"""
مرحباً {client_info['name']}،

تم إنشاء نموذج طلب اعتماد لشركتكم {client_info['company_name']}.

يرجى النقر على الرابط التالي لملء النموذج:
{form_link}

مع أطيب التحيات،
بيان للتحقق والمطابقة

---

Hello {client_info['name']},

A certification application form has been created for your company {client_info['company_name']}.

Please click the following link to fill out the form:
{form_link}

Best regards,
Bayan Auditing & Conformity
"""
    
    await send_email(
        to=client_info['email'],
        subject="طلب اعتماد - Certification Application Form",
        body=email_body
    )
    
    return {"message": "Email sent successfully", "form_link": form_link}

# ================= PUBLIC FORM ACCESS (NO LOGIN REQUIRED) =================

@api_router.get("/public/form/{access_token}", response_model=PublicApplicationFormResponse)
async def get_public_form(access_token: str):
    """Public access to form using access token (no login required)"""
    form = await db.application_forms.find_one({"access_token": access_token}, {"_id": 0})
    if not form:
        raise HTTPException(status_code=404, detail="Form not found or invalid link")
    
    return PublicApplicationFormResponse(
        id=form['id'],
        client_info=form['client_info'],
        company_data=form.get('company_data'),
        status=form['status']
    )

@api_router.put("/public/form/{access_token}", response_model=PublicApplicationFormResponse)
async def update_public_form(access_token: str, update_data: ApplicationFormUpdate):
    """Public save draft (no login required)"""
    form = await db.application_forms.find_one({"access_token": access_token})
    if not form:
        raise HTTPException(status_code=404, detail="Form not found or invalid link")
    
    # Only allow updates if form is pending
    if form['status'] != 'pending':
        raise HTTPException(status_code=400, detail="Cannot update a submitted form")
    
    # Update form data
    await db.application_forms.update_one(
        {"access_token": access_token},
        {"$set": {"company_data": update_data.company_data.model_dump()}}
    )
    
    updated_form = await db.application_forms.find_one({"access_token": access_token}, {"_id": 0})
    
    return PublicApplicationFormResponse(
        id=updated_form['id'],
        client_info=updated_form['client_info'],
        company_data=updated_form.get('company_data'),
        status=updated_form['status']
    )

@api_router.post("/public/form/{access_token}/submit", response_model=PublicApplicationFormResponse)
async def submit_public_form(access_token: str, update_data: ApplicationFormUpdate):
    """Public form submission (no login required)"""
    form = await db.application_forms.find_one({"access_token": access_token})
    if not form:
        raise HTTPException(status_code=404, detail="Form not found or invalid link")
    
    # Only allow submission if form is pending
    if form['status'] != 'pending':
        raise HTTPException(status_code=400, detail="Form has already been submitted")
    
    # Validate required fields
    company_data = update_data.company_data
    if not company_data.companyName or not company_data.declarationAgreed:
        raise HTTPException(status_code=400, detail="Company name and declaration agreement are required")
    
    # Calculate audit time automatically
    audit_calculation = calculate_audit_from_form_data(company_data)
    
    # Update and submit
    submitted_at = datetime.now(timezone.utc)
    await db.application_forms.update_one(
        {"access_token": access_token},
        {
            "$set": {
                "company_data": company_data.model_dump(),
                "audit_calculation": audit_calculation,
                "status": "submitted",
                "submitted_at": submitted_at.isoformat()
            }
        }
    )
    
    updated_form = await db.application_forms.find_one({"access_token": access_token}, {"_id": 0})
    
    return PublicApplicationFormResponse(
        id=updated_form['id'],
        client_info=updated_form['client_info'],
        company_data=updated_form.get('company_data'),
        status=updated_form['status']
    )

# ================= PROPOSAL ROUTES =================

@api_router.post("/proposals", response_model=Proposal)
async def create_proposal(proposal_data: ProposalCreate, current_user: dict = Depends(require_admin)):
    """Admin creates a proposal/quotation for a client"""
    # Calculate total amount
    fees = proposal_data.service_fees
    total = fees.initial_certification + fees.surveillance_1 + fees.surveillance_2 + fees.recertification
    
    proposal = Proposal(
        application_form_id=proposal_data.application_form_id,
        organization_name=proposal_data.organization_name,
        organization_address=proposal_data.organization_address,
        organization_phone=proposal_data.organization_phone,
        contact_person=proposal_data.contact_person,
        contact_position=proposal_data.contact_position,
        contact_email=proposal_data.contact_email,
        standards=proposal_data.standards,
        scope=proposal_data.scope,
        total_employees=proposal_data.total_employees,
        number_of_sites=proposal_data.number_of_sites,
        audit_duration=proposal_data.audit_duration,
        service_fees=proposal_data.service_fees,
        total_amount=total,
        notes=proposal_data.notes,
        validity_days=proposal_data.validity_days,
        issuer_name=current_user.get('name', 'Admin'),
        issuer_designation="Certification Manager",
        issued_date=datetime.now(timezone.utc)
    )
    
    proposal_doc = proposal.model_dump()
    proposal_doc['created_at'] = proposal_doc['created_at'].isoformat()
    proposal_doc['issued_date'] = proposal_doc['issued_date'].isoformat() if proposal_doc['issued_date'] else None
    
    await db.proposals.insert_one(proposal_doc)
    
    # Update application form status to under_review
    await db.application_forms.update_one(
        {"id": proposal_data.application_form_id},
        {"$set": {"status": "under_review"}}
    )
    
    return proposal

@api_router.get("/proposals", response_model=List[Proposal])
async def get_proposals(current_user: dict = Depends(require_admin)):
    """Get all proposals (admin only)"""
    proposals = await db.proposals.find({}, {"_id": 0}).to_list(1000)
    
    for p in proposals:
        if isinstance(p.get('created_at'), str):
            p['created_at'] = datetime.fromisoformat(p['created_at'])
        if p.get('issued_date') and isinstance(p['issued_date'], str):
            p['issued_date'] = datetime.fromisoformat(p['issued_date'])
        if p.get('client_response_date') and isinstance(p['client_response_date'], str):
            p['client_response_date'] = datetime.fromisoformat(p['client_response_date'])
    
    return proposals

@api_router.get("/proposals/{proposal_id}", response_model=Proposal)
async def get_proposal(proposal_id: str, current_user: dict = Depends(require_admin)):
    """Get a specific proposal"""
    proposal = await db.proposals.find_one({"id": proposal_id}, {"_id": 0})
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    
    if isinstance(proposal.get('created_at'), str):
        proposal['created_at'] = datetime.fromisoformat(proposal['created_at'])
    if proposal.get('issued_date') and isinstance(proposal['issued_date'], str):
        proposal['issued_date'] = datetime.fromisoformat(proposal['issued_date'])
    
    return Proposal(**proposal)

@api_router.post("/proposals/{proposal_id}/send")
async def send_proposal(proposal_id: str, current_user: dict = Depends(require_admin)):
    """Send proposal link to client via email"""
    proposal = await db.proposals.find_one({"id": proposal_id})
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    
    frontend_url = os.environ.get('FRONTEND_URL', 'https://bayan-contracts.preview.emergentagent.com')
    proposal_link = f"{frontend_url}/proposal/{proposal['access_token']}"
    
    email_body = f"""
مرحباً {proposal['contact_person']}،

نرفق لكم عرض السعر للحصول على شهادة الاعتماد لشركتكم {proposal['organization_name']}.

يرجى النقر على الرابط التالي لمراجعة العرض والموافقة عليه:
{proposal_link}

العرض صالح لمدة {proposal['validity_days']} يوماً.

مع أطيب التحيات،
بيان للتحقق والمطابقة

---

Hello {proposal['contact_person']},

Please find attached the price quotation for certification of your organization {proposal['organization_name']}.

Click the following link to review and accept the proposal:
{proposal_link}

This proposal is valid for {proposal['validity_days']} days.

Best regards,
Bayan Auditing & Conformity
"""
    
    await send_email(
        to=proposal['contact_email'],
        subject=f"عرض سعر - Price Quotation - {proposal['organization_name']}",
        body=email_body
    )
    
    return {"message": "Proposal sent successfully", "proposal_link": proposal_link}

# ================= PUBLIC PROPOSAL ACCESS =================

@api_router.get("/public/proposal/{access_token}", response_model=PublicProposalResponse)
async def get_public_proposal(access_token: str):
    """Public access to proposal (no login required)"""
    proposal = await db.proposals.find_one({"access_token": access_token}, {"_id": 0})
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found or invalid link")
    
    return PublicProposalResponse(
        id=proposal['id'],
        organization_name=proposal['organization_name'],
        organization_address=proposal.get('organization_address', ''),
        contact_person=proposal['contact_person'],
        contact_email=proposal['contact_email'],
        standards=proposal['standards'],
        scope=proposal['scope'],
        total_employees=proposal['total_employees'],
        number_of_sites=proposal['number_of_sites'],
        audit_duration=proposal['audit_duration'],
        service_fees=proposal['service_fees'],
        total_amount=proposal['total_amount'],
        notes=proposal.get('notes', ''),
        validity_days=proposal['validity_days'],
        status=proposal['status'],
        issuer_name=proposal.get('issuer_name', ''),
        issuer_designation=proposal.get('issuer_designation', ''),
        issued_date=datetime.fromisoformat(proposal['issued_date']) if proposal.get('issued_date') else None
    )

@api_router.post("/public/proposal/{access_token}/respond")
async def respond_to_proposal(access_token: str, response: ProposalResponse):
    """Client accepts or rejects proposal (no login required)"""
    proposal = await db.proposals.find_one({"access_token": access_token})
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found or invalid link")
    
    if proposal['status'] != 'pending':
        raise HTTPException(status_code=400, detail="Proposal has already been responded to")
    
    update_data = {
        "status": response.status,
        "client_response_date": datetime.now(timezone.utc).isoformat(),
        "client_signatory_name": response.signatory_name,
        "client_signatory_designation": response.signatory_designation,
    }
    
    if response.status == "rejected":
        update_data["rejection_reason"] = response.rejection_reason
    
    await db.proposals.update_one(
        {"access_token": access_token},
        {"$set": update_data}
    )
    
    # If accepted, update application form status and create contract
    if response.status == "accepted":
        await db.application_forms.update_one(
            {"id": proposal['application_form_id']},
            {"$set": {"status": "approved"}}
        )
        
        # TODO: Generate contract PDF
        contract = Contract(
            quotation_id="",
            proposal_id=proposal['id'],
            client_id=proposal['organization_name'],
            pdf_path=""  # Will be generated
        )
        contract_doc = contract.model_dump()
        contract_doc['created_at'] = contract_doc['created_at'].isoformat()
        await db.contracts.insert_one(contract_doc)
    
    return {"message": f"Proposal {response.status} successfully"}

# ================= CERTIFICATION AGREEMENT ROUTES =================

@api_router.post("/public/agreement/{access_token}/submit")
async def submit_certification_agreement(access_token: str, agreement_data: CertificationAgreementSubmit):
    """Submit certification agreement form (no login required)"""
    # Find the proposal by access token
    proposal = await db.proposals.find_one({"access_token": access_token})
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found or invalid link")
    
    # Check if proposal is accepted
    if proposal['status'] != 'accepted':
        raise HTTPException(status_code=400, detail="Proposal must be accepted before signing agreement")
    
    # Check if agreement already exists
    existing_agreement = await db.certification_agreements.find_one({"proposal_access_token": access_token})
    if existing_agreement:
        raise HTTPException(status_code=400, detail="Agreement has already been submitted")
    
    # Create certification agreement
    agreement = CertificationAgreement(
        proposal_id=proposal['id'],
        proposal_access_token=access_token,
        organization_name=agreement_data.organization_name,
        organization_address=agreement_data.organization_address,
        selected_standards=agreement_data.selected_standards,
        other_standard=agreement_data.other_standard,
        scope_of_services=agreement_data.scope_of_services,
        sites=agreement_data.sites,
        signatory_name=agreement_data.signatory_name,
        signatory_position=agreement_data.signatory_position,
        signatory_date=agreement_data.signatory_date,
        acknowledgements=agreement_data.acknowledgements.model_dump()
    )
    
    agreement_doc = agreement.model_dump()
    agreement_doc['created_at'] = agreement_doc['created_at'].isoformat()
    
    await db.certification_agreements.insert_one(agreement_doc)
    
    # Update proposal status to indicate agreement signed
    await db.proposals.update_one(
        {"access_token": access_token},
        {"$set": {"status": "agreement_signed"}}
    )
    
    # Update application form status
    await db.application_forms.update_one(
        {"id": proposal['application_form_id']},
        {"$set": {"status": "agreement_signed"}}
    )
    
    return {"message": "Certification agreement submitted successfully", "agreement_id": agreement.id}

@api_router.get("/public/agreement/{access_token}")
async def get_certification_agreement(access_token: str):
    """Get certification agreement status"""
    agreement = await db.certification_agreements.find_one({"proposal_access_token": access_token}, {"_id": 0})
    if agreement:
        return {"status": "submitted", "agreement": agreement}
    
    # Check if proposal exists and is accepted
    proposal = await db.proposals.find_one({"access_token": access_token}, {"_id": 0})
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    
    if proposal['status'] != 'accepted':
        raise HTTPException(status_code=400, detail="Proposal is not accepted")
    
    return {"status": "pending", "proposal": proposal}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
