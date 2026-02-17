"""
Grant Agreement Generator
Uses the official BAYAN DOCX template to generate professional Grant Agreement PDFs.
Fills all yellow-highlighted placeholders with client data from the database.
Preserves all terms, conditions, and formatting from the original template.
"""

from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_COLOR_INDEX
from pathlib import Path
import subprocess
import shutil
import os
import logging
import re
from datetime import datetime

ROOT_DIR = Path(__file__).parent
ASSETS_DIR = ROOT_DIR / "assets"
TEMPLATE_PATH = ASSETS_DIR / "grant_agreement_template.docx"
CONTRACTS_DIR = ROOT_DIR / "contracts"

# Ensure contracts directory exists
CONTRACTS_DIR.mkdir(exist_ok=True)

# Standard name mappings for checkbox matching
STANDARD_MAPPINGS = {
    'ISO9001': 'ISO 9001',
    'ISO 9001': 'ISO 9001',
    'ISO14001': 'ISO 14001',
    'ISO 14001': 'ISO 14001',
    'ISO45001': 'ISO 45001',
    'ISO 45001': 'ISO 45001',
    'ISO22000': 'ISO 22000',
    'ISO 22000': 'ISO 22000',
    'ISO22301': 'ISO 22301',
    'ISO 22301': 'ISO 22301',
    'ISO27001': 'ISO 27001',
    'ISO 27001': 'ISO 27001',
}


def normalize_standard(std: str) -> str:
    """Normalize standard name for comparison"""
    std_upper = std.upper().replace(' ', '').replace('-', '')
    for key, value in STANDARD_MAPPINGS.items():
        if key.upper().replace(' ', '').replace('-', '') == std_upper:
            return value
    return std


def is_standard_selected(standard_in_template: str, selected_standards: list) -> bool:
    """Check if a standard from template matches any selected standard"""
    template_normalized = standard_in_template.upper().replace(' ', '').replace('-', '')
    
    for selected in selected_standards:
        selected_normalized = selected.upper().replace(' ', '').replace('-', '')
        if template_normalized in selected_normalized or selected_normalized in template_normalized:
            return True
    return False


