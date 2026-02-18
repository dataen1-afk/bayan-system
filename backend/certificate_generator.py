"""
Certificate PDF Generator with QR Code
Generates professional ISO certification certificates in bilingual format (English/Arabic)
"""

from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm, mm
from reportlab.lib.colors import HexColor, white, black
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pathlib import Path
import qrcode
from io import BytesIO
import base64
from PIL import Image
from datetime import datetime
import arabic_reshaper
from bidi.algorithm import get_display

# Register Arabic font
ROOT_DIR = Path(__file__).parent
FONTS_DIR = ROOT_DIR / "fonts"
ASSETS_DIR = ROOT_DIR / "assets"

try:
    pdfmetrics.registerFont(TTFont('Amiri', str(FONTS_DIR / 'Amiri-Regular.ttf')))
    pdfmetrics.registerFont(TTFont('Amiri-Bold', str(FONTS_DIR / 'Amiri-Bold.ttf')))
except:
    pass

# Brand colors
NAVY_BLUE = HexColor('#1e3a5f')
GOLD = HexColor('#c9a227')
LIGHT_GOLD = HexColor('#f5e6b3')
LIGHT_BLUE = HexColor('#e8f4f8')


def generate_qr_code(verification_url: str, size: int = 150) -> BytesIO:
    """Generate QR code for certificate verification"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=2,
    )
    qr.add_data(verification_url)
    qr.make(fit=True)
    
    qr_img = qr.make_image(fill_color="#1e3a5f", back_color="white")
    
    # Convert to bytes
    buffer = BytesIO()
    qr_img.save(buffer, format='PNG')
    buffer.seek(0)
    return buffer


def draw_arabic_text(c, text, x, y, font_size=12, font='Amiri', align='right'):
    """Draw properly shaped Arabic text"""
    try:
        reshaped = arabic_reshaper.reshape(str(text))
        bidi_text = get_display(reshaped)
        c.setFont(font, font_size)
        if align == 'right':
            c.drawRightString(x, y, bidi_text)
        elif align == 'center':
            c.drawCentredString(x, y, bidi_text)
        else:
            c.drawString(x, y, bidi_text)
    except:
        c.setFont('Helvetica', font_size)
        if align == 'right':
            c.drawRightString(x, y, str(text))
        elif align == 'center':
            c.drawCentredString(x, y, str(text))
        else:
            c.drawString(x, y, str(text))


def generate_certificate_pdf(certificate_data: dict, output_path: str) -> str:
    """
    Generate a professional ISO certificate PDF with QR code
    
    Args:
        certificate_data: Dictionary containing certificate information
        output_path: Path to save the PDF
    
    Returns:
        Path to generated PDF
    """
    # Use landscape A4
    width, height = landscape(A4)
    c = canvas.Canvas(output_path, pagesize=landscape(A4))
    
    # Background
    c.setFillColor(white)
    c.rect(0, 0, width, height, fill=True, stroke=False)
    
    # Decorative border
    border_margin = 15 * mm
    c.setStrokeColor(NAVY_BLUE)
    c.setLineWidth(3)
    c.rect(border_margin, border_margin, width - 2*border_margin, height - 2*border_margin, stroke=True, fill=False)
    
    # Inner decorative border
    inner_margin = 20 * mm
    c.setStrokeColor(GOLD)
    c.setLineWidth(1)
    c.rect(inner_margin, inner_margin, width - 2*inner_margin, height - 2*inner_margin, stroke=True, fill=False)
    
    # Header banner
    banner_height = 60
    c.setFillColor(NAVY_BLUE)
    c.rect(inner_margin, height - inner_margin - banner_height, width - 2*inner_margin, banner_height, fill=True, stroke=False)
    
    # Logo placeholder (left side)
    logo_path = ASSETS_DIR / "bayan-logo.png"
    if logo_path.exists():
        try:
            c.drawImage(str(logo_path), inner_margin + 20, height - inner_margin - banner_height + 5, width=100, height=50, preserveAspectRatio=True, mask='auto')
        except:
            pass
    
    # Header text
    c.setFillColor(white)
    c.setFont('Helvetica-Bold', 22)
    c.drawCentredString(width/2, height - inner_margin - 35, "CERTIFICATE OF CONFORMITY")
    
    # Arabic title
    draw_arabic_text(c, "شهادة المطابقة", width/2, height - inner_margin - 55, font_size=18, font='Amiri-Bold', align='center')
    
    # Content area
    content_y = height - inner_margin - banner_height - 30
    
    # Certificate number and accreditation
    c.setFillColor(NAVY_BLUE)
    c.setFont('Helvetica-Bold', 10)
    cert_number = certificate_data.get('certificate_number', 'CERT-XXXX-XXXX')
    c.drawString(inner_margin + 20, content_y, f"Certificate No: {cert_number}")
    draw_arabic_text(c, f"رقم الشهادة: {cert_number}", width - inner_margin - 20, content_y, font_size=10)
    
    content_y -= 40
    
    # Main certification statement (English)
    c.setFillColor(black)
    c.setFont('Helvetica', 12)
    c.drawCentredString(width/2, content_y, "This is to certify that the Management System of")
    content_y -= 20
    draw_arabic_text(c, "نشهد بأن نظام الإدارة الخاص بـ", width/2, content_y, font_size=12, align='center')
    
    content_y -= 35
    
    # Organization name (prominent)
    org_name = certificate_data.get('organization_name', 'Organization Name')
    org_name_ar = certificate_data.get('organization_name_ar', '')
    
    c.setFillColor(NAVY_BLUE)
    c.setFont('Helvetica-Bold', 24)
    c.drawCentredString(width/2, content_y, org_name)
    
    if org_name_ar:
        content_y -= 28
        draw_arabic_text(c, org_name_ar, width/2, content_y, font_size=20, font='Amiri-Bold', align='center')
    
    content_y -= 35
    
    # Standards certification
    c.setFillColor(black)
    c.setFont('Helvetica', 12)
    c.drawCentredString(width/2, content_y, "has been assessed and found to be in conformity with the requirements of")
    content_y -= 18
    draw_arabic_text(c, "تم تقييمه ووجد أنه مطابق لمتطلبات", width/2, content_y, font_size=11, align='center')
    
    content_y -= 35
    
    # Standards (highlighted)
    standards = certificate_data.get('standards', [])
    standards_text = ", ".join(standards) if standards else "ISO 9001:2015"
    
    c.setFillColor(GOLD)
    c.setFont('Helvetica-Bold', 20)
    c.drawCentredString(width/2, content_y, standards_text)
    
    content_y -= 35
    
    # Scope
    scope = certificate_data.get('scope', '')
    scope_ar = certificate_data.get('scope_ar', '')
    
    if scope:
        c.setFillColor(black)
        c.setFont('Helvetica', 11)
        c.drawCentredString(width/2, content_y, "for the following scope:")
        content_y -= 18
        c.setFont('Helvetica-Bold', 11)
        # Wrap scope text if too long
        if len(scope) > 80:
            mid = len(scope) // 2
            space_idx = scope.rfind(' ', 0, mid + 20)
            if space_idx > 0:
                c.drawCentredString(width/2, content_y, scope[:space_idx])
                content_y -= 15
                c.drawCentredString(width/2, content_y, scope[space_idx+1:])
            else:
                c.drawCentredString(width/2, content_y, scope)
        else:
            c.drawCentredString(width/2, content_y, scope)
        
        content_y -= 20
        if scope_ar:
            draw_arabic_text(c, scope_ar, width/2, content_y, font_size=11, font='Amiri-Bold', align='center')
    
    # Dates section at bottom
    dates_y = inner_margin + 100
    
    # Issue date
    issue_date = certificate_data.get('issue_date', datetime.now().strftime('%Y-%m-%d'))
    expiry_date = certificate_data.get('expiry_date', '')
    
    c.setFillColor(NAVY_BLUE)
    c.setFont('Helvetica-Bold', 10)
    
    # Left column - Issue Date
    c.drawString(inner_margin + 40, dates_y + 20, "Issue Date / تاريخ الإصدار")
    c.setFont('Helvetica', 12)
    c.drawString(inner_margin + 40, dates_y, issue_date)
    
    # Center column - Expiry Date
    c.setFont('Helvetica-Bold', 10)
    c.drawCentredString(width/2, dates_y + 20, "Expiry Date / تاريخ الانتهاء")
    c.setFont('Helvetica', 12)
    c.drawCentredString(width/2, dates_y, expiry_date)
    
    # Right column - Lead Auditor
    lead_auditor = certificate_data.get('lead_auditor', '')
    if lead_auditor:
        c.setFont('Helvetica-Bold', 10)
        c.drawRightString(width - inner_margin - 40, dates_y + 20, "Lead Auditor / المدقق الرئيسي")
        c.setFont('Helvetica', 12)
        c.drawRightString(width - inner_margin - 40, dates_y, lead_auditor)
    
    # QR Code
    verification_url = certificate_data.get('verification_url', '')
    if verification_url:
        qr_buffer = generate_qr_code(verification_url)
        qr_img = Image.open(qr_buffer)
        qr_path = Path(output_path).parent / f"temp_qr_{certificate_data.get('id', 'temp')}.png"
        qr_img.save(str(qr_path))
        
        qr_size = 70
        qr_x = width - inner_margin - qr_size - 20
        qr_y = inner_margin + 30
        
        c.drawImage(str(qr_path), qr_x, qr_y, width=qr_size, height=qr_size)
        
        c.setFillColor(NAVY_BLUE)
        c.setFont('Helvetica', 7)
        c.drawCentredString(qr_x + qr_size/2, qr_y - 10, "Scan to verify")
        
        # Cleanup temp QR file
        try:
            qr_path.unlink()
        except:
            pass
    
    # Footer
    footer_y = inner_margin + 10
    c.setFillColor(NAVY_BLUE)
    c.setFont('Helvetica', 8)
    c.drawCentredString(width/2, footer_y, "BAYAN for Verification and Conformity | بيان للتحقق والمطابقة | www.bayan.sa")
    
    # Decorative elements - corner ornaments
    c.setStrokeColor(GOLD)
    c.setLineWidth(2)
    corner_size = 20
    
    # Top-left corner
    c.line(inner_margin, height - inner_margin - corner_size, inner_margin, height - inner_margin)
    c.line(inner_margin, height - inner_margin, inner_margin + corner_size, height - inner_margin)
    
    # Top-right corner
    c.line(width - inner_margin - corner_size, height - inner_margin, width - inner_margin, height - inner_margin)
    c.line(width - inner_margin, height - inner_margin, width - inner_margin, height - inner_margin - corner_size)
    
    # Bottom-left corner
    c.line(inner_margin, inner_margin, inner_margin, inner_margin + corner_size)
    c.line(inner_margin, inner_margin, inner_margin + corner_size, inner_margin)
    
    # Bottom-right corner
    c.line(width - inner_margin - corner_size, inner_margin, width - inner_margin, inner_margin)
    c.line(width - inner_margin, inner_margin, width - inner_margin, inner_margin + corner_size)
    
    c.save()
    return output_path


def get_qr_code_base64(verification_url: str) -> str:
    """Generate QR code and return as base64 string"""
    qr_buffer = generate_qr_code(verification_url)
    return base64.b64encode(qr_buffer.getvalue()).decode('utf-8')
