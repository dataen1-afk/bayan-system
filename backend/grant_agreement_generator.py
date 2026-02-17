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

ROOT_DIR = Path(__file__).parent
ASSETS_DIR = ROOT_DIR / "assets"
TEMPLATE_PATH = ASSETS_DIR / "grant_agreement_template.docx"
CONTRACTS_DIR = ROOT_DIR / "contracts"

# Ensure contracts directory exists
CONTRACTS_DIR.mkdir(exist_ok=True)


def add_image_to_paragraph(paragraph, image_data: str, width_inches: float = 1.5):
    """Add an image from base64 data to a paragraph"""
    try:
        # Remove data URL prefix if present
        if 'base64,' in image_data:
            image_data = image_data.split('base64,')[1]
        
        # Decode base64
        image_bytes = base64.b64decode(image_data)
        image_stream = BytesIO(image_bytes)
        
        # Add image to paragraph
        run = paragraph.add_run()
        run.add_picture(image_stream, width=Inches(width_inches))
        return True
    except Exception as e:
        logging.error(f"Failed to add image: {e}")
        return False


def replace_text_in_paragraph(paragraph, old_text: str, new_text: str):
    """Replace text in a paragraph while preserving formatting"""
    if old_text not in paragraph.text:
        return False
    
    # Simple replacement for plain text
    for run in paragraph.runs:
        if old_text in run.text:
            run.text = run.text.replace(old_text, new_text)
            return True
    
    # If runs don't contain the text directly, try full paragraph replacement
    if old_text in paragraph.text:
        # Get the full text and replace
        full_text = paragraph.text
        new_full_text = full_text.replace(old_text, new_text)
        
        # Clear existing runs and add new text
        for run in paragraph.runs:
            run.text = ""
        if paragraph.runs:
            paragraph.runs[0].text = new_full_text
        else:
            paragraph.add_run(new_full_text)
        return True
    
    return False


def fill_docx_template(agreement_data: dict, output_docx_path: str) -> str:
    """
    Fill the DOCX template with agreement data
    
    Args:
        agreement_data: Dictionary containing:
            - organization_name: Client organization name
            - organization_address: Client address
            - standards: List of selected standards
            - scope: Scope of services
            - sites: Site locations
            - signatory_name: Client signatory name
            - signatory_position: Client signatory position
            - signatory_date: Date of signing
            - signature_image: Base64 encoded signature image
            - stamp_image: Base64 encoded stamp image
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
    standards = agreement_data.get('standards', []) or agreement_data.get('selected_standards', []) or []
    scope = agreement_data.get('scope', '') or agreement_data.get('scope_of_services', '') or ''
    sites = agreement_data.get('sites', []) or []
    signatory_name = agreement_data.get('signatory_name', '') or agreement_data.get('contact_name', '') or ''
    signatory_position = agreement_data.get('signatory_position', '') or ''
    signatory_date = agreement_data.get('signatory_date', '') or datetime.now().strftime('%Y-%m-%d')
    issuer_name = agreement_data.get('issuer_name', 'Abdullah Al-Rashid')
    issuer_designation = agreement_data.get('issuer_designation', 'General Manager')
    
    # Format sites as string
    sites_str = ', '.join(sites) if isinstance(sites, list) else str(sites)
    
    # Format standards as string  
    standards_str = ', '.join(standards) if isinstance(standards, list) else str(standards)
    
    # Process all paragraphs
    for paragraph in doc.paragraphs:
        text = paragraph.text
        
        # Replace Client Organization name placeholder
        if 'Client Organization:' in text and text.strip().endswith('.'):
            # This is the organization name line
            replace_text_in_paragraph(paragraph, 'Client Organization:', f'Client Organization: {org_name}')
        elif 'Client Organization Name:' in text:
            replace_text_in_paragraph(paragraph, 'Client Organization Name:', f'Client Organization Name: {org_name}')
        
        # Replace address placeholder
        if 'XXXXXXXXXXXXXXXXXXX' in text:
            replace_text_in_paragraph(paragraph, 'XXXXXXXXXXXXXXXXXXX', org_address)
        
        # Replace sites placeholder
        if 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxx' in text:
            replace_text_in_paragraph(paragraph, 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxx', sites_str if sites_str else 'As per application')
        
        # Replace scope - look for the example scope text
        if 'Scope: Providing senior management' in text:
            # Replace the entire scope line with actual scope
            new_scope_text = f"Scope: {scope}" if scope else "Scope: As per certification application"
            for run in paragraph.runs:
                run.text = ""
            if paragraph.runs:
                paragraph.runs[0].text = new_scope_text
            else:
                paragraph.add_run(new_scope_text)
        
        # Replace in signature section - organization name placeholder
        if 'xxxxx' in text.lower():
            replace_text_in_paragraph(paragraph, 'xxxxx', org_name)
            replace_text_in_paragraph(paragraph, 'XXXXX', org_name)
        
        # Replace BAC signatory name
        if 'Islam Abd El-Aal' in text:
            replace_text_in_paragraph(paragraph, 'Islam Abd El-Aal', issuer_name)
        
        # Replace "Company  ." with actual company name
        if 'Company  .' in text:
            replace_text_in_paragraph(paragraph, 'Company  .', f'{org_name}')
        
        # Handle signatory name fields
        if 'Name of Signatory:' in text and 'Eng.' in text:
            # This is the client signatory line
            replace_text_in_paragraph(paragraph, 'Name of Signatory: Eng.', f'Name of Signatory: {signatory_name}')
    
    # Process tables if any
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    text = paragraph.text
                    
                    if 'XXXXXXXXXXXXXXXXXXX' in text:
                        replace_text_in_paragraph(paragraph, 'XXXXXXXXXXXXXXXXXXX', org_address)
                    if 'xxxxx' in text.lower():
                        replace_text_in_paragraph(paragraph, 'xxxxx', org_name)
                        replace_text_in_paragraph(paragraph, 'XXXXX', org_name)
    
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
    # Test data
    test_data = {
        "organization_name": "Test Company Ltd",
        "organization_address": "123 Test Street, Riyadh, Saudi Arabia",
        "standards": ["ISO 9001", "ISO 14001"],
        "scope": "Manufacturing and distribution of electronic components",
        "sites": ["Main Office - Riyadh", "Factory - Jeddah"],
        "signatory_name": "Mohammed Al-Test",
        "signatory_position": "CEO",
        "signatory_date": "2025-02-17",
        "issuer_name": "Abdullah Al-Rashid",
        "issuer_designation": "General Manager"
    }
    
    output_pdf = CONTRACTS_DIR / "test_grant_agreement.pdf"
    result = generate_grant_agreement_pdf(test_data, str(output_pdf))
    print(f"Generated: {result}")
