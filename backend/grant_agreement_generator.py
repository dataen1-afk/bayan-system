"""
Grant Agreement Generator
Uses the official BAYAN DOCX template to generate professional Grant Agreement PDFs
Fills the template with client data and converts to PDF using LibreOffice
"""

from docx import Document
from docx.shared import Pt, Inches
from pathlib import Path
import subprocess
import shutil
import os
import logging
import tempfile
import base64
from io import BytesIO
from datetime import datetime
import re

ROOT_DIR = Path(__file__).parent
ASSETS_DIR = ROOT_DIR / "assets"
TEMPLATE_PATH = ASSETS_DIR / "grant_agreement_template.docx"
CONTRACTS_DIR = ROOT_DIR / "contracts"

# Ensure contracts directory exists
CONTRACTS_DIR.mkdir(exist_ok=True)


def normalize_standard(std):
    """Normalize standard name for comparison"""
    # Remove spaces and convert to uppercase
    normalized = std.upper().replace(' ', '').replace('-', '')
    return normalized


def standards_match(template_std, selected_standards):
    """Check if a template standard matches any selected standard"""
    normalized_template = normalize_standard(template_std)
    for selected in selected_standards:
        if normalize_standard(selected) == normalized_template:
            return True
    return False


def fill_docx_template(agreement_data: dict, output_docx_path: str) -> str:
    """
    Fill the DOCX template with agreement data
    
    Args:
        agreement_data: Dictionary containing:
            - organization_name: Client organization name
            - organization_address: Client address
            - standards/selected_standards: List of selected standards
            - scope/scope_of_services: Scope of services
            - sites: Site locations (list or string)
            - signatory_name: Client signatory name
            - signatory_position: Client signatory position
            - signatory_date: Date of signing
            - issuer_name: BAC signatory name
            - issuer_designation: BAC signatory position
        output_docx_path: Path to save the filled document
    
    Returns:
        Path to generated DOCX
    """
    
    if not TEMPLATE_PATH.exists():
        raise FileNotFoundError(f"Template not found: {TEMPLATE_PATH}")
    
    # Load template
    doc = Document(str(TEMPLATE_PATH))
    
    # Extract data with fallbacks
    org_name = agreement_data.get('organization_name', '') or agreement_data.get('organizationName', '') or ''
    org_address = agreement_data.get('organization_address', '') or agreement_data.get('organizationAddress', '') or ''
    
    # Handle standards - could be 'standards' or 'selected_standards'
    standards = agreement_data.get('standards', []) or agreement_data.get('selected_standards', []) or []
    if isinstance(standards, str):
        standards = [s.strip() for s in standards.split(',')]
    
    # Handle scope
    scope = agreement_data.get('scope', '') or agreement_data.get('scope_of_services', '') or ''
    
    # Handle sites
    sites = agreement_data.get('sites', []) or []
    if isinstance(sites, list):
        sites_str = ', '.join([str(s) for s in sites]) if sites else 'As per application'
    else:
        sites_str = str(sites) if sites else 'As per application'
    
    signatory_name = agreement_data.get('signatory_name', '') or agreement_data.get('contact_name', '') or ''
    signatory_position = agreement_data.get('signatory_position', '') or ''
    signatory_date = agreement_data.get('signatory_date', '') or datetime.now().strftime('%Y-%m-%d')
    issuer_name = agreement_data.get('issuer_name', 'Abdullah Al-Rashid')
    issuer_designation = agreement_data.get('issuer_designation', 'General Manager')
    
    logging.info(f"Filling template for: {org_name}")
    logging.info(f"Standards: {standards}")
    logging.info(f"Scope: {scope[:50]}..." if scope else "No scope")
    
    # Process all paragraphs
    for i, paragraph in enumerate(doc.paragraphs):
        text = paragraph.text
        
        # === Replace Client Organization name ===
        if 'Client Organization:' in text:
            # Find and update the client organization line
            for run in paragraph.runs:
                if 'Client Organization:' in run.text:
                    run.text = run.text.replace('Client Organization:', f'Client Organization: {org_name}')
                    # Remove trailing placeholder dots if any
                    run.text = run.text.replace('  .', '')
        
        # === Replace address placeholder ===
        if 'XXXXXXXXXXXXXXXXXXX' in text:
            for run in paragraph.runs:
                if 'XXXXXXXXXXXXXXXXXXX' in run.text:
                    run.text = run.text.replace('XXXXXXXXXXXXXXXXXXX', org_address)
        
        # === Handle Standards checkboxes (Para 12) ===
        # The checkboxes are in separate runs - we need to replace ☐ with ☑ for selected standards
        if '☐' in text and 'ISO' in text:
            runs = paragraph.runs
            for r_idx in range(len(runs)):
                run_text = runs[r_idx].text
                
                # If this run is a checkbox, check if the NEXT run contains a selected standard
                if '☐' in run_text:
                    # Look ahead to find which standard this checkbox is for
                    for next_idx in range(r_idx + 1, min(r_idx + 3, len(runs))):
                        next_text = runs[next_idx].text.strip()
                        if next_text:
                            # Check if any part of the next text matches a standard
                            for std in ['ISO 9001', 'ISO9001', 'ISO 14001', 'ISO14001', 
                                       'ISO 45001', 'ISO45001', 'ISO 22000', 'ISO22000', 
                                       'ISO 22301', 'ISO22301', 'ISO 27001', 'ISO27001']:
                                if std.replace(' ', '') in next_text.replace(' ', ''):
                                    # Check if this standard is selected
                                    if standards_match(std, standards):
                                        runs[r_idx].text = runs[r_idx].text.replace('☐', '☑')
                                    break
                            break
        
        # === Replace Scope ===
        if text.startswith('Scope:') and 'Providing senior management' in text:
            # Clear all runs and set new scope
            for run in paragraph.runs:
                run.text = ''
            if paragraph.runs:
                paragraph.runs[0].text = f'Scope: {scope}' if scope else 'Scope: As per certification application'
        
        # === Replace Sites ===
        if 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxx' in text:
            for run in paragraph.runs:
                if 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxx' in run.text:
                    run.text = run.text.replace('xxxxxxxxxxxxxxxxxxxxxxxxxxxxx', sites_str)
        
        # === Replace in signature section ===
        # Replace "xxxxx" with organization name
        if 'xxxxx' in text.lower():
            for run in paragraph.runs:
                if 'xxxxx' in run.text.lower():
                    run.text = run.text.replace('xxxxx', org_name)
                    run.text = run.text.replace('XXXXX', org_name)
        
        # Replace BAC signatory name
        if 'Islam Abd El-Aal' in text:
            for run in paragraph.runs:
                if 'Islam Abd El-Aal' in run.text:
                    run.text = run.text.replace('Islam Abd El-Aal', issuer_name)
        
        # Replace "Company  ." with actual company name
        if 'Company  .' in text:
            for run in paragraph.runs:
                if 'Company  .' in run.text:
                    run.text = run.text.replace('Company  .', org_name)
        
        # Handle client signatory name in signature section
        if 'Name of Signatory' in text and ('Eng.' in text or 'Designation:' in text):
            for run in paragraph.runs:
                if 'Eng.' in run.text:
                    run.text = run.text.replace('Eng.', signatory_name or '________________')
    
    # Process tables if any exist
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    text = paragraph.text
                    
                    if 'XXXXXXXXXXXXXXXXXXX' in text:
                        for run in paragraph.runs:
                            if 'XXXXXXXXXXXXXXXXXXX' in run.text:
                                run.text = run.text.replace('XXXXXXXXXXXXXXXXXXX', org_address)
                    
                    if 'xxxxx' in text.lower():
                        for run in paragraph.runs:
                            run.text = run.text.replace('xxxxx', org_name)
                            run.text = run.text.replace('XXXXX', org_name)
    
    # Save filled document
    doc.save(output_docx_path)
    logging.info(f"Filled DOCX saved to: {output_docx_path}")
    
    return output_docx_path


