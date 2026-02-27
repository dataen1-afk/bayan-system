"""
Opening and Closing Meeting PDF Generator (BACF6-09)
Generates a professional bilingual PDF for Opening and Closing Meeting attendance records.
"""

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from pathlib import Path
import arabic_reshaper
from bidi.algorithm import get_display
from io import BytesIO
import qrcode

ROOT_DIR = Path(__file__).parent

# Company info
COMPANY_PHONE = "+966 55 123 4567"
COMPANY_WEBSITE = "www.bfrvc.sa"

def generate_opening_closing_meeting_pdf(meeting_data: dict) -> bytes:
    """
    Generate a professional bilingual Opening and Closing Meeting PDF (BACF6-09).
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
    
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    # Colors
    primary_color = colors.HexColor('#1e3a5f')
    section_color = colors.HexColor('#4a7c9b')
    light_bg = colors.HexColor('#f0f4f8')
    table_header_bg = colors.HexColor('#1e3a5f')
    meeting_color = colors.HexColor('#0891b2')  # Cyan for meetings
    
    # Extract data
    organization_name = meeting_data.get('organization_name', '')
    audit_type = meeting_data.get('audit_type', '')
    audit_date = meeting_data.get('audit_date', '')
    file_no = meeting_data.get('file_no', '')
    standards = meeting_data.get('standards', [])
    attendees = meeting_data.get('attendees', [])
    opening_meeting_notes = meeting_data.get('opening_meeting_notes', '')
    closing_meeting_notes = meeting_data.get('closing_meeting_notes', '')
    submitted_date = meeting_data.get('submitted_date', '')
    
    def draw_arabic(text, x, y, size=10, bold=False, right_align=False):
        if arabic_font_available and text:
            try:
                reshaped = arabic_reshaper.reshape(str(text))
                bidi_text = get_display(reshaped)
                font = 'Amiri-Bold' if bold and font_bold_path.exists() else 'Amiri'
                c.setFont(font, size)
                if right_align:
                    c.drawRightString(x, y, bidi_text)
                else:
                    c.drawString(x, y, bidi_text)
            except Exception:
                pass
    
    def draw_footer(page_num):
        c.setFillColor(primary_color)
        c.rect(0, 0, width, 25, fill=True, stroke=False)
        c.setFillColor(colors.white)
        c.setFont('Helvetica', 8)
        c.drawCentredString(width/2, 10, f"Page {page_num} | BAYAN for Verification and Conformity | Opening & Closing Meeting BACF6-09")
    
    # ============ PAGE 1 ============
    page_num = 1
    
    # Header
    c.setFillColor(primary_color)
    c.rect(0, height - 100, width, 100, fill=True, stroke=False)
    c.setFillColor(meeting_color)
    c.rect(0, height - 105, width, 5, fill=True, stroke=False)
    
    if logo_path.exists():
        try:
            c.setFillColor(colors.white)
            c.roundRect(25, height - 85, 65, 65, 5, fill=True, stroke=False)
            c.drawImage(str(logo_path), 28, height - 82, width=59, height=59, preserveAspectRatio=True, mask='auto')
        except Exception:
            pass
    
    c.setFillColor(colors.white)
    c.setFont('Helvetica-Bold', 18)
    c.drawCentredString(width/2, height - 35, "OPENING & CLOSING MEETING")
    c.setFont('Helvetica', 11)
    c.drawCentredString(width/2, height - 52, "Audit Meeting Attendance Record")
    draw_arabic("الاجتماع الافتتاحي والختامي", width/2 + 80, height - 70, 12, bold=True)
    
    c.setFont('Helvetica', 9)
    c.drawRightString(width - 25, height - 25, "BACF6-09")
    
    y = height - 125
    
    # Company Information
    c.setFillColor(section_color)
    c.setFont('Helvetica-Bold', 11)
    c.drawString(30, y, "Company Information / معلومات الشركة")
    y -= 20
    
    c.setFillColor(light_bg)
    c.roundRect(30, y - 55, width - 60, 60, 5, fill=True, stroke=False)
    
    c.setFillColor(colors.black)
    c.setFont('Helvetica', 8)
    
    left_col = 40
    right_col = width/2 + 20
    info_y = y - 15
    
    c.setFillColor(colors.grey)
    c.drawString(left_col, info_y, "Company Name / اسم الشركة:")
    c.setFillColor(colors.black)
    c.setFont('Helvetica-Bold', 9)
    c.drawString(left_col + 120, info_y, organization_name[:40] or "N/A")
    
    c.setFont('Helvetica', 8)
    c.setFillColor(colors.grey)
    c.drawString(right_col, info_y, "File No. / رقم الملف:")
    c.setFillColor(colors.black)
    c.setFont('Helvetica-Bold', 9)
    c.drawString(right_col + 80, info_y, file_no or "N/A")
    
    info_y -= 18
    c.setFont('Helvetica', 8)
    c.setFillColor(colors.grey)
    c.drawString(left_col, info_y, "Audit Type / نوع التدقيق:")
    c.setFillColor(colors.black)
    c.setFont('Helvetica-Bold', 9)
    c.drawString(left_col + 100, info_y, audit_type or "N/A")
    
    c.setFont('Helvetica', 8)
    c.setFillColor(colors.grey)
    c.drawString(right_col, info_y, "Audit Date / تاريخ التدقيق:")
    c.setFillColor(colors.black)
    c.drawString(right_col + 100, info_y, audit_date or "N/A")
    
    info_y -= 18
    c.setFont('Helvetica', 8)
    c.setFillColor(colors.grey)
    c.drawString(left_col, info_y, "Standards / المعايير:")
    c.setFillColor(colors.black)
    standards_str = ', '.join(standards) if standards else "N/A"
    c.drawString(left_col + 80, info_y, standards_str[:50])
    
    y -= 75
    
    # Attendees Table
    c.setFillColor(section_color)
    c.setFont('Helvetica-Bold', 11)
    c.drawString(30, y, "Meeting Attendees / الحضور")
    y -= 15
    
    table_x = 30
    table_width = width - 60
    col_widths = [35, 150, 120, 100, 100]  # S.N, Name, Designation, Opening Date, Closing Date
    col_headers = [
        ('S.N', 'م'),
        ('Name', 'الاسم'),
        ('Designation', 'المسمى الوظيفي'),
        ('Opening Meeting', 'الاجتماع الافتتاحي'),
        ('Closing Meeting', 'الاجتماع الختامي')
    ]
    
    # Table header
    c.setFillColor(table_header_bg)
    c.rect(table_x, y - 30, table_width, 30, fill=True, stroke=False)
    
    c.setFillColor(colors.white)
    c.setFont('Helvetica-Bold', 8)
    
    x = table_x
    for i, (eng, ar) in enumerate(col_headers):
        col_center = x + col_widths[i]/2
        c.drawCentredString(col_center, y - 12, eng)
        if arabic_font_available:
            draw_arabic(ar, col_center + 10, y - 24, 7)
        x += col_widths[i]
    
    y -= 32
    
    # Table rows
    row_height = 25
    num_rows = max(len(attendees), 5)  # Minimum 5 rows
    
    for row_idx in range(num_rows):
        if row_idx % 2 == 0:
            c.setFillColor(light_bg)
        else:
            c.setFillColor(colors.white)
        
        c.rect(table_x, y - row_height, table_width, row_height, fill=True, stroke=False)
        
        c.setStrokeColor(colors.grey)
        c.setLineWidth(0.5)
        c.rect(table_x, y - row_height, table_width, row_height, fill=False, stroke=True)
        
        # Vertical lines
        x = table_x
        for w in col_widths[:-1]:
            x += w
            c.line(x, y, x, y - row_height)
        
        c.setFillColor(colors.black)
        c.setFont('Helvetica', 9)
        
        if row_idx < len(attendees):
            attendee = attendees[row_idx]
            data = [
                str(row_idx + 1),
                attendee.get('name', ''),
                attendee.get('designation', ''),
                attendee.get('opening_meeting_date', ''),
                attendee.get('closing_meeting_date', '')
            ]
            
            x = table_x
            for i, val in enumerate(data):
                text = str(val)[:20] if val else ''
                c.drawCentredString(x + col_widths[i]/2, y - row_height + 9, text)
                x += col_widths[i]
        else:
            # Empty row with number
            c.drawCentredString(table_x + col_widths[0]/2, y - row_height + 9, str(row_idx + 1))
        
        y -= row_height
        
        # Page break check
        if y < 150:
            draw_footer(page_num)
            c.showPage()
            page_num += 1
            y = height - 50
            
            c.setFillColor(primary_color)
            c.rect(0, height - 40, width, 40, fill=True, stroke=False)
            c.setFillColor(meeting_color)
            c.rect(0, height - 45, width, 5, fill=True, stroke=False)
            c.setFillColor(colors.white)
            c.setFont('Helvetica-Bold', 12)
            c.drawCentredString(width/2, height - 25, "Opening & Closing Meeting - Continued")
    
    y -= 15
    
    # Meeting Notes Section
    if y < 200:
        draw_footer(page_num)
        c.showPage()
        page_num += 1
        y = height - 50
    
    # Opening Meeting Notes
    c.setFillColor(meeting_color)
    c.setFont('Helvetica-Bold', 10)
    c.drawString(30, y, "Opening Meeting Notes / ملاحظات الاجتماع الافتتاحي")
    y -= 15
    
    c.setFillColor(light_bg)
    c.roundRect(30, y - 50, width - 60, 55, 5, fill=True, stroke=False)
    
    c.setFillColor(colors.black)
    c.setFont('Helvetica', 8)
    
    if opening_meeting_notes:
        # Word wrap the notes
        words = opening_meeting_notes.split()
        lines = []
        current_line = ""
        for word in words:
            test_line = current_line + " " + word if current_line else word
            if c.stringWidth(test_line, 'Helvetica', 8) < width - 80:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        
        text_y = y - 12
        for line in lines[:4]:
            c.drawString(40, text_y, line)
            text_y -= 12
    else:
        c.setFillColor(colors.grey)
        c.drawString(40, y - 25, "No notes provided")
    
    y -= 70
    
    # Closing Meeting Notes
    c.setFillColor(meeting_color)
    c.setFont('Helvetica-Bold', 10)
    c.drawString(30, y, "Closing Meeting Notes / ملاحظات الاجتماع الختامي")
    y -= 15
    
    c.setFillColor(light_bg)
    c.roundRect(30, y - 50, width - 60, 55, 5, fill=True, stroke=False)
    
    c.setFillColor(colors.black)
    c.setFont('Helvetica', 8)
    
    if closing_meeting_notes:
        words = closing_meeting_notes.split()
        lines = []
        current_line = ""
        for word in words:
            test_line = current_line + " " + word if current_line else word
            if c.stringWidth(test_line, 'Helvetica', 8) < width - 80:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        
        text_y = y - 12
        for line in lines[:4]:
            c.drawString(40, text_y, line)
            text_y -= 12
    else:
        c.setFillColor(colors.grey)
        c.drawString(40, y - 25, "No notes provided")
    
    y -= 70
    
    # Submission Info
    if submitted_date:
        c.setFillColor(section_color)
        c.roundRect(30, y - 30, width - 60, 35, 5, fill=True, stroke=False)
        c.setFillColor(colors.white)
        c.setFont('Helvetica-Bold', 9)
        c.drawString(40, y - 12, f"Submitted on: {submitted_date}")
        draw_arabic("تاريخ التقديم:", width - 150, y - 12, 9)
    
    draw_footer(page_num)
    
    c.save()
    
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    return pdf_bytes
