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
- **Backend**: FastAPI (Python), Motor (async MongoDB driver), Pydantic, JWT, ReportLab (PDF), openpyxl (Excel)
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

### UI/UX Improvements ✅
- **Forms Screen**: Quick Stats header (Total, Pending, Submitted, Completed), improved list design with status badges
- **Quotations Screen**: Quick Stats header (Total Proposals, Pending Review, Accepted, Total Quoted), prominent pricing
- **Contracts Screen**: Stats cards (Total Contracts, Revenue, Most Recent), Download PDF buttons
- **Notification Dropdown**: "Mark All as Read" button fully visible (wider dropdown), clicking clears/deletes all notifications from database to prevent accumulation
- **Certification Agreement Checkboxes**: Fixed checkbox hitbox issue - clicking anywhere on the checkbox row (box or text) now properly toggles the selection for both Standards and Acknowledgements sections
- **Numeral Standardization**: All numbers display in Western Arabic numerals (0-9)
- **Currency Standardization**: All amounts show "SAR" instead of "ر.س."

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

### PDF Contract Generation ✅
- Professional PDF contracts with company branding
- Includes: parties, standards, scope, sites, audit duration, fees, terms, signatures
- **Digital Signatures**: Client signatures embedded in PDF
- **Company Seals**: Optional company stamp/seal in PDF
- Robust image validation with PIL preprocessing
- Graceful fallback for corrupted images
- Admin can download via `/api/contracts/{agreement_id}/pdf`
- Client can download via `/api/public/contracts/{access_token}/pdf`

### Digital Signatures ✅
- **Signature Pad Component**: Canvas-based drawing with mouse/touch support
- **Dual Mode**: Draw signature online OR upload signature image
- **Company Seal**: **MANDATORY** stamp/seal upload
- **Form Validation**: Signature AND seal required before agreement submission
- **Database Storage**: signature_image and stamp_image stored as Base64
- **PDF Integration**: Signatures rendered in contract PDF with proper sizing

### Admin Notifications ✅
- Bell icon in header with unread count badge
- Dropdown shows recent notifications
- Notification types: form_submitted, proposal_accepted, proposal_rejected, agreement_signed
- Mark as read / **Mark all as read** functionality
- **NEW: Clickable Notifications** - Click a notification to:
  - Mark it as read automatically
  - Navigate to the relevant tab (Forms/Quotations/Contracts)
  - Highlight the specific item with yellow background for 3 seconds
  - Close the dropdown

### Contract Status Timeline ✅
- Compact view on dashboard form cards (X/6 progress indicator)
- 6 stages: Created → Submitted → Proposal Sent → Accepted → Agreement Signed → Contract Generated
- Visual progress with icons and colors

### Templates Feature ✅
- **Certification Packages**: Pre-configured ISO packages
- **Proposal Templates**: Default pricing tiers (Standard, Small Business, Enterprise)
- Edit functionality for both packages and templates

### Reports & Analytics ✅ (UPDATED - Dec 2025)
- **Summary Cards**: Total forms, submitted, conversion rate, contracts
- **Revenue Overview**: Total quoted, accepted, pending, rejected
- **Proposal Statistics**: With conversion progress bar
- **Monthly Submissions Chart**: Last 6 months bar chart
- **Enhanced Filtering**: Date range, status, certification standard
- **NEW: Export to Excel**: Download `.xlsx` file with formatted data
- **NEW: Export to PDF**: Download `.pdf` report summary

### Modification Request Mechanism ✅
- Clients can request modifications to proposals before accepting/rejecting
- "Request Modification" button on Public Proposal Page
- Modal with required comment field
- Admin receives notification with client's comment

## NEW FEATURES (December 2025)

### Customer Portal ✅ (NEW)
- **Public tracking page**: `/track` and `/track/:trackingId`
- Clients can track their application status using form ID or access token
- **Order Status Timeline**: 6-step visual progress (Form Created → Submitted → Under Review → Proposal Accepted → Agreement Signed → Contract Ready)
- Displays: Company info, contact details, standards, dates
- Download contract button when available
- View proposal link
- Help section with contact email
- Full RTL support for Arabic

