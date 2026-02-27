"""
Audit Program PDF Generator (BACF6-05)
Generates a professional bilingual PDF for Audit Programs - scheduling audit stages.
Uses the official BAC document template.
"""

from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.units import mm
from pathlib import Path
import arabic_reshaper
from bidi.algorithm import get_display
from datetime import datetime
import logging
from io import BytesIO
import qrcode

ROOT_DIR = Path(__file__).parent

# Company info for footer
COMPANY_PHONE = "+966 55 123 4567"
COMPANY_WEBSITE = "www.bfrvc.sa"
PRIMARY_COLOR = colors.HexColor('#1e3a5f')

def generate_audit_program_pdf(program_data: dict) -> bytes:
    """
    Generate a professional bilingual Audit Program PDF (BACF6-05).
    Uses the official BAC document template design.
    """
    
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
        except Exception:
            pass
    
    logo_path = ROOT_DIR / "assets" / "bayan-logo.png"
    
    # Create PDF
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    # Colors - Official BAC colors
    primary_color = PRIMARY_COLOR
    section_color = colors.HexColor('#4a7c9b')
    light_bg = colors.HexColor('#f8f9fa')
    table_header_bg = primary_color
    
    # Extract data
    org_name = program_data.get('organization_name', '')
    standards = program_data.get('standards', [])
    num_shifts = program_data.get('num_shifts', 1)
    activities = program_data.get('activities', [])
    certification_manager = program_data.get('certification_manager', '')
    approval_date = program_data.get('approval_date', '')
    
    # Helper function for Arabic text
    def draw_arabic(text, x, y, size=10, bold=False, right_align=False, center=False):
        if arabic_font_available:
            try:
                reshaped = arabic_reshaper.reshape(str(text))
                bidi_text = get_display(reshaped)
                font = 'Amiri-Bold' if bold and font_bold_path.exists() else 'Amiri'
                c.setFont(font, size)
                if center:
                    c.drawCentredString(x, y, bidi_text)
                elif right_align:
                    c.drawRightString(x, y, bidi_text)
                else:
                    c.drawString(x, y, bidi_text)
            except Exception:
                pass

    def draw_official_header(title_en="AUDIT PROGRAM", title_ar="برنامج التدقيق"):
        """Draw the official BAC header"""
        logo_x = 40
        logo_y = height - 75
        
        if logo_path.exists():
            try:
                c.drawImage(str(logo_path), logo_x, logo_y, width=60, height=55, 
                           preserveAspectRatio=True, mask='auto')
            except Exception:
                pass
        
        # Company name
        name_x = logo_x + 70
        name_y = height - 30
        c.setFillColor(primary_color)
        draw_arabic("بيان للتحقق والمطابقة", name_x + 130, name_y, 13, bold=True, right_align=True)
        c.setFont('Helvetica-Bold', 9)
        c.drawString(name_x, name_y - 15, "BAYAN AUDITING & CONFORMITY")
        
        # Document title
        title_y = height - 95
        c.setFont('Helvetica-Bold', 16)
        c.setFillColor(primary_color)
        c.drawCentredString(width / 2, title_y, title_en)
        draw_arabic(title_ar, width / 2, title_y - 20, 14, bold=True, center=True)
        
        # Form reference
        c.setFont('Helvetica', 9)
        c.setFillColor(colors.black)
        c.drawRightString(width - 40, height - 25, "BACF6-05")
        c.drawRightString(width - 40, height - 38, f"Date: {datetime.now().strftime('%Y-%m-%d')}")
        
        return height - 130

    def draw_official_footer(page_num=1):
        """Draw the official BAC footer"""
        footer_y = 55
        
        c.setStrokeColor(primary_color)
        c.setLineWidth(1)
        c.line(40, footer_y + 25, width - 40, footer_y + 25)
        
        try:
            qr = qrcode.QRCode(version=1, box_size=10, border=2)
            qr.add_data(f"https://{COMPANY_WEBSITE}")
            qr.make(fit=True)
            qr_img = qr.make_image(fill_color="black", back_color="white")
            qr_buffer = BytesIO()
            qr_img.save(qr_buffer, format='PNG')
            qr_buffer.seek(0)
            from reportlab.lib.utils import ImageReader
            c.drawImage(ImageReader(qr_buffer), 45, footer_y - 20, width=45, height=45)
        except Exception:
            pass
        
        info_x = 100
        info_y = footer_y + 12
        c.setFont('Helvetica', 8)
        c.setFillColor(colors.black)
        c.drawString(info_x, info_y, f"Tel: {COMPANY_PHONE}")
        c.drawString(info_x, info_y - 11, f"Web: {COMPANY_WEBSITE}")
        
        c.setFont('Helvetica-Bold', 8)
        c.drawRightString(width - 45, info_y, "Director")
        c.setFont('Helvetica', 8)
        c.drawRightString(width - 45, info_y - 11, "BAYAN AUDITING & CONFORMITY (BAC)")
        
        c.setFont('Helvetica', 7)
        c.drawCentredString(width / 2, footer_y - 30, f"Page {page_num} | BACF6-05")
        
        return footer_y + 35
    
    # ============ PAGE 1 ============
    page_num = 1
    
    # Draw official header
    y = draw_official_header("AUDIT PROGRAM", "برنامج التدقيق")
    
    # Client Information Section
    c.setFillColor(section_color)
    c.setFont('Helvetica-Bold', 11)
    c.drawString(30, y, "Client Information")
    draw_arabic("معلومات العميل", width - 30, y, 10, bold=True, right_align=True)
    y -= 20
    
    # Info boxes
    c.setFillColor(light_bg)
    c.roundRect(30, y - 50, width/2 - 40, 55, 5, fill=True, stroke=False)
    c.roundRect(width/2 + 10, y - 50, width/2 - 40, 55, 5, fill=True, stroke=False)
    
    c.setFillColor(colors.black)
    c.setFont('Helvetica', 8)
    c.drawString(40, y - 10, "Client Name / اسم العميل:")
    c.setFont('Helvetica-Bold', 10)
    c.drawString(40, y - 26, org_name or "_______________________________________________")
    
    c.setFont('Helvetica', 8)
    c.drawString(40, y - 42, "No. of Shifts / عدد الورديات:")
    c.setFont('Helvetica-Bold', 10)
    c.drawString(150, y - 42, str(num_shifts) if num_shifts else "___")
    
    c.setFont('Helvetica', 8)
    c.drawString(width/2 + 20, y - 10, "Audit Standard(s) / معايير التدقيق:")
    c.setFont('Helvetica-Bold', 10)
    standards_str = ', '.join(standards) if standards else "_______________"
    c.drawString(width/2 + 20, y - 26, standards_str)
    
    y -= 70
    
    # Audit Activities Table Section
    c.setFillColor(section_color)
    c.setFont('Helvetica-Bold', 11)
    c.drawString(30, y, "Audit Activities Schedule")
    draw_arabic("جدول أنشطة التدقيق", width - 30, y, 10, bold=True, right_align=True)
    y -= 15
    
    # Table
    table_x = 30
    table_width = width - 60
    
    # Column widths
    col_widths = [100, 70, 55, 55, 55, 55, 55, 80]
    col_headers = [
        ('Audit Activities', 'أنشطة التدقيق'),
        ('Audit Type', 'نوع التدقيق'),
        ('Stage 1', 'المرحلة 1'),
        ('Stage 2', 'المرحلة 2'),
        ('SUR 1', 'المراقبة 1'),
        ('SUR 2', 'المراقبة 2'),
        ('RC', 'إعادة الاعتماد'),
        ('Planned Date', 'التاريخ المخطط')
    ]
    
    # Draw table header
    c.setFillColor(table_header_bg)
    c.rect(table_x, y - 30, table_width, 30, fill=True, stroke=False)
    
    c.setFillColor(colors.white)
    c.setFont('Helvetica-Bold', 7)
    
    x = table_x
    for i, (eng, ar) in enumerate(col_headers):
        col_center = x + col_widths[i]/2
        c.drawCentredString(col_center, y - 12, eng)
        if arabic_font_available:
            draw_arabic(ar, col_center + 15, y - 24, 6)
        x += col_widths[i]
    
    y -= 32
    
    # Draw table rows
    row_height = 25
    c.setFont('Helvetica', 8)
    
    # Draw at least 10 rows (empty if no activities)
    num_rows = max(len(activities), 10)
    
    for row_idx in range(num_rows):
        # Alternate row colors
        if row_idx % 2 == 0:
            c.setFillColor(light_bg)
        else:
            c.setFillColor(colors.white)
        
        c.rect(table_x, y - row_height, table_width, row_height, fill=True, stroke=False)
        
        # Draw cell borders
        c.setStrokeColor(colors.grey)
        c.setLineWidth(0.5)
        c.rect(table_x, y - row_height, table_width, row_height, fill=False, stroke=True)
        
        # Vertical lines
        x = table_x
        for w in col_widths[:-1]:
            x += w
            c.line(x, y, x, y - row_height)
        
        # Fill data if available
        c.setFillColor(colors.black)
        if row_idx < len(activities):
            activity = activities[row_idx]
            data = [
                activity.get('activity', ''),
                activity.get('audit_type', ''),
                activity.get('stage1', ''),
                activity.get('stage2', ''),
                activity.get('sur1', ''),
                activity.get('sur2', ''),
                activity.get('rc', ''),
                activity.get('planned_date', '')
            ]
            
            x = table_x
            for i, val in enumerate(data):
                text = str(val)[:15] if val else ''  # Truncate long text
                c.drawCentredString(x + col_widths[i]/2, y - row_height + 8, text)
                x += col_widths[i]
        
        y -= row_height
        
        # Check if we need a new page
        if y < 120:
            draw_official_footer(page_num)
            c.showPage()
            page_num += 1
            
            # New page header
            c.setFillColor(primary_color)
            c.rect(0, height - 50, width, 50, fill=True, stroke=False)
            c.setFillColor(colors.white)
            c.setFont('Helvetica-Bold', 14)
            c.drawCentredString(width/2, height - 30, "AUDIT PROGRAM - Continued")
            draw_arabic("برنامج التدقيق - تابع", width/2 + 80, height - 45, 10, bold=True)
            
            y = height - 70
    
    y -= 20
    
    # Check if we have enough space for signature section
    if y < 150:
        draw_official_footer(page_num)
        c.showPage()
        page_num += 1
        c.setFillColor(primary_color)
        c.rect(0, height - 50, width, 50, fill=True, stroke=False)
        c.setFillColor(colors.white)
        c.setFont('Helvetica-Bold', 14)
        c.drawCentredString(width/2, height - 30, "AUDIT PROGRAM")
        y = height - 70
    
    # Approval Section
    c.setFillColor(section_color)
    c.setFont('Helvetica-Bold', 11)
    c.drawString(30, y, "Approval / الموافقة")
    y -= 25
    
    # Signature box
    c.setFillColor(light_bg)
    c.roundRect(30, y - 70, width/2 - 40, 75, 5, fill=True, stroke=False)
    c.setStrokeColor(section_color)
    c.roundRect(30, y - 70, width/2 - 40, 75, 5, fill=False, stroke=True)
    
    c.setFillColor(section_color)
    c.setFont('Helvetica-Bold', 9)
    c.drawString(40, y - 12, "Certification Manager / مدير الاعتماد")
    
    c.setFillColor(colors.black)
    c.setFont('Helvetica', 9)
    c.drawString(40, y - 32, f"Name / الاسم: {certification_manager or '________________________'}")
    c.drawString(40, y - 50, f"Date / التاريخ: {approval_date or '________________________'}")
    c.drawString(40, y - 65, "Signature / التوقيع: ________________________")
    
    # Notes section
    c.setFillColor(light_bg)
    c.roundRect(width/2 + 10, y - 70, width/2 - 40, 75, 5, fill=True, stroke=False)
    
    c.setFillColor(section_color)
    c.setFont('Helvetica-Bold', 9)
    c.drawString(width/2 + 20, y - 12, "Notes / ملاحظات")
    
    c.setFillColor(colors.black)
    c.setFont('Helvetica', 8)
    notes = program_data.get('notes', '')
    if notes:
        notes_lines = [notes[i:i+40] for i in range(0, min(len(notes), 120), 40)]
        for idx, line in enumerate(notes_lines):
            c.drawString(width/2 + 20, y - 30 - (idx * 12), line)
    
    draw_official_footer(page_num)
    
    # Save
    c.save()
    
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    return pdf_bytes


