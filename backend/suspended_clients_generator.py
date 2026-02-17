"""
Suspended Clients Registry (BAC-F6-20) PDF Generator
Generates bilingual (Arabic/English) PDF for suspended client records.
"""
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor, black, white
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import arabic_reshaper
from bidi.algorithm import get_display
from pathlib import Path

# Register Arabic font
FONTS_DIR = Path(__file__).parent / "fonts"
try:
    pdfmetrics.registerFont(TTFont('Amiri', str(FONTS_DIR / 'Amiri-Regular.ttf')))
    pdfmetrics.registerFont(TTFont('Amiri-Bold', str(FONTS_DIR / 'Amiri-Bold.ttf')))
except:
    pass

def reshape_arabic(text):
    """Reshape Arabic text for proper display"""
    if not text:
        return ""
    try:
        reshaped = arabic_reshaper.reshape(str(text))
        return get_display(reshaped)
    except:
        return str(text)

# Colors
BAYAN_NAVY = HexColor("#1a4d7c")
BAYAN_RED = HexColor("#c0392b")
BAYAN_GOLD = HexColor("#d4af37")
LIGHT_RED = HexColor("#fce4e4")
BORDER_GRAY = HexColor("#cccccc")

def generate_suspended_client_pdf(client: dict, output_path: str):
    """Generate PDF for a single suspended client record"""
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4
    
    # Header
    y = height - 2*cm
    
    # Company logo area with red theme for suspended
    c.setFillColor(BAYAN_RED)
    c.rect(1*cm, y - 1.5*cm, width - 2*cm, 2*cm, fill=True, stroke=False)
    
    # Company name
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(2*cm, y - 0.5*cm, "BAYAN AUDITING & CONFORMITY")
    
    # Arabic company name
    try:
        c.setFont("Amiri-Bold", 14)
        arabic_name = reshape_arabic("بيان للتدقيق والمطابقة")
        c.drawRightString(width - 2*cm, y - 0.5*cm, arabic_name)
    except:
        pass
    
    # Form title
    y -= 2.5*cm
    c.setFillColor(LIGHT_RED)
    c.rect(1*cm, y - 1*cm, width - 2*cm, 1.2*cm, fill=True, stroke=False)
    c.setStrokeColor(BAYAN_RED)
    c.setLineWidth(2)
    c.rect(1*cm, y - 1*cm, width - 2*cm, 1.2*cm, fill=False, stroke=True)
    
    c.setFillColor(BAYAN_RED)
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width/2, y - 0.6*cm, "SUSPENDED CLIENT RECORD - BAC-F6-20")
    
    # Status Banner
    y -= 2*cm
    status = client.get('status', 'suspended').upper()
    status_colors = {
        'SUSPENDED': BAYAN_RED,
        'REINSTATED': HexColor("#27ae60"),
        'WITHDRAWN': HexColor("#7f8c8d")
    }
    status_color = status_colors.get(status, BAYAN_RED)
    
    # Draw large status badge
    badge_width = 4*cm
    c.setFillColor(status_color)
    c.roundRect(width/2 - badge_width/2, y - 0.6*cm, badge_width, 1*cm, 0.3*cm, fill=True, stroke=False)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width/2, y - 0.2*cm, status)
    
    # Client Information Section
    y -= 2.2*cm
    c.setFillColor(BAYAN_RED)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(1.5*cm, y, "CLIENT INFORMATION")
    try:
        c.setFont("Amiri-Bold", 12)
        c.drawRightString(width - 1.5*cm, y, reshape_arabic("معلومات العميل"))
    except:
        pass
    
    y -= 0.5*cm
    c.setStrokeColor(BAYAN_RED)
    c.setLineWidth(2)
    c.line(1.5*cm, y, width - 1.5*cm, y)
    
    # Client details
    y -= 1*cm
    c.setFont("Helvetica", 10)
    c.setFillColor(black)
    
    fields = [
        ("Sr. No.", str(client.get('serial_number', '-')), "الرقم التسلسلي"),
        ("Client ID", client.get('client_id', '-'), "رقم العميل"),
        ("Client Name", client.get('client_name', '-'), "اسم العميل"),
        ("Client Name (Arabic)", client.get('client_name_ar', '-'), "اسم العميل (عربي)"),
        ("Address", client.get('address', '-'), "العنوان"),
    ]
    
    for label_en, value, label_ar in fields:
        c.setFont("Helvetica-Bold", 10)
        c.drawString(1.5*cm, y, f"{label_en}:")
        c.setFont("Helvetica", 10)
        c.drawString(5*cm, y, str(value) if value else '-')
        try:
            c.setFont("Amiri", 10)
            c.drawRightString(width - 1.5*cm, y, reshape_arabic(label_ar))
        except:
            pass
        y -= 0.6*cm
    
    # Suspension Details Section
    y -= 0.8*cm
    c.setFillColor(BAYAN_RED)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(1.5*cm, y, "SUSPENSION DETAILS")
    try:
        c.setFont("Amiri-Bold", 12)
        c.drawRightString(width - 1.5*cm, y, reshape_arabic("تفاصيل التعليق"))
    except:
        pass
    
    y -= 0.5*cm
    c.setStrokeColor(BAYAN_RED)
    c.line(1.5*cm, y, width - 1.5*cm, y)
    
    y -= 1*cm
    c.setFillColor(black)
    
    suspension_fields = [
        ("Registration Date", client.get('registration_date', '-'), "تاريخ التسجيل"),
        ("Suspended On", client.get('suspended_on', '-'), "تاريخ التعليق"),
        ("Reason for Suspension", client.get('reason_for_suspension', '-')[:50] + ('...' if len(client.get('reason_for_suspension', '')) > 50 else ''), "سبب التعليق"),
        ("Future Action", client.get('future_action', '-').replace('_', ' ').title(), "الإجراء المستقبلي"),
    ]
    
    for label_en, value, label_ar in suspension_fields:
        c.setFont("Helvetica-Bold", 10)
        c.drawString(1.5*cm, y, f"{label_en}:")
        c.setFont("Helvetica", 10)
        c.drawString(5.5*cm, y, str(value) if value else '-')
        try:
            c.setFont("Amiri", 10)
            c.drawRightString(width - 1.5*cm, y, reshape_arabic(label_ar))
        except:
            pass
        y -= 0.6*cm
    
    # Remarks section
    y -= 0.5*cm
    c.setFont("Helvetica-Bold", 10)
    c.drawString(1.5*cm, y, "Remarks:")
    y -= 0.5*cm
    c.setFont("Helvetica", 10)
    remarks = client.get('remarks', '') or 'No remarks'
    # Handle multi-line remarks
    words = remarks.split()
    line = ""
    for word in words:
        if len(line + " " + word) < 80:
            line = line + " " + word if line else word
        else:
            c.drawString(1.5*cm, y, line)
            y -= 0.5*cm
            line = word
    if line:
        c.drawString(1.5*cm, y, line)
    
    # If reinstated or withdrawn, show those details
    if client.get('status') in ['reinstated', 'withdrawn']:
        y -= 1.5*cm
        c.setFillColor(HexColor("#27ae60") if client.get('status') == 'reinstated' else HexColor("#7f8c8d"))
        c.setFont("Helvetica-Bold", 12)
        c.drawString(1.5*cm, y, "RESOLUTION DETAILS")
        
        y -= 0.5*cm
        c.setStrokeColor(HexColor("#27ae60") if client.get('status') == 'reinstated' else HexColor("#7f8c8d"))
        c.line(1.5*cm, y, width - 1.5*cm, y)
        
        y -= 1*cm
        c.setFillColor(black)
        
        c.setFont("Helvetica-Bold", 10)
        c.drawString(1.5*cm, y, "Lifted On:")
        c.setFont("Helvetica", 10)
        c.drawString(5*cm, y, client.get('lifted_on', '-'))
        
        y -= 0.6*cm
        c.setFont("Helvetica-Bold", 10)
        c.drawString(1.5*cm, y, "Resolution:")
        c.setFont("Helvetica", 10)
        c.drawString(5*cm, y, client.get('lifted_reason', '-')[:60])
    
    # Footer
    y = 2*cm
    c.setStrokeColor(BAYAN_RED)
    c.setLineWidth(1)
    c.line(1.5*cm, y, width - 1.5*cm, y)
    
    c.setFont("Helvetica", 8)
    c.setFillColor(HexColor("#666666"))
    c.drawString(1.5*cm, y - 0.5*cm, "BAC-F6-20 - Suspended Client Record")
    c.drawRightString(width - 1.5*cm, y - 0.5*cm, "Generated by Bayan Certification Management System")
    
    c.save()