### Audit Scheduling & Calendar ✅ (NEW)
- **Dedicated page**: `/audit-scheduling`
- **Calendar View**: Interactive monthly calendar with audit events
- **List View**: Toggle between calendar and list modes
- **Create Audit Modal**: Select contract, audit type (initial/surveillance/recertification), date/time, duration, auditors, notes
- **Delete Audit**: Remove scheduled audits
- Audit types with color coding
- Full RTL support

### Contact History Management ✅ (NEW)
- **Dedicated page**: `/contact-history`
- **CRUD Operations**: Create, view, filter, delete contact records
- **Contact Types**: Phone Call, Email, Meeting, Other
- **Follow-up Tracking**: Set follow-up dates and mark as completed
- **Customer Filter**: Filter by specific customer
- Color-coded contact type badges
- Full RTL support

### Document Management ✅ (NEW)
- **Component**: `DocumentManagement.js`
- **Upload documents**: Base64 encoding for file storage
- **Download documents**: Retrieve with original filename
- **Delete documents**: Remove uploaded files
- Support for PDF, images, and other formats
- File size display
- Can be linked to forms, proposals, or contracts

### Sites Management API ✅ (NEW)
- **Endpoints**: `/api/sites` (GET, POST), `/api/sites/{id}` (DELETE)
- Create sites with: name, address, city, country, contact info
- Support for multi-site auditing
- Link sites to contracts

### Enhanced Sidebar Navigation ✅ (NEW)
- **New menu items**:
  - جدولة التدقيق (Audit Scheduling) → `/audit-scheduling`
  - سجل الاتصالات (Contact History) → `/contact-history`
  - المستندات (Documents) → `/documents`

### Bilingual PDF Contracts ✅ (NEW - Dec 2025)
- **Dual-language PDF generation**: Arabic + English in same PDF
- **Arabic text processing**: Uses arabic-reshaper and python-bidi for proper RTL display
- **Arabic fonts**: Noto Sans Arabic font registration
- **Admin endpoint**: `/api/contracts/{agreement_id}/pdf/bilingual`
- **Public endpoint**: `/api/public/contracts/{access_token}/pdf/bilingual`
- **UI**: Two PDF buttons on Contracts tab - standard and bilingual (AR/EN)
- Includes all contract sections in both languages

### Google Calendar Integration ✅ (NEW - Dec 2025)
- **Status endpoint**: `/api/calendar/status` - Check connection status
- **Auth URL endpoint**: `/api/calendar/auth/url` - Get OAuth URL
- **OAuth callback**: `/api/oauth/calendar/callback` - Handle Google auth
- **Sync audit**: `/api/calendar/sync-audit` - Sync audit to Google Calendar
- **Disconnect**: `/api/calendar/disconnect` - Remove calendar connection
- **UI**: Connect/Disconnect buttons on Audit Scheduling page
- **Sync button**: Per-audit sync to Google Calendar when connected
- **Note**: Requires GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in environment

### Documents Page ✅ (NEW - Dec 2025)
- **Dedicated page**: `/documents`
- **Sidebar link**: Added to admin navigation
- **Features**: Upload, download, delete documents
- **Grid layout**: Responsive document cards
- **RTL support**: Full Arabic layout support
- Proper navigation with route handling

### Advanced Audit Scheduling with Recurring Events ✅ (NEW - Feb 2026)
- **Recurring Event Support**: Create audits that automatically repeat
- **Frequency Options**: Weekly, Monthly, Quarterly (every 3 months), Yearly
- **End Date Configuration**: Set when recurring series should end
- **Auto-generation**: System automatically creates all recurring audit instances
- **UI**: Checkbox to enable recurring + frequency dropdown + end date picker
- **Backend**: Uses python-dateutil for date calculations

