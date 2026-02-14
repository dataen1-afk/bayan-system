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
9. Agreement submission finalizes the contract & PDF is generated

## Tech Stack
- **Backend**: FastAPI (Python), Motor (async MongoDB driver), Pydantic, JWT, ReportLab (PDF)
- **Frontend**: React, Tailwind CSS, shadcn/ui, react-router-dom, axios
- **Internationalization**: i18next, react-i18next
- **Database**: MongoDB

## Complete Workflow
```
Admin creates form → Client fills form (public link) → Form submitted → 
Audit calculation runs → Admin creates proposal → Proposal sent to client →
Client accepts proposal → Client fills Agreement form → Contract PDF generated
```

## Completed Features (December 2025)

### Core Features ✅
- Full Form → Quotation → Contract workflow
- Admin dashboard with form management
- JWT authentication for admin
- Public form access via unique tokens
- Automated audit duration calculation

### Branding & Localization ✅
- Company logo integration (high-quality)
- Professional color scheme matching Bayan brand
- English/Arabic language switching
- Full RTL layout support for Arabic

### UI/UX Improvements ✅ (NEW - Feb 2026)
- **Forms Screen**: Quick Stats header (Total, Pending, Submitted, Completed), improved list design with status badges
- **Quotations Screen**: Quick Stats header (Total Proposals, Pending Review, Accepted, Total Quoted), prominent pricing
- **Contracts Screen**: Stats cards (Total Contracts, Revenue, Most Recent), Download PDF buttons
- **Notification Dropdown**: "Mark All as Read" now clears notifications from dropdown immediately

### Proposal System ✅
- Create Proposal page with fee inputs
- Public Proposal page for client review
- Accept/Reject functionality
- Proposal access via unique tokens

### Certification Agreement ✅
- Agreement form shows after proposal acceptance
- Pre-fills data from proposal
- 6 acknowledgement checkboxes
- Signatory information capture

### PDF Contract Generation ✅ (Updated - Feb 2026)
- Professional PDF contracts with company branding
- Includes: parties, standards, scope, sites, audit duration, fees, terms, signatures
- **Digital Signatures**: Client signatures embedded in PDF
- **Company Seals**: Optional company stamp/seal in PDF
- Robust image validation with PIL preprocessing
- Graceful fallback for corrupted images
- Admin can download via `/api/contracts/{agreement_id}/pdf`
- Client can download via `/api/public/contracts/{access_token}/pdf`

### Digital Signatures ✅ (NEW - Feb 2026)
- **Signature Pad Component**: Canvas-based drawing with mouse/touch support
- **Dual Mode**: Draw signature online OR upload signature image
- **Company Seal**: **MANDATORY** stamp/seal upload (updated Feb 2026)
- **Form Validation**: Signature AND seal required before agreement submission
- **Database Storage**: signature_image and stamp_image stored as Base64
- **PDF Integration**: Signatures rendered in contract PDF with proper sizing

### Admin Notifications ✅ (Updated - Feb 2026)
- Bell icon in header with unread count badge
- Dropdown shows recent notifications
- Notification types: form_submitted, proposal_accepted, proposal_rejected, agreement_signed
- Mark as read / **Mark all as read** functionality (text truncation fixed)
- Proper RTL alignment with `whitespace-nowrap` CSS

### Contract Status Timeline ✅ (NEW - Dec 2025)
- Compact view on dashboard form cards (X/6 progress indicator)
- 6 stages: Created → Submitted → Proposal Sent → Accepted → Agreement Signed → Contract Generated
- Visual progress with icons and colors

### Templates Feature ✅ (NEW - Dec 2025)
- **Certification Packages**: Pre-configured ISO packages
  - QMS Basic (ISO 9001)
  - EMS Basic (ISO 14001)
  - OHS Basic (ISO 45001)
  - Integrated Management System (9001+14001+45001)
  - Food Safety (ISO 22000)
  - Information Security (ISO 27001)
- **Proposal Templates**: Default pricing tiers
  - Standard Pricing
  - Small Business (discounted)
  - Enterprise

### Reports & Analytics ✅ (Updated - Feb 2026)
- **Summary Cards**: Total forms, submitted, conversion rate, contracts
- **Revenue Overview**: Total quoted, accepted, pending, rejected
- **Proposal Statistics**: With conversion progress bar
- **Monthly Submissions Chart**: Last 6 months bar chart
- **Enhanced Filtering** (NEW):
  - Toggle filter panel with button
  - Date range selection (start/end date)
  - Status filter dropdown (all, pending, submitted, under_review, accepted, rejected, agreement_signed, modification_requested)
  - Certification Standard filter (ISO9001, ISO14001, etc.)
  - Apply/Clear filters buttons
  - Standards breakdown card when filters applied
  - Backend `/api/reports/filtered` endpoint with comprehensive filtering

### Contracts Page ✅ (Updated - Feb 2026)
- Displays approved price quotes converted to contracts (proposals with `status: agreement_signed`)
- **Statistics Summary Cards** at top showing:
  - Total Contracts count
  - Total Revenue in SAR
  - Most Recent Contract with date
