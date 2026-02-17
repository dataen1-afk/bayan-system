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
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch, cm
from reportlab.lib.colors import HexColor
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import qrcode
from io import BytesIO
import base64

# Import audit calculator
from audit_calculator import calculate_total_audit_time

# Import PDF generators
from pdf_generator import generate_contract_pdf
from bilingual_pdf_generator import generate_bilingual_contract_pdf
from certificate_generator import generate_certificate_pdf, get_qr_code_base64
from grant_agreement_generator import generate_grant_agreement_pdf

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
    # First Party (Bayan) authorized signatory
    issuer_name: str = "Abdullah Al-Rashid"  # Default authorized signatory
    issuer_designation: str = "General Manager"  # Default job title
    issuer_signature: str = ""  # Base64 encoded signature image
    issuer_stamp: str = ""  # Base64 encoded stamp image

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
    # First Party (Bayan) Signatures
    issuer_name: str = ""
    issuer_designation: str = ""
    issuer_signature: str = ""  # Base64 encoded signature image
    issuer_stamp: str = ""  # Base64 encoded stamp image
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

# ================= INVOICE & PAYMENT MODELS =================

class InvoiceItem(BaseModel):
    description: str
    description_ar: str = ""
    quantity: int = 1
    unit_price: float
    total: float = 0

class Invoice(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    invoice_number: str = ""  # Auto-generated: INV-2026-001
    contract_id: str  # Links to proposal/agreement
    organization_name: str
    organization_address: str = ""
    contact_email: str = ""
    contact_phone: str = ""
    # Invoice details
    items: List[InvoiceItem] = []
    subtotal: float = 0
    tax_rate: float = 15  # VAT percentage (Saudi Arabia: 15%)
    tax_amount: float = 0
    total_amount: float = 0
    currency: str = "SAR"
    # Payment terms
    issue_date: str = ""  # When invoice was created
    due_date: str = ""  # Payment due date
    payment_terms: str = "net_30"  # net_15, net_30, net_60, due_on_receipt
    # Status tracking
    status: str = "draft"  # draft, sent, viewed, paid, overdue, cancelled
    paid_amount: float = 0
    paid_date: Optional[str] = None
    payment_method: str = ""  # bank_transfer, stripe, cash, cheque
    payment_reference: str = ""  # Transaction ID or reference
    # Stripe integration
    stripe_invoice_id: str = ""
    stripe_payment_intent_id: str = ""
    stripe_payment_url: str = ""
    # Notes
    notes: str = ""
    internal_notes: str = ""
    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None

class InvoiceCreate(BaseModel):
    contract_id: str
    items: List[InvoiceItem] = []
    tax_rate: float = 15
    due_date: str = ""
    payment_terms: str = "net_30"
    notes: str = ""

class PaymentRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    invoice_id: str
    amount: float
    payment_date: str
    payment_method: str  # bank_transfer, stripe, cash, cheque
    reference: str = ""  # Transaction ID
    notes: str = ""
    recorded_by: str = ""  # Admin who recorded the payment
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# ================= CERTIFICATE MODELS =================

class Certificate(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    certificate_number: str = ""  # Auto-generated: CERT-YYYY-XXXX
    contract_id: str  # Reference to certification agreement
    audit_id: str = ""  # Reference to the final audit that granted certification
    # Organization details
    organization_name: str
    organization_name_ar: str = ""
    # Certification details
    standards: List[str] = []  # ISO 9001, ISO 14001, etc.
    scope: str = ""
    scope_ar: str = ""
    # Dates
    issue_date: str  # YYYY-MM-DD
    expiry_date: str  # YYYY-MM-DD (typically 3 years from issue)
    # Status
    status: str = "active"  # active, suspended, withdrawn, expired
    # QR Code
    verification_url: str = ""  # URL for QR code verification
    qr_code_data: str = ""  # Base64 encoded QR code image
    # Audit details
    lead_auditor: str = ""
    audit_team: List[str] = []
    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None

class CertificateCreate(BaseModel):
    contract_id: str
    audit_id: str = ""
    standards: List[str] = []
    scope: str = ""
    scope_ar: str = ""
    lead_auditor: str = ""
    audit_team: List[str] = []

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

# ================= AUDITOR MODELS =================

class AuditorAvailability(BaseModel):
    date: str  # YYYY-MM-DD
    is_available: bool = True
    reason: str = ""  # Reason if unavailable (vacation, sick, training, etc.)

class Auditor(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    employee_id: str = ""  # Employee ID/Badge number
    name: str
    name_ar: str = ""
    email: str
    phone: str = ""
    mobile: str = ""
    # Qualifications
    specializations: List[str] = []  # ISO 9001, ISO 14001, ISO 45001, etc.
    certification_level: str = "auditor"  # trainee, auditor, lead_auditor, technical_expert
    years_experience: int = 0
    certifications: List[str] = []  # List of certifications held
    # Status
    status: str = "active"  # active, inactive, on_leave
    # Availability
    availability: List[AuditorAvailability] = []
    default_available: bool = True  # Default availability if no specific date set
    max_audits_per_month: int = 10
    # Assignments tracking
    current_assignments: int = 0
    total_audits_completed: int = 0
    # Notes
    notes: str = ""
    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None

class AuditorCreate(BaseModel):
    employee_id: str = ""
    name: str
    name_ar: str = ""
    email: str
    phone: str = ""
    mobile: str = ""
    specializations: List[str] = []
    certification_level: str = "auditor"
    years_experience: int = 0
    certifications: List[str] = []
    max_audits_per_month: int = 10
    notes: str = ""

class AuditAssignment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    audit_id: str
    auditor_id: str
    role: str = "auditor"  # lead_auditor, auditor, technical_expert, observer
    status: str = "assigned"  # assigned, confirmed, completed, cancelled
    assigned_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    confirmed_at: Optional[datetime] = None
    notes: str = ""

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
    mobile: str = ""  # Optional mobile number for easier customer communication

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
@api_router.get("/defaults/signature")
async def get_default_signature():
    """Get the default Bayan signature as base64"""
    signature_path = ROOT_DIR / "assets" / "bayan-signature.png"
    if signature_path.exists():
        import base64
        with open(signature_path, "rb") as f:
            data = base64.b64encode(f.read()).decode('utf-8')
            return {"signature": f"data:image/png;base64,{data}"}
    return {"signature": ""}

@api_router.get("/defaults/stamp")
async def get_default_stamp():
    """Get the default Bayan stamp as base64"""
    stamp_path = ROOT_DIR / "assets" / "bayan-stamp.png"
    if stamp_path.exists():
        import base64
        with open(stamp_path, "rb") as f:
            data = base64.b64encode(f.read()).decode('utf-8')
            return {"stamp": f"data:image/png;base64,{data}"}
    return {"stamp": ""}

@api_router.get("/defaults/signatory")
async def get_default_signatory():
    """Get all default signatory details (name, title, signature, stamp)"""
    import base64
    result = {
        "issuer_name": "Abdullah Al-Rashid",
        "issuer_designation": "General Manager",
        "issuer_signature": "",
        "issuer_stamp": ""
    }
    
    signature_path = ROOT_DIR / "assets" / "bayan-signature.png"
    if signature_path.exists():
        with open(signature_path, "rb") as f:
            data = base64.b64encode(f.read()).decode('utf-8')
            result["issuer_signature"] = f"data:image/png;base64,{data}"
    
    stamp_path = ROOT_DIR / "assets" / "bayan-stamp.png"
    if stamp_path.exists():
        with open(stamp_path, "rb") as f:
            data = base64.b64encode(f.read()).decode('utf-8')
            result["issuer_stamp"] = f"data:image/png;base64,{data}"
    
    return result

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

# Certification Agreement routes
@api_router.get("/certification-agreements")
async def get_certification_agreements(status: str = None, current_user: dict = Depends(get_current_user)):
    """Get all certification agreements (signed contracts)"""
    query = {}
    if status and status != 'all':
        query['status'] = status
    
    agreements = await db.certification_agreements.find(query, {"_id": 0}).sort("created_at", -1).to_list(1000)
    return agreements

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
    frontend_url = os.environ.get('FRONTEND_URL', 'https://facility-grants.preview.emergentagent.com')
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
        issuer_name=proposal_data.issuer_name,  # Use value from form
        issuer_designation=proposal_data.issuer_designation,  # Use value from form
        issuer_signature=proposal_data.issuer_signature,  # First party signature
        issuer_stamp=proposal_data.issuer_stamp,  # First party stamp
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
    
    frontend_url = os.environ.get('FRONTEND_URL', 'https://facility-grants.preview.emergentagent.com')
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
        message=f"قامت {agreement_data.organization_name} بتوقيع اتفاقية المنح",
        related_id=agreement.id,
        related_type="agreement"
    )
    
    # ===== AUTO-SCHEDULE AUDITS =====
    # Automatically create audit schedules based on the proposal's audit duration
    try:
        audit_duration = proposal.get('audit_duration', {})
        organization_name = proposal.get('organization_name', '')
        sites = agreement_data.sites or ['Main Site']
        
        # Calculate audit dates starting from today
        from dateutil.relativedelta import relativedelta
        base_date = datetime.now(timezone.utc)
        
        # Define the audit schedule (audit type, days from contract signing, duration field)
        audit_schedule_plan = [
            ("stage_1", 30, "stage_1", "Initial Audit - Stage 1 | التدقيق الأولي - المرحلة 1"),
            ("stage_2", 60, "stage_2", "Initial Audit - Stage 2 | التدقيق الأولي - المرحلة 2"),
            ("surveillance_1", 365, "surveillance_1", "Surveillance Audit 1 | تدقيق المراقبة 1"),
            ("surveillance_2", 730, "surveillance_2", "Surveillance Audit 2 | تدقيق المراقبة 2"),
            ("recertification", 1065, "recertification", "Recertification Audit | تدقيق إعادة الاعتماد"),
        ]
        
        created_audits = []
        for audit_type, days_offset, duration_field, audit_notes in audit_schedule_plan:
            duration_days = audit_duration.get(duration_field, 1)
            if duration_days and duration_days > 0:
                scheduled_date = base_date + timedelta(days=days_offset)
                
                # Create audit for each site
                for site_idx, site in enumerate(sites):
                    site_name = site if isinstance(site, str) else site.get('name', f'Site {site_idx + 1}')
                    
                    audit_entry = {
                        "id": str(uuid.uuid4()),
                        "contract_id": proposal['id'],
                        "site_id": str(site_idx),
                        "organization_name": organization_name,
                        "site_name": site_name,
                        "audit_type": audit_type,
                        "scheduled_date": scheduled_date.strftime("%Y-%m-%d"),
                        "scheduled_time": "09:00",
                        "duration_days": int(duration_days),
                        "auditors": "",
                        "notes": audit_notes,
                        "status": "scheduled",
                        "is_recurring": False,
                        "recurrence_type": "",
                        "recurrence_end_date": "",
                        "parent_audit_id": "",
                        "calendar_event_id": "",
                        "calendar_synced": False,
                        "sms_reminder_sent": False,
                        "created_at": datetime.now(timezone.utc).isoformat(),
                        "auto_generated": True  # Mark as auto-generated
                    }
                    
                    await db.audit_schedules.insert_one(audit_entry)
                    created_audits.append(audit_entry['id'])
        
        print(f"Auto-scheduled {len(created_audits)} audits for contract {proposal['id']}")
        
        # Create notification for auto-scheduled audits
        if created_audits:
            await create_notification(
                notification_type="audits_scheduled",
                title="تم جدولة التدقيقات تلقائياً",
                message=f"تم إنشاء {len(created_audits)} جدولة تدقيق تلقائياً لـ {organization_name}",
                related_id=agreement.id,
                related_type="audit_schedule"
            )
    except Exception as e:
        print(f"Warning: Failed to auto-schedule audits: {e}")
        # Don't fail the agreement signing if audit scheduling fails
    
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
    """Generate PDF Grant Agreement for a signed agreement (Admin only)"""
    await get_current_user(credentials)
    
    # Get agreement
    agreement = await db.certification_agreements.find_one({"id": agreement_id}, {"_id": 0})
    if not agreement:
        raise HTTPException(status_code=404, detail="Agreement not found")
    
    # Get proposal for issuer details
    proposal = await db.proposals.find_one({"id": agreement['proposal_id']}, {"_id": 0})
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    
    # Prepare agreement data with correct field mappings
    agreement_data = {
        'organization_name': agreement.get('organization_name', ''),
        'organization_address': agreement.get('organization_address', ''),
        'selected_standards': agreement.get('selected_standards', []),
        'standards': agreement.get('selected_standards', []),  # alias
        'scope': agreement.get('scope_of_services', ''),
        'scope_of_services': agreement.get('scope_of_services', ''),  # alias
        'sites': agreement.get('sites', []),
        'signatory_name': agreement.get('signatory_name', ''),
        'signatory_position': agreement.get('signatory_position', ''),
        'signatory_date': agreement.get('signatory_date', ''),
        'signature_image': agreement.get('signature_image', ''),
        'stamp_image': agreement.get('stamp_image', ''),
        # BAC signatory from proposal
        'issuer_name': proposal.get('issuer_name', 'Abdullah Al-Rashid'),
        'issuer_designation': proposal.get('issuer_designation', 'General Manager'),
    }
    
    # Generate PDF
    try:
        pdf_path = CONTRACTS_DIR / f"grant_agreement_{agreement_id[:8]}.pdf"
        
        generate_grant_agreement_pdf(agreement_data, str(pdf_path))
        
        # Read PDF bytes
        with open(pdf_path, 'rb') as f:
            pdf_bytes = f.read()
        
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
                "Content-Disposition": f"attachment; filename=grant_agreement_{agreement_id[:8]}.pdf"
            }
        )
    except Exception as e:
        logging.error(f"Error generating Grant Agreement PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")