### SMS Notifications via Twilio ✅ (NEW - Feb 2026)
- **Status endpoint**: `/api/sms/status` - Check SMS configuration status
- **Send endpoint**: `/api/sms/send` - Send SMS notification
- **Audit reminder**: `/api/sms/send-audit-reminder` - Send audit reminder SMS
- **Logs endpoint**: `/api/sms/logs` - View SMS sending history
- **Simulation Mode**: Works without Twilio credentials (logs simulated messages)
- **Bilingual Messages**: Reminders sent in both Arabic and English
- **UI**: SMS reminder button on each audit in list view
- **Note**: Requires TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER in environment for real SMS

### Multilingual PDF Generation ✅ (NEW - Feb 2026)
- **Forms PDF**: `/api/forms/{form_id}/bilingual_pdf` - Bilingual form submission PDF
- **Proposals PDF**: `/api/proposals/{proposal_id}/bilingual_pdf` - Bilingual quotation PDF
- **Reports PDF**: `/api/reports/bilingual_pdf` - Bilingual summary report PDF
- **UI Buttons**: Added bilingual PDF download buttons in Forms and Quotations tabs
- **Arabic + English**: All PDFs contain both languages side by side
- **Professional formatting**: Company branding, color scheme, proper RTL text

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
- `POST /api/public/proposal/{access_token}/request_modification` - Request modification

### Agreement & Contracts
- `GET /api/public/agreement/{access_token}` - Get agreement status
- `POST /api/public/agreement/{access_token}/submit` - Submit agreement
- `GET /api/contracts/{agreement_id}/pdf` - Download contract (admin)
- `GET /api/public/contracts/{access_token}/pdf` - Download contract (public)

### Notifications
- `GET /api/notifications` - Get notifications
- `PUT /api/notifications/{id}/read` - Mark as read
- `PUT /api/notifications/read-all` - Mark all as read

### Templates
- `GET/POST /api/templates/packages` - Certification packages
- `PUT/DELETE /api/templates/packages/{id}` - Package CRUD
- `GET/POST /api/templates/proposals` - Proposal templates
- `PUT/DELETE /api/templates/proposals/{id}` - Template CRUD

### Reports (UPDATED)
- `GET /api/reports/submissions` - Submission statistics
- `GET /api/reports/revenue` - Revenue statistics
- `GET /api/reports/filtered` - Filtered reports
- **NEW**: `GET /api/reports/export?format=excel|pdf` - Export reports

### Customer Portal (NEW)
- `GET /api/public/track/{tracking_id}` - Track order status (public)

### Audit Scheduling (NEW)
- `GET /api/audit-schedules` - List audit schedules
- `POST /api/audit-schedules` - Create audit schedule
- `PUT /api/audit-schedules/{id}` - Update audit schedule
- `DELETE /api/audit-schedules/{id}` - Delete audit schedule

### Contact History (NEW)
- `GET /api/contacts` - List contacts (optional: ?customer_id=xxx)
- `POST /api/contacts` - Create contact record
- `PUT /api/contacts/{id}/follow-up` - Mark follow-up completed
- `DELETE /api/contacts/{id}` - Delete contact record

### Document Management (NEW)
- `GET /api/documents` - List documents (optional: ?related_id=xxx)
- `POST /api/documents` - Upload document
- `GET /api/documents/{id}` - Get document with file data
- `DELETE /api/documents/{id}` - Delete document

### Sites Management (NEW)
- `GET /api/sites` - List sites
- `POST /api/sites` - Create site
- `DELETE /api/sites/{id}` - Delete site

## Test Credentials
- **Admin**: admin@test.com / admin123

## UI Components Update (December 2025)

### DataTable Component ✅ (NEW/FIXED)
- **Location**: `/app/frontend/src/components/DataTable.js`
- **Purpose**: Professional reusable table component with:
  - Pagination, search, sorting, filtering
  - **Native RTL Support**: Uses `dir="rtl"` attribute instead of `flex-row-reverse` classes
  - Works across Forms, Quotations, and Contracts tabs
- **Key RTL Implementation**:
  - Table body uses `dir={isRTL ? 'rtl' : 'ltr'}` for native browser RTL support
  - Row cells use `text-start` class which auto-adjusts based on dir attribute
  - Action columns have `dir="ltr"` to maintain consistent button order

