"""
Grant Agreement PDF Generator
Generates a professional bilingual PDF for Grant Agreements.
Uses ReportLab with the same styling as other system reports.
Contains all terms and conditions from the official BAYAN template.
Dynamic client data: Organization name, ISO standards, and work locations.
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
import logging
from io import BytesIO

ROOT_DIR = Path(__file__).parent
CONTRACTS_DIR = ROOT_DIR / "contracts"
CONTRACTS_DIR.mkdir(exist_ok=True)

# ============ GRANT AGREEMENT TERMS AND CONDITIONS ============
# These are the fixed terms from the official BAYAN template

AGREEMENT_SECTIONS = {
    "section_3": {
        "title_en": "3. Legal Enforceability",
        "title_ar": "3. القوة القانونية",
        "content_en": [
            "This Agreement is legally binding.",
            "The CB retains full authority to grant, maintain, reduce, suspend, or withdraw certification.",
            "Certification activities shall comply with ISO/IEC 17021-1:2015 and applicable IAF Mandatory Documents.",
            "For clients with multiple sites, this Agreement applies to and covers all certified sites under a single enforceable contract."
        ],
        "content_ar": [
            "هذه الاتفاقية ملزمة قانونياً.",
            "تحتفظ جهة الاعتماد بالسلطة الكاملة لمنح أو الحفاظ على أو تقليل أو تعليق أو سحب الاعتماد.",
            "يجب أن تتوافق أنشطة الاعتماد مع ISO/IEC 17021-1:2015 والوثائق الإلزامية لـ IAF.",
            "بالنسبة للعملاء الذين لديهم مواقع متعددة، تنطبق هذه الاتفاقية وتغطي جميع المواقع المعتمدة بموجب عقد واحد قابل للتنفيذ."
        ]
    },
    "section_4": {
        "title_en": "4. Certification Body Responsibilities",
        "title_ar": "4. مسؤوليات جهة الاعتماد",
        "content_en": [
            "Maintain impartiality and avoid conflicts of interest",
            "Assign competent auditors for the applicable scheme and sector",
            "Notify clients of changes in certification requirements and verify their continued compliance",
            "Respect confidentiality of client data at all organizational levels",
            "Handle appeals, complaints, and misuse of certification transparently",
            "Provide detailed guidance on certification mark use",
            "Inform the client before placing any information in the public domain"
        ],
        "content_ar": [
            "الحفاظ على الحياد وتجنب تضارب المصالح",
            "تعيين مدققين أكفاء للخطة والقطاع المعمول به",
            "إخطار العملاء بالتغييرات في متطلبات الاعتماد والتحقق من استمرار امتثالهم",
            "احترام سرية بيانات العميل على جميع المستويات التنظيمية",
            "التعامل مع الطعون والشكاوى وسوء استخدام الاعتماد بشفافية",
            "تقديم إرشادات تفصيلية حول استخدام علامة الاعتماد",
            "إبلاغ العميل قبل وضع أي معلومات في المجال العام"
        ]
    },
    "section_5": {
        "title_en": "5. Client Responsibilities",
        "title_ar": "5. مسؤوليات العميل",
        "content_en": [
            "Comply with applicable certification requirements",
            "Provide unrestricted access to premises, personnel, documentation, and records for audit purposes",
            "Permit the presence of observers (e.g. accreditation assessors or trainees) when applicable",
            "Maintain system performance and promptly notify the CB of changes affecting certification",
            "Use certification status in accordance with the CB's published requirements",
            "Cease all use of certificates and marks upon suspension, withdrawal, or expiration"
        ],
        "content_ar": [
            "الامتثال لمتطلبات الاعتماد المعمول بها",
            "توفير الوصول غير المقيد إلى المباني والموظفين والوثائق والسجلات لأغراض التدقيق",
            "السماح بحضور المراقبين (مثل مقيمي الاعتماد أو المتدربين) عند الاقتضاء",
            "الحفاظ على أداء النظام وإخطار جهة الاعتماد فوراً بالتغييرات المؤثرة على الاعتماد",
            "استخدام حالة الاعتماد وفقاً للمتطلبات المنشورة لجهة الاعتماد",
            "التوقف عن استخدام جميع الشهادات والعلامات عند التعليق أو السحب أو انتهاء الصلاحية"
        ]
    },
    "section_6": {
        "title_en": "6. Use and Misuse of Certification",
        "title_ar": "6. استخدام وسوء استخدام الاعتماد",
        "content_en": [
            "a) Follow CB guidance when referencing certification in any communication medium",
            "b) Avoid any misleading statements regarding certification",
            "c) Not misuse certification documents or marks",
            "d) Discontinue use of certification marks and references upon withdrawal or suspension",
            "e) Amend marketing content if the scope is reduced",
            "f) Not imply that certification applies to products or services unless explicitly authorized",
            "g) Not reference activities or sites outside the certified scope",
            "h) Avoid damaging the CB's reputation or public trust in the certification system"
        ],
        "content_ar": [
            "أ) اتباع إرشادات جهة الاعتماد عند الإشارة إلى الاعتماد في أي وسيلة اتصال",
            "ب) تجنب أي بيانات مضللة بشأن الاعتماد",
            "ج) عدم إساءة استخدام وثائق أو علامات الاعتماد",
            "د) التوقف عن استخدام علامات ومراجع الاعتماد عند السحب أو التعليق",
            "هـ) تعديل محتوى التسويق إذا تم تقليل النطاق",
            "و) عدم الإيحاء بأن الاعتماد ينطبق على المنتجات أو الخدمات ما لم يكن مصرحاً به صراحة",
            "ز) عدم الإشارة إلى الأنشطة أو المواقع خارج النطاق المعتمد",
            "ح) تجنب الإضرار بسمعة جهة الاعتماد أو الثقة العامة في نظام الاعتماد"
        ]
    },
    "section_7": {
        "title_en": "7. Confidentiality",
        "title_ar": "7. السرية",
        "content_en": [
            "The CB shall manage all information obtained or created during certification as confidential, except where disclosure is:",
            "• Required by law or accreditation body agreement",
            "• Approved by the client in writing",
            "• Based on public information or external sources handled under confidentiality",
            "The CB ensures all staff, contractors, and committees respect confidentiality obligations."
        ],
        "content_ar": [
            "تدير جهة الاعتماد جميع المعلومات التي تم الحصول عليها أو إنشاؤها أثناء الاعتماد باعتبارها سرية، باستثناء الحالات التالية:",
            "• مطلوب بموجب القانون أو اتفاقية هيئة الاعتماد",
            "• موافقة العميل كتابياً",
            "• بناءً على معلومات عامة أو مصادر خارجية يتم التعامل معها بسرية",
            "تضمن جهة الاعتماد احترام جميع الموظفين والمقاولين واللجان لالتزامات السرية."
        ]
    },
    "section_9": {
        "title_en": "9. Fees and Payment",
        "title_ar": "9. الرسوم والدفع",
        "content_en": [
            "All fees are listed in the official proposal.",
            "Special visits (unannounced, follow-up, etc.) are billed separately.",
            "Cancellation less than 3 weeks prior to audit may incur a 20% cancellation fee.",
            "Invoices are payable within 14 days; late payments are subject to 1.5% interest per month.",
            "Certification is issued only after full payment."
        ],
        "content_ar": [
            "جميع الرسوم مدرجة في العرض الرسمي.",
            "الزيارات الخاصة (غير المعلنة، المتابعة، إلخ) تُحسب بشكل منفصل.",
            "الإلغاء قبل أقل من 3 أسابيع من التدقيق قد يترتب عليه رسوم إلغاء بنسبة 20%.",
            "الفواتير مستحقة الدفع خلال 14 يوماً؛ التأخر في السداد يخضع لفائدة 1.5% شهرياً.",
            "يصدر الاعتماد فقط بعد السداد الكامل."
        ]
    },
    "section_10": {
        "title_en": "10. Notification of Changes",
        "title_ar": "10. الإخطار بالتغييرات",
        "content_en": [
            "The Client shall inform the CB without delay of any change affecting certification, including:",
            "• Legal, commercial, or organizational changes (e.g., ownership, mergers)",
            "• Changes in key management or decision-makers",
            "• Changes in contact information or site locations",
            "• Changes in operational scope",
            "• Major modifications to the management system or processes",
            "The CB reserves the right to take appropriate action, including special audits or reassessment."
        ],
        "content_ar": [
            "يجب على العميل إبلاغ جهة الاعتماد دون تأخير بأي تغيير يؤثر على الاعتماد، بما في ذلك:",
            "• التغييرات القانونية أو التجارية أو التنظيمية (مثل الملكية والاندماجات)",
            "• التغييرات في الإدارة الرئيسية أو صانعي القرار",
            "• التغييرات في معلومات الاتصال أو مواقع العمل",
            "• التغييرات في نطاق العمليات",
            "• التعديلات الرئيسية على نظام الإدارة أو العمليات",
            "تحتفظ جهة الاعتماد بالحق في اتخاذ الإجراءات المناسبة، بما في ذلك عمليات التدقيق الخاصة أو إعادة التقييم."
        ]
    },
    "section_11": {
        "title_en": "11. Suspension, Withdrawal, and Termination",
        "title_ar": "11. التعليق والسحب والإنهاء",
        "content_en": [
            "Either party may terminate the Agreement with two months' written notice.",
            "Immediate termination applies in cases of breach, insolvency, or reputational harm.",
            "Upon termination, the Client shall cease all use of certification and return all related materials."
        ],
        "content_ar": [
            "يجوز لأي طرف إنهاء الاتفاقية بإشعار كتابي قبل شهرين.",
            "ينطبق الإنهاء الفوري في حالات الإخلال أو الإعسار أو الضرر بالسمعة.",
            "عند الإنهاء، يتوقف العميل عن استخدام جميع الاعتمادات وإعادة جميع المواد ذات الصلة."
        ]
    },
    "section_12": {
        "title_en": "12. Liability and Indemnity",
        "title_ar": "12. المسؤولية والتعويض",
        "content_en": [
            "The CB is not liable for indirect loss or damages except in proven cases of gross negligence.",
            "Maximum liability is limited to the total fee paid for certification.",
            "The Client shall indemnify the CB against misuse of certificates, marks, or audit reports."
        ],
        "content_ar": [
            "جهة الاعتماد غير مسؤولة عن الخسارة أو الأضرار غير المباشرة إلا في حالات الإهمال الجسيم المثبتة.",
            "الحد الأقصى للمسؤولية يقتصر على إجمالي الرسوم المدفوعة للاعتماد.",
            "يعوض العميل جهة الاعتماد عن سوء استخدام الشهادات أو العلامات أو تقارير التدقيق."
        ]
    },
    "section_13": {
        "title_en": "13. Force Majeure",
        "title_ar": "13. القوة القاهرة",
        "content_en": [
            "Neither party is liable for non-performance due to events beyond their control (e.g., natural disasters, pandemics, regulatory closures)."
        ],
        "content_ar": [
            "لا يتحمل أي طرف المسؤولية عن عدم الأداء بسبب أحداث خارجة عن إرادته (مثل الكوارث الطبيعية والأوبئة والإغلاقات التنظيمية)."
        ]
    },
    "section_14": {
        "title_en": "14. Governing Law and Disputes",
        "title_ar": "14. القانون الحاكم والنزاعات",
        "content_en": [
            "This Agreement is governed by the laws of the Kingdom of Saudi Arabia.",
            "Disputes are handled first through internal complaints/appeals procedures, and if unresolved, settled by competent courts in the Kingdom of Saudi Arabia."
        ],
        "content_ar": [
            "تخضع هذه الاتفاقية لقوانين المملكة العربية السعودية.",
            "يتم التعامل مع النزاعات أولاً من خلال إجراءات الشكاوى/الطعون الداخلية، وإذا لم يتم حلها، يتم البت فيها من قبل المحاكم المختصة في المملكة العربية السعودية."
        ]
    }
}


def generate_grant_agreement_pdf(agreement_data: dict, output_path: str = None) -> bytes:
    """
    Generate a professional bilingual Grant Agreement PDF.
    
    Args:
        agreement_data: Dictionary containing:
            - organization_name: Client organization name
            - organization_address: Client address
            - standards/selected_standards: List of ISO standards
            - scope/scope_of_services: Scope of certification
            - sites: List of work locations
            - signatory_name: Client signatory name
            - signatory_position: Client signatory position
            - issuer_name: BAC signatory name
            - issuer_designation: BAC signatory position
        output_path: Optional path to save PDF (if None, returns bytes)
    
    Returns:
        PDF bytes or path to saved file
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
        except:
            pass
    
    logo_path = ROOT_DIR / "assets" / "bayan-logo.png"
    
    # Create PDF
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    # Colors matching other system reports
    primary_color = colors.HexColor('#1e3a5f')
    section_color = colors.HexColor('#4a7c9b')
    light_bg = colors.HexColor('#f0f4f8')
    accent_color = colors.HexColor('#2563eb')
    
    # Extract data
    org_name = agreement_data.get('organization_name', '') or ''
    org_address = agreement_data.get('organization_address', '') or ''
    
    standards = agreement_data.get('standards', []) or agreement_data.get('selected_standards', []) or []
    if isinstance(standards, str):
        standards = [s.strip() for s in standards.split(',')]
    
    scope = agreement_data.get('scope', '') or agreement_data.get('scope_of_services', '') or ''
    
    sites = agreement_data.get('sites', []) or []
    if isinstance(sites, list):
        sites_str = ', '.join([str(s) for s in sites]) if sites else 'As per application'
    else:
        sites_str = str(sites) if sites else 'As per application'
    
    signatory_name = agreement_data.get('signatory_name', '') or ''
    signatory_position = agreement_data.get('signatory_position', '') or ''
    signatory_date = agreement_data.get('signatory_date', '') or datetime.now().strftime('%Y-%m-%d')
    
    bac_signatory = agreement_data.get('issuer_name', 'Abdullah Al-Rashid')
    bac_position = agreement_data.get('issuer_designation', 'General Manager')
    
    # Helper functions
    def draw_arabic(text, x, y, size=10, bold=False, right_align=False):
        if arabic_font_available:
            try:
                reshaped = arabic_reshaper.reshape(str(text))
                bidi_text = get_display(reshaped)
                font = 'Amiri-Bold' if bold and font_bold_path.exists() else 'Amiri'
                c.setFont(font, size)
                if right_align:
                    c.drawRightString(x, y, bidi_text)
                else:
                    c.drawString(x, y, bidi_text)
            except:
                c.setFont('Helvetica', size)
                c.drawString(x, y, str(text))
    
    def new_page():
        c.showPage()
        # Header on new page
        c.setFillColor(primary_color)
        c.rect(0, height - 50, width, 50, fill=True, stroke=False)
        c.setFillColor(colors.white)
        c.setFont('Helvetica-Bold', 12)
        c.drawCentredString(width/2, height - 30, "GRANT AGREEMENT")
        if arabic_font_available:
            try:
                ar_title = get_display(arabic_reshaper.reshape("اتفاقية المنح"))
                c.setFont('Amiri-Bold', 11)
                c.drawCentredString(width/2, height - 45, ar_title)
            except: pass
        return height - 70
    
    def draw_footer(page_num):
        c.setFillColor(primary_color)
        c.rect(0, 0, width, 25, fill=True, stroke=False)
        c.setFillColor(colors.white)
        c.setFont('Helvetica', 8)
        c.drawCentredString(width/2, 10, f"Page {page_num} | BAYAN Auditing & Conformity | Grant Agreement")
    
    # ============ PAGE 1: HEADER AND PARTIES ============
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
        except: pass
    
    # Title
    c.setFillColor(colors.white)
    c.setFont('Helvetica-Bold', 24)
    c.drawCentredString(width/2, height - 40, "GRANT AGREEMENT")
    if arabic_font_available:
        try:
            ar_title = get_display(arabic_reshaper.reshape("اتفاقية المنح"))
            c.setFont('Amiri-Bold', 18)
            c.drawCentredString(width/2, height - 65, ar_title)
        except: pass
    
    # Form reference
    c.setFont('Helvetica', 9)
    c.drawRightString(width - 25, height - 25, "BAC-F6-03")
    c.drawRightString(width - 25, height - 40, f"Date: {signatory_date}")
    
    y = height - 130
    
    # ============ SECTION 1: PARTIES ============
    c.setFillColor(section_color)
    c.setFont('Helvetica-Bold', 12)
    c.drawString(30, y, "1. Parties to the Agreement")
    draw_arabic("1. أطراف الاتفاقية", width - 30, y, 11, bold=True, right_align=True)
    y -= 25
    
    c.setFillColor(colors.black)
    c.setFont('Helvetica', 10)
    c.drawString(30, y, "This Certification Agreement (\"Agreement\") is made between:")
    y -= 20
    
    # Certification Body box
    c.setFillColor(light_bg)
    c.roundRect(30, y - 60, width/2 - 45, 65, 5, fill=True, stroke=False)
    c.setStrokeColor(section_color)
    c.setLineWidth(1)
    c.roundRect(30, y - 60, width/2 - 45, 65, 5, fill=False, stroke=True)
    
    c.setFillColor(section_color)
    c.setFont('Helvetica-Bold', 9)
    c.drawString(40, y - 5, "CERTIFICATION BODY")
    c.setFillColor(colors.black)
    c.setFont('Helvetica', 9)
    c.drawString(40, y - 20, "BAYAN AUDITING & CONFORMITY (BAC)")
    c.drawString(40, y - 32, "Arabia Limited Certification Body")
    c.drawString(40, y - 44, "3879 Al Khadar Street, Riyadh, 12282")
    c.drawString(40, y - 56, "Saudi Arabia")
    
    # Client Organization box
    c.setFillColor(light_bg)
    c.roundRect(width/2 + 15, y - 60, width/2 - 45, 65, 5, fill=True, stroke=False)
    c.setStrokeColor(section_color)
    c.roundRect(width/2 + 15, y - 60, width/2 - 45, 65, 5, fill=False, stroke=True)
    
    c.setFillColor(section_color)
    c.setFont('Helvetica-Bold', 9)
    c.drawString(width/2 + 25, y - 5, "CLIENT ORGANIZATION / المنشأة")
    c.setFillColor(colors.black)
    c.setFont('Helvetica-Bold', 10)
    c.drawString(width/2 + 25, y - 20, org_name[:35] if len(org_name) > 35 else org_name)
    c.setFont('Helvetica', 9)
    # Wrap address if needed
    addr_lines = [org_address[i:i+40] for i in range(0, len(org_address), 40)]
    for idx, line in enumerate(addr_lines[:2]):
        c.drawString(width/2 + 25, y - 35 - (idx * 12), line)
    
    y -= 85
    
    # ============ SECTION 2: PURPOSE AND SCOPE ============
    c.setFillColor(section_color)
    c.setFont('Helvetica-Bold', 12)
    c.drawString(30, y, "2. Purpose and Scope")
    draw_arabic("2. الغرض والنطاق", width - 30, y, 11, bold=True, right_align=True)
    y -= 20
    
    c.setFillColor(colors.black)
    c.setFont('Helvetica', 9)
    c.drawString(30, y, "This Agreement defines the terms under which the CB provides certification services for:")
    y -= 20
    
    # Standards box
    c.setFillColor(light_bg)
    c.roundRect(30, y - 35, width - 60, 40, 5, fill=True, stroke=False)
    c.setStrokeColor(accent_color)
    c.setLineWidth(1.5)
    c.roundRect(30, y - 35, width - 60, 40, 5, fill=False, stroke=True)
    
    c.setFillColor(section_color)
    c.setFont('Helvetica-Bold', 9)
    c.drawString(40, y - 5, "CERTIFICATION STANDARDS:")
    # Draw Arabic translation separately
    draw_arabic("معايير الاعتماد", width - 70, y - 5, 9, bold=True, right_align=True)
    
    # Draw standards with checkboxes
    c.setFillColor(colors.black)
    c.setFont('Helvetica', 9)
    std_x = 40
    std_y = y - 22
    all_standards = ['ISO 9001', 'ISO 14001', 'ISO 45001', 'ISO 22000', 'ISO 22301', 'ISO 27001']
    
    for std in all_standards:
        # Check if this standard is selected
        is_selected = any(std.replace(' ', '') in s.upper().replace(' ', '') or 
                         s.upper().replace(' ', '') in std.replace(' ', '') 
                         for s in standards)
        checkbox = "☑" if is_selected else "☐"
        c.drawString(std_x, std_y, f"{checkbox} {std}")
        std_x += 80
        if std_x > width - 100:
            std_x = 40
            std_y -= 12
    
    y -= 55
    
    # Scope
    c.setFillColor(section_color)
    c.setFont('Helvetica-Bold', 9)
    c.drawString(30, y, "Scope of Services:")
    draw_arabic("نطاق الخدمات", width - 30, y, 9, bold=True, right_align=True)
    y -= 12
    c.setFillColor(colors.black)
    c.setFont('Helvetica', 9)
    # Wrap scope text
    scope_lines = [scope[i:i+90] for i in range(0, min(len(scope), 270), 90)]
    for line in scope_lines:
        c.drawString(40, y, line)
        y -= 12
    
    y -= 5
    
    # Sites
    c.setFillColor(section_color)
    c.setFont('Helvetica-Bold', 9)
    c.drawString(30, y, "Work Locations / مواقع العمل:")
    y -= 12
    c.setFillColor(colors.black)
    c.setFont('Helvetica', 9)
    sites_lines = [sites_str[i:i+90] for i in range(0, min(len(sites_str), 180), 90)]
    for line in sites_lines:
        c.drawString(40, y, line)
        y -= 12
    
    y -= 15
    
    # ============ SECTIONS 3-7 ============
    sections_page1 = ['section_3', 'section_4', 'section_5']
    
    for section_key in sections_page1:
        section = AGREEMENT_SECTIONS[section_key]
        
        if y < 150:
            draw_footer(page_num)
            page_num += 1
            y = new_page()
        
        # Section title
        c.setFillColor(section_color)
        c.setFont('Helvetica-Bold', 10)
        c.drawString(30, y, section['title_en'])
        draw_arabic(section['title_ar'], width - 30, y, 9, bold=True, right_align=True)
        y -= 15
        
        # Section content
        c.setFillColor(colors.black)
        c.setFont('Helvetica', 8)
        for item in section['content_en']:
            if y < 80:
                draw_footer(page_num)
                page_num += 1
                y = new_page()
            
            if item.startswith('•') or item.startswith('a)') or item.startswith('b)'):
                c.drawString(40, y, item[:100])
            else:
                c.drawString(30, y, item[:100])
            y -= 11
        
        y -= 8
    
    draw_footer(page_num)
    
    # ============ PAGE 2+ : REMAINING SECTIONS ============
    page_num += 1
    y = new_page()
    
    sections_remaining = ['section_6', 'section_7', 'section_9', 'section_10', 'section_11', 'section_12', 'section_13', 'section_14']
    
    for section_key in sections_remaining:
        section = AGREEMENT_SECTIONS[section_key]
        
        if y < 120:
            draw_footer(page_num)
            page_num += 1
            y = new_page()
        
        # Section title
        c.setFillColor(section_color)
        c.setFont('Helvetica-Bold', 10)
        c.drawString(30, y, section['title_en'])
        draw_arabic(section['title_ar'], width - 30, y, 9, bold=True, right_align=True)
        y -= 15
        
        # Section content
        c.setFillColor(colors.black)
        c.setFont('Helvetica', 8)
        for item in section['content_en']:
            if y < 80:
                draw_footer(page_num)
                page_num += 1
                y = new_page()
            
            if item.startswith('•') or item.startswith('a)') or item.startswith('b)'):
                c.drawString(40, y, item[:100])
            else:
                c.drawString(30, y, item[:100])
            y -= 11
        
        y -= 8
    
    # ============ SIGNATURE SECTION ============
    if y < 200:
        draw_footer(page_num)
        page_num += 1
        y = new_page()
    
    y -= 10
    c.setFillColor(section_color)
    c.setFont('Helvetica-Bold', 12)
    c.drawString(30, y, "15. Acceptance and Signatures")
    draw_arabic("15. القبول والتوقيعات", width - 30, y, 11, bold=True, right_align=True)
    y -= 25
    
    # Two signature boxes
    box_width = width/2 - 45
    box_height = 100
    
    # BAC signature box
    c.setFillColor(light_bg)
    c.roundRect(30, y - box_height, box_width, box_height, 5, fill=True, stroke=False)
    c.setStrokeColor(section_color)
    c.setLineWidth(1)
    c.roundRect(30, y - box_height, box_width, box_height, 5, fill=False, stroke=True)
    
    c.setFillColor(section_color)
    c.setFont('Helvetica-Bold', 9)
    c.drawString(40, y - 15, "FOR BAYAN AUDITING & CONFORMITY")
    
    c.setFillColor(colors.black)
    c.setFont('Helvetica', 9)
    c.drawString(40, y - 35, f"Name: {bac_signatory}")
    c.drawString(40, y - 50, f"Position: {bac_position}")
    c.drawString(40, y - 65, "Signature: _____________________")
    c.drawString(40, y - 80, f"Date: {signatory_date}")
    
    # Client signature box
    c.setFillColor(light_bg)
    c.roundRect(width/2 + 15, y - box_height, box_width, box_height, 5, fill=True, stroke=False)
    c.setStrokeColor(section_color)
    c.roundRect(width/2 + 15, y - box_height, box_width, box_height, 5, fill=False, stroke=True)
    
    c.setFillColor(section_color)
    c.setFont('Helvetica-Bold', 9)
    c.drawString(width/2 + 25, y - 15, "FOR CLIENT / للعميل")
    
    c.setFillColor(colors.black)
    c.setFont('Helvetica', 9)
    c.drawString(width/2 + 25, y - 35, f"Name: {signatory_name}")
    c.drawString(width/2 + 25, y - 50, f"Position: {signatory_position}")
    c.drawString(width/2 + 25, y - 65, "Signature: _____________________")
    c.drawString(width/2 + 25, y - 80, f"Date: {signatory_date}")
    
    draw_footer(page_num)
    
    # Save
    c.save()
    
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    if output_path:
        with open(output_path, 'wb') as f:
            f.write(pdf_bytes)
        return output_path
    
    return pdf_bytes


# For testing
if __name__ == "__main__":
    test_data = {
        "organization_name": "ABC International Company Ltd.",
        "organization_address": "456 King Fahd Road, Al Olaya District, Riyadh 12211, Saudi Arabia",
        "selected_standards": ["ISO9001", "ISO14001"],
        "scope_of_services": "Design, development, and manufacturing of industrial automation systems and equipment. Provision of technical consulting services for industrial process optimization.",
        "sites": ["Head Office - Riyadh", "Manufacturing Plant - Dammam", "Service Center - Jeddah"],
        "signatory_name": "Mohammed Al-Rashid",
        "signatory_position": "Chief Executive Officer",
        "signatory_date": "2025-02-17",
        "issuer_name": "Abdullah Al-Rashid",
        "issuer_designation": "General Manager"
    }
    
    output_file = CONTRACTS_DIR / "test_grant_agreement.pdf"
    result = generate_grant_agreement_pdf(test_data, str(output_file))
    print(f"Generated: {result}")