def fill_grant_agreement_template(agreement_data: dict, output_docx_path: str) -> str:
    """
    Fill the Grant Agreement DOCX template with client data.
    
    Replaces all yellow-highlighted placeholders:
    - Client Organization Name
    - Client Address (XXXXXXXXXXXXXXXXXXX)
    - Standards checkboxes (☐ → ☑)
    - Scope of services
    - Sites (xxxxxxxxxxxxxxxxxxxxxxxxxxxxx)
    - Signatory information
    
    Args:
        agreement_data: Dictionary containing client data
        output_docx_path: Path to save the filled document
    
    Returns:
        Path to generated DOCX
    """
    
    if not TEMPLATE_PATH.exists():
        raise FileNotFoundError(f"Template not found: {TEMPLATE_PATH}")
    
    # Load template
    doc = Document(str(TEMPLATE_PATH))
    
    # Extract client data with fallbacks
    org_name = agreement_data.get('organization_name', '') or ''
    org_address = agreement_data.get('organization_address', '') or ''
    
    # Handle standards
    standards = agreement_data.get('standards', []) or agreement_data.get('selected_standards', []) or []
    if isinstance(standards, str):
        standards = [s.strip() for s in standards.split(',')]
    
    # Handle scope
    scope = agreement_data.get('scope', '') or agreement_data.get('scope_of_services', '') or ''
    
    # Handle sites
    sites = agreement_data.get('sites', []) or []
    if isinstance(sites, list):
        sites_str = ', '.join([str(s) for s in sites]) if sites else ''
    else:
        sites_str = str(sites) if sites else ''
    
    # Signatory info
    client_signatory_name = agreement_data.get('signatory_name', '') or agreement_data.get('contact_name', '') or ''
    client_signatory_position = agreement_data.get('signatory_position', '') or ''
    signatory_date = agreement_data.get('signatory_date', '') or datetime.now().strftime('%Y-%m-%d')
    
    # BAC signatory
    bac_signatory_name = agreement_data.get('issuer_name', '') or 'Abdullah Al-Rashid'
    bac_signatory_position = agreement_data.get('issuer_designation', '') or 'General Manager'
    
    logging.info(f"Filling Grant Agreement for: {org_name}")
    logging.info(f"Standards: {standards}")
    
    # Process all paragraphs
    for i, paragraph in enumerate(doc.paragraphs):
        text = paragraph.text
        
        # === Para 7: Client Organization Name ===
        if 'Client Organization:' in text and text.strip().endswith('.'):
            for run in paragraph.runs:
                if 'Client Organization:' in run.text:
                    run.text = f' Client Organization: {org_name}'
                elif run.text.strip() == '.':
                    run.text = ''
        
        # === Para 8: Client Address (XXXXXXXXXXXXXXXXXXX) ===
        if 'XXXXXXXXXXXXXXXXXXX' in text:
            for run in paragraph.runs:
                if 'XXXXXXXXXXXXXXXXXXX' in run.text:
                    run.text = run.text.replace('XXXXXXXXXXXXXXXXXXX', org_address)
        
        # === Para 12: Standards Checkboxes ===
        if '☐' in text and 'ISO' in text:
            runs = paragraph.runs
            i = 0
            while i < len(runs):
                run = runs[i]
                # If this run contains a checkbox
                if '☐' in run.text:
                    # Look at next runs to find which standard this checkbox is for
                    standard_found = None
                    for j in range(i + 1, min(i + 4, len(runs))):
                        next_text = runs[j].text
                        for std in ['ISO 9001', 'ISO 14001', 'ISO 45001', 'ISO 22000', 'ISO 22301', 'ISO 27001']:
                            if std in next_text:
                                standard_found = std
                                break
                        if standard_found:
                            break
                    
                    # Check if this standard is selected
                    if standard_found and is_standard_selected(standard_found, standards):
                        run.text = run.text.replace('☐', '☑')
                i += 1
        
        # === Para 13: Scope ===
        if 'Scope:' in text and 'Providing senior management' in text:
            # Replace the entire scope content with actual scope
            if scope:
                for run in paragraph.runs:
                    run.text = ''
                if paragraph.runs:
                    paragraph.runs[0].text = f'Scope: {scope}'
        
        # === Para 14: Sites ===
        if 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxx' in text:
            for run in paragraph.runs:
                if 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxx' in run.text:
                    run.text = run.text.replace('xxxxxxxxxxxxxxxxxxxxxxxxxxxxx', sites_str if sites_str else 'As per certification application')
        
        # === Para 95: Client Organization Name + BAC signatory ===
        if 'For Client Organization Name:' in text:
            # This line has both organization name and BAC signatory name
            full_text = ''.join([r.text for r in paragraph.runs])
            
            # Replace "Islam Abd El-Aal" with BAC signatory
            if 'Islam Abd El-Aal' in full_text:
                new_text = full_text.replace('Islam Abd El-Aal', bac_signatory_name)
                # Also update "For Client Organization Name:" to include org name
                new_text = new_text.replace('For Client Organization Name:', f'For Client Organization Name: {org_name}')
                
                # Clear and set new text
                for run in paragraph.runs:
                    run.text = ''
                if paragraph.runs:
                    paragraph.runs[0].text = new_text
        
        # === Para 96: BAC Position ===
        if text.strip() == 'Position: Director':
            for run in paragraph.runs:
                if 'Director' in run.text:
                    run.text = run.text.replace('Director', bac_signatory_position)
        
        # === Para 97: Client Position ===
        if text.strip().startswith('Position:') and text.strip() != 'Position: Director':
            for run in paragraph.runs:
                if 'Position:' in run.text and run.text.strip() == 'Position:':
                    run.text = f'Position: {client_signatory_position}'
        
        # === Para 105: FOR & ON BEHALF OF sections ===
        if 'FOR & ON BEHALF OF' in text and 'xxxxx' in text:
            for run in paragraph.runs:
                if 'xxxxx' in run.text:
                    run.text = run.text.replace('xxxxx', org_name)
                # Also handle "Company" placeholder
                if run.text.strip() == 'Company':
                    run.text = org_name
        
        # === Para 108: Client Signatory Name ===
        if 'Name of Signatory: Eng.' in text:
            for run in paragraph.runs:
                if 'Eng.' in run.text:
                    run.text = run.text.replace('Eng.', client_signatory_name if client_signatory_name else '________________')
    
    # Save filled document
    doc.save(output_docx_path)
    logging.info(f"Filled DOCX saved to: {output_docx_path}")
    
    return output_docx_path


