# Service Contract Management System - PRD

## Original Problem Statement
Build a full-stack application for managing service contracts with the following workflow:
1. Admin creates a form by entering client information (name, company, email, phone)
2. System generates a unique public link for the form
3. Admin shares the link with the client (via email, WhatsApp, etc.)
4. Client fills out the form via the public link (NO LOGIN REQUIRED)
5. Client submits the form
6. Admin reviews the submission and sends a price quote
7. Client can approve, reject, or request modifications to the quote
8. An approved quote automatically becomes a contract, generating a PDF

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

## Completed Features (December 2025)

### Phase 1: Core Application ✅
- Full Form → Quotation → Contract workflow
- Admin dashboard with form management
- JWT authentication
- PDF contract generation

### Phase 2: Branding & UI ✅
- Company logo integration
- Professional color scheme matching Bayan brand
- Collapsible sidebar navigation

### Phase 3: Internationalization ✅
- English/Arabic language switching
- Complete Arabic translations
- RTL Layout using CSS `[dir="rtl"]` selectors

### Phase 4: Multi-Step Application Form Wizard ✅
- **6-Step Certification Application Wizard**:
  1. Company Information
  2. Certification Selection
  3. Sites and Employees
  4. Existing Certifications
  5. Management Systems
  6. Declaration

### Phase 5: Public Form Access (NEW - December 2025) ✅
- **Admin Form Creation**:
  - Modal to enter client info (name, company, email, phone)
  - Generates unique access token for each form
  - Shows form link modal after creation
  - Copy link to clipboard functionality
  - Send email button (MOCKED - logs to console)

- **Public Form Page** (`/form/{access_token}`):
  - No login required
  - Displays client info header
  - Full 6-step wizard form
  - Save draft functionality
  - Submit functionality with validation
  - Success message after submission
  - Language switching (Arabic/English)

- **Backend API - Public Endpoints**:
  - `GET /api/public/form/{access_token}` - Get form data
  - `PUT /api/public/form/{access_token}` - Save draft
  - `POST /api/public/form/{access_token}/submit` - Submit form

## API Endpoints

### Authentication (Admin Only)
- `POST /api/auth/login` - Admin login
- `GET /api/auth/me` - Get current user

### Application Forms (Admin)
- `POST /api/application-forms` - Create form with client info
- `GET /api/application-forms` - List all forms
- `GET /api/application-forms/{id}` - Get specific form
- `POST /api/application-forms/{id}/send-email` - Send form link via email (MOCKED)

### Public Form Access (No Auth)
- `GET /api/public/form/{access_token}` - Get form for client
- `PUT /api/public/form/{access_token}` - Save draft
- `POST /api/public/form/{access_token}/submit` - Submit form

### Legacy Endpoints
- `/api/forms`, `/api/quotations`, `/api/contracts`

## Database Schema

### ApplicationForm
```json
{
  "id": "UUID",
  "access_token": "UUID (for public access)",
  "client_info": {
    "name": "string",
    "company_name": "string",
    "email": "string",
    "phone": "string"
  },
  "company_data": { /* Form data from 6-step wizard */ },
  "status": "pending | submitted | under_review | approved | rejected",
  "created_at": "datetime",
  "submitted_at": "datetime | null"
}
```

## File Structure
```
/app/
├── backend/
│   ├── server.py
│   ├── tests/
│   │   └── test_service_contract.py
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ApplicationForm.js
│   │   │   ├── LanguageSwitcher.js
│   │   │   ├── Sidebar.js
│   │   │   └── ui/
│   │   ├── pages/
│   │   │   ├── AdminDashboard.js
│   │   │   ├── ClientDashboard.js (legacy, kept for reference)
│   │   │   ├── LoginPage.js
│   │   │   └── PublicFormPage.js (NEW)
│   │   ├── App.js
│   │   ├── index.css
│   │   └── i18n.js
│   └── tailwind.config.js
└── test_reports/
```

## Test Credentials
- **Admin**: admin@test.com / admin123

## Testing Status
- Backend API: 16/16 PASSED (100%)
- Frontend UI: All PASSED (100%)
- Test Report: `/app/test_reports/iteration_3.json`

## MOCKED Integrations
- **Email Sending**: MOCKED - Logs to console instead of sending real emails (SMTP not configured). To enable real email, configure SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS in backend/.env

## Upcoming Tasks (P1)
1. **Quotation Workflow**:
   - Admin review submitted applications
   - Create quotations from submitted forms
   - Send quotation to client

2. **Configure Real Email Sending**:
   - Integrate with email service (SendGrid, SMTP, etc.)
   - Send form links automatically to clients

## Future/Backlog Tasks (P2)
- Templates feature for reusable form templates
- Reports section for analytics
- Contract PDF generation from approved quotations
- Form status email notifications
