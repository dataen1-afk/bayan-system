"""
Stage 1 Audit Report PDF Generator (BACF6-10)
Generates a comprehensive bilingual PDF for Stage 1 Audit Reports.
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

ROOT_DIR = Path(__file__).parent

def generate_stage1_audit_report_pdf(report_data: dict) -> bytes:
    """
    Generate a comprehensive bilingual Stage 1 Audit Report PDF (BACF6-10).
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
    report_color = colors.HexColor('#dc2626')  # Red for audit report
    success_color = colors.HexColor('#16a34a')
    warning_color = colors.HexColor('#ea580c')
    
    # Extract data
    organization_name = report_data.get('organization_name', '')
    address = report_data.get('address', '')
    site_address = report_data.get('site_address', '')
    standards = report_data.get('standards', [])
    num_employees = report_data.get('num_employees', '')
    num_shifts = report_data.get('num_shifts', '')
    email = report_data.get('email', '')
    contact_person = report_data.get('contact_person', '')
    phone = report_data.get('phone', '')
    scope = report_data.get('scope', '')
    ea_code = report_data.get('ea_code', '')
    exclusions = report_data.get('exclusions', '')
    
    audit_team = report_data.get('audit_team', {})
    lead_auditor = audit_team.get('lead_auditor', '')
    auditors = audit_team.get('auditors', [])
    technical_experts = audit_team.get('technical_experts', [])
    audit_duration = report_data.get('audit_duration', '')
    start_date = report_data.get('start_date', '')
    end_date = report_data.get('end_date', '')
    
    organization_brief = report_data.get('organization_brief', '')
    audit_objective = report_data.get('audit_objective', "To evaluate the client's documented system, location planning and readiness for stage 2 audit.")
    audit_criteria = report_data.get('audit_criteria', 'The requirements of a defined normative document or the certified management system requirements')
    
    # Change details
    employee_change = report_data.get('employee_change', '')
    scope_change = report_data.get('scope_change', '')
    integrated_system = report_data.get('integrated_system', '')
    additional_info = report_data.get('additional_info', '')
    man_days_adequate = report_data.get('man_days_adequate', True)
    
    # Attendance
    attendees = report_data.get('attendees', [])
    
    # Findings
    positive_findings = report_data.get('positive_findings', [])
    areas_of_concern = report_data.get('areas_of_concern', [])
    
    # Team leader declarations
    declarations = report_data.get('declarations', {})
    
    # Recommendation
    recommendation = report_data.get('recommendation', '')
    
    # Checklist
    checklist_items = report_data.get('checklist_items', [])
    
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
        c.drawCentredString(width/2, 10, f"Page {page_num} | BAYAN for Verification and Conformity | Stage 1 Audit Report BACF6-10")
    
    def check_page_break(current_y, needed_space=100):
        nonlocal page_num
        if current_y < needed_space:
            draw_footer(page_num)
            c.showPage()
            page_num += 1
            return height - 50
        return current_y
    
    # ============ PAGE 1 ============
    page_num = 1
    
    # Header
    c.setFillColor(primary_color)
    c.rect(0, height - 100, width, 100, fill=True, stroke=False)
    c.setFillColor(report_color)
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
    c.drawCentredString(width/2, height - 35, "STAGE 1 AUDIT REPORT")
    c.setFont('Helvetica', 11)
    c.drawCentredString(width/2, height - 52, "According to the Standard/s: " + (', '.join(standards) if standards else 'ISO'))
    draw_arabic("تقرير تدقيق المرحلة الأولى", width/2 + 80, height - 70, 12, bold=True)
    
    c.setFont('Helvetica', 9)
    c.drawRightString(width - 25, height - 25, "BACF6-10")
    
    y = height - 125
    
    # Organization Details Section
    c.setFillColor(section_color)
    c.setFont('Helvetica-Bold', 11)
    c.drawString(30, y, "1. ORGANIZATION DETAILS / معلومات المنشأة")
    y -= 15
    
    # Organization info table
    org_fields = [
        ("Name of the Organization", organization_name, "اسم المنشأة"),
        ("Address", address, "العنوان"),
        ("Site Address (If any)", site_address, "عنوان الموقع"),
        ("Applicable Standard/s", ', '.join(standards) if standards else '', "المعايير المطبقة"),
        ("No. of Employees", str(num_employees), "عدد الموظفين"),
        ("No. of Shifts", str(num_shifts), "عدد الورديات"),
        ("Email", email, "البريد الإلكتروني"),
        ("Contact Person", contact_person, "شخص الاتصال"),
        ("Telephone/Fax", phone, "الهاتف/الفاكس"),
        ("Scope", scope[:80] if scope else '', "نطاق العمل"),
        ("EA Code/Technical Area", ea_code, "الرمز الفني"),
        ("Exclusions", exclusions[:60] if exclusions else 'None', "الاستثناءات"),
    ]
    
    row_height = 18
    for label, value, ar_label in org_fields:
        c.setFillColor(light_bg)
        c.rect(30, y - row_height, width - 60, row_height, fill=True, stroke=False)
        c.setStrokeColor(colors.grey)
        c.setLineWidth(0.5)
        c.rect(30, y - row_height, width - 60, row_height, fill=False, stroke=True)
        
        c.setFillColor(colors.black)
        c.setFont('Helvetica', 8)
        c.drawString(35, y - row_height + 5, label)
        c.setFont('Helvetica-Bold', 8)
        c.drawString(180, y - row_height + 5, str(value)[:45])
        
        y -= row_height
        y = check_page_break(y, 100)
    
    y -= 10
    
    # Audit Team & Duration
    c.setFillColor(section_color)
    c.setFont('Helvetica-Bold', 10)
    c.drawString(30, y, "Audit Team / فريق التدقيق")
    y -= 15
    
    c.setFillColor(light_bg)
    c.roundRect(30, y - 50, width - 60, 55, 5, fill=True, stroke=False)
    
    c.setFillColor(colors.black)
    c.setFont('Helvetica', 8)
    c.drawString(40, y - 12, f"Lead Auditor: {lead_auditor}")
    c.drawString(40, y - 26, f"Auditor(s): {', '.join(auditors) if auditors else 'N/A'}")
    c.drawString(40, y - 40, f"Technical Expert(s): {', '.join(technical_experts) if technical_experts else 'N/A'}")
    c.drawString(300, y - 12, f"Duration: {audit_duration} man-day(s)")
    c.drawString(300, y - 26, f"Start Date: {start_date}")
    c.drawString(300, y - 40, f"End Date: {end_date}")
    
    y -= 65
    y = check_page_break(y, 150)
    
    # Audit Objective & Criteria
    c.setFillColor(section_color)
    c.setFont('Helvetica-Bold', 10)
    c.drawString(30, y, "Audit Objective / هدف التدقيق")
    y -= 12
    
    c.setFillColor(colors.black)
    c.setFont('Helvetica', 8)
    # Word wrap
    words = audit_objective.split()
    line = ""
    for word in words:
        test = line + " " + word if line else word
        if c.stringWidth(test, 'Helvetica', 8) < width - 80:
            line = test
        else:
            c.drawString(35, y, line)
            y -= 12
            line = word
    if line:
        c.drawString(35, y, line)
        y -= 15
    
    y = check_page_break(y, 120)
    
    # Change Details Section
    c.setFillColor(section_color)
    c.setFont('Helvetica-Bold', 11)
    c.drawString(30, y, "2. CHANGE DETAILS / تفاصيل التغييرات")
    y -= 20
    
    change_fields = [
        ("Any change in employee detail since application?", employee_change or "No", "هل تغير عدد الموظفين؟"),
        ("Any change in Scope since application?", scope_change or "No", "هل تغير النطاق؟"),
        ("Does the client have an integrated system?", integrated_system or "No", "هل لدى العميل نظام متكامل؟"),
        ("Additional Information", additional_info or "None", "معلومات إضافية"),
    ]
    
    for label, value, ar in change_fields:
        c.setFillColor(light_bg)
        c.rect(30, y - 20, width - 60, 20, fill=True, stroke=False)
        c.setFillColor(colors.black)
        c.setFont('Helvetica', 8)
        c.drawString(35, y - 14, label)
        c.setFont('Helvetica-Bold', 8)
        c.drawString(300, y - 14, str(value)[:40])
        y -= 22
    
    # Man-days adequacy
    c.setFillColor(success_color if man_days_adequate else warning_color)
    c.setFont('Helvetica-Bold', 9)
    c.drawString(35, y - 5, f"Are quoted man-days adequate? {'YES' if man_days_adequate else 'NO'}")
    y -= 25
    
    y = check_page_break(y, 150)
    
    # Attendance Sheet
    c.setFillColor(section_color)
    c.setFont('Helvetica-Bold', 11)
    c.drawString(30, y, "3. ATTENDANCE SHEET / قائمة الحضور")
    y -= 20
    
    # Attendance table header
    c.setFillColor(table_header_bg)
    c.rect(30, y - 20, width - 60, 20, fill=True, stroke=False)
    c.setFillColor(colors.white)
    c.setFont('Helvetica-Bold', 9)
    c.drawString(40, y - 14, "NAME OF PERSON")
    c.drawString(280, y - 14, "DESIGNATION")
    y -= 22
    
    for i, attendee in enumerate(attendees[:6]):
        c.setFillColor(light_bg if i % 2 == 0 else colors.white)
        c.rect(30, y - 18, width - 60, 18, fill=True, stroke=False)
        c.setStrokeColor(colors.grey)
        c.rect(30, y - 18, width - 60, 18, fill=False, stroke=True)
        c.setFillColor(colors.black)
        c.setFont('Helvetica', 8)
        c.drawString(40, y - 12, attendee.get('name', '')[:35])
        c.drawString(280, y - 12, attendee.get('designation', '')[:30])
        y -= 18
    
    y -= 15
    y = check_page_break(y, 200)
    
    # Summary of Audit - Positive Findings
    c.setFillColor(section_color)
    c.setFont('Helvetica-Bold', 11)
    c.drawString(30, y, "4. SUMMARY OF AUDIT / ملخص التدقيق")
    y -= 20
    
    c.setFillColor(success_color)
    c.setFont('Helvetica-Bold', 10)
    c.drawString(30, y, "4.1 Positive Findings / النتائج الإيجابية")
    y -= 18
    
    # Positive findings table
    c.setFillColor(table_header_bg)
    c.rect(30, y - 18, width - 60, 18, fill=True, stroke=False)
    c.setFillColor(colors.white)
    c.setFont('Helvetica-Bold', 8)
    c.drawString(35, y - 12, "No.")
    c.drawString(60, y - 12, "Unit/Department/Site")
    c.drawString(200, y - 12, "Positive Findings")
    y -= 20
    
    for i, finding in enumerate(positive_findings[:5]):
        c.setFillColor(light_bg if i % 2 == 0 else colors.white)
        c.rect(30, y - 25, width - 60, 25, fill=True, stroke=False)
        c.setStrokeColor(colors.grey)
        c.rect(30, y - 25, width - 60, 25, fill=False, stroke=True)
        c.setFillColor(colors.black)
        c.setFont('Helvetica', 8)
        c.drawString(35, y - 15, str(i + 1))
        c.drawString(60, y - 15, finding.get('department', '')[:25])
        c.drawString(200, y - 15, finding.get('finding', '')[:50])
        y -= 25
    
    y -= 15
    y = check_page_break(y, 200)
    
    # Areas of Concern
    c.setFillColor(warning_color)
    c.setFont('Helvetica-Bold', 10)
    c.drawString(30, y, "4.2 Areas of Concern / مجالات القلق")
    y -= 5
    
    # Rating legend
    c.setFillColor(colors.black)
    c.setFont('Helvetica', 7)
    c.drawString(35, y - 10, "Rating: 1 = Opportunities for improvement | 2 = Probably rated as nonconformity in Stage 2 | 3 = Not ready for certification")
    y -= 20
    
    # Concerns table
    c.setFillColor(table_header_bg)
    c.rect(30, y - 18, width - 60, 18, fill=True, stroke=False)
    c.setFillColor(colors.white)
    c.setFont('Helvetica-Bold', 8)
    c.drawString(35, y - 12, "No.")
    c.drawString(55, y - 12, "Unit/Department")
    c.drawString(160, y - 12, "Areas of Concern")
    c.drawString(width - 75, y - 12, "Rating")
    y -= 20
    
    for i, concern in enumerate(areas_of_concern[:5]):
        c.setFillColor(light_bg if i % 2 == 0 else colors.white)
        c.rect(30, y - 25, width - 60, 25, fill=True, stroke=False)
        c.setStrokeColor(colors.grey)
        c.rect(30, y - 25, width - 60, 25, fill=False, stroke=True)
        c.setFillColor(colors.black)
        c.setFont('Helvetica', 8)
        c.drawString(35, y - 15, str(i + 1))
        c.drawString(55, y - 15, concern.get('department', '')[:20])
        c.drawString(160, y - 15, concern.get('concern', '')[:45])
        
        rating = concern.get('rating', 1)
        rating_color = success_color if rating == 1 else (warning_color if rating == 2 else report_color)
        c.setFillColor(rating_color)
        c.setFont('Helvetica-Bold', 10)
        c.drawCentredString(width - 55, y - 15, str(rating))
        y -= 25
    
    y -= 15
    y = check_page_break(y, 200)
    
    # Team Leader Declaration
    c.setFillColor(section_color)
    c.setFont('Helvetica-Bold', 11)
    c.drawString(30, y, "5. TEAM LEADER DECLARATION / إعلان قائد الفريق")
    y -= 20
    
    declaration_items = [
        ("sampling", "Auditing is based on a sampling process of the available information"),
        ("combined", "Audit is combined, joint or integrated"),
        ("corrective_actions", "The effectiveness of corrective actions taken regarding previous audit findings"),
        ("outcomes_effective", "Outcomes are effective and complying"),
        ("internal_audit", "The internal audit and management review process are planned and effective"),
        ("scope_appropriate", "The scope of certification is appropriate"),
        ("capability", "The capability of the management system to meet applicable requirements"),
        ("objectives_fulfilled", "The audit objectives have been fulfilled and achieved"),
    ]
    
    for key, text in declaration_items:
        checked = declarations.get(key, False)
        c.setFillColor(light_bg)
        c.rect(30, y - 16, width - 60, 16, fill=True, stroke=False)
        
        # Checkbox
        c.setStrokeColor(colors.black)
        c.rect(35, y - 14, 10, 10, fill=False, stroke=True)
        if checked:
            c.setFillColor(success_color)
            c.setFont('Helvetica-Bold', 10)
            c.drawString(36, y - 12, "✓")
        
        c.setFillColor(colors.black)
        c.setFont('Helvetica', 8)
        c.drawString(50, y - 11, text[:75])
        y -= 18
        y = check_page_break(y, 100)
    
    y -= 10
    
    # Recommendation
    c.setFillColor(section_color)
    c.setFont('Helvetica-Bold', 11)
    c.drawString(30, y, "6. RECOMMENDATION / التوصية")
    y -= 20
    
    recommendations = [
        ("proceed", "Recommended proceeding with Stage 2 (within 60 days)", success_color),
        ("not_proceed", "Recommend not proceeding to Stage 2 until audit evidence submitted", warning_color),
        ("further_stage1", "Recommend not proceeding without a further Stage 1 visit", report_color),
    ]
    
    for key, text, color in recommendations:
        selected = recommendation == key
        c.setFillColor(color if selected else light_bg)
        c.rect(30, y - 20, width - 60, 20, fill=True, stroke=False)
        
        c.setStrokeColor(colors.black)
        c.circle(40, y - 10, 5, fill=False, stroke=True)
        if selected:
            c.setFillColor(colors.white if selected else colors.black)
            c.circle(40, y - 10, 3, fill=True, stroke=False)
        
        c.setFillColor(colors.white if selected else colors.black)
        c.setFont('Helvetica-Bold' if selected else 'Helvetica', 9)
        c.drawString(50, y - 14, text)
        y -= 22
    
    y -= 15
    y = check_page_break(y, 150)
    
    # Lead Auditor Authorization
    c.setFillColor(primary_color)
    c.roundRect(30, y - 60, width - 60, 65, 5, fill=True, stroke=False)
    c.setFillColor(colors.white)
    c.setFont('Helvetica-Bold', 10)
    c.drawString(40, y - 15, "Lead Auditor Authorization / توقيع رئيس فريق التدقيق")
    c.setFont('Helvetica', 9)
    c.drawString(40, y - 35, f"Name: {lead_auditor}")
    c.drawString(300, y - 35, f"Date: {end_date}")
    c.drawString(40, y - 50, "Signature: _______________________")
    
    y -= 80
    y = check_page_break(y, 250)
    
    # Audit Checklist
    c.setFillColor(section_color)
    c.setFont('Helvetica-Bold', 11)
    c.drawString(30, y, "7. AUDIT CHECKLIST / قائمة فحص التدقيق")
    y -= 20
    
    # Checklist header
    c.setFillColor(table_header_bg)
    c.rect(30, y - 20, width - 60, 20, fill=True, stroke=False)
    c.setFillColor(colors.white)
    c.setFont('Helvetica-Bold', 8)
    c.drawString(35, y - 14, "REQUIREMENTS")
    c.drawString(340, y - 14, "Status")
    c.drawString(400, y - 14, "Comments")
    y -= 22
    
    for i, item in enumerate(checklist_items):
        y = check_page_break(y, 30)
        
        c.setFillColor(light_bg if i % 2 == 0 else colors.white)
        c.rect(30, y - 28, width - 60, 28, fill=True, stroke=False)
        c.setStrokeColor(colors.grey)
        c.rect(30, y - 28, width - 60, 28, fill=False, stroke=True)
        
        c.setFillColor(colors.black)
        c.setFont('Helvetica', 7)
        req_text = item.get('requirement', '')[:55]
        c.drawString(35, y - 18, req_text)
        
        status = item.get('status', 'C')
        status_color = success_color if status == 'C' else (warning_color if status == 'O' else report_color)
        c.setFillColor(status_color)
        c.setFont('Helvetica-Bold', 9)
        c.drawCentredString(360, y - 18, status)
        
        c.setFillColor(colors.black)
        c.setFont('Helvetica', 7)
        c.drawString(400, y - 18, item.get('comments', '')[:25])
        y -= 30
    
    y -= 10
    
    # End of Report
    y = check_page_break(y, 50)
    c.setFillColor(primary_color)
    c.setFont('Helvetica-Bold', 12)
    c.drawCentredString(width/2, y - 20, "END OF REPORT")
    draw_arabic("نهاية التقرير", width/2 + 60, y - 35, 10, bold=True)
    
    draw_footer(page_num)
    
    c.save()
    
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    return pdf_bytes
