"""
Stage 2 Audit Plan PDF Generator (BACF6-08)
Generates a professional bilingual PDF for Stage 2 Audit Plans.
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
PRIMARY_COLOR_HEX = "#1e3a5f"

def generate_stage2_audit_plan_pdf(plan_data: dict) -> bytes:
    """
    Generate a professional bilingual Stage 2 Audit Plan PDF (BACF6-08).
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
    success_color = colors.HexColor('#059669')
    stage2_color = colors.HexColor('#7c3aed')  # Purple for Stage 2
    
    # Extract data
    organization_name = plan_data.get('organization_name', '')
    file_no = plan_data.get('file_no', '')
    address = plan_data.get('address', '')
    plan_date = plan_data.get('plan_date', '')
    contact_person = plan_data.get('contact_person', '')
    contact_phone = plan_data.get('contact_phone', '')
    contact_designation = plan_data.get('contact_designation', '')
    contact_email = plan_data.get('contact_email', '')
    
    standards = plan_data.get('standards', [])
    audit_language = plan_data.get('audit_language', 'English')
    audit_type = plan_data.get('audit_type', 'Stage 2')  # Stage 2, Renewal, Surveillance
    audit_date_from = plan_data.get('audit_date_from', '')
    audit_date_to = plan_data.get('audit_date_to', '')
    scope = plan_data.get('scope', '')
    
    team_leader = plan_data.get('team_leader', {})
    team_members = plan_data.get('team_members', [])
    schedule_entries = plan_data.get('schedule_entries', [])
    
    manager_approved = plan_data.get('manager_approved', False)
    client_accepted = plan_data.get('client_accepted', False)
    
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

    def draw_official_header(title_en="STAGE 2 AUDIT PLAN", title_ar="خطة تدقيق المرحلة الثانية"):
        """Draw the official BAC header"""
        logo_x = 40
        logo_y = height - 75
        
        if logo_path.exists():
            try:
                c.drawImage(str(logo_path), logo_x, logo_y, width=60, height=55, 
                           preserveAspectRatio=True, mask='auto')
            except Exception:
                pass
        
        name_x = logo_x + 70
        name_y = height - 30
        c.setFillColor(primary_color)
        draw_arabic("بيان للتحقق والمطابقة", name_x + 130, name_y, 13, bold=True, right_align=True)
        c.setFont('Helvetica-Bold', 9)
        c.drawString(name_x, name_y - 15, "BAYAN AUDITING & CONFORMITY")
        
        title_y = height - 95
        c.setFont('Helvetica-Bold', 16)
        c.setFillColor(primary_color)
        c.drawCentredString(width / 2, title_y, title_en)
        draw_arabic(title_ar, width / 2, title_y - 20, 14, bold=True, center=True)
        
        c.setFont('Helvetica', 9)
        c.setFillColor(colors.black)
        c.drawRightString(width - 40, height - 25, "BACF6-08")
        
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
        c.drawCentredString(width / 2, footer_y - 30, f"Page {page_num} | BACF6-08")
        
        return footer_y + 35
    
    # ============ PAGE 1 ============
    page_num = 1
    
    # Draw official header
    y = draw_official_header("STAGE 2 AUDIT PLAN", "خطة تدقيق المرحلة الثانية")
    
    # Client Information
    c.setFillColor(section_color)
    c.setFont('Helvetica-Bold', 11)
    c.drawString(30, y, "Client Information / معلومات العميل")
    y -= 20
    
    c.setFillColor(light_bg)
    c.roundRect(30, y - 85, width - 60, 90, 5, fill=True, stroke=False)
    
    c.setFillColor(colors.black)
    c.setFont('Helvetica', 8)
    
    left_col = 40
    right_col = width/2 + 20
    info_y = y - 15
    
    c.setFillColor(colors.grey)
    c.drawString(left_col, info_y, "Name of Client / اسم العميل:")
    c.setFillColor(colors.black)
    c.setFont('Helvetica-Bold', 9)
    c.drawString(left_col + 120, info_y, organization_name[:35] or "N/A")
    
    c.setFont('Helvetica', 8)
    c.setFillColor(colors.grey)
    c.drawString(right_col, info_y, "File No. / رقم الملف:")
    c.setFillColor(colors.black)
    c.setFont('Helvetica-Bold', 9)
    c.drawString(right_col + 80, info_y, file_no or "N/A")
    
    info_y -= 18
    c.setFont('Helvetica', 8)
    c.setFillColor(colors.grey)
    c.drawString(left_col, info_y, "Address / العنوان:")
    c.setFillColor(colors.black)
    c.setFont('Helvetica', 8)
    c.drawString(left_col + 80, info_y, address[:50] or "N/A")
    
    c.setFillColor(colors.grey)
    c.drawString(right_col, info_y, "Date of Plan / تاريخ الخطة:")
    c.setFillColor(colors.black)
    c.setFont('Helvetica-Bold', 9)
    c.drawString(right_col + 100, info_y, plan_date or "N/A")
    
    info_y -= 18
    c.setFont('Helvetica', 8)
    c.setFillColor(colors.grey)
    c.drawString(left_col, info_y, "Contact Person / شخص الاتصال:")
    c.setFillColor(colors.black)
    c.setFont('Helvetica', 9)
    c.drawString(left_col + 120, info_y, contact_person or "N/A")
    
    c.setFillColor(colors.grey)
    c.drawString(right_col, info_y, "Contact No. / رقم الاتصال:")
    c.setFillColor(colors.black)
    c.drawString(right_col + 100, info_y, contact_phone or "N/A")
    
    info_y -= 18
    c.setFont('Helvetica', 8)
    c.setFillColor(colors.grey)
    c.drawString(left_col, info_y, "Designation / المسمى الوظيفي:")
    c.setFillColor(colors.black)
    c.drawString(left_col + 120, info_y, contact_designation or "N/A")
    
    c.setFillColor(colors.grey)
    c.drawString(right_col, info_y, "E-mail / البريد الإلكتروني:")
    c.setFillColor(colors.black)
    c.drawString(right_col + 100, info_y, contact_email[:25] or "N/A")
    
    y -= 105
    
    # Audit Details
    c.setFillColor(section_color)
    c.setFont('Helvetica-Bold', 11)
    c.drawString(30, y, "Audit Details / تفاصيل التدقيق")
    y -= 20
    
    c.setFillColor(light_bg)
    c.roundRect(30, y - 55, width - 60, 60, 5, fill=True, stroke=False)
    
    c.setFillColor(colors.black)
    c.setFont('Helvetica', 8)
    
    info_y = y - 15
    c.setFillColor(colors.grey)
    c.drawString(left_col, info_y, "Audit Criteria / معايير التدقيق:")
    c.setFillColor(colors.black)
    c.setFont('Helvetica-Bold', 9)
    standards_str = ', '.join(standards) if standards else "N/A"
    c.drawString(left_col + 110, info_y, standards_str[:40])
    
    c.setFont('Helvetica', 8)
    c.setFillColor(colors.grey)
    c.drawString(right_col, info_y, "Audit Language / لغة التدقيق:")
    c.setFillColor(colors.black)
    c.drawString(right_col + 110, info_y, audit_language)
    
    info_y -= 18
    c.setFillColor(colors.grey)
    c.drawString(left_col, info_y, "Type of Audit / نوع التدقيق:")
    c.setFillColor(colors.black)
    c.setFont('Helvetica-Bold', 9)
    c.drawString(left_col + 100, info_y, audit_type)
    
    c.setFont('Helvetica', 8)
    c.setFillColor(colors.grey)
    c.drawString(right_col, info_y, "Date From / من تاريخ:")
    c.setFillColor(colors.black)
    c.drawString(right_col + 90, info_y, audit_date_from or "DD/MM/YYYY")
    
    c.setFillColor(colors.grey)
    c.drawString(right_col + 160, info_y, "To / إلى:")
    c.setFillColor(colors.black)
    c.drawString(right_col + 190, info_y, audit_date_to or "DD/MM/YYYY")
    
    info_y -= 18
    c.setFillColor(colors.grey)
    c.drawString(left_col, info_y, "Scope / النطاق:")
    c.setFillColor(colors.black)
    c.setFont('Helvetica', 8)
    scope_display = scope[:80] + "..." if scope and len(scope) > 80 else (scope or "N/A")
    c.drawString(left_col + 70, info_y, scope_display)
    
    y -= 75
    
    # Stage 2 Audit Objectives
    c.setFillColor(stage2_color)
    c.setFont('Helvetica-Bold', 11)
    c.drawString(30, y, "Stage 2 Audit Objectives / أهداف تدقيق المرحلة الثانية")
    y -= 12
    
    objectives = [
        "Verify conformity to all requirements of the applicable management system standard",
        "Performance monitoring, measuring, reporting and reviewing against key performance objectives",
        "Organization's management system and performance as regards legal compliance",
        "Operational control of the Organization's processes",
        "Internal auditing and management review effectiveness",
        "Management responsibility for the Organization's policies",
        "Review of actions taken on nonconformities from previous audit",
        "Treatment of complaints and continual improvement demonstration"
    ]
    
    c.setFillColor(colors.black)
    c.setFont('Helvetica', 6)
    for i, obj in enumerate(objectives):
        c.drawString(35, y - (i * 9), f"• {obj}")
    
    y -= (len(objectives) * 9) + 10
    
    # Audit Team
    c.setFillColor(section_color)
    c.setFont('Helvetica-Bold', 11)
    c.drawString(30, y, "Audit Team / فريق التدقيق")
    y -= 18
    
    c.setFillColor(light_bg)
    c.roundRect(30, y - 40, width - 60, 45, 5, fill=True, stroke=False)
    
    c.setFillColor(colors.black)
    c.setFont('Helvetica', 8)
    
    info_y = y - 12
    c.setFillColor(colors.grey)
    c.drawString(left_col, info_y, "Team Leader / قائد الفريق:")
    c.setFillColor(colors.black)
    c.setFont('Helvetica-Bold', 9)
    leader_name = team_leader.get('name', '') if isinstance(team_leader, dict) else str(team_leader)
    c.drawString(left_col + 110, info_y, leader_name or "N/A")
    
    info_y -= 15
    c.setFont('Helvetica', 8)
    c.setFillColor(colors.grey)
    c.drawString(left_col, info_y, "Team Members / أعضاء الفريق:")
    c.setFillColor(colors.black)
    
    members_str = ""
    for member in team_members[:4]:
        member_name = member.get('name', '') if isinstance(member, dict) else str(member)
        role = member.get('role', 'Auditor') if isinstance(member, dict) else 'Auditor'
        if members_str:
            members_str += ", "
        members_str += f"{member_name} ({role})"
    
    c.setFont('Helvetica', 8)
    c.drawString(left_col + 120, info_y, members_str[:70] if members_str else "N/A")
    
    y -= 58
    
    # Check page break
    if y < 220:
        draw_official_footer(page_num)
        c.showPage()
        page_num += 1
        y = height - 50
        
        c.setFillColor(primary_color)
        c.rect(0, height - 40, width, 40, fill=True, stroke=False)
        c.setFillColor(stage2_color)
        c.rect(0, height - 45, width, 5, fill=True, stroke=False)
        c.setFillColor(colors.white)
        c.setFont('Helvetica-Bold', 12)
        c.drawCentredString(width/2, height - 25, "Stage 2 Audit Plan - Schedule")
    
    # Schedule Table
    c.setFillColor(section_color)
    c.setFont('Helvetica-Bold', 11)
    c.drawString(30, y, "Audit Schedule Details / تفاصيل جدول التدقيق")
    y -= 15
    
    table_x = 30
    table_width = width - 60
    col_widths = [70, 120, 100, 100, 80]
    col_headers = [
        ('Date/Time', 'التاريخ/الوقت'),
        ('Process', 'العملية'),
        ('Process Owner', 'مالك العملية'),
        ('Applicable Clauses', 'البنود'),
        ('Auditor', 'المدقق')
    ]
    
    c.setFillColor(table_header_bg)
    c.rect(table_x, y - 25, table_width, 25, fill=True, stroke=False)
    
    c.setFillColor(colors.white)
    c.setFont('Helvetica-Bold', 7)
    
    x = table_x
    for i, (eng, ar) in enumerate(col_headers):
        col_center = x + col_widths[i]/2
        c.drawCentredString(col_center, y - 10, eng)
        if arabic_font_available:
            draw_arabic(ar, col_center + 10, y - 20, 6)
        x += col_widths[i]
    
    y -= 27
    
    row_height = 22
    num_rows = max(len(schedule_entries), 8)
    
    for row_idx in range(num_rows):
        if row_idx % 2 == 0:
            c.setFillColor(light_bg)
        else:
            c.setFillColor(colors.white)
        
        c.rect(table_x, y - row_height, table_width, row_height, fill=True, stroke=False)
        
        c.setStrokeColor(colors.grey)
        c.setLineWidth(0.5)
        c.rect(table_x, y - row_height, table_width, row_height, fill=False, stroke=True)
        
        x = table_x
        for w in col_widths[:-1]:
            x += w
            c.line(x, y, x, y - row_height)
        
        c.setFillColor(colors.black)
        c.setFont('Helvetica', 7)
        
        if row_idx < len(schedule_entries):
            entry = schedule_entries[row_idx]
            data = [
                entry.get('date_time', ''),
                entry.get('process', ''),
                entry.get('process_owner', ''),
                entry.get('clauses', ''),
                entry.get('auditor', '')
            ]
            
            x = table_x
            for i, val in enumerate(data):
                text = str(val)[:18] if val else ''
                c.drawCentredString(x + col_widths[i]/2, y - row_height + 8, text)
                x += col_widths[i]
        
        y -= row_height
        
        if y < 120:
            draw_official_footer(page_num)
            c.showPage()
            page_num += 1
            y = height - 50
    
    y -= 15
    
    # Acceptance Statement
    if y < 130:
        draw_official_footer(page_num)
        c.showPage()
        page_num += 1
        y = height - 50
    
    c.setFillColor(section_color)
    c.setFont('Helvetica-Bold', 10)
    c.drawString(30, y, "Acceptance Statement / بيان القبول")
    y -= 18
    
    c.setFillColor(light_bg)
    c.roundRect(30, y - 50, width - 60, 55, 5, fill=True, stroke=False)
    
    c.setFillColor(colors.black)
    c.setFont('Helvetica', 7)
    
    acceptance_text = "We trust the proposed schedule and audit team is acceptable to you. If you have any objections to the audit team composition, please register the non-acceptance (with reasons) immediately. If no objections are received within 2 working days, the audit team shall be deemed accepted."
    
    words = acceptance_text.split()
    lines = []
    current_line = ""
    for word in words:
        test_line = current_line + " " + word if current_line else word
        if c.stringWidth(test_line, 'Helvetica', 7) < width - 80:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    
    text_y = y - 12
    for line in lines[:4]:
        c.drawString(40, text_y, line)
        text_y -= 10
    
    y -= 65
    
    # Signature Section
    c.setFillColor(success_color if manager_approved else section_color)
    c.roundRect(30, y - 45, width/2 - 40, 50, 5, fill=True, stroke=False)
    
    c.setFillColor(colors.white)
    c.setFont('Helvetica-Bold', 9)
    c.drawString(40, y - 12, "Team Leader / قائد الفريق")
    c.setFont('Helvetica', 8)
    c.drawString(40, y - 27, f"Name: {leader_name}")
    c.drawString(40, y - 40, f"Status: {'Approved' if manager_approved else 'Pending'}")
    
    c.setFillColor(success_color if client_accepted else colors.orange)
    c.roundRect(width/2 + 10, y - 45, width/2 - 40, 50, 5, fill=True, stroke=False)
    
    c.setFillColor(colors.white)
    c.setFont('Helvetica-Bold', 9)
    c.drawString(width/2 + 20, y - 12, "Client Acceptance / قبول العميل")
    c.setFont('Helvetica', 8)
    status_text = "Accepted" if client_accepted else "Pending Review"
    c.drawString(width/2 + 20, y - 27, f"Status: {status_text}")
    
    draw_official_footer(page_num)
    
    c.save()
    
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    return pdf_bytes
