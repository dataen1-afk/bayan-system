"""
Technical Review and Certification Decision (BAC-F6-15) PDF Generator
Generates bilingual (Arabic/English) PDF for technical review checklist and certification decision.
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
import os

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

def generate_technical_review_pdf(data: dict, output_path: str = None) -> str:
    """Generate Technical Review and Certification Decision PDF"""
    
    if output_path is None:
        contracts_dir = Path(__file__).parent / "contracts"
        contracts_dir.mkdir(exist_ok=True)
        output_path = str(contracts_dir / f"technical_review_{data.get('id', 'unknown')}.pdf")
    
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4
    
    # Colors
    primary_color = HexColor("#1e3a5f")
    secondary_color = HexColor("#2c5282")
    light_bg = HexColor("#f7fafc")
    
    def draw_header(page_num=1):
        """Draw page header"""
        # Header background
        c.setFillColor(primary_color)
        c.rect(0, height - 80, width, 80, fill=1, stroke=0)
        
        # Logo placeholder
        logo_path = Path(__file__).parent / "assets" / "bayan-logo.png"
        if logo_path.exists():
            try:
                c.drawImage(str(logo_path), 30, height - 70, width=50, height=50, preserveAspectRatio=True, mask='auto')
            except:
                pass
        
        # Title
        c.setFillColor(primary_color)
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(width / 2, height - 95, "Technical Review and Certification Decision")
        
        c.setFont("Amiri-Bold", 14)
        arabic_title = reshape_arabic("المراجعة الفنية وقرار الاعتماد")
        c.drawCentredString(width / 2, height - 115, arabic_title)
        
        # Form reference
        c.setFont("Helvetica", 9)
        c.setFillColor(black)
        c.drawRightString(width - 40, height - 25, "BAC-F6-15")
    
    def draw_footer():
        """Draw official BAC footer"""
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
        except:
            pass
        
        info_x = 100
        info_y = footer_y + 12
        c.setFont('Helvetica', 8)
        c.setFillColor(black)
        c.drawString(info_x, info_y, f"Tel: {COMPANY_PHONE}")
        c.drawString(info_x, info_y - 11, f"Web: {COMPANY_WEBSITE}")
        
        c.setFont('Helvetica-Bold', 8)
        c.drawRightString(width - 45, info_y, "Director")
        c.setFont('Helvetica', 8)
        c.drawRightString(width - 45, info_y - 11, "BAYAN AUDITING & CONFORMITY (BAC)")
    
    # Page 1
    draw_header(1)
    draw_footer()
    
    y = height - 140
    
    # Client Information Section
    c.setFillColor(secondary_color)
    c.rect(30, y - 25, width - 60, 25, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(40, y - 18, "Client Information")
    c.setFont("Amiri-Bold", 11)
    c.drawRightString(width - 40, y - 18, reshape_arabic("معلومات العميل"))
    
    y -= 35
    
    # Client info fields
    info_fields = [
        ("Client Name:", "اسم العميل:", data.get('client_name', '')),
        ("Location(s):", "الموقع:", data.get('location', '')),
        ("Scope:", "نطاق العمل:", data.get('scope', '')),
        ("EA Code:", "رمز EA:", data.get('ea_code', '')),
        ("Standard(s):", "المعايير:", ', '.join(data.get('standards', []))),
        ("Audit Type:", "نوع التدقيق:", data.get('audit_type', '')),
        ("Audit Date(s):", "تاريخ التدقيق:", data.get('audit_dates', '')),
    ]
    
    c.setFillColor(light_bg)
    c.rect(30, y - len(info_fields) * 18 - 10, width - 60, len(info_fields) * 18 + 10, fill=1, stroke=0)
    
    for label_en, label_ar, value in info_fields:
        c.setFillColor(black)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(40, y - 5, label_en)
        c.setFont("Helvetica", 9)
        c.drawString(140, y - 5, str(value)[:50])
        
        c.setFont("Amiri-Bold", 9)
        c.drawRightString(width - 40, y - 5, reshape_arabic(label_ar))
        
        y -= 18
    
    y -= 15
    
    # Audit Team Section
    c.setFillColor(secondary_color)
    c.rect(30, y - 25, width - 60, 25, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(40, y - 18, "Audit Team")
    c.setFont("Amiri-Bold", 11)
    c.drawRightString(width - 40, y - 18, reshape_arabic("فريق التدقيق"))
    
    y -= 35
    
    team_members = data.get('audit_team_members', [])
    technical_expert = data.get('technical_expert', '')
    
    c.setFillColor(light_bg)
    c.rect(30, y - 60, width - 60, 60, fill=1, stroke=0)
    
    c.setFillColor(black)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(40, y - 5, "Team Members:")
    c.setFont("Helvetica", 9)
    for i, member in enumerate(team_members[:3]):
        c.drawString(140 + i * 120, y - 5, f"{i+1}. {member[:20]}")
    
    c.setFont("Helvetica-Bold", 9)
    c.drawString(40, y - 25, "Technical Expert:")
    c.setFont("Helvetica", 9)
    c.drawString(140, y - 25, technical_expert[:40])
    
    y -= 75
    
    # Assessment Checklist Section
    c.setFillColor(secondary_color)
    c.rect(30, y - 25, width - 60, 25, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(40, y - 18, "Assessment Checklist")
    c.setFont("Amiri-Bold", 11)
    c.drawRightString(width - 40, y - 18, reshape_arabic("قائمة التقييم"))
    
    y -= 35
    
    # Table header
    c.setFillColor(HexColor("#e2e8f0"))
    c.rect(30, y - 20, width - 60, 20, fill=1, stroke=0)
    c.setFillColor(black)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(40, y - 14, "Items")
    c.drawString(350, y - 14, "Y/N")
    c.drawString(400, y - 14, "Remarks")
    
    y -= 25
    
    # Checklist items
    checklist = data.get('checklist_items', [])
    
    # Define default checklist structure
    default_items = [
        {"category": "General", "item": "Correctness of Name, address, scope, Ref no.", "item_ar": "صحة الاسم والعنوان والنطاق ورقم المرجع"},
        {"category": "General", "item": "Scope Terminology", "item_ar": "مصطلحات النطاق"},
        {"category": "General", "item": "EA Code verification", "item_ar": "التحقق من رمز EA"},
        {"category": "General", "item": "Conformance to audited processes", "item_ar": "المطابقة للعمليات المدققة"},
        {"category": "Application", "item": "Application form complete and signed", "item_ar": "نموذج الطلب مكتمل وموقع"},
        {"category": "Quotation", "item": "Quotation signed by both parties", "item_ar": "عرض السعر موقع من الطرفين"},
        {"category": "Man Days", "item": "Adequacy per IAF guidelines", "item_ar": "الكفاية وفقًا لإرشادات IAF"},
        {"category": "Man Days", "item": "Adequacy on complexity", "item_ar": "الكفاية من حيث التعقيد"},
        {"category": "Audit Team", "item": "Team competent for scope", "item_ar": "الفريق مؤهل للنطاق"},
        {"category": "Stage 1", "item": "Audit plan available and complete", "item_ar": "خطة التدقيق متوفرة ومكتملة"},
        {"category": "Stage 1", "item": "Opening & Closing Meeting attendance", "item_ar": "حضور الاجتماع الافتتاحي والختامي"},
        {"category": "Stage 1", "item": "Audit report covers all areas", "item_ar": "تقرير التدقيق يغطي جميع المجالات"},
        {"category": "Stage 2", "item": "Stage 2 audit plan complete", "item_ar": "خطة تدقيق المرحلة 2 مكتملة"},
        {"category": "Stage 2", "item": "Stage 2 Audit Report correct", "item_ar": "تقرير تدقيق المرحلة 2 صحيح"},
        {"category": "Stage 2", "item": "NC Closure evidence recorded", "item_ar": "دليل إغلاق عدم المطابقة مسجل"},
        {"category": "Other", "item": "Conflict of Interest declaration", "item_ar": "إقرار تضارب المصالح"},
        {"category": "Other", "item": "Customer Feedback reviewed", "item_ar": "مراجعة ملاحظات العميل"},
        {"category": "Other", "item": "Certificate data request reviewed", "item_ar": "مراجعة طلب بيانات الشهادة"},
    ]
    
    # Use provided checklist or default
    items_to_render = checklist if checklist else default_items
    
    current_category = ""
    for item in items_to_render:
        if y < 120:
            c.showPage()
            draw_header(2)
            draw_footer()
            y = height - 100
        
        item_category = item.get('category', '')
        if item_category != current_category:
            current_category = item_category
            c.setFillColor(HexColor("#edf2f7"))
            c.rect(30, y - 15, width - 60, 15, fill=1, stroke=0)
            c.setFillColor(primary_color)
            c.setFont("Helvetica-Bold", 8)
            c.drawString(40, y - 11, current_category)
            y -= 18
        
        c.setFillColor(black)
        c.setFont("Helvetica", 8)
        item_text = item.get('item', '')[:55]
        c.drawString(40, y - 10, item_text)
        
        # Y/N value
        check_value = item.get('checked', None)
        if check_value is True:
            c.setFillColor(HexColor("#38a169"))
            c.drawString(355, y - 10, "Y")
        elif check_value is False:
            c.setFillColor(HexColor("#e53e3e"))
            c.drawString(355, y - 10, "N")
        else:
            c.setFillColor(black)
            c.drawString(355, y - 10, "-")
        
        c.setFillColor(black)
        remarks = item.get('remarks', '')[:25]
        c.drawString(400, y - 10, remarks)
        
        y -= 15
    
    y -= 20
    
    # Technical Reviewer Section
    if y < 200:
        c.showPage()
        draw_header(2)
        draw_footer()
        y = height - 100
    
    c.setFillColor(secondary_color)
    c.rect(30, y - 25, width - 60, 25, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(40, y - 18, "Technical Review")
    c.setFont("Amiri-Bold", 11)
    c.drawRightString(width - 40, y - 18, reshape_arabic("المراجعة الفنية"))
    
    y -= 35
    
    c.setFillColor(light_bg)
    c.rect(30, y - 50, width - 60, 50, fill=1, stroke=0)
    
    c.setFillColor(black)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(40, y - 15, "Technical Reviewer:")
    c.setFont("Helvetica", 9)
    c.drawString(160, y - 15, data.get('technical_reviewer', ''))
    
    c.setFont("Helvetica-Bold", 9)
    c.drawString(40, y - 35, "Review Date:")
    c.setFont("Helvetica", 9)
    c.drawString(160, y - 35, data.get('review_date', ''))
    
    # Arabic labels
    c.setFont("Amiri-Bold", 9)
    c.drawRightString(width - 40, y - 15, reshape_arabic("المراجع الفني:"))
    c.drawRightString(width - 40, y - 35, reshape_arabic("تاريخ المراجعة:"))
    
    y -= 70
    
    # Certification Decision Section
    c.setFillColor(HexColor("#2d3748"))
    c.rect(30, y - 25, width - 60, 25, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, y - 18, "Certification Decision")
    c.setFont("Amiri-Bold", 12)
    c.drawRightString(width - 40, y - 18, reshape_arabic("قرار الاعتماد"))
    
    y -= 35
    
    c.setFillColor(light_bg)
    c.rect(30, y - 80, width - 60, 80, fill=1, stroke=0)
    
    decision = data.get('certification_decision', '')
    
    # Decision checkboxes
    c.setFillColor(black)
    c.setFont("Helvetica-Bold", 10)
    
    decisions = [
        ("issue_certificate", "Issue Certificate", "إصدار الشهادة"),
        ("reject_certificate", "Reject Certificate", "رفض الشهادة"),
        ("needs_review", "Needs Further Technical Review", "يحتاج مراجعة فنية إضافية"),
    ]
    
    checkbox_y = y - 20
    for dec_key, dec_en, dec_ar in decisions:
        is_checked = decision == dec_key
        draw_checkbox(c, 50, checkbox_y - 3, is_checked)
        c.setFont("Helvetica", 10)
        c.drawString(70, checkbox_y, dec_en)
        c.setFont("Amiri", 10)
        c.drawRightString(width - 50, checkbox_y, reshape_arabic(dec_ar))
        checkbox_y -= 22
    
    y -= 100
    
    # Approval Section
    c.setFillColor(secondary_color)
    c.rect(30, y - 25, width - 60, 25, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(40, y - 18, "Approval")
    c.setFont("Amiri-Bold", 11)
    c.drawRightString(width - 40, y - 18, reshape_arabic("الموافقة"))
    
    y -= 35
    
    c.setFillColor(light_bg)
    c.rect(30, y - 60, width - 60, 60, fill=1, stroke=0)
    
    c.setFillColor(black)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(40, y - 15, "Approved By:")
    c.setFont("Helvetica", 9)
    c.drawString(130, y - 15, data.get('approved_by', ''))
    
    c.setFont("Helvetica-Bold", 9)
    c.drawString(40, y - 35, "Signature:")
    c.line(130, y - 38, 250, y - 38)  # Signature line
    
    c.setFont("Helvetica-Bold", 9)
    c.drawString(300, y - 35, "Date:")
    c.setFont("Helvetica", 9)
    c.drawString(340, y - 35, data.get('approval_date', ''))
    
    # Arabic labels
    c.setFont("Amiri-Bold", 9)
    c.drawRightString(width - 40, y - 15, reshape_arabic("الموافق:"))
    c.drawRightString(width - 40, y - 35, reshape_arabic("التوقيع:"))
    
    c.save()
    return output_path


if __name__ == "__main__":
    # Test data
    test_data = {
        "id": "test-001",
        "client_name": "Test Company Ltd.",
        "location": "Riyadh, Saudi Arabia",
        "scope": "Manufacturing of Electronic Components",
        "ea_code": "19",
        "standards": ["ISO 9001:2015"],
        "audit_type": "Initial Certification",
        "audit_dates": "2026-02-15 to 2026-02-17",
        "audit_team_members": ["Ahmed Ali", "Mohammed Hassan"],
        "technical_expert": "Dr. Khalid Ibrahim",
        "technical_reviewer": "Eng. Fahad Al-Saud",
        "review_date": "2026-02-18",
        "certification_decision": "issue_certificate",
        "approved_by": "Abdullah Al-Rashid",
        "approval_date": "2026-02-19",
        "checklist_items": []
    }
    
    pdf_path = generate_technical_review_pdf(test_data, "test_technical_review.pdf")
    print(f"Generated: {pdf_path}")
