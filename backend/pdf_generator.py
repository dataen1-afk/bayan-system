"""
PDF Contract Generator for Bayan Auditing & Conformity
Generates professional certification contracts with company branding
"""

import io
import os
import base64
import pathlib
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable
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

# Register Arabic fonts
ARABIC_FONT_REGISTERED = False
ROOT_DIR = pathlib.Path(__file__).parent

try:
    amiri_regular = ROOT_DIR / "fonts" / "Amiri-Regular.ttf"
    amiri_bold = ROOT_DIR / "fonts" / "Amiri-Bold.ttf"
    
    if amiri_regular.exists():
        pdfmetrics.registerFont(TTFont('Amiri', str(amiri_regular)))
        ARABIC_FONT_REGISTERED = True
        print(f"PDF Generator: Registered Arabic font: {amiri_regular}")
        
        if amiri_bold.exists():
            pdfmetrics.registerFont(TTFont('Amiri-Bold', str(amiri_bold)))
            print(f"PDF Generator: Registered Arabic Bold font: {amiri_bold}")
    else:
        # Fallback to system fonts
        arabic_font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
        ]
        for font_path in arabic_font_paths:
            if os.path.exists(font_path):
                pdfmetrics.registerFont(TTFont('Arabic', font_path))
                break
except Exception as e:
    print(f"Warning: Could not register Arabic font: {e}")


def process_arabic_text(text):
    """Process Arabic text for proper RTL display in PDF"""
    if not text or not ARABIC_SUPPORT:
        return text
    try:
        reshaped = arabic_reshaper.reshape(str(text))
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


