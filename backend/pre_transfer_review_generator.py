"""
Pre-Transfer Review (BAC-F6-17) PDF Generator
Generates bilingual (Arabic/English) PDF for pre-transfer review assessment.
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

def draw_checkbox(c, x, y, checked=False, size=10):
    """Draw a checkbox"""
    c.rect(x, y, size, size, stroke=1, fill=0)
    if checked:
        c.setFont("Helvetica-Bold", 8)
        c.drawString(x + 2, y + 2, "✓")

def generate_pre_transfer_review_pdf(data: dict, output_path: str = None) -> str:
    """Generate Pre-Transfer Review PDF"""
    
    if output_path is None:
        contracts_dir = Path(__file__).parent / "contracts"
        contracts_dir.mkdir(exist_ok=True)
        output_path = str(contracts_dir / f"pre_transfer_review_{data.get('id', 'unknown')}.pdf")
    
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4
    
    # Colors
    primary_color = HexColor("#1e3a5f")
    secondary_color = HexColor("#2c5282")
    light_bg = HexColor("#f7fafc")
    success_color = HexColor("#10b981")
    danger_color = HexColor("#ef4444")
    
    def draw_header():
        """Draw page header"""
        c.setFillColor(primary_color)
        c.rect(0, height - 80, width, 80, fill=1, stroke=0)
        
        # Logo
        logo_path = Path(__file__).parent / "assets" / "bayan-logo.png"
        if logo_path.exists():
            try:
                c.drawImage(str(logo_path), 30, height - 70, width=50, height=50, preserveAspectRatio=True, mask='auto')
            except:
                pass
        
        # Title
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(100, height - 35, "Pre-Transfer Review")
        
        c.setFont("Amiri-Bold", 14)
        arabic_title = reshape_arabic("مراجعة ما قبل النقل")
        c.drawRightString(width - 30, height - 35, arabic_title)
        
        c.setFont("Helvetica", 10)
        c.drawString(100, height - 55, "BAC-F6-17")
        
        c.setFont("Amiri", 10)
        c.drawRightString(width - 30, height - 55, reshape_arabic("نموذج رقم BAC-F6-17"))
    
    def draw_footer():
        """Draw page footer"""
        c.setFillColor(primary_color)
        c.rect(0, 0, width, 30, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont("Helvetica", 8)
        c.drawString(30, 12, "BAYAN Auditing & Conformity - Pre-Transfer Review")
        c.drawRightString(width - 30, 12, reshape_arabic("بيان للتدقيق والمطابقة - مراجعة ما قبل النقل"))
    
    draw_header()
    draw_footer()
    
    y = height - 100
    
    # Client Information Section
    c.setFillColor(secondary_color)
    c.rect(30, y - 25, width - 60, 25, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(40, y - 18, "Client Information")
    c.setFont("Amiri-Bold", 11)
    c.drawRightString(width - 40, y - 18, reshape_arabic("معلومات العميل"))
    
    y -= 35
    
    client_fields = [
        ("Name of Client:", "اسم العميل:", data.get('client_name', '')),
        ("Address:", "العنوان:", data.get('client_address', '')),
        ("Contact Telephone:", "رقم الهاتف:", data.get('client_phone', '')),
        ("Enquiry Reference No.:", "رقم مرجع الاستفسار:", data.get('enquiry_reference', '')),
    ]
    
    c.setFillColor(light_bg)
    c.rect(30, y - len(client_fields) * 18 - 10, width - 60, len(client_fields) * 18 + 10, fill=1, stroke=0)
    
    for label_en, label_ar, value in client_fields:
        c.setFillColor(black)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(40, y - 5, label_en)
        c.setFont("Helvetica", 9)
        c.drawString(170, y - 5, str(value)[:45])
        c.setFont("Amiri-Bold", 9)
        c.drawRightString(width - 40, y - 5, reshape_arabic(label_ar))
        y -= 18
    
    y -= 20
    
    # Transfer Details Section
    c.setFillColor(secondary_color)
    c.rect(30, y - 25, width - 60, 25, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(40, y - 18, "Transfer Details")
    c.setFont("Amiri-Bold", 11)
    c.drawRightString(width - 40, y - 18, reshape_arabic("تفاصيل النقل"))
    
    y -= 35
    
    transfer_fields = [
        ("Reason for Transfer:", "سبب النقل:", data.get('transfer_reason', '')),
        ("Existing Certification Body:", "جهة الاعتماد الحالية:", data.get('existing_cb', '')),
        ("Certificate Number:", "رقم الشهادة:", data.get('certificate_number', '')),
        ("Validity:", "الصلاحية:", data.get('validity', '')),
        ("Scope of Activities:", "نطاق الأنشطة:", data.get('scope', '')),
        ("Sites Under Scope:", "المواقع ضمن النطاق:", data.get('sites', '')),
        ("EAC Code / Technical Category:", "رمز EAC / الفئة الفنية:", data.get('eac_code', '')),
    ]
    
    c.setFillColor(light_bg)
    c.rect(30, y - len(transfer_fields) * 18 - 10, width - 60, len(transfer_fields) * 18 + 10, fill=1, stroke=0)
    
    for label_en, label_ar, value in transfer_fields:
        c.setFillColor(black)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(40, y - 5, label_en)
        c.setFont("Helvetica", 9)
        value_str = str(value)[:40] if value else '-'
        c.drawString(200, y - 5, value_str)
        c.setFont("Amiri-Bold", 9)
        c.drawRightString(width - 40, y - 5, reshape_arabic(label_ar))
        y -= 18
    
    y -= 20
    
    # Compliance Checklist Section
    c.setFillColor(secondary_color)
    c.rect(30, y - 25, width - 60, 25, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(40, y - 18, "Compliance Checklist")
    c.setFont("Amiri-Bold", 11)
    c.drawRightString(width - 40, y - 18, reshape_arabic("قائمة التحقق من الامتثال"))
    
    y -= 35
    
    # Table header
    c.setFillColor(HexColor("#e2e8f0"))
    c.rect(30, y - 18, width - 60, 18, fill=1, stroke=0)
    c.setFillColor(black)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(40, y - 13, "Item")
    c.drawString(380, y - 13, "Yes")
    c.drawString(420, y - 13, "No")
    c.drawString(460, y - 13, "N/A")
    
    y -= 22
    
    checklist_items = [
        ("suspension_status", "Certificate under suspension?", "الشهادة تحت التعليق؟"),
        ("threat_of_suspension", "Under threat of suspension?", "تحت تهديد بالتعليق؟"),
        ("minor_nc_outstanding", "Any minor non-conformity outstanding?", "هل توجد عدم مطابقة بسيطة معلقة؟"),
        ("major_nc_outstanding", "Any major non-conformity outstanding?", "هل توجد عدم مطابقة كبرى معلقة؟"),
        ("legal_representation", "Engaged in legal representation with statutory bodies?", "مشارك في تمثيل قانوني مع هيئات قانونية؟"),
        ("complaints_handled", "Have complaints been received and appropriately handled?", "هل تم استلام الشكاوى والتعامل معها بشكل مناسب؟"),
        ("within_bac_scope", "Activities fall within BAC accreditation scope?", "الأنشطة ضمن نطاق اعتماد بيان؟"),
        ("previous_reports_available", "Last assessment reports from previous CB available?", "تقارير التقييم السابقة متوفرة؟"),
    ]
    
    checklist_data = data.get('checklist', {})
    
    for key, label_en, label_ar in checklist_items:
        c.setFillColor(light_bg if checklist_items.index((key, label_en, label_ar)) % 2 == 0 else white)
        c.rect(30, y - 16, width - 60, 16, fill=1, stroke=0)
        
        c.setFillColor(black)
        c.setFont("Helvetica", 8)
        c.drawString(40, y - 12, label_en[:55])
        
        value = checklist_data.get(key)
        # Yes checkbox
        draw_checkbox(c, 380, y - 14, value == True, 10)
        # No checkbox
        draw_checkbox(c, 420, y - 14, value == False, 10)
        # N/A checkbox
        draw_checkbox(c, 460, y - 14, value is None, 10)
        
        y -= 18
    
    y -= 20
    
    # Certification Cycle Stage
    c.setFillColor(light_bg)
    c.rect(30, y - 35, width - 60, 35, fill=1, stroke=0)
    c.setFillColor(black)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(40, y - 12, "Stage of Current Certification Cycle:")
    c.setFont("Helvetica", 9)
    c.drawString(40, y - 28, data.get('certification_cycle_stage', '-'))
    
    y -= 50
    
    # Attachments Section
    c.setFillColor(secondary_color)
    c.rect(30, y - 25, width - 60, 25, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(40, y - 18, "Attachments")
    c.setFont("Amiri-Bold", 11)
    c.drawRightString(width - 40, y - 18, reshape_arabic("المرفقات"))
    
    y -= 35
    
    attachments = data.get('attachments', [])
    c.setFillColor(light_bg)
    c.rect(30, y - 40, width - 60, 40, fill=1, stroke=0)
    
    c.setFillColor(black)
    c.setFont("Helvetica", 9)
    
    att_items = [
        ("previous_audit_report", "Audit Report of previous CB", data.get('has_previous_audit_report', False)),
        ("previous_certificates", "Copy of previous existing Certificates", data.get('has_previous_certificates', False)),
    ]
    
    att_y = y - 12
    for key, label, has_item in att_items:
        draw_checkbox(c, 40, att_y - 3, has_item, 10)
        c.drawString(55, att_y, label)
        att_y -= 15
    
    y -= 55
    
    # Evaluation / Certification Decision
    c.setFillColor(HexColor("#1e3a5f"))
    c.rect(30, y - 25, width - 60, 25, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(40, y - 18, "Evaluation / Certification Decision")
    c.setFont("Amiri-Bold", 11)
    c.drawRightString(width - 40, y - 18, reshape_arabic("التقييم / قرار الاعتماد"))
    
    y -= 35
    
    decision = data.get('transfer_decision', '')
    decision_reason = data.get('decision_reason', '')
    
    c.setFillColor(light_bg)
    c.rect(30, y - 70, width - 60, 70, fill=1, stroke=0)
    
    c.setFillColor(black)
    c.setFont("Helvetica", 9)
    c.drawString(40, y - 12, "The Prerequisites for the Transfer of Certificate(s) are fulfilled:")
    
    # Decision checkboxes
    c.setFont("Helvetica-Bold", 10)
    draw_checkbox(c, 40, y - 32, decision == 'approved', 12)
    c.setFillColor(success_color if decision == 'approved' else black)
    c.drawString(58, y - 30, "Yes - Approved")
    
    draw_checkbox(c, 180, y - 32, decision == 'rejected', 12)
    c.setFillColor(danger_color if decision == 'rejected' else black)
    c.drawString(198, y - 30, "No - Rejected")
    
    if decision == 'rejected' and decision_reason:
        c.setFillColor(black)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(40, y - 50, "Reason for rejection:")
        c.setFont("Helvetica", 9)
        c.drawString(150, y - 50, decision_reason[:50])
    
    y -= 85
    
    # Approval Section
    c.setFillColor(secondary_color)
    c.rect(30, y - 25, width - 60, 25, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(40, y - 18, "Review and Approval")
    c.setFont("Amiri-Bold", 11)
    c.drawRightString(width - 40, y - 18, reshape_arabic("المراجعة والموافقة"))
    
    y -= 35
    
    c.setFillColor(light_bg)
    c.rect(30, y - 60, width - 60, 60, fill=1, stroke=0)
    
    # Two columns for reviewer and approver
    c.setFillColor(black)
    
    # Reviewer (left column)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(40, y - 12, "Reviewed by:")
    c.setFont("Helvetica", 9)
    c.drawString(40, y - 26, data.get('reviewed_by', ''))
    c.setFont("Helvetica-Oblique", 8)
    c.drawString(40, y - 40, "Quality Manager / Lead Auditor")
    c.setFont("Helvetica", 8)
    c.drawString(40, y - 52, f"Date: {data.get('review_date', '')}")
    
    # Approver (right column)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(300, y - 12, "Approved by:")
    c.setFont("Helvetica", 9)
    c.drawString(300, y - 26, data.get('approved_by', ''))
    c.setFont("Helvetica-Oblique", 8)
    c.drawString(300, y - 40, "Certification Manager")
    c.setFont("Helvetica", 8)
    c.drawString(300, y - 52, f"Date: {data.get('approval_date', '')}")
    
    c.save()
    return output_path


if __name__ == "__main__":
    test_data = {
        "id": "test-001",
        "client_name": "Test Manufacturing Co.",
        "client_address": "123 Industrial Area, Riyadh",
        "client_phone": "+966 12 345 6789",
        "enquiry_reference": "ENQ-2026-001",
        "transfer_reason": "Better service and coverage",
        "existing_cb": "ABC Certification",
        "certificate_number": "ABC-2024-12345",
        "validity": "2024-01-01 to 2027-01-01",
        "scope": "Manufacturing of electronic components",
        "sites": "Main factory, Warehouse",
        "eac_code": "19",
        "checklist": {
            "suspension_status": False,
            "threat_of_suspension": False,
            "minor_nc_outstanding": False,
            "major_nc_outstanding": False,
            "legal_representation": False,
            "complaints_handled": True,
            "within_bac_scope": True,
            "previous_reports_available": True
        },
        "certification_cycle_stage": "After 1st Surveillance Audit",
        "has_previous_audit_report": True,
        "has_previous_certificates": True,
        "transfer_decision": "approved",
        "decision_reason": "",
        "reviewed_by": "Ahmed Ali",
        "review_date": "2026-02-18",
        "approved_by": "Mohammed Hassan",
        "approval_date": "2026-02-19"
    }
    
    pdf_path = generate_pre_transfer_review_pdf(test_data, "test_pre_transfer_review.pdf")
    print(f"Generated: {pdf_path}")
