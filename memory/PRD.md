# Service Contract Management System - PRD

## Original Problem Statement
Build a full-stack application for managing service contracts with the following workflow:
1. Admin creates and sends a form to a client
2. Client fills the form and submits it
3. Admin reviews the submission and sends a price quote
4. Client can **approve**, **reject**, or **request modifications** to the quote
5. An approved quote automatically becomes a contract, generating a PDF

## User Personas
- **Admin**: Creates forms, manages quotations, and oversees contracts
- **Client**: Fills forms, reviews quotations, downloads contracts

## Core Requirements
- **User Roles**: Admin and Client, with distinct dashboards and permissions
- **Authentication**: Internal system (JWT) where Admins manage all user accounts
- **UI/UX**: Professional, branded interface matching "Bayan Auditing & Conformity" logo
- **Multi-language Support**: English and Arabic with RTL layout for Arabic
- **Empty States**: Helpful, user-friendly messages when no data exists

## Tech Stack
- **Backend**: FastAPI (Python), Motor (async MongoDB driver), Pydantic, JWT
- **Frontend**: React, Tailwind CSS, shadcn/ui, react-router-dom, axios
- **Internationalization**: i18next, react-i18next
- **Database**: MongoDB

## Completed Features (December 2025)

### Phase 1: Core Application ✅
- Full Form → Quotation → Contract workflow
- Admin & Client dashboards with distinct views
- JWT authentication with "Remember me" feature
- PDF contract generation

### Phase 2: Branding & UI ✅
- Company logo integration with white background container
- Professional color scheme matching Bayan brand
- Admin credentials displayed on login page for testing
- Collapsible sidebar navigation

### Phase 3: Internationalization ✅
- English/Arabic language switching with flag icons
- Complete Arabic translations for all UI components
- RTL Layout implemented using CSS `[dir="rtl"]` selectors
- LTR Layout verified working correctly

### Phase 4: Empty States ✅
- Empty state messages for Admin Dashboard (Forms, Quotations, Contracts)
- Empty state messages for Client Dashboard (My Forms, Quotations, Contracts)
- Complete translation keys in Arabic and English

### Phase 5: Multi-Step Application Form Wizard ✅ (NEW)
- **6-Step Certification Application Wizard** implemented:
  1. **Company Information**: Company name, address, contact details, legal status
  2. **Certification Selection**: ISO 9001, 14001, 45001, 27001, 22000, 50001, 13485, 22301, 41001
  3. **Sites & Employees**: Number of sites, employee breakdown, shift information
  4. **Existing Certifications**: Current certifications, consultant involvement
  5. **Management Systems**: Conditional fields based on selected certifications (EMS, FSMS, OHSMS, EnMS, Medical Devices, ISMS)
  6. **Declaration**: Signature and agreement confirmation
- **Admin Features**:
  - Assign new application forms to clients via modal
  - View submitted applications
  - Client selection dropdown from registered users
- **Client Features**:
  - View assigned application forms
  - Fill forms step-by-step with navigation (Next/Previous)
  - Save draft functionality
  - Submit completed applications
- **Backend API**:
  - `POST /api/application-forms` - Create and assign form
  - `GET /api/application-forms` - List forms (filtered by role)
  - `GET /api/application-forms/{id}` - Get specific form
  - `PUT /api/application-forms/{id}` - Save draft
  - `POST /api/application-forms/{id}/submit` - Submit form
  - `GET /api/users/clients` - Get list of clients (admin only)

## Key Technical Implementation

### RTL/LTR CSS Approach
The RTL layout is implemented using CSS selectors in `/app/frontend/src/index.css`:
- `html[dir="rtl"] .tabs-wrapper { justify-content: flex-end !important; }`
- `html[dir="rtl"] .dashboard-header { flex-direction: row-reverse !important; }`
- `html[dir="rtl"] .sidebar-container { right: 0; left: auto; }`

### CSS Class Structure
- `.tabs-wrapper` - Container for tab navigation
- `.dashboard-header` - Header flex container
- `.dashboard-header-left` - Logo and title section
- `.dashboard-header-right` - Language switcher and logout
- `.btn-icon` - Icon margin handling
- `.sidebar-container` - Sidebar positioning

## API Endpoints
- `/api/auth/login`, `/api/auth/me` - Authentication
- `/api/forms`, `/api/forms/{form_id}/submit` - Form management (legacy)
- `/api/application-forms` - Certification application forms (new)
- `/api/users/clients` - List client users (admin only)
- `/api/quotations`, `/api/quotations/{quotation_id}/respond` - Quotation management
- `/api/contracts/{contract_id}/download` - Contract PDF download

## Database Schema
- **User**: id, name, email, password, role
- **Form**: id, client_id, fields, responses, status (legacy)
- **ApplicationForm**: id, client_id, company_data (nested), status, created_at, submitted_at
- **Quotation**: id, form_id, client_id, price, details, status
- **Contract**: id, quotation_id, client_id, pdf_path, created_at

## Test Credentials
- **Admin**: admin@test.com / admin123
- **Client**: client@test.com / client123

## File Structure
```
/app/
├── backend/
│   ├── server.py
│   ├── tests/
│   │   └── test_application_forms.py
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ApplicationForm.js  (NEW - 6-step wizard)
│   │   │   ├── LanguageSwitcher.js
│   │   │   ├── Sidebar.js
│   │   │   └── ui/
│   │   ├── pages/
│   │   │   ├── AdminDashboard.js  (Updated with form assignment)
│   │   │   ├── ClientDashboard.js  (Updated with form filling)
│   │   │   └── LoginPage.js
│   │   ├── App.js
│   │   ├── index.css
│   │   └── i18n.js  (Updated with new translations)
│   └── tailwind.config.js
├── contracts/
└── test_reports/
```

## Known Issues
None - All P0/P1 issues resolved

## Testing Status
- Backend API Tests: 21/21 PASSED (100%)
- Frontend UI Tests: All PASSED (100%)
- Test Report: `/app/test_reports/iteration_2.json`

## Upcoming Tasks (P1)
1. **Form Workflow Integration**:
   - Admin review submitted applications
   - "BAC Official Use" section visible only to admins after submission
   - Create quotations from submitted application forms

2. **Form Status Management**:
   - Implement `under_review` status
   - Implement `approved`/`rejected` status with notifications

## Future/Backlog Tasks (P2)
- Templates feature for reusable form templates
- Reports section for analytics
- Email notifications for form status changes
- Bulk form creation
- Contract templates
