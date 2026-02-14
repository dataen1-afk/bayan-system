"""
PDF Contract Generator for Bayan Auditing & Conformity
Generates professional certification contracts with company branding
"""

import io
import os
import base64
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Try to register Arabic font if available
try:
    # Check for common Arabic fonts
    arabic_font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
    ]
    for font_path in arabic_font_paths:
        if os.path.exists(font_path):
            pdfmetrics.registerFont(TTFont('Arabic', font_path))
            break
except:
    pass


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
            spaceAfter=20,
            textColor=colors.HexColor('#1a365d')  # Bayan navy
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
            leading=14
        ))
        
        # Footer style
        self.styles.add(ParagraphStyle(
            name='Footer',
            parent=self.styles['Normal'],
            fontSize=8,
            alignment=TA_CENTER,
            textColor=colors.gray
        ))

    def _create_header(self, canvas, doc):
        """Create document header with logo and company info"""
        canvas.saveState()
        
        # Draw header background
        canvas.setFillColor(colors.HexColor('#1a365d'))
        canvas.rect(0, A4[1] - 80, A4[0], 80, fill=True)
        
        # Company name
        canvas.setFillColor(colors.white)
        canvas.setFont('Helvetica-Bold', 16)
        canvas.drawString(50, A4[1] - 35, "BAYAN AUDITING & CONFORMITY")
        
        # Subtitle
        canvas.setFont('Helvetica', 10)
        canvas.drawString(50, A4[1] - 50, "Arabia Limited Certification Body")
        
        # Contact info
        canvas.setFont('Helvetica', 8)
        canvas.drawString(50, A4[1] - 65, "3879 Al Khadar Street, Riyadh, 12282, Saudi Arabia")
        
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
        
        # Title
        story.append(Paragraph("CERTIFICATION AGREEMENT", self.styles['ContractTitle']))
        story.append(Paragraph("اتفاقية الاعتماد", self.styles['ContractTitle']))
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
            ['Client Organization:', agreement_data.get('organization_name', 'N/A')],
            ['Address:', agreement_data.get('organization_address', 'N/A')],
        ]
        
        parties_table = Table(parties_data, colWidths=[2*inch, 4*inch])
        parties_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
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
            ['Scope of Services:', agreement_data.get('scope_of_services', 'N/A')],
        ]
        
        # Add other standard if exists
        if agreement_data.get('other_standard'):
            scope_data.append(['Other Standard:', agreement_data.get('other_standard')])
        
        scope_table = Table(scope_data, colWidths=[2*inch, 4*inch])
        scope_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
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
                    story.append(Paragraph(f"  {i}. {site}", self.styles['ContractText']))
        
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
            status = "✓" if acks.get(key, False) else "☐"
            story.append(Paragraph(f"{status} {desc}", self.styles['ContractText']))
        
        story.append(Spacer(1, 30))
        
        # Section 7: Signatures
        story.append(Paragraph("7. SIGNATURES", self.styles['SectionHeader']))
        
        sig_data = [
            ['FOR THE CERTIFICATION BODY', 'FOR THE CLIENT'],
            ['', ''],
            ['BAYAN AUDITING & CONFORMITY', agreement_data.get('organization_name', '')],
            ['', ''],
            ['_________________________', '_________________________'],
            ['Authorized Signatory', agreement_data.get('signatory_name', '')],
            ['', agreement_data.get('signatory_position', '')],
            ['', ''],
            [f"Date: {datetime.now().strftime('%Y-%m-%d')}", f"Date: {agreement_data.get('signatory_date', '')}"],
        ]
        
        sig_table = Table(sig_data, colWidths=[3*inch, 3*inch])
        sig_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(sig_table)
        
        # Build PDF
        doc.build(story, onFirstPage=self._create_header, onLaterPages=self._create_header)
        
        buffer.seek(0)
        return buffer.getvalue()


# Singleton instance
pdf_generator = ContractPDFGenerator()


def generate_contract_pdf(agreement_data: dict, proposal_data: dict) -> bytes:
    """Generate a contract PDF from agreement and proposal data"""
    return pdf_generator.generate_contract(agreement_data, proposal_data)
