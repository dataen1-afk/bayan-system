# Service Contract Management System - PRD

## Original Problem Statement
Build a full-stack application for managing service contracts for Bayan Auditing & Conformity with the following workflow:
1. Admin creates a form by entering client information (name, company, email, phone)
2. System generates a unique public link for the form
3. Admin shares the link with the client (via email, WhatsApp, etc.)
4. Client fills out the form via the public link (NO LOGIN REQUIRED)
5. Client submits the form - system auto-calculates audit duration
6. Admin reviews the submission and creates a price quote/proposal
7. Client can approve or reject the proposal
8. **If approved**: Client fills the Certification Agreement form
9. Agreement submission finalizes the contract

## User Personas
- **Admin**: Creates forms, manages quotations, and oversees contracts
- **Client**: Fills forms via public links (no system account needed)

## Core Requirements
- **User Roles**: Admin only has system access; Clients access forms via public links
- **Authentication**: Admin-only JWT authentication
- **UI/UX**: Professional, branded interface matching "Bayan Auditing & Conformity" logo
- **Multi-language Support**: English and Arabic with RTL layout for Arabic
- **Public Form Access**: Clients can fill forms without logging in

## Tech Stack
- **Backend**: FastAPI (Python), Motor (async MongoDB driver), Pydantic, JWT
- **Frontend**: React, Tailwind CSS, shadcn/ui, react-router-dom, axios
- **Internationalization**: i18next, react-i18next
- **Database**: MongoDB

## Complete Workflow Diagram
```
Admin creates form → Client fills form (public link) → Form submitted → 
Audit calculation runs → Admin creates proposal → Proposal sent to client →
Client accepts proposal → Client fills Agreement form → Contract finalized
```

## Completed Features (December 2025)

### Phase 1: Core Application ✅
- Full Form → Quotation → Contract workflow
- Admin dashboard with form management
- JWT authentication

### Phase 2: Branding & UI ✅
- Company logo integration (high-quality)
- Professional color scheme matching Bayan brand
- Collapsible sidebar navigation

### Phase 3: Internationalization ✅
- English/Arabic language switching
- Complete Arabic translations
- Full RTL Layout support

### Phase 4: Multi-Step Application Form Wizard ✅
- 6-Step Certification Application Wizard
- Form validation and draft saving
- Declaration section

### Phase 5: Public Form Access ✅
- Admin creates forms with unique access tokens
- Public form page at `/form/{access_token}`
- No login required for clients
- Copy link functionality

### Phase 6: Automated Audit Calculation ✅
- Business logic from Excel file implemented
- Calculates audit duration based on:
  - Number of employees
  - Number of sites
  - Certification standards selected
- Results displayed on Admin Dashboard

### Phase 7: Proposal/Quotation System ✅
- **Create Proposal Page** (`/create-proposal/{formId}`):
  - Pre-fills data from application form
  - Service fees input (Initial, Surveillance 1 & 2, Recertification)
  - Auto-calculates total amount
  - Notes and validity period
  - Save & Send functionality

- **Public Proposal Page** (`/proposal/{access_token}`):
  - Client views full proposal details
  - Audit duration breakdown
  - Service fees in SAR
  - Terms and conditions
  - Accept/Reject buttons

### Phase 8: Certification Agreement Form ✅ (NEW - Dec 2025)
- **Agreement Page** (`/agreement/{access_token}`):
  - Shows after client accepts proposal
  - Pre-fills data from proposal
  - Sections:
    1. Parties to Agreement (BAC info + Client info)
    2. Management System Standards (ISO checkboxes)
    3. Scope of Services
    4. Sites for Certification
    5. Acknowledgements (6 required checkboxes)
    6. Signatory Information (Name, Position, Date)
  - Submit Agreement button
  - Success page after submission

## API Endpoints

### Authentication (Admin Only)
- `POST /api/auth/login` - Admin login
- `GET /api/auth/me` - Get current user

### Application Forms (Admin)
- `POST /api/application-forms` - Create form with client info
- `GET /api/application-forms` - List all forms
- `GET /api/application-forms/{id}` - Get specific form
- `POST /api/application-forms/{id}/send-email` - Send form link (MOCKED)

