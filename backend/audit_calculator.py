"""
Audit Time Calculation Module
Based on IAF MD guidelines for certification audit duration
"""

from typing import Dict, List, Optional, Tuple
from enum import Enum

class RiskCategory(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    LIMITED = "limited"

class FoodSafetyCategory(str, Enum):
    AI = "AI"
    AII = "AII"
    BI = "BI"
    BII = "BII"
    BIII = "BIII"
    CO = "CO"
    CI = "CI"
    CII = "CII"
    CIII = "CIII"
    CIV = "CIV"
    D = "D"
    E = "E"
    FI = "FI"
    FII = "FII"
    G = "G"
    H = "H"
    I = "I"
    J = "J"
    K = "K"

# ISO 9001:2015 Audit Time Table (Man-Days by Employee Count)
ISO_9001_TABLE = [
    (1, 5, 1.5),
    (6, 10, 2),
    (11, 15, 2.5),
    (16, 25, 3),
    (26, 45, 4),
    (46, 65, 5),
    (66, 85, 6),
    (86, 125, 7),
    (126, 175, 8),
    (176, 275, 9),
    (276, 425, 10),
    (426, 625, 11),
    (626, 875, 12),
    (876, 1175, 13),
    (1176, 1550, 14),
    (1551, 2025, 15),
    (2026, 2675, 16),
    (2676, 3450, 17),
    (3451, 4350, 18),
    (4351, 5450, 19),
    (5451, 6800, 20),
    (6801, 8500, 21),
    (8501, 10700, 22),
]

# ISO 14001:2015 & ISO 45001:2018 Table (with Risk Category)
# Format: (from, to, high, medium, low, limited)
ISO_14001_45001_TABLE = [
    (1, 5, 3, 2.5, 2.5, 2.5),
    (6, 10, 3.5, 3, 3, 3),
    (11, 15, 4.5, 3.5, 3, 3),
    (16, 25, 5.5, 4.5, 3.5, 3),
    (26, 45, 7, 5.5, 4, 3),
    (46, 65, 8, 6, 4.5, 3.5),
    (66, 85, 9, 7, 5, 3.5),
    (86, 125, 11, 8, 5.5, 4),
    (126, 175, 12, 9, 6, 4.5),
    (176, 275, 13, 10, 7, 5),
    (276, 425, 15, 11, 8, 5.5),
    (426, 625, 16, 12, 9, 6),
    (626, 875, 17, 13, 10, 6.5),
    (876, 1175, 19, 15, 11, 7),
    (1176, 1550, 20, 16, 12, 7.5),
    (1551, 2025, 21, 17, 12, 8),
    (2026, 2675, 23, 18, 13, 8.5),
    (2676, 3450, 25, 19, 14, 9),
    (3451, 4350, 27, 20, 15, 10),
    (4351, 5450, 28, 21, 16, 11),
    (5451, 6800, 30, 23, 17, 12),
    (6801, 8500, 32, 25, 19, 13),
    (8501, 10700, 34, 27, 20, 14),
]

# ISO 22000:2018 Food Safety Table
# Format: (category, base_duration, haccp_factor)
ISO_22000_CATEGORIES = {
    "AI": (1, 0.25),
    "AII": (1, 0.25),
    "BI": (1, 0.25),
    "BII": (1, 0.25),
    "BIII": (1, 0.25),
    "CO": (2, 0.5),
    "CI": (2, 0.5),
    "CII": (2, 0.5),
    "CIII": (2, 0.5),
    "CIV": (2, 0.5),
    "D": (1, 0.5),
    "E": (1.5, 0.5),
    "FI": (1, 0.5),
    "FII": (1, 0.5),
    "G": (1.5, 0.25),
    "H": (1.5, 0.25),
    "I": (1.5, 0.5),
    "J": (1.5, 0.5),
    "K": (2, 0.5),
}

# ISO 22000 Employee Duration Table
ISO_22000_EMPLOYEE_TABLE = [
    (1, 5, 0),
    (6, 49, 0.5),
    (50, 99, 1),
    (100, 199, 1.5),
    (200, 499, 2),
    (500, 999, 2.5),
    (1000, 9999, 3),
]

# ISO 13485:2016 Medical Devices Table
# Format: (from, to, duration, integration_duration)
ISO_13485_TABLE = [
    (1, 5, 3, 2.75),
    (6, 10, 4, 3),
    (11, 15, 4.5, 3.5),
    (16, 25, 5, 4),
    (26, 45, 6, 5),
    (46, 65, 7, 6),
    (66, 85, 8, 7),
    (86, 125, 10, 8.5),
    (126, 175, 11, 9.5),
    (176, 275, 12, 10),
    (276, 425, 13, 11),
    (426, 625, 14, 12),
    (626, 875, 15, 13),
]

# ISO/IEC 20000-1:2018 Table
ISO_20000_TABLE = [
    (1, 15, 3.5),
    (16, 25, 4.5),
    (26, 45, 5.5),
    (46, 65, 6),
    (66, 85, 7),
    (86, 125, 8),
    (126, 175, 9),
    (176, 275, 10),
    (276, 425, 11),
    (426, 625, 12),
    (626, 875, 13),
    (876, 1175, 15),
]

# ISO 22301:2019, ISO 27001:2022, ISO 21001:2018 use same table as ISO 9001
ISO_22301_TABLE = ISO_9001_TABLE
ISO_27001_TABLE = ISO_9001_TABLE
ISO_21001_TABLE = ISO_9001_TABLE


def get_man_days_from_table(employees: int, table: List[Tuple]) -> float:
    """Lookup man-days from a simple employee range table"""
    for row in table:
        if row[0] <= employees <= row[1]:
            return row[2]
    # If above max, return max value
    return table[-1][2]


def get_man_days_with_risk(employees: int, risk: str, table: List[Tuple]) -> float:
    """Lookup man-days with risk category"""
    risk_index = {
        "high": 2,
        "medium": 3,
        "low": 4,
        "limited": 5
    }
    idx = risk_index.get(risk.lower(), 3)  # Default to medium
    
    for row in table:
        if row[0] <= employees <= row[1]:
            return row[idx]
    return table[-1][idx]


def calculate_iso_9001(employees: int) -> float:
    """Calculate audit time for ISO 9001:2015"""
    return get_man_days_from_table(employees, ISO_9001_TABLE)


def calculate_iso_14001(employees: int, risk: str = "medium") -> float:
    """Calculate audit time for ISO 14001:2015"""
    return get_man_days_with_risk(employees, risk, ISO_14001_45001_TABLE)


def calculate_iso_45001(employees: int, risk: str = "medium") -> float:
    """Calculate audit time for ISO 45001:2018"""
    return get_man_days_with_risk(employees, risk, ISO_14001_45001_TABLE)


def calculate_iso_22000(category: str, employees: int, haccp_studies: int = 1) -> float:
    """Calculate audit time for ISO 22000:2018"""
    if category not in ISO_22000_CATEGORIES:
        category = "AI"  # Default
    
    base_duration, haccp_factor = ISO_22000_CATEGORIES[category]
    
    # Get employee duration
    employee_duration = 0
    for row in ISO_22000_EMPLOYEE_TABLE:
        if row[0] <= employees <= row[1]:
            employee_duration = row[2]
            break
    
    # Total = base + (haccp_factor * haccp_studies) + employee_duration
    return base_duration + (haccp_factor * haccp_studies) + employee_duration


def calculate_iso_13485(employees: int, integrated_with_9001: bool = False) -> float:
    """Calculate audit time for ISO 13485:2016"""
    for row in ISO_13485_TABLE:
        if row[0] <= employees <= row[1]:
            return row[3] if integrated_with_9001 else row[2]
    return ISO_13485_TABLE[-1][2]


def calculate_iso_22301(employees: int) -> float:
    """Calculate audit time for ISO 22301:2019"""
    return get_man_days_from_table(employees, ISO_22301_TABLE)


def calculate_iso_27001(employees: int) -> float:
    """Calculate audit time for ISO 27001:2022"""
    return get_man_days_from_table(employees, ISO_27001_TABLE)


def calculate_iso_20000(employees: int) -> float:
    """Calculate audit time for ISO/IEC 20000-1:2018"""
    return get_man_days_from_table(employees, ISO_20000_TABLE)


def calculate_iso_21001(employees: int) -> float:
    """Calculate audit time for ISO 21001:2018"""
    return get_man_days_from_table(employees, ISO_21001_TABLE)


def calculate_audit_phases(total_md: float) -> Dict[str, float]:
    """
    Break down total man-days into audit phases.
    Based on IAF guidelines:
    - Stage 1: ~30% of total
    - Stage 2: ~70% of total (or remaining)
    - Surveillance: ~33% of initial (Stage 1 + Stage 2)
    - Recertification: ~67% of initial
    """
    return {
        "stage_1": round(total_md * 0.3, 2),
        "stage_2": round(total_md * 0.7, 2),
        "surveillance": round(total_md * 0.33, 2),
        "recertification": round(total_md * 0.67, 2)
    }


def calculate_total_audit_time(
    certifications: List[str],
    employees: int,
    risk_category: str = "medium",
    food_safety_category: str = None,
    haccp_studies: int = 1,
    integrated_with_9001: bool = False
) -> Dict:
    """
    Calculate total audit time for selected certifications.
    
    Args:
        certifications: List of ISO standards (e.g., ["ISO9001", "ISO14001"])
        employees: Number of effective employees
        risk_category: For ISO 14001/45001 - high, medium, low, limited
        food_safety_category: For ISO 22000 - AI, AII, BI, etc.
        haccp_studies: Number of HACCP studies for ISO 22000
        integrated_with_9001: For ISO 13485 integration discount
    
    Returns:
        Dictionary with detailed calculation results
    """
    results = {
        "certifications": {},
        "total_md": 0,
        "phases": {},
        "reduction": 0,
        "final_total_md": 0
    }
    
    calculation_map = {
        "ISO9001": lambda: calculate_iso_9001(employees),
        "ISO14001": lambda: calculate_iso_14001(employees, risk_category),
        "ISO45001": lambda: calculate_iso_45001(employees, risk_category),
        "ISO22000": lambda: calculate_iso_22000(food_safety_category or "AI", employees, haccp_studies),
        "ISO13485": lambda: calculate_iso_13485(employees, integrated_with_9001),
        "ISO22301": lambda: calculate_iso_22301(employees),
        "ISO27001": lambda: calculate_iso_27001(employees),
        "ISO20000": lambda: calculate_iso_20000(employees),
        "ISO21001": lambda: calculate_iso_21001(employees),
    }
    
    total = 0
    for cert in certifications:
        # Normalize certification name
        cert_key = cert.replace(":", "").replace("-", "").replace(" ", "").upper()
        cert_key = cert_key.replace("ISO", "ISO").replace("IEC", "")
        
        # Map common variations
        cert_mapping = {
            "ISO9001": "ISO9001",
            "ISO90012015": "ISO9001",
            "ISO14001": "ISO14001",
            "ISO140012015": "ISO14001",
            "ISO45001": "ISO45001",
            "ISO450012018": "ISO45001",
            "ISO22000": "ISO22000",
            "ISO220002018": "ISO22000",
            "ISO13485": "ISO13485",
            "ISO134852016": "ISO13485",
            "ISO22301": "ISO22301",
            "ISO223012019": "ISO22301",
            "ISO27001": "ISO27001",
            "ISO270012022": "ISO27001",
            "ISO200001": "ISO20000",
            "ISO2000012018": "ISO20000",
            "ISO21001": "ISO21001",
            "ISO210012018": "ISO21001",
        }
        
        normalized = cert_mapping.get(cert_key, cert_key)
        
        if normalized in calculation_map:
            md = calculation_map[normalized]()
            results["certifications"][cert] = {
                "man_days": md,
                "phases": calculate_audit_phases(md)
            }
            total += md
    
    # Apply integration reduction for multiple certifications (typically 10-20%)
    reduction = 0
    if len(certifications) > 1:
        reduction = round(total * 0.15, 2)  # 15% reduction for integrated audits
    
    results["total_md"] = round(total, 2)
    results["reduction"] = reduction
    results["final_total_md"] = round(total - reduction, 2)
    results["phases"] = calculate_audit_phases(results["final_total_md"])
    
    return results


# Example usage
if __name__ == "__main__":
    # Test calculation
    result = calculate_total_audit_time(
        certifications=["ISO9001", "ISO14001"],
        employees=50,
        risk_category="medium"
    )
    print("Calculation Result:")
    print(f"Total MD: {result['total_md']}")
    print(f"Reduction: {result['reduction']}")
    print(f"Final Total: {result['final_total_md']}")
    print(f"Phases: {result['phases']}")
    for cert, data in result['certifications'].items():
        print(f"\n{cert}:")
        print(f"  Man-Days: {data['man_days']}")
        print(f"  Phases: {data['phases']}")
