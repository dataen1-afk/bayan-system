"""
Certificate PDF Generator
Generates elegant, professional ISO certification certificates in English.
Clean, modern design reflecting quality and professionalism.
"""

from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm, mm
from reportlab.lib.colors import HexColor, white, black
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pathlib import Path
import qrcode
from io import BytesIO
from datetime import datetime

# Paths
ROOT_DIR = Path(__file__).parent
FONTS_DIR = ROOT_DIR / "fonts"
ASSETS_DIR = ROOT_DIR / "assets"

# Register fonts
try:
    pdfmetrics.registerFont(TTFont('Amiri', str(FONTS_DIR / 'Amiri-Regular.ttf')))
    pdfmetrics.registerFont(TTFont('Amiri-Bold', str(FONTS_DIR / 'Amiri-Bold.ttf')))
except:
    pass

# Elegant color palette
NAVY = HexColor('#1a2a3a')           # Deep navy for text
GOLD = HexColor('#b8860b')           # Elegant gold accent
GOLD_LIGHT = HexColor('#d4af37')     # Lighter gold
SLATE = HexColor('#4a5568')          # Secondary text
CREAM = HexColor('#faf8f5')          # Background tint
BORDER_GOLD = HexColor('#c9a227')    # Border accent


def generate_qr_code(verification_url: str) -> BytesIO:
    """Generate QR code for certificate verification"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=8,
        border=2,
    )
    qr.add_data(verification_url)
    qr.make(fit=True)
    
    qr_img = qr.make_image(fill_color="#1a2a3a", back_color="white")
    buffer = BytesIO()
    qr_img.save(buffer, format='PNG')
    buffer.seek(0)
    return buffer


def generate_certificate_pdf(certificate_data: dict) -> bytes:
    """
    Generate an elegant, professional certificate in English.
    
    Args:
        certificate_data: Dictionary containing:
            - certificate_number: Unique certificate ID
            - organization_name: Name of certified organization
            - organization_address: Address of organization
            - standard: ISO standard (e.g., "ISO 9001:2015")
            - scope: Scope of certification
            - initial_certification_date: First certification date
            - issue_date: Current certificate issue date
            - expiry_date: Certificate expiry date
            - verification_url: URL for QR code verification
    
    Returns:
        PDF bytes
    """
    
    # Extract data
    cert_number = certificate_data.get('certificate_number', 'BAC-XXXX-XXXX')
    org_name = certificate_data.get('organization_name', '')
    org_address = certificate_data.get('organization_address', '')
    standard = certificate_data.get('standard', 'ISO 9001:2015')
    scope = certificate_data.get('scope', '')
    initial_date = certificate_data.get('initial_certification_date', '')
    issue_date = certificate_data.get('issue_date', datetime.now().strftime('%Y-%m-%d'))
    expiry_date = certificate_data.get('expiry_date', '')
    verification_url = certificate_data.get('verification_url', f'https://www.bfrvc.sa/verify/{cert_number}')
    
    # Create PDF in landscape A4
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=landscape(A4))
    width, height = landscape(A4)
    
    # === BACKGROUND ===
    # Subtle cream background
    c.setFillColor(CREAM)
    c.rect(0, 0, width, height, fill=True, stroke=False)
    
    # === ELEGANT BORDER ===
    # Outer gold border
    c.setStrokeColor(GOLD)
    c.setLineWidth(3)
    c.rect(20, 20, width - 40, height - 40, fill=False, stroke=True)
    
    # Inner thin border
    c.setStrokeColor(NAVY)
    c.setLineWidth(0.5)
    c.rect(30, 30, width - 60, height - 60, fill=False, stroke=True)
    
    # Corner decorative elements
    corner_size = 25
    c.setStrokeColor(GOLD)
    c.setLineWidth(2)
    
    # Top-left corner
    c.line(35, height - 35, 35 + corner_size, height - 35)
    c.line(35, height - 35, 35, height - 35 - corner_size)
    
    # Top-right corner
    c.line(width - 35, height - 35, width - 35 - corner_size, height - 35)
    c.line(width - 35, height - 35, width - 35, height - 35 - corner_size)
    
    # Bottom-left corner
    c.line(35, 35, 35 + corner_size, 35)
    c.line(35, 35, 35, 35 + corner_size)
    
    # Bottom-right corner
    c.line(width - 35, 35, width - 35 - corner_size, 35)
    c.line(width - 35, 35, width - 35, 35 + corner_size)
    
    # === LOGO ===
    logo_path = ASSETS_DIR / "bayan-logo.png"
    if logo_path.exists():
        try:
            c.drawImage(str(logo_path), 60, height - 110, width=80, height=70, 
                       preserveAspectRatio=True, mask='auto')
        except:
            pass
    
    # === HEADER ===
    # Certification body name
    c.setFillColor(NAVY)
    c.setFont('Helvetica-Bold', 14)
    c.drawString(150, height - 60, "BAYAN AUDITING & CONFORMITY")
    
    c.setFont('Helvetica', 10)
    c.setFillColor(SLATE)
    c.drawString(150, height - 75, "Accredited Certification Body")
    
    # Certificate title
    c.setFillColor(NAVY)
    c.setFont('Helvetica-Bold', 28)
    c.drawCentredString(width / 2, height - 130, "CERTIFICATE OF REGISTRATION")
    
    # Decorative line under title
    c.setStrokeColor(GOLD)
    c.setLineWidth(2)
    c.line(width/2 - 150, height - 145, width/2 + 150, height - 145)
    
    # === MAIN CONTENT ===
    # "This is to certify that"
    c.setFont('Helvetica', 12)
    c.setFillColor(SLATE)
    c.drawCentredString(width / 2, height - 175, "This is to certify that")
    
    # Organization name (prominent)
    c.setFont('Helvetica-Bold', 22)
    c.setFillColor(NAVY)
    c.drawCentredString(width / 2, height - 210, org_name.upper())
    
    # Organization address
    c.setFont('Helvetica', 11)
    c.setFillColor(SLATE)
    c.drawCentredString(width / 2, height - 235, org_address)
    
    # Certification statement
    c.setFont('Helvetica', 12)
    c.setFillColor(SLATE)
    c.drawCentredString(width / 2, height - 270, "has been assessed and certified as meeting the requirements of")
    
    # Standard (prominent, with gold accent)
    c.setFont('Helvetica-Bold', 26)
    c.setFillColor(GOLD)
    c.drawCentredString(width / 2, height - 305, standard)
    
    # Scope section
    c.setFont('Helvetica', 11)
    c.setFillColor(SLATE)
    c.drawCentredString(width / 2, height - 340, "for the following scope:")
    
    # Scope text (wrapped if needed)
    c.setFont('Helvetica-Bold', 12)
    c.setFillColor(NAVY)
    
    # Simple text wrapping for scope
    max_width = 500
    if len(scope) > 80:
        # Split into multiple lines
        words = scope.split()
        lines = []
        current_line = ""
        for word in words:
            test_line = current_line + " " + word if current_line else word
            if c.stringWidth(test_line, 'Helvetica-Bold', 12) < max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        
        y_pos = height - 365
        for line in lines[:3]:  # Max 3 lines
            c.drawCentredString(width / 2, y_pos, line)
            y_pos -= 16
    else:
        c.drawCentredString(width / 2, height - 365, scope)
    
    # === DATES SECTION ===
    dates_y = 120
    
    # Left column - dates
    c.setFont('Helvetica', 9)
    c.setFillColor(SLATE)
    
    col1_x = 120
    col2_x = 320
    col3_x = 520
    
    # Initial Certification
    c.drawString(col1_x, dates_y, "Initial Certification:")
    c.setFont('Helvetica-Bold', 10)
    c.setFillColor(NAVY)
    c.drawString(col1_x, dates_y - 15, initial_date or "—")
    
    # Issue Date
    c.setFont('Helvetica', 9)
    c.setFillColor(SLATE)
    c.drawString(col2_x, dates_y, "Issue Date:")
    c.setFont('Helvetica-Bold', 10)
    c.setFillColor(NAVY)
    c.drawString(col2_x, dates_y - 15, issue_date)
    
    # Expiry Date
    c.setFont('Helvetica', 9)
    c.setFillColor(SLATE)
    c.drawString(col3_x, dates_y, "Valid Until:")
    c.setFont('Helvetica-Bold', 10)
    c.setFillColor(NAVY)
    c.drawString(col3_x, dates_y - 15, expiry_date)
    
    # === CERTIFICATE NUMBER ===
    c.setFont('Helvetica', 9)
    c.setFillColor(SLATE)
    c.drawString(col1_x, dates_y - 45, "Certificate Number:")
    c.setFont('Helvetica-Bold', 11)
    c.setFillColor(NAVY)
    c.drawString(col1_x, dates_y - 60, cert_number)
    
    # === SIGNATURE SECTION ===
    sig_x = width - 200
    sig_y = 90
    
    # Signature line
    c.setStrokeColor(SLATE)
    c.setLineWidth(0.5)
    c.line(sig_x, sig_y, sig_x + 120, sig_y)
    
    c.setFont('Helvetica', 9)
    c.setFillColor(SLATE)
    c.drawCentredString(sig_x + 60, sig_y - 15, "Authorized Signatory")
    
    c.setFont('Helvetica-Bold', 10)
    c.setFillColor(NAVY)
    c.drawCentredString(sig_x + 60, sig_y + 15, "Director")
    
    # === QR CODE ===
    qr_x = width - 120
    qr_y = height - 110
    qr_size = 70
    
    try:
        qr_buffer = generate_qr_code(verification_url)
        from reportlab.lib.utils import ImageReader
        qr_image = ImageReader(qr_buffer)
        c.drawImage(qr_image, qr_x, qr_y, width=qr_size, height=qr_size)
        
        # QR label
        c.setFont('Helvetica', 7)
        c.setFillColor(SLATE)
        c.drawCentredString(qr_x + qr_size/2, qr_y - 10, "Scan to Verify")
    except Exception as e:
        print(f"QR Error: {e}")
    
    # === FOOTER ===
    footer_y = 45
    c.setFont('Helvetica', 8)
    c.setFillColor(SLATE)
    c.drawCentredString(width / 2, footer_y, "This certificate remains the property of BAYAN Auditing & Conformity (BAC)")
    c.drawCentredString(width / 2, footer_y - 12, "Verification: www.bfrvc.sa | Tel: +966 55 123 4567")
    
    # Save
    c.save()
    
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    return pdf_bytes


def get_qr_code_base64(verification_url: str) -> str:
    """Generate QR code and return as base64 string for web display"""
    import base64
    qr_buffer = generate_qr_code(verification_url)
    qr_base64 = base64.b64encode(qr_buffer.getvalue()).decode('utf-8')
    return f"data:image/png;base64,{qr_base64}"


# For testing
if __name__ == "__main__":
    test_data = {
        'certificate_number': 'BAC-QMS-2026-0001',
        'organization_name': 'Sample Manufacturing Company',
        'organization_address': 'Industrial Area, Riyadh, Kingdom of Saudi Arabia',
        'standard': 'ISO 9001:2015',
        'scope': 'Design, Development, and Manufacturing of Industrial Equipment and Machinery',
        'initial_certification_date': '2024-01-15',
        'issue_date': '2026-01-15',
        'expiry_date': '2027-01-14',
        'verification_url': 'https://www.bfrvc.sa/verify/BAC-QMS-2026-0001'
    }
    
    pdf_bytes = generate_certificate_pdf(test_data)
    
    output_path = Path("/tmp/test_certificate.pdf")
    output_path.write_bytes(pdf_bytes)
    print(f"Generated certificate: {output_path}")
    print(f"Size: {len(pdf_bytes)} bytes")
