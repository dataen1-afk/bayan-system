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

### Phase 3: Internationalization ✅
- English/Arabic language switching with flag icons
- Complete Arabic translations for all UI components
- **RTL Layout Fix (P0)**: Tabs now positioned on RIGHT side in Arabic mode
  - Implemented using `html[dir="rtl"] .tabs-wrapper { justify-content: flex-end !important; }`
  - Header elements properly aligned with flex-direction: row-reverse
- LTR Layout verified working correctly

### Phase 4: Empty States ✅
- Empty state messages for Admin Dashboard (Forms, Quotations, Contracts)
- Empty state messages for Client Dashboard (My Forms, Quotations, Contracts)
- Complete translation keys in Arabic and English

## Key Technical Implementation

### RTL/LTR CSS Approach
The RTL layout is implemented using CSS selectors in `/app/frontend/src/index.css`:
- `html[dir="rtl"] .tabs-wrapper { justify-content: flex-end !important; }`
- `html[dir="rtl"] .dashboard-header { flex-direction: row-reverse !important; }`

### CSS Class Structure
- `.tabs-wrapper` - Container for tab navigation
- `.dashboard-header` - Header flex container
- `.dashboard-header-left` - Logo and title section
- `.dashboard-header-right` - Language switcher and logout
- `.btn-icon` - Icon margin handling

## API Endpoints
- `/api/auth/login`, `/api/auth/me` - Authentication
- `/api/forms`, `/api/forms/{form_id}/submit` - Form management
- `/api/quotations`, `/api/quotations/{quotation_id}/respond` - Quotation management
- `/api/contracts/{contract_id}/download` - Contract PDF download

## Database Schema
- **User**: id, name, email, password, role
- **Form**: id, client_id, fields, responses, status
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
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── LanguageSwitcher.js
│   │   │   └── ui/
│   │   ├── pages/
│   │   │   ├── AdminDashboard.js
│   │   │   ├── ClientDashboard.js
│   │   │   └── LoginPage.js
│   │   ├── App.js
│   │   ├── index.css
│   │   └── i18n.js
│   └── tailwind.config.js
├── contracts/
└── test_reports/
```

## Known Issues
None - All P0/P1 issues resolved

## Future Enhancements (Backlog)
- Email notifications for quotation status changes
- Dashboard analytics and reporting
- Bulk form creation
- Contract templates