- Contract card shows: organization name, contact person, email, standards badges, total amount, signing date
- Download Contract PDF button (generates professional PDF with branding)
- View Proposal button opens original proposal
- Status Timeline with 6-stage progress indicator
- Full RTL support for Arabic

### Sticky Footer for Form Navigation ✅ (NEW - Feb 2026)
- Form navigation buttons (Previous, Next, Save Draft, Submit) now always visible at bottom
- Fixed position footer that stays visible while scrolling through long forms
- Step indicator shows current progress (Step X of 6)
- Responsive design hides Save Draft label on small screens

### Editable Templates ✅ (NEW - Feb 2026)
- Certification Packages can now be edited after creation
- Proposal Templates can now be edited after creation
- Edit button (blue) visible next to Delete button (red) on each template card
- Edit form pre-populates with existing data
- Backend PUT endpoints for both packages and templates

### Modification Request Mechanism ✅ (NEW - Feb 2026)
- Clients can request modifications to proposals before accepting/rejecting
- "Request Modification" button (orange) on Public Proposal Page
- Modal with required comment field and optional specific changes field
- Proposal status updates to `modification_requested`
- Admin receives notification with client's comment
- Dedicated status page shows when modification is pending review
- Backend endpoint: `POST /api/public/proposal/{access_token}/request_modification`

## API Endpoints

### Authentication
- `POST /api/auth/login` - Admin login
- `GET /api/auth/me` - Get current user

### Application Forms
- `POST /api/application-forms` - Create form
- `GET /api/application-forms` - List forms
- `GET /api/public/form/{access_token}` - Get form (public)
- `POST /api/public/form/{access_token}/submit` - Submit form

### Proposals
- `POST /api/proposals` - Create proposal
- `GET /api/proposals` - List proposals
- `GET /api/public/proposal/{access_token}` - Get proposal (public)
- `POST /api/public/proposal/{access_token}/respond` - Accept/Reject

### Agreement & Contracts
- `GET /api/public/agreement/{access_token}` - Get agreement status
- `POST /api/public/agreement/{access_token}/submit` - Submit agreement
- `GET /api/contracts/{agreement_id}/pdf` - Download contract (admin)
- `GET /api/public/contracts/{access_token}/pdf` - Download contract (public)

### Notifications
- `GET /api/notifications` - Get notifications (with limit, unread_only params)
- `PUT /api/notifications/{id}/read` - Mark as read
- `PUT /api/notifications/read-all` - Mark all as read

### Templates
- `GET /api/templates/packages` - Get certification packages
- `POST /api/templates/packages` - Create package
- `PUT /api/templates/packages/{id}` - Update package
- `DELETE /api/templates/packages/{id}` - Delete package
- `GET /api/templates/proposals` - Get proposal templates
- `POST /api/templates/proposals` - Create template
- `PUT /api/templates/proposals/{id}` - Update template
- `DELETE /api/templates/proposals/{id}` - Delete template

### Reports
- `GET /api/reports/submissions` - Submission statistics
- `GET /api/reports/revenue` - Revenue statistics
- `GET /api/reports/filtered` - Filtered reports with date range, status, and standard parameters

### Modification Request
- `POST /api/public/proposal/{access_token}/request_modification` - Submit modification request (public)

## Test Credentials
- **Admin**: admin@test.com / admin123

## Testing Status (Feb 2026)
- Backend API: 100% (all tests passed)
- Frontend UI: 100% (all tests passed)
- Latest Test Report: `/app/test_reports/iteration_10.json`
- Signature Tests: `/app/backend/tests/test_signature_feature.py`
- Seal Mandatory Tests: `/app/backend/tests/test_seal_mandatory.py`

## Cleanup Completed
- Removed obsolete `ClientDashboard.js` (clients access via public links, no login)

## MOCKED Integrations
- **Email Sending**: MOCKED - Logs to console instead of sending real emails

## File Structure
```
/app/
├── backend/
│   ├── server.py (main API)
│   ├── audit_calculator.py (audit duration logic)
│   ├── pdf_generator.py (contract PDF generation)
│   └── tests/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── NotificationBell.js (NEW)
│   │   │   ├── StatusTimeline.js (NEW)
│   │   │   └── ...
│   │   ├── pages/
│   │   │   ├── AdminDashboard.js
│   │   │   ├── ReportsPage.js (NEW)
│   │   │   ├── TemplatesPage.js (NEW)
│   │   │   ├── CertificationAgreementPage.js
│   │   │   └── ...
│   │   └── i18n.js
└── test_reports/
```

## Upcoming Features (User Requested)
1. **Customer Portal for Order Status Tracking** - Simple page for clients to track application status
2. **Multi-Site Auditing/Scheduling** - Manage audits across multiple client locations
3. **Export Reports Dashboard to Excel/PDF** - Download reports functionality
4. **View Audit Scheduling Calendar** - Calendar view for audit schedules
5. **Record Customer Contacts** - Customer contact history log

## Future Enhancements
- Enable real email sending (SendGrid integration)
