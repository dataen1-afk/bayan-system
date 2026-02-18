"""
Certified Clients Registry (BAC-F6-19) PDF Generator
Generates bilingual (Arabic/English) PDF for certified client records.
"""
from reportlab.lib.pagesizes import A4, landscape
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
BAYAN_GOLD = HexColor("#d4af37")
LIGHT_GRAY = HexColor("#f5f5f5")
BORDER_GRAY = HexColor("#cccccc")

def generate_certified_client_pdf(client: dict, output_path: str):
    """Generate PDF for a single certified client record"""
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4
    
    # Header
    y = height - 2*cm
    
    # Company logo area
    c.setFillColor(BAYAN_NAVY)
    c.rect(1*cm, y - 1.5*cm, width - 2*cm, 2*cm, fill=True, stroke=False)
    
    # Company name
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(2*cm, y - 0.5*cm, "BAYAN AUDITING & CONFORMITY")
    
    # Arabic company name
    try:
        c.setFont("Amiri-Bold", 14)
        arabic_name = reshape_arabic("بيان للتحقق والمطابقة")
        c.drawRightString(width - 2*cm, y - 0.5*cm, arabic_name)
    except:
        pass
    
    # Form title
    y -= 2.5*cm
    c.setFillColor(BAYAN_GOLD)
    c.rect(1*cm, y - 1*cm, width - 2*cm, 1.2*cm, fill=True, stroke=False)
    
    c.setFillColor(BAYAN_NAVY)
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width/2, y - 0.6*cm, "CERTIFIED CLIENT RECORD - BAC-F6-19")
    
    # Certificate Number Banner
    y -= 2*cm
    c.setFillColor(BAYAN_NAVY)
    c.setFont("Helvetica-Bold", 18)
    cert_no = client.get('certificate_number', 'N/A')
    c.drawCentredString(width/2, y, f"Certificate No: {cert_no}")
    
    # Status Badge
    y -= 1*cm
    status = client.get('status', 'active').upper()
    status_colors = {
        'ACTIVE': HexColor("#22c55e"),
        'SUSPENDED': HexColor("#f59e0b"),
        'WITHDRAWN': HexColor("#ef4444"),
        'EXPIRED': HexColor("#6b7280")
    }
    status_color = status_colors.get(status, BAYAN_NAVY)
    
    # Draw status badge
    badge_width = 3*cm
    c.setFillColor(status_color)
    c.roundRect(width/2 - badge_width/2, y - 0.5*cm, badge_width, 0.8*cm, 0.2*cm, fill=True, stroke=False)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(width/2, y - 0.2*cm, status)
    
    # Client Information Section
    y -= 2*cm
    c.setFillColor(BAYAN_NAVY)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(1.5*cm, y, "CLIENT INFORMATION")
    try:
        c.setFont("Amiri-Bold", 12)
        c.drawRightString(width - 1.5*cm, y, reshape_arabic("معلومات العميل"))
    except:
        pass
    
    y -= 0.5*cm
    c.setStrokeColor(BAYAN_NAVY)
    c.setLineWidth(2)
    c.line(1.5*cm, y, width - 1.5*cm, y)
    
    # Client details table
    y -= 1*cm
    c.setFont("Helvetica", 10)
    c.setFillColor(black)
    
    fields = [
        ("S.No.", str(client.get('serial_number', '-')), "الرقم التسلسلي"),
        ("Client Name", client.get('client_name', '-'), "اسم العميل"),
        ("Client Name (Arabic)", client.get('client_name_ar', '-'), "اسم العميل (عربي)"),
        ("Address", client.get('address', '-'), "العنوان"),
        ("Contact Person", client.get('contact_person', '-'), "مسؤول الاتصال"),
        ("Contact Number", client.get('contact_number', '-'), "رقم الاتصال"),
    ]
    
    for label_en, value, label_ar in fields:
        # Label
        c.setFont("Helvetica-Bold", 10)
        c.drawString(1.5*cm, y, f"{label_en}:")
        
        # Value
        c.setFont("Helvetica", 10)
        c.drawString(5*cm, y, str(value) if value else '-')
        
        # Arabic label
        try:
            c.setFont("Amiri", 10)
            c.drawRightString(width - 1.5*cm, y, reshape_arabic(label_ar))
        except:
            pass
        
        y -= 0.6*cm
    
    # Certification Details Section
    y -= 0.8*cm
    c.setFillColor(BAYAN_NAVY)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(1.5*cm, y, "CERTIFICATION DETAILS")
    try:
        c.setFont("Amiri-Bold", 12)
        c.drawRightString(width - 1.5*cm, y, reshape_arabic("تفاصيل الشهادة"))
    except:
        pass
    
    y -= 0.5*cm
    c.setStrokeColor(BAYAN_NAVY)
    c.line(1.5*cm, y, width - 1.5*cm, y)
    
    y -= 1*cm
    c.setFillColor(black)
    
    cert_fields = [
        ("Scope", client.get('scope', '-'), "نطاق العمل"),
        ("Accreditation", ', '.join(client.get('accreditation', [])) or '-', "الاعتماد"),
        ("EA Code/Food Category", client.get('ea_code', '-'), "رمز EA / فئة الغذاء"),
    ]
    
    for label_en, value, label_ar in cert_fields:
        c.setFont("Helvetica-Bold", 10)
        c.drawString(1.5*cm, y, f"{label_en}:")
        c.setFont("Helvetica", 10)
        # Handle long text
        if len(str(value)) > 60:
            value = str(value)[:60] + "..."
        c.drawString(5*cm, y, str(value) if value else '-')
        try:
            c.setFont("Amiri", 10)
            c.drawRightString(width - 1.5*cm, y, reshape_arabic(label_ar))
        except:
            pass
        y -= 0.6*cm
    
    # Important Dates Section
    y -= 0.8*cm
    c.setFillColor(BAYAN_NAVY)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(1.5*cm, y, "IMPORTANT DATES")
    try:
        c.setFont("Amiri-Bold", 12)
        c.drawRightString(width - 1.5*cm, y, reshape_arabic("التواريخ المهمة"))
    except:
        pass
    
    y -= 0.5*cm
    c.setStrokeColor(BAYAN_NAVY)
    c.line(1.5*cm, y, width - 1.5*cm, y)
    
    # Dates table
    y -= 1*cm
    c.setFillColor(black)
    
    # Draw dates in a grid
    date_fields = [
        ("Issue Date", client.get('issue_date', '-'), "تاريخ الإصدار"),
        ("Expiry Date", client.get('expiry_date', '-'), "تاريخ الانتهاء"),
        ("Surveillance 1", client.get('surveillance_1_date', '-'), "المراقبة الأولى"),
        ("Surveillance 2", client.get('surveillance_2_date', '-'), "المراقبة الثانية"),
        ("Recertification", client.get('recertification_date', '-'), "إعادة الاعتماد"),
    ]
    
    col_width = (width - 3*cm) / 2
    row = 0
    for i, (label_en, value, label_ar) in enumerate(date_fields):
        col = i % 2
        if col == 0 and i > 0:
            y -= 0.8*cm
        
        x = 1.5*cm + col * col_width
        
        c.setFont("Helvetica-Bold", 10)
        c.drawString(x, y, f"{label_en}:")
        c.setFont("Helvetica", 10)
        c.drawString(x + 3*cm, y, str(value) if value else '-')
    
    # Footer
    y = 2*cm
    c.setStrokeColor(BAYAN_NAVY)
    c.setLineWidth(1)
    c.line(1.5*cm, y, width - 1.5*cm, y)
    
    c.setFont("Helvetica", 8)
    c.setFillColor(HexColor("#666666"))
    c.drawString(1.5*cm, y - 0.5*cm, "BAC-F6-19 - Certified Client Record")
    c.drawRightString(width - 1.5*cm, y - 0.5*cm, f"Generated by Bayan Certification Management System")
    
    c.save()