def convert_docx_to_pdf(docx_path: str, output_pdf_path: str) -> str:
    """
    Convert DOCX to PDF using LibreOffice
    
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
    
    # Use LibreOffice to convert
    output_dir = output_pdf_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Run LibreOffice in headless mode
        result = subprocess.run([
            'libreoffice',
            '--headless',
            '--convert-to', 'pdf',
            '--outdir', str(output_dir),
            str(docx_path)
        ], capture_output=True, text=True, timeout=60)
        
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
                # Check if file was created with expected name
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
    Generate a Grant Agreement PDF using the official BAYAN template
    
    This function:
    1. Fills the DOCX template with client data
    2. Converts the filled DOCX to PDF using LibreOffice
    
    Args:
        agreement_data: Dictionary containing agreement information
        output_path: Path to save the PDF
    
    Returns:
        Path to generated PDF
    """
    
    output_path = Path(output_path)
    
    # Create temporary DOCX file
    temp_docx = output_path.parent / f"temp_{output_path.stem}.docx"
    
    try:
        # Step 1: Fill the template
        logging.info("Filling DOCX template...")
        fill_docx_template(agreement_data, str(temp_docx))
        
        # Step 2: Convert to PDF
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


def generate_grant_agreement_docx(agreement_data: dict, output_path: str) -> str:
    """
    Generate only the filled DOCX (without PDF conversion)
    Useful for debugging or when PDF is not needed
    
    Args:
        agreement_data: Dictionary containing agreement information
        output_path: Path to save the DOCX
    
    Returns:
        Path to generated DOCX
    """
    
    return fill_docx_template(agreement_data, output_path)


# For testing
if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO)
    
    # Test data matching actual database structure
    test_data = {
        "organization_name": "Test Company Ltd",
        "organization_address": "123 Test Street, Riyadh, Saudi Arabia",
        "selected_standards": ["ISO9001", "ISO14001"],  # Without spaces to test matching
        "scope_of_services": "Manufacturing and distribution of electronic components",
        "sites": ["Main Office - Riyadh", "Factory - Jeddah"],
        "signatory_name": "Mohammed Al-Test",
        "signatory_position": "CEO",
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
