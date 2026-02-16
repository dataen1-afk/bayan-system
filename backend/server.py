from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.responses import FileResponse, Response, RedirectResponse
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

# Import PDF generators
from pdf_generator import generate_contract_pdf
from bilingual_pdf_generator import generate_bilingual_contract_pdf

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

class ModificationRequest(BaseModel):
    comment: str
    requested_changes: str = ""

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
    modification_comment: str = ""
    modification_requested_changes: str = ""

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
    signature_image: str  # Base64 encoded signature image (required)
    stamp_image: str  # Base64 encoded stamp image (required)

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
    signature_image: Optional[str] = None  # Base64 encoded signature image
    stamp_image: Optional[str] = None  # Base64 encoded stamp image
    status: str = "submitted"  # submitted, contract_generated
    contract_pdf_path: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# ================= NOTIFICATION MODELS =================

class Notification(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: str  # form_submitted, proposal_sent, proposal_accepted, proposal_rejected, agreement_signed
    title: str
    message: str
    related_id: Optional[str] = None  # ID of related form/proposal/agreement
    related_type: Optional[str] = None  # form, proposal, agreement
    is_read: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class NotificationCreate(BaseModel):
    type: str
    title: str
    message: str
    related_id: Optional[str] = None
    related_type: Optional[str] = None

# ================= TEMPLATE MODELS =================

class CertificationPackage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    name_ar: str
    description: str
    description_ar: str
    standards: List[str]
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ProposalTemplate(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    name_ar: str
    description: str = ""
    default_fees: Dict[str, float] = {}  # initial_certification, surveillance_1, surveillance_2, recertification
    default_notes: str = ""
    default_validity_days: int = 30
    is_active: bool = True
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

def generate_legacy_contract_pdf(quotation: Quotation, user: dict) -> str:
    """Generate PDF contract (legacy - for old quotation system)"""
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
    
    # Sort by most recent first
    contracts = await db.contracts.find(query, {"_id": 0}).sort("created_at", -1).to_list(1000)
    
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
    """Get all application forms (admin only) - sorted by most recent first"""
    # Only return forms that have client_info (new format), sorted by created_at descending
    forms = await db.application_forms.find({"client_info": {"$exists": True}}, {"_id": 0}).sort("created_at", -1).to_list(1000)
    
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
    frontend_url = os.environ.get('FRONTEND_URL', 'https://bayan-audit-forms.preview.emergentagent.com')
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
    
    # Create notification for admin
    client_name = form.get('client_info', {}).get('company_name', 'Unknown')
    await create_notification(
        notification_type="form_submitted",
        title="طلب اعتماد جديد",
        message=f"قامت {client_name} بتقديم طلب اعتماد جديد",
        related_id=updated_form['id'],
        related_type="form"
    )
    
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
    """Get all proposals (admin only) - sorted by most recent first"""
    proposals = await db.proposals.find({}, {"_id": 0}).sort("created_at", -1).to_list(1000)
    
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
    
    frontend_url = os.environ.get('FRONTEND_URL', 'https://bayan-audit-forms.preview.emergentagent.com')
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
        issued_date=datetime.fromisoformat(proposal['issued_date']) if proposal.get('issued_date') else None,
        modification_comment=proposal.get('modification_comment', ''),
        modification_requested_changes=proposal.get('modification_requested_changes', '')
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
    
    # Create notification for admin
    org_name = proposal.get('organization_name', 'Unknown')
    if response.status == "accepted":
        await create_notification(
            notification_type="proposal_accepted",
            title="تم قبول العرض",
            message=f"قامت {org_name} بقبول عرض السعر",
            related_id=proposal['id'],
            related_type="proposal"
        )
    else:
        await create_notification(
            notification_type="proposal_rejected",
            title="تم رفض العرض",
            message=f"قامت {org_name} برفض عرض السعر",
            related_id=proposal['id'],
            related_type="proposal"
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

# ================= PUBLIC PROPOSAL PDF DOWNLOAD =================

@api_router.get("/public/proposals/{access_token}/bilingual_pdf")
async def get_public_proposal_bilingual_pdf(access_token: str):
    """Public access to download bilingual proposal PDF (no login required)"""
    proposal = await db.proposals.find_one({"access_token": access_token}, {"_id": 0})
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found or invalid link")
    
    # Generate the PDF
    pdf_path = await generate_bilingual_proposal_pdf_file(proposal)
    
    return FileResponse(
        pdf_path,
        media_type='application/pdf',
        filename=f'proposal_{proposal["id"][:8]}_ar_en.pdf'
    )

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
    
    # Validate signature is provided
    if not agreement_data.signature_image:
        raise HTTPException(status_code=422, detail="Digital signature is required")
    
    # Validate company seal is provided
    if not agreement_data.stamp_image:
        raise HTTPException(status_code=422, detail="Company seal/stamp is required")
    
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
        acknowledgements=agreement_data.acknowledgements.model_dump(),
        signature_image=agreement_data.signature_image,
        stamp_image=agreement_data.stamp_image
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
    
    # Create notification for admin
    await create_notification(
        notification_type="agreement_signed",
        title="اتفاقية جديدة موقعة",
        message=f"قامت {agreement_data.organization_name} بتوقيع اتفاقية الاعتماد",
        related_id=agreement.id,
        related_type="agreement"
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

# ================= PDF CONTRACT GENERATION =================

@api_router.get("/contracts/{agreement_id}/pdf")
async def generate_contract_pdf_endpoint(agreement_id: str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Generate PDF contract for a signed agreement (Admin only)"""
    await get_current_user(credentials)
    
    # Get agreement
    agreement = await db.certification_agreements.find_one({"id": agreement_id}, {"_id": 0})
    if not agreement:
        raise HTTPException(status_code=404, detail="Agreement not found")
    
    # Get proposal
    proposal = await db.proposals.find_one({"id": agreement['proposal_id']}, {"_id": 0})
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    
    # Generate PDF
    try:
        pdf_bytes = generate_contract_pdf(agreement, proposal)
        
        # Update agreement status
        await db.certification_agreements.update_one(
            {"id": agreement_id},
            {"$set": {"status": "contract_generated"}}
        )
        
        # Return PDF
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=contract_{agreement_id[:8]}.pdf"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")

@api_router.get("/public/contracts/{access_token}/pdf")
async def get_public_contract_pdf(access_token: str):
    """Get PDF contract for a signed agreement (Public - client access)"""
    # Get agreement by access token
    agreement = await db.certification_agreements.find_one({"proposal_access_token": access_token}, {"_id": 0})
    if not agreement:
        raise HTTPException(status_code=404, detail="Agreement not found")
    
    # Get proposal
    proposal = await db.proposals.find_one({"id": agreement['proposal_id']}, {"_id": 0})
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    
    # Generate PDF
    try:
        pdf_bytes = generate_contract_pdf(agreement, proposal)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=contract_{agreement['id'][:8]}.pdf"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")

# ================= BILINGUAL PDF CONTRACT GENERATION =================

@api_router.get("/contracts/{agreement_id}/pdf/bilingual")
async def generate_bilingual_contract_pdf_endpoint(agreement_id: str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Generate bilingual PDF contract (Arabic + English) for a signed agreement (Admin only)"""
    await get_current_user(credentials)
    
    # Get agreement
    agreement = await db.certification_agreements.find_one({"id": agreement_id}, {"_id": 0})
    if not agreement:
        raise HTTPException(status_code=404, detail="Agreement not found")
    
    # Get proposal
    proposal = await db.proposals.find_one({"id": agreement['proposal_id']}, {"_id": 0})
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    
    # Generate bilingual PDF
    try:
        pdf_bytes = generate_bilingual_contract_pdf(agreement, proposal)
        
        # Update agreement status
        await db.certification_agreements.update_one(
            {"id": agreement_id},
            {"$set": {"status": "contract_generated"}}
        )
        
        # Return PDF
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=contract_bilingual_{agreement_id[:8]}.pdf"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating bilingual PDF: {str(e)}")

@api_router.get("/public/contracts/{access_token}/pdf/bilingual")
async def get_public_bilingual_contract_pdf(access_token: str):
    """Get bilingual PDF contract (Arabic + English) for a signed agreement (Public - client access)"""
    # Get agreement by access token
    agreement = await db.certification_agreements.find_one({"proposal_access_token": access_token}, {"_id": 0})
    if not agreement:
        raise HTTPException(status_code=404, detail="Agreement not found")
    
    # Get proposal
    proposal = await db.proposals.find_one({"id": agreement['proposal_id']}, {"_id": 0})
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    
    # Generate bilingual PDF
    try:
        pdf_bytes = generate_bilingual_contract_pdf(agreement, proposal)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=contract_bilingual_{agreement['id'][:8]}.pdf"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating bilingual PDF: {str(e)}")

# ================= NOTIFICATION ROUTES =================

async def create_notification(notification_type: str, title: str, message: str, related_id: str = None, related_type: str = None):
    """Helper function to create a notification"""
    notification = Notification(
        type=notification_type,
        title=title,
        message=message,
        related_id=related_id,
        related_type=related_type
    )
    notification_doc = notification.model_dump()
    notification_doc['created_at'] = notification_doc['created_at'].isoformat()
    await db.notifications.insert_one(notification_doc)
    return notification

@api_router.get("/notifications")
async def get_notifications(credentials: HTTPAuthorizationCredentials = Depends(security), limit: int = 20, unread_only: bool = False):
    """Get admin notifications"""
    await get_current_user(credentials)
    
    query = {}
    if unread_only:
        query['is_read'] = False
    
    notifications = await db.notifications.find(query, {"_id": 0}).sort("created_at", -1).limit(limit).to_list(limit)
    unread_count = await db.notifications.count_documents({"is_read": False})
    
    return {
        "notifications": notifications,
        "unread_count": unread_count
    }

@api_router.put("/notifications/{notification_id}/read")
async def mark_notification_read(notification_id: str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Mark a notification as read"""
    await get_current_user(credentials)
    
    result = await db.notifications.update_one(
        {"id": notification_id},
        {"$set": {"is_read": True}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    return {"message": "Notification marked as read"}

@api_router.put("/notifications/read-all")
async def mark_all_notifications_read(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Mark all notifications as read and clear them"""
    await get_current_user(credentials)
    
    # Delete all notifications to prevent accumulation
    await db.notifications.delete_many({})
    
    return {"message": "All notifications cleared"}

# ================= TEMPLATE ROUTES =================

@api_router.get("/templates/packages")
async def get_certification_packages(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get all certification packages"""
    await get_current_user(credentials)
    packages = await db.certification_packages.find({"is_active": True}, {"_id": 0}).to_list(100)
    return packages

@api_router.post("/templates/packages")
async def create_certification_package(package: CertificationPackage, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Create a new certification package"""
    await get_current_user(credentials)
    package_doc = package.model_dump()
    package_doc['created_at'] = package_doc['created_at'].isoformat()
    await db.certification_packages.insert_one(package_doc)
    return {"message": "Package created", "id": package.id}

@api_router.delete("/templates/packages/{package_id}")
async def delete_certification_package(package_id: str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Delete a certification package"""
    await get_current_user(credentials)
    await db.certification_packages.update_one(
        {"id": package_id},
        {"$set": {"is_active": False}}
    )
    return {"message": "Package deleted"}

@api_router.put("/templates/packages/{package_id}")
async def update_certification_package(package_id: str, package: CertificationPackage, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Update a certification package"""
    await get_current_user(credentials)
    update_data = {
        "name": package.name,
        "name_ar": package.name_ar,
        "description": package.description,
        "description_ar": package.description_ar,
        "standards": package.standards
    }
    await db.certification_packages.update_one(
        {"id": package_id},
        {"$set": update_data}
    )
    return {"message": "Package updated", "id": package_id}

@api_router.get("/templates/proposals")
async def get_proposal_templates(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get all proposal templates"""
    await get_current_user(credentials)
    templates = await db.proposal_templates.find({"is_active": True}, {"_id": 0}).to_list(100)
    return templates

@api_router.post("/templates/proposals")
async def create_proposal_template(template: ProposalTemplate, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Create a new proposal template"""
    await get_current_user(credentials)
    template_doc = template.model_dump()
    template_doc['created_at'] = template_doc['created_at'].isoformat()
    await db.proposal_templates.insert_one(template_doc)
    return {"message": "Template created", "id": template.id}

@api_router.delete("/templates/proposals/{template_id}")
async def delete_proposal_template(template_id: str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Delete a proposal template"""
    await get_current_user(credentials)
    await db.proposal_templates.update_one(
        {"id": template_id},
        {"$set": {"is_active": False}}
    )
    return {"message": "Template deleted"}

@api_router.put("/templates/proposals/{template_id}")
async def update_proposal_template(template_id: str, template: ProposalTemplate, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Update a proposal template"""
    await get_current_user(credentials)
    update_data = {
        "name": template.name,
        "name_ar": template.name_ar,
        "description": template.description,
        "default_fees": template.default_fees,
        "default_notes": template.default_notes,
        "default_validity_days": template.default_validity_days
    }
    await db.proposal_templates.update_one(
        {"id": template_id},
        {"$set": update_data}
    )
    return {"message": "Template updated", "id": template_id}

# ================= REPORTS ROUTES =================

@api_router.get("/reports/submissions")
async def get_submission_statistics(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get submission statistics"""
    await get_current_user(credentials)
    
    # Get counts by status
    total_forms = await db.application_forms.count_documents({})
    submitted_forms = await db.application_forms.count_documents({"status": {"$in": ["submitted", "under_review", "approved", "agreement_signed"]}})
    pending_forms = await db.application_forms.count_documents({"status": "pending"})
    
    # Get monthly statistics (last 6 months)
    from datetime import datetime, timedelta
    monthly_stats = []
    for i in range(5, -1, -1):
        start_date = datetime.now().replace(day=1) - timedelta(days=i*30)
        end_date = start_date + timedelta(days=30)
        
        count = await db.application_forms.count_documents({
            "created_at": {
                "$gte": start_date.isoformat(),
                "$lt": end_date.isoformat()
            }
        })
        monthly_stats.append({
            "month": start_date.strftime("%b %Y"),
            "count": count
        })
    
    # Conversion rate
    total_proposals = await db.proposals.count_documents({})
    accepted_proposals = await db.proposals.count_documents({"status": {"$in": ["accepted", "agreement_signed"]}})
    conversion_rate = (accepted_proposals / total_proposals * 100) if total_proposals > 0 else 0
    
    return {
        "total_forms": total_forms,
        "submitted_forms": submitted_forms,
        "pending_forms": pending_forms,
        "monthly_stats": monthly_stats,
        "total_proposals": total_proposals,
        "accepted_proposals": accepted_proposals,
        "conversion_rate": round(conversion_rate, 1)
    }

@api_router.get("/reports/revenue")
async def get_revenue_statistics(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get revenue statistics"""
    await get_current_user(credentials)
    
    # Get all proposals
    proposals = await db.proposals.find({}, {"_id": 0}).to_list(1000)
    
    total_quoted = sum(p.get('total_amount', 0) for p in proposals)
    accepted_revenue = sum(p.get('total_amount', 0) for p in proposals if p.get('status') in ['accepted', 'agreement_signed'])
    pending_revenue = sum(p.get('total_amount', 0) for p in proposals if p.get('status') == 'sent')
    rejected_revenue = sum(p.get('total_amount', 0) for p in proposals if p.get('status') == 'rejected')
    
    # Get agreements (contracts)
    agreements = await db.certification_agreements.count_documents({})
    
    # Revenue by month (last 6 months)
    from datetime import datetime, timedelta
    monthly_revenue = []
    for i in range(5, -1, -1):
        start_date = datetime.now().replace(day=1) - timedelta(days=i*30)
        end_date = start_date + timedelta(days=30)
        
        month_proposals = [p for p in proposals if p.get('status') in ['accepted', 'agreement_signed']]
        # Filter by date if issued_date exists
        month_total = sum(
            p.get('total_amount', 0) for p in month_proposals
            if p.get('issued_date') and start_date.isoformat() <= p.get('issued_date', '') < end_date.isoformat()
        )
        
        monthly_revenue.append({
            "month": start_date.strftime("%b %Y"),
            "amount": month_total
        })
    
    return {
        "total_quoted": total_quoted,
        "accepted_revenue": accepted_revenue,
        "pending_revenue": pending_revenue,
        "rejected_revenue": rejected_revenue,
        "total_contracts": agreements,
        "monthly_revenue": monthly_revenue,
        "currency": "SAR"
    }

@api_router.get("/reports/filtered")
async def get_filtered_report(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    status: Optional[str] = None,
    standard: Optional[str] = None
):
    """Get filtered report data with comprehensive filters"""
    await get_current_user(credentials)
    
    # Build query for forms
    forms_query = {}
    if status and status != "all":
        forms_query["status"] = status
    
    # Date filtering
    if start_date or end_date:
        forms_query["created_at"] = {}
        if start_date:
            forms_query["created_at"]["$gte"] = start_date
        if end_date:
            forms_query["created_at"]["$lte"] = end_date
    
    # Get filtered forms
    forms = await db.application_forms.find(forms_query, {"_id": 0}).to_list(1000)
    
    # Filter by standard if specified
    if standard and standard != "all":
        forms = [f for f in forms if f.get('company_data') and f.get('company_data', {}).get('certificationSchemes') and standard in f.get('company_data', {}).get('certificationSchemes', [])]
    
    # Build query for proposals
    proposals_query = {}
    if status and status != "all":
        proposals_query["status"] = status
    if start_date or end_date:
        proposals_query["created_at"] = {}
        if start_date:
            proposals_query["created_at"]["$gte"] = start_date
        if end_date:
            proposals_query["created_at"]["$lte"] = end_date
    
    # Get filtered proposals
    proposals = await db.proposals.find(proposals_query, {"_id": 0}).to_list(1000)
    
    # Filter proposals by standard if specified
    if standard and standard != "all":
        proposals = [p for p in proposals if standard in p.get('standards', [])]
    
    # Calculate statistics
    total_forms = len(forms)
    submitted_forms = len([f for f in forms if f.get('status') in ['submitted', 'under_review', 'approved', 'agreement_signed']])
    pending_forms = len([f for f in forms if f.get('status') == 'pending'])
    
    total_proposals = len(proposals)
    accepted_proposals = len([p for p in proposals if p.get('status') in ['accepted', 'agreement_signed']])
    pending_proposals = len([p for p in proposals if p.get('status') == 'pending'])
    rejected_proposals = len([p for p in proposals if p.get('status') == 'rejected'])
    modification_requested = len([p for p in proposals if p.get('status') == 'modification_requested'])
    
    # Revenue calculations
    total_quoted = sum(p.get('total_amount', 0) for p in proposals)
    accepted_revenue = sum(p.get('total_amount', 0) for p in proposals if p.get('status') in ['accepted', 'agreement_signed'])
    pending_revenue = sum(p.get('total_amount', 0) for p in proposals if p.get('status') == 'pending')
    rejected_revenue = sum(p.get('total_amount', 0) for p in proposals if p.get('status') == 'rejected')
    
    conversion_rate = (accepted_proposals / total_proposals * 100) if total_proposals > 0 else 0
    
    # Standards breakdown
    standards_count = {}
    for p in proposals:
        for std in p.get('standards', []):
            standards_count[std] = standards_count.get(std, 0) + 1
    
    # Status breakdown for forms
    form_status_breakdown = {}
    for f in forms:
        status_val = f.get('status', 'unknown')
        form_status_breakdown[status_val] = form_status_breakdown.get(status_val, 0) + 1
    
    # Status breakdown for proposals
    proposal_status_breakdown = {}
    for p in proposals:
        status_val = p.get('status', 'unknown')
        proposal_status_breakdown[status_val] = proposal_status_breakdown.get(status_val, 0) + 1
    
    return {
        "forms": {
            "total": total_forms,
            "submitted": submitted_forms,
            "pending": pending_forms,
            "status_breakdown": form_status_breakdown,
            "data": forms[:50]  # Return first 50 for detail view
        },
        "proposals": {
            "total": total_proposals,
            "accepted": accepted_proposals,
            "pending": pending_proposals,
            "rejected": rejected_proposals,
            "modification_requested": modification_requested,
            "status_breakdown": proposal_status_breakdown,
            "data": proposals[:50]
        },
        "revenue": {
            "total_quoted": total_quoted,
            "accepted": accepted_revenue,
            "pending": pending_revenue,
            "rejected": rejected_revenue,
            "currency": "SAR"
        },
        "conversion_rate": round(conversion_rate, 1),
        "standards_breakdown": standards_count,
        "filters_applied": {
            "start_date": start_date,
            "end_date": end_date,
            "status": status,
            "standard": standard
        }
    }

# ================= MODIFICATION REQUEST ROUTES =================

@api_router.post("/public/proposal/{access_token}/request_modification")
async def request_proposal_modification(access_token: str, request: ModificationRequest):
    """Client requests modification to a proposal (no login required)"""
    proposal = await db.proposals.find_one({"access_token": access_token})
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found or invalid link")
    
    if proposal['status'] != 'pending':
        raise HTTPException(status_code=400, detail="Proposal has already been responded to")
    
    if not request.comment:
        raise HTTPException(status_code=400, detail="Please provide a comment explaining the requested modifications")
    
    # Update proposal with modification request
    update_data = {
        "status": "modification_requested",
        "modification_comment": request.comment,
        "modification_requested_changes": request.requested_changes,
        "modification_requested_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.proposals.update_one(
        {"access_token": access_token},
        {"$set": update_data}
    )
    
    # Create notification for admin
    org_name = proposal.get('organization_name', 'Unknown')
    await create_notification(
        notification_type="modification_requested",
        title="طلب تعديل على العرض",
        message=f"طلبت {org_name} تعديلات على عرض السعر: {request.comment[:100]}",
        related_id=proposal['id'],
        related_type="proposal"
    )
    
    return {"message": "Modification request submitted successfully"}

# ================= CUSTOMER PORTAL / TRACKING ROUTES =================

@api_router.get("/public/track/{tracking_id}")
async def track_order(tracking_id: str):
    """Public endpoint to track order status by tracking ID (form ID or access token)"""
    
    # Try to find by form ID first
    form = await db.application_forms.find_one({"id": tracking_id}, {"_id": 0})
    
    # If not found, try by access token
    if not form:
        form = await db.application_forms.find_one({"access_token": tracking_id}, {"_id": 0})
    
    if not form:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Get proposal if exists
    proposal = await db.proposals.find_one({"application_form_id": form['id']}, {"_id": 0})
    
    # Get agreement if exists
    agreement = None
    if proposal:
        agreement = await db.certification_agreements.find_one({"proposal_id": proposal['id']}, {"_id": 0})
    
    # Determine current status
    current_status = form.get('status', 'pending')
    if agreement:
        current_status = 'agreement_signed'
    elif proposal and proposal.get('status') in ['accepted', 'agreement_signed']:
        current_status = 'accepted'
    elif proposal:
        current_status = 'under_review'
    
    # Build timeline dates
    timeline_dates = {
        'pending': form.get('created_at')
    }
    if form.get('submitted_at'):
        timeline_dates['submitted'] = form.get('submitted_at')
    if proposal:
        timeline_dates['under_review'] = proposal.get('created_at')
        if proposal.get('status') in ['accepted', 'agreement_signed']:
            timeline_dates['accepted'] = proposal.get('client_response_date')
    if agreement:
        timeline_dates['agreement_signed'] = agreement.get('created_at')
        if agreement.get('status') == 'contract_generated':
            timeline_dates['contract_generated'] = agreement.get('created_at')
    
    # Get standards from form data
    standards = []
    if form.get('company_data') and form['company_data'].get('certificationSchemes'):
        standards = form['company_data']['certificationSchemes']
    elif proposal:
        standards = proposal.get('standards', [])
    
    response = {
        "tracking_id": form['id'],
        "company_name": form.get('client_info', {}).get('company_name', 'Unknown'),
        "contact_email": form.get('client_info', {}).get('email', ''),
        "contact_phone": form.get('client_info', {}).get('phone', ''),
        "created_at": form.get('created_at'),
        "submitted_at": form.get('submitted_at'),
        "current_status": current_status,
        "standards": standards,
        "timeline_dates": timeline_dates,
        "contract_available": agreement is not None and agreement.get('status') == 'contract_generated'
    }
    
    # Add proposal info if available
    if proposal:
        response["proposal"] = {
            "id": proposal['id'],
            "access_token": proposal.get('access_token'),
            "total_amount": proposal.get('total_amount', 0),
            "status": proposal.get('status', 'pending')
        }
    
    return response

# ================= SITE MANAGEMENT ROUTES =================

class Site(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    contract_id: str  # Links to proposal/contract
    name: str
    address: str
    city: str = ""
    country: str = "Saudi Arabia"
    contact_name: str = ""
    contact_email: str = ""
    contact_phone: str = ""
    is_main_site: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class SiteCreate(BaseModel):
    contract_id: str
    name: str
    address: str
    city: str = ""
    country: str = "Saudi Arabia"
    contact_name: str = ""
    contact_email: str = ""
    contact_phone: str = ""
    is_main_site: bool = False

@api_router.get("/sites")
async def get_sites(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get all sites"""
    await get_current_user(credentials)
    sites = await db.sites.find({}, {"_id": 0}).to_list(1000)
    return sites

@api_router.post("/sites")
async def create_site(site_data: SiteCreate, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Create a new site"""
    await get_current_user(credentials)
    
    site = Site(
        contract_id=site_data.contract_id,
        name=site_data.name,
        address=site_data.address,
        city=site_data.city,
        country=site_data.country,
        contact_name=site_data.contact_name,
        contact_email=site_data.contact_email,
        contact_phone=site_data.contact_phone,
        is_main_site=site_data.is_main_site
    )
    
    site_doc = site.model_dump()
    site_doc['created_at'] = site_doc['created_at'].isoformat()
    
    await db.sites.insert_one(site_doc)
    return {"message": "Site created", "id": site.id}

@api_router.delete("/sites/{site_id}")
async def delete_site(site_id: str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Delete a site"""
    await get_current_user(credentials)
    await db.sites.delete_one({"id": site_id})
    return {"message": "Site deleted"}

# ================= AUDIT SCHEDULING ROUTES =================

class AuditSchedule(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    contract_id: str  # Links to proposal/contract
    site_id: str = ""  # Optional - for multi-site
    organization_name: str = ""
    site_name: str = ""
    audit_type: str = "initial"  # initial, surveillance, recertification
    scheduled_date: str
    scheduled_time: str = "09:00"
    duration_days: int = 1
    auditors: str = ""
    notes: str = ""
    status: str = "scheduled"  # scheduled, in_progress, completed, cancelled
    # Recurring event fields
    is_recurring: bool = False
    recurrence_type: str = ""  # weekly, monthly, quarterly, yearly
    recurrence_end_date: str = ""
    parent_audit_id: str = ""  # For generated recurring events
    # Google Calendar sync
    calendar_event_id: str = ""
    calendar_synced: bool = False
    # SMS notification
    sms_reminder_sent: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class AuditScheduleCreate(BaseModel):
    contract_id: str
    site_id: str = ""
    audit_type: str = "initial"
    scheduled_date: str
    scheduled_time: str = "09:00"
    duration_days: int = 1
    auditors: str = ""
    notes: str = ""
    # Recurring event fields
    is_recurring: bool = False
    recurrence_type: str = ""  # weekly, monthly, quarterly, yearly
    recurrence_end_date: str = ""

@api_router.get("/audit-schedules")
async def get_audit_schedules(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get all audit schedules"""
    await get_current_user(credentials)
    audits = await db.audit_schedules.find({}, {"_id": 0}).to_list(1000)
    
    # Enrich with organization names
    for audit in audits:
        if audit.get('contract_id'):
            proposal = await db.proposals.find_one({"id": audit['contract_id']}, {"_id": 0})
            if proposal:
                audit['organization_name'] = proposal.get('organization_name', '')
        if audit.get('site_id'):
            site = await db.sites.find_one({"id": audit['site_id']}, {"_id": 0})
            if site:
                audit['site_name'] = site.get('name', '')
    
    return audits

@api_router.post("/audit-schedules")
async def create_audit_schedule(audit_data: AuditScheduleCreate, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Create a new audit schedule with optional recurring events"""
    await get_current_user(credentials)
    
    # Get organization name from contract
    organization_name = ""
    contact_phone = ""
    contact_email = ""
    if audit_data.contract_id:
        proposal = await db.proposals.find_one({"id": audit_data.contract_id}, {"_id": 0})
        if proposal:
            organization_name = proposal.get('organization_name', '')
            contact_phone = proposal.get('contact_phone', '')
            contact_email = proposal.get('contact_email', '')
    
    # Get site name if provided
    site_name = ""
    if audit_data.site_id:
        site = await db.sites.find_one({"id": audit_data.site_id}, {"_id": 0})
        if site:
            site_name = site.get('name', '')
    
    # Create the main audit
    audit = AuditSchedule(
        contract_id=audit_data.contract_id,
        site_id=audit_data.site_id,
        organization_name=organization_name,
        site_name=site_name,
        audit_type=audit_data.audit_type,
        scheduled_date=audit_data.scheduled_date,
        scheduled_time=audit_data.scheduled_time,
        duration_days=audit_data.duration_days,
        auditors=audit_data.auditors,
        notes=audit_data.notes,
        is_recurring=audit_data.is_recurring,
        recurrence_type=audit_data.recurrence_type,
        recurrence_end_date=audit_data.recurrence_end_date
    )
    
    audit_doc = audit.model_dump()
    audit_doc['created_at'] = audit_doc['created_at'].isoformat()
    
    await db.audit_schedules.insert_one(audit_doc)
    
    created_audits = [audit.id]
    
    # Generate recurring events if enabled
    if audit_data.is_recurring and audit_data.recurrence_type and audit_data.recurrence_end_date:
        recurring_audits = generate_recurring_audits(
            parent_audit=audit,
            organization_name=organization_name,
            site_name=site_name,
            recurrence_type=audit_data.recurrence_type,
            end_date=audit_data.recurrence_end_date
        )
        
        for recurring_audit in recurring_audits:
            recurring_doc = recurring_audit.model_dump()
            recurring_doc['created_at'] = recurring_doc['created_at'].isoformat()
            await db.audit_schedules.insert_one(recurring_doc)
            created_audits.append(recurring_audit.id)
    
    return {"message": "Audit scheduled", "id": audit.id, "total_created": len(created_audits)}


def generate_recurring_audits(parent_audit: AuditSchedule, organization_name: str, site_name: str, recurrence_type: str, end_date: str) -> List[AuditSchedule]:
    """Generate recurring audit schedules based on recurrence type"""
    from dateutil.relativedelta import relativedelta
    
    recurring_audits = []
    
    try:
        start_date = datetime.strptime(parent_audit.scheduled_date, "%Y-%m-%d")
        end_date_dt = datetime.strptime(end_date, "%Y-%m-%d")
        
        # Calculate next dates based on recurrence type
        delta = None
        if recurrence_type == "weekly":
            delta = relativedelta(weeks=1)
        elif recurrence_type == "monthly":
            delta = relativedelta(months=1)
        elif recurrence_type == "quarterly":
            delta = relativedelta(months=3)
        elif recurrence_type == "yearly":
            delta = relativedelta(years=1)
        else:
            return recurring_audits
        
        current_date = start_date + delta
        
        while current_date <= end_date_dt:
            recurring_audit = AuditSchedule(
                contract_id=parent_audit.contract_id,
                site_id=parent_audit.site_id,
                organization_name=organization_name,
                site_name=site_name,
                audit_type=parent_audit.audit_type,
                scheduled_date=current_date.strftime("%Y-%m-%d"),
                scheduled_time=parent_audit.scheduled_time,
                duration_days=parent_audit.duration_days,
                auditors=parent_audit.auditors,
                notes=parent_audit.notes,
                is_recurring=True,
                recurrence_type=recurrence_type,
                parent_audit_id=parent_audit.id
            )
            recurring_audits.append(recurring_audit)
            current_date += delta
        
    except Exception as e:
        logging.error(f"Error generating recurring audits: {e}")
    
    return recurring_audits

@api_router.put("/audit-schedules/{audit_id}")
async def update_audit_schedule(audit_id: str, audit_data: AuditScheduleCreate, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Update an audit schedule"""
    await get_current_user(credentials)
    
    update_data = {
        "contract_id": audit_data.contract_id,
        "site_id": audit_data.site_id,
        "audit_type": audit_data.audit_type,
        "scheduled_date": audit_data.scheduled_date,
        "scheduled_time": audit_data.scheduled_time,
        "duration_days": audit_data.duration_days,
        "auditors": audit_data.auditors,
        "notes": audit_data.notes
    }
    
    await db.audit_schedules.update_one(
        {"id": audit_id},
        {"$set": update_data}
    )
    return {"message": "Audit updated", "id": audit_id}

@api_router.delete("/audit-schedules/{audit_id}")
async def delete_audit_schedule(audit_id: str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Delete an audit schedule"""
    await get_current_user(credentials)
    await db.audit_schedules.delete_one({"id": audit_id})
    return {"message": "Audit deleted"}

# ================= CUSTOMER CONTACT HISTORY ROUTES =================

class ContactRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    customer_id: str  # Links to form or proposal ID
    customer_name: str = ""
    contact_type: str = "call"  # call, email, meeting, other
    subject: str
    notes: str
    contact_date: str
    follow_up_date: str = ""
    follow_up_completed: bool = False
    created_by: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ContactRecordCreate(BaseModel):
    customer_id: str
    contact_type: str = "call"
    subject: str
    notes: str
    contact_date: str
    follow_up_date: str = ""

@api_router.get("/contacts")
async def get_contact_records(credentials: HTTPAuthorizationCredentials = Depends(security), customer_id: Optional[str] = None):
    """Get all contact records or filtered by customer"""
    await get_current_user(credentials)
    
    query = {}
    if customer_id:
        query["customer_id"] = customer_id
    
    contacts = await db.contact_records.find(query, {"_id": 0}).sort("contact_date", -1).to_list(1000)
    return contacts

@api_router.post("/contacts")
async def create_contact_record(contact_data: ContactRecordCreate, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Create a new contact record"""
    current_user = await get_current_user(credentials)
    
    # Get customer name from form or proposal
    customer_name = ""
    form = await db.application_forms.find_one({"id": contact_data.customer_id}, {"_id": 0})
    if form:
        customer_name = form.get('client_info', {}).get('company_name', '')
    else:
        proposal = await db.proposals.find_one({"id": contact_data.customer_id}, {"_id": 0})
        if proposal:
            customer_name = proposal.get('organization_name', '')
    
    contact = ContactRecord(
        customer_id=contact_data.customer_id,
        customer_name=customer_name,
        contact_type=contact_data.contact_type,
        subject=contact_data.subject,
        notes=contact_data.notes,
        contact_date=contact_data.contact_date,
        follow_up_date=contact_data.follow_up_date,
        created_by=current_user.get('user_id', '')
    )
    
    contact_doc = contact.model_dump()
    contact_doc['created_at'] = contact_doc['created_at'].isoformat()
    
    await db.contact_records.insert_one(contact_doc)
    return {"message": "Contact record created", "id": contact.id}

@api_router.put("/contacts/{contact_id}/follow-up")
async def mark_follow_up_completed(contact_id: str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Mark a follow-up as completed"""
    await get_current_user(credentials)
    
    await db.contact_records.update_one(
        {"id": contact_id},
        {"$set": {"follow_up_completed": True}}
    )
    return {"message": "Follow-up marked as completed"}

@api_router.delete("/contacts/{contact_id}")
async def delete_contact_record(contact_id: str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Delete a contact record"""
    await get_current_user(credentials)
    await db.contact_records.delete_one({"id": contact_id})
    return {"message": "Contact record deleted"}

# ================= REPORT EXPORT ROUTES =================

@api_router.get("/reports/export")
async def export_report(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    format: str = "excel",  # excel or pdf
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    status: Optional[str] = None,
    standard: Optional[str] = None
):
    """Export reports to Excel or PDF"""
    await get_current_user(credentials)
    
    # Build query for forms
    forms_query = {}
    if status and status != "all":
        forms_query["status"] = status
    if start_date or end_date:
        forms_query["created_at"] = {}
        if start_date:
            forms_query["created_at"]["$gte"] = start_date
        if end_date:
            forms_query["created_at"]["$lte"] = end_date
    
    # Get data
    forms = await db.application_forms.find(forms_query, {"_id": 0}).to_list(1000)
    proposals = await db.proposals.find({}, {"_id": 0}).to_list(1000)
    
    # Filter by standard if specified
    if standard and standard != "all":
        forms = [f for f in forms if f.get('company_data') and standard in f.get('company_data', {}).get('certificationSchemes', [])]
        proposals = [p for p in proposals if standard in p.get('standards', [])]
    
    if format == "excel":
        # Generate Excel file
        import io
        try:
            import openpyxl
            from openpyxl import Workbook
            from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
            
            wb = Workbook()
            
            # Forms Sheet
            ws_forms = wb.active
            ws_forms.title = "Application Forms"
            
            # Headers
            headers = ["Company Name", "Contact", "Email", "Status", "Standards", "Created Date", "Submitted Date"]
            header_fill = PatternFill(start_color="1B365D", end_color="1B365D", fill_type="solid")
            header_font = Font(color="FFFFFF", bold=True)
            
            for col, header in enumerate(headers, 1):
                cell = ws_forms.cell(row=1, column=col, value=header)
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = Alignment(horizontal="center")
            
            # Data rows
            for row, form in enumerate(forms, 2):
                client_info = form.get('client_info') or {}
                company_data = form.get('company_data') or {}
                
                ws_forms.cell(row=row, column=1, value=client_info.get('company_name', ''))
                ws_forms.cell(row=row, column=2, value=client_info.get('name', ''))
                ws_forms.cell(row=row, column=3, value=client_info.get('email', ''))
                ws_forms.cell(row=row, column=4, value=form.get('status', ''))
                ws_forms.cell(row=row, column=5, value=', '.join(company_data.get('certificationSchemes', [])))
                ws_forms.cell(row=row, column=6, value=form.get('created_at', '')[:10] if form.get('created_at') else '')
                ws_forms.cell(row=row, column=7, value=form.get('submitted_at', '')[:10] if form.get('submitted_at') else '')
            
            # Adjust column widths
            for col in ws_forms.columns:
                max_length = 0
                column = col[0].column_letter
                for cell in col:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                ws_forms.column_dimensions[column].width = min(max_length + 2, 50)
            
            # Proposals Sheet
            ws_proposals = wb.create_sheet("Proposals")
            
            headers = ["Organization", "Contact", "Standards", "Status", "Total Amount", "Issued Date"]
            for col, header in enumerate(headers, 1):
                cell = ws_proposals.cell(row=1, column=col, value=header)
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = Alignment(horizontal="center")
            
            for row, proposal in enumerate(proposals, 2):
                ws_proposals.cell(row=row, column=1, value=proposal.get('organization_name', ''))
                ws_proposals.cell(row=row, column=2, value=proposal.get('contact_person', ''))
                ws_proposals.cell(row=row, column=3, value=', '.join(proposal.get('standards', [])))
                ws_proposals.cell(row=row, column=4, value=proposal.get('status', ''))
                ws_proposals.cell(row=row, column=5, value=proposal.get('total_amount', 0))
                ws_proposals.cell(row=row, column=6, value=proposal.get('issued_date', '')[:10] if proposal.get('issued_date') else '')
            
            # Adjust column widths for proposals
            for col in ws_proposals.columns:
                max_length = 0
                column = col[0].column_letter
                for cell in col:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                ws_proposals.column_dimensions[column].width = min(max_length + 2, 50)
            
            # Save to bytes
            output = io.BytesIO()
            wb.save(output)
            output.seek(0)
            
            return Response(
                content=output.getvalue(),
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={
                    "Content-Disposition": f"attachment; filename=report_{datetime.now().strftime('%Y%m%d')}.xlsx"
                }
            )
        except ImportError:
            raise HTTPException(status_code=500, detail="Excel export library not installed")
    
    elif format == "pdf":
        # Generate PDF report
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.units import inch
        import io
        
        output = io.BytesIO()
        doc = SimpleDocTemplate(output, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=18, textColor=colors.HexColor('#1B365D'))
        
        elements = []
        
        # Title
        elements.append(Paragraph("Reports Summary", title_style))
        elements.append(Spacer(1, 20))
        
        # Summary stats
        total_forms = len(forms)
        submitted_forms = len([f for f in forms if f.get('status') in ['submitted', 'under_review', 'approved', 'agreement_signed']])
        total_proposals = len(proposals)
        accepted_proposals = len([p for p in proposals if p.get('status') in ['accepted', 'agreement_signed']])
        total_revenue = sum(p.get('total_amount', 0) for p in proposals if p.get('status') in ['accepted', 'agreement_signed'])
        
        summary_data = [
            ["Metric", "Value"],
            ["Total Forms", str(total_forms)],
            ["Submitted Forms", str(submitted_forms)],
            ["Total Proposals", str(total_proposals)],
            ["Accepted Proposals", str(accepted_proposals)],
            ["Total Revenue (SAR)", f"{total_revenue:,.0f}"]
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1B365D')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(summary_table)
        elements.append(Spacer(1, 30))
        
        # Forms table
        elements.append(Paragraph("Application Forms", styles['Heading2']))
        elements.append(Spacer(1, 10))
        
        forms_data = [["Company", "Status", "Standards"]]
        for form in forms[:20]:  # Limit to 20 rows
            client_info = form.get('client_info') or {}
            company_data = form.get('company_data') or {}
            forms_data.append([
                (client_info.get('company_name', '') or '')[:30],
                form.get('status', ''),
                ', '.join(company_data.get('certificationSchemes', []))[:30]
            ])
        
        forms_table = Table(forms_data, colWidths=[2.5*inch, 1.5*inch, 2.5*inch])
        forms_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1B365D')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))
        
        elements.append(forms_table)
        
        doc.build(elements)
        output.seek(0)
        
        return Response(
            content=output.getvalue(),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=report_{datetime.now().strftime('%Y%m%d')}.pdf"
            }
        )
    
    raise HTTPException(status_code=400, detail="Invalid format. Use 'excel' or 'pdf'")

# ================= DOCUMENT UPLOAD ROUTES =================

class Document(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    related_id: str  # Links to form, proposal, or contract ID
    related_type: str  # form, proposal, contract
    name: str
    file_type: str
    file_size: int = 0
    file_data: str  # Base64 encoded file data
    uploaded_by: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class DocumentCreate(BaseModel):
    related_id: str
    related_type: str
    name: str
    file_type: str
    file_data: str  # Base64 encoded

@api_router.get("/documents")
async def get_documents(credentials: HTTPAuthorizationCredentials = Depends(security), related_id: Optional[str] = None):
    """Get documents, optionally filtered by related ID"""
    await get_current_user(credentials)
    
    query = {}
    if related_id:
        query["related_id"] = related_id
    
    # Return documents without file_data for listing (to reduce payload size)
    documents = await db.documents.find(query, {"_id": 0, "file_data": 0}).sort("created_at", -1).to_list(100)
    return documents

@api_router.post("/documents")
async def upload_document(doc_data: DocumentCreate, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Upload a new document"""
    current_user = await get_current_user(credentials)
    
    # Calculate file size from base64
    import base64
    try:
        file_bytes = base64.b64decode(doc_data.file_data.split(',')[-1] if ',' in doc_data.file_data else doc_data.file_data)
        file_size = len(file_bytes)
    except:
        file_size = 0
    
    document = Document(
        related_id=doc_data.related_id,
        related_type=doc_data.related_type,
        name=doc_data.name,
        file_type=doc_data.file_type,
        file_size=file_size,
        file_data=doc_data.file_data,
        uploaded_by=current_user.get('user_id', '')
    )
    
    doc_doc = document.model_dump()
    doc_doc['created_at'] = doc_doc['created_at'].isoformat()
    
    await db.documents.insert_one(doc_doc)
    return {"message": "Document uploaded", "id": document.id}

@api_router.get("/documents/{document_id}")
async def get_document(document_id: str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get a specific document including file data"""
    await get_current_user(credentials)
    
    document = await db.documents.find_one({"id": document_id}, {"_id": 0})
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return document

@api_router.delete("/documents/{document_id}")
async def delete_document(document_id: str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Delete a document"""
    await get_current_user(credentials)
    await db.documents.delete_one({"id": document_id})
    return {"message": "Document deleted"}

# ================= SEED DATA =================

async def seed_default_templates():
    """Seed default certification packages and proposal templates"""
    
    # Check if already seeded
    existing_packages = await db.certification_packages.count_documents({})
    if existing_packages > 0:
        return
    
    # Default certification packages
    packages = [
        CertificationPackage(
            name="QMS Basic",
            name_ar="نظام إدارة الجودة الأساسي",
            description="ISO 9001 Quality Management System certification",
            description_ar="شهادة نظام إدارة الجودة ISO 9001",
            standards=["ISO9001"]
        ),
        CertificationPackage(
            name="EMS Basic",
            name_ar="نظام الإدارة البيئية الأساسي",
            description="ISO 14001 Environmental Management System certification",
            description_ar="شهادة نظام الإدارة البيئية ISO 14001",
            standards=["ISO14001"]
        ),
        CertificationPackage(
            name="OHS Basic",
            name_ar="نظام السلامة والصحة المهنية الأساسي",
            description="ISO 45001 Occupational Health & Safety certification",
            description_ar="شهادة نظام السلامة والصحة المهنية ISO 45001",
            standards=["ISO45001"]
        ),
        CertificationPackage(
            name="Integrated Management System",
            name_ar="نظام الإدارة المتكامل",
            description="Combined QMS, EMS, and OHS certification (ISO 9001, 14001, 45001)",
            description_ar="شهادة نظام الإدارة المتكامل (ISO 9001, 14001, 45001)",
            standards=["ISO9001", "ISO14001", "ISO45001"]
        ),
        CertificationPackage(
            name="Food Safety",
            name_ar="سلامة الغذاء",
            description="ISO 22000 Food Safety Management System certification",
            description_ar="شهادة نظام إدارة سلامة الغذاء ISO 22000",
            standards=["ISO22000"]
        ),
        CertificationPackage(
            name="Information Security",
            name_ar="أمن المعلومات",
            description="ISO 27001 Information Security Management certification",
            description_ar="شهادة نظام إدارة أمن المعلومات ISO 27001",
            standards=["ISO27001"]
        )
    ]
    
    for pkg in packages:
        pkg_doc = pkg.model_dump()
        pkg_doc['created_at'] = pkg_doc['created_at'].isoformat()
        await db.certification_packages.insert_one(pkg_doc)
    
    # Default proposal templates
    templates = [
        ProposalTemplate(
            name="Standard Pricing",
            name_ar="الأسعار القياسية",
            description="Standard pricing for most certifications",
            default_fees={
                "initial_certification": 15000,
                "surveillance_1": 8000,
                "surveillance_2": 8000,
                "recertification": 12000
            },
            default_notes="العرض شامل كافة التكاليف عدا السفر والإقامة",
            default_validity_days=30
        ),
        ProposalTemplate(
            name="Small Business",
            name_ar="المنشآت الصغيرة",
            description="Discounted pricing for small businesses (< 50 employees)",
            default_fees={
                "initial_certification": 10000,
                "surveillance_1": 5000,
                "surveillance_2": 5000,
                "recertification": 8000
            },
            default_notes="عرض خاص للمنشآت الصغيرة - شامل كافة التكاليف عدا السفر والإقامة",
            default_validity_days=30
        ),
        ProposalTemplate(
            name="Enterprise",
            name_ar="المؤسسات الكبيرة",
            description="Pricing for large enterprises (500+ employees)",
            default_fees={
                "initial_certification": 25000,
                "surveillance_1": 12000,
                "surveillance_2": 12000,
                "recertification": 20000
            },
            default_notes="عرض للمؤسسات الكبيرة - يشمل تدقيق متعدد المواقع",
            default_validity_days=45
        )
    ]
    
    for tmpl in templates:
        tmpl_doc = tmpl.model_dump()
        tmpl_doc['created_at'] = tmpl_doc['created_at'].isoformat()
        await db.proposal_templates.insert_one(tmpl_doc)
    
    logger.info("Default templates seeded successfully")

# ================= GOOGLE CALENDAR INTEGRATION =================

# Google Calendar OAuth Configuration
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', '')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', '')
GOOGLE_REDIRECT_URI = os.environ.get('GOOGLE_REDIRECT_URI', '')

# Check if Google Calendar is configured
GOOGLE_CALENDAR_ENABLED = bool(GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET)

@api_router.get("/calendar/status")
async def get_calendar_status(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Check if Google Calendar integration is enabled and connected"""
    current_user = await get_current_user(credentials)
    
    # Check if configured
    if not GOOGLE_CALENDAR_ENABLED:
        return {
            "enabled": False,
            "configured": False,
            "connected": False,
            "message": "Google Calendar integration not configured. Please add GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET to environment."
        }
    
    # Check if user has connected their calendar
    user = await db.users.find_one({"email": current_user['email']}, {"_id": 0})
    has_tokens = bool(user and user.get('google_tokens'))
    
    return {
        "enabled": True,
        "configured": True,
        "connected": has_tokens,
        "message": "Connected to Google Calendar" if has_tokens else "Click 'Connect Calendar' to enable sync"
    }

@api_router.get("/calendar/auth/url")
async def get_calendar_auth_url(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get Google Calendar OAuth authorization URL"""
    await get_current_user(credentials)
    
    if not GOOGLE_CALENDAR_ENABLED:
        raise HTTPException(status_code=400, detail="Google Calendar integration not configured")
    
    # Build authorization URL
    scopes = "https://www.googleapis.com/auth/calendar"
    auth_url = (
        f"https://accounts.google.com/o/oauth2/auth?"
        f"client_id={GOOGLE_CLIENT_ID}&"
        f"redirect_uri={GOOGLE_REDIRECT_URI}&"
        f"response_type=code&"
        f"scope={scopes}&"
        f"access_type=offline&"
        f"prompt=consent"
    )
    
    return {"authorization_url": auth_url}

@api_router.get("/oauth/calendar/callback")
async def calendar_oauth_callback(code: str):
    """Handle Google Calendar OAuth callback"""
    import requests
    
    if not GOOGLE_CALENDAR_ENABLED:
        raise HTTPException(status_code=400, detail="Google Calendar integration not configured")
    
    # Exchange code for tokens
    token_response = requests.post('https://oauth2.googleapis.com/token', data={
        'code': code,
        'client_id': GOOGLE_CLIENT_ID,
        'client_secret': GOOGLE_CLIENT_SECRET,
        'redirect_uri': GOOGLE_REDIRECT_URI,
        'grant_type': 'authorization_code'
    })
    
    if token_response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to exchange code for tokens")
    
    tokens = token_response.json()
    
    # Get user email
    user_response = requests.get(
        'https://www.googleapis.com/oauth2/v2/userinfo',
        headers={'Authorization': f'Bearer {tokens["access_token"]}'}
    )
    
    if user_response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to get user info")
    
    user_info = user_response.json()
    
    # Save tokens to user record
    await db.users.update_one(
        {"email": user_info['email']},
        {"$set": {"google_tokens": tokens}},
        upsert=False
    )
    
    # Redirect back to dashboard
    frontend_url = os.environ.get('FRONTEND_URL', '')
    return RedirectResponse(url=f"{frontend_url}/audit-scheduling?calendar_connected=true")

@api_router.post("/calendar/sync-audit")
async def sync_audit_to_calendar(
    audit_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Sync an audit schedule to Google Calendar"""
    import requests
    
    current_user = await get_current_user(credentials)
    
    if not GOOGLE_CALENDAR_ENABLED:
        raise HTTPException(status_code=400, detail="Google Calendar integration not configured")
    
    # Get user tokens
    user = await db.users.find_one({"email": current_user['email']}, {"_id": 0})
    if not user or not user.get('google_tokens'):
        raise HTTPException(status_code=400, detail="Google Calendar not connected")
    
    tokens = user['google_tokens']
    
    # Get audit schedule
    audit = await db.audit_schedules.find_one({"id": audit_id}, {"_id": 0})
    if not audit:
        raise HTTPException(status_code=404, detail="Audit schedule not found")
    
    # Get contract details for more info
    contract = await db.proposals.find_one({"id": audit.get('contract_id')}, {"_id": 0})
    org_name = contract.get('organization_name', 'Client') if contract else 'Client'
    
    # Create calendar event
    event = {
        'summary': f"Audit: {org_name}",
        'description': f"Audit Type: {audit.get('audit_type', 'N/A')}\nAuditor: {audit.get('auditor', 'N/A')}\nSite: {audit.get('site', 'N/A')}\nNotes: {audit.get('notes', '')}",
        'start': {
            'date': audit.get('start_date'),
            'timeZone': 'Asia/Riyadh'
        },
        'end': {
            'date': audit.get('end_date'),
            'timeZone': 'Asia/Riyadh'
        },
        'location': audit.get('site', ''),
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'email', 'minutes': 24 * 60},
                {'method': 'popup', 'minutes': 60}
            ]
        }
    }
    
    # Create event in Google Calendar
    response = requests.post(
        'https://www.googleapis.com/calendar/v3/calendars/primary/events',
        headers={
            'Authorization': f'Bearer {tokens["access_token"]}',
            'Content-Type': 'application/json'
        },
        json=event
    )
    
    if response.status_code == 401:
        # Token expired, need to re-authenticate
        raise HTTPException(status_code=401, detail="Google Calendar token expired. Please reconnect.")
    
    if response.status_code not in [200, 201]:
        raise HTTPException(status_code=500, detail=f"Failed to create calendar event: {response.text}")
    
    event_data = response.json()
    
    # Save calendar event ID to audit
    await db.audit_schedules.update_one(
        {"id": audit_id},
        {"$set": {"calendar_event_id": event_data.get('id')}}
    )
    
    return {"message": "Audit synced to Google Calendar", "event_id": event_data.get('id')}

@api_router.delete("/calendar/disconnect")
async def disconnect_calendar(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Disconnect Google Calendar"""
    current_user = await get_current_user(credentials)
    
    await db.users.update_one(
        {"email": current_user['email']},
        {"$unset": {"google_tokens": ""}}
    )
    
    return {"message": "Google Calendar disconnected"}


# ================= SMS NOTIFICATIONS (TWILIO) =================

# Twilio configuration
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID', '')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN', '')
TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER', '')
TWILIO_ENABLED = bool(TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN and TWILIO_PHONE_NUMBER)

class SMSRequest(BaseModel):
    to_phone: str
    message: str
    customer_name: str = ""

class SMSNotificationSettings(BaseModel):
    enabled: bool = True
    reminder_days_before: int = 1  # Days before audit to send reminder
    send_on_proposal_accepted: bool = True
    send_on_agreement_signed: bool = True
    send_on_audit_scheduled: bool = True

@api_router.get("/sms/status")
async def get_sms_status(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get SMS integration status"""
    await get_current_user(credentials)
    
    return {
        "enabled": TWILIO_ENABLED,
        "configured": TWILIO_ENABLED,
        "simulation_mode": not TWILIO_ENABLED,
        "message": "SMS notifications active" if TWILIO_ENABLED else "SMS running in simulation mode (no Twilio credentials)"
    }

@api_router.post("/sms/send")
async def send_sms(sms_data: SMSRequest, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Send SMS notification"""
    await get_current_user(credentials)
    
    if TWILIO_ENABLED:
        # Real Twilio integration
        try:
            from twilio.rest import Client
            client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
            
            message = client.messages.create(
                body=sms_data.message,
                from_=TWILIO_PHONE_NUMBER,
                to=sms_data.to_phone
            )
            
            # Log the SMS
            sms_log = {
                "id": str(uuid.uuid4()),
                "to_phone": sms_data.to_phone,
                "customer_name": sms_data.customer_name,
                "message": sms_data.message,
                "status": "sent",
                "twilio_sid": message.sid,
                "sent_at": datetime.now(timezone.utc).isoformat()
            }
            await db.sms_logs.insert_one(sms_log)
            
            return {"success": True, "message": "SMS sent successfully", "sid": message.sid}
            
        except Exception as e:
            logging.error(f"Twilio SMS error: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to send SMS: {str(e)}")
    else:
        # Simulation mode
        sms_log = {
            "id": str(uuid.uuid4()),
            "to_phone": sms_data.to_phone,
            "customer_name": sms_data.customer_name,
            "message": sms_data.message,
            "status": "simulated",
            "sent_at": datetime.now(timezone.utc).isoformat()
        }
        await db.sms_logs.insert_one(sms_log)
        
        logging.info(f"[SIMULATED SMS] To: {sms_data.to_phone}, Message: {sms_data.message}")
        
        return {
            "success": True, 
            "message": "SMS simulated (Twilio not configured)",
            "simulated": True,
            "log_id": sms_log["id"]
        }

@api_router.get("/sms/logs")
async def get_sms_logs(credentials: HTTPAuthorizationCredentials = Depends(security), limit: int = 50):
    """Get SMS notification logs"""
    await get_current_user(credentials)
    
    logs = await db.sms_logs.find({}, {"_id": 0}).sort("sent_at", -1).limit(limit).to_list(limit)
    return logs

@api_router.post("/sms/send-audit-reminder")
async def send_audit_reminder(audit_id: str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Send SMS reminder for an upcoming audit"""
    await get_current_user(credentials)
    
    # Get audit details
    audit = await db.audit_schedules.find_one({"id": audit_id}, {"_id": 0})
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")
    
    # Get contract/proposal for contact info
    proposal = await db.proposals.find_one({"id": audit.get('contract_id')}, {"_id": 0})
    if not proposal:
        raise HTTPException(status_code=404, detail="Contract not found")
    
    contact_phone = proposal.get('contact_phone', '')
    if not contact_phone:
        raise HTTPException(status_code=400, detail="No phone number available for this client")
    
    # Create reminder message (bilingual)
    message_ar = f"تذكير: موعد التدقيق المجدول لشركة {audit.get('organization_name', '')} في {audit.get('scheduled_date')} الساعة {audit.get('scheduled_time', '09:00')}. بيان للتحقق والمطابقة"
    message_en = f"Reminder: Audit scheduled for {audit.get('organization_name', '')} on {audit.get('scheduled_date')} at {audit.get('scheduled_time', '09:00')}. BAYAN Auditing"
    
    full_message = f"{message_ar}\n\n{message_en}"
    
    # Send the SMS
    sms_request = SMSRequest(
        to_phone=contact_phone,
        message=full_message,
        customer_name=proposal.get('contact_name', '')
    )
    
    result = await send_sms(sms_request, credentials)
    
    # Mark audit as reminder sent
    await db.audit_schedules.update_one(
        {"id": audit_id},
        {"$set": {"sms_reminder_sent": True, "sms_reminder_sent_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    return result


# ================= MULTILINGUAL PDF GENERATION =================

@api_router.get("/proposals/{proposal_id}/bilingual_pdf")
async def generate_bilingual_proposal_pdf(proposal_id: str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Generate bilingual (Arabic + English) PDF for a proposal/quotation"""
    await get_current_user(credentials)
    
    proposal = await db.proposals.find_one({"id": proposal_id}, {"_id": 0})
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    
    # Generate the PDF
    pdf_path = await generate_bilingual_proposal_pdf_file(proposal)
    
    return FileResponse(
        pdf_path,
        media_type='application/pdf',
        filename=f'proposal_{proposal_id}_bilingual.pdf'
    )

async def generate_bilingual_proposal_pdf_file(proposal: dict) -> str:
    """Generate a bilingual proposal PDF with company stamp (no signature - not yet approved)"""
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib.units import cm
    from reportlab.lib import colors
    import arabic_reshaper
    from bidi.algorithm import get_display
    import base64
    import io
    
    # Register Arabic fonts
    font_path = ROOT_DIR / "fonts" / "Amiri-Regular.ttf"
    font_bold_path = ROOT_DIR / "fonts" / "Amiri-Bold.ttf"
    arabic_font_available = False
    
    if font_path.exists():
        try:
            pdfmetrics.registerFont(TTFont('Amiri', str(font_path)))
            arabic_font_available = True
            if font_bold_path.exists():
                pdfmetrics.registerFont(TTFont('Amiri-Bold', str(font_bold_path)))
        except Exception as e:
            print(f"Error registering Arabic font: {e}")
            arabic_font_available = False
    
    # Logo path
    logo_path = ROOT_DIR / "assets" / "bayan-logo.png"
    
    pdf_path = CONTRACTS_DIR / f"proposal_{proposal['id']}_bilingual.pdf"
    c = canvas.Canvas(str(pdf_path), pagesize=A4)
    width, height = A4
    
    def draw_arabic_text(text, x, y, font_size=11, bold=False):
        """Draw Arabic text with proper reshaping"""
        if arabic_font_available:
            try:
                reshaped = arabic_reshaper.reshape(str(text))
                bidi_text = get_display(reshaped)
                font_name = 'Amiri-Bold' if bold and font_bold_path.exists() else 'Amiri'
                c.setFont(font_name, font_size)
                c.drawRightString(x, y, bidi_text)
                return
            except Exception as e:
                print(f"Error drawing Arabic text: {e}")
        c.setFont('Helvetica-Bold' if bold else 'Helvetica', font_size)
        c.drawRightString(x, y, str(text))
    
    def draw_section_header(en_text, ar_text, y_pos):
        """Draw bilingual section header"""
        c.setFillColor(colors.HexColor('#1e3a5f'))
        c.setFont('Helvetica-Bold', 12)
        c.drawString(50, y_pos, en_text)
        draw_arabic_text(ar_text, width - 50, y_pos, 12, bold=True)
        c.setStrokeColor(colors.HexColor('#1e3a5f'))
        c.setLineWidth(1)
        c.line(50, y_pos - 5, width - 50, y_pos - 5)
        return y_pos - 25
    
    def draw_field(label_en, label_ar, value, y_pos):
        """Draw bilingual field with value on both sides"""
        value_str = str(value) if value else 'N/A'
        c.setFillColor(colors.black)
        # English side (left)
        c.setFont('Helvetica-Bold', 10)
        c.drawString(50, y_pos, f"{label_en}:")
        c.setFont('Helvetica', 10)
        c.drawString(180, y_pos, value_str)
        # Arabic side (right) - label and value
        draw_arabic_text(f"{label_ar}:", width - 50, y_pos, 10, bold=True)
        draw_arabic_text(value_str, width - 130, y_pos, 10)
        return y_pos - 18
    
    # Header with logo
    c.setFillColor(colors.HexColor('#1e3a5f'))
    c.rect(0, height - 100, width, 100, fill=True, stroke=False)
    
    # Draw white background for logo then logo
    if logo_path.exists():
        try:
            # White rounded rectangle background for logo
            c.setFillColor(colors.white)
            c.roundRect(25, height - 95, 80, 80, 5, fill=True, stroke=False)
            # Draw logo
            c.drawImage(str(logo_path), 30, height - 90, width=70, height=70, preserveAspectRatio=True, mask='auto')
        except:
            pass
    
    # Title
    c.setFillColor(colors.white)
    c.setFont('Helvetica-Bold', 22)
    c.drawCentredString(width/2, height - 45, "PRICE QUOTATION")
    
    # Arabic title
    if arabic_font_available:
        try:
            reshaped = arabic_reshaper.reshape("عرض السعر")
            bidi_text = get_display(reshaped)
            c.setFont('Amiri-Bold' if font_bold_path.exists() else 'Amiri', 18)
            c.drawCentredString(width/2, height - 70, bidi_text)
        except:
            pass
    
    # Reference info
    c.setFont('Helvetica', 9)
    c.drawRightString(width - 30, height - 30, f"Ref: {proposal.get('id', 'N/A')[:8].upper()}")
    c.drawRightString(width - 30, height - 45, f"Date: {proposal.get('issued_date', 'N/A')[:10] if proposal.get('issued_date') else 'N/A'}")
    
    y = height - 130
    
    # Section 1: Client Information
    y = draw_section_header("1. CLIENT INFORMATION", "١. معلومات العميل", y)
    y = draw_field("Organization", "المنظمة", proposal.get('organization_name', 'N/A'), y)
    y = draw_field("Contact Person", "جهة الاتصال", proposal.get('contact_person', proposal.get('contact_name', 'N/A')), y)
    y = draw_field("Email", "البريد الإلكتروني", proposal.get('contact_email', 'N/A'), y)
    y = draw_field("Phone", "الهاتف", proposal.get('contact_phone', 'N/A'), y)
    y -= 10
    
    # Section 2: Certification Scope
    y = draw_section_header("2. CERTIFICATION SCOPE", "٢. نطاق الاعتماد", y)
    standards = proposal.get('standards', [])
    standards_text = ', '.join(standards) if standards else 'N/A'
    y = draw_field("Standards", "المعايير", standards_text, y)
    y = draw_field("Scope", "النطاق", proposal.get('scope', 'N/A'), y)
    y -= 10
    
    # Section 3: Audit Duration
    y = draw_section_header("3. AUDIT DURATION (Days)", "٣. مدة التدقيق (أيام)", y)
    audit_duration = proposal.get('audit_duration', {})
    y = draw_field("Stage 1", "المرحلة الأولى", audit_duration.get('stage_1', 'N/A'), y)
    y = draw_field("Stage 2", "المرحلة الثانية", audit_duration.get('stage_2', 'N/A'), y)
    y = draw_field("Surveillance 1", "تدقيق المراقبة 1", audit_duration.get('surveillance_1', 'N/A'), y)
    y = draw_field("Surveillance 2", "تدقيق المراقبة 2", audit_duration.get('surveillance_2', 'N/A'), y)
    y = draw_field("Recertification", "إعادة الاعتماد", audit_duration.get('recertification', 'N/A'), y)
    y -= 10
    
    # Section 4: Service Fees
    y = draw_section_header("4. SERVICE FEES", "٤. رسوم الخدمة", y)
    service_fees = proposal.get('service_fees', {})
    currency = service_fees.get('currency', 'SAR')
    
    def format_fee(amount):
        return f"{currency} {amount:,.2f}" if amount else f"{currency} 0.00"
    
    y = draw_field("Initial Certification", "الاعتماد الأولي", format_fee(service_fees.get('initial_certification', 0)), y)
    y = draw_field("Surveillance 1 Fee", "رسوم المراقبة 1", format_fee(service_fees.get('surveillance_1', 0)), y)
    y = draw_field("Surveillance 2 Fee", "رسوم المراقبة 2", format_fee(service_fees.get('surveillance_2', 0)), y)
    y = draw_field("Recertification Fee", "رسوم إعادة الاعتماد", format_fee(service_fees.get('recertification', 0)), y)
    y -= 5
    
    # Total Amount (highlighted)
    c.setFillColor(colors.HexColor('#e8f4e8'))
    c.rect(50, y - 5, width - 100, 25, fill=True, stroke=False)
    c.setStrokeColor(colors.HexColor('#1e3a5f'))
    c.rect(50, y - 5, width - 100, 25, fill=False, stroke=True)
    c.setFillColor(colors.HexColor('#1e3a5f'))
    c.setFont('Helvetica-Bold', 12)
    c.drawString(60, y + 3, "TOTAL AMOUNT:")
    c.drawString(200, y + 3, format_fee(proposal.get('total_amount', 0)))
    draw_arabic_text(":المبلغ الإجمالي", width - 60, y + 3, 12, bold=True)
    y -= 35
    
    # Section 5: Validity
    y = draw_section_header("5. VALIDITY", "٥. الصلاحية", y)
    y = draw_field("Valid Until", "صالح حتى", proposal.get('valid_until', 'N/A'), y)
    y = draw_field("Validity Days", "أيام الصلاحية", f"{proposal.get('validity_days', 30)} days", y)
    y -= 10
    
    # Section 6: Status
    status_ar = {
        'draft': 'مسودة',
        'sent': 'تم الإرسال للعميل',
        'pending': 'قيد الانتظار',
        'accepted': 'مقبول',
        'rejected': 'مرفوض',
        'agreement_signed': 'تم الإرسال للعميل',
        'modification_requested': 'طلب تعديل'
    }
    status_en = {
        'draft': 'Draft',
        'sent': 'Sent to Client',
        'pending': 'Pending',
        'accepted': 'Accepted',
        'rejected': 'Rejected',
        'agreement_signed': 'Sent to Client',
        'modification_requested': 'Modification Requested'
    }
    status = proposal.get('status', 'pending')
    y = draw_section_header("6. STATUS", "٦. الحالة", y)
    c.setFillColor(colors.black)
    c.setFont('Helvetica', 11)
    c.drawString(50, y, f"Current Status: {status_en.get(status, status.replace('_', ' ').title())}")
    draw_arabic_text(f"الحالة الحالية: {status_ar.get(status, status)}", width - 50, y, 11)
    y -= 30
    
    # Company Seal Section - Use official seal image
    seal_path = ROOT_DIR / "assets" / "company-seal.png"
    c.setFillColor(colors.HexColor('#1e3a5f'))
    c.setFont('Helvetica-Bold', 10)
    # Draw bilingual header for seal section
    c.drawString(width/2 - 80, y, "Company Seal /")
    draw_arabic_text("ختم الشركة", width/2 + 80, y, 10, bold=True)
    y -= 15
    
    # Draw the official company seal image - positioned higher to avoid footer overlap
    if seal_path.exists():
        try:
            c.drawImage(str(seal_path), width/2 - 45, y - 95, width=90, height=90, preserveAspectRatio=True, mask='auto')
        except Exception as e:
            print(f"Error drawing seal: {e}")
    
    # Footer with proper Arabic text rendering
    c.setFillColor(colors.HexColor('#1e3a5f'))
    c.rect(0, 0, width, 45, fill=True, stroke=False)
    c.setFillColor(colors.white)
    c.setFont('Helvetica', 9)
    # English part
    c.drawString(width/2 - 180, 28, "BAYAN Auditing & Conformity |")
    # Arabic part with proper reshaping
    if arabic_font_available:
        try:
            footer_ar = arabic_reshaper.reshape("بيان للتدقيق والمطابقة")
            c.setFont('Amiri', 10)
            c.drawString(width/2 + 10, 26, get_display(footer_ar))
        except:
            pass
    c.setFont('Helvetica', 9)
    c.drawCentredString(width/2, 10, "3879 Al Khadar Street, Riyadh, 12282, Saudi Arabia")
    
    c.save()
    return str(pdf_path)


@api_router.get("/forms/{form_id}/bilingual_pdf")
async def generate_bilingual_form_pdf(form_id: str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Generate bilingual (Arabic + English) PDF for a submitted form"""
    await get_current_user(credentials)
    
    form = await db.application_forms.find_one({"id": form_id}, {"_id": 0})
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    
    # Generate the PDF
    pdf_path = await generate_bilingual_form_pdf_file(form)
    
    return FileResponse(
        pdf_path,
        media_type='application/pdf',
        filename=f'form_submission_{form_id}_bilingual.pdf'
    )

async def generate_bilingual_form_pdf_file(form: dict) -> str:
    """Generate a comprehensive bilingual form submission PDF with all client data"""
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    import arabic_reshaper
    from bidi.algorithm import get_display
    
    # Register Arabic font
    font_path = ROOT_DIR / "fonts" / "Amiri-Regular.ttf"
    font_bold_path = ROOT_DIR / "fonts" / "Amiri-Bold.ttf"
    arabic_font_available = False
    if font_path.exists():
        try:
            pdfmetrics.registerFont(TTFont('Amiri', str(font_path)))
            arabic_font_available = True
            if font_bold_path.exists():
                pdfmetrics.registerFont(TTFont('Amiri-Bold', str(font_bold_path)))
        except:
            pass
    
    # Logo path
    logo_path = ROOT_DIR / "assets" / "bayan-logo.png"
    
    pdf_path = CONTRACTS_DIR / f"form_{form['id']}_bilingual.pdf"
    c = canvas.Canvas(str(pdf_path), pagesize=A4)
    width, height = A4
    
    def draw_arabic_text(text, x, y, font_size=11, bold=False):
        if arabic_font_available:
            try:
                reshaped = arabic_reshaper.reshape(str(text))
                bidi_text = get_display(reshaped)
                font_name = 'Amiri-Bold' if bold and font_bold_path.exists() else 'Amiri'
                c.setFont(font_name, font_size)
                c.drawRightString(x, y, bidi_text)
                return
            except:
                pass
        c.setFont('Helvetica-Bold' if bold else 'Helvetica', font_size)
        c.drawRightString(x, y, str(text))
    
    def draw_section_header(en_text, ar_text, y_pos):
        """Draw bilingual section header"""
        c.setFillColor(colors.HexColor('#1e3a5f'))
        c.setFont('Helvetica-Bold', 12)
        c.drawString(50, y_pos, en_text)
        draw_arabic_text(ar_text, width - 50, y_pos, 12, bold=True)
        c.setStrokeColor(colors.HexColor('#1e3a5f'))
        c.setLineWidth(1)
        c.line(50, y_pos - 5, width - 50, y_pos - 5)
        return y_pos - 25
    
    def draw_field(label_en, label_ar, value, y_pos, value_ar=None):
        """Draw bilingual field with value on both sides"""
        value_str = str(value) if value else 'N/A'
        c.setFillColor(colors.black)
        # English side (left)
        c.setFont('Helvetica-Bold', 10)
        c.drawString(50, y_pos, f"{label_en}:")
        c.setFont('Helvetica', 10)
        c.drawString(170, y_pos, value_str)
        # Arabic side (right) - label and value
        draw_arabic_text(f"{label_ar}:", width - 50, y_pos, 10, bold=True)
        # Use Arabic value if provided, otherwise use the same value
        display_value = str(value_ar) if value_ar else value_str
        draw_arabic_text(display_value, width - 130, y_pos, 10)
        return y_pos - 18
    
    # ========== PAGE 1 ==========
    # Header with logo
    c.setFillColor(colors.HexColor('#1e3a5f'))
    c.rect(0, height - 100, width, 100, fill=True, stroke=False)
    
    # Draw white background for logo then logo
    if logo_path.exists():
        try:
            # White rounded rectangle background for logo
            c.setFillColor(colors.white)
            c.roundRect(25, height - 95, 80, 80, 5, fill=True, stroke=False)
            # Draw logo
            c.drawImage(str(logo_path), 30, height - 90, width=70, height=70, preserveAspectRatio=True, mask='auto')
        except:
            pass
    
    # Title
    c.setFillColor(colors.white)
    c.setFont('Helvetica-Bold', 20)
    c.drawCentredString(width/2, height - 45, "APPLICATION FORM")
    if arabic_font_available:
        try:
            reshaped = arabic_reshaper.reshape("طلب الاعتماد")
            bidi_text = get_display(reshaped)
            c.setFont('Amiri-Bold' if font_bold_path.exists() else 'Amiri', 18)
            c.drawCentredString(width/2, height - 70, bidi_text)
        except:
            pass
    
    # Submission info
    c.setFont('Helvetica', 9)
    c.drawRightString(width - 30, height - 30, f"Ref: {form.get('id', 'N/A')[:8].upper()}")
    c.drawRightString(width - 30, height - 45, f"Date: {form.get('submitted_at', form.get('created_at', 'N/A'))[:10] if form.get('submitted_at') or form.get('created_at') else 'N/A'}")
    
    y = height - 130
    company_data = form.get('company_data', {})
    client_info = form.get('client_info', {})
    
    # Section 1: Company Information
    y = draw_section_header("1. COMPANY INFORMATION", "١. معلومات الشركة", y)
    y = draw_field("Company Name", "اسم الشركة", company_data.get('companyName', client_info.get('company_name', 'N/A')), y)
    y = draw_field("Legal Entity", "الكيان القانوني", company_data.get('legalEntity', 'N/A'), y)
    y = draw_field("Commercial Reg. No", "رقم السجل التجاري", company_data.get('commercialRegNo', 'N/A'), y)
    y = draw_field("Address", "العنوان", company_data.get('address', 'N/A'), y)
    y = draw_field("City", "المدينة", company_data.get('city', 'N/A'), y)
    y = draw_field("Country", "الدولة", company_data.get('country', 'N/A'), y)
    y = draw_field("Postal Code", "الرمز البريدي", company_data.get('postalCode', 'N/A'), y)
    y -= 10
    
    # Section 2: Contact Information
    y = draw_section_header("2. CONTACT INFORMATION", "٢. معلومات الاتصال", y)
    y = draw_field("Contact Person", "جهة الاتصال", company_data.get('contactPerson', client_info.get('name', 'N/A')), y)
    y = draw_field("Position", "المنصب", company_data.get('contactPosition', 'N/A'), y)
    y = draw_field("Email", "البريد الإلكتروني", company_data.get('email', client_info.get('email', 'N/A')), y)
    y = draw_field("Phone", "الهاتف", company_data.get('phone', client_info.get('phone', 'N/A')), y)
    y = draw_field("Fax", "الفاكس", company_data.get('fax', 'N/A'), y)
    y = draw_field("Website", "الموقع الإلكتروني", company_data.get('website', 'N/A'), y)
    y -= 10
    
    # Section 3: Organization Details
    y = draw_section_header("3. ORGANIZATION DETAILS", "٣. تفاصيل المنظمة", y)
    y = draw_field("Total Employees", "إجمالي الموظفين", company_data.get('totalEmployees', 'N/A'), y)
    y = draw_field("Shift Workers", "عمال الورديات", company_data.get('shiftWorkers', 'N/A'), y)
    y = draw_field("Industry Sector", "قطاع الصناعة", company_data.get('industrySector', 'N/A'), y)
    y = draw_field("Business Activity", "النشاط التجاري", company_data.get('businessActivity', 'N/A'), y)
    y = draw_field("Scope of Services", "نطاق الخدمات", company_data.get('scopeOfServices', 'N/A'), y)
    y -= 10
    
    # Section 4: Certification Standards
    y = draw_section_header("4. CERTIFICATION STANDARDS", "٤. معايير الاعتماد", y)
    standards = company_data.get('certificationSchemes', [])
    standards_text = ', '.join(standards) if standards else 'N/A'
    y = draw_field("Selected Standards", "المعايير المختارة", standards_text, y)
    if company_data.get('otherStandard'):
        y = draw_field("Other Standard", "معيار آخر", company_data.get('otherStandard'), y)
    y -= 10
    
    # Section 5: Sites Information
    y = draw_section_header("5. SITES INFORMATION", "٥. معلومات المواقع", y)
    sites = company_data.get('sites', [])
    if sites:
        for i, site in enumerate(sites, 1):
            if isinstance(site, dict):
                site_text = f"{site.get('name', '')} - {site.get('address', '')}"
            else:
                site_text = str(site)
            y = draw_field(f"Site {i}", f"الموقع {i}", site_text, y)
    else:
        y = draw_field("Sites", "المواقع", "Main site only", y)
    
    # Footer for page 1
    c.setFillColor(colors.HexColor('#1e3a5f'))
    c.rect(0, 0, width, 45, fill=True, stroke=False)
    c.setFillColor(colors.white)
    c.setFont('Helvetica', 9)
    # English part
    c.drawString(width/2 - 180, 28, "BAYAN Auditing & Conformity |")
    # Arabic part with proper reshaping
    if arabic_font_available:
        try:
            footer_ar = arabic_reshaper.reshape("بيان للتدقيق والمطابقة")
            c.setFont('Amiri', 10)
            c.drawString(width/2 + 10, 26, get_display(footer_ar))
        except:
            pass
    c.setFont('Helvetica', 9)
    c.drawCentredString(width/2, 10, "Page 1")
    
    # ========== PAGE 2 (if more data) ==========
    audit_info = company_data.get('auditInfo', {})
    if audit_info or company_data.get('previousCertification') or company_data.get('consultantUsed'):
        c.showPage()
        
        # Header for page 2
        c.setFillColor(colors.HexColor('#1e3a5f'))
        c.rect(0, height - 60, width, 60, fill=True, stroke=False)
        if logo_path.exists():
            try:
                # White background for logo
                c.setFillColor(colors.white)
                c.roundRect(25, height - 58, 55, 55, 4, fill=True, stroke=False)
                c.drawImage(str(logo_path), 28, height - 55, width=50, height=50, preserveAspectRatio=True, mask='auto')
            except:
                pass
        c.setFillColor(colors.white)
        c.setFont('Helvetica-Bold', 14)
        c.drawCentredString(width/2, height - 35, "APPLICATION FORM (Continued)")
        
        y = height - 90
        
        # Section 6: Audit Information
        y = draw_section_header("6. AUDIT INFORMATION", "٦. معلومات التدقيق", y)
        y = draw_field("Preferred Audit Date", "تاريخ التدقيق المفضل", audit_info.get('preferredDate', 'N/A'), y)
        y = draw_field("Audit Language", "لغة التدقيق", audit_info.get('language', 'N/A'), y)
        y -= 10
        
        # Section 7: Previous Certification
        if company_data.get('previousCertification'):
            y = draw_section_header("7. PREVIOUS CERTIFICATION", "٧. الشهادات السابقة", y)
            y = draw_field("Previous Cert. Body", "جهة الاعتماد السابقة", company_data.get('previousCertBody', 'N/A'), y)
            y = draw_field("Previous Cert. Expiry", "انتهاء الشهادة السابقة", company_data.get('previousCertExpiry', 'N/A'), y)
            y -= 10
        
        # Section 8: Consultant
        if company_data.get('consultantUsed'):
            y = draw_section_header("8. CONSULTANT INFORMATION", "٨. معلومات المستشار", y)
            y = draw_field("Consultant Name", "اسم المستشار", company_data.get('consultantName', 'N/A'), y)
            y = draw_field("Consultant Contact", "اتصال المستشار", company_data.get('consultantContact', 'N/A'), y)
        
        # Footer for page 2
        c.setFillColor(colors.HexColor('#1e3a5f'))
        c.rect(0, 0, width, 45, fill=True, stroke=False)
        c.setFillColor(colors.white)
        c.setFont('Helvetica', 9)
        # English part
        c.drawString(width/2 - 180, 28, "BAYAN Auditing & Conformity |")
        # Arabic part with proper reshaping
        if arabic_font_available:
            try:
                footer_ar = arabic_reshaper.reshape("بيان للتدقيق والمطابقة")
                c.setFont('Amiri', 10)
                c.drawString(width/2 + 10, 26, get_display(footer_ar))
            except:
                pass
        c.setFont('Helvetica', 9)
        c.drawCentredString(width/2, 10, "Page 2")
    
    c.save()
    return str(pdf_path)


@api_router.get("/reports/bilingual_pdf")
async def generate_bilingual_report_pdf(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    report_type: str = "summary",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """Generate bilingual (Arabic + English) PDF report"""
    await get_current_user(credentials)
    
    # Get data based on report type
    if report_type == "summary":
        # Get all relevant data
        forms = await db.application_forms.find({}, {"_id": 0}).to_list(1000)
        proposals = await db.proposals.find({}, {"_id": 0}).to_list(1000)
        agreements = await db.certification_agreements.find({}, {"_id": 0}).to_list(1000)
        
        report_data = {
            "total_forms": len(forms),
            "total_proposals": len(proposals),
            "total_agreements": len(agreements),
            "accepted_proposals": len([p for p in proposals if p.get('status') in ['accepted', 'agreement_signed']]),
            "total_revenue": sum(p.get('total_amount', 0) for p in proposals if p.get('status') in ['accepted', 'agreement_signed'])
        }
    else:
        report_data = {}
    
    # Generate the PDF
    pdf_path = await generate_bilingual_report_pdf_file(report_data, report_type)
    
    return FileResponse(
        pdf_path,
        media_type='application/pdf',
        filename=f'report_{report_type}_bilingual.pdf'
    )

async def generate_bilingual_report_pdf_file(data: dict, report_type: str) -> str:
    """Generate a bilingual report PDF"""
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib import colors
    import arabic_reshaper
    from bidi.algorithm import get_display
    
    # Register Arabic font
    font_path = ROOT_DIR / "fonts" / "Amiri-Regular.ttf"
    if font_path.exists():
        try:
            pdfmetrics.registerFont(TTFont('Amiri', str(font_path)))
        except:
            pass
    
    pdf_path = CONTRACTS_DIR / f"report_{report_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    c = canvas.Canvas(str(pdf_path), pagesize=A4)
    width, height = A4
    
    def draw_arabic_text(text, x, y, font_size=12):
        try:
            reshaped = arabic_reshaper.reshape(str(text))
            bidi_text = get_display(reshaped)
            c.setFont('Amiri', font_size)
            c.drawRightString(x, y, bidi_text)
        except:
            c.setFont('Helvetica', font_size)
            c.drawRightString(x, y, str(text))
    
    # Header
    c.setFillColor(colors.HexColor('#1e3a5f'))
    c.rect(0, height - 100, width, 100, fill=True, stroke=False)
    
    c.setFillColor(colors.white)
    c.setFont('Helvetica-Bold', 24)
    c.drawCentredString(width/2, height - 50, "SUMMARY REPORT / تقرير ملخص")
    
    y = height - 140
    
    # English Section
    c.setFillColor(colors.black)
    c.setFont('Helvetica-Bold', 14)
    c.drawString(50, y, "ENGLISH")
    y -= 30
    
    c.setFont('Helvetica', 11)
    c.drawString(50, y, f"Total Applications: {data.get('total_forms', 0)}")
    y -= 20
    c.drawString(50, y, f"Total Proposals: {data.get('total_proposals', 0)}")
    y -= 20
    c.drawString(50, y, f"Accepted Proposals: {data.get('accepted_proposals', 0)}")
    y -= 20
    c.drawString(50, y, f"Total Contracts: {data.get('total_agreements', 0)}")
    y -= 20
    c.drawString(50, y, f"Total Revenue: SAR {data.get('total_revenue', 0):,.2f}")
    y -= 20
    c.drawString(50, y, f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    y -= 50
    
    # Divider
    c.setStrokeColor(colors.HexColor('#1e3a5f'))
    c.setLineWidth(2)
    c.line(50, y, width - 50, y)
    y -= 30
    
    # Arabic Section
    c.setFont('Helvetica-Bold', 14)
    draw_arabic_text("العربية", width - 50, y, 14)
    y -= 30
    
    draw_arabic_text(f"إجمالي الطلبات: {data.get('total_forms', 0)}", width - 50, y)
    y -= 20
    draw_arabic_text(f"إجمالي العروض: {data.get('total_proposals', 0)}", width - 50, y)
    y -= 20
    draw_arabic_text(f"العروض المقبولة: {data.get('accepted_proposals', 0)}", width - 50, y)
    y -= 20
    draw_arabic_text(f"إجمالي العقود: {data.get('total_agreements', 0)}", width - 50, y)
    y -= 20
    draw_arabic_text(f"إجمالي الإيرادات: {data.get('total_revenue', 0):,.2f} ريال", width - 50, y)
    
    # Footer
    c.setFillColor(colors.HexColor('#1e3a5f'))
    c.rect(0, 0, width, 50, fill=True, stroke=False)
    c.setFillColor(colors.white)
    c.setFont('Helvetica', 10)
    c.drawCentredString(width/2, 20, "BAYAN Auditing & Conformity | بيان للتحقق والمطابقة")
    
    c.save()
    return str(pdf_path)

@app.on_event("startup")
async def startup_event():
    """Run startup tasks"""
    await seed_default_templates()

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
