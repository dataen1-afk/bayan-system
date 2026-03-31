"""
Shared role keys and permission metadata (used by API and DB seeding).
"""


class UserRole:
    SYSTEM_ADMIN = "system_admin"
    CEO = "ceo"
    GENERAL_MANAGER = "general_manager"
    QUALITY_MANAGER = "quality_manager"
    CERTIFICATION_MANAGER = "certification_manager"
    MARKETING_MANAGER = "marketing_manager"
    FINANCIAL_MANAGER = "financial_manager"
    HR_MANAGER = "hr_manager"
    OPERATION_COORDINATOR = "operation_coordinator"
    LEAD_AUDITOR = "lead_auditor"
    AUDITOR = "auditor"
    TECHNICAL_EXPERT = "technical_expert"
    ADMIN = "admin"
    CLIENT = "client"


ROLE_PERMISSIONS = {
    UserRole.SYSTEM_ADMIN: {
        "level": 0,
        "name": "System Administrator",
        "name_ar": "مدير النظام",
        "permissions": [
            "all",
            "system_admin",
            "manage_all_users",
            "delete_users",
            "system_settings",
            "view_logs",
            "manage_roles",
        ],
        "description": "Full system control - add, modify, delete all users and system settings",
    },
    UserRole.CEO: {
        "level": 1,
        "name": "Chief Executive Officer",
        "name_ar": "الرئيس التنفيذي",
        "permissions": ["all"],
        "description": "Overall strategic direction, certification approval, signing certificates",
    },
    UserRole.GENERAL_MANAGER: {
        "level": 2,
        "name": "General Manager",
        "name_ar": "المدير العام",
        "permissions": ["all"],
        "description": "Branch operations, approve certifications, sign agreements",
    },
    UserRole.QUALITY_MANAGER: {
        "level": 3,
        "name": "Quality Manager",
        "name_ar": "مدير الجودة",
        "permissions": [
            "manage_documents",
            "manage_internal_audits",
            "manage_complaints",
            "manage_appeals",
            "technical_review",
            "certification_decisions",
            "view_reports",
            "manage_management_review",
        ],
        "description": "ISO 17021 compliance, document control, internal audits, complaints/appeals",
    },
    UserRole.CERTIFICATION_MANAGER: {
        "level": 3,
        "name": "Certification Manager",
        "name_ar": "مدير الاعتماد",
        "permissions": [
            "manage_auditors",
            "assign_auditors",
            "technical_review",
            "certification_decisions",
            "manage_audit_programs",
            "view_all_audits",
            "manage_contract_reviews",
            "contact_accreditation_bodies",
        ],
        "description": "Auditor qualification, technical review, certification decisions",
    },
    UserRole.OPERATION_COORDINATOR: {
        "level": 4,
        "name": "Operation Coordinator",
        "name_ar": "منسق العمليات",
        "permissions": [
            "schedule_audits",
            "manage_client_files",
            "prepare_job_orders",
            "communicate_customers",
            "update_certified_list",
            "view_audit_reports",
        ],
        "description": "Schedule audits, manage client files, prepare job orders",
    },
    UserRole.MARKETING_MANAGER: {
        "level": 4,
        "name": "Marketing Manager",
        "name_ar": "مدير التسويق",
        "permissions": [
            "manage_marketing",
            "view_customer_feedback",
            "manage_proposals",
            "view_clients",
            "manage_portal_content",
        ],
        "description": "Marketing strategy, business development",
    },
    UserRole.FINANCIAL_MANAGER: {
        "level": 4,
        "name": "Financial Manager",
        "name_ar": "المدير المالي",
        "permissions": [
            "manage_invoices",
            "view_payments",
            "manage_budgets",
            "financial_reports",
            "manage_expenses",
        ],
        "description": "Financial reporting, budgeting, invoicing",
    },
    UserRole.HR_MANAGER: {
        "level": 4,
        "name": "Admin & HR Manager",
        "name_ar": "مدير الموارد البشرية",
        "permissions": [
            "manage_users",
            "manage_staff",
            "manage_training",
            "manage_policies",
            "approve_leaves",
            "view_staff_records",
        ],
        "description": "Staff management, recruitment, training, policy enforcement",
    },
    UserRole.LEAD_AUDITOR: {
        "level": 5,
        "name": "Lead Auditor",
        "name_ar": "المدقق الرئيسي",
        "permissions": [
            "lead_audits",
            "create_audit_reports",
            "evaluate_auditors",
            "recommend_certification",
            "manage_audit_team",
            "follow_up_ca",
        ],
        "description": "Lead audits, recommend certifications, evaluate auditors",
    },
    UserRole.AUDITOR: {
        "level": 6,
        "name": "Auditor",
        "name_ar": "مدقق",
        "permissions": [
            "conduct_audits",
            "submit_audit_findings",
            "view_assigned_audits",
            "create_auditor_notes",
        ],
        "description": "Conduct audits per plan, report findings",
    },
    UserRole.TECHNICAL_EXPERT: {
        "level": 6,
        "name": "Technical Expert",
        "name_ar": "خبير فني",
        "permissions": [
            "provide_technical_expertise",
            "view_assigned_audits",
            "submit_technical_findings",
        ],
        "description": "Provide technical expertise during audits",
    },
    UserRole.ADMIN: {
        "level": 1,
        "name": "Administrator",
        "name_ar": "مدير النظام",
        "permissions": ["all"],
        "description": "Full system access (legacy)",
    },
    UserRole.CLIENT: {
        "level": 10,
        "name": "Client",
        "name_ar": "عميل",
        "permissions": [
            "view_own_data",
            "submit_applications",
            "view_proposals",
            "sign_agreements",
            "submit_feedback",
            "view_certificates",
        ],
        "description": "External customer access",
    },
}