def convert_docx_to_pdf(docx_path: str, output_pdf_path: str) -> str:
    """
    Convert DOCX to PDF using LibreOffice.
    Preserves all formatting, fonts, and layout from the original document.
    
    Args:
        docx_path: Path to input DOCX file
        output_pdf_path: Path for output PDF file
    
    Returns:
        Path to generated PDF
    """
    
    docx_path = Path(docx_path)
    output_pdf_path = Path(output_pdf_path)
    
    if not docx_path.exists():
        raise FileNotFoundError(f"DOCX file not found: {docx_path}")
    
    output_dir = output_pdf_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Run LibreOffice in headless mode for high-quality conversion
        result = subprocess.run([
            'libreoffice',
            '--headless',
            '--convert-to', 'pdf',
            '--outdir', str(output_dir),
            str(docx_path)
        ], capture_output=True, text=True, timeout=120)
        
        if result.returncode != 0:
            logging.error(f"LibreOffice conversion failed: {result.stderr}")
            raise RuntimeError(f"PDF conversion failed: {result.stderr}")
        
        # LibreOffice outputs with the same name but .pdf extension
        generated_pdf = output_dir / f"{docx_path.stem}.pdf"
        
        # Rename to desired output path if different
        if generated_pdf != output_pdf_path:
            if generated_pdf.exists():
                shutil.move(str(generated_pdf), str(output_pdf_path))
            else:
                raise FileNotFoundError(f"Expected PDF not created: {generated_pdf}")
        
        logging.info(f"PDF generated: {output_pdf_path}")
        return str(output_pdf_path)
        
    except subprocess.TimeoutExpired:
        raise RuntimeError("PDF conversion timed out")
    except Exception as e:
        logging.error(f"PDF conversion error: {e}")
        raise


def generate_grant_agreement_pdf(agreement_data: dict, output_path: str) -> str:
    """
    Generate a professional Grant Agreement PDF using the official BAYAN template.
    
    This function:
    1. Loads the official DOCX template with all terms and conditions
    2. Fills yellow-highlighted placeholders with client data
    3. Converts to PDF while preserving all formatting
    
    Args:
        agreement_data: Dictionary containing:
            - organization_name: Client organization name
            - organization_address: Client address
            - standards/selected_standards: List of certification standards
            - scope/scope_of_services: Scope of certification
            - sites: List of site locations
            - signatory_name: Client signatory name
            - signatory_position: Client signatory position
            - issuer_name: BAC signatory name
            - issuer_designation: BAC signatory position
        output_path: Path to save the PDF
    
    Returns:
        Path to generated PDF
    """
    
    output_path = Path(output_path)
    
    # Create temporary DOCX file
    temp_docx = output_path.parent / f"temp_{output_path.stem}.docx"
    
    try:
        # Step 1: Fill the template with client data
        logging.info("Filling Grant Agreement template with client data...")
        fill_grant_agreement_template(agreement_data, str(temp_docx))
        
        # Step 2: Convert to professional PDF
        logging.info("Converting to PDF...")
        convert_docx_to_pdf(str(temp_docx), str(output_path))
        
        return str(output_path)
        
    finally:
        # Cleanup temporary DOCX
        if temp_docx.exists():
            try:
                os.remove(temp_docx)
            except:
                pass


# For testing
if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO)
    
    # Test data matching database structure
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
    
    output_pdf = CONTRACTS_DIR / "test_grant_agreement.pdf"
    
    try:
        result = generate_grant_agreement_pdf(test_data, str(output_pdf))
        print(f"SUCCESS: Generated PDF at {result}")
        print(f"File size: {output_pdf.stat().st_size} bytes")
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
