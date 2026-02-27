"""
BAC Official PDF Template
This module provides the official company letterhead design for all PDF outputs.
Based on the company's Quality Policy document template.
"""

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm, mm
from reportlab.lib.colors import HexColor, black, white
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pathlib import Path
import qrcode
from io import BytesIO

# Company information
COMPANY_NAME_AR = "بيان للتحقق والمطابقة"
COMPANY_NAME_EN = "BAYAN AUDITING & CONFORMITY"
COMPANY_SHORT = "BAC"
COMPANY_PHONE = "+966 55 123 4567"  # Update with actual phone
COMPANY_WEBSITE = "www.bfrvc.sa"  # Update with actual website
COMPANY_DIRECTOR = "Director"

# Colors
PRIMARY_COLOR = HexColor('#1e3a5f')  # Dark navy blue
SECONDARY_COLOR = HexColor('#c9a55c')  # Gold accent
TEXT_COLOR = black
LIGHT_GRAY = HexColor('#f5f5f5')

# Paths
ROOT_DIR = Path(__file__).parent
ASSETS_DIR = ROOT_DIR / "assets"
FONTS_DIR = ROOT_DIR / "fonts"
LOGO_PATH = ASSETS_DIR / "bayan-logo.png"


def register_arabic_fonts():
    """Register Arabic fonts if available"""
    font_path = FONTS_DIR / "Amiri-Regular.ttf"
    font_bold_path = FONTS_DIR / "Amiri-Bold.ttf"
    
    if font_path.exists():
        try:
            pdfmetrics.registerFont(TTFont('Amiri', str(font_path)))
            if font_bold_path.exists():
                pdfmetrics.registerFont(TTFont('Amiri-Bold', str(font_bold_path)))
            return True
        except Exception as e:
            print(f"Error registering Arabic font: {e}")
    return False


def draw_arabic_text(c, text, x, y, font_size=11, bold=False, align='right'):
    """Draw Arabic text with proper reshaping"""
    try:
        import arabic_reshaper
        from bidi.algorithm import get_display
        
        reshaped = arabic_reshaper.reshape(str(text))
        bidi_text = get_display(reshaped)
        
        font_name = 'Amiri-Bold' if bold else 'Amiri'
        try:
            c.setFont(font_name, font_size)
        except:
            c.setFont('Helvetica-Bold' if bold else 'Helvetica', font_size)
        
        if align == 'right':
            c.drawRightString(x, y, bidi_text)
        elif align == 'center':
            c.drawCentredString(x, y, bidi_text)
        else:
            c.drawString(x, y, bidi_text)
    except Exception as e:
        print(f"Error drawing Arabic text: {e}")
        c.setFont('Helvetica-Bold' if bold else 'Helvetica', font_size)
        if align == 'right':
            c.drawRightString(x, y, str(text))
        elif align == 'center':
            c.drawCentredString(x, y, str(text))
        else:
            c.drawString(x, y, str(text))