### Public Form Access (No Auth)
- `GET /api/public/form/{access_token}` - Get form for client
- `PUT /api/public/form/{access_token}` - Save draft
- `POST /api/public/form/{access_token}/submit` - Submit form (triggers audit calculation)

### Proposals (Admin)
- `POST /api/proposals` - Create proposal
- `GET /api/proposals` - List proposals
- `POST /api/proposals/{id}/send` - Send proposal to client

### Public Proposal (No Auth)
- `GET /api/public/proposal/{access_token}` - Get proposal details
- `POST /api/public/proposal/{access_token}/respond` - Accept/Reject proposal

### Certification Agreement (No Auth)
- `GET /api/public/agreement/{access_token}` - Get agreement status
- `POST /api/public/agreement/{access_token}/submit` - Submit signed agreement

## Database Schema

### ApplicationForm
```json
{
  "id": "UUID",
  "access_token": "UUID",
  "client_info": { "name", "company_name", "email", "phone" },
  "company_data": { /* 6-step wizard data */ },
  "audit_calculation": { "stage_1", "stage_2", "total_days", "integration_discount" },
  "status": "pending | submitted | under_review | approved | agreement_signed",
  "created_at": "datetime",
  "submitted_at": "datetime"
}
```

### Proposal
```json
{
  "id": "UUID",
  "access_token": "UUID",
  "application_form_id": "UUID",
  "organization_name": "string",
  "service_fees": { "initial_certification", "surveillance_1", "surveillance_2", "recertification" },
  "audit_duration": { "stage_1", "stage_2", "surveillance_1", "surveillance_2", "recertification" },
  "total_amount": "float",
  "status": "draft | sent | accepted | rejected | agreement_signed",
  "issued_date": "datetime"
}
```

### CertificationAgreement
```json
{
  "id": "UUID",
  "proposal_id": "UUID",
  "proposal_access_token": "UUID",
  "organization_name": "string",
  "selected_standards": ["ISO9001", "ISO14001"],
  "scope_of_services": "string",
  "sites": ["address1", "address2"],
  "signatory_name": "string",
  "signatory_position": "string",
  "acknowledgements": { /* 6 boolean fields */ },
  "status": "submitted | contract_generated",
  "created_at": "datetime"
}
```

## File Structure
```
/app/
├── backend/
│   ├── server.py
│   ├── audit_calculator.py (audit duration logic)
│   ├── tests/
│   │   ├── test_service_contract.py
│   │   └── test_agreement.py
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ApplicationForm.js
│   │   │   ├── LanguageSwitcher.js
│   │   │   └── Sidebar.js
│   │   ├── pages/
│   │   │   ├── AdminDashboard.js
│   │   │   ├── LoginPage.js
│   │   │   ├── PublicFormPage.js
│   │   │   ├── CreateProposalPage.js
│   │   │   ├── PublicProposalPage.js
│   │   │   └── CertificationAgreementPage.js (NEW)
│   │   ├── App.js
│   │   └── i18n.js
│   └── tailwind.config.js
└── test_reports/
    └── iteration_4.json
```

## Test Credentials
- **Admin**: admin@test.com / admin123

## Testing Status
- Backend API: 100% PASSED
- Frontend UI: 100% PASSED
- Test Reports: `/app/test_reports/iteration_4.json`

## MOCKED Integrations
- **Email Sending**: MOCKED - Logs to console instead of sending real emails

## Upcoming Tasks (P1)
1. **PDF Contract Generation**: Generate PDF from signed agreement
2. **Admin Notifications**: Alerts when forms submitted or proposals actioned
3. **Fix form button visibility**: Sticky footer for navigation buttons

## Future/Backlog Tasks (P2)
1. **Enable Real Email Sending**: Integrate SendGrid or SMTP
2. **Templates Feature**: Reusable form and proposal templates
3. **Reports Section**: Business analytics
4. **Clean up ClientDashboard.js**: Remove legacy component