def generate_certified_clients_list_pdf(clients: list, output_path: str):
    """Generate PDF for the complete certified clients registry list"""
    c = canvas.Canvas(output_path, pagesize=landscape(A4))
    width, height = landscape(A4)
    
    page_num = 1
    
    def draw_header():
        nonlocal page_num
        y = height - 1.5*cm
        
        # Company header
        c.setFillColor(BAYAN_NAVY)
        c.rect(1*cm, y - 1*cm, width - 2*cm, 1.5*cm, fill=True, stroke=False)
        
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(2*cm, y - 0.5*cm, "BAYAN AUDITING & CONFORMITY")
        
        try:
            c.setFont("Amiri-Bold", 12)
            c.drawRightString(width - 2*cm, y - 0.5*cm, reshape_arabic("بيان للتحقق والمطابقة"))
        except:
            pass
        
        # Title
        y -= 2*cm
        c.setFillColor(BAYAN_NAVY)
        c.setFont("Helvetica-Bold", 12)
        c.drawCentredString(width/2, y, "LIST OF CERTIFIED CLIENTS - BAC-F6-19")
        
        # Page number
        c.setFont("Helvetica", 9)
        c.drawRightString(width - 1.5*cm, y, f"Page {page_num}")
        
        return y - 1*cm
    
    def draw_table_header(y):
        # Column headers
        headers = [
            ("S.No.", 1.5),
            ("Client Name", 4),
            ("Address", 4),
            ("Contact", 2.5),
            ("Scope", 4),
            ("Standards", 3),
            ("EA Code", 1.5),
            ("Cert No.", 2.5),
            ("Issue", 2),
            ("Expiry", 2),
            ("Status", 1.5),
        ]
        
        c.setFillColor(BAYAN_GOLD)
        c.rect(1*cm, y - 0.6*cm, width - 2*cm, 0.8*cm, fill=True, stroke=False)
        
        c.setFillColor(BAYAN_NAVY)
        c.setFont("Helvetica-Bold", 8)
        
        x = 1.2*cm
        for header, col_width in headers:
            c.drawString(x, y - 0.4*cm, header)
            x += col_width * cm
        
        return y - 1*cm
    
    y = draw_header()
    y = draw_table_header(y)
    
    c.setFont("Helvetica", 7)
    c.setFillColor(black)
    
    for i, client in enumerate(clients):
        if y < 2*cm:
            c.showPage()
            page_num += 1
            y = draw_header()
            y = draw_table_header(y)
            c.setFont("Helvetica", 7)
            c.setFillColor(black)
        
        # Alternate row background
        if i % 2 == 0:
            c.setFillColor(LIGHT_GRAY)
            c.rect(1*cm, y - 0.4*cm, width - 2*cm, 0.6*cm, fill=True, stroke=False)
            c.setFillColor(black)
        
        x = 1.2*cm
        col_widths = [1.5, 4, 4, 2.5, 4, 3, 1.5, 2.5, 2, 2, 1.5]
        
        values = [
            str(client.get('serial_number', i + 1)),
            client.get('client_name', '')[:25],
            client.get('address', '')[:25],
            client.get('contact_person', '')[:15],
            client.get('scope', '')[:25],
            ', '.join(client.get('accreditation', []))[:20],
            client.get('ea_code', ''),
            client.get('certificate_number', ''),
            client.get('issue_date', ''),
            client.get('expiry_date', ''),
            client.get('status', 'active').upper()[:8],
        ]
        
        for val, col_width in zip(values, col_widths):
            c.drawString(x, y - 0.2*cm, str(val) if val else '-')
            x += col_width * cm
        
        y -= 0.6*cm
    
    # Footer
    c.setFont("Helvetica", 8)
    c.setFillColor(HexColor("#666666"))
    c.drawString(1.5*cm, 1*cm, f"Total Clients: {len(clients)}")
    c.drawRightString(width - 1.5*cm, 1*cm, "BAC-F6-19 - Generated by Bayan Certification Management System")
    
    c.save()
