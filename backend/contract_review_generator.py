"""
Contract Review PDF Generator (BACF6-04)
Generates a professional bilingual PDF for Contract Reviews / Audit Programs.
Uses the official BAC document template.
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
import qrcode

ROOT_DIR = Path(__file__).parent

# Company info
COMPANY_PHONE = "+966 55 123 4567"
COMPANY_WEBSITE = "www.bfrvc.sa"
PRIMARY_COLOR = colors.HexColor('#1e3a5f')

def generate_contract_review_pdf(review_data: dict) -> bytes:
    """
    Generate a professional bilingual Contract Review PDF (BACF6-04).
    Uses the official BAC document template design.
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
    
    # Colors - Official BAC colors
    primary_color = PRIMARY_COLOR
    section_color = colors.HexColor('#4a7c9b')
    light_bg = colors.HexColor('#f8f9fa')
    accent_color = colors.HexColor('#c9a55c')
    
    # Extract data
    org_name = review_data.get('organization_name', '')
    standards = review_data.get('standards', [])
    scope = review_data.get('scope_of_services', '')
    employees = review_data.get('total_employees', 0)
    application_date = review_data.get('application_date', '')
    client_id = review_data.get('client_id', '')
    
    # Client data
    consultant_name = review_data.get('consultant_name', '')
    consultant_affects = review_data.get('consultant_affects_impartiality', False)
    consultant_explanation = review_data.get('consultant_impact_explanation', '')
    exclusions = review_data.get('exclusions_justification', '')
    
    # Admin data
    contract_review_date = review_data.get('contract_review_date', '')
    risk_category = review_data.get('risk_category', '')
    complexity_category = review_data.get('complexity_category', '')
    integration_level = review_data.get('integration_level_percent', 100)
    combined_audit = review_data.get('combined_audit_ability_percent', 100)
    auditor_code_matched = review_data.get('auditor_code_matched', False)
    audit_times = review_data.get('audit_times', [])
    final_man_days = review_data.get('final_man_days', 0)
    lead_auditor = review_data.get('lead_auditor_name', '')
    auditor_names = review_data.get('auditor_names', [])
    other_team = review_data.get('other_team_members', '')
    tech_expert_needed = review_data.get('technical_expert_needed', False)
    tech_expert_name = review_data.get('technical_expert_name', '')
    cert_decision_maker = review_data.get('certification_decision_maker', '')
    prepared_by = review_data.get('prepared_by_name', '')
    prepared_date = review_data.get('prepared_by_date', '')
    reviewed_by = review_data.get('reviewed_by_name', '')
    reviewed_date = review_data.get('reviewed_by_date', '')
    
    # Helper function for Arabic text
    def draw_arabic(text, x, y, size=10, bold=False, right_align=False, center=False):
        if arabic_font_available:
            try:
                reshaped = arabic_reshaper.reshape(str(text))
                bidi_text = get_display(reshaped)
                font = 'Amiri-Bold' if bold and font_bold_path.exists() else 'Amiri'
                c.setFont(font, size)
                if center:
                    c.drawCentredString(x, y, bidi_text)
                elif right_align:
                    c.drawRightString(x, y, bidi_text)
                else:
                    c.drawString(x, y, bidi_text)
            except Exception:
                pass

    def draw_official_header(title_en="CONTRACT REVIEW", title_ar="مراجعة العقد"):
        """Draw the official BAC header"""
        logo_x = 40
        logo_y = height - 75
        
        if logo_path.exists():
            try:
                c.drawImage(str(logo_path), logo_x, logo_y, width=60, height=55, 
                           preserveAspectRatio=True, mask='auto')
            except Exception:
                pass
        
        name_x = logo_x + 70
        name_y = height - 30
        c.setFillColor(primary_color)
        draw_arabic("بيان للتحقق والمطابقة", name_x + 130, name_y, 13, bold=True, right_align=True)
        c.setFont('Helvetica-Bold', 9)
        c.drawString(name_x, name_y - 15, "BAYAN AUDITING & CONFORMITY")
        
        title_y = height - 95
        c.setFont('Helvetica-Bold', 16)
        c.setFillColor(primary_color)
        c.drawCentredString(width / 2, title_y, title_en)
        draw_arabic(title_ar, width / 2, title_y - 20, 14, bold=True, center=True)
        
        c.setFont('Helvetica', 9)
        c.setFillColor(colors.black)
        c.drawRightString(width - 40, height - 25, "BACF6-04")
        c.drawRightString(width - 40, height - 38, f"Date: {datetime.now().strftime('%Y-%m-%d')}")
        
        return height - 130

    def draw_official_footer(page_num=1):
        """Draw the official BAC footer"""
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
        except Exception:
            pass
        
        info_x = 100
        info_y = footer_y + 12
        c.setFont('Helvetica', 8)
        c.setFillColor(colors.black)
        c.drawString(info_x, info_y, f"Tel: {COMPANY_PHONE}")
        c.drawString(info_x, info_y - 11, f"Web: {COMPANY_WEBSITE}")
        
        c.setFont('Helvetica-Bold', 8)
        c.drawRightString(width - 45, info_y, "Director")
        c.setFont('Helvetica', 8)
        c.drawRightString(width - 45, info_y - 11, "BAYAN AUDITING & CONFORMITY (BAC)")
        
        c.setFont('Helvetica', 7)
        c.drawCentredString(width / 2, footer_y - 30, f"Page {page_num} | BACF6-04")
        
        return footer_y + 35
                if right_align:
                    c.drawRightString(x, y, bidi_text)
                else:
                    c.drawString(x, y, bidi_text)
            except:
                pass
    
    def new_page(page_num):
        c.showPage()
        return draw_official_header("CONTRACT REVIEW", "مراجعة العقد")
    
    # ============ PAGE 1 ============
    page_num = 1
    
    # Draw official header
    y = draw_official_header("CONTRACT REVIEW", "مراجعة العقد")
    
    # Title
    c.setFillColor(colors.white)
    c.setFont('Helvetica-Bold', 18)
    c.drawCentredString(width/2, height - 35, "CONTRACT REVIEW")
    c.setFont('Helvetica', 12)
    c.drawCentredString(width/2, height - 52, "Certification Body Application")
    draw_arabic("مراجعة العقد", width/2 + 50, height - 70, 14, bold=True)
    
    # Form reference
    c.setFont('Helvetica', 9)
    c.drawRightString(width - 25, height - 25, "BACF6-04")
    
    y = height - 120
    
    # Section 1: General Application Details
    c.setFillColor(section_color)
    c.setFont('Helvetica-Bold', 11)
    c.drawString(30, y, "1. General Application Details")
    draw_arabic("تفاصيل الطلب العامة", width - 30, y, 10, bold=True, right_align=True)
    y -= 20
    
    # Info boxes
    c.setFillColor(light_bg)
    c.roundRect(30, y - 45, width/3 - 40, 50, 5, fill=True, stroke=False)
    c.roundRect(width/3, y - 45, width/3 - 10, 50, 5, fill=True, stroke=False)
    c.roundRect(2*width/3, y - 45, width/3 - 30, 50, 5, fill=True, stroke=False)
    
    c.setFillColor(colors.black)
    c.setFont('Helvetica', 8)
    c.drawString(35, y - 10, "Application Date:")
    c.setFont('Helvetica-Bold', 9)
    c.drawString(35, y - 25, application_date or "___________")
    
    c.setFont('Helvetica', 8)
    c.drawString(width/3 + 5, y - 10, "Contract Review Date:")
    c.setFont('Helvetica-Bold', 9)
    c.drawString(width/3 + 5, y - 25, contract_review_date or "___________")
    
    c.setFont('Helvetica', 8)
    c.drawString(2*width/3 + 5, y - 10, "Client ID:")
    c.setFont('Helvetica-Bold', 9)
    c.drawString(2*width/3 + 5, y - 25, client_id or "___________")
    
    y -= 60
    
    # Section 2: Organization Information
    c.setFillColor(section_color)
    c.setFont('Helvetica-Bold', 11)
    c.drawString(30, y, "2. Organization Information")
    draw_arabic("معلومات المنظمة", width - 30, y, 10, bold=True, right_align=True)
    y -= 20
    
    c.setFillColor(light_bg)
    c.roundRect(30, y - 30, width - 60, 35, 5, fill=True, stroke=False)
    c.setStrokeColor(accent_color)
    c.setLineWidth(1.5)
    c.roundRect(30, y - 30, width - 60, 35, 5, fill=False, stroke=True)
    
    c.setFillColor(colors.black)
    c.setFont('Helvetica', 8)
    c.drawString(40, y - 8, "Name of Organization:")
    c.setFont('Helvetica-Bold', 11)
    c.drawString(40, y - 22, org_name or "_______________________________________________")
    
    y -= 50
    
    # Section 3: Consultant Information
    c.setFillColor(section_color)
    c.setFont('Helvetica-Bold', 11)
    c.drawString(30, y, "3. Consultant / Business Associates")
    draw_arabic("المستشار / شركاء الأعمال", width - 30, y, 10, bold=True, right_align=True)
    y -= 20
    
    c.setFillColor(light_bg)
    c.roundRect(30, y - 65, width - 60, 70, 5, fill=True, stroke=False)
    
    c.setFillColor(colors.black)
    c.setFont('Helvetica', 8)
    c.drawString(40, y - 10, "Name of Consultant/Business Associates (if any):")
    c.setFont('Helvetica', 9)
    c.drawString(40, y - 25, consultant_name or "_______________________________________")
    
    c.setFont('Helvetica', 8)
    c.drawString(40, y - 42, "Does the Consultant affect impartial auditing?")
    checkbox_yes = "☑" if consultant_affects else "☐"
    checkbox_no = "☐" if consultant_affects else "☑"
    c.drawString(250, y - 42, f"{checkbox_yes} Yes    {checkbox_no} No")
    
    if consultant_affects and consultant_explanation:
        c.setFont('Helvetica', 8)
        c.drawString(40, y - 57, f"If yes: {consultant_explanation[:60]}")
    
    y -= 85
    
    # Section 4: Exclusions
    c.setFillColor(section_color)
    c.setFont('Helvetica-Bold', 11)
    c.drawString(30, y, "4. Exclusions (Non-Applicable Clauses)")
    draw_arabic("الاستثناءات", width - 30, y, 10, bold=True, right_align=True)
    y -= 20
    
    c.setFillColor(light_bg)
    c.roundRect(30, y - 35, width - 60, 40, 5, fill=True, stroke=False)
    
    c.setFillColor(colors.black)
    c.setFont('Helvetica', 9)
    excl_text = exclusions if exclusions else "None / N/A"
    c.drawString(40, y - 15, excl_text[:80])
    if len(excl_text) > 80:
        c.drawString(40, y - 27, excl_text[80:160])
    
    y -= 55
    
    # Section 5: Standard and Scope
    c.setFillColor(section_color)
    c.setFont('Helvetica-Bold', 11)
    c.drawString(30, y, "5. Standard and Scope Information")
    draw_arabic("معلومات المعيار والنطاق", width - 30, y, 10, bold=True, right_align=True)
    y -= 20
    
    c.setFillColor(light_bg)
    c.roundRect(30, y - 75, width - 60, 80, 5, fill=True, stroke=False)
    
    c.setFillColor(colors.black)
    c.setFont('Helvetica', 8)
    c.drawString(40, y - 10, "Standard(s) Applicable:")
    c.setFont('Helvetica-Bold', 9)
    standards_str = ', '.join(standards) if standards else "_______________"
    c.drawString(150, y - 10, standards_str)
    
    c.setFont('Helvetica', 8)
    c.drawString(40, y - 28, "Scope:")
    c.setFont('Helvetica', 9)
    scope_lines = [scope[i:i+70] for i in range(0, min(len(scope), 140), 70)] if scope else ["_______________________________________"]
    for idx, line in enumerate(scope_lines):
        c.drawString(80, y - 28 - (idx * 12), line)
    
    c.setFont('Helvetica', 8)
    c.drawString(40, y - 58, "Number of Employees:")
    c.setFont('Helvetica-Bold', 9)
    c.drawString(150, y - 58, str(employees) if employees else "______")
    
    y -= 95
    
    # Section 6: Organization Characteristics
    c.setFillColor(section_color)
    c.setFont('Helvetica-Bold', 11)
    c.drawString(30, y, "6. Organization Characteristics for Audit Planning")
    draw_arabic("خصائص المنظمة لتخطيط التدقيق", width - 30, y, 10, bold=True, right_align=True)
    y -= 20
    
    c.setFillColor(light_bg)
    c.roundRect(30, y - 50, width/2 - 40, 55, 5, fill=True, stroke=False)
    c.roundRect(width/2, y - 50, width/2 - 30, 55, 5, fill=True, stroke=False)
    
    c.setFillColor(colors.black)
    c.setFont('Helvetica', 8)
    c.drawString(40, y - 12, "Risk Category (QMS):")
    c.setFont('Helvetica', 9)
    c.drawString(40, y - 26, risk_category or "_____________")
    
    c.setFont('Helvetica', 8)
    c.drawString(40, y - 42, "Complexity Category:")
    c.setFont('Helvetica', 9)
    c.drawString(150, y - 42, complexity_category or "_____________")
    
    c.setFont('Helvetica', 8)
    c.drawString(width/2 + 10, y - 12, f"Integration Level: {integration_level}%")
    c.drawString(width/2 + 10, y - 28, f"Combined Audit Ability: {combined_audit}%")
    
    auditor_match = "☑ Yes" if auditor_code_matched else "☐ Yes"
    c.drawString(width/2 + 10, y - 44, f"Auditor Code Matched: {auditor_match}")
    
    y -= 70
    
    draw_footer(page_num)
    
    # ============ PAGE 2 ============
    page_num += 1
    y = new_page(page_num)
    
    # Section 7: Audit Time Calculation
    c.setFillColor(section_color)
    c.setFont('Helvetica-Bold', 11)
    c.drawString(30, y, "7. Audit Time Calculation")
    draw_arabic("حساب وقت التدقيق", width - 30, y, 10, bold=True, right_align=True)
    y -= 15
    
    c.setFillColor(colors.black)
    c.setFont('Helvetica', 8)
    c.drawString(30, y, "As per IAF MD 5 / ISO 22003")
    y -= 20
    
    # Table header
    c.setFillColor(section_color)
    c.rect(30, y - 15, width - 60, 18, fill=True, stroke=False)
    c.setFillColor(colors.white)
    c.setFont('Helvetica-Bold', 8)
    
    col_widths = [80, 60, 50, 60, 60, 90]
    col_x = [30]
    for w in col_widths[:-1]:
        col_x.append(col_x[-1] + w)
    
    headers = ['Standard', 'Audit Type', 'Days', '% Increase', '% Reduction', 'Final Days']
    for i, header in enumerate(headers):
        c.drawCentredString(col_x[i] + col_widths[i]/2, y - 10, header)
    
    y -= 18
    
    # Table rows
    c.setFillColor(colors.black)
    c.setFont('Helvetica', 8)
    
    if audit_times:
        for entry in audit_times[:8]:  # Limit to 8 rows
            c.setFillColor(light_bg)
            c.rect(30, y - 15, width - 60, 15, fill=True, stroke=False)
            c.setFillColor(colors.black)
            
            row_data = [
                entry.get('standard', ''),
                entry.get('audit_type', ''),
                str(entry.get('num_days', '')),
                str(entry.get('percent_increase', '')),
                str(entry.get('percent_reduction', '')),
                str(entry.get('final_days', ''))
            ]
            for i, data in enumerate(row_data):
                c.drawCentredString(col_x[i] + col_widths[i]/2, y - 10, data)
            y -= 16
    else:
        # Empty rows
        for _ in range(5):
            c.setStrokeColor(colors.grey)
            c.rect(30, y - 15, width - 60, 15, fill=False, stroke=True)
            y -= 16
    
    y -= 10
    c.setFont('Helvetica-Bold', 9)
    c.drawString(30, y, f"Final Man-days during certification cycle: {final_man_days}")
    y -= 25
    
    # Section 8: Audit Team
    c.setFillColor(section_color)
    c.setFont('Helvetica-Bold', 11)
    c.drawString(30, y, "8. Team of Auditors")
    draw_arabic("فريق المدققين", width - 30, y, 10, bold=True, right_align=True)
    y -= 20
    
    c.setFillColor(light_bg)
    c.roundRect(30, y - 65, width - 60, 70, 5, fill=True, stroke=False)
    
    c.setFillColor(colors.black)
    c.setFont('Helvetica', 8)
    c.drawString(40, y - 12, "Lead Auditor (LA):")
    c.setFont('Helvetica-Bold', 9)
    c.drawString(130, y - 12, lead_auditor or "_______________________")
    
    c.setFont('Helvetica', 8)
    c.drawString(40, y - 28, "Auditor(s):")
    c.setFont('Helvetica', 9)
    auditors_str = ', '.join(auditor_names) if auditor_names else "_______________________"
    c.drawString(100, y - 28, auditors_str[:50])
    
    c.setFont('Helvetica', 8)
    c.drawString(40, y - 44, "Other(s):")
    c.setFont('Helvetica', 9)
    c.drawString(90, y - 44, other_team or "_______________________")
    
    tech_expert = "☑ Yes" if tech_expert_needed else "☐ No"
    c.setFont('Helvetica', 8)
    c.drawString(40, y - 58, f"Technical Expert Needed: {tech_expert}")
    if tech_expert_needed and tech_expert_name:
        c.drawString(200, y - 58, f"Name: {tech_expert_name}")
    
    y -= 85
    
    # Section 9: Decision Maker
    c.setFillColor(section_color)
    c.setFont('Helvetica-Bold', 11)
    c.drawString(30, y, "9. Certification Decision")
    draw_arabic("قرار الاعتماد", width - 30, y, 10, bold=True, right_align=True)
    y -= 20
    
    c.setFillColor(light_bg)
    c.roundRect(30, y - 25, width - 60, 30, 5, fill=True, stroke=False)
    
    c.setFillColor(colors.black)
    c.setFont('Helvetica', 8)
    c.drawString(40, y - 15, "Certification Decision Maker:")
    c.setFont('Helvetica-Bold', 9)
    c.drawString(180, y - 15, cert_decision_maker or "_______________________")
    
    y -= 50
    
    # Section 10: Approval Signatures
    c.setFillColor(section_color)
    c.setFont('Helvetica-Bold', 11)
    c.drawString(30, y, "10. Document Approval")
    draw_arabic("اعتماد الوثيقة", width - 30, y, 10, bold=True, right_align=True)
    y -= 25
    
    # Two signature boxes
    box_width = width/2 - 45
    box_height = 70
    
    # Prepared by box
    c.setFillColor(light_bg)
    c.roundRect(30, y - box_height, box_width, box_height, 5, fill=True, stroke=False)
    c.setStrokeColor(section_color)
    c.roundRect(30, y - box_height, box_width, box_height, 5, fill=False, stroke=True)
    
    c.setFillColor(section_color)
    c.setFont('Helvetica-Bold', 9)
    c.drawString(40, y - 12, "Prepared by (Technical Manager)")
    
    c.setFillColor(colors.black)
    c.setFont('Helvetica', 8)
    c.drawString(40, y - 30, f"Name: {prepared_by or '________________'}")
    c.drawString(40, y - 45, f"Date: {prepared_date or '________________'}")
    c.drawString(40, y - 60, "Signature: ________________")
    
    # Reviewed by box
    c.setFillColor(light_bg)
    c.roundRect(width/2 + 15, y - box_height, box_width, box_height, 5, fill=True, stroke=False)
    c.setStrokeColor(section_color)
    c.roundRect(width/2 + 15, y - box_height, box_width, box_height, 5, fill=False, stroke=True)
    
    c.setFillColor(section_color)
    c.setFont('Helvetica-Bold', 9)
    c.drawString(width/2 + 25, y - 12, "Reviewed by (Certification Manager)")
    
    c.setFillColor(colors.black)
    c.setFont('Helvetica', 8)
    c.drawString(width/2 + 25, y - 30, f"Name: {reviewed_by or '________________'}")
    c.drawString(width/2 + 25, y - 45, f"Date: {reviewed_date or '________________'}")
    c.drawString(width/2 + 25, y - 60, "Signature: ________________")
    
    draw_footer(page_num)
    
    # Save
    c.save()
    
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    return pdf_bytes


# For testing
if __name__ == "__main__":
    test_data = {
        "organization_name": "Test Company Ltd.",
        "standards": ["ISO 9001", "ISO 14001"],
        "scope_of_services": "Manufacturing of electronic components",
        "total_employees": 150,
        "application_date": "2025-02-17",
        "client_id": "CL-001",
        "consultant_name": "ABC Consulting",
        "consultant_affects_impartiality": False,
        "exclusions_justification": "Clause 7.1.5.2 - No monitoring/measuring equipment",
        "contract_review_date": "2025-02-18",
        "risk_category": "Medium",
        "complexity_category": "Standard",
        "lead_auditor_name": "John Smith",
        "auditor_names": ["Jane Doe", "Bob Wilson"],
        "certification_decision_maker": "Admin User",
        "prepared_by_name": "Technical Manager",
        "prepared_by_date": "2025-02-18",
        "reviewed_by_name": "Certification Manager",
        "reviewed_by_date": "2025-02-19"
    }
    
    pdf_bytes = generate_contract_review_pdf(test_data)
    
    output_path = ROOT_DIR / "contracts" / "test_contract_review.pdf"
    with open(output_path, 'wb') as f:
        f.write(pdf_bytes)
    print(f"Generated: {output_path}")
