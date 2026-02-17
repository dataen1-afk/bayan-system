"""
Job Order PDF Generator (BACF6-06)
Generates a professional bilingual PDF for Job Orders - auditor appointments.
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

ROOT_DIR = Path(__file__).parent

def generate_job_order_pdf(job_order_data: dict) -> bytes:
    """
    Generate a professional bilingual Job Order PDF (BACF6-06).
    
    Args:
        job_order_data: Dictionary containing job order data
    
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
    accent_color = colors.HexColor('#2563eb')
    success_color = colors.HexColor('#059669')
    
    # Extract data
    auditor_name = job_order_data.get('auditor_name', '')
    auditor_name_ar = job_order_data.get('auditor_name_ar', '')
    auditor_email = job_order_data.get('auditor_email', '')
    position = job_order_data.get('position', 'Auditor')  # Auditor, Lead Auditor, Technical Expert
    
    # Client/Audit details (from Audit Program)
    organization_name = job_order_data.get('organization_name', '')
    organization_address = job_order_data.get('organization_address', '')
    total_employees = job_order_data.get('total_employees', 0)
    phone = job_order_data.get('phone', '')
    scope = job_order_data.get('scope_of_services', '')
    standards = job_order_data.get('standards', [])
    audit_type = job_order_data.get('audit_type', '')
    audit_date = job_order_data.get('audit_date', '')
    client_ref = job_order_data.get('client_ref', '')
    
    # Approval
    certification_manager = job_order_data.get('certification_manager', '')
    manager_approval_date = job_order_data.get('manager_approval_date', '')
    
    # Auditor confirmation
    auditor_confirmed = job_order_data.get('auditor_confirmed', False)
    auditor_confirmation_date = job_order_data.get('auditor_confirmation_date', '')
    auditor_signature = job_order_data.get('auditor_signature', '')
    unable_reason = job_order_data.get('unable_reason', '')
    
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
    
    def draw_footer():
        c.setFillColor(primary_color)
        c.rect(0, 0, width, 25, fill=True, stroke=False)
        c.setFillColor(colors.white)
        c.setFont('Helvetica', 8)
        c.drawCentredString(width/2, 10, "BAYAN Auditing & Conformity | Job Order BACF6-06")
    
    # ============ PAGE 1 - APPOINTMENT ============
    
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
    c.drawCentredString(width/2, height - 35, "JOB ORDER")
    c.setFont('Helvetica', 11)
    c.drawCentredString(width/2, height - 52, "Internal Audit Plan - Auditor Appointment")
    draw_arabic("أمر العمل - تعيين المدقق", width/2 + 80, height - 70, 12, bold=True)
    
    # Form reference
    c.setFont('Helvetica', 9)
    c.drawRightString(width - 25, height - 25, "BACF6-06")
    
    y = height - 120
    
    # Appointment Section
    c.setFillColor(section_color)
    c.setFont('Helvetica-Bold', 12)
    c.drawString(30, y, "Appointment")
    draw_arabic("التعيين", width - 30, y, 11, bold=True, right_align=True)
    y -= 25
    
    # Appointment letter
    c.setFillColor(colors.black)
    c.setFont('Helvetica', 10)
    
    # Dear Mr./Ms.
    c.drawString(30, y, f"Dear {auditor_name},")
    if auditor_name_ar:
        draw_arabic(f"عزيزي {auditor_name_ar}،", width - 30, y, 10, right_align=True)
    y -= 20
    
    # Position mapping
    position_ar = {
        'Auditor': 'مدقق',
        'Lead Auditor': 'مدقق رئيسي',
        'Technical Expert': 'خبير فني'
    }.get(position, 'مدقق')
    
    c.drawString(30, y, f"We appoint you for the position of {position} for conducting the following audit:")
    draw_arabic(f"نعينك في منصب {position_ar} لإجراء التدقيق التالي:", width - 30, y, 9, right_align=True)
    y -= 30
    
    # Client/Audit Details Box
    c.setFillColor(light_bg)
    c.roundRect(30, y - 180, width - 60, 185, 8, fill=True, stroke=False)
    c.setStrokeColor(section_color)
    c.setLineWidth(1)
    c.roundRect(30, y - 180, width - 60, 185, 8, fill=False, stroke=True)
    
    # Details header
    c.setFillColor(section_color)
    c.setFont('Helvetica-Bold', 10)
    c.drawString(40, y - 15, "Audit Details / تفاصيل التدقيق")
    
    # Two column layout for details
    left_col = 45
    right_col = width/2 + 20
    c.setFillColor(colors.black)
    c.setFont('Helvetica', 9)
    
    details_y = y - 35
    line_height = 18
    
    # Left column
    c.setFont('Helvetica', 8)
    c.setFillColor(colors.grey)
    c.drawString(left_col, details_y, "Client Ref / مرجع العميل:")
    c.setFillColor(colors.black)
    c.setFont('Helvetica-Bold', 9)
    c.drawString(left_col + 110, details_y, client_ref or "N/A")
    details_y -= line_height
    
    c.setFont('Helvetica', 8)
    c.setFillColor(colors.grey)
    c.drawString(left_col, details_y, "Company Name / اسم الشركة:")
    c.setFillColor(colors.black)
    c.setFont('Helvetica-Bold', 9)
    c.drawString(left_col + 120, details_y, organization_name[:35] if organization_name else "N/A")
    details_y -= line_height
    
    c.setFont('Helvetica', 8)
    c.setFillColor(colors.grey)
    c.drawString(left_col, details_y, "Address / العنوان:")
    c.setFillColor(colors.black)
    c.setFont('Helvetica', 8)
    c.drawString(left_col + 80, details_y, organization_address[:40] if organization_address else "N/A")
    details_y -= line_height
    
    c.setFont('Helvetica', 8)
    c.setFillColor(colors.grey)
    c.drawString(left_col, details_y, "No. of Employees / عدد الموظفين:")
    c.setFillColor(colors.black)
    c.setFont('Helvetica-Bold', 9)
    c.drawString(left_col + 130, details_y, str(total_employees) if total_employees else "N/A")
    details_y -= line_height
    
    c.setFont('Helvetica', 8)
    c.setFillColor(colors.grey)
    c.drawString(left_col, details_y, "Telephone / الهاتف:")
    c.setFillColor(colors.black)
    c.setFont('Helvetica', 9)
    c.drawString(left_col + 90, details_y, phone or "N/A")
    
    # Right column
    details_y = y - 35
    
    c.setFont('Helvetica', 8)
    c.setFillColor(colors.grey)
    c.drawString(right_col, details_y, "Standards / المعايير:")
    c.setFillColor(colors.black)
    c.setFont('Helvetica-Bold', 9)
    standards_str = ', '.join(standards) if standards else "N/A"
    c.drawString(right_col + 90, details_y, standards_str[:30])
    details_y -= line_height
    
    c.setFont('Helvetica', 8)
    c.setFillColor(colors.grey)
    c.drawString(right_col, details_y, "Audit Type / نوع التدقيق:")
    c.setFillColor(colors.black)
    c.setFont('Helvetica-Bold', 9)
    c.drawString(right_col + 100, details_y, audit_type or "N/A")
    details_y -= line_height
    
    c.setFont('Helvetica', 8)
    c.setFillColor(colors.grey)
    c.drawString(right_col, details_y, "Audit Date / تاريخ التدقيق:")
    c.setFillColor(colors.black)
    c.setFont('Helvetica-Bold', 9)
    c.drawString(right_col + 105, details_y, audit_date or "N/A")
    details_y -= line_height
    
    c.setFont('Helvetica', 8)
    c.setFillColor(colors.grey)
    c.drawString(right_col, details_y, "Scope / النطاق:")
    c.setFillColor(colors.black)
    c.setFont('Helvetica', 8)
    scope_display = scope[:50] + "..." if scope and len(scope) > 50 else (scope or "N/A")
    c.drawString(right_col + 70, details_y, scope_display)
    
    y -= 200
    
    # Manager Approval Section
    c.setFillColor(section_color)
    c.setFont('Helvetica-Bold', 11)
    c.drawString(30, y, "Issued By / صادر من")
    y -= 25
    
    c.setFillColor(light_bg)
    c.roundRect(30, y - 50, width/2 - 40, 55, 5, fill=True, stroke=False)
    
    c.setFillColor(colors.black)
    c.setFont('Helvetica', 9)
    c.drawString(40, y - 15, f"Certification Manager / مدير الاعتماد:")
    c.setFont('Helvetica-Bold', 10)
    c.drawString(40, y - 32, certification_manager or "________________________")
    c.setFont('Helvetica', 9)
    c.drawString(40, y - 48, f"Date / التاريخ: {manager_approval_date or '________________'}")
    
    y -= 80
    
    # ============ AUDITOR DECLARATION SECTION ============
    
    c.setFillColor(section_color)
    c.setFont('Helvetica-Bold', 12)
    c.drawString(30, y, "Confirmation / Declaration of Appointment")
    draw_arabic("تأكيد / إقرار التعيين", width - 30, y, 11, bold=True, right_align=True)
    y -= 25
    
    # Declaration box
    c.setFillColor(light_bg)
    c.roundRect(30, y - 200, width - 60, 205, 8, fill=True, stroke=False)
    
    c.setFillColor(colors.black)
    c.setFont('Helvetica', 9)
    
    decl_y = y - 15
    
    # Declaration text
    c.drawString(40, decl_y, f"I, {auditor_name or '________________________'}, hereby confirm my agreement of appointment for the position as")
    draw_arabic(f"أنا، {auditor_name_ar or '________________________'}، أؤكد موافقتي على التعيين في منصب", width - 40, decl_y, 8, right_align=True)
    decl_y -= 15
    
    c.setFont('Helvetica-Bold', 9)
    c.drawString(40, decl_y, f"{position} for conducting the stated audit.")
    draw_arabic(f"{position_ar} لإجراء التدقيق المذكور.", width - 40, decl_y, 8, right_align=True)
    decl_y -= 25
    
    c.setFont('Helvetica', 8)
    
    # Declaration points with checkboxes
    declarations = [
        ("I am aware of facts which may influence my independence and objectiveness against the auditee.",
         "أنا على دراية بالحقائق التي قد تؤثر على استقلاليتي وموضوعيتي تجاه الجهة الخاضعة للتدقيق."),
        ("Information and data collected during audit will not be provided to third parties nor used for personal benefits.",
         "المعلومات والبيانات المجمعة أثناء التدقيق لن تُقدم لأطراف ثالثة ولن تُستخدم لمصالح شخصية."),
        ("I confirm that I have no commercial or other interests in the above stated company.",
         "أؤكد أنه ليس لدي مصالح تجارية أو غيرها في الشركة المذكورة أعلاه."),
        ("I have not acted as a consultant for this company within the last two years.",
         "لم أعمل كمستشار لهذه الشركة خلال العامين الماضيين.")
    ]
    
    for eng, ar in declarations:
        # Checkbox
        c.setStrokeColor(section_color)
        c.setLineWidth(1)
        c.rect(40, decl_y - 3, 10, 10, fill=False, stroke=True)
        if auditor_confirmed:
            c.setFillColor(success_color)
            c.setFont('Helvetica-Bold', 10)
            c.drawString(42, decl_y - 1, "✓")
        
        c.setFillColor(colors.black)
        c.setFont('Helvetica', 7)
        c.drawString(55, decl_y, eng[:85])
        decl_y -= 20
    
    decl_y -= 5
    
    # Unable to carry out option
    c.setFont('Helvetica-Bold', 8)
    c.drawString(40, decl_y, "Or I am unable to carry out the assignment because:")
    draw_arabic("أو لا أستطيع تنفيذ المهمة بسبب:", width - 40, decl_y, 7, right_align=True)
    decl_y -= 15
    
    c.setFont('Helvetica', 8)
    unable_display = unable_reason if unable_reason else "________________________________________________"
    c.drawString(40, decl_y, unable_display)
    
    y -= 220
    
    # Auditor Signature Section
    c.setFillColor(success_color if auditor_confirmed else section_color)
    c.roundRect(30, y - 60, width/2 - 40, 65, 5, fill=True, stroke=False)
    
    c.setFillColor(colors.white)
    c.setFont('Helvetica-Bold', 9)
    c.drawString(40, y - 15, "Auditor Signature / توقيع المدقق")
    
    c.setFont('Helvetica', 9)
    c.drawString(40, y - 32, f"Name / الاسم: {auditor_name or '________________'}")
    c.drawString(40, y - 48, f"Date / التاريخ: {auditor_confirmation_date or '________________'}")
    
    # Status indicator
    status_text = "CONFIRMED ✓" if auditor_confirmed else "PENDING"
    status_ar = "مؤكد ✓" if auditor_confirmed else "قيد الانتظار"
    
    c.setFillColor(success_color if auditor_confirmed else colors.orange)
    c.roundRect(width/2 + 10, y - 60, width/2 - 40, 65, 5, fill=True, stroke=False)
    
    c.setFillColor(colors.white)
    c.setFont('Helvetica-Bold', 14)
    c.drawCentredString(width/2 + 10 + (width/2 - 40)/2, y - 30, status_text)
    draw_arabic(status_ar, width/2 + 10 + (width/2 - 40)/2 + 30, y - 50, 12, bold=True)
    
    draw_footer()
    
    # Save
    c.save()
    
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    return pdf_bytes


# For testing
if __name__ == "__main__":
    test_data = {
        "auditor_name": "Ahmed Mohammed",
        "auditor_name_ar": "أحمد محمد",
        "auditor_email": "ahmed@bayan.com",
        "position": "Lead Auditor",
        "organization_name": "Test Company Ltd.",
        "organization_address": "123 Main St, Riyadh, Saudi Arabia",
        "total_employees": 150,
        "phone": "+966 11 123 4567",
        "scope_of_services": "Manufacturing and distribution of industrial equipment",
        "standards": ["ISO 9001", "ISO 14001"],
        "audit_type": "Stage 2",
        "audit_date": "2026-03-15",
        "client_ref": "CR-2026-001",
        "certification_manager": "John Smith",
        "manager_approval_date": "2026-02-15",
        "auditor_confirmed": True,
        "auditor_confirmation_date": "2026-02-16",
    }
    
    pdf_bytes = generate_job_order_pdf(test_data)
    
    output_path = ROOT_DIR / "contracts" / "test_job_order.pdf"
    with open(output_path, 'wb') as f:
        f.write(pdf_bytes)
    print(f"Generated: {output_path}")
