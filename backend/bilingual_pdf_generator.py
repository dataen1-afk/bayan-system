"""
Bilingual PDF Contract Generator for Bayan Auditing & Conformity
Generates professional certification contracts in both Arabic and English
"""

import io
import os
import base64
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Arabic text processing
try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    ARABIC_SUPPORT = True
except ImportError:
    ARABIC_SUPPORT = False
    print("Warning: arabic-reshaper or python-bidi not installed. Arabic text may not display correctly.")

# Register Arabic font
ARABIC_FONT_REGISTERED = False
ARABIC_FONT_BOLD_REGISTERED = False

# Try to register Amiri font from our fonts directory
try:
    import pathlib
    ROOT_DIR = pathlib.Path(__file__).parent
    amiri_regular = ROOT_DIR / "fonts" / "Amiri-Regular.ttf"
    amiri_bold = ROOT_DIR / "fonts" / "Amiri-Bold.ttf"
    
    if amiri_regular.exists():
        pdfmetrics.registerFont(TTFont('ArabicFont', str(amiri_regular)))
        ARABIC_FONT_REGISTERED = True
        print(f"Registered Arabic font: {amiri_regular}")
        
        if amiri_bold.exists():
            pdfmetrics.registerFont(TTFont('ArabicFontBold', str(amiri_bold)))
            ARABIC_FONT_BOLD_REGISTERED = True
            print(f"Registered Arabic Bold font: {amiri_bold}")
    else:
        # Fallback to system fonts
        arabic_font_paths = [
            "/usr/share/fonts/truetype/noto/NotoSansArabic-Regular.ttf",
            "/usr/share/fonts/truetype/noto/NotoKufiArabic-Regular.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]
        for font_path in arabic_font_paths:
            if os.path.exists(font_path):
                pdfmetrics.registerFont(TTFont('ArabicFont', font_path))
                ARABIC_FONT_REGISTERED = True
                print(f"Registered Arabic font: {font_path}")
                break
except Exception as e:
    print(f"Warning: Could not register Arabic font: {e}")


def process_arabic_text(text):
    """Process Arabic text for proper RTL display in PDF"""
    if not text or not ARABIC_SUPPORT:
        return text
    try:
        reshaped = arabic_reshaper.reshape(text)
        bidi_text = get_display(reshaped)
        return bidi_text
    except Exception as e:
        print(f"Error processing Arabic text: {e}")
        return text


def process_dynamic_text(text):
    """
    Process dynamic text that may contain Arabic characters.
    Detects if text contains Arabic and processes accordingly.
    """
    if not text:
        return text
    
    text = str(text)
    
    # Check if text contains Arabic characters (Unicode range for Arabic)
    has_arabic = any('\u0600' <= char <= '\u06FF' or '\u0750' <= char <= '\u077F' for char in text)
    
    if has_arabic and ARABIC_SUPPORT:
        return process_arabic_text(text)
    
    return text


class BilingualContractPDFGenerator:
    """Generate professional bilingual PDF contracts (Arabic + English)"""
    
    # Translations dictionary
    TRANSLATIONS = {
        'title': {
            'en': 'CERTIFICATION AGREEMENT',
            'ar': 'اتفاقية الاعتماد'
        },
        'agreement_ref': {
            'en': 'Agreement Reference',
            'ar': 'مرجع الاتفاقية'
        },
        'date': {
            'en': 'Date',
            'ar': 'التاريخ'
        },
        'parties': {
            'en': '1. PARTIES TO THE AGREEMENT',
            'ar': '1. أطراف الاتفاقية'
        },
        'certification_body': {
            'en': 'Certification Body',
            'ar': 'جهة الاعتماد'
        },
        'client_organization': {
            'en': 'Client Organization',
            'ar': 'المنظمة العميلة'
        },
        'address': {
            'en': 'Address',
            'ar': 'العنوان'
        },
        'certification_scope': {
            'en': '2. CERTIFICATION SCOPE',
            'ar': '2. نطاق الاعتماد'
        },
        'management_standards': {
            'en': 'Management System Standards',
            'ar': 'معايير نظام الإدارة'
        },
        'scope_of_services': {
            'en': 'Scope of Services',
            'ar': 'نطاق الخدمات'
        },
        'other_standard': {
            'en': 'Other Standard',
            'ar': 'معيار آخر'
        },
        'sites_for_certification': {
            'en': 'Sites for Certification',
            'ar': 'مواقع الاعتماد'
        },
        'audit_duration': {
            'en': '3. AUDIT DURATION (Working Days)',
            'ar': '3. مدة التدقيق (أيام العمل)'
        },
        'audit_phase': {
            'en': 'Audit Phase',
            'ar': 'مرحلة التدقيق'
        },
        'duration_days': {
            'en': 'Duration (Days)',
            'ar': 'المدة (أيام)'
        },
        'stage_1': {
            'en': 'Initial Certification - Stage 1',
            'ar': 'الاعتماد الأولي - المرحلة 1'
        },
        'stage_2': {
            'en': 'Initial Certification - Stage 2',
            'ar': 'الاعتماد الأولي - المرحلة 2'
        },
        'surveillance_1': {
            'en': 'Surveillance Audit 1',
            'ar': 'تدقيق المراقبة 1'
        },
        'surveillance_2': {
            'en': 'Surveillance Audit 2',
            'ar': 'تدقيق المراقبة 2'
        },
        'recertification': {
            'en': 'Recertification Audit',
            'ar': 'تدقيق إعادة الاعتماد'
        },
        'service_fees': {
            'en': '4. SERVICE FEES',
            'ar': '4. رسوم الخدمة'
        },
        'service': {
            'en': 'Service',
            'ar': 'الخدمة'
        },
        'fee': {
            'en': 'Fee',
            'ar': 'الرسوم'
        },
        'initial_cert_fee': {
            'en': 'Initial Certification Fee',
            'ar': 'رسوم الاعتماد الأولي'
        },
        'surv_1_fee': {
            'en': 'Surveillance Audit 1 Fee',
            'ar': 'رسوم تدقيق المراقبة 1'
        },
        'surv_2_fee': {
            'en': 'Surveillance Audit 2 Fee',
            'ar': 'رسوم تدقيق المراقبة 2'
        },
        'recert_fee': {
            'en': 'Recertification Audit Fee',
            'ar': 'رسوم تدقيق إعادة الاعتماد'
        },
        'total_amount': {
            'en': 'TOTAL AMOUNT',
            'ar': 'المبلغ الإجمالي'
        },
        'notes': {
            'en': 'Notes',
            'ar': 'ملاحظات'
        },
        'terms_conditions': {
            'en': '5. TERMS AND CONDITIONS',
            'ar': '5. الشروط والأحكام'
        },
        'client_acks': {
            'en': '6. CLIENT ACKNOWLEDGEMENTS',
            'ar': '6. إقرارات العميل'
        },
        'signatures': {
            'en': '7. SIGNATURES',
            'ar': '7. التوقيعات'
        },
        'for_cert_body': {
            'en': 'FOR THE CERTIFICATION BODY',
            'ar': 'عن جهة الاعتماد'
        },
        'for_client': {
            'en': 'FOR THE CLIENT',
            'ar': 'عن العميل'
        },
        'authorized_signatory': {
            'en': 'Authorized Signatory',
            'ar': 'المفوض بالتوقيع'
        },
        'company_seal': {
            'en': 'Company Seal',
            'ar': 'ختم الشركة'
        },
        'digital_signature_notice': {
            'en': 'This document has been digitally signed through the Bayan Auditing & Conformity online portal.',
            'ar': 'تم توقيع هذه الوثيقة إلكترونياً من خلال بوابة بيان للتدقيق والمطابقة.'
        },
        'terms': {
            'en': [
                "Payment: 50% upon acceptance, 50% after completion of the audit.",
                "All fees are exclusive of VAT (15%).",
                "Travel and accommodation expenses are additional.",
                "This agreement is valid for {validity_days} days from the date of issue.",
                "Cancellation within 7 days of scheduled audit: 50% fee applies.",
                "The certification cycle is 3 years with annual surveillance audits.",
            ],
            'ar': [
                "الدفع: 50% عند القبول، 50% بعد اكتمال التدقيق.",
                "جميع الرسوم لا تشمل ضريبة القيمة المضافة (15%).",
                "مصاريف السفر والإقامة إضافية.",
                "هذه الاتفاقية صالحة لمدة {validity_days} يوماً من تاريخ الإصدار.",
                "الإلغاء خلال 7 أيام من موعد التدقيق: تطبق رسوم 50%.",
                "دورة الاعتماد 3 سنوات مع تدقيقات مراقبة سنوية.",
            ]
        },
        'acknowledgements': {
            'en': {
                'certificationRules': 'Compliance with certification body rules and requirements',
                'publicDirectory': 'Inclusion in public directory of certified organizations',
                'certificationCommunication': 'Professional communication regarding certification',
                'surveillanceSchedule': 'Acceptance of surveillance audit schedule',
                'nonconformityResolution': 'Commitment to resolve nonconformities within specified timeframe',
                'feesAndPayment': 'Acceptance of fees and payment terms',
            },
            'ar': {
                'certificationRules': 'الالتزام بقواعد ومتطلبات جهة الاعتماد',
                'publicDirectory': 'الإدراج في الدليل العام للمنظمات المعتمدة',
                'certificationCommunication': 'التواصل المهني بشأن الاعتماد',
                'surveillanceSchedule': 'قبول جدول تدقيقات المراقبة',
                'nonconformityResolution': 'الالتزام بحل عدم المطابقات ضمن الإطار الزمني المحدد',
                'feesAndPayment': 'قبول الرسوم وشروط الدفع',
            }
        }
    }
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._ensure_arabic_fonts()
        self._setup_custom_styles()
    
    def _ensure_arabic_fonts(self):
        """Ensure Arabic fonts are registered"""
        global ARABIC_FONT_REGISTERED, ARABIC_FONT_BOLD_REGISTERED
        
        try:
            import pathlib
            ROOT_DIR = pathlib.Path(__file__).parent
            amiri_regular = ROOT_DIR / "fonts" / "Amiri-Regular.ttf"
            amiri_bold = ROOT_DIR / "fonts" / "Amiri-Bold.ttf"
            
            if amiri_regular.exists():
                try:
                    pdfmetrics.registerFont(TTFont('ArabicFont', str(amiri_regular)))
                    ARABIC_FONT_REGISTERED = True
                except Exception:
                    pass  # Font already registered
                    
                if amiri_bold.exists():
                    try:
                        pdfmetrics.registerFont(TTFont('ArabicFontBold', str(amiri_bold)))
                        ARABIC_FONT_BOLD_REGISTERED = True
                    except Exception:
                        pass  # Font already registered
        except Exception as e:
            print(f"Error ensuring Arabic fonts: {e}")
        
    def _setup_custom_styles(self):
        """Setup custom paragraph styles for both languages"""
        # English Title
        self.styles.add(ParagraphStyle(
            name='TitleEN',
            parent=self.styles['Heading1'],
            fontSize=16,
            alignment=TA_CENTER,
            spaceAfter=5,
            textColor=colors.HexColor('#1a365d'),
            fontName='Helvetica-Bold'
        ))
        
        # Arabic Title
        self.styles.add(ParagraphStyle(
            name='TitleAR',
            parent=self.styles['Heading1'],
            fontSize=16,
            alignment=TA_CENTER,
            spaceAfter=15,
            textColor=colors.HexColor('#1a365d'),
            fontName='ArabicFont' if ARABIC_FONT_REGISTERED else 'Helvetica-Bold'
        ))
        
        # Section Header English
        self.styles.add(ParagraphStyle(
            name='SectionEN',
            parent=self.styles['Heading2'],
            fontSize=11,
            alignment=TA_LEFT,
            spaceBefore=12,
            spaceAfter=3,
            textColor=colors.HexColor('#1a365d'),
            fontName='Helvetica-Bold'
        ))
        
        # Section Header Arabic
        self.styles.add(ParagraphStyle(
            name='SectionAR',
            parent=self.styles['Heading2'],
            fontSize=11,
            alignment=TA_RIGHT,
            spaceBefore=0,
            spaceAfter=8,
            textColor=colors.HexColor('#1a365d'),
            fontName='ArabicFont' if ARABIC_FONT_REGISTERED else 'Helvetica-Bold'
        ))
        
        # Normal text English
        self.styles.add(ParagraphStyle(
            name='TextEN',
            parent=self.styles['Normal'],
            fontSize=9,
            alignment=TA_LEFT,
            spaceAfter=4,
            leading=12,
            fontName='Helvetica'
        ))
        
        # Normal text Arabic
        self.styles.add(ParagraphStyle(
            name='TextAR',
            parent=self.styles['Normal'],
            fontSize=9,
            alignment=TA_RIGHT,
            spaceAfter=4,
            leading=12,
            fontName='ArabicFont' if ARABIC_FONT_REGISTERED else 'Helvetica'
        ))
        
        # Footer style
        self.styles.add(ParagraphStyle(
            name='FooterBilingual',
            parent=self.styles['Normal'],
            fontSize=7,
            alignment=TA_CENTER,
            textColor=colors.gray
        ))

    def _bilingual_text(self, en_text, ar_text, en_style='TextEN', ar_style='TextAR'):
        """Create bilingual text block with English and Arabic"""
        elements = []
        elements.append(Paragraph(en_text, self.styles[en_style]))
        ar_processed = process_arabic_text(ar_text)
        elements.append(Paragraph(ar_processed, self.styles[ar_style]))
        return elements

    def _bilingual_section_header(self, key):
        """Create bilingual section header"""
        en_text = self.TRANSLATIONS[key]['en']
        ar_text = process_arabic_text(self.TRANSLATIONS[key]['ar'])
        elements = []
        elements.append(Paragraph(en_text, self.styles['SectionEN']))
        elements.append(Paragraph(ar_text, self.styles['SectionAR']))
        return elements

    def _process_image_for_pdf(self, image_data, width, height, fallback=''):
        """Process base64 image for PDF embedding"""
        if not image_data:
            return fallback
        
        try:
            if image_data.startswith('data:image'):
                base64_data = image_data.split(',')[1]
            else:
                base64_data = image_data
            
            image_bytes = base64.b64decode(base64_data)
            
            try:
                from PIL import Image as PILImage
                pil_img = PILImage.open(io.BytesIO(image_bytes))
                pil_img.load()
                
                if pil_img.mode in ('RGBA', 'LA'):
                    background = PILImage.new('RGB', pil_img.size, (255, 255, 255))
                    background.paste(pil_img, mask=pil_img.split()[-1])
                    pil_img = background
                elif pil_img.mode == 'P':
                    pil_img = pil_img.convert('RGB')
                elif pil_img.mode != 'RGB':
                    pil_img = pil_img.convert('RGB')
                
                clean_buffer = io.BytesIO()
                pil_img.save(clean_buffer, format='PNG')
                clean_buffer.seek(0)
                
                img_element = Image(clean_buffer, width=width, height=height)
                img_element.wrap(width, height)
                
                clean_buffer.seek(0)
                return Image(clean_buffer, width=width, height=height)
                
            except Exception as pil_error:
                print(f"PIL image processing failed: {pil_error}")
                return fallback
                    
        except Exception as e:
            print(f"Error processing image for PDF: {e}")
            return fallback

    def _create_header(self, canvas, doc):
        """Create bilingual document header"""
        canvas.saveState()
        
        # Header background
        canvas.setFillColor(colors.HexColor('#1a365d'))
        canvas.rect(0, A4[1] - 70, A4[0], 70, fill=True)
        
        # English company name (left)
        canvas.setFillColor(colors.white)
        canvas.setFont('Helvetica-Bold', 14)
        canvas.drawString(40, A4[1] - 30, "BAYAN AUDITING & CONFORMITY")
        
        canvas.setFont('Helvetica', 9)
        canvas.drawString(40, A4[1] - 42, "Arabia Limited Certification Body")
        canvas.drawString(40, A4[1] - 54, "3879 Al Khadar Street, Riyadh, 12282, Saudi Arabia")
        
        # Arabic company name (right)
        if ARABIC_FONT_REGISTERED:
            canvas.setFont('ArabicFont', 14)
        else:
            canvas.setFont('Helvetica-Bold', 14)
        ar_company = process_arabic_text("بيان للتدقيق والمطابقة")
        canvas.drawRightString(A4[0] - 40, A4[1] - 30, ar_company)
        
        if ARABIC_FONT_REGISTERED:
            canvas.setFont('ArabicFont', 9)
        else:
            canvas.setFont('Helvetica', 9)
        ar_subtitle = process_arabic_text("جهة اعتماد عربية محدودة")
        canvas.drawRightString(A4[0] - 40, A4[1] - 42, ar_subtitle)
        
        canvas.restoreState()

    def _create_footer(self, canvas, doc):
        """Create bilingual document footer"""
        canvas.saveState()
        
        canvas.setStrokeColor(colors.HexColor('#1a365d'))
        canvas.line(40, 45, A4[0] - 40, 45)
        
        canvas.setFillColor(colors.gray)
        canvas.setFont('Helvetica', 7)
        canvas.drawCentredString(A4[0] / 2, 32, 
            f"© {datetime.now().year} Bayan Auditing & Conformity. All Rights Reserved. | جميع الحقوق محفوظة لبيان للتدقيق والمطابقة")
        canvas.drawCentredString(A4[0] / 2, 22, 
            f"Page {doc.page}")
        
        canvas.restoreState()

    def generate_bilingual_contract(self, agreement_data: dict, proposal_data: dict) -> bytes:
        """Generate a bilingual PDF contract (Arabic + English)"""
        buffer = io.BytesIO()
        
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=40,
            leftMargin=40,
            topMargin=85,
            bottomMargin=60
        )
        
        story = []
        
        # Title (bilingual)
        story.append(Paragraph(self.TRANSLATIONS['title']['en'], self.styles['TitleEN']))
        ar_title = process_arabic_text(self.TRANSLATIONS['title']['ar'])
        story.append(Paragraph(ar_title, self.styles['TitleAR']))
        story.append(Spacer(1, 10))
        
        # Agreement Reference (bilingual table)
        ref_data = [
            [f"{self.TRANSLATIONS['agreement_ref']['en']}:", 
             agreement_data.get('id', 'N/A')[:8].upper(),
             f":{process_arabic_text(self.TRANSLATIONS['agreement_ref']['ar'])}"],
            [f"{self.TRANSLATIONS['date']['en']}:",
             agreement_data.get('signatory_date', datetime.now().strftime('%Y-%m-%d')),
             f":{process_arabic_text(self.TRANSLATIONS['date']['ar'])}"],
        ]
        
        ref_table = Table(ref_data, colWidths=[1.8*inch, 2.2*inch, 1.8*inch])
        ref_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'ArabicFont' if ARABIC_FONT_REGISTERED else 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(ref_table)
        story.append(Spacer(1, 8))
        
        # Horizontal line
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#1a365d')))
        story.append(Spacer(1, 10))
        
        # Section 1: Parties
        story.extend(self._bilingual_section_header('parties'))
        
        parties_data = [
            [self.TRANSLATIONS['certification_body']['en'] + ':', 
             'BAYAN AUDITING & CONFORMITY (BAC)',
             ':' + process_arabic_text(self.TRANSLATIONS['certification_body']['ar'])],
            ['', 'Arabia Limited Certification Body', ''],
            ['', '3879 Al Khadar Street, Riyadh, Saudi Arabia', ''],
            ['', '', ''],
            [self.TRANSLATIONS['client_organization']['en'] + ':',
             process_dynamic_text(agreement_data.get('organization_name', 'N/A')),
             ':' + process_arabic_text(self.TRANSLATIONS['client_organization']['ar'])],
            [self.TRANSLATIONS['address']['en'] + ':',
             process_dynamic_text(agreement_data.get('organization_address', 'N/A')),
             ':' + process_arabic_text(self.TRANSLATIONS['address']['ar'])],
        ]
        
        parties_table = Table(parties_data, colWidths=[1.6*inch, 2.6*inch, 1.6*inch])
        parties_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'ArabicFont' if ARABIC_FONT_REGISTERED else 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ]))
        story.append(parties_table)
        story.append(Spacer(1, 12))
        
        # Section 2: Certification Scope
        story.extend(self._bilingual_section_header('certification_scope'))
        
        standards = agreement_data.get('selected_standards', [])
        standards_text = ', '.join(standards) if standards else 'N/A'
        
        scope_data = [
            [self.TRANSLATIONS['management_standards']['en'] + ':', 
             standards_text,
             ':' + process_arabic_text(self.TRANSLATIONS['management_standards']['ar'])],
            [self.TRANSLATIONS['scope_of_services']['en'] + ':',
             process_dynamic_text(agreement_data.get('scope_of_services', 'N/A')),
             ':' + process_arabic_text(self.TRANSLATIONS['scope_of_services']['ar'])],
        ]
        
        if agreement_data.get('other_standard'):
            scope_data.append([
                self.TRANSLATIONS['other_standard']['en'] + ':',
                process_dynamic_text(agreement_data.get('other_standard')),
                ':' + process_arabic_text(self.TRANSLATIONS['other_standard']['ar'])
            ])
        
        scope_table = Table(scope_data, colWidths=[1.6*inch, 2.6*inch, 1.6*inch])
        scope_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'ArabicFont' if ARABIC_FONT_REGISTERED else 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ]))
        story.append(scope_table)
        
        # Sites
        sites = agreement_data.get('sites', [])
        if sites:
            story.append(Spacer(1, 6))
            sites_header = f"<b>{self.TRANSLATIONS['sites_for_certification']['en']} | {process_arabic_text(self.TRANSLATIONS['sites_for_certification']['ar'])}</b>"
            story.append(Paragraph(sites_header, self.styles['TextEN']))
            for i, site in enumerate(sites, 1):
                if site.strip():
                    story.append(Paragraph(f"  {i}. {process_dynamic_text(site)}", self.styles['TextEN']))
        
        story.append(Spacer(1, 12))
        
        # Section 3: Audit Duration
        story.extend(self._bilingual_section_header('audit_duration'))
        
        audit_duration = proposal_data.get('audit_duration', {})
        duration_data = [
            [self.TRANSLATIONS['audit_phase']['en'], 
             self.TRANSLATIONS['duration_days']['en'],
             process_arabic_text(self.TRANSLATIONS['audit_phase']['ar'])],
            [self.TRANSLATIONS['stage_1']['en'], 
             str(audit_duration.get('stage_1', 'N/A')),
             process_arabic_text(self.TRANSLATIONS['stage_1']['ar'])],
            [self.TRANSLATIONS['stage_2']['en'],
             str(audit_duration.get('stage_2', 'N/A')),
             process_arabic_text(self.TRANSLATIONS['stage_2']['ar'])],
            [self.TRANSLATIONS['surveillance_1']['en'],
             str(audit_duration.get('surveillance_1', 'N/A')),
             process_arabic_text(self.TRANSLATIONS['surveillance_1']['ar'])],
            [self.TRANSLATIONS['surveillance_2']['en'],
             str(audit_duration.get('surveillance_2', 'N/A')),
             process_arabic_text(self.TRANSLATIONS['surveillance_2']['ar'])],
            [self.TRANSLATIONS['recertification']['en'],
             str(audit_duration.get('recertification', 'N/A')),
             process_arabic_text(self.TRANSLATIONS['recertification']['ar'])],
        ]
        
        duration_table = Table(duration_data, colWidths=[2.2*inch, 1*inch, 2.2*inch])
        duration_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a365d')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, 0), 'ArabicFont' if ARABIC_FONT_REGISTERED else 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(duration_table)
        story.append(Spacer(1, 12))
        
        # Section 4: Service Fees
        story.extend(self._bilingual_section_header('service_fees'))
        
        service_fees = proposal_data.get('service_fees', {})
        currency = service_fees.get('currency', 'SAR')
        
        def format_currency(amount):
            return f"{currency} {amount:,.2f}" if amount else f"{currency} 0.00"
        
        fees_data = [
            [self.TRANSLATIONS['service']['en'],
             self.TRANSLATIONS['fee']['en'],
             process_arabic_text(self.TRANSLATIONS['service']['ar'])],
            [self.TRANSLATIONS['initial_cert_fee']['en'],
             format_currency(service_fees.get('initial_certification', 0)),
             process_arabic_text(self.TRANSLATIONS['initial_cert_fee']['ar'])],
            [self.TRANSLATIONS['surv_1_fee']['en'],
             format_currency(service_fees.get('surveillance_1', 0)),
             process_arabic_text(self.TRANSLATIONS['surv_1_fee']['ar'])],
            [self.TRANSLATIONS['surv_2_fee']['en'],
             format_currency(service_fees.get('surveillance_2', 0)),
             process_arabic_text(self.TRANSLATIONS['surv_2_fee']['ar'])],
            [self.TRANSLATIONS['recert_fee']['en'],
             format_currency(service_fees.get('recertification', 0)),
             process_arabic_text(self.TRANSLATIONS['recert_fee']['ar'])],
            ['', '', ''],
            [self.TRANSLATIONS['total_amount']['en'],
             format_currency(proposal_data.get('total_amount', 0)),
             process_arabic_text(self.TRANSLATIONS['total_amount']['ar'])],
        ]
        
        fees_table = Table(fees_data, colWidths=[2.2*inch, 1.2*inch, 2*inch])
        fees_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a365d')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e8f4e8')),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(fees_table)
        
        if proposal_data.get('notes'):
            story.append(Spacer(1, 6))
            story.append(Paragraph(f"<b>{self.TRANSLATIONS['notes']['en']} | {process_arabic_text(self.TRANSLATIONS['notes']['ar'])}:</b> {process_dynamic_text(proposal_data.get('notes'))}", self.styles['TextEN']))
        
        story.append(Spacer(1, 12))
        
        # Section 5: Terms and Conditions
        story.extend(self._bilingual_section_header('terms_conditions'))
        
        validity_days = proposal_data.get('validity_days', 30)
        
        for i, (en_term, ar_term) in enumerate(zip(self.TRANSLATIONS['terms']['en'], self.TRANSLATIONS['terms']['ar']), 1):
            en_term_formatted = en_term.replace('{validity_days}', str(validity_days))
            ar_term_formatted = ar_term.replace('{validity_days}', str(validity_days))
            story.append(Paragraph(f"{i}. {en_term_formatted}", self.styles['TextEN']))
            story.append(Paragraph(f"   {process_arabic_text(ar_term_formatted)}", self.styles['TextAR']))
        
        story.append(Spacer(1, 12))
        
        # Section 6: Client Acknowledgements
        story.extend(self._bilingual_section_header('client_acks'))
        
        acks = agreement_data.get('acknowledgements', {})
        ack_keys = ['certificationRules', 'publicDirectory', 'certificationCommunication', 
                    'surveillanceSchedule', 'nonconformityResolution', 'feesAndPayment']
        
        for key in ack_keys:
            # Use ASCII checkmark characters that work without special fonts
            status = "[X]" if acks.get(key, False) else "[ ]"
            en_desc = self.TRANSLATIONS['acknowledgements']['en'].get(key, key)
            ar_desc = self.TRANSLATIONS['acknowledgements']['ar'].get(key, key)
            story.append(Paragraph(f"{status} {en_desc}", self.styles['TextEN']))
            story.append(Paragraph(f"   {process_arabic_text(ar_desc)}", self.styles['TextAR']))
        
        story.append(Spacer(1, 15))
        
        # Section 7: Signatures
        story.extend(self._bilingual_section_header('signatures'))
        
        signature_image = agreement_data.get('signature_image')
        stamp_image = agreement_data.get('stamp_image')
        
        client_signature_element = '_________________________'
        if signature_image:
            sig_img = self._process_image_for_pdf(signature_image, 1.2*inch, 0.4*inch, '_________________________')
            if isinstance(sig_img, Image):
                client_signature_element = sig_img
        
        sig_data = [
            [f"{self.TRANSLATIONS['for_cert_body']['en']}\n{process_arabic_text(self.TRANSLATIONS['for_cert_body']['ar'])}", 
             f"{self.TRANSLATIONS['for_client']['en']}\n{process_arabic_text(self.TRANSLATIONS['for_client']['ar'])}"],
            ['', ''],
            ['BAYAN AUDITING & CONFORMITY', process_dynamic_text(agreement_data.get('organization_name', ''))],
            ['', ''],
            ['_________________________', client_signature_element],
            [f"{self.TRANSLATIONS['authorized_signatory']['en']}", 
             process_dynamic_text(agreement_data.get('signatory_name', ''))],
            ['', process_dynamic_text(agreement_data.get('signatory_position', ''))],
            ['', ''],
            [f"{self.TRANSLATIONS['date']['en']}: {datetime.now().strftime('%Y-%m-%d')}", 
             f"{self.TRANSLATIONS['date']['en']}: {agreement_data.get('signatory_date', '')}"],
        ]
        
        if stamp_image:
            stamp_img = self._process_image_for_pdf(stamp_image, 0.8*inch, 0.8*inch, '')
            if isinstance(stamp_img, Image):
                sig_data.append(['', ''])
                sig_data.append(['', stamp_img])
                sig_data.append(['', f"{self.TRANSLATIONS['company_seal']['en']} | {process_arabic_text(self.TRANSLATIONS['company_seal']['ar'])}"])
        
        sig_table = Table(sig_data, colWidths=[2.8*inch, 2.8*inch])
        sig_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        story.append(sig_table)
        
        # Digital signature notice
        story.append(Spacer(1, 15))
        story.append(Paragraph(
            f"<i>{self.TRANSLATIONS['digital_signature_notice']['en']}</i>",
            self.styles['FooterBilingual']
        ))
        story.append(Paragraph(
            f"<i>{process_arabic_text(self.TRANSLATIONS['digital_signature_notice']['ar'])}</i>",
            self.styles['FooterBilingual']
        ))
        
        # Build PDF
        doc.build(story, onFirstPage=self._create_header, onLaterPages=self._create_header)
        
        buffer.seek(0)
        return buffer.getvalue()


# Singleton instance
bilingual_pdf_generator = BilingualContractPDFGenerator()


def generate_bilingual_contract_pdf(agreement_data: dict, proposal_data: dict) -> bytes:
    """Generate a bilingual contract PDF from agreement and proposal data"""
    return bilingual_pdf_generator.generate_bilingual_contract(agreement_data, proposal_data)