@api_router.get("/public/contracts/{access_token}/pdf")
async def get_public_contract_pdf(access_token: str):
    """Get PDF Grant Agreement for a signed agreement (Public - client access)
    Uses the official DOCX template for professional output"""
    # Get agreement by access token
    agreement = await db.certification_agreements.find_one({"proposal_access_token": access_token}, {"_id": 0})
    if not agreement:
        raise HTTPException(status_code=404, detail="Agreement not found")
    
    # Get proposal for issuer details
    proposal = await db.proposals.find_one({"id": agreement['proposal_id']}, {"_id": 0})
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    
    # Prepare agreement data with correct field mappings
    agreement_data = {
        'organization_name': agreement.get('organization_name', ''),
        'organization_address': agreement.get('organization_address', ''),
        'selected_standards': agreement.get('selected_standards', []),
        'standards': agreement.get('selected_standards', []),
        'scope': agreement.get('scope_of_services', ''),
        'scope_of_services': agreement.get('scope_of_services', ''),
        'sites': agreement.get('sites', []),
        'signatory_name': agreement.get('signatory_name', ''),
        'signatory_position': agreement.get('signatory_position', ''),
        'signatory_date': agreement.get('signatory_date', ''),
        'signature_image': agreement.get('signature_image', ''),
        'stamp_image': agreement.get('stamp_image', ''),
        'issuer_name': proposal.get('issuer_name', 'Abdullah Al-Rashid'),
        'issuer_designation': proposal.get('issuer_designation', 'General Manager'),
    }
    
    # Generate PDF using DOCX template
    try:
        pdf_path = CONTRACTS_DIR / f"grant_agreement_{agreement['id'][:8]}.pdf"
        generate_grant_agreement_pdf(agreement_data, str(pdf_path))
        
        # Read PDF bytes
        with open(pdf_path, 'rb') as f:
            pdf_bytes = f.read()
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=grant_agreement_{agreement['id'][:8]}.pdf"
            }
        )
    except Exception as e:
        logging.error(f"Error generating Grant Agreement PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")

# ================= BILINGUAL PDF CONTRACT GENERATION =================

