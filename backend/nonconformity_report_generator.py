"""
Nonconformity Report (BACF6-13) PDF Generator
Bilingual PDF with English and Arabic support
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, black, white
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Table, TableStyle
from pathlib import Path
import arabic_reshaper
from bidi.algorithm import get_display
import io

# Register Arabic fonts
FONTS_DIR = Path(__file__).parent / "fonts"
try:
    pdfmetrics.registerFont(TTFont('Amiri', str(FONTS_DIR / 'Amiri-Regular.ttf')))
    pdfmetrics.registerFont(TTFont('Amiri-Bold', str(FONTS_DIR / 'Amiri-Bold.ttf')))
except:
    pass

# Colors
PRIMARY_COLOR = HexColor('#1e3a5f')
SECONDARY_COLOR = HexColor('#2c5282')
LIGHT_GRAY = HexColor('#f7fafc')
BORDER_COLOR = HexColor('#e2e8f0')
TEXT_COLOR = HexColor('#2d3748')
MAJOR_NC_COLOR = HexColor('#e53e3e')  # Red for major
MINOR_NC_COLOR = HexColor('#dd6b20')  # Orange for minor
SUCCESS_COLOR = HexColor('#38a169')  # Green for closed


def reshape_arabic(text):
    """Reshape Arabic text for proper RTL display"""
    if not text:
        return ""
    try:
        reshaped = arabic_reshaper.reshape(str(text))
        return get_display(reshaped)
    except:
        return str(text)


def generate_nonconformity_report_pdf(data: dict) -> bytes:
    """Generate bilingual Nonconformity Report PDF"""
    
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    # Draw content
    draw_header(c, width, height, data)
    y = height - 6*cm
    
    y = draw_info_section(c, data, y, width)
    y = draw_nonconformities_table(c, data, y, width, height)
    y = draw_verification_section(c, data, y, width, height)
    y = draw_signature_section(c, data, y, width, height)
    
    draw_footer(c, width, data)
    
    c.save()
    buffer.seek(0)
    return buffer.getvalue()


def draw_header(c, width, height, data):
    """Draw document header with logo"""
    # Header background
    c.setFillColor(PRIMARY_COLOR)
    c.rect(0, height - 2.5*cm, width, 2.5*cm, fill=True, stroke=False)
    
    # Logo
    logo_path = Path(__file__).parent / "assets" / "bayan-logo.png"
    if logo_path.exists():
        try:
            c.drawImage(str(logo_path), 1.5*cm, height - 2.2*cm, width=3*cm, height=1.8*cm, preserveAspectRatio=True, mask='auto')
        except:
            pass
    
    # Company name
    c.setFillColor(white)
    c.setFont('Helvetica-Bold', 14)
    c.drawRightString(width - 1.5*cm, height - 1.2*cm, "BAYAN")
    
    c.setFont('Helvetica', 9)
    c.drawRightString(width - 1.5*cm, height - 1.7*cm, "Auditing & Conformity Assessment")
    
    c.setFont('Amiri', 9)
    c.drawRightString(width - 1.5*cm, height - 2.1*cm, reshape_arabic("بيان للتدقيق وتقييم المطابقة"))
    
    # Title
    y = height - 3.5*cm
    c.setFont('Helvetica-Bold', 16)
    c.setFillColor(PRIMARY_COLOR)
    c.drawString(2*cm, y, "Nonconformity Report")
    
    c.setFont('Amiri-Bold', 16)
    c.drawRightString(width - 2*cm, y, reshape_arabic("تقرير عدم المطابقة"))
    
    # Form number
    y -= 0.6*cm
    c.setFont('Helvetica', 10)
    c.setFillColor(TEXT_COLOR)
    c.drawString(2*cm, y, "BAC-F6-13")


def draw_info_section(c, data, y, width):
    """Draw the header information section"""
    
    y -= 0.5*cm
    
    # Background box
    c.setFillColor(LIGHT_GRAY)
    c.roundRect(1.5*cm, y - 4.5*cm, width - 3*cm, 4.5*cm, 5, fill=True, stroke=False)
    c.setStrokeColor(BORDER_COLOR)
    c.roundRect(1.5*cm, y - 4.5*cm, width - 3*cm, 4.5*cm, 5, fill=False, stroke=True)
    
    field_y = y - 0.5*cm
    
    # Row 1: Client
    c.setFont('Helvetica-Bold', 9)
    c.setFillColor(PRIMARY_COLOR)
    c.drawString(2*cm, field_y, "Client:")
    c.setFont('Helvetica', 9)
    c.setFillColor(TEXT_COLOR)
    c.drawString(4.5*cm, field_y, data.get("client_name", "—"))
    
    c.setFont('Amiri-Bold', 9)
    c.setFillColor(PRIMARY_COLOR)
    c.drawRightString(width - 2*cm, field_y, reshape_arabic(":العميل"))
    
    # Row 2: Certificate No & Standards
    field_y -= 0.7*cm
    c.setFont('Helvetica-Bold', 9)
    c.setFillColor(PRIMARY_COLOR)
    c.drawString(2*cm, field_y, "Certificate(s) No:")
    c.setFont('Helvetica', 9)
    c.setFillColor(TEXT_COLOR)
    c.drawString(5*cm, field_y, data.get("certificate_no", "—"))
    
    c.setFont('Helvetica-Bold', 9)
    c.setFillColor(PRIMARY_COLOR)
    c.drawString(10*cm, field_y, "Standard(s):")
    c.setFont('Helvetica', 9)
    c.setFillColor(TEXT_COLOR)
    standards = data.get("standards", [])
    c.drawString(13*cm, field_y, ", ".join(standards) if standards else "—")
    
    # Row 3: Audit Type & Date
    field_y -= 0.7*cm
    c.setFont('Helvetica-Bold', 9)
    c.setFillColor(PRIMARY_COLOR)
    c.drawString(2*cm, field_y, "Type of Audit:")
    c.setFont('Helvetica', 9)
    c.setFillColor(TEXT_COLOR)
    c.drawString(5*cm, field_y, data.get("audit_type", "—"))
    
    c.setFont('Helvetica-Bold', 9)
    c.setFillColor(PRIMARY_COLOR)
    c.drawString(10*cm, field_y, "Date of Audit:")
    c.setFont('Helvetica', 9)
    c.setFillColor(TEXT_COLOR)
    c.drawString(13*cm, field_y, data.get("audit_date", "—"))
    
    # Row 4: Lead Auditor
    field_y -= 0.7*cm
    c.setFont('Helvetica-Bold', 9)
    c.setFillColor(PRIMARY_COLOR)
    c.drawString(2*cm, field_y, "Lead Auditor:")
    c.setFont('Helvetica', 9)
    c.setFillColor(TEXT_COLOR)
    c.drawString(5*cm, field_y, data.get("lead_auditor", "—"))
    
    # Row 5: Management Representative
    field_y -= 0.7*cm
    c.setFont('Helvetica-Bold', 9)
    c.setFillColor(PRIMARY_COLOR)
    c.drawString(2*cm, field_y, "Management Representative:")
    c.setFont('Helvetica', 9)
    c.setFillColor(TEXT_COLOR)
    c.drawString(6.5*cm, field_y, data.get("management_representative", "—"))
    
    # NC Summary
    field_y -= 0.7*cm
    total_major = data.get("total_major", 0)
    total_minor = data.get("total_minor", 0)
    
    c.setFont('Helvetica-Bold', 9)
    c.setFillColor(MAJOR_NC_COLOR)
    c.drawString(2*cm, field_y, f"Major NCs: {total_major}")
    
    c.setFillColor(MINOR_NC_COLOR)
    c.drawString(6*cm, field_y, f"Minor NCs: {total_minor}")
    
    c.setFillColor(SUCCESS_COLOR)
    c.drawString(10*cm, field_y, f"Closed: {data.get('closed_count', 0)}")
    
    return y - 5.2*cm


def draw_nonconformities_table(c, data, y, width, height):
    """Draw the nonconformities table"""
    
    # Section header
    c.setFillColor(SECONDARY_COLOR)
    c.roundRect(1.5*cm, y - 0.7*cm, width - 3*cm, 0.7*cm, 3, fill=True, stroke=False)
    
    c.setFillColor(white)
    c.setFont('Helvetica-Bold', 10)
    c.drawString(2*cm, y - 0.5*cm, "Nonconformities / عدم المطابقات")
    
    y -= 1.2*cm
    
    nonconformities = data.get("nonconformities", [])
    
    if not nonconformities:
        c.setFont('Helvetica', 10)
        c.setFillColor(TEXT_COLOR)
        c.drawString(2*cm, y, "No nonconformities recorded.")
        return y - 1*cm
    
    # Draw each nonconformity
    for i, nc in enumerate(nonconformities):
        if y < 5*cm:
            # New page
            c.showPage()
            draw_header(c, width, height, data)
            y = height - 5*cm
        
        # NC Header
        nc_type = nc.get("nc_type", "minor")
        type_color = MAJOR_NC_COLOR if nc_type == "major" else MINOR_NC_COLOR
        type_label = "MJ - Major" if nc_type == "major" else "MN - Minor"
        
        c.setFillColor(type_color)
        c.roundRect(1.5*cm, y - 0.6*cm, width - 3*cm, 0.6*cm, 3, fill=True, stroke=False)
        
        c.setFillColor(white)
        c.setFont('Helvetica-Bold', 9)
        c.drawString(2*cm, y - 0.45*cm, f"NC #{i+1} - {type_label}")
        
        c.setFont('Helvetica', 9)
        c.drawString(7*cm, y - 0.45*cm, f"Clause: {nc.get('standard_clause', '—')}")
        
        status = nc.get("status", "open")
        status_label = "CLOSED" if status == "closed" else "OPEN"
        c.drawRightString(width - 2*cm, y - 0.45*cm, status_label)
        
        y -= 1*cm
        
        # NC Details in box
        box_height = 3.5*cm
        c.setFillColor(white)
        c.setStrokeColor(BORDER_COLOR)
        c.roundRect(1.5*cm, y - box_height, width - 3*cm, box_height, 3, fill=True, stroke=True)
        
        detail_y = y - 0.4*cm
        
        # Description
        c.setFont('Helvetica-Bold', 8)
        c.setFillColor(PRIMARY_COLOR)
        c.drawString(2*cm, detail_y, "Description:")
        c.setFont('Helvetica', 8)
        c.setFillColor(TEXT_COLOR)
        desc = nc.get("description", "")[:80]
        c.drawString(4.5*cm, detail_y, desc + ("..." if len(nc.get("description", "")) > 80 else ""))
        
        # Root Cause
        detail_y -= 0.5*cm
        c.setFont('Helvetica-Bold', 8)
        c.setFillColor(PRIMARY_COLOR)
        c.drawString(2*cm, detail_y, "Root Cause:")
        c.setFont('Helvetica', 8)
        c.setFillColor(TEXT_COLOR)
        root = nc.get("root_cause", "")[:80]
        c.drawString(4.5*cm, detail_y, root + ("..." if len(nc.get("root_cause", "")) > 80 else ""))
        
        # Corrections
        detail_y -= 0.5*cm
        c.setFont('Helvetica-Bold', 8)
        c.setFillColor(PRIMARY_COLOR)
        c.drawString(2*cm, detail_y, "Corrections:")
        c.setFont('Helvetica', 8)
        c.setFillColor(TEXT_COLOR)
        corr = nc.get("corrections", "")[:80]
        c.drawString(4.5*cm, detail_y, corr + ("..." if len(nc.get("corrections", "")) > 80 else ""))
        
        # Corrective Actions
        detail_y -= 0.5*cm
        c.setFont('Helvetica-Bold', 8)
        c.setFillColor(PRIMARY_COLOR)
        c.drawString(2*cm, detail_y, "Corrective Actions:")
        c.setFont('Helvetica', 8)
        c.setFillColor(TEXT_COLOR)
        ca = nc.get("corrective_actions", "")[:70]
        c.drawString(5.5*cm, detail_y, ca + ("..." if len(nc.get("corrective_actions", "")) > 70 else ""))
        
        # Verification
        detail_y -= 0.5*cm
        c.setFont('Helvetica-Bold', 8)
        c.setFillColor(PRIMARY_COLOR)
        c.drawString(2*cm, detail_y, "Verification:")
        c.setFont('Helvetica', 8)
        c.setFillColor(TEXT_COLOR)
        verif = nc.get("verification_decision", "")[:70]
        c.drawString(4.5*cm, detail_y, verif + ("..." if len(nc.get("verification_decision", "")) > 70 else ""))
        
        y -= box_height + 0.5*cm
    
    return y


def draw_verification_section(c, data, y, width, height):
    """Draw the verification options section"""
    
    if y < 6*cm:
        c.showPage()
        draw_header(c, width, height, data)
        y = height - 5*cm
    
    # Deadline notice
    deadline = data.get("submission_deadline", "")
    if deadline:
        c.setFont('Helvetica-Bold', 9)
        c.setFillColor(MAJOR_NC_COLOR)
        c.drawString(2*cm, y, f"Deadline for submitting corrective action evidence: {deadline}")
        y -= 0.8*cm
    
    # Verification options header
    c.setFillColor(SECONDARY_COLOR)
    c.roundRect(1.5*cm, y - 0.6*cm, width - 3*cm, 0.6*cm, 3, fill=True, stroke=False)
    
    c.setFillColor(white)
    c.setFont('Helvetica-Bold', 9)
    c.drawString(2*cm, y - 0.45*cm, "Verification Options")
    
    y -= 1.2*cm
    
    # Verification checkboxes
    options = data.get("verification_options", {})
    
    checkbox_items = [
        ("corrections_appropriate", "Correction(s) and corrective action(s) are appropriate"),
        ("corrections_verified", "Correction(s) has (have) been verified, including documents submitted"),
        ("verify_next_audit", "Correction(s) will be verified at the next audit"),
        ("re_audit_performed", "A re-audit was performed")
    ]
    
    for key, label in checkbox_items:
        checked = options.get(key, False)
        # Checkbox
        c.setStrokeColor(PRIMARY_COLOR)
        c.rect(2*cm, y - 0.1*cm, 0.4*cm, 0.4*cm, fill=False, stroke=True)
        
        if checked:
            c.setFillColor(PRIMARY_COLOR)
            c.setFont('Helvetica-Bold', 10)
            c.drawString(2.08*cm, y - 0.05*cm, "✓")
        
        c.setFont('Helvetica', 9)
        c.setFillColor(TEXT_COLOR)
        c.drawString(2.7*cm, y, label)
        
        y -= 0.6*cm
    
    return y - 0.5*cm


def draw_signature_section(c, data, y, width, height):
    """Draw signature section"""
    
    if y < 5*cm:
        c.showPage()
        draw_header(c, width, height, data)
        y = height - 5*cm
    
    # Signature boxes
    c.setStrokeColor(BORDER_COLOR)
    
    # Management Representative
    c.rect(1.5*cm, y - 2*cm, 5*cm, 2*cm, fill=False, stroke=True)
    c.setFont('Helvetica-Bold', 8)
    c.setFillColor(PRIMARY_COLOR)
    c.drawString(1.7*cm, y - 0.4*cm, "Management Representative")
    c.setFont('Helvetica', 8)
    c.setFillColor(TEXT_COLOR)
    c.drawString(1.7*cm, y - 1*cm, f"Name: {data.get('management_representative', '')}")
    c.drawString(1.7*cm, y - 1.5*cm, f"Date: {data.get('management_rep_date', '')}")
    
    # Audit Team Leader
    c.rect(7*cm, y - 2*cm, 5*cm, 2*cm, fill=False, stroke=True)
    c.setFont('Helvetica-Bold', 8)
    c.setFillColor(PRIMARY_COLOR)
    c.drawString(7.2*cm, y - 0.4*cm, "Audit Team Leader")
    c.setFont('Helvetica', 8)
    c.setFillColor(TEXT_COLOR)
    c.drawString(7.2*cm, y - 1*cm, f"Name: {data.get('lead_auditor', '')}")
    c.drawString(7.2*cm, y - 1.5*cm, f"Date: {data.get('audit_team_leader_date', '')}")
    
    # Lead Auditor (final)
    c.rect(12.5*cm, y - 2*cm, 5*cm, 2*cm, fill=False, stroke=True)
    c.setFont('Helvetica-Bold', 8)
    c.setFillColor(PRIMARY_COLOR)
    c.drawString(12.7*cm, y - 0.4*cm, "Lead Auditor (Final)")
    c.setFont('Helvetica', 8)
    c.setFillColor(TEXT_COLOR)
    c.drawString(12.7*cm, y - 1*cm, f"Signature: ___________")
    c.drawString(12.7*cm, y - 1.5*cm, f"Date: {data.get('final_date', '')}")
    
    return y - 2.5*cm


def draw_footer(c, width, data):
    """Draw document footer"""
    c.setFont('Helvetica', 8)
    c.setFillColor(HexColor('#718096'))
    c.drawString(1.5*cm, 1.5*cm, "BAC-F6-13 | Nonconformity Report")
    c.drawRightString(width - 1.5*cm, 1.5*cm, "BAYAN for Verification and Conformity Assessment")
    
    # Footer line
    c.setStrokeColor(BORDER_COLOR)
    c.line(1.5*cm, 2*cm, width - 1.5*cm, 2*cm)


if __name__ == "__main__":
    # Test PDF generation
    test_data = {
        "id": "test-001",
        "client_name": "Test Company LLC",
        "certificate_no": "CERT-2026-001",
        "standards": ["ISO 9001:2015"],
        "audit_type": "Stage 2",
        "audit_date": "2026-02-17",
        "lead_auditor": "Ahmed Al-Rashid",
        "management_representative": "Mohammad Ali",
        "total_major": 1,
        "total_minor": 2,
        "closed_count": 1,
        "submission_deadline": "2026-03-17",
        "nonconformities": [
            {
                "standard_clause": "7.1.5",
                "description": "Calibration records not maintained for 3 months",
                "nc_type": "major",
                "root_cause": "Lack of awareness about calibration requirements",
                "corrections": "Immediate calibration of all measuring equipment",
                "corrective_actions": "Training provided, procedure updated",
                "verification_decision": "Corrective action verified",
                "status": "closed"
            },
            {
                "standard_clause": "8.5.1",
                "description": "Work instructions outdated",
                "nc_type": "minor",
                "root_cause": "Document control process gap",
                "corrections": "Work instructions updated",
                "corrective_actions": "Quarterly review process implemented",
                "status": "open"
            }
        ],
        "verification_options": {
            "corrections_appropriate": True,
            "corrections_verified": True
        }
    }
    
    pdf_bytes = generate_nonconformity_report_pdf(test_data)
    with open("/tmp/nc_report_test.pdf", "wb") as f:
        f.write(pdf_bytes)
    print("PDF generated: /tmp/nc_report_test.pdf")
