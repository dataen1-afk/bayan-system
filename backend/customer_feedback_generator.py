"""
Customer Feedback (BAC-F6-16) PDF Generator
Generates bilingual (Arabic/English) PDF for customer satisfaction survey results.
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

def draw_star_rating(c, x, y, rating, max_rating=5, size=10):
    """Draw star rating visualization"""
    for i in range(max_rating):
        if i < rating:
            c.setFillColor(HexColor("#f59e0b"))  # Gold for filled
        else:
            c.setFillColor(HexColor("#d1d5db"))  # Gray for empty
        # Draw a simple circle instead of star for simplicity
        c.circle(x + i * (size + 3), y + size/2, size/2.5, fill=1, stroke=0)
    c.setFillColor(black)

def generate_customer_feedback_pdf(data: dict, output_path: str = None) -> str:
    """Generate Customer Feedback PDF"""
    
    if output_path is None:
        contracts_dir = Path(__file__).parent / "contracts"
        contracts_dir.mkdir(exist_ok=True)
        output_path = str(contracts_dir / f"customer_feedback_{data.get('id', 'unknown')}.pdf")
    
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4
    
    # Colors
    primary_color = HexColor("#1e3a5f")
    secondary_color = HexColor("#2c5282")
    light_bg = HexColor("#f7fafc")
    excellent_color = HexColor("#10b981")
    good_color = HexColor("#3b82f6")
    average_color = HexColor("#f59e0b")
    poor_color = HexColor("#ef4444")
    
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
        c.drawString(100, height - 35, "Customer Feedback Survey")
        
        c.setFont("Amiri-Bold", 14)
        arabic_title = reshape_arabic("استبيان رضا العملاء")
        c.drawRightString(width - 30, height - 35, arabic_title)
        
        c.setFont("Helvetica", 10)
        c.drawString(100, height - 55, "BAC-F6-16")
        
        c.setFont("Amiri", 10)
        c.drawRightString(width - 30, height - 55, reshape_arabic("نموذج رقم BAC-F6-16"))
    
    def draw_footer():
        """Draw page footer"""
        c.setFillColor(primary_color)
        c.rect(0, 0, width, 30, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont("Helvetica", 8)
        c.drawString(30, 12, "BAYAN Auditing & Conformity - Customer Feedback")
        c.drawRightString(width - 30, 12, reshape_arabic("بيان للتدقيق والمطابقة - ملاحظات العملاء"))
    
    draw_header()
    draw_footer()
    
    y = height - 100
    
    # Intro text
    c.setFillColor(black)
    c.setFont("Helvetica", 9)
    intro_text = "Thank you for taking the time to provide feedback on our certification services."
    c.drawString(30, y, intro_text)
    c.setFont("Amiri", 9)
    c.drawRightString(width - 30, y - 15, reshape_arabic("شكراً لك على الوقت الذي خصصته لتقديم ملاحظاتك حول خدمات الاعتماد لدينا."))
    
    y -= 40
    
    # Client Information Section
    c.setFillColor(secondary_color)
    c.rect(30, y - 25, width - 60, 25, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(40, y - 18, "Audit Information")
    c.setFont("Amiri-Bold", 11)
    c.drawRightString(width - 40, y - 18, reshape_arabic("معلومات التدقيق"))
    
    y -= 35
    
    info_fields = [
        ("Organization:", "المنظمة:", data.get('organization_name', '')),
        ("Audit Type:", "نوع التدقيق:", data.get('audit_type', '')),
        ("Audit Standard:", "معيار التدقيق:", ', '.join(data.get('standards', []))),
        ("Audit Date:", "تاريخ التدقيق:", data.get('audit_date', '')),
        ("Lead Auditor:", "المدقق الرئيسي:", data.get('lead_auditor', '')),
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
    
    y -= 25
    
    # Rating Scale Legend
    c.setFillColor(HexColor("#e2e8f0"))
    c.rect(30, y - 20, width - 60, 20, fill=1, stroke=0)
    c.setFillColor(black)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(40, y - 14, "Rating Scale: 5=Excellent, 4=Very Good, 3=Good, 2=Average, 1=Poor, N/A=Not Applicable")
    c.setFont("Amiri", 8)
    c.drawRightString(width - 40, y - 14, reshape_arabic("مقياس التقييم: 5=ممتاز، 4=جيد جداً، 3=جيد، 2=متوسط، 1=ضعيف"))
    
    y -= 30
    
    # Feedback Questions by Category
    questions = data.get('questions', [])
    
    # Default questions if not provided
    default_questions = [
        {"category": "BAC Office", "category_ar": "مكتب بيان", "question": "Responsiveness to your enquiries - Promptness", "question_ar": "الاستجابة لاستفساراتكم - السرعة"},
        {"category": "BAC Office", "category_ar": "مكتب بيان", "question": "Accuracy of the quotes communicated to you", "question_ar": "دقة عروض الأسعار المقدمة لكم"},
        {"category": "BAC Office", "category_ar": "مكتب بيان", "question": "Handling of your Complaint(s)", "question_ar": "التعامل مع شكواكم"},
        {"category": "Audit Preparation", "category_ar": "التحضير للتدقيق", "question": "The audit Plan was sent sufficiently in advance", "question_ar": "تم إرسال خطة التدقيق مسبقاً بوقت كافٍ"},
        {"category": "Audit Preparation", "category_ar": "التحضير للتدقيق", "question": "The audit team was well prepared for audit", "question_ar": "كان فريق التدقيق مستعداً جيداً للتدقيق"},
        {"category": "Punctuality", "category_ar": "الالتزام بالمواعيد", "question": "The audit carried out as per the programme", "question_ar": "تم التدقيق وفقاً للبرنامج"},
        {"category": "Audit", "category_ar": "التدقيق", "question": "Opening and closing meetings were professional", "question_ar": "كانت الاجتماعات الافتتاحية والختامية احترافية"},
        {"category": "Audit", "category_ar": "التدقيق", "question": "Questions asked were relevant and easy to understand", "question_ar": "كانت الأسئلة ذات صلة وسهلة الفهم"},
        {"category": "Audit", "category_ar": "التدقيق", "question": "The audit team gave enough explanation for your questions", "question_ar": "قدم فريق التدقيق شرحاً كافياً لأسئلتكم"},
        {"category": "Audit", "category_ar": "التدقيق", "question": "The audit team was fair and impartial", "question_ar": "كان فريق التدقيق عادلاً ومحايداً"},
        {"category": "Ethics", "category_ar": "الأخلاقيات", "question": "The audit team concentrated on the audit", "question_ar": "ركز فريق التدقيق على التدقيق"},
        {"category": "Ethics", "category_ar": "الأخلاقيات", "question": "The audit team didn't make unreasonable demands", "question_ar": "لم يقدم فريق التدقيق طلبات غير معقولة"},
        {"category": "Effectiveness", "category_ar": "الفعالية", "question": "Issues found were helpful for improving your system", "question_ar": "كانت النتائج مفيدة لتحسين نظامكم"},
    ]
    
    items_to_render = questions if questions else default_questions
    current_category = ""
    
    for idx, item in enumerate(items_to_render):
        if y < 100:
            c.showPage()
            draw_header()
            draw_footer()
            y = height - 100
        
        item_category = item.get('category', '')
        if item_category != current_category:
            current_category = item_category
            c.setFillColor(secondary_color)
            c.rect(30, y - 18, width - 60, 18, fill=1, stroke=0)
            c.setFillColor(white)
            c.setFont("Helvetica-Bold", 9)
            c.drawString(40, y - 13, item_category)
            c.setFont("Amiri-Bold", 9)
            c.drawRightString(width - 40, y - 13, reshape_arabic(item.get('category_ar', '')))
            y -= 25
        
        # Question
        c.setFillColor(black)
        c.setFont("Helvetica", 8)
        question_text = f"{idx + 1}. {item.get('question', '')}"[:70]
        c.drawString(40, y - 5, question_text)
        
        # Rating
        rating = item.get('rating', 0)
        if rating and rating != 'na':
            try:
                rating_int = int(rating)
                draw_star_rating(c, 400, y - 10, rating_int)
                c.setFont("Helvetica-Bold", 9)
                c.drawString(470, y - 5, f"({rating_int}/5)")
            except:
                c.setFont("Helvetica", 9)
                c.drawString(400, y - 5, "N/A")
        else:
            c.setFont("Helvetica", 9)
            c.drawString(400, y - 5, "N/A")
        
        y -= 18
    
    y -= 20
    
    # Overall Score Section
    if y < 150:
        c.showPage()
        draw_header()
        draw_footer()
        y = height - 100
    
    c.setFillColor(HexColor("#1e3a5f"))
    c.rect(30, y - 60, width - 60, 60, fill=1, stroke=0)
    
    score = data.get('overall_score', 0)
    evaluation = data.get('evaluation_result', '')
    
    # Determine color based on score
    if score >= 90:
        score_color = excellent_color
        eval_text = "Excellent / ممتاز"
    elif score >= 75:
        score_color = good_color
        eval_text = "Good / جيد"
    elif score >= 60:
        score_color = average_color
        eval_text = "Average / متوسط"
    else:
        score_color = poor_color
        eval_text = "Unsatisfactory / غير مرضٍ"
    
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, y - 20, "Overall Evaluation")
    c.setFont("Amiri-Bold", 12)
    c.drawRightString(width - 40, y - 20, reshape_arabic("التقييم العام"))
    
    c.setFillColor(score_color)
    c.setFont("Helvetica-Bold", 24)
    c.drawString(40, y - 50, f"{score:.1f}%")
    
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(120, y - 50, eval_text)
    
    y -= 80
    
    # Additional Questions
    want_same_team = data.get('want_same_team', None)
    if want_same_team is not None:
        c.setFillColor(light_bg)
        c.rect(30, y - 25, width - 60, 25, fill=1, stroke=0)
        c.setFillColor(black)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(40, y - 17, "Do you want this audit team to assess your system next time?")
        c.setFont("Helvetica", 9)
        answer = "Yes" if want_same_team else "No"
        c.drawString(350, y - 17, answer)
        y -= 35
    
    # Suggestions
    suggestions = data.get('suggestions', '')
    if suggestions:
        c.setFillColor(secondary_color)
        c.rect(30, y - 20, width - 60, 20, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(40, y - 14, "Suggestions / اقتراحات")
        y -= 30
        
        c.setFillColor(light_bg)
        c.rect(30, y - 50, width - 60, 50, fill=1, stroke=0)
        c.setFillColor(black)
        c.setFont("Helvetica", 9)
        # Word wrap suggestions
        lines = []
        words = suggestions.split()
        current_line = ""
        for word in words:
            if len(current_line + " " + word) < 80:
                current_line = (current_line + " " + word).strip()
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        
        for i, line in enumerate(lines[:3]):
            c.drawString(40, y - 10 - i * 12, line)
        y -= 60
    
    # Customer Signature Section
    c.setFillColor(secondary_color)
    c.rect(30, y - 20, width - 60, 20, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(40, y - 14, "Customer Information / معلومات العميل")
    y -= 30
    
    c.setFillColor(light_bg)
    c.rect(30, y - 50, width - 60, 50, fill=1, stroke=0)
    
    c.setFillColor(black)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(40, y - 15, "Name:")
    c.setFont("Helvetica", 9)
    c.drawString(100, y - 15, data.get('respondent_name', ''))
    
    c.setFont("Helvetica-Bold", 9)
    c.drawString(250, y - 15, "Designation:")
    c.setFont("Helvetica", 9)
    c.drawString(320, y - 15, data.get('respondent_designation', ''))
    
    c.setFont("Helvetica-Bold", 9)
    c.drawString(40, y - 35, "Signature:")
    c.line(100, y - 38, 200, y - 38)
    
    c.setFont("Helvetica-Bold", 9)
    c.drawString(250, y - 35, "Date:")
    c.setFont("Helvetica", 9)
    c.drawString(290, y - 35, data.get('submission_date', ''))
    
    y -= 70
    
    # Internal Review Section
    if data.get('reviewed_by'):
        c.setFillColor(HexColor("#374151"))
        c.rect(30, y - 20, width - 60, 20, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(40, y - 14, "Internal Review (BAC Use Only)")
        y -= 30
        
        c.setFillColor(HexColor("#f3f4f6"))
        c.rect(30, y - 40, width - 60, 40, fill=1, stroke=0)
        
        c.setFillColor(black)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(40, y - 15, "Reviewed By:")
        c.setFont("Helvetica", 9)
        c.drawString(120, y - 15, data.get('reviewed_by', ''))
        
        c.setFont("Helvetica-Bold", 9)
        c.drawString(250, y - 15, "Review Date:")
        c.setFont("Helvetica", 9)
        c.drawString(330, y - 15, data.get('review_date', ''))
        
        if data.get('review_comments'):
            c.setFont("Helvetica-Bold", 9)
            c.drawString(40, y - 30, "Comments:")
            c.setFont("Helvetica", 9)
            c.drawString(120, y - 30, data.get('review_comments', '')[:60])
    
    c.save()
    return output_path


if __name__ == "__main__":
    test_data = {
        "id": "test-001",
        "organization_name": "Test Manufacturing Co.",
        "audit_type": "Initial Certification",
        "standards": ["ISO 9001:2015"],
        "audit_date": "2026-02-15",
        "lead_auditor": "Ahmed Ali",
        "overall_score": 85.5,
        "evaluation_result": "good",
        "want_same_team": True,
        "suggestions": "Great service overall. Would appreciate more detailed reports.",
        "respondent_name": "Mohammed Hassan",
        "respondent_designation": "Quality Manager",
        "submission_date": "2026-02-20",
        "reviewed_by": "Admin User",
        "review_date": "2026-02-21",
        "questions": []
    }
    
    pdf_path = generate_customer_feedback_pdf(test_data, "test_customer_feedback.pdf")
    print(f"Generated: {pdf_path}")
