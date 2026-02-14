from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.responses import FileResponse, Response
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

# Import PDF generator
from pdf_generator import generate_contract_pdf

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
    frontend_url = os.environ.get('FRONTEND_URL', 'https://agreement-hub-14.preview.emergentagent.com')
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
    
    frontend_url = os.environ.get('FRONTEND_URL', 'https://agreement-hub-14.preview.emergentagent.com')
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
    """Mark all notifications as read"""
    await get_current_user(credentials)
    
    await db.notifications.update_many(
        {"is_read": False},
        {"$set": {"is_read": True}}
    )
    
    return {"message": "All notifications marked as read"}

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