class ContractPDFGenerator:
    """Generate professional PDF contracts"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='ContractTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            alignment=TA_CENTER,
            spaceAfter=10,
            textColor=colors.HexColor('#1a365d')  # Bayan navy
        ))
        
        # Arabic Title style
        self.styles.add(ParagraphStyle(
            name='ContractTitleArabic',
            parent=self.styles['Heading1'],
            fontSize=18,
            alignment=TA_CENTER,
            spaceAfter=20,
            textColor=colors.HexColor('#1a365d'),
            fontName='Amiri' if ARABIC_FONT_REGISTERED else 'Helvetica'
        ))
        
        # Section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=12,
            alignment=TA_LEFT,
            spaceBefore=15,
            spaceAfter=10,
            textColor=colors.HexColor('#1a365d'),
            borderPadding=5
        ))
        
        # Normal text style
        self.styles.add(ParagraphStyle(
            name='ContractText',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=TA_LEFT,
            spaceAfter=6,
            leading=14
        ))
        
        # Right-aligned text (for Arabic)
        self.styles.add(ParagraphStyle(
            name='ContractTextRTL',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=TA_RIGHT,
            spaceAfter=6,
            leading=14,
            fontName='Amiri' if ARABIC_FONT_REGISTERED else 'Helvetica'
        ))
        
        # Footer style
        self.styles.add(ParagraphStyle(
            name='Footer',
            parent=self.styles['Normal'],
            fontSize=8,
            alignment=TA_CENTER,
            textColor=colors.gray
        ))

    def _process_image_for_pdf(self, image_data, width, height, fallback=''):
        """
        Process a base64 image for PDF embedding with robust error handling.
        Returns an Image element or fallback string if processing fails.
        """
        if not image_data:
            return fallback
        
        try:
            # Extract base64 data from data URL
            if image_data.startswith('data:image'):
                base64_data = image_data.split(',')[1]
            else:
                base64_data = image_data
            
            image_bytes = base64.b64decode(base64_data)
            
            # Use PIL to validate and convert the image
            try:
                from PIL import Image as PILImage
                pil_img = PILImage.open(io.BytesIO(image_bytes))
                
                # Force load to fully validate image data
                pil_img.load()
                
                # Convert to RGB if needed (handle RGBA, P, LA modes)
                if pil_img.mode in ('RGBA', 'LA'):
                    background = PILImage.new('RGB', pil_img.size, (255, 255, 255))
                    background.paste(pil_img, mask=pil_img.split()[-1])
                    pil_img = background
                elif pil_img.mode == 'P':
                    pil_img = pil_img.convert('RGB')
                elif pil_img.mode != 'RGB':
                    pil_img = pil_img.convert('RGB')
                
                # Save to a clean PNG buffer
                clean_buffer = io.BytesIO()
                pil_img.save(clean_buffer, format='PNG')
                clean_buffer.seek(0)
                
                # Create the reportlab Image and validate it
                img_element = Image(clean_buffer, width=width, height=height)
                # Force validation by wrapping
                img_element.wrap(width, height)
                
                # Re-create for actual use (wrap consumes the buffer)
                clean_buffer.seek(0)
                return Image(clean_buffer, width=width, height=height)
                
            except Exception as pil_error:
                print(f"PIL image processing failed, using fallback: {pil_error}")
                return fallback
                    
        except Exception as e:
            print(f"Error processing image for PDF: {e}")
            return fallback



    def _create_header(self, canvas, doc):
        """Create document header with logo and company info"""
        canvas.saveState()
        
        # Draw header background
        canvas.setFillColor(colors.HexColor('#1a365d'))
        canvas.rect(0, A4[1] - 80, A4[0], 80, fill=True)
        
        # Draw company logo
        logo_path = ROOT_DIR / "assets" / "bayan-logo.png"
        if logo_path.exists():
            try:
                canvas.drawImage(str(logo_path), 30, A4[1] - 75, width=60, height=60, preserveAspectRatio=True, mask='auto')
            except Exception as e:
                print(f"Error drawing logo: {e}")
        
        # Company name (after logo)
        canvas.setFillColor(colors.white)
        canvas.setFont('Helvetica-Bold', 16)
        canvas.drawString(100, A4[1] - 35, "BAYAN AUDITING & CONFORMITY")
        
        # Subtitle
        canvas.setFont('Helvetica', 10)
        canvas.drawString(100, A4[1] - 50, "Arabia Limited Certification Body")
        
        # Contact info
        canvas.setFont('Helvetica', 8)
        canvas.drawString(100, A4[1] - 65, "3879 Al Khadar Street, Riyadh, 12282, Saudi Arabia")
        
        # Contract number on right
        canvas.setFont('Helvetica-Bold', 10)
        canvas.drawRightString(A4[0] - 50, A4[1] - 35, f"Contract Date: {datetime.now().strftime('%Y-%m-%d')}")
        
        canvas.restoreState()

    def _create_footer(self, canvas, doc):
        """Create document footer"""
        canvas.saveState()
        
        # Draw footer line
        canvas.setStrokeColor(colors.HexColor('#1a365d'))
        canvas.line(50, 50, A4[0] - 50, 50)
        
        # Footer text
        canvas.setFillColor(colors.gray)
        canvas.setFont('Helvetica', 8)
        canvas.drawCentredString(A4[0] / 2, 35, 
            f"© {datetime.now().year} Bayan Auditing & Conformity. All Rights Reserved.")
        canvas.drawCentredString(A4[0] / 2, 25, 
            f"Page {doc.page}")
        
        canvas.restoreState()

    def generate_contract(self, agreement_data: dict, proposal_data: dict) -> bytes:
        """
        Generate a PDF contract from agreement and proposal data
        
        Args:
            agreement_data: The certification agreement data
            proposal_data: The proposal/quotation data
            
        Returns:
            PDF file as bytes
        """
        buffer = io.BytesIO()
        
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=50,
            leftMargin=50,
            topMargin=100,
            bottomMargin=70
        )
        
        story = []
        
        # Title - English
        story.append(Paragraph("CERTIFICATION AGREEMENT", self.styles['ContractTitle']))
        # Title - Arabic (properly processed)
        if ARABIC_FONT_REGISTERED and ARABIC_SUPPORT:
            ar_title = process_arabic_text("اتفاقية الاعتماد")
            story.append(Paragraph(ar_title, self.styles['ContractTitleArabic']))
        story.append(Spacer(1, 20))
        
        # Agreement Reference
        story.append(Paragraph(
            f"<b>Agreement Reference:</b> {agreement_data.get('id', 'N/A')[:8].upper()}",
            self.styles['ContractText']
        ))
        story.append(Paragraph(
            f"<b>Date:</b> {agreement_data.get('signatory_date', datetime.now().strftime('%Y-%m-%d'))}",
            self.styles['ContractText']
        ))
        story.append(Spacer(1, 15))
        
        # Horizontal line
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#1a365d')))
        story.append(Spacer(1, 15))
        
        # Section 1: Parties
        story.append(Paragraph("1. PARTIES TO THE AGREEMENT", self.styles['SectionHeader']))
        
        parties_data = [
            ['Certification Body:', 'BAYAN AUDITING & CONFORMITY (BAC)'],
            ['', 'Arabia Limited Certification Body'],
            ['', '3879 Al Khadar Street, Riyadh, 12282, Saudi Arabia'],
            ['', ''],
            ['Client Organization:', process_dynamic_text(agreement_data.get('organization_name', 'N/A'))],
            ['Address:', process_dynamic_text(agreement_data.get('organization_address', 'N/A'))],
        ]
        
        parties_table = Table(parties_data, colWidths=[2*inch, 4*inch])
        parties_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Amiri' if ARABIC_FONT_REGISTERED else 'Helvetica'),  # Use Amiri for Arabic support
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        story.append(parties_table)
        story.append(Spacer(1, 20))
        
        # Section 2: Certification Scope
        story.append(Paragraph("2. CERTIFICATION SCOPE", self.styles['SectionHeader']))
        
        # Standards
        standards = agreement_data.get('selected_standards', [])
        standards_text = ', '.join(standards) if standards else 'N/A'
        
        scope_data = [
            ['Management System Standards:', standards_text],
            ['Scope of Services:', process_dynamic_text(agreement_data.get('scope_of_services', 'N/A'))],
        ]
        
        # Add other standard if exists
        if agreement_data.get('other_standard'):
            scope_data.append(['Other Standard:', process_dynamic_text(agreement_data.get('other_standard'))])
        
        scope_table = Table(scope_data, colWidths=[2*inch, 4*inch])
        scope_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Amiri' if ARABIC_FONT_REGISTERED else 'Helvetica'),  # Use Amiri for Arabic support
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        story.append(scope_table)
        story.append(Spacer(1, 10))
        
        # Sites
        sites = agreement_data.get('sites', [])
        if sites:
            story.append(Paragraph("<b>Sites for Certification:</b>", self.styles['ContractText']))
            for i, site in enumerate(sites, 1):
                if site.strip():
                    story.append(Paragraph(f"  {i}. {process_dynamic_text(site)}", self.styles['ContractText']))
        
        story.append(Spacer(1, 20))
        
        # Section 3: Audit Duration (from proposal)
        story.append(Paragraph("3. AUDIT DURATION (Working Days)", self.styles['SectionHeader']))
        
        audit_duration = proposal_data.get('audit_duration', {})
        duration_data = [
            ['Audit Phase', 'Duration (Days)'],
            ['Initial Certification - Stage 1', str(audit_duration.get('stage_1', 'N/A'))],
            ['Initial Certification - Stage 2', str(audit_duration.get('stage_2', 'N/A'))],
            ['Surveillance Audit 1', str(audit_duration.get('surveillance_1', 'N/A'))],
            ['Surveillance Audit 2', str(audit_duration.get('surveillance_2', 'N/A'))],
            ['Recertification Audit', str(audit_duration.get('recertification', 'N/A'))],
        ]
        
        duration_table = Table(duration_data, colWidths=[3.5*inch, 1.5*inch])
        duration_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a365d')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(duration_table)
        story.append(Spacer(1, 20))
        
        # Section 4: Service Fees (from proposal)
        story.append(Paragraph("4. SERVICE FEES", self.styles['SectionHeader']))
        
        service_fees = proposal_data.get('service_fees', {})
        currency = service_fees.get('currency', 'SAR')
        
        def format_currency(amount):
            return f"{currency} {amount:,.2f}" if amount else f"{currency} 0.00"
        
        fees_data = [
            ['Service', 'Fee'],
            ['Initial Certification Fee', format_currency(service_fees.get('initial_certification', 0))],
            ['Surveillance Audit 1 Fee', format_currency(service_fees.get('surveillance_1', 0))],
            ['Surveillance Audit 2 Fee', format_currency(service_fees.get('surveillance_2', 0))],
            ['Recertification Audit Fee', format_currency(service_fees.get('recertification', 0))],
            ['', ''],
            ['TOTAL AMOUNT', format_currency(proposal_data.get('total_amount', 0))],
        ]
        
        fees_table = Table(fees_data, colWidths=[3.5*inch, 1.5*inch])
        fees_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a365d')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e8f4e8')),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(fees_table)
        story.append(Spacer(1, 10))
        
        # Notes
        if proposal_data.get('notes'):
            story.append(Paragraph(f"<b>Notes:</b> {proposal_data.get('notes')}", self.styles['ContractText']))
        
        story.append(Spacer(1, 20))
        
        # Section 5: Terms and Conditions
        story.append(Paragraph("5. TERMS AND CONDITIONS", self.styles['SectionHeader']))
        
        terms = [
            "Payment: 50% upon acceptance, 50% after completion of the audit.",
            "All fees are exclusive of VAT (15%).",
            "Travel and accommodation expenses are additional.",
            f"This agreement is valid for {proposal_data.get('validity_days', 30)} days from the date of issue.",
            "Cancellation within 7 days of scheduled audit: 50% fee applies.",
            "The certification cycle is 3 years with annual surveillance audits.",
        ]
        
        for i, term in enumerate(terms, 1):
            story.append(Paragraph(f"{i}. {term}", self.styles['ContractText']))
        
        story.append(Spacer(1, 20))
        
        # Section 6: Client Acknowledgements
        story.append(Paragraph("6. CLIENT ACKNOWLEDGEMENTS", self.styles['SectionHeader']))
        
        acks = agreement_data.get('acknowledgements', {})
        ack_items = [
            ('certificationRules', 'Compliance with certification body rules and requirements'),
            ('publicDirectory', 'Inclusion in public directory of certified organizations'),
            ('certificationCommunication', 'Professional communication regarding certification'),
            ('surveillanceSchedule', 'Acceptance of surveillance audit schedule'),
            ('nonconformityResolution', 'Commitment to resolve nonconformities within specified timeframe'),
            ('feesAndPayment', 'Acceptance of fees and payment terms'),
        ]
        
        for key, desc in ack_items:
            # Use ASCII checkmark characters that work without special fonts
            status = "[X]" if acks.get(key, False) else "[ ]"
            story.append(Paragraph(f"{status} {desc}", self.styles['ContractText']))
        
        story.append(Spacer(1, 30))
        
        # Section 7: Signatures
        story.append(Paragraph("7. SIGNATURES", self.styles['SectionHeader']))
        
        # Get signature and stamp images from agreement data
        signature_image = agreement_data.get('signature_image')
        stamp_image = agreement_data.get('stamp_image')
        
        # Create signature elements
        client_signature_element = '_________________________'
        client_stamp_element = ''
        
        if signature_image:
            client_signature_element = self._process_image_for_pdf(signature_image, 1.5*inch, 0.5*inch, '_________________________')
        
        if stamp_image:
            client_stamp_element = self._process_image_for_pdf(stamp_image, 1*inch, 1*inch, '')
        
        # Build signature table with images
        sig_data = [
            ['FOR THE CERTIFICATION BODY', 'FOR THE CLIENT'],
            ['', ''],
            ['BAYAN AUDITING & CONFORMITY', process_dynamic_text(agreement_data.get('organization_name', ''))],
            ['', ''],
            ['_________________________', client_signature_element if isinstance(client_signature_element, Image) else client_signature_element],
            ['Authorized Signatory', process_dynamic_text(agreement_data.get('signatory_name', ''))],
            ['', process_dynamic_text(agreement_data.get('signatory_position', ''))],
            ['', ''],
            [f"Date: {datetime.now().strftime('%Y-%m-%d')}", f"Date: {agreement_data.get('signatory_date', '')}"],
        ]
        
        # Add stamp row if available
        if client_stamp_element:
            sig_data.append(['', ''])
            sig_data.append(['', client_stamp_element])
            sig_data.append(['', 'Company Seal'])
        
        sig_table = Table(sig_data, colWidths=[3*inch, 3*inch])
        sig_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (1, 1), (1, -1), 'Amiri' if ARABIC_FONT_REGISTERED else 'Helvetica'),  # Client column may have Arabic text
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(sig_table)
        
        # Add digital signature notice
        story.append(Spacer(1, 20))
        story.append(Paragraph(
            "<i>This document has been digitally signed through the Bayan Auditing & Conformity online portal.</i>",
            self.styles['Footer']
        ))
        
        # Build PDF
        doc.build(story, onFirstPage=self._create_header, onLaterPages=self._create_header)
        
        buffer.seek(0)
        return buffer.getvalue()


# Singleton instance
pdf_generator = ContractPDFGenerator()


def generate_contract_pdf(agreement_data: dict, proposal_data: dict) -> bytes:
    """Generate a contract PDF from agreement and proposal data"""
    return pdf_generator.generate_contract(agreement_data, proposal_data)