# For testing
if __name__ == "__main__":
    test_data = {
        "organization_name": "Test Company Ltd.",
        "standards": ["ISO 9001", "ISO 14001"],
        "num_shifts": 2,
        "activities": [
            {
                "activity": "Document Review",
                "audit_type": "Desktop",
                "stage1": "1 day",
                "stage2": "",
                "sur1": "",
                "sur2": "",
                "rc": "",
                "planned_date": "2026-03-15"
            },
            {
                "activity": "Opening Meeting",
                "audit_type": "On-site",
                "stage1": "0.5 day",
                "stage2": "0.5 day",
                "sur1": "0.5 day",
                "sur2": "0.5 day",
                "rc": "0.5 day",
                "planned_date": "2026-03-20"
            },
            {
                "activity": "Process Audit",
                "audit_type": "On-site",
                "stage1": "",
                "stage2": "2 days",
                "sur1": "1 day",
                "sur2": "1 day",
                "rc": "2 days",
                "planned_date": "2026-03-21"
            },
            {
                "activity": "Closing Meeting",
                "audit_type": "On-site",
                "stage1": "",
                "stage2": "0.5 day",
                "sur1": "0.5 day",
                "sur2": "0.5 day",
                "rc": "0.5 day",
                "planned_date": "2026-03-22"
            }
        ],
        "certification_manager": "John Smith",
        "approval_date": "2026-03-10",
        "notes": "Initial certification audit scheduled for Q1 2026."
    }
    
    pdf_bytes = generate_audit_program_pdf(test_data)
    
    output_path = ROOT_DIR / "contracts" / "test_audit_program.pdf"
    with open(output_path, 'wb') as f:
        f.write(pdf_bytes)
    print(f"Generated: {output_path}")
