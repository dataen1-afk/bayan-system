"""
Certificate Data (BACF6-14) PDF Generator
Bilingual PDF with English and Arabic support
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, black, white
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pathlib import Path
import arabic_reshaper
from bidi.algorithm import get_display
import io
import base64

# Register Arabic fonts
FONTS_DIR = Path(__file__).parent / "fonts"
try:
    pdfmetrics.registerFont(TTFont('Amiri', str(FONTS_DIR / 'Amiri-Regular.ttf')))
    pdfmetrics.registerFont(TTFont('Amiri-Bold', str(FONTS_DIR / 'Amiri-Bold.ttf')))
except:
    pass

# Colors
PRIMARY_COLOR = HexColor('#1e3a5f')
SECONDARY_COLOR = HexColor('#2c5282')
LIGHT_GRAY = HexColor('#f7fafc')
BORDER_COLOR = HexColor('#e2e8f0')
TEXT_COLOR = HexColor('#2d3748')
SUCCESS_COLOR = HexColor('#38a169')


def reshape_arabic(text):
    """Reshape Arabic text for proper RTL display"""
    if not text:
        return ""
    try:
        reshaped = arabic_reshaper.reshape(str(text))
        return get_display(reshaped)
    except:
        return str(text)


def generate_certificate_data_pdf(data: dict) -> bytes:
    """Generate bilingual Certificate Data PDF"""
    
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    # Draw content
    draw_header(c, width, height, data)
    y = height - 5.5*cm
    
    y = draw_info_section(c, data, y, width)
    y = draw_scope_section(c, data, y, width)
    y = draw_company_data_section(c, data, y, width)
    y = draw_signature_section(c, data, y, width)
    
    draw_footer(c, width, data)
    
    c.save()
    buffer.seek(0)
    return buffer.getvalue()


def draw_header(c, width, height, data):
    """Draw document header with logo"""
    # Header background
    c.setFillColor(PRIMARY_COLOR)
    c.rect(0, height - 2.5*cm, width, 2.5*cm, fill=True, stroke=False)
    
    # Logo
    logo_path = Path(__file__).parent / "assets" / "bayan-logo.png"
    if logo_path.exists():
        try:
            c.drawImage(str(logo_path), 1.5*cm, height - 2.2*cm, width=3*cm, height=1.8*cm, preserveAspectRatio=True, mask='auto')
        except:
            pass
    
    # Company name
    c.setFillColor(white)
    c.setFont('Helvetica-Bold', 14)
    c.drawRightString(width - 1.5*cm, height - 1.2*cm, "BAYAN")
    
    c.setFont('Helvetica', 9)
    c.drawRightString(width - 1.5*cm, height - 1.7*cm, "Auditing & Conformity Assessment")
    
    c.setFont('Amiri', 9)
    c.drawRightString(width - 1.5*cm, height - 2.1*cm, reshape_arabic("بيان للتدقيق وتقييم المطابقة"))
    
    # Title
    y = height - 3.5*cm
    c.setFont('Helvetica-Bold', 16)
    c.setFillColor(PRIMARY_COLOR)
    c.drawString(2*cm, y, "Certificate Data")
    
    c.setFont('Amiri-Bold', 16)
    c.drawRightString(width - 2*cm, y, reshape_arabic("بيانات الشهادة"))
    
    # Subtitle
    y -= 0.6*cm
    c.setFont('Helvetica', 10)
    c.setFillColor(TEXT_COLOR)
    c.drawString(2*cm, y, "Confirmation of details for certificate printing")
    
    # Form number
    y -= 0.5*cm
    c.setFont('Helvetica', 9)
    c.setFillColor(HexColor('#718096'))
    c.drawString(2*cm, y, "BAC-F6-14")


def draw_info_section(c, data, y, width):
    """Draw the header information section"""
    
    y -= 0.5*cm
    
    # Background box
    c.setFillColor(LIGHT_GRAY)
    c.roundRect(1.5*cm, y - 3.5*cm, width - 3*cm, 3.5*cm, 5, fill=True, stroke=False)
    c.setStrokeColor(BORDER_COLOR)
    c.roundRect(1.5*cm, y - 3.5*cm, width - 3*cm, 3.5*cm, 5, fill=False, stroke=True)
    
    field_y = y - 0.5*cm
    
    # Row 1: Client Name
    c.setFont('Helvetica-Bold', 9)
    c.setFillColor(PRIMARY_COLOR)
    c.drawString(2*cm, field_y, "CLIENT NAME:")
    c.setFont('Helvetica', 9)
    c.setFillColor(TEXT_COLOR)
    c.drawString(5.5*cm, field_y, data.get("client_name", "—"))
    
    c.setFont('Amiri-Bold', 9)
    c.setFillColor(PRIMARY_COLOR)
    c.drawRightString(width - 2*cm, field_y, reshape_arabic(":اسم العميل"))
    
    # Row 2: Standard(s) & Lead Auditor
    field_y -= 0.7*cm
    c.setFont('Helvetica-Bold', 9)
    c.setFillColor(PRIMARY_COLOR)
    c.drawString(2*cm, field_y, "STANDARD(s):")
    c.setFont('Helvetica', 9)
    c.setFillColor(TEXT_COLOR)
    standards = data.get("standards", [])
    c.drawString(5.5*cm, field_y, ", ".join(standards) if standards else "—")
    
    c.setFont('Helvetica-Bold', 9)
    c.setFillColor(PRIMARY_COLOR)
    c.drawString(11*cm, field_y, "LEAD AUDITOR:")
    c.setFont('Helvetica', 9)
    c.setFillColor(TEXT_COLOR)
    c.drawString(14*cm, field_y, data.get("lead_auditor", "—"))
    
    # Row 3: Type of Audit & Date
    field_y -= 0.7*cm
    c.setFont('Helvetica-Bold', 9)
    c.setFillColor(PRIMARY_COLOR)
    c.drawString(2*cm, field_y, "TYPE OF AUDIT:")
    c.setFont('Helvetica', 9)
    c.setFillColor(TEXT_COLOR)
    c.drawString(5.5*cm, field_y, data.get("audit_type", "—"))
    
    c.setFont('Helvetica-Bold', 9)
    c.setFillColor(PRIMARY_COLOR)
    c.drawString(11*cm, field_y, "DATE:")
    c.setFont('Helvetica', 9)
    c.setFillColor(TEXT_COLOR)
    c.drawString(14*cm, field_y, data.get("audit_date", "—"))
    
    # Row 4: EA Code & Technical Category
    field_y -= 0.7*cm
    c.setFont('Helvetica-Bold', 9)
    c.setFillColor(PRIMARY_COLOR)
    c.drawString(2*cm, field_y, "EA Code/Technical Category:")
    c.setFont('Helvetica', 9)
    c.setFillColor(TEXT_COLOR)
    ea_code = data.get("ea_code", "")
    tech_cat = data.get("technical_category", "")
    c.drawString(7*cm, field_y, f"{ea_code} / {tech_cat}" if ea_code or tech_cat else "—")
    
    return y - 4.2*cm


def draw_scope_section(c, data, y, width):
    """Draw the certification scope section"""
    
    # Section header
    c.setFillColor(SECONDARY_COLOR)
    c.roundRect(1.5*cm, y - 0.7*cm, width - 3*cm, 0.7*cm, 3, fill=True, stroke=False)
    
    c.setFillColor(white)
    c.setFont('Helvetica-Bold', 10)
    c.drawString(2*cm, y - 0.5*cm, "AGREED CERTIFICATION SCOPE")
    
    c.setFont('Amiri-Bold', 10)
    c.drawRightString(width - 2*cm, y - 0.5*cm, reshape_arabic("نطاق الشهادة المتفق عليه"))
    
    y -= 1.2*cm
    
    # Scope content box
    scope_height = 2*cm
    c.setFillColor(white)
    c.setStrokeColor(BORDER_COLOR)
    c.roundRect(1.5*cm, y - scope_height, width - 3*cm, scope_height, 3, fill=True, stroke=True)
    
    # English scope
    scope_en = data.get("agreed_certification_scope", "") or data.get("certification_scope_english", "")
    if scope_en:
        c.setFont('Helvetica', 9)
        c.setFillColor(TEXT_COLOR)
        # Simple text wrapping
        words = scope_en.split()
        lines = []
        current_line = ""
        for word in words:
            test_line = current_line + " " + word if current_line else word
            if c.stringWidth(test_line, 'Helvetica', 9) < width - 5*cm:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        
        text_y = y - 0.5*cm
        for line in lines[:3]:  # Max 3 lines
            c.drawString(2*cm, text_y, line)
            text_y -= 0.4*cm
    
    return y - scope_height - 0.5*cm


def draw_company_data_section(c, data, y, width):
    """Draw company data sections (Local Language and English)"""
    
    # Local Language (Arabic) Section
    c.setFillColor(SECONDARY_COLOR)
    c.roundRect(1.5*cm, y - 0.7*cm, width - 3*cm, 0.7*cm, 3, fill=True, stroke=False)
    
    c.setFillColor(white)
    c.setFont('Helvetica-Bold', 10)
    c.drawString(2*cm, y - 0.5*cm, "COMPANY DATA (LOCAL LANGUAGE - ARABIC)")
    
    y -= 1.2*cm
    
    # Local language content box
    box_height = 2.5*cm
    c.setFillColor(white)
    c.setStrokeColor(BORDER_COLOR)
    c.roundRect(1.5*cm, y - box_height, width - 3*cm, box_height, 3, fill=True, stroke=True)
    
    # Company data in Arabic
    company_local = data.get("company_data_local", "")
    scope_local = data.get("certification_scope_local", "")
    
    text_y = y - 0.5*cm
    c.setFont('Helvetica-Bold', 8)
    c.setFillColor(PRIMARY_COLOR)
    c.drawString(2*cm, text_y, "Company Data:")
    c.setFont('Amiri', 9)
    c.setFillColor(TEXT_COLOR)
    if company_local:
        c.drawRightString(width - 2*cm, text_y, reshape_arabic(company_local[:60]))
    
    text_y -= 0.8*cm
    c.setFont('Helvetica-Bold', 8)
    c.setFillColor(PRIMARY_COLOR)
    c.drawString(2*cm, text_y, "Certification Scope:")
    c.setFont('Amiri', 9)
    c.setFillColor(TEXT_COLOR)
    if scope_local:
        c.drawRightString(width - 2*cm, text_y, reshape_arabic(scope_local[:60]))
    
    y -= box_height + 0.5*cm
    
    # English Section
    c.setFillColor(SECONDARY_COLOR)
    c.roundRect(1.5*cm, y - 0.7*cm, width - 3*cm, 0.7*cm, 3, fill=True, stroke=False)
    
    c.setFillColor(white)
    c.setFont('Helvetica-Bold', 10)
    c.drawString(2*cm, y - 0.5*cm, "COMPANY DATA (ENGLISH)")
    
    y -= 1.2*cm
    
    # English content box
    c.setFillColor(white)
    c.setStrokeColor(BORDER_COLOR)
    c.roundRect(1.5*cm, y - box_height, width - 3*cm, box_height, 3, fill=True, stroke=True)
    
    # Company data in English
    company_en = data.get("company_data_english", "")
    scope_en = data.get("certification_scope_english", "")
    
    text_y = y - 0.5*cm
    c.setFont('Helvetica-Bold', 8)
    c.setFillColor(PRIMARY_COLOR)
    c.drawString(2*cm, text_y, "Company Data:")
    c.setFont('Helvetica', 9)
    c.setFillColor(TEXT_COLOR)
    c.drawString(5*cm, text_y, company_en[:70] if company_en else "—")
    
    text_y -= 0.8*cm
    c.setFont('Helvetica-Bold', 8)
    c.setFillColor(PRIMARY_COLOR)
    c.drawString(2*cm, text_y, "Certification Scope:")
    c.setFont('Helvetica', 9)
    c.setFillColor(TEXT_COLOR)
    c.drawString(5*cm, text_y, scope_en[:70] if scope_en else "—")
    
    return y - box_height - 0.5*cm


def draw_signature_section(c, data, y, width):
    """Draw client signature section"""
    
    # Instruction text
    c.setFont('Helvetica-Oblique', 8)
    c.setFillColor(HexColor('#718096'))
    c.drawString(2*cm, y, "Please complete in case of CA, RA audits and only where applicable e.g. extension, special audit etc")
    
    y -= 1*cm
    
    # Signature box
    c.setStrokeColor(BORDER_COLOR)
    c.roundRect(1.5*cm, y - 2.5*cm, width - 3*cm, 2.5*cm, 3, fill=False, stroke=True)
    
    # Client signature area
    c.setFont('Helvetica-Bold', 9)
    c.setFillColor(PRIMARY_COLOR)
    c.drawString(2*cm, y - 0.5*cm, "Client signature:")
    
    c.setFont('Amiri-Bold', 9)
    c.drawRightString(width - 2*cm, y - 0.5*cm, reshape_arabic(":توقيع العميل"))
    
    # Stamp area
    c.setFont('Helvetica-Bold', 9)
    c.setFillColor(PRIMARY_COLOR)
    c.drawString(8*cm, y - 0.5*cm, "Stamp:")
    
    # Date
    c.setFont('Helvetica-Bold', 9)
    c.drawString(14*cm, y - 0.5*cm, "Date:")
    c.setFont('Helvetica', 9)
    c.setFillColor(TEXT_COLOR)
    c.drawString(15.5*cm, y - 0.5*cm, data.get("client_signature_date", ""))
    
    # Draw signature image if exists
    sig_data = data.get("client_signature", "")
    if sig_data and sig_data.startswith("data:"):
        try:
            # Extract base64 data
            base64_data = sig_data.split(",")[1] if "," in sig_data else sig_data
            sig_bytes = base64.b64decode(base64_data)
            
            # Save temporarily and draw
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
                f.write(sig_bytes)
                sig_path = f.name
            
            c.drawImage(sig_path, 2*cm, y - 2.2*cm, width=4*cm, height=1.5*cm, preserveAspectRatio=True, mask='auto')
        except:
            pass
    
    # Confirmed status
    if data.get("client_confirmed"):
        c.setFillColor(SUCCESS_COLOR)
        c.setFont('Helvetica-Bold', 10)
        c.drawString(2*cm, y - 2.8*cm, "✓ CONFIRMED BY CLIENT")
    
    return y - 3*cm


def draw_footer(c, width, data):
    """Draw document footer"""
    c.setFont('Helvetica', 8)
    c.setFillColor(HexColor('#718096'))
    c.drawString(1.5*cm, 1.5*cm, "BAC-F6-14 | Certificate Data")
    c.drawRightString(width - 1.5*cm, 1.5*cm, "BAYAN for Verification and Conformity Assessment")
    
    # Footer line
    c.setStrokeColor(BORDER_COLOR)
    c.line(1.5*cm, 2*cm, width - 1.5*cm, 2*cm)


if __name__ == "__main__":
    # Test PDF generation
    test_data = {
        "id": "test-001",
        "client_name": "Test Manufacturing Co.",
        "standards": ["ISO 9001:2015", "ISO 14001:2015"],
        "lead_auditor": "Ahmed Al-Rashid",
        "audit_type": "CA - Certification Audit",
        "audit_date": "2026-02-17",
        "ea_code": "EA 17",
        "technical_category": "Manufacturing",
        "agreed_certification_scope": "Design, development, and manufacturing of industrial equipment and components",
        "company_data_local": "شركة التصنيع الاختبارية - الرياض، المملكة العربية السعودية",
        "certification_scope_local": "تصميم وتطوير وتصنيع المعدات والمكونات الصناعية",
        "company_data_english": "Test Manufacturing Co. - Riyadh, Saudi Arabia",
        "certification_scope_english": "Design, development, and manufacturing of industrial equipment",
        "client_signature_date": "2026-02-17",
        "client_confirmed": True
    }
    
    pdf_bytes = generate_certificate_data_pdf(test_data)
    with open("/tmp/cert_data_test.pdf", "wb") as f:
        f.write(pdf_bytes)
    print(f"PDF generated: /tmp/cert_data_test.pdf ({len(pdf_bytes)} bytes)")