def generate_qr_code(data, size=60):
    """Generate QR code image"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=2,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return buffer


def draw_header(c, width, height, title_en="", title_ar="", ref_number=None, date=None):
    """
    Draw the official BAC header on the PDF.
    White background with logo on top-left, Arabic name above English name.
    """
    # White background (default)
    
    # Draw logo on top-left
    logo_x = 40
    logo_y = height - 80
    logo_width = 70
    logo_height = 60
    
    if LOGO_PATH.exists():
        try:
            c.drawImage(str(LOGO_PATH), logo_x, logo_y, width=logo_width, height=logo_height, 
                       preserveAspectRatio=True, mask='auto')
        except Exception as e:
            print(f"Error drawing logo: {e}")
    
    # Company name - Arabic above English (next to logo)
    name_x = logo_x + logo_width + 15
    name_y = height - 35
    
    # Arabic company name
    c.setFillColor(PRIMARY_COLOR)
    draw_arabic_text(c, COMPANY_NAME_AR, name_x + 150, name_y, font_size=14, bold=True, align='right')
    
    # English company name
    c.setFont('Helvetica-Bold', 10)
    c.setFillColor(PRIMARY_COLOR)
    c.drawString(name_x, name_y - 18, COMPANY_NAME_EN)
    
    # Document title (centered, if provided)
    if title_en or title_ar:
        title_y = height - 100
        
        if title_en:
            c.setFont('Helvetica-Bold', 18)
            c.setFillColor(PRIMARY_COLOR)
            c.drawCentredString(width / 2, title_y, title_en)
        
        if title_ar:
            draw_arabic_text(c, title_ar, width / 2, title_y - 25, font_size=16, bold=True, align='center')
    
    # Reference and date (top right)
    if ref_number or date:
        ref_y = height - 30
        c.setFont('Helvetica', 9)
        c.setFillColor(TEXT_COLOR)
        
        if ref_number:
            c.drawRightString(width - 40, ref_y, f"Ref: {ref_number}")
        if date:
            c.drawRightString(width - 40, ref_y - 12, f"Date: {date}")
    
    # Return the Y position where content should start
    return height - 140 if (title_en or title_ar) else height - 100


def draw_footer(c, width, height, page_num=None, total_pages=None):
    """
    Draw the official BAC footer on the PDF.
    Horizontal line separator, QR code, phone, website, director info.
    """
    footer_y = 60  # Footer starts at this Y position
    
    # Horizontal separator line
    c.setStrokeColor(PRIMARY_COLOR)
    c.setLineWidth(1)
    c.line(40, footer_y + 30, width - 40, footer_y + 30)
    
    # QR Code (left side)
    qr_x = 45
    qr_y = footer_y - 25
    qr_size = 50
    
    try:
        qr_buffer = generate_qr_code(f"https://{COMPANY_WEBSITE}")
        from reportlab.lib.utils import ImageReader
        qr_image = ImageReader(qr_buffer)
        c.drawImage(qr_image, qr_x, qr_y, width=qr_size, height=qr_size)
    except Exception as e:
        print(f"Error drawing QR code: {e}")
    
    # Contact info (center)
    info_x = qr_x + qr_size + 30
    info_y = footer_y + 15
    
    c.setFont('Helvetica', 8)
    c.setFillColor(TEXT_COLOR)
    
    # Phone with icon representation
    c.drawString(info_x, info_y, f"Tel: {COMPANY_PHONE}")
    
    # Website
    c.drawString(info_x, info_y - 12, f"Web: {COMPANY_WEBSITE}")
    
    # Director and company name (right side)
    right_x = width - 45
    c.setFont('Helvetica-Bold', 8)
    c.drawRightString(right_x, info_y, COMPANY_DIRECTOR)
    c.setFont('Helvetica', 8)
    c.drawRightString(right_x, info_y - 12, f"{COMPANY_NAME_EN} ({COMPANY_SHORT})")
    
    # Page number (if provided)
    if page_num is not None:
        page_text = f"Page {page_num}"
        if total_pages:
            page_text += f" of {total_pages}"
        c.setFont('Helvetica', 8)
        c.drawCentredString(width / 2, footer_y - 35, page_text)
    
    # Return the Y position where content should end (above footer)
    return footer_y + 40


def create_pdf_with_template(filepath, title_en="", title_ar="", ref_number=None, date=None):
    """
    Create a new PDF canvas with the official BAC template.
    Returns the canvas, width, height, content_start_y, and content_end_y.
    """
    # Register Arabic fonts
    register_arabic_fonts()
    
    # Create canvas
    c = canvas.Canvas(str(filepath), pagesize=A4)
    width, height = A4
    
    # Draw header and get content start position
    content_start_y = draw_header(c, width, height, title_en, title_ar, ref_number, date)
    
    # Get content end position (above footer)
    content_end_y = draw_footer(c, width, height)
    
    return c, width, height, content_start_y, content_end_y


def add_new_page(c, width, height, title_en="", title_ar="", page_num=None, total_pages=None):
    """
    Add a new page with header and footer.
    Returns the content_start_y and content_end_y for the new page.
    """
    c.showPage()
    
    # Draw header
    content_start_y = draw_header(c, width, height, title_en, title_ar)
    
    # Draw footer
    content_end_y = draw_footer(c, width, height, page_num, total_pages)
    
    return content_start_y, content_end_y


def draw_section_header(c, width, en_text, ar_text, y_pos):
    """Draw a bilingual section header with underline"""
    c.setFillColor(PRIMARY_COLOR)
    c.setFont('Helvetica-Bold', 12)
    c.drawString(50, y_pos, en_text)
    draw_arabic_text(c, ar_text, width - 50, y_pos, 12, bold=True)
    
    c.setStrokeColor(PRIMARY_COLOR)
    c.setLineWidth(0.5)
    c.line(50, y_pos - 5, width - 50, y_pos - 5)
    
    return y_pos - 25


def draw_field_row(c, width, label_en, label_ar, value, y_pos, value_ar=None):
    """Draw a bilingual field row with label and value"""
    c.setFillColor(TEXT_COLOR)
    
    # English side (left)
    c.setFont('Helvetica-Bold', 9)
    c.drawString(50, y_pos, f"{label_en}:")
    c.setFont('Helvetica', 9)
    value_str = str(value) if value else 'N/A'
    c.drawString(150, y_pos, value_str[:40])  # Truncate if too long
    
    # Arabic side (right)
    draw_arabic_text(c, f":{label_ar}", width - 50, y_pos, 9, bold=True)
    if value_ar:
        draw_arabic_text(c, value_ar, width - 150, y_pos, 9)
    else:
        draw_arabic_text(c, value_str, width - 150, y_pos, 9)
    
    return y_pos - 18


# Update company info function (can be called to set custom values)
def set_company_info(phone=None, website=None, director=None):
    """Update company contact information"""
    global COMPANY_PHONE, COMPANY_WEBSITE, COMPANY_DIRECTOR
    if phone:
        COMPANY_PHONE = phone
    if website:
        COMPANY_WEBSITE = website
    if director:
        COMPANY_DIRECTOR = director
