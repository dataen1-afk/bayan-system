"""
Stage 1 Audit Plan PDF Generator (BACF6-07)
Generates a professional bilingual PDF for Stage 1 Audit Plans.
"""

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.units import mm
from pathlib import Path
import arabic_reshaper
from bidi.algorithm import get_display
from datetime import datetime
from io import BytesIO
import qrcode

ROOT_DIR = Path(__file__).parent

# Company info
COMPANY_PHONE = "+966 55 123 4567"
COMPANY_WEBSITE = "www.bfrvc.sa"
PRIMARY_COLOR_HEX = "#1e3a5f"

def generate_stage1_audit_plan_pdf(plan_data: dict) -> bytes:
    """
    Generate a professional bilingual Stage 1 Audit Plan PDF (BACF6-07).
    
    Args:
        plan_data: Dictionary containing audit plan data
    
    Returns:
        PDF bytes
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
    
    # Colors
    primary_color = colors.HexColor('#1e3a5f')
    section_color = colors.HexColor('#4a7c9b')
    light_bg = colors.HexColor('#f0f4f8')
    table_header_bg = colors.HexColor('#1e3a5f')
    success_color = colors.HexColor('#059669')
    
    # Extract data
    organization_name = plan_data.get('organization_name', '')
    file_no = plan_data.get('file_no', '')
    address = plan_data.get('address', '')
    plan_date = plan_data.get('plan_date', '')
    contact_person = plan_data.get('contact_person', '')
    contact_phone = plan_data.get('contact_phone', '')
    contact_designation = plan_data.get('contact_designation', '')
    contact_email = plan_data.get('contact_email', '')
    
    # Audit details
    standards = plan_data.get('standards', [])
    audit_language = plan_data.get('audit_language', 'English')
    audit_type = plan_data.get('audit_type', 'Stage 1')
    audit_date_from = plan_data.get('audit_date_from', '')
    audit_date_to = plan_data.get('audit_date_to', '')
    scope = plan_data.get('scope', '')
    
    # Team
    team_leader = plan_data.get('team_leader', {})
    team_members = plan_data.get('team_members', [])
    
    # Schedule
    schedule_entries = plan_data.get('schedule_entries', [])
    
    # Status
    manager_approved = plan_data.get('manager_approved', False)
    client_accepted = plan_data.get('client_accepted', False)
    
    # Helper function for Arabic text
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
        c.drawCentredString(width/2, 10, f"Page {page_num} | BAYAN for Verification and Conformity | Stage 1 Audit Plan BACF6-07")
    
    # ============ PAGE 1 ============
    page_num = 1
    
    # Header
    c.setFillColor(primary_color)
    c.rect(0, height - 100, width, 100, fill=True, stroke=False)
    
    # Logo
    if logo_path.exists():
        try:
            c.setFillColor(colors.white)
            c.roundRect(25, height - 85, 65, 65, 5, fill=True, stroke=False)
            c.drawImage(str(logo_path), 28, height - 82, width=59, height=59, preserveAspectRatio=True, mask='auto')
        except Exception:
            pass
    
    # Title
    c.setFillColor(colors.white)
    c.setFont('Helvetica-Bold', 18)
    c.drawCentredString(width/2, height - 35, "STAGE 1 AUDIT PLAN")
    c.setFont('Helvetica', 11)
    c.drawCentredString(width/2, height - 52, "Initial Certification Audit - Phase 1")
    draw_arabic("خطة تدقيق المرحلة الأولى", width/2 + 80, height - 70, 12, bold=True)
    
    # Form reference
    c.setFont('Helvetica', 9)
    c.drawRightString(width - 25, height - 25, "BACF6-07")
    
    y = height - 120
    
    # Client Information Section
    c.setFillColor(section_color)
    c.setFont('Helvetica-Bold', 11)
    c.drawString(30, y, "Client Information / معلومات العميل")
    y -= 20
    
    # Client info box
    c.setFillColor(light_bg)
    c.roundRect(30, y - 85, width - 60, 90, 5, fill=True, stroke=False)
    
    c.setFillColor(colors.black)
    c.setFont('Helvetica', 8)
    
    # Two columns
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
    
    # Audit Details Section
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
    
    # Audit Objectives Section
    c.setFillColor(section_color)
    c.setFont('Helvetica-Bold', 11)
    c.drawString(30, y, "Audit Objectives / أهداف التدقيق")
    y -= 15
    
    objectives = [
        "Review the organization's management system documentation",
        "Evaluate location and site-specific conditions for Stage 2 preparedness",
        "Review status and understanding of requirements, key aspects, hazards & risks",
        "Collect information regarding scope, processes, locations, and compliance",
        "Review resource allocation for Stage 2 and agree on details",
        "Provide focus for Stage 2 planning through understanding of operations",
        "Evaluate internal audits and management review implementation"
    ]
    
    c.setFillColor(colors.black)
    c.setFont('Helvetica', 7)
    for i, obj in enumerate(objectives):
        c.drawString(35, y - (i * 11), f"• {obj}")
    
    y -= (len(objectives) * 11) + 15
    
    # Audit Team Section
    c.setFillColor(section_color)
    c.setFont('Helvetica-Bold', 11)
    c.drawString(30, y, "Audit Team / فريق التدقيق")
    y -= 20
    
    c.setFillColor(light_bg)
    c.roundRect(30, y - 45, width - 60, 50, 5, fill=True, stroke=False)
    
    c.setFillColor(colors.black)
    c.setFont('Helvetica', 8)
    
    # Team leader
    info_y = y - 15
    c.setFillColor(colors.grey)
    c.drawString(left_col, info_y, "Team Leader / قائد الفريق:")
    c.setFillColor(colors.black)
    c.setFont('Helvetica-Bold', 9)
    leader_name = team_leader.get('name', '') if isinstance(team_leader, dict) else str(team_leader)
    c.drawString(left_col + 110, info_y, leader_name or "N/A")
    
    # Other team members
    info_y -= 18
    c.setFont('Helvetica', 8)
    c.setFillColor(colors.grey)
    c.drawString(left_col, info_y, "Team Members / أعضاء الفريق:")
    c.setFillColor(colors.black)
    
    members_str = ""
    for i, member in enumerate(team_members[:4]):
        member_name = member.get('name', '') if isinstance(member, dict) else str(member)
        role = member.get('role', 'Auditor') if isinstance(member, dict) else 'Auditor'
        if members_str:
            members_str += ", "
        members_str += f"{member_name} ({role})"
    
    c.setFont('Helvetica', 8)
    c.drawString(left_col + 120, info_y, members_str[:70] if members_str else "N/A")
    
    y -= 65
    
    # Check if we need a new page before schedule
    if y < 250:
        draw_footer(page_num)
        c.showPage()
        page_num += 1
        y = height - 50
        
        c.setFillColor(primary_color)
        c.rect(0, height - 40, width, 40, fill=True, stroke=False)
        c.setFillColor(colors.white)
        c.setFont('Helvetica-Bold', 12)
        c.drawCentredString(width/2, height - 25, "Stage 1 Audit Plan - Schedule")
    
    # Audit Schedule Table
    c.setFillColor(section_color)
    c.setFont('Helvetica-Bold', 11)
    c.drawString(30, y, "Audit Schedule Details / تفاصيل جدول التدقيق")
    y -= 15
    
    # Table
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
    
    # Header row
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
    
    # Table rows
    row_height = 22
    num_rows = max(len(schedule_entries), 6)
    
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
        
        # Fill data
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
        
        # Check for page break
        if y < 120:
            draw_footer(page_num)
            c.showPage()
            page_num += 1
            y = height - 50
    
    y -= 20
    
    # Acceptance Statement
    if y < 150:
        draw_footer(page_num)
        c.showPage()
        page_num += 1
        y = height - 50
    
    c.setFillColor(section_color)
    c.setFont('Helvetica-Bold', 10)
    c.drawString(30, y, "Acceptance Statement / بيان القبول")
    y -= 20
    
    c.setFillColor(light_bg)
    c.roundRect(30, y - 60, width - 60, 65, 5, fill=True, stroke=False)
    
    c.setFillColor(colors.black)
    c.setFont('Helvetica', 8)
    
    acceptance_text = "We trust the proposed schedule and audit team is acceptable to you. If you have any objections to the audit team composition, please register the non-acceptance (with reasons) immediately. If no objections are received within 2 working days, the audit team shall be deemed accepted."
    
    # Word wrap
    words = acceptance_text.split()
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
    
    text_y = y - 15
    for line in lines[:4]:
        c.drawString(40, text_y, line)
        text_y -= 12
    
    y -= 80
    
    # Signature Section
    c.setFillColor(success_color if manager_approved else section_color)
    c.roundRect(30, y - 50, width/2 - 40, 55, 5, fill=True, stroke=False)
    
    c.setFillColor(colors.white)
    c.setFont('Helvetica-Bold', 9)
    c.drawString(40, y - 15, "Team Leader / قائد الفريق")
    c.setFont('Helvetica', 8)
    c.drawString(40, y - 30, f"Name: {leader_name}")
    c.drawString(40, y - 45, f"Status: {'Approved' if manager_approved else 'Pending'}")
    
    # Client acceptance status
    c.setFillColor(success_color if client_accepted else colors.orange)
    c.roundRect(width/2 + 10, y - 50, width/2 - 40, 55, 5, fill=True, stroke=False)
    
    c.setFillColor(colors.white)
    c.setFont('Helvetica-Bold', 9)
    c.drawString(width/2 + 20, y - 15, "Client Acceptance / قبول العميل")
    c.setFont('Helvetica', 8)
    status_text = "Accepted" if client_accepted else "Pending Review"
    c.drawString(width/2 + 20, y - 30, f"Status: {status_text}")
    
    draw_footer(page_num)
    
    # Save
    c.save()
    
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    return pdf_bytes


# For testing
if __name__ == "__main__":
    test_data = {
        "organization_name": "Test Company Ltd.",
        "file_no": "FILE-2026-001",
        "address": "123 Main St, Riyadh, Saudi Arabia",
        "plan_date": "2026-02-17",
        "contact_person": "John Doe",
        "contact_phone": "+966 11 123 4567",
        "contact_designation": "Quality Manager",
        "contact_email": "john@testcompany.com",
        "standards": ["ISO 9001", "ISO 14001"],
        "audit_language": "English",
        "audit_type": "Stage 1",
        "audit_date_from": "2026-03-15",
        "audit_date_to": "2026-03-16",
        "scope": "Quality and Environmental Management Systems",
        "team_leader": {"name": "Ahmed Al-Rashid", "role": "Lead Auditor"},
        "team_members": [
            {"name": "Mohammad Ali", "role": "Auditor"},
            {"name": "Sara Hassan", "role": "Technical Expert"}
        ],
        "schedule_entries": [
            {"date_time": "09:00 - 10:00", "process": "Opening Meeting", "process_owner": "Top Management", "clauses": "4.1, 4.2", "auditor": "Team"},
            {"date_time": "10:00 - 12:00", "process": "Document Review", "process_owner": "QA Manager", "clauses": "7.5", "auditor": "A. Al-Rashid"},
            {"date_time": "13:00 - 15:00", "process": "Management Review", "process_owner": "CEO", "clauses": "9.3", "auditor": "A. Al-Rashid"},
            {"date_time": "15:00 - 16:00", "process": "Closing Meeting", "process_owner": "Top Management", "clauses": "N/A", "auditor": "Team"}
        ],
        "manager_approved": True,
        "client_accepted": False
    }
    
    pdf_bytes = generate_stage1_audit_plan_pdf(test_data)
    
    output_path = ROOT_DIR / "contracts" / "test_stage1_plan.pdf"
    with open(output_path, 'wb') as f:
        f.write(pdf_bytes)
    print(f"Generated: {output_path}")
