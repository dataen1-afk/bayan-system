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
from reportlab.lib import colors
from pathlib import Path
from io import BytesIO
import qrcode

# Company information
COMPANY_NAME_AR = "بيان للتحقق والمطابقة"
COMPANY_NAME_EN = "BAYAN AUDITING & CONFORMITY"
COMPANY_SHORT = "BAC"
COMPANY_PHONE = "+966 55 123 4567"
COMPANY_WEBSITE = "www.bfrvc.sa"
COMPANY_DIRECTOR = "Director"

# Colors
PRIMARY_COLOR = HexColor('#1e3a5f')
SECTION_COLOR = HexColor('#4a7c9b')
LIGHT_BG = HexColor('#f8f9fa')
ACCENT_COLOR = HexColor('#c9a55c')

# Paths
ROOT_DIR = Path(__file__).parent
ASSETS_DIR = ROOT_DIR / "assets"
FONTS_DIR = ROOT_DIR / "fonts"
LOGO_PATH = ASSETS_DIR / "bayan-logo.png"


class BACPDFTemplate:
    """
    Official BAC PDF Template class.
    Provides header, footer, and common styling for all PDF documents.
    """
    
    def __init__(self, canvas_obj, width, height):
        self.c = canvas_obj
        self.width = width
        self.height = height
        self.arabic_font_available = self._register_fonts()
        self.font_bold_path = FONTS_DIR / "Amiri-Bold.ttf"
    
    def _register_fonts(self):
        """Register Arabic fonts"""
        font_path = FONTS_DIR / "Amiri-Regular.ttf"
        font_bold_path = FONTS_DIR / "Amiri-Bold.ttf"
        
        if font_path.exists():
            try:
                pdfmetrics.registerFont(TTFont('Amiri', str(font_path)))
                if font_bold_path.exists():
                    pdfmetrics.registerFont(TTFont('Amiri-Bold', str(font_bold_path)))
                return True
            except Exception as e:
                print(f"Error registering font: {e}")
        return False
    
    def draw_arabic(self, text, x, y, size=10, bold=False, right_align=False, center=False):
        """Draw Arabic text with proper reshaping"""
        if not text:
            return
        try:
            import arabic_reshaper
            from bidi.algorithm import get_display
            
            reshaped = arabic_reshaper.reshape(str(text))
            bidi_text = get_display(reshaped)
            
            if self.arabic_font_available:
                font = 'Amiri-Bold' if bold and self.font_bold_path.exists() else 'Amiri'
            else:
                font = 'Helvetica-Bold' if bold else 'Helvetica'
            
            self.c.setFont(font, size)
            
            if center:
                self.c.drawCentredString(x, y, bidi_text)
            elif right_align:
                self.c.drawRightString(x, y, bidi_text)
            else:
                self.c.drawString(x, y, bidi_text)
        except Exception as e:
            print(f"Error drawing Arabic: {e}")
            self.c.setFont('Helvetica-Bold' if bold else 'Helvetica', size)
            if center:
                self.c.drawCentredString(x, y, str(text))
            elif right_align:
                self.c.drawRightString(x, y, str(text))
            else:
                self.c.drawString(x, y, str(text))
    
    def draw_header(self, title_en="", title_ar="", form_code="", date_str=""):
        """
        Draw the official BAC header.
        Returns the Y position where content should start.
        """
        c = self.c
        width = self.width
        height = self.height
        
        # Logo on top-left
        logo_x = 40
        logo_y = height - 75
        
        if LOGO_PATH.exists():
            try:
                c.drawImage(str(LOGO_PATH), logo_x, logo_y, width=60, height=55, 
                           preserveAspectRatio=True, mask='auto')
            except Exception as e:
                print(f"Error drawing logo: {e}")
        
        # Company name next to logo
        name_x = logo_x + 70
        name_y = height - 30
        
        c.setFillColor(PRIMARY_COLOR)
        self.draw_arabic(COMPANY_NAME_AR, name_x + 130, name_y, 13, bold=True, right_align=True)
        c.setFont('Helvetica-Bold', 9)
        c.setFillColor(PRIMARY_COLOR)
        c.drawString(name_x, name_y - 15, COMPANY_NAME_EN)
        
        # Document title - centered
        if title_en or title_ar:
            title_y = height - 95
            if title_en:
                c.setFont('Helvetica-Bold', 16)
                c.setFillColor(PRIMARY_COLOR)
                c.drawCentredString(width / 2, title_y, title_en)
            if title_ar:
                self.draw_arabic(title_ar, width / 2, title_y - 20, 14, bold=True, center=True)
        
        # Form code and date - top right
        c.setFont('Helvetica', 9)
        c.setFillColor(black)
        if form_code:
            c.drawRightString(width - 40, height - 25, form_code)
        if date_str:
            c.drawRightString(width - 40, height - 38, f"Date: {date_str}")
        
        return height - 130 if (title_en or title_ar) else height - 90
    
    def draw_footer(self, page_num=None, total_pages=None, form_code=""):
        """
        Draw the official BAC footer.
        Returns the Y position where content should end.
        """
        c = self.c
        width = self.width
        footer_y = 55
        
        # Horizontal separator line
        c.setStrokeColor(PRIMARY_COLOR)
        c.setLineWidth(1)
        c.line(40, footer_y + 25, width - 40, footer_y + 25)
        
        # QR Code (left side)
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
        except Exception:
            pass
        
        # Contact info (center-left)
        info_x = 100
        info_y = footer_y + 12
        c.setFont('Helvetica', 8)
        c.setFillColor(black)
        c.drawString(info_x, info_y, f"Tel: {COMPANY_PHONE}")
        c.drawString(info_x, info_y - 11, f"Web: {COMPANY_WEBSITE}")
        
        # Director and company (right side)
        c.setFont('Helvetica-Bold', 8)
        c.drawRightString(width - 45, info_y, COMPANY_DIRECTOR)
        c.setFont('Helvetica', 8)
        c.drawRightString(width - 45, info_y - 11, f"{COMPANY_NAME_EN} ({COMPANY_SHORT})")
        
        # Page number (center bottom)
        if page_num is not None:
            page_text = f"Page {page_num}"
            if total_pages:
                page_text += f" of {total_pages}"
            if form_code:
                page_text += f" | {form_code}"
            c.setFont('Helvetica', 7)
            c.drawCentredString(width / 2, footer_y - 30, page_text)
        
        return footer_y + 35
    
    def draw_section_header(self, en_text, ar_text, y_pos):
        """Draw a bilingual section header with underline"""
        c = self.c
        width = self.width
        
        c.setFillColor(PRIMARY_COLOR)
        c.setFont('Helvetica-Bold', 11)
        c.drawString(50, y_pos, en_text)
        self.draw_arabic(ar_text, width - 50, y_pos, 11, bold=True, right_align=True)
        
        c.setStrokeColor(SECTION_COLOR)
        c.setLineWidth(0.5)
        c.line(50, y_pos - 5, width - 50, y_pos - 5)
        
        return y_pos - 22
    
    def draw_field_row(self, label_en, label_ar, value, y_pos, value_ar=None):
        """Draw a bilingual field row"""
        c = self.c
        width = self.width
        
        c.setFillColor(black)
        c.setFont('Helvetica-Bold', 9)
        c.drawString(50, y_pos, f"{label_en}:")
        c.setFont('Helvetica', 9)
        value_str = str(value)[:40] if value else 'N/A'
        c.drawString(150, y_pos, value_str)
        
        self.draw_arabic(f":{label_ar}", width - 50, y_pos, 9, bold=True, right_align=True)
        self.draw_arabic(value_ar or value_str, width - 150, y_pos, 9, right_align=True)
        
        return y_pos - 16
    
    def new_page(self, title_en="", title_ar="", form_code=""):
        """Start a new page with header and footer"""
        self.c.showPage()
        content_start = self.draw_header(title_en, title_ar, form_code)
        return content_start


def create_bac_pdf(filepath, title_en="", title_ar="", form_code="", date_str=""):
    """
    Create a new PDF with official BAC template.
    Returns (canvas, template, width, height, content_start_y, content_end_y)
    """
    from datetime import datetime
    
    c = canvas.Canvas(str(filepath), pagesize=A4)
    width, height = A4
    template = BACPDFTemplate(c, width, height)
    
    if not date_str:
        date_str = datetime.now().strftime('%Y-%m-%d')
    
    content_start = template.draw_header(title_en, title_ar, form_code, date_str)
    content_end = template.draw_footer(form_code=form_code)
    
    return c, template, width, height, content_start, content_end