@api_router.get("/contracts/{agreement_id}/pdf/bilingual")
async def generate_bilingual_contract_pdf_endpoint(agreement_id: str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Generate PDF Grant Agreement for a signed agreement (Admin only)
    Uses the official DOCX template for professional output"""
    await get_current_user(credentials)
    
    # Get agreement
    agreement = await db.certification_agreements.find_one({"id": agreement_id}, {"_id": 0})
    if not agreement:
        raise HTTPException(status_code=404, detail="Agreement not found")
    
    # Get proposal for issuer details
    proposal = await db.proposals.find_one({"id": agreement['proposal_id']}, {"_id": 0})
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    
    # Prepare agreement data
    agreement_data = {
        'organization_name': agreement.get('organization_name', ''),
        'organization_address': agreement.get('organization_address', ''),
        'selected_standards': agreement.get('selected_standards', []),
        'standards': agreement.get('selected_standards', []),
        'scope': agreement.get('scope_of_services', ''),
        'scope_of_services': agreement.get('scope_of_services', ''),
        'sites': agreement.get('sites', []),
        'signatory_name': agreement.get('signatory_name', ''),
        'signatory_position': agreement.get('signatory_position', ''),
        'signatory_date': agreement.get('signatory_date', ''),
        'signature_image': agreement.get('signature_image', ''),
        'stamp_image': agreement.get('stamp_image', ''),
        'issuer_name': proposal.get('issuer_name', 'Abdullah Al-Rashid'),
        'issuer_designation': proposal.get('issuer_designation', 'General Manager'),
    }
    
    # Generate PDF using DOCX template
    try:
        pdf_path = CONTRACTS_DIR / f"grant_agreement_{agreement_id[:8]}.pdf"
        generate_grant_agreement_pdf(agreement_data, str(pdf_path))
        
        # Read PDF bytes
        with open(pdf_path, 'rb') as f:
            pdf_bytes = f.read()
        
        # Update agreement status
        await db.certification_agreements.update_one(
            {"id": agreement_id},
            {"$set": {"status": "contract_generated"}}
        )
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=grant_agreement_{agreement_id[:8]}.pdf"
            }
        )
    except Exception as e:
        logging.error(f"Error generating Grant Agreement PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")

@api_router.get("/public/contracts/{access_token}/pdf/bilingual")
async def get_public_bilingual_contract_pdf(access_token: str):
    """Get PDF Grant Agreement for a signed agreement (Public - client access)
    Uses the official DOCX template for professional output"""
    # Get agreement by access token
    agreement = await db.certification_agreements.find_one({"proposal_access_token": access_token}, {"_id": 0})
    if not agreement:
        raise HTTPException(status_code=404, detail="Agreement not found")
    
    # Get proposal for issuer details
    proposal = await db.proposals.find_one({"id": agreement['proposal_id']}, {"_id": 0})
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    
    # Prepare agreement data
    agreement_data = {
        'organization_name': agreement.get('organization_name', ''),
        'organization_address': agreement.get('organization_address', ''),
        'selected_standards': agreement.get('selected_standards', []),
        'standards': agreement.get('selected_standards', []),
        'scope': agreement.get('scope_of_services', ''),
        'scope_of_services': agreement.get('scope_of_services', ''),
        'sites': agreement.get('sites', []),
        'signatory_name': agreement.get('signatory_name', ''),
        'signatory_position': agreement.get('signatory_position', ''),
        'signatory_date': agreement.get('signatory_date', ''),
        'signature_image': agreement.get('signature_image', ''),
        'stamp_image': agreement.get('stamp_image', ''),
        'issuer_name': proposal.get('issuer_name', 'Abdullah Al-Rashid'),
        'issuer_designation': proposal.get('issuer_designation', 'General Manager'),
    }
    
    # Generate PDF using DOCX template
    try:
        pdf_path = CONTRACTS_DIR / f"grant_agreement_{agreement['id'][:8]}.pdf"
        generate_grant_agreement_pdf(agreement_data, str(pdf_path))
        
        # Read PDF bytes
        with open(pdf_path, 'rb') as f:
            pdf_bytes = f.read()
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=grant_agreement_{agreement['id'][:8]}.pdf"
            }
        )
    except Exception as e:
        logging.error(f"Error generating Grant Agreement PDF: {str(e)}")
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
    """Public endpoint to track order status by tracking ID (form ID, access token, or proposal access token)"""
    
    # Try to find by form ID first
    form = await db.application_forms.find_one({"id": tracking_id}, {"_id": 0})
    
    # If not found, try by form access token
    if not form:
        form = await db.application_forms.find_one({"access_token": tracking_id}, {"_id": 0})
    
    # If still not found, try by proposal access token
    proposal_by_token = None
    if not form:
        proposal_by_token = await db.proposals.find_one({"access_token": tracking_id}, {"_id": 0})
        if proposal_by_token:
            # Get the form linked to this proposal
            form = await db.application_forms.find_one({"id": proposal_by_token['application_form_id']}, {"_id": 0})
    
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
        "contract_available": agreement is not None and agreement.get('signature_image')
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

# ================= AUDITOR MANAGEMENT ROUTES =================

@api_router.get("/auditors")
async def get_auditors(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    status: Optional[str] = None,
    specialization: Optional[str] = None
):
    """Get all auditors with optional filtering"""
    await get_current_user(credentials)
    
    query = {}
    if status:
        query["status"] = status
    if specialization:
        query["specializations"] = specialization
    
    auditors = await db.auditors.find(query, {"_id": 0}).sort("name", 1).to_list(100)
    
    # Calculate current assignments for each auditor
    for auditor in auditors:
        assignments = await db.audit_assignments.count_documents({
            "auditor_id": auditor['id'],
            "status": {"$in": ["assigned", "confirmed"]}
        })
        auditor['current_assignments'] = assignments
    
    return auditors

@api_router.get("/auditors/available")
async def get_available_auditors(
    date: str,
    specialization: Optional[str] = None,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get auditors available on a specific date"""
    await get_current_user(credentials)
    
    query = {"status": "active"}
    if specialization:
        query["specializations"] = specialization
    
    auditors = await db.auditors.find(query, {"_id": 0}).to_list(100)
    
    available_auditors = []
    for auditor in auditors:
        # Check if auditor has specific unavailability for this date
        is_available = auditor.get('default_available', True)
        for avail in auditor.get('availability', []):
            if avail.get('date') == date:
                is_available = avail.get('is_available', True)
                break
        
        if is_available:
            # Check if auditor is already assigned to an audit on this date
            existing = await db.audit_schedules.count_documents({
                "scheduled_date": date,
                "auditors": {"$regex": auditor['id']}
            })
            
            # Check max audits per month
            month_start = date[:7] + "-01"
            month_end = date[:7] + "-31"
            monthly_count = await db.audit_assignments.count_documents({
                "auditor_id": auditor['id'],
                "status": {"$in": ["assigned", "confirmed", "completed"]}
            })
            
            auditor['is_available'] = existing == 0 and monthly_count < auditor.get('max_audits_per_month', 10)
            auditor['existing_audits_today'] = existing
            auditor['monthly_audits'] = monthly_count
            available_auditors.append(auditor)
    
    return available_auditors

@api_router.post("/auditors")
async def create_auditor(auditor_data: AuditorCreate, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Create a new auditor"""
    await get_current_user(credentials)
    
    # Check if email already exists
    existing = await db.auditors.find_one({"email": auditor_data.email})
    if existing:
        raise HTTPException(status_code=400, detail="Auditor with this email already exists")
    
    auditor = Auditor(**auditor_data.model_dump())
    auditor_doc = auditor.model_dump()
    auditor_doc['created_at'] = auditor_doc['created_at'].isoformat()
    
    await db.auditors.insert_one(auditor_doc)
    
    return {"message": "Auditor created", "auditor_id": auditor.id}

@api_router.get("/auditors/{auditor_id}")
async def get_auditor(auditor_id: str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get auditor details"""
    await get_current_user(credentials)
    
    auditor = await db.auditors.find_one({"id": auditor_id}, {"_id": 0})
    if not auditor:
        raise HTTPException(status_code=404, detail="Auditor not found")
    
    # Get recent assignments
    assignments = await db.audit_assignments.find(
        {"auditor_id": auditor_id},
        {"_id": 0}
    ).sort("assigned_at", -1).to_list(20)
    
    auditor['recent_assignments'] = assignments
    
    return auditor

@api_router.put("/auditors/{auditor_id}")
async def update_auditor(auditor_id: str, updates: dict, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Update auditor details"""
    await get_current_user(credentials)
    
    auditor = await db.auditors.find_one({"id": auditor_id})
    if not auditor:
        raise HTTPException(status_code=404, detail="Auditor not found")
    
    updates['updated_at'] = datetime.now(timezone.utc).isoformat()
    await db.auditors.update_one({"id": auditor_id}, {"$set": updates})
    
    return {"message": "Auditor updated"}

@api_router.delete("/auditors/{auditor_id}")
async def delete_auditor(auditor_id: str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Delete an auditor (soft delete - sets status to inactive)"""
    await get_current_user(credentials)
    
    auditor = await db.auditors.find_one({"id": auditor_id})
    if not auditor:
        raise HTTPException(status_code=404, detail="Auditor not found")
    
    # Check for active assignments
    active_assignments = await db.audit_assignments.count_documents({
        "auditor_id": auditor_id,
        "status": {"$in": ["assigned", "confirmed"]}
    })
    
    if active_assignments > 0:
        raise HTTPException(status_code=400, detail=f"Cannot delete auditor with {active_assignments} active assignments")
    
    # Soft delete
    await db.auditors.update_one(
        {"id": auditor_id},
        {"$set": {"status": "inactive", "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    return {"message": "Auditor deactivated"}

@api_router.post("/auditors/{auditor_id}/availability")
async def set_auditor_availability(
    auditor_id: str,
    availability_data: dict,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Set auditor availability for specific dates"""
    await get_current_user(credentials)
    
    auditor = await db.auditors.find_one({"id": auditor_id})
    if not auditor:
        raise HTTPException(status_code=404, detail="Auditor not found")
    
    # Update availability array
    current_availability = auditor.get('availability', [])
    date = availability_data.get('date')
    
    # Remove existing entry for this date
    current_availability = [a for a in current_availability if a.get('date') != date]
    
    # Add new entry
    current_availability.append({
        "date": date,
        "is_available": availability_data.get('is_available', True),
        "reason": availability_data.get('reason', '')
    })
    
    await db.auditors.update_one(
        {"id": auditor_id},
        {"$set": {
            "availability": current_availability,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    return {"message": "Availability updated"}

# ================= AUDIT ASSIGNMENT ROUTES =================

@api_router.post("/audit-schedules/{audit_id}/assign")
async def assign_auditor_to_audit(
    audit_id: str,
    assignment_data: dict,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Assign an auditor to an audit"""
    await get_current_user(credentials)
    
    # Verify audit exists
    audit = await db.audit_schedules.find_one({"id": audit_id})
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")
    
    # Verify auditor exists
    auditor_id = assignment_data.get('auditor_id')
    auditor = await db.auditors.find_one({"id": auditor_id})
    if not auditor:
        raise HTTPException(status_code=404, detail="Auditor not found")
    
    # Check if already assigned
    existing = await db.audit_assignments.find_one({
        "audit_id": audit_id,
        "auditor_id": auditor_id,
        "status": {"$ne": "cancelled"}
    })
    if existing:
        raise HTTPException(status_code=400, detail="Auditor already assigned to this audit")
    
    # Create assignment
    assignment = AuditAssignment(
        audit_id=audit_id,
        auditor_id=auditor_id,
        role=assignment_data.get('role', 'auditor'),
        notes=assignment_data.get('notes', '')
    )
    
    assignment_doc = assignment.model_dump()
    assignment_doc['assigned_at'] = assignment_doc['assigned_at'].isoformat()
    await db.audit_assignments.insert_one(assignment_doc)
    
    # Update audit with auditor name
    current_auditors = audit.get('auditors', '')
    auditor_name = auditor.get('name', '')
    if current_auditors:
        current_auditors += f", {auditor_name}"
    else:
        current_auditors = auditor_name
    
    await db.audit_schedules.update_one(
        {"id": audit_id},
        {"$set": {"auditors": current_auditors}}
    )
    
    return {"message": "Auditor assigned", "assignment_id": assignment.id}

@api_router.get("/audit-schedules/{audit_id}/assignments")
async def get_audit_assignments(audit_id: str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get all auditor assignments for an audit"""
    await get_current_user(credentials)
    
    assignments = await db.audit_assignments.find(
        {"audit_id": audit_id, "status": {"$ne": "cancelled"}},
        {"_id": 0}
    ).to_list(20)
    
    # Enrich with auditor details
    for assignment in assignments:
        auditor = await db.auditors.find_one({"id": assignment['auditor_id']}, {"_id": 0})
        if auditor:
            assignment['auditor'] = {
                "id": auditor['id'],
                "name": auditor['name'],
                "name_ar": auditor.get('name_ar', ''),
                "email": auditor['email'],
                "certification_level": auditor.get('certification_level', ''),
                "specializations": auditor.get('specializations', [])
            }
    
    return assignments

@api_router.delete("/audit-assignments/{assignment_id}")
async def remove_auditor_assignment(assignment_id: str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Remove an auditor from an audit"""
    await get_current_user(credentials)
    
    assignment = await db.audit_assignments.find_one({"id": assignment_id})
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    # Cancel assignment
    await db.audit_assignments.update_one(
        {"id": assignment_id},
        {"$set": {"status": "cancelled"}}
    )
    
    # Update audit auditors list
    audit = await db.audit_schedules.find_one({"id": assignment['audit_id']})
    if audit:
        auditor = await db.auditors.find_one({"id": assignment['auditor_id']})
        if auditor:
            current_auditors = audit.get('auditors', '')
            auditor_name = auditor.get('name', '')
            # Remove auditor name from list
            auditor_list = [a.strip() for a in current_auditors.split(',') if a.strip() != auditor_name]
            await db.audit_schedules.update_one(
                {"id": assignment['audit_id']},
                {"$set": {"auditors": ', '.join(auditor_list)}}
            )
    
    return {"message": "Assignment removed"}

# ================= AUDIT SCHEDULE ROUTES =================

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

# ================= INVOICE & PAYMENT ROUTES =================

async def generate_invoice_number():
    """Generate unique invoice number: INV-YYYY-XXXX"""
    year = datetime.now().year
    # Find the last invoice number for this year
    last_invoice = await db.invoices.find_one(
        {"invoice_number": {"$regex": f"^INV-{year}-"}},
        sort=[("invoice_number", -1)]
    )
    if last_invoice:
        last_num = int(last_invoice['invoice_number'].split('-')[-1])
        new_num = last_num + 1
    else:
        new_num = 1
    return f"INV-{year}-{new_num:04d}"

@api_router.get("/invoices")
async def get_invoices(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    status: Optional[str] = None,
    contract_id: Optional[str] = None
):
    """Get all invoices with optional filtering"""
    await get_current_user(credentials)
    
    query = {}
    if status:
        query["status"] = status
    if contract_id:
        query["contract_id"] = contract_id
    
    invoices = await db.invoices.find(query, {"_id": 0}).sort("created_at", -1).to_list(1000)
    
    # Check for overdue invoices and update status
    today = datetime.now().strftime("%Y-%m-%d")
    for invoice in invoices:
        if invoice.get('status') == 'sent' and invoice.get('due_date') and invoice.get('due_date') < today:
            await db.invoices.update_one(
                {"id": invoice['id']},
                {"$set": {"status": "overdue"}}
            )
            invoice['status'] = 'overdue'
    
    return invoices

@api_router.get("/invoices/stats")
async def get_invoice_stats(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get invoice statistics"""
    await get_current_user(credentials)
    
    invoices = await db.invoices.find({}, {"_id": 0}).to_list(1000)
    today = datetime.now().strftime("%Y-%m-%d")
    
    total_invoiced = sum(inv.get('total_amount', 0) for inv in invoices)
    total_paid = sum(inv.get('paid_amount', 0) for inv in invoices if inv.get('status') == 'paid')
    total_pending = sum(inv.get('total_amount', 0) for inv in invoices if inv.get('status') in ['sent', 'viewed'])
    total_overdue = sum(inv.get('total_amount', 0) for inv in invoices if inv.get('status') == 'overdue' or (inv.get('status') == 'sent' and inv.get('due_date', '') < today))
    
    return {
        "total_invoices": len(invoices),
        "total_invoiced": total_invoiced,
        "total_paid": total_paid,
        "total_pending": total_pending,
        "total_overdue": total_overdue,
        "paid_count": len([inv for inv in invoices if inv.get('status') == 'paid']),
        "pending_count": len([inv for inv in invoices if inv.get('status') in ['sent', 'viewed']]),
        "overdue_count": len([inv for inv in invoices if inv.get('status') == 'overdue' or (inv.get('status') == 'sent' and inv.get('due_date', '') < today)]),
        "draft_count": len([inv for inv in invoices if inv.get('status') == 'draft'])
    }

@api_router.post("/invoices")
async def create_invoice(invoice_data: InvoiceCreate, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Create a new invoice from a contract/proposal"""
    await get_current_user(credentials)
    
    # Get contract/proposal details
    proposal = await db.proposals.find_one({"id": invoice_data.contract_id}, {"_id": 0})
    if not proposal:
        raise HTTPException(status_code=404, detail="Contract not found")
    
    # Generate invoice number
    invoice_number = await generate_invoice_number()
    
    # Calculate due date based on payment terms
    issue_date = datetime.now()
    if invoice_data.due_date:
        due_date = invoice_data.due_date
    else:
        days_map = {"due_on_receipt": 0, "net_15": 15, "net_30": 30, "net_60": 60}
        days = days_map.get(invoice_data.payment_terms, 30)
        due_date = (issue_date + timedelta(days=days)).strftime("%Y-%m-%d")
    
    # Create invoice items from proposal if not provided
    items = invoice_data.items
    if not items:
        service_fees = proposal.get('service_fees', {})
        items = []
        
        if service_fees.get('initial_certification', 0) > 0:
            items.append(InvoiceItem(
                description="Initial Certification Fee",
                description_ar="رسوم الشهادة الأولية",
                quantity=1,
                unit_price=service_fees['initial_certification'],
                total=service_fees['initial_certification']
            ).model_dump())
        
        if service_fees.get('surveillance_1', 0) > 0:
            items.append(InvoiceItem(
                description="Surveillance Audit 1 Fee",
                description_ar="رسوم تدقيق المراقبة 1",
                quantity=1,
                unit_price=service_fees['surveillance_1'],
                total=service_fees['surveillance_1']
            ).model_dump())
        
        if service_fees.get('surveillance_2', 0) > 0:
            items.append(InvoiceItem(
                description="Surveillance Audit 2 Fee",
                description_ar="رسوم تدقيق المراقبة 2",
                quantity=1,
                unit_price=service_fees['surveillance_2'],
                total=service_fees['surveillance_2']
            ).model_dump())
        
        if service_fees.get('recertification', 0) > 0:
            items.append(InvoiceItem(
                description="Recertification Fee",
                description_ar="رسوم إعادة الاعتماد",
                quantity=1,
                unit_price=service_fees['recertification'],
                total=service_fees['recertification']
            ).model_dump())
    
    # Calculate totals
    subtotal = sum(item.get('total', item.get('unit_price', 0) * item.get('quantity', 1)) for item in items)
    tax_amount = subtotal * (invoice_data.tax_rate / 100)
    total_amount = subtotal + tax_amount
    
    invoice = Invoice(
        invoice_number=invoice_number,
        contract_id=invoice_data.contract_id,
        organization_name=proposal.get('organization_name', ''),
        organization_address=proposal.get('organization_address', ''),
        contact_email=proposal.get('contact_email', ''),
        contact_phone=proposal.get('organization_phone', ''),
        items=items,
        subtotal=subtotal,
        tax_rate=invoice_data.tax_rate,
        tax_amount=tax_amount,
        total_amount=total_amount,
        currency=proposal.get('service_fees', {}).get('currency', 'SAR'),
        issue_date=issue_date.strftime("%Y-%m-%d"),
        due_date=due_date,
        payment_terms=invoice_data.payment_terms,
        notes=invoice_data.notes,
        status="draft"
    )
    
    invoice_doc = invoice.model_dump()
    invoice_doc['created_at'] = invoice_doc['created_at'].isoformat()
    
    await db.invoices.insert_one(invoice_doc)
    
    return {"message": "Invoice created", "invoice_id": invoice.id, "invoice_number": invoice_number}

@api_router.get("/invoices/{invoice_id}")
async def get_invoice(invoice_id: str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get invoice details"""
    await get_current_user(credentials)
    
    invoice = await db.invoices.find_one({"id": invoice_id}, {"_id": 0})
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    return invoice

@api_router.put("/invoices/{invoice_id}")
async def update_invoice(invoice_id: str, updates: dict, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Update invoice details"""
    await get_current_user(credentials)
    
    invoice = await db.invoices.find_one({"id": invoice_id}, {"_id": 0})
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    # Don't allow editing paid invoices
    if invoice.get('status') == 'paid':
        raise HTTPException(status_code=400, detail="Cannot edit paid invoice")
    
    updates['updated_at'] = datetime.now(timezone.utc).isoformat()
    
    # Recalculate totals if items changed
    if 'items' in updates:
        subtotal = sum(item.get('total', item.get('unit_price', 0) * item.get('quantity', 1)) for item in updates['items'])
        tax_rate = updates.get('tax_rate', invoice.get('tax_rate', 15))
        tax_amount = subtotal * (tax_rate / 100)
        updates['subtotal'] = subtotal
        updates['tax_amount'] = tax_amount
        updates['total_amount'] = subtotal + tax_amount
    
    await db.invoices.update_one({"id": invoice_id}, {"$set": updates})
    
    return {"message": "Invoice updated"}

@api_router.post("/invoices/{invoice_id}/send")
async def send_invoice(invoice_id: str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Mark invoice as sent (would send email in production)"""
    await get_current_user(credentials)
    
    invoice = await db.invoices.find_one({"id": invoice_id}, {"_id": 0})
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    await db.invoices.update_one(
        {"id": invoice_id},
        {"$set": {
            "status": "sent",
            "sent_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    # Create notification
    await create_notification(
        notification_type="invoice_sent",
        title="تم إرسال فاتورة",
        message=f"تم إرسال الفاتورة {invoice.get('invoice_number')} إلى {invoice.get('organization_name')}",
        related_id=invoice_id,
        related_type="invoice"
    )
    
    return {"message": "Invoice sent"}

@api_router.post("/invoices/{invoice_id}/record-payment")
async def record_payment(invoice_id: str, payment_data: dict, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Record a payment against an invoice"""
    current_user = await get_current_user(credentials)
    
    invoice = await db.invoices.find_one({"id": invoice_id}, {"_id": 0})
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    amount = payment_data.get('amount', 0)
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Payment amount must be positive")
    
    # Create payment record
    payment = PaymentRecord(
        invoice_id=invoice_id,
        amount=amount,
        payment_date=payment_data.get('payment_date', datetime.now().strftime("%Y-%m-%d")),
        payment_method=payment_data.get('payment_method', 'bank_transfer'),
        reference=payment_data.get('reference', ''),
        notes=payment_data.get('notes', ''),
        recorded_by=current_user.get('email', '')
    )
    
    payment_doc = payment.model_dump()
    payment_doc['created_at'] = payment_doc['created_at'].isoformat()
    await db.payments.insert_one(payment_doc)
    
    # Update invoice
    new_paid_amount = invoice.get('paid_amount', 0) + amount
    new_status = 'paid' if new_paid_amount >= invoice.get('total_amount', 0) else invoice.get('status')
    
    await db.invoices.update_one(
        {"id": invoice_id},
        {"$set": {
            "paid_amount": new_paid_amount,
            "status": new_status,
            "paid_date": payment_data.get('payment_date') if new_status == 'paid' else None,
            "payment_method": payment_data.get('payment_method', ''),
            "payment_reference": payment_data.get('reference', ''),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    # Create notification
    await create_notification(
        notification_type="payment_received",
        title="تم استلام دفعة",
        message=f"تم استلام دفعة بقيمة {amount} {invoice.get('currency', 'SAR')} للفاتورة {invoice.get('invoice_number')}",
        related_id=invoice_id,
        related_type="invoice"
    )
    
    return {"message": "Payment recorded", "new_status": new_status, "paid_amount": new_paid_amount}

@api_router.get("/invoices/{invoice_id}/payments")
async def get_invoice_payments(invoice_id: str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get all payments for an invoice"""
    await get_current_user(credentials)
    
    payments = await db.payments.find({"invoice_id": invoice_id}, {"_id": 0}).sort("payment_date", -1).to_list(100)
    return payments

@api_router.delete("/invoices/{invoice_id}")
async def delete_invoice(invoice_id: str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Delete a draft invoice"""
    await get_current_user(credentials)
    
    invoice = await db.invoices.find_one({"id": invoice_id}, {"_id": 0})
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    if invoice.get('status') != 'draft':
        raise HTTPException(status_code=400, detail="Only draft invoices can be deleted")
    
    await db.invoices.delete_one({"id": invoice_id})
    return {"message": "Invoice deleted"}

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
    
    def has_arabic_chars(text):
        """Check if text contains Arabic characters"""
        if not text:
            return False
        return any('\u0600' <= char <= '\u06FF' or '\u0750' <= char <= '\u077F' for char in str(text))
    
    def draw_text_value(text, x, y, font_size=9):
        """Draw text value using appropriate font based on content"""
        text_str = str(text) if text else 'N/A'
        if has_arabic_chars(text_str) and arabic_font_available:
            # Use Arabic font for Arabic text
            try:
                reshaped = arabic_reshaper.reshape(text_str)
                bidi_text = get_display(reshaped)
                c.setFont('Amiri', font_size)
                c.drawString(x, y, bidi_text)
            except Exception as e:
                print(f"Error rendering Arabic value: {e}")
                c.setFont('Helvetica', font_size)
                c.drawString(x, y, text_str)
        else:
            c.setFont('Helvetica', font_size)
            c.drawString(x, y, text_str)
    
    def draw_field(label_en, label_ar, value, y_pos):
        """Draw bilingual field with value on both sides - separated columns to prevent overlap"""
        value_str = str(value) if value else 'N/A'
        # Truncate long values to prevent overflow (max ~25 chars for each side)
        value_display = value_str[:30] + '...' if len(value_str) > 30 else value_str
        c.setFillColor(colors.black)
        # English side (left half of page) - label at 50, value at 145
        c.setFont('Helvetica-Bold', 9)
        c.drawString(50, y_pos, f"{label_en}:")
        # Draw value using appropriate font (Amiri for Arabic, Helvetica for English)
        draw_text_value(value_display, 145, y_pos, 9)
        # Arabic side (right half of page) - value at center-right, label at far right
        draw_arabic_text(f"{label_ar}:", width - 50, y_pos, 9, bold=True)
        draw_arabic_text(value_display, width - 160, y_pos, 9)
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
    y -= 10
    
    # Draw the official company seal image - positioned with sufficient margin above footer (footer is 0-45)
    # Seal needs to be placed at minimum y=50 to avoid footer overlap
    seal_y = max(y - 80, 55)  # Ensure seal stays above footer with 10px buffer
    if seal_path.exists():
        try:
            c.drawImage(str(seal_path), width/2 - 40, seal_y, width=80, height=80, preserveAspectRatio=True, mask='auto')
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
            footer_ar = arabic_reshaper.reshape("بيان للتحقق والمطابقة")
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
    """Generate a professional bilingual form submission PDF"""
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib import colors
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
    
    logo_path = ROOT_DIR / "assets" / "bayan-logo.png"
    pdf_path = CONTRACTS_DIR / f"form_{form['id']}_bilingual.pdf"
    c = canvas.Canvas(str(pdf_path), pagesize=A4)
    width, height = A4
    
    # Colors
    primary_color = colors.HexColor('#1e3a5f')  # Dark blue for header/footer
    section_color = colors.HexColor('#4a7c9b')  # Muted blue for section titles
    light_bg = colors.HexColor('#f0f4f8')
    accent_color = colors.HexColor('#2563eb')
    
    def draw_arabic(text, x, y, size=10, bold=False, right_align=False):
        """Draw Arabic text with proper reshaping"""
        if arabic_font_available:
            try:
                reshaped = arabic_reshaper.reshape(str(text))
                bidi_text = get_display(reshaped)
                font = 'Amiri-Bold' if bold and font_bold_path.exists() else 'Amiri'
                c.setFont(font, size)
                if right_align:
                    c.drawRightString(x, y, bidi_text)
                else:
                    c.drawString(x, y, bidi_text)
            except:
                c.setFont('Helvetica', size)
                c.drawString(x, y, str(text))
        else:
            c.setFont('Helvetica', size)
            c.drawString(x, y, str(text))
    
    def has_arabic(text):
        if not text: return False
        return any('\u0600' <= c <= '\u06FF' for c in str(text))
    
    def draw_value(text, x, y, size=10):
        """Draw value with appropriate font"""
        text_str = str(text) if text else 'N/A'
        if has_arabic(text_str) and arabic_font_available:
            try:
                reshaped = arabic_reshaper.reshape(text_str)
                bidi_text = get_display(reshaped)
                c.setFont('Amiri', size)
                c.drawString(x, y, bidi_text)
            except:
                c.setFont('Helvetica', size)
                c.drawString(x, y, text_str)
        else:
            c.setFont('Helvetica', size)
            c.drawString(x, y, text_str)
    
    # ============ HEADER ============
    c.setFillColor(primary_color)
    c.rect(0, height - 80, width, 80, fill=True, stroke=False)
    
    # Logo with white background
    if logo_path.exists():
        try:
            c.setFillColor(colors.white)
            c.roundRect(20, height - 70, 60, 60, 5, fill=True, stroke=False)
            c.drawImage(str(logo_path), 23, height - 67, width=54, height=54, preserveAspectRatio=True, mask='auto')
        except: pass
    
    # Title
    c.setFillColor(colors.white)
    c.setFont('Helvetica-Bold', 20)
    c.drawCentredString(width/2, height - 40, "APPLICATION FORM")
    if arabic_font_available:
        try:
            ar_title = get_display(arabic_reshaper.reshape("طلب المنح"))
            c.setFont('Amiri-Bold', 16)
            c.drawCentredString(width/2, height - 60, ar_title)
        except: pass
    
    # Reference and Date
    c.setFont('Helvetica', 9)
    c.drawRightString(width - 25, height - 30, f"Ref: {form.get('id', 'N/A')[:8].upper()}")
    c.drawRightString(width - 25, height - 45, f"Date: {str(form.get('submitted_at', form.get('created_at', '')))[:10]}")
    
    company_data = form.get('company_data', {})
    client_info = form.get('client_info', {})
    
    # ============ SECTION DRAWING FUNCTIONS ============
    def draw_section_box(title_en, title_ar, y_start, fields, box_height=None):
        """Draw a section with background box and fields
        Layout: English Label | VALUE (centered) | Arabic Label
        Dropdown values are translated to Arabic
        """
        if box_height is None:
            box_height = len(fields) * 18 + 30
        
        # Translation map for dropdown values (show full Arabic label as in dropdown)
        translations = {
            # Legal Status - match dropdown exactly
            'private': 'شركة خاصة',
            'public': 'شركة عامة',
            'government': 'مؤسسة حكومية',
            'public_sector': 'قطاع عام',
            'sole_proprietorship': 'ملكية فردية',
            'non-profit': 'منظمة غير ربحية',
            'partnership': 'شراكة',
            'other': 'أخرى',
            # Certification Program
            'initial': 'اعتماد أولي',
            'renewal': 'تجديد الاعتماد',
            'transfer': 'نقل الاعتماد',
            'surveillance': 'تدقيق مراقبة',
            # Yes/No
            'yes': 'نعم',
            'no': 'لا',
            'Yes': 'نعم',
            'No': 'لا',
            'true': 'نعم',
            'false': 'لا',
            'True': 'نعم',
            'False': 'لا',
        }
        
        # Section header bar (different color from main header/footer)
        c.setFillColor(section_color)
        c.rect(30, y_start - 22, width - 60, 22, fill=True, stroke=False)
        c.setFillColor(colors.white)
        c.setFont('Helvetica-Bold', 10)
        c.drawString(40, y_start - 16, title_en)
        if arabic_font_available:
            try:
                ar = get_display(arabic_reshaper.reshape(title_ar))
                c.setFont('Amiri-Bold', 10)
                c.drawRightString(width - 40, y_start - 16, ar)
            except: pass
        
        # Content box
        c.setFillColor(light_bg)
        c.rect(30, y_start - box_height, width - 60, box_height - 22, fill=True, stroke=False)
        c.setStrokeColor(colors.HexColor('#d1d5db'))
        c.setLineWidth(0.5)
        c.rect(30, y_start - box_height, width - 60, box_height, fill=False, stroke=True)
        
        # Draw fields: English Label | Value (center) | Arabic Label
        y = y_start - 40
        center_x = width / 2
        
        for label_en, label_ar, value in fields:
            c.setFillColor(colors.black)
            val_str = str(value) if value else 'N/A'
            val_display = val_str[:35] + '...' if len(val_str) > 35 else val_str
            
            # Translate dropdown values to Arabic
            if val_display in translations:
                val_display = translations[val_display]
            elif val_display.lower() in translations:
                val_display = translations[val_display.lower()]
            
            # LEFT: English label
            c.setFont('Helvetica-Bold', 9)
            c.drawString(40, y, f"{label_en}:")
            
            # CENTER: Value (with appropriate font)
            if has_arabic(val_display):
                if arabic_font_available:
                    try:
                        reshaped = arabic_reshaper.reshape(val_display)
                        bidi_val = get_display(reshaped)
                        c.setFont('Amiri', 9)
                        c.drawCentredString(center_x, y, bidi_val)
                    except:
                        c.setFont('Helvetica', 9)
                        c.drawCentredString(center_x, y, val_display)
                else:
                    c.setFont('Helvetica', 9)
                    c.drawCentredString(center_x, y, val_display)
            else:
                c.setFont('Helvetica', 9)
                c.drawCentredString(center_x, y, val_display)
            
            # RIGHT: Arabic label
            if arabic_font_available:
                try:
                    ar_label = get_display(arabic_reshaper.reshape(f"{label_ar}:"))
                    c.setFont('Amiri-Bold', 9)
                    c.drawRightString(width - 40, y, ar_label)
                except: pass
            
            y -= 18
        
        return y_start - box_height - 8
    
    # ============ PAGE 1 CONTENT ============
    y = height - 100
    
    # Section 1: Company Information
    company_fields = [
        ("Company Name", "اسم الشركة", company_data.get('companyName', client_info.get('company_name', 'N/A'))),
        ("Legal Status", "الحالة القانونية", company_data.get('legalStatus', 'N/A')),
        ("Address", "العنوان", company_data.get('address', 'N/A')),
        ("Phone", "الهاتف", company_data.get('phoneNumber', client_info.get('phone', 'N/A'))),
        ("Email", "البريد الإلكتروني", company_data.get('email', client_info.get('email', 'N/A'))),
        ("Website", "الموقع الإلكتروني", company_data.get('website', 'N/A')),
    ]
    y = draw_section_box("1. COMPANY INFORMATION", "١. معلومات الشركة", y, company_fields)
    
    # Consistent spacing between sections on page 1
    section_gap = 18
    y -= section_gap
    
    # Section 2: Contact Information
    contact_fields = [
        ("Contact Person", "جهة الاتصال", company_data.get('contactPerson', client_info.get('name', 'N/A'))),
        ("Designation", "المنصب", company_data.get('designation', 'N/A')),
        ("Mobile", "الجوال", company_data.get('mobileNumber', 'N/A')),
        ("Contact Email", "البريد الإلكتروني", company_data.get('contactEmail', 'N/A')),
    ]
    y = draw_section_box("2. CONTACT INFORMATION", "٢. معلومات الاتصال", y, contact_fields)
    y -= section_gap
    
    # Section 3: Organization Details
    org_fields = [
        ("Total Employees", "إجمالي الموظفين", company_data.get('totalEmployees', 'N/A')),
        ("Full-Time Employees", "دوام كامل", company_data.get('fullTimeEmployees', 'N/A')),
        ("Part-Time Employees", "دوام جزئي", company_data.get('partTimeEmployees', 'N/A')),
        ("Number of Sites", "عدد المواقع", company_data.get('numberOfSites', 'N/A')),
        ("Location Shifts", "الورديات", company_data.get('locationShifts', 'N/A')),
        ("Key Business Processes", "العمليات الرئيسية", company_data.get('keyBusinessProcesses', 'N/A')),
    ]
    y = draw_section_box("3. ORGANIZATION DETAILS", "٣. تفاصيل المنظمة", y, org_fields)
    y -= section_gap
    
    # Section 4: Certification Standards (moved to page 1)
    standards = company_data.get('certificationSchemes', [])
    standards_text = ', '.join(standards) if standards else 'N/A'
    cert_fields = [
        ("Selected Standards", "المعايير المختارة", standards_text),
        ("Certification Program", "برنامج الاعتماد", company_data.get('certificationProgram', 'N/A')),
        ("Already Certified?", "معتمد حالياً؟", company_data.get('isAlreadyCertified', 'N/A')),
    ]
    if company_data.get('otherStandard'):
        cert_fields.append(("Other Standard", "معيار آخر", company_data.get('otherStandard')))
    y = draw_section_box("4. CERTIFICATION STANDARDS", "٤. معايير الاعتماد", y, cert_fields)
    y -= section_gap
    
    # Section 5: Sites Information (on page 1)
    site_fields = []
    site1 = company_data.get('site1Address', '')
    site2 = company_data.get('site2Address', '')
    if site1:
        site_fields.append(("Site 1 Address", "عنوان الموقع 1", site1))
    if site2:
        site_fields.append(("Site 2 Address", "عنوان الموقع 2", site2))
    if not site_fields:
        site_fields.append(("Primary Location", "الموقع الرئيسي", "Main office only"))
    y = draw_section_box("5. SITES INFORMATION", "٥. معلومات المواقع", y, site_fields)
    y -= section_gap
    
    # Section 6: Consultant Information (on page 1)
    consultant_fields = [
        ("Consultant Used?", "هل تم استخدام مستشار؟", company_data.get('isConsultantInvolved', 'N/A')),
    ]
    if company_data.get('consultantName'):
        consultant_fields.append(("Consultant Name", "اسم المستشار", company_data.get('consultantName')))
    y = draw_section_box("6. CONSULTANT", "٦. المستشار", y, consultant_fields)
    
    # Footer for page 1
    c.setFillColor(primary_color)
    c.rect(0, 0, width, 35, fill=True, stroke=False)
    c.setFillColor(colors.white)
    c.setFont('Helvetica', 9)
    c.drawCentredString(width/2 - 60, 18, "BAYAN Auditing & Conformity")
    if arabic_font_available:
        try:
            ar_footer = get_display(arabic_reshaper.reshape("بيان للتحقق والمطابقة"))
            c.setFont('Amiri', 9)
            c.drawString(width/2 + 20, 16, ar_footer)
        except: pass
    c.setFont('Helvetica', 8)
    c.drawCentredString(width/2, 6, "Page 1 of 2")
    
    # ============ PAGE 2 ============
    c.showPage()
    
    # Header for page 2
    c.setFillColor(primary_color)
    c.rect(0, height - 50, width, 50, fill=True, stroke=False)
    if logo_path.exists():
        try:
            c.setFillColor(colors.white)
            c.roundRect(20, height - 45, 40, 40, 4, fill=True, stroke=False)
            c.drawImage(str(logo_path), 22, height - 43, width=36, height=36, preserveAspectRatio=True, mask='auto')
        except: pass
    c.setFillColor(colors.white)
    c.setFont('Helvetica-Bold', 14)
    c.drawCentredString(width/2, height - 30, "APPLICATION FORM (Continued)")
    
    y = height - 70
    
    # Section 7: Declaration (on page 2)
    decl_fields = [
        ("Declared By", "المُقِر", company_data.get('declarationName', 'N/A')),
        ("Designation", "المنصب", company_data.get('declarationDesignation', 'N/A')),
        ("Agreement", "الموافقة", "Yes / نعم" if company_data.get('declarationAgreed') else "No / لا"),
    ]
    y = draw_section_box("7. DECLARATION", "٧. الإقرار", y, decl_fields)
    
    # ============ IMPORTANT NOTES SECTION (on page 2) ============
    c.setFillColor(section_color)
    c.rect(30, y - 22, width - 60, 22, fill=True, stroke=False)
    c.setFillColor(colors.white)
    # Draw English part with Helvetica
    c.setFont('Helvetica-Bold', 10)
    c.drawString(40, y - 16, "IMPORTANT NOTES /")
    # Draw Arabic part with Amiri font
    if arabic_font_available:
        try:
            ar_header = get_display(arabic_reshaper.reshape("ملاحظات هامة"))
            c.setFont('Amiri-Bold', 11)
            c.drawRightString(width - 40, y - 16, ar_header)
        except:
            pass
    
    # Notes content box
    notes_box_height = 85
    c.setFillColor(light_bg)
    c.rect(30, y - 22 - notes_box_height, width - 60, notes_box_height, fill=True, stroke=False)
    c.setStrokeColor(colors.HexColor('#d1d5db'))
    c.setLineWidth(0.5)
    c.rect(30, y - 22 - notes_box_height, width - 60, notes_box_height + 22, fill=False, stroke=True)
    
    c.setFillColor(colors.black)
    c.setFont('Helvetica', 9)
    # English notes (left side)
    notes_english = [
        "• Please ensure all information provided is accurate and up-to-date.",
        "• Incomplete applications may delay the certification process.",
        "• Additional documentation may be requested during the review process.",
        "• For inquiries, contact us at: info@bayan.sa or +966 11 XXX XXXX",
    ]
    # Arabic notes (right side) - matching English content
    notes_arabic = [
        "• يرجى التأكد من صحة جميع المعلومات المقدمة وحداثتها",
        "• قد تؤدي الطلبات غير المكتملة إلى تأخير عملية الاعتماد",
        "• قد يتم طلب وثائق إضافية خلال عملية المراجعة",
        "• للاستفسارات، تواصل معنا على: info@bayan.sa أو +966 11 XXX XXXX",
    ]
    
    ny = y - 35
    # Draw English notes on left, Arabic notes on right (side by side)
    for i in range(len(notes_english)):
        # English on left
        c.setFont('Helvetica', 9)
        c.drawString(40, ny, notes_english[i])
        # Arabic on right
        if i < len(notes_arabic):
            draw_arabic(notes_arabic[i], width - 40, ny, 9, right_align=True)
        ny -= 16
    
    y = y - 22 - notes_box_height - 10
    
    # ============ TERMS & CONDITIONS (on page 2) ============
    c.setFillColor(section_color)
    c.rect(30, y - 22, width - 60, 22, fill=True, stroke=False)
    c.setFillColor(colors.white)
    c.setFont('Helvetica-Bold', 10)
    c.drawString(40, y - 16, "TERMS & CONDITIONS /")
    # Draw Arabic part with Amiri font
    if arabic_font_available:
        try:
            ar_terms_header = get_display(arabic_reshaper.reshape("الشروط والأحكام"))
            c.setFont('Amiri-Bold', 11)
            c.drawRightString(width - 40, y - 16, ar_terms_header)
        except:
            pass
    
    # Terms content box - fixed height
    terms_box_height = 115
    c.setFillColor(light_bg)
    c.rect(30, y - 22 - terms_box_height, width - 60, terms_box_height, fill=True, stroke=False)
    c.setStrokeColor(colors.HexColor('#d1d5db'))
    c.setLineWidth(0.5)
    c.rect(30, y - 22 - terms_box_height, width - 60, terms_box_height + 22, fill=False, stroke=True)
    
    c.setFillColor(colors.black)
    c.setFont('Helvetica', 8)
    # English terms (left side)
    terms_english = [
        "1. This application is subject to review and approval by BAYAN.",
        "2. All information provided must be accurate and complete.",
        "3. The applicant agrees to comply with all certification requirements.",
        "4. Certification fees are non-refundable once the audit begins.",
        "5. BAYAN reserves the right to conduct surveillance audits.",
    ]
    # Arabic terms (right side) - matching English content
    terms_arabic = [
        "١. هذا الطلب خاضع للمراجعة والموافقة من قبل بيان",
        "٢. يجب أن تكون جميع المعلومات المقدمة دقيقة وكاملة",
        "٣. يوافق المتقدم على الامتثال لجميع متطلبات الاعتماد",
        "٤. رسوم الاعتماد غير قابلة للاسترداد بمجرد بدء التدقيق",
        "٥. تحتفظ بيان بحق إجراء عمليات تدقيق المراقبة",
    ]
    
    ty = y - 35
    for i in range(len(terms_english)):
        c.setFont('Helvetica', 8)
        c.drawString(40, ty, terms_english[i])
        if i < len(terms_arabic):
            draw_arabic(terms_arabic[i], width - 40, ty, 8, right_align=True)
        ty -= 14
    
    y = y - 22 - terms_box_height - 10
    
    # ============ CLIENT DECLARATION SECTION (at the end of page 2) ============
    # Single centered declaration box for client
    sig_box_height = 130
    sig_box_width = width - 60  # Full width box, centered
    
    # ===== CLIENT DECLARATION BOX (Centered) =====
    c.setFillColor(light_bg)
    c.rect(30, y - sig_box_height, sig_box_width, sig_box_height - 10, fill=True, stroke=False)
    c.setStrokeColor(section_color)
    c.setLineWidth(1.5)
    c.rect(30, y - sig_box_height, sig_box_width, sig_box_height - 10, fill=False, stroke=True)
    
    # Header - Client's Declaration
    c.setFillColor(section_color)
    c.setFont('Helvetica-Bold', 9)
    c.drawString(40, y - 20, "CLIENT'S DECLARATION OF THE ACCURACY OF DATA /")
    if arabic_font_available:
        try:
            ar_declaration = get_display(arabic_reshaper.reshape("إقرار العميل بصحة البيانات"))
            c.setFont('Amiri-Bold', 9)
            c.drawRightString(width - 40, y - 20, ar_declaration)
        except: pass
    
    # Client signature fields - arranged in two columns
    c.setFillColor(colors.black)
    col1_x = 50  # Left column
    col2_x = width/2 + 20  # Right column
    line_length = 140
    
    # Name field (left column)
    c.setFont('Helvetica', 8)
    c.drawString(col1_x, y - 45, "Name:")
    c.line(col1_x + 45, y - 47, col1_x + 45 + line_length, y - 47)
    if arabic_font_available:
        try:
            ar_name = get_display(arabic_reshaper.reshape("الاسم:"))
            c.setFont('Amiri', 9)
            c.drawRightString(col1_x + 45 + line_length + 40, y - 45, ar_name)
        except: pass
    
    # Date field (right column)
    c.setFont('Helvetica', 8)
    c.drawString(col2_x, y - 45, "Date:")
    c.line(col2_x + 45, y - 47, col2_x + 45 + line_length, y - 47)
    if arabic_font_available:
        try:
            ar_date = get_display(arabic_reshaper.reshape("التاريخ:"))
            c.setFont('Amiri', 9)
            c.drawRightString(col2_x + 45 + line_length + 40, y - 45, ar_date)
        except: pass
    
    # Signature field (left column)
    c.setFont('Helvetica', 8)
    c.drawString(col1_x, y - 70, "Signature:")
    c.line(col1_x + 55, y - 72, col1_x + 55 + line_length - 10, y - 72)
    if arabic_font_available:
        try:
            ar_sig = get_display(arabic_reshaper.reshape("التوقيع:"))
            c.setFont('Amiri', 9)
            c.drawRightString(col1_x + 45 + line_length + 40, y - 70, ar_sig)
        except: pass
    
    # Stamp field (right column)
    c.setFont('Helvetica', 8)
    c.drawString(col2_x, y - 70, "Stamp:")
    if arabic_font_available:
        try:
            ar_stamp = get_display(arabic_reshaper.reshape("الختم:"))
            c.setFont('Amiri', 9)
            c.drawRightString(col2_x + 45 + line_length + 40, y - 70, ar_stamp)
        except: pass
    
    # Draw stamp placeholder box
    stamp_box_size = 50
    stamp_x = col2_x + 50
    stamp_y = y - sig_box_height + 25
    c.setStrokeColor(colors.grey)
    c.setLineWidth(0.5)
    c.rect(stamp_x, stamp_y, stamp_box_size, stamp_box_size, fill=False, stroke=True)
    
    # Footer for page 2
    c.setFillColor(primary_color)
    c.rect(0, 0, width, 35, fill=True, stroke=False)
    c.setFillColor(colors.white)
    c.setFont('Helvetica', 9)
    c.drawCentredString(width/2 - 60, 18, "BAYAN Auditing & Conformity")
    if arabic_font_available:
        try:
            ar_footer = get_display(arabic_reshaper.reshape("بيان للتحقق والمطابقة"))
            c.setFont('Amiri', 9)
            c.drawString(width/2 + 20, 16, ar_footer)
        except: pass
    c.setFont('Helvetica', 8)
    c.drawCentredString(width/2, 6, "Page 2 of 2")
    
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

# ================= CERTIFICATE ENDPOINTS =================

async def generate_certificate_number():
    """Generate unique certificate number: CERT-YYYY-XXXX"""
    year = datetime.now().year
    last_cert = await db.certificates.find_one(
        {"certificate_number": {"$regex": f"^CERT-{year}-"}},
        sort=[("certificate_number", -1)]
    )
    if last_cert:
        last_num = int(last_cert['certificate_number'].split('-')[-1])
        new_num = last_num + 1
    else:
        new_num = 1
    return f"CERT-{year}-{new_num:04d}"

@api_router.get("/certificates")
async def get_certificates(
    status: str = None,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get all certificates with optional status filtering"""
    await get_current_user(credentials)
    
    query = {}
    if status and status != 'all':
        query['status'] = status
    
    certificates = await db.certificates.find(query, {"_id": 0}).sort("created_at", -1).to_list(1000)
    
    # Check for expired certificates and update status
    today = datetime.now().strftime("%Y-%m-%d")
    for cert in certificates:
        if cert.get('status') == 'active' and cert.get('expiry_date') and cert.get('expiry_date') < today:
            await db.certificates.update_one(
                {"id": cert['id']},
                {"$set": {"status": "expired"}}
            )
            cert['status'] = 'expired'
    
    return certificates

@api_router.get("/certificates/stats")
async def get_certificate_stats(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get certificate statistics"""
    await get_current_user(credentials)
    
    certificates = await db.certificates.find({}, {"_id": 0}).to_list(1000)
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Calculate expiring soon (within 90 days)
    expiring_date = (datetime.now() + timedelta(days=90)).strftime("%Y-%m-%d")
    
    return {
        "total_certificates": len(certificates),
        "active_count": len([c for c in certificates if c.get('status') == 'active']),
        "expired_count": len([c for c in certificates if c.get('status') == 'expired' or (c.get('status') == 'active' and c.get('expiry_date', '') < today)]),
        "suspended_count": len([c for c in certificates if c.get('status') == 'suspended']),
        "expiring_soon_count": len([c for c in certificates if c.get('status') == 'active' and today < c.get('expiry_date', '') <= expiring_date])
    }

@api_router.post("/certificates")
async def create_certificate(cert_data: CertificateCreate, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Create a new certificate after successful audit"""
    await get_current_user(credentials)
    
    # Get contract/agreement data
    agreement = await db.certification_agreements.find_one({"id": cert_data.contract_id}, {"_id": 0})
    if not agreement:
        raise HTTPException(status_code=404, detail="Agreement not found")
    
    # Get proposal data for organization info
    proposal = await db.proposals.find_one({"id": agreement.get('proposal_id')}, {"_id": 0})
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    
    # Get form data for detailed info
    form = await db.forms.find_one({"id": proposal.get('form_id')}, {"_id": 0})
    
    # Generate certificate number
    cert_number = await generate_certificate_number()
    
    # Calculate dates
    issue_date = datetime.now().strftime("%Y-%m-%d")
    expiry_date = (datetime.now() + timedelta(days=365*3)).strftime("%Y-%m-%d")  # 3 years validity
    
    # Generate verification URL
    base_url = os.environ.get('FRONTEND_URL', 'https://facility-grants.preview.emergentagent.com')
    verification_url = f"{base_url}/verify/{cert_number}"
    
    # Generate QR code
    qr_base64 = get_qr_code_base64(verification_url)
    
    # Get organization names
    org_name = form.get('responses', {}).get('organizationName', '') if form else agreement.get('organizationName', '')
    org_name_ar = form.get('responses', {}).get('organizationNameAr', '') if form else ''
    
    # Get standards
    standards = cert_data.standards if cert_data.standards else proposal.get('certification_standards', [])
    
    # Create certificate
    certificate = Certificate(
        certificate_number=cert_number,
        contract_id=cert_data.contract_id,
        audit_id=cert_data.audit_id,
        organization_name=org_name,
        organization_name_ar=org_name_ar,
        standards=standards,
        scope=cert_data.scope or proposal.get('scope', ''),
        scope_ar=cert_data.scope_ar or '',
        issue_date=issue_date,
        expiry_date=expiry_date,
        status="active",
        verification_url=verification_url,
        qr_code_data=qr_base64,
        lead_auditor=cert_data.lead_auditor,
        audit_team=cert_data.audit_team
    )
    
    cert_doc = certificate.model_dump()
    cert_doc['created_at'] = cert_doc['created_at'].isoformat()
    
    await db.certificates.insert_one(cert_doc)
    
    # Create notification
    await create_notification(
        notification_type="certificate_issued",
        title="Certificate Issued",
        message=f"Certificate {cert_number} has been issued for {org_name}",
        related_id=certificate.id,
        related_type="certificate"
    )
    
    return {"message": "Certificate created", "certificate_id": certificate.id, "certificate_number": cert_number}

@api_router.get("/certificates/{certificate_id}")
async def get_certificate(certificate_id: str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get certificate details"""
    await get_current_user(credentials)
    
    certificate = await db.certificates.find_one({"id": certificate_id}, {"_id": 0})
    if not certificate:
        raise HTTPException(status_code=404, detail="Certificate not found")
    
    return certificate

@api_router.put("/certificates/{certificate_id}/status")
async def update_certificate_status(certificate_id: str, status_data: dict, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Update certificate status (suspend, withdraw, reactivate)"""
    await get_current_user(credentials)
    
    certificate = await db.certificates.find_one({"id": certificate_id})
    if not certificate:
        raise HTTPException(status_code=404, detail="Certificate not found")
    
    new_status = status_data.get('status')
    valid_statuses = ['active', 'suspended', 'withdrawn', 'expired']
    if new_status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of {valid_statuses}")
    
    await db.certificates.update_one(
        {"id": certificate_id},
        {"$set": {
            "status": new_status,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    return {"message": f"Certificate status updated to {new_status}"}

@api_router.get("/certificates/{certificate_id}/pdf")
async def download_certificate_pdf(certificate_id: str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Generate and download certificate PDF"""
    await get_current_user(credentials)
    
    certificate = await db.certificates.find_one({"id": certificate_id}, {"_id": 0})
    if not certificate:
        raise HTTPException(status_code=404, detail="Certificate not found")
    
    # Generate PDF
    CERTIFICATES_DIR = ROOT_DIR / "certificates"
    CERTIFICATES_DIR.mkdir(exist_ok=True)
    
    pdf_filename = f"certificate_{certificate['certificate_number'].replace('-', '_')}.pdf"
    pdf_path = CERTIFICATES_DIR / pdf_filename
    
    generate_certificate_pdf(certificate, str(pdf_path))
    
    return FileResponse(
        str(pdf_path),
        media_type="application/pdf",
        filename=pdf_filename
    )

@api_router.get("/public/verify/{certificate_number}")
async def verify_certificate_public(certificate_number: str):
    """Public endpoint to verify a certificate via QR code scan"""
    certificate = await db.certificates.find_one(
        {"certificate_number": certificate_number},
        {"_id": 0, "qr_code_data": 0}  # Exclude QR code data for public
    )
    
    if not certificate:
        raise HTTPException(status_code=404, detail="Certificate not found")
    
    # Check if expired
    today = datetime.now().strftime("%Y-%m-%d")
    if certificate.get('expiry_date') and certificate.get('expiry_date') < today:
        certificate['status'] = 'expired'
    
    return {
        "valid": certificate.get('status') == 'active',
        "certificate_number": certificate.get('certificate_number'),
        "organization_name": certificate.get('organization_name'),
        "organization_name_ar": certificate.get('organization_name_ar'),
        "standards": certificate.get('standards', []),
        "scope": certificate.get('scope'),
        "issue_date": certificate.get('issue_date'),
        "expiry_date": certificate.get('expiry_date'),
        "status": certificate.get('status'),
        "lead_auditor": certificate.get('lead_auditor')
    }

# ================= EXPIRATION ALERTS ENDPOINTS =================

@api_router.get("/alerts/expiring")
async def get_expiring_items(
    days: int = 90,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get all items expiring within specified days (certificates, contracts)"""
    await get_current_user(credentials)
    
    today = datetime.now()
    expiry_date = (today + timedelta(days=days)).strftime("%Y-%m-%d")
    today_str = today.strftime("%Y-%m-%d")
    
    # Get expiring certificates
    expiring_certs = await db.certificates.find({
        "status": "active",
        "expiry_date": {"$gte": today_str, "$lte": expiry_date}
    }, {"_id": 0}).to_list(100)
    
    # Categorize by urgency
    alerts = {
        "critical": [],  # Expiring within 30 days
        "warning": [],   # Expiring within 60 days
        "info": []       # Expiring within 90 days
    }
    
    for cert in expiring_certs:
        exp_date = datetime.strptime(cert['expiry_date'], "%Y-%m-%d")
        days_until = (exp_date - today).days
        
        alert_item = {
            "type": "certificate",
            "id": cert['id'],
            "reference": cert['certificate_number'],
            "organization": cert['organization_name'],
            "expiry_date": cert['expiry_date'],
            "days_until_expiry": days_until,
            "standards": cert.get('standards', [])
        }
        
        if days_until <= 30:
            alerts["critical"].append(alert_item)
        elif days_until <= 60:
            alerts["warning"].append(alert_item)
        else:
            alerts["info"].append(alert_item)
    
    # Get upcoming surveillance audits
    upcoming_audits = await db.audit_schedules.find({
        "status": {"$ne": "completed"},
        "scheduled_date": {"$gte": today_str, "$lte": expiry_date}
    }, {"_id": 0}).to_list(100)
    
    for audit in upcoming_audits:
        audit_date = datetime.strptime(audit['scheduled_date'], "%Y-%m-%d")
        days_until = (audit_date - today).days
        
        alert_item = {
            "type": "audit",
            "id": audit['id'],
            "reference": audit.get('audit_type', 'Audit'),
            "organization": audit.get('organization_name', ''),
            "expiry_date": audit['scheduled_date'],
            "days_until_expiry": days_until,
            "audit_type": audit.get('audit_type', '')
        }
        
        if days_until <= 7:
            alerts["critical"].append(alert_item)
        elif days_until <= 14:
            alerts["warning"].append(alert_item)
        else:
            alerts["info"].append(alert_item)
    
    return {
        "summary": {
            "total_alerts": len(alerts["critical"]) + len(alerts["warning"]) + len(alerts["info"]),
            "critical_count": len(alerts["critical"]),
            "warning_count": len(alerts["warning"]),
            "info_count": len(alerts["info"])
        },
        "alerts": alerts
    }

@api_router.get("/dashboard/analytics")
async def get_dashboard_analytics(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get comprehensive analytics for the dashboard"""
    await get_current_user(credentials)
    
    # Get all data
    forms = await db.forms.find({}, {"_id": 0}).to_list(1000)
    proposals = await db.proposals.find({}, {"_id": 0}).to_list(1000)
    agreements = await db.certification_agreements.find({}, {"_id": 0}).to_list(1000)
    invoices = await db.invoices.find({}, {"_id": 0}).to_list(1000)
    certificates = await db.certificates.find({}, {"_id": 0}).to_list(1000)
    audits = await db.audit_schedules.find({}, {"_id": 0}).to_list(1000)
    
    # Calculate conversion rates
    total_forms = len(forms)
    submitted_forms = len([f for f in forms if f.get('status') in ['submitted', 'proposal_sent', 'proposal_accepted', 'agreement_signed']])
    proposals_sent = len(proposals)
    proposals_accepted = len([p for p in proposals if p.get('status') == 'agreement_signed'])
    contracts_signed = len(agreements)
    
    form_to_proposal_rate = (proposals_sent / total_forms * 100) if total_forms > 0 else 0
    proposal_to_contract_rate = (contracts_signed / proposals_sent * 100) if proposals_sent > 0 else 0
    overall_conversion_rate = (contracts_signed / total_forms * 100) if total_forms > 0 else 0
    
    # Revenue analytics
    total_quoted = sum(p.get('total_fees', 0) for p in proposals)
    total_accepted = sum(p.get('total_fees', 0) for p in proposals if p.get('status') == 'agreement_signed')
    total_invoiced = sum(i.get('total_amount', 0) for i in invoices)
    total_paid = sum(i.get('paid_amount', 0) for i in invoices if i.get('status') == 'paid')
    
    # Monthly data (last 6 months)
    monthly_data = []
    for i in range(5, -1, -1):
        month_date = datetime.now() - timedelta(days=30*i)
        month_str = month_date.strftime("%Y-%m")
        
        month_forms = len([f for f in forms if f.get('created_at', '')[:7] == month_str])
        month_proposals = len([p for p in proposals if p.get('created_at', '')[:7] == month_str])
        month_contracts = len([a for a in agreements if a.get('created_at', '')[:7] == month_str])
        month_revenue = sum(p.get('total_fees', 0) for p in proposals if p.get('created_at', '')[:7] == month_str and p.get('status') == 'agreement_signed')
        
        monthly_data.append({
            "month": month_date.strftime("%b %Y"),
            "forms": month_forms,
            "proposals": month_proposals,
            "contracts": month_contracts,
            "revenue": month_revenue
        })
    
    # Standards breakdown
    standards_count = {}
    for p in proposals:
        for std in p.get('certification_standards', []):
            standards_count[std] = standards_count.get(std, 0) + 1
    
    # Audit status
    completed_audits = len([a for a in audits if a.get('status') == 'completed'])
    scheduled_audits = len([a for a in audits if a.get('status') == 'scheduled'])
    pending_audits = len([a for a in audits if a.get('status') == 'pending'])
    
    return {
        "overview": {
            "total_forms": total_forms,
            "total_proposals": proposals_sent,
            "total_contracts": contracts_signed,
            "total_certificates": len(certificates),
            "active_certificates": len([c for c in certificates if c.get('status') == 'active'])
        },
        "conversion_rates": {
            "form_to_proposal": round(form_to_proposal_rate, 1),
            "proposal_to_contract": round(proposal_to_contract_rate, 1),
            "overall": round(overall_conversion_rate, 1)
        },
        "revenue": {
            "total_quoted": total_quoted,
            "total_accepted": total_accepted,
            "total_invoiced": total_invoiced,
            "total_collected": total_paid,
            "collection_rate": round((total_paid / total_invoiced * 100) if total_invoiced > 0 else 0, 1)
        },
        "monthly_trends": monthly_data,
        "standards_breakdown": standards_count,
        "audits": {
            "total": len(audits),
            "completed": completed_audits,
            "scheduled": scheduled_audits,
            "pending": pending_audits
        }
    }

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