### RTL Layout Fix (December 2025) ✅
- **Issue**: Previous implementation used CSS `flex-row-reverse` conditionally, which was unreliable
- **Solution**: Changed to native HTML `dir` attribute approach:
  1. Table body wrapper has `dir="rtl"` for Arabic
  2. This makes flexbox naturally reverse
  3. Action column uses `dir="ltr"` to keep button order consistent
- **Result**: In Arabic mode:
  - Action buttons appear on **LEFT**
  - Data columns (company name) appear on **RIGHT**
  - Works correctly across Forms, Quotations, Contracts tabs

### Data Table Professional Layout Fix (February 2026) ✅
- **Issue**: Data overlapping in Forms, Quotations, and Contracts tabs. Action icons not visible properly.
- **Solution**: 
  1. Changed from fixed percentage widths to min-width + flex-1 approach
  2. Added horizontal scrolling for smaller screens
  3. Used square icon buttons (w-8 h-8 p-0) for consistent action column layout
  4. Added proper gap spacing (gap-1.5) between action buttons
  5. Added tooltips (title attribute) for truncated text
- **Files Modified**:
  - `/app/frontend/src/pages/AdminDashboard.js` - Updated column definitions and row rendering
  - `/app/frontend/src/components/DataTable.js` - Added overflow-x-auto and min-width to table
- **Result**:
  - All data visible without overlap
  - Action icons clearly displayed with consistent spacing
  - Professional layout across all three tabs (Forms, Quotations, Contracts)
  - Hover tooltips show full text for truncated fields

## Testing Status (February 2026)
- Backend API: 100% (All tests passed)
- Frontend UI: 100% (All features working)
- RTL Layout Tests: 100% (All 6 scenarios passed)
- Bilingual PDF Tests: 100% (Both endpoints working - Amiri Arabic font verified)
- Google Calendar API: 100% (Status endpoint tested)
- **Full E2E Workflow Test**: PASSED (Iteration 16 - 21/21 tests)
- **Clickable Notifications Test**: PASSED (Iteration 17 - 5/5 features)
- Latest Test Report: `/app/test_reports/iteration_17.json`
- New Test Files:
  - `/app/backend/tests/test_iteration15_features.py`
  - `/app/backend/tests/test_iteration16_full_workflow.py`

### Latest E2E Test Results (Feb 2026)
- Admin login ✅
- Create application form ✅
- Client fills public form ✅
- Audit duration auto-calculation ✅
- Admin creates proposal ✅
- Client accepts proposal ✅
- Client signs certification agreement ✅
- PDF generation (standard & bilingual) ✅
- Arabic text rendering in PDF ✅ (Amiri font embedded)
- **Clickable Notifications** ✅ (Navigate to item, mark as read, highlight row)

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
│       ├── test_new_features.py (NEW)
│       └── ...
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── DataTable.js (NEW - Professional table with RTL support)
│   │   │   ├── NotificationBell.js
│   │   │   ├── StatusTimeline.js
│   │   │   ├── Sidebar.js (UPDATED)
│   │   │   ├── DocumentManagement.js (NEW)
│   │   │   └── ...
│   │   ├── pages/
│   │   │   ├── AdminDashboard.js (UPDATED - Uses DataTable)
│   │   │   ├── ReportsPage.js (UPDATED - Export)
│   │   │   ├── TemplatesPage.js
│   │   │   ├── CustomerPortalPage.js (NEW)
│   │   │   ├── AuditSchedulingPage.js (NEW)
│   │   │   ├── ContactHistoryPage.js (NEW)
│   │   │   ├── CertificationAgreementPage.js
│   │   │   └── ...
│   │   ├── utils/
│   │   │   └── formatter.js (number/currency formatting)
│   │   └── i18n.js (UPDATED)
└── test_reports/
```

## Future Enhancements
- Enable real email sending (SendGrid integration)
- Advanced audit scheduling with recurring events
- Integration with external calendar systems
- Dashboard analytics with charts
