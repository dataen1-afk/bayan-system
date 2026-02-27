"""
Auditor Notes (BACF6-12) PDF Generator
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
import os

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


def reshape_arabic(text):
    """Reshape Arabic text for proper RTL display"""
    if not text:
        return ""
    try:
        reshaped = arabic_reshaper.reshape(str(text))
        return get_display(reshaped)
    except:
        return str(text)


def generate_auditor_notes_pdf(data: dict) -> str:
    """Generate bilingual Auditor Notes PDF"""
    
    # Create output directory
    output_dir = Path(__file__).parent / "contracts"
    output_dir.mkdir(exist_ok=True)
    
    filename = f"auditor_notes_{data.get('id', 'unknown')}.pdf"
    filepath = output_dir / filename
    
    # Create PDF
    c = canvas.Canvas(str(filepath), pagesize=A4)
    width, height = A4
    
    # Draw header with logo
    draw_header(c, width, height)
    
    y = height - 4*cm
    
    # Title
    c.setFont('Helvetica-Bold', 16)
    c.setFillColor(PRIMARY_COLOR)
    c.drawString(2*cm, y, "Auditor Notes")
    
    c.setFont('Amiri-Bold', 16)
    c.drawRightString(width - 2*cm, y, reshape_arabic("ملاحظات المدقق"))
    
    y -= 0.8*cm
    
    # Form number
    c.setFont('Helvetica', 10)
    c.setFillColor(TEXT_COLOR)
    c.drawString(2*cm, y, "BAC-F6-12")
    
    y -= 1.5*cm
    
    # Draw form fields
    y = draw_form_fields(c, data, y, width)
    
    # Draw notes section
    y = draw_notes_section(c, data, y, width, height)
    
    # Draw footer
    draw_footer(c, width)
    
    c.save()
    return str(filepath)


def draw_header(c, width, height):
    """Draw official BAC header"""
    logo_path = Path(__file__).parent / "assets" / "bayan-logo.png"
    
    # Logo on top-left
    logo_x = 40
    logo_y = height - 75
    
    if logo_path.exists():
        try:
            c.drawImage(str(logo_path), logo_x, logo_y, width=60, height=55, 
                       preserveAspectRatio=True, mask='auto')
        except:
            pass
    
    # Company name next to logo
    name_x = logo_x + 70
    name_y = height - 30
    c.setFillColor(PRIMARY_COLOR)
    c.setFont('Amiri-Bold', 13)
    c.drawRightString(name_x + 130, name_y, reshape_arabic("بيان للتحقق والمطابقة"))
    c.setFont('Helvetica-Bold', 9)
    c.drawString(name_x, name_y - 15, "BAYAN AUDITING & CONFORMITY")
    
    # Title centered
    title_y = height - 95
    c.setFont('Helvetica-Bold', 16)
    c.setFillColor(PRIMARY_COLOR)
    c.drawCentredString(width / 2, title_y, "AUDITOR NOTES")
    c.setFont('Amiri-Bold', 14)
    c.drawCentredString(width / 2, title_y - 20, reshape_arabic("ملاحظات المدقق"))
    
    # Form reference
    c.setFont('Helvetica', 9)
    c.setFillColor(TEXT_COLOR)
    c.drawRightString(width - 40, height - 25, "BAC-F6-12")


def draw_form_fields(c, data, y, width):
    """Draw the form fields section"""
    
    # Field definitions: (English label, Arabic label, value key)
    fields = [
        ("CLIENT NAME", "اسم العميل", "client_name"),
        ("LOCATION", "الموقع", "location"),
        ("STANDARD(s)", "المعايير", "standards"),
        ("AUDITOR", "المدقق", "auditor_name"),
        ("TYPE OF AUDIT", "نوع التدقيق", "audit_type"),
        ("AUDIT DATE", "تاريخ التدقيق", "audit_date"),
        ("Department", "القسم", "department"),
    ]
    
    # Background for fields
    c.setFillColor(LIGHT_GRAY)
    c.roundRect(1.5*cm, y - 6*cm, width - 3*cm, 6*cm, 5, fill=True, stroke=False)
    
    c.setStrokeColor(BORDER_COLOR)
    c.roundRect(1.5*cm, y - 6*cm, width - 3*cm, 6*cm, 5, fill=False, stroke=True)
    
    field_y = y - 0.6*cm
    
    for eng_label, ar_label, key in fields:
        # Get value
        value = data.get(key, "")
        if isinstance(value, list):
            value = ", ".join(value)
        
        # English label and value (left side)
        c.setFont('Helvetica-Bold', 10)
        c.setFillColor(PRIMARY_COLOR)
        c.drawString(2*cm, field_y, f"{eng_label}:")
        
        c.setFont('Helvetica', 10)
        c.setFillColor(TEXT_COLOR)
        c.drawString(6*cm, field_y, str(value) if value else "—")
        
        # Arabic label (right side)
        c.setFont('Amiri-Bold', 10)
        c.setFillColor(PRIMARY_COLOR)
        c.drawRightString(width - 2*cm, field_y, reshape_arabic(f":{ar_label}"))
        
        field_y -= 0.8*cm
    
    return y - 7*cm


def draw_notes_section(c, data, y, width, height):
    """Draw the notes section"""
    
    # Section header
    c.setFillColor(SECONDARY_COLOR)
    c.roundRect(1.5*cm, y - 0.8*cm, width - 3*cm, 0.8*cm, 3, fill=True, stroke=False)
    
    c.setFillColor(white)
    c.setFont('Helvetica-Bold', 11)
    c.drawString(2*cm, y - 0.6*cm, "Auditor Notes")
    
    c.setFont('Amiri-Bold', 11)
    c.drawRightString(width - 2*cm, y - 0.6*cm, reshape_arabic("ملاحظات المدقق"))
    
    y -= 1.2*cm
    
    # Notes content area
    notes = data.get("notes", "")
    notes_ar = data.get("notes_ar", "")
    
    # Calculate available height (leave space for footer)
    available_height = y - 3*cm
    
    # Notes box
    c.setFillColor(white)
    c.setStrokeColor(BORDER_COLOR)
    c.roundRect(1.5*cm, 3*cm, width - 3*cm, available_height, 5, fill=True, stroke=True)
    
    # Draw notes text
    text_y = y - 0.8*cm
    
    if notes:
        c.setFont('Helvetica', 10)
        c.setFillColor(TEXT_COLOR)
        
        # Split notes into lines
        lines = notes.split('\n')
        for line in lines:
            # Word wrap long lines
            words = line.split()
            current_line = ""
            for word in words:
                test_line = current_line + " " + word if current_line else word
                if c.stringWidth(test_line, 'Helvetica', 10) < width - 5*cm:
                    current_line = test_line
                else:
                    if current_line:
                        c.drawString(2*cm, text_y, current_line)
                        text_y -= 0.5*cm
                    current_line = word
                
                if text_y < 4*cm:
                    # Need new page
                    c.showPage()
                    draw_header(c, width, height)
                    text_y = height - 5*cm
                    c.setFont('Helvetica', 10)
                    c.setFillColor(TEXT_COLOR)
            
            if current_line:
                c.drawString(2*cm, text_y, current_line)
                text_y -= 0.5*cm
    
    # Arabic notes (if any)
    if notes_ar:
        text_y -= 0.5*cm
        c.setFont('Amiri', 10)
        c.setFillColor(TEXT_COLOR)
        
        lines = notes_ar.split('\n')
        for line in lines:
            if text_y < 4*cm:
                break
            reshaped = reshape_arabic(line)
            c.drawRightString(width - 2*cm, text_y, reshaped)
            text_y -= 0.5*cm
    
    return text_y


def draw_footer(c, width):
    """Draw official BAC footer"""
    footer_y = 55
    
    c.setStrokeColor(PRIMARY_COLOR)
    c.setLineWidth(1)
    c.line(40, footer_y + 25, width - 40, footer_y + 25)
    
    try:
        qr = qrcode.QRCode(version=1, box_size=10, border=2)
        qr.add_data("https://www.bfrvc.sa")
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_buffer = BytesIO()
        qr_img.save(qr_buffer, format='PNG')
        qr_buffer.seek(0)
        from reportlab.lib.utils import ImageReader
        c.drawImage(ImageReader(qr_buffer), 45, footer_y - 20, width=45, height=45)
    except:
        pass
    
    info_x = 100
    info_y = footer_y + 12
    c.setFont('Helvetica', 8)
    c.setFillColor(TEXT_COLOR)
    c.drawString(info_x, info_y, "Tel: +966 55 123 4567")
    c.drawString(info_x, info_y - 11, "Web: www.bfrvc.sa")
    
    c.setFont('Helvetica-Bold', 8)
    c.drawRightString(width - 45, info_y, "Director")
    c.setFont('Helvetica', 8)
    c.drawRightString(width - 45, info_y - 11, "BAYAN AUDITING & CONFORMITY (BAC)")


if __name__ == "__main__":
    # Test PDF generation
    test_data = {
        "id": "test-001",
        "client_name": "Test Company LLC",
        "location": "Riyadh, Saudi Arabia",
        "standards": ["ISO 9001:2015", "ISO 14001:2015"],
        "auditor_name": "Ahmed Al-Rashid",
        "audit_type": "Stage 2",
        "audit_date": "2026-02-17",
        "department": "Quality Management",
        "notes": "This is a test note.\n\nThe audit was conducted successfully.\n\n- Finding 1: Documentation complete\n- Finding 2: Process controls adequate\n- Finding 3: Training records updated",
        "notes_ar": "هذه ملاحظة اختبارية"
    }
    
    pdf_path = generate_auditor_notes_pdf(test_data)
    print(f"PDF generated: {pdf_path}")
