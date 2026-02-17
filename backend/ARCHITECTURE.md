# Backend Architecture & Refactoring Guide

## Current State (February 2026)

The backend consists of a monolithic `server.py` file (~8,152 lines) containing all:
- Pydantic models
- API endpoints
- Business logic
- Database operations

### Current File Structure
```
/app/backend/
├── server.py                 # MONOLITH - All API logic (~8,152 lines)
├── database.py               # NEW - DB configuration (extracted)
├── auth.py                   # NEW - Auth utilities (extracted)
│
├── models/                   # NEW - Pydantic models (extracted)
│   ├── __init__.py
│   ├── user.py
│   ├── application_form.py
│   ├── proposal.py
│   ├── agreement.py
│   ├── contract_review.py
│   ├── job_order.py
│   ├── audit_plan.py
│   ├── meeting.py
│   ├── audit_report.py
│   ├── certificate.py
│   ├── auditor.py
│   ├── invoice.py
│   ├── notification.py
│   ├── template.py
│   ├── document.py
│   ├── site.py
│   ├── audit_schedule.py
│   └── contact.py
│
├── routes/                   # NEW - API routes (extracted)
│   ├── __init__.py
│   ├── auth.py
│   ├── notifications.py
│   ├── auditors.py
│   ├── certificates.py
│   ├── public_verify.py
│   ├── templates.py
│   ├── documents.py
│   ├── sites.py
│   └── contacts.py
│
├── utils/
│   └── email.py              # NEW - Email utilities
│
├── fonts/                    # Arabic fonts for PDF generation
│   ├── Amiri-Bold.ttf
│   └── Amiri-Regular.ttf
│
├── assets/                   # Static assets
│   ├── bayan-logo.png
│   ├── bayan-signature.png
│   ├── bayan-stamp.png
│   └── company-seal.png
│
└── PDF Generators (at root level):
    ├── audit_calculator.py
    ├── audit_program_generator.py
    ├── bilingual_pdf_generator.py
    ├── certificate_generator.py
    ├── contract_review_generator.py
    ├── grant_agreement_generator.py
    ├── job_order_generator.py
    ├── opening_closing_meeting_generator.py
    ├── pdf_generator.py
    ├── stage1_audit_plan_generator.py
    ├── stage1_audit_report_generator.py
    ├── stage2_audit_plan_generator.py
    └── stage2_audit_report_generator.py
```

## Modular Structure Created

The following modules have been extracted and are ready for use:

### Models (`/app/backend/models/`)
All Pydantic models have been extracted into domain-specific files:
- `user.py` - User, UserLogin, UserRegister, TokenResponse
- `application_form.py` - ApplicationForm, ApplicationFormData, ClientInfo
- `proposal.py` - Proposal, ProposalCreate, AuditDuration, ServiceFees
- `agreement.py` - CertificationAgreement, AgreementAcknowledgements
- `contract_review.py` - ContractReview, AuditProgram, AuditActivityEntry
- `job_order.py` - JobOrder, JobOrderCreate, JobOrderUpdate
- `audit_plan.py` - Stage1AuditPlan, Stage2AuditPlan, ScheduleEntry, TeamMember
- `meeting.py` - OpeningClosingMeeting, MeetingAttendee
- `audit_report.py` - Stage1AuditReport, Stage2AuditReport, AuditFinding, Nonconformity
- `certificate.py` - Certificate, CertificateCreate
- `auditor.py` - Auditor, AuditorCreate, AuditAssignment
- `invoice.py` - Invoice, InvoiceItem, PaymentRecord
- `notification.py` - Notification, NotificationCreate
- `template.py` - CertificationPackage, ProposalTemplate
- `document.py` - Document, DocumentCreate
- `site.py` - Site, SiteCreate
- `audit_schedule.py` - AuditSchedule, AuditScheduleCreate
- `contact.py` - ContactRecord, ContactRecordCreate

### Routes (`/app/backend/routes/`)
Extracted route modules (ready for integration):
- `auth.py` - /api/auth/* endpoints
- `notifications.py` - /api/notifications/* endpoints
- `auditors.py` - /api/auditors/* endpoints
- `certificates.py` - /api/certificates/* endpoints
- `public_verify.py` - /api/public/verify/* endpoint
- `templates.py` - /api/templates/* endpoints
- `documents.py` - /api/documents/* endpoints
- `sites.py` - /api/sites/* endpoints
- `contacts.py` - /api/contacts/* endpoints

### Shared Utilities
- `database.py` - MongoDB connection and configuration
- `auth.py` - JWT and password utilities
- `utils/email.py` - Email sending functions

## Migration Plan

### Phase 1: Low-Risk Routes (COMPLETED)
The following routes have been extracted and can be tested independently:
- Authentication (auth.py)
- Notifications (notifications.py)
- Auditors (auditors.py)
- Certificates (certificates.py)
- Templates (templates.py)
- Documents (documents.py)
- Sites (sites.py)
- Contacts (contacts.py)

### Phase 2: Core Workflow Routes (TODO)
Extract these complex routes with careful testing:
1. Application Forms (forms, public forms)
2. Proposals (proposals, public proposals)
3. Agreements (certification agreements, PDF generation)
4. Contract Reviews (BACF6-04)
5. Audit Programs (BACF6-05)
6. Job Orders (BACF6-06)
7. Audit Plans (BACF6-07, BACF6-08)
8. Meetings (BACF6-09)
9. Audit Reports (BACF6-10, BACF6-11)

### Phase 3: Reports & Analytics (TODO)
- Reports routes
- Analytics dashboard
- Export functionality

### Phase 4: Integration Routes (TODO)
- Google Calendar
- SMS notifications
- Invoices

## How to Complete the Migration

1. **Test each new route module** before replacing in server.py
2. **Comment out** the corresponding section in server.py
3. **Import the new router** and include it in the api_router
4. **Run full test suite** after each migration step
5. **Keep server.py as backup** until all routes are migrated

## Example: Adding a New Route Module

```python
# In server.py, after line 56 (api_router definition):

# Import new route modules
from routes.auth import router as auth_router
from routes.notifications import router as notifications_router

# Include routers (after api_router definition)
api_router.include_router(auth_router)
api_router.include_router(notifications_router)

# Then comment out the corresponding routes in server.py
```

## Benefits of Modular Architecture

1. **Maintainability**: Each domain has its own file
2. **Testing**: Routes can be tested in isolation
3. **Team Collaboration**: Different developers can work on different modules
4. **Code Navigation**: Easier to find and modify specific functionality
5. **Reduced Risk**: Changes to one module don't affect others
6. **Faster Development**: New features can be added as new modules

## Notes

- The existing `server.py` remains fully functional
- New route modules are tested and ready for gradual integration
- All Pydantic models have been extracted to `/models/`
- Shared utilities are in `database.py`, `auth.py`, and `utils/`
