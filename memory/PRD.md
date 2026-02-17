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
- **Forms PDF**: `/api/forms/{form_id}/bilingual_pdf` - Comprehensive bilingual form PDF with ALL client-filled data
  - Includes: Company info, contact details, organization details, certification standards, sites info, audit info
  - Company logo at top of PDF
  - Multi-page support for extensive data
- **Proposals PDF**: `/api/proposals/{proposal_id}/bilingual_pdf` - Professional bilingual quotation PDF
  - Includes: Client info, certification scope, audit duration, service fees, validity
  - Company stamp section (no signature - pending client approval)
  - Company logo at top of PDF
- **Contracts PDF**: Both standard and bilingual versions
  - Full signature and company seal from client
  - Company logo at top of PDF
- **Reports PDF**: `/api/reports/bilingual_pdf` - Bilingual summary report PDF
- **UI Buttons**: Added bilingual PDF download buttons in Forms and Quotations tabs
- **Arabic + English**: All PDFs contain both languages side by side
- **Professional formatting**: Company branding, color scheme, proper RTL text

### Grant Agreement PDF from DOCX Template ✅ (NEW - Feb 2026)
- **Template-based generation**: Uses official BAYAN DOCX template (`/app/backend/assets/grant_agreement_template.docx`)
- **Dynamic data filling**:
  - Client Organization name
  - Client address
  - Standards checkboxes (☑ for selected, ☐ for unselected)
  - Scope of services
  - Site locations
  - Client signatory information
  - BAC signatory (issuer) information
- **PDF conversion**: Uses LibreOffice headless mode for high-quality conversion
- **Endpoints**:
  - Admin: `/api/contracts/{agreement_id}/pdf`
  - Public: `/api/public/contracts/{access_token}/pdf`
- **Files**:
  - Generator: `/app/backend/grant_agreement_generator.py`
  - Template: `/app/backend/assets/grant_agreement_template.docx`

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

## Latest Test Report (February 2026)
- **Iteration 19**: Proposal Creation with Signature/Stamp Fix
  - Create proposal with signature/stamp images: PASS
  - ~400KB payload with base64 images: PASS
  - Error handling (no more [object Object]): PASS
  - Pydantic validation errors display properly: PASS
  - **Overall: 100% tests passed (backend 3/3, frontend all scenarios)**

- **Iteration 18**: Bilingual PDF Visual Verification
  - Form PDF Text Layout: PASS
  - Proposal PDF Text Layout: PASS  
  - Company Seal Visibility: PASS
  - Arabic Text Rendering: PASS
  - PDF Endpoints: PASS
  - **Overall: 11/11 tests passed (100%)**

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
- **UI Cleanup - Redundant Download Buttons Removed** ✅ (Feb 2026)
  - Quotations tab: Removed standalone bilingual PDF button; only green PDF button for signed agreements remains
  - Contracts tab: Removed all download buttons; downloads are available from Forms tab (agreement_signed status)
  - Forms tab: Primary download button preserved for agreement_signed forms

## MOCKED Integrations
- **Email Sending**: MOCKED - Logs to console instead of sending real emails
- **SMS Notifications**: MOCKED (simulation mode) - Requires Twilio credentials for real SMS

## Bug Fixes (February 2026)
### P0: Proposal Creation with Signature/Stamp Images ✅ (FIXED)
- **Issue**: Creating a price quote with signature and stamp images showed `[object Object]` error
- **Root Cause**: Frontend error handling didn't properly parse Pydantic validation error arrays
- **Fix**: Updated `CreateProposalPage.js` lines 167-216 to handle Array.isArray(detail) case
- **Result**: Proposals with ~400KB payloads (including base64 signature/stamp) now work correctly
- **Test File**: `/app/backend/tests/test_proposal_creation.py`

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

## Completed Fixes (February 2026)

### Phase 4: Certificate Generation with QR Codes ✅ (NEW)
- **Backend**: Full certificate CRUD API (`/api/certificates`)
- **Features**:
  - Auto-generated certificate numbers (CERT-YYYY-XXXX)
  - QR code generation for verification
  - 3-year validity period
  - Status management (active, suspended, withdrawn, expired)
  - PDF certificate generation with bilingual support
  - Public verification endpoint (`/api/public/verify/{cert_number}`)
- **Frontend**: `/certificates` - Certificate management page with stats, search, filter

### Phase 5: Expiration Alerts Dashboard ✅ (NEW)
- **Backend**: `/api/alerts/expiring` endpoint
- **Features**:
  - Categorized alerts (Critical: 30 days, Warning: 60 days, Info: 90 days)
  - Configurable time period (30/60/90/180 days)
  - Tracks certificate expirations and upcoming audits
  - Clickable alerts navigate to relevant pages
- **Frontend**: `/alerts` - Expiration alerts dashboard

### Phase 6: Analytics Dashboard ✅ (NEW)
- **Backend**: `/api/dashboard/analytics` endpoint
- **Features**:
  - Overview stats (forms, proposals, contracts, certificates)
  - Conversion funnel (form→proposal→contract rates)
  - Revenue overview (quoted, accepted, invoiced, collected)
  - Monthly trends chart (last 6 months)
  - Standards breakdown
  - Audit statistics
- **Frontend**: `/analytics` - Comprehensive analytics dashboard

### Auditor Management System ✅ (February 2026)
- **Full CRUD Operations**: Create, Read, Update, Delete (soft delete) auditors
- **API Endpoints**: 
  - `GET /api/auditors` - List all auditors with filtering
  - `POST /api/auditors` - Create new auditor
  - `GET /api/auditors/{id}` - Get auditor details
  - `PUT /api/auditors/{id}` - Update auditor
  - `DELETE /api/auditors/{id}` - Soft delete (status -> inactive)
  - `POST /api/auditors/{id}/availability` - Set auditor availability
- **Frontend Page**: `/auditors` - Complete management UI
  - Stats cards: Total Auditors, Active Auditors, Lead Auditors, Active Assignments
  - Search and filter by status/specialization
  - Add/Edit auditor modal with all fields
  - Set availability modal
  - Auditor cards with full details
- **Data Fields**: name, name_ar, email, phone, mobile, employee_id, certification_level (trainee/auditor/lead_auditor/technical_expert), specializations (ISO standards), years_experience, max_audits_per_month, notes
- **Full Bilingual Support**: Arabic/English translations with RTL layout
- **Test Report**: `/app/test_reports/iteration_20.json` - 100% passed (Backend: 14/14, Frontend: All UI working)

### PDF Layout Fixes ✅
- **Overlapping Text Fix** - Fixed bilingual PDF layout in Forms and Quotations tabs:
  - English labels at X=50, values at X=145 (left side)
  - Arabic values at X=width-160, labels at X=width-50 (right side)
  - Clear column separation prevents text overlap
- **Company Seal Fix** - Fixed seal cutoff in Quotation PDFs:
  - Seal Y-position now uses `max(y - 80, 55)` to ensure minimum 55px above footer
  - Seal dimensions: 80x80 pixels, centered horizontally
- **Arabic Text Rendering** - All Arabic text renders correctly using Amiri font (no black boxes)
- **Test Report**: `/app/test_reports/iteration_18.json` - 11/11 tests passed (100%)

### Important Notes Section Fix ✅ (December 2025)
- **Arabic Header Fix** - Fixed "ملاحظات هامة" rendering as square boxes:
  - Split header into separate English (Helvetica-Bold) and Arabic (Amiri-Bold) parts
  - Arabic text now properly right-aligned with correct font
- **Notes Content Alignment** - Fixed mismatch between English and Arabic notes:
  - Added missing 4th Arabic bullet point for contact information
  - All 4 notes now correspond side-by-side (English left, Arabic right)
  - Contact line "للاستفسارات، تواصل معنا على" now matches English equivalent

### Audit Program (BACF6-05) Feature ✅ (NEW - Feb 2026)
- **Purpose**: Schedule audit stages (Stage 1, Stage 2, Surveillance 1 & 2, Recertification)
- **Backend API Endpoints**:
  - `GET /api/audit-programs` - List all audit programs
  - `POST /api/audit-programs` - Create from completed contract review
  - `GET /api/audit-programs/{id}` - Get specific program
  - `PUT /api/audit-programs/{id}` - Update activities and approval
  - `DELETE /api/audit-programs/{id}` - Delete program
  - `GET /api/audit-programs/{id}/pdf` - Generate bilingual PDF
  - `POST /api/audit-programs/{id}/approve` - Approve program
- **Frontend Page**: `/audit-programs` - Admin management page
  - Stats cards (Total, Draft, Approved, Completed)
  - Programs table with organization, standards, activities count, status
  - Create modal (select from completed contract reviews)
  - Edit modal with full activities table
- **Activities Table Columns**: Activity, Audit Type, Stage 1, Stage 2, SUR 1, SUR 2, RC, Planned Date
- **Default Activities**: Document Review, Opening Meeting, Management Review, Process Audits, Internal Audit Review, Closing Meeting
- **PDF Generator**: `/app/backend/audit_program_generator.py` - Bilingual PDF using ReportLab
- **Workflow**: Contract Review (BACF6-04) → Audit Program (BACF6-05)
- **Test File**: `/app/backend/tests/test_audit_programs.py`
- **Test Report**: `/app/test_reports/iteration_23.json` - 100% pass rate

### Job Order (BACF6-06) Feature ✅ (NEW - Feb 2026)
- **Purpose**: Auditor appointment with internal approval and auditor confirmation
- **Workflow**: 
  1. Admin creates Job Order from approved Audit Program
  2. Admin selects auditor from system's registered auditors
  3. Certification Manager approves the job order
  4. System generates confirmation link
  5. Auditor receives link, reviews details, confirms or declines with reason
- **Backend API Endpoints**:
  - `POST /api/job-orders` - Create from audit program with auditor assignment
  - `GET /api/job-orders` - List all job orders
  - `GET /api/job-orders/{id}` - Get specific job order
  - `PUT /api/job-orders/{id}` - Update job order
  - `DELETE /api/job-orders/{id}` - Delete job order
  - `POST /api/job-orders/{id}/approve` - Manager approval
  - `POST /api/job-orders/{id}/send-to-auditor` - Generate confirmation link
  - `GET /api/job-orders/{id}/pdf` - Generate bilingual PDF
  - `GET /api/public/job-orders/{token}` - Public access for auditor
  - `POST /api/public/job-orders/{token}/confirm` - Auditor confirms/declines
- **Frontend Pages**:
  - `/job-orders` - Admin management page with stats, table, create/view modals
  - `/job-order-confirm/:accessToken` - Public auditor confirmation page
- **Status Flow**: pending_approval → approved → pending_auditor → confirmed/rejected
- **PDF Generator**: `/app/backend/job_order_generator.py` - Bilingual PDF with declaration
- **Test File**: `/app/backend/tests/test_job_orders.py`
- **Test Report**: `/app/test_reports/iteration_24.json` - 100% pass rate

### Stage 1 Audit Plan (BACF6-07) Feature ✅ (NEW - Feb 2026)
- **Purpose**: Initial certification audit planning (Phase 1)
- **Workflow**:
  1. Admin creates Stage 1 Plan from confirmed Job Order
  2. Team Leader auto-populated from Job Order's auditor
  3. Admin can add additional team members from system auditors
  4. Admin fills schedule table (Date/Time, Process, Owner, Clauses, Auditor)
  5. Manager internal approval
  6. Send to client for review via public link
  7. Client accepts plan OR requests changes with reason
- **Backend API Endpoints**:
  - `POST /api/stage1-audit-plans` - Create from confirmed job order
  - `GET /api/stage1-audit-plans` - List all plans
  - `PUT /api/stage1-audit-plans/{id}` - Update plan details
  - `DELETE /api/stage1-audit-plans/{id}` - Delete plan
  - `POST /api/stage1-audit-plans/{id}/manager-approve` - Manager approval
  - `POST /api/stage1-audit-plans/{id}/send-to-client` - Send for client review
  - `GET /api/stage1-audit-plans/{id}/pdf` - Generate bilingual PDF
  - `GET /api/public/stage1-audit-plans/{token}` - Public client access
  - `POST /api/public/stage1-audit-plans/{token}/respond` - Client accept/request changes
- **Frontend Pages**:
  - `/stage1-audit-plans` - Admin page with stats, table, create/edit modals
  - `/stage1-plan-review/:accessToken` - Public client review page
- **Status Flow**: draft → pending_manager → manager_approved → pending_client → client_accepted/changes_requested
- **PDF Generator**: `/app/backend/stage1_audit_plan_generator.py` - Bilingual PDF with objectives, team, schedule
- **Test Report**: `/app/test_reports/iteration_25.json` - 100% pass rate (17/17 backend tests)

### Stage 2 Audit Plan (BACF6-08) Feature ✅ (NEW - Feb 2026)
- **Purpose**: Certification audit - Phase 2 planning
- **Workflow**:
  1. Admin creates Stage 2 Plan from either an accepted Stage 1 plan OR a confirmed Job Order
  2. Admin fills schedule table (Date/Time, Process, Owner, Clauses, Auditor)
  3. Admin can add additional team members
  4. Manager internal approval
  5. Send to client for review via public link
  6. Client accepts plan OR requests changes with reason
- **Backend API Endpoints**:
  - `POST /api/stage2-audit-plans` - Create from Stage 1 plan or job order
  - `GET /api/stage2-audit-plans` - List all plans
  - `GET /api/stage2-audit-plans/{id}` - Get specific plan
  - `PUT /api/stage2-audit-plans/{id}` - Update plan details
  - `DELETE /api/stage2-audit-plans/{id}` - Delete plan
  - `POST /api/stage2-audit-plans/{id}/manager-approve` - Manager approval
  - `POST /api/stage2-audit-plans/{id}/send-to-client` - Send for client review
  - `GET /api/stage2-audit-plans/{id}/pdf` - Generate bilingual PDF
  - `GET /api/public/stage2-audit-plans/{token}` - Public client access
  - `POST /api/public/stage2-audit-plans/{token}/respond` - Client accept/request changes
- **Frontend Pages**:
  - `/stage2-audit-plans` - Admin page with stats, table, create/edit modals
  - `/stage2-plan-review/:accessToken` - Public client review page
- **Status Flow**: draft → pending_manager → manager_approved → pending_client → client_accepted/changes_requested
- **PDF Generator**: `/app/backend/stage2_audit_plan_generator.py` - Bilingual PDF with Stage 2 objectives, team, schedule
- **Stage 2 Audit Objectives Included**:
  - Verify conformity to all requirements of the applicable management system standard
  - Performance monitoring, measuring, reporting and reviewing against key performance objectives
  - Organization's management system and performance as regards legal compliance
  - Operational control of the Organization's processes
  - Internal auditing and management review effectiveness
  - Management responsibility for the Organization's policies
  - Review of actions taken on nonconformities from previous audit
  - Treatment of complaints and continual improvement demonstration
- **Test Report**: `/app/test_reports/iteration_26.json` - 100% pass rate (21/21 backend tests, 100% frontend)

### Opening & Closing Meeting (BACF6-09) Feature ✅ (NEW - Feb 2026)
- **Purpose**: Audit meeting attendance records - sent to client after Stage 1 audit
- **Workflow**:
  1. Admin creates meeting form from a client-accepted Stage 1 plan
  2. Admin sends the form to the client via public link
  3. Client fills in the attendee list (name, designation, opening meeting date, closing meeting date)
  4. Client adds opening and closing meeting notes
  5. Client submits the form
- **Backend API Endpoints**:
  - `POST /api/opening-closing-meetings` - Create from Stage 1 plan
  - `GET /api/opening-closing-meetings` - List all meetings
  - `GET /api/opening-closing-meetings/{id}` - Get specific meeting
  - `DELETE /api/opening-closing-meetings/{id}` - Delete meeting
  - `POST /api/opening-closing-meetings/{id}/send-to-client` - Send for client filling
  - `GET /api/opening-closing-meetings/{id}/pdf` - Generate bilingual PDF
  - `GET /api/public/opening-closing-meetings/{token}` - Public client access
  - `POST /api/public/opening-closing-meetings/{token}/submit` - Client submits form
- **Frontend Pages**:
  - `/opening-closing-meetings` - Admin page with stats, table, create/view modals
  - `/meeting-form/:accessToken` - Public client form page with attendees table
- **Status Flow**: pending → sent_to_client → submitted
- **PDF Generator**: `/app/backend/opening_closing_meeting_generator.py` - Bilingual PDF with attendees table
- **Test Report**: `/app/test_reports/iteration_27.json` - 100% pass rate (16/16 backend tests, 100% frontend)

### Stage 1 Audit Report (BACF6-10) Feature ✅ (NEW - Feb 2026)
- **Purpose**: Comprehensive audit findings and recommendations after Stage 1 audit
- **Workflow**:
  1. Admin creates audit report from client-accepted Stage 1 plan (optionally links meeting form)
  2. Admin fills: Change details, Positive findings, Areas of concern (with rating 1-3)
  3. Admin completes Team Leader Declarations checklist
  4. Admin selects Recommendation (Proceed to Stage 2 / Not proceed / Further Stage 1)
  5. Admin fills Audit Checklist (C/NC/O status for each requirement)
  6. Admin marks report as Complete
  7. Admin approves the report
- **Backend API Endpoints**:
  - `POST /api/stage1-audit-reports` - Create from Stage 1 plan
  - `GET /api/stage1-audit-reports` - List all reports
  - `GET /api/stage1-audit-reports/{id}` - Get specific report
  - `PUT /api/stage1-audit-reports/{id}` - Update report details
  - `DELETE /api/stage1-audit-reports/{id}` - Delete report
  - `POST /api/stage1-audit-reports/{id}/complete` - Mark as completed
  - `POST /api/stage1-audit-reports/{id}/approve` - Approve report
  - `GET /api/stage1-audit-reports/{id}/pdf` - Generate bilingual PDF
- **Frontend Pages**:
  - `/stage1-audit-reports` - Admin page with stats, table, create/edit modals
- **Status Flow**: draft → completed → approved
- **PDF Generator**: `/app/backend/stage1_audit_report_generator.py` - Comprehensive bilingual PDF with:
  - Organization details, audit team, duration
  - Change details section
  - Attendance sheet
  - Positive findings and Areas of concern tables with ratings
  - Team leader declaration checkboxes
  - Recommendation section (color-coded)
  - Audit checklist with C/NC/O status
- **Key Features**:
  - 14 pre-populated checklist items (legal requirements, documentation, scope, etc.)
  - Rating system: 1=OFI, 2=Probable NC in Stage 2, 3=Not Ready
  - Automatic import of data from Stage 1 plan and contract review

### Stage 2 Audit Report (BACF6-11) Feature ✅ (NEW - Feb 2026)
- **Purpose**: Comprehensive Stage 2 audit findings and certification recommendation
- **Workflow**:
  1. Admin creates audit report from client-accepted Stage 2 plan (optionally links Stage 1 report)
  2. Admin fills: Change details, Positive findings, Opportunities for Improvement (OFI)
  3. Admin records Nonconformities with rating (1=Minor NC, 2=Major NC)
  4. Admin selects Certification Recommendations (checkboxes):
     - Issuance of certificate, Use of BAC & EGAC Logo, Refusal, Post audit, Modification, Other
  5. Admin selects Overall Recommendation:
     - System complies - RECOMMENDED for certification
     - Minor NC - Corrective action required
     - Major NC - Corrective action within 90 days
     - Not Recommended for certification
  6. Admin fills Audit Checklist (28 ISO clause-based items)
  7. Admin marks report as Complete → Approve
- **Backend API Endpoints**:
  - `POST /api/stage2-audit-reports` - Create from Stage 2 plan
  - `GET /api/stage2-audit-reports` - List all reports
  - `GET /api/stage2-audit-reports/{id}` - Get specific report
  - `PUT /api/stage2-audit-reports/{id}` - Update report details
  - `DELETE /api/stage2-audit-reports/{id}` - Delete report
  - `POST /api/stage2-audit-reports/{id}/complete` - Mark as completed
  - `POST /api/stage2-audit-reports/{id}/approve` - Approve report
  - `GET /api/stage2-audit-reports/{id}/pdf` - Generate bilingual PDF
- **Frontend Pages**:
  - `/stage2-audit-reports` - Admin page with stats, table, create/edit modals
- **Status Flow**: draft → completed → approved
- **PDF Generator**: `/app/backend/stage2_audit_report_generator.py` - Comprehensive bilingual PDF with:
  - Organization details, audit team, duration
  - Positive findings, OFI, and Nonconformities tables
  - Certification recommendation checkboxes
  - Color-coded overall recommendation section
  - 28-item ISO clause-based checklist (clauses 4-10)
- **Key Differences from Stage 1**:
  - Nonconformities instead of Areas of Concern
  - Rating: 1=Minor NC, 2=Major NC (vs 1-3 scale in Stage 1)
  - Certification recommendation checkboxes (issue, use logo, refuse, etc.)
  - Overall recommendation for certification decision

### Auditor Notes (BACF6-12) Feature ✅ (NEW - Feb 2026)
- **Purpose**: Notes recorded by auditors after conducting audits
- **Workflow**:
  1. Auditor creates notes after completing Stage 2 audit report
  2. Notes can be created from an approved Stage 2 report (auto-fills client info) OR manually
  3. Can be used for any audit type (Stage 1, Stage 2, Surveillance, Recertification)
  4. Auditor records observations, findings, and comments
  5. Notes can be marked as "draft" or "completed"
- **Form Fields**:
  - Client Name (اسم العميل)
  - Location (الموقع)
  - Standard(s) (المعايير)
  - Auditor (المدقق)
  - Type of Audit (نوع التدقيق)
  - Audit Date (تاريخ التدقيق)
  - Department (القسم)
  - Notes (ملاحظات المدقق) - main content area
- **Backend API Endpoints**:
  - `POST /api/auditor-notes` - Create notes (from Stage 2 report or manually)
  - `GET /api/auditor-notes` - List all notes
  - `GET /api/auditor-notes/{id}` - Get specific notes
  - `PUT /api/auditor-notes/{id}` - Update notes
  - `DELETE /api/auditor-notes/{id}` - Delete notes
  - `POST /api/auditor-notes/{id}/complete` - Mark as completed
  - `GET /api/auditor-notes/{id}/pdf` - Generate bilingual PDF
- **Frontend Pages**:
  - `/auditor-notes` - Admin page with stats, table, create/edit modals
- **Status Flow**: draft → completed
- **PDF Generator**: `/app/backend/auditor_notes_generator.py` - Bilingual PDF with:
  - Client information header
  - Audit details (type, date, department)
  - Main notes content section
  - Arabic text support

### Nonconformity Report (BACF6-13) Feature ✅ (NEW - Feb 2026)
- **Purpose**: Track and manage audit nonconformities, corrections, and corrective actions
- **Workflow**:
  1. Admin/Auditor creates NC report from Stage 2 report (imports NCs) OR manually
  2. Each NC item includes: Standard clause, Description, NC type (Major/Minor), Root cause
  3. Client provides: Corrections (immediate fixes), Corrective actions (long-term)
  4. Auditor verifies and records decision for each NC
  5. Verification options include: Appropriate, Verified, Next audit, Re-audit
  6. Report can be closed when all NCs are addressed
- **Form Fields**:
  - Client Name, Certificate No., Standard(s)
  - Type of Audit, Date of Audit, Lead Auditor
  - Management Representative
  - Nonconformities table with: Clause, Description, Type (MJ/MN), Root Cause, Corrections, Corrective Actions, Verification
  - Submission Deadline
  - Verification Options (checkboxes)
  - Signature sections
- **Backend API Endpoints**:
  - `POST /api/nonconformity-reports` - Create NC report
  - `GET /api/nonconformity-reports` - List all reports
  - `GET /api/nonconformity-reports/{id}` - Get specific report
  - `PUT /api/nonconformity-reports/{id}` - Update report
  - `DELETE /api/nonconformity-reports/{id}` - Delete report
  - `POST /api/nonconformity-reports/{id}/add-nc` - Add nonconformity
  - `PUT /api/nonconformity-reports/{id}/nc/{nc_id}` - Update NC
  - `DELETE /api/nonconformity-reports/{id}/nc/{nc_id}` - Delete NC
  - `POST /api/nonconformity-reports/{id}/close` - Close report
  - `GET /api/nonconformity-reports/{id}/pdf` - Generate PDF
- **Frontend Pages**:
  - `/nonconformity-reports` - Admin page with stats (Total, Open, Closed, Major NCs, Minor NCs)
  - Create/Edit modals for reports and individual NCs
  - View modal with full NC details
- **Status Flow**: draft → sent_to_client → pending_verification → closed
- **PDF Generator**: `/app/backend/nonconformity_report_generator.py` - Bilingual PDF with:
  - Header with client info and audit details
  - NC summary (Major/Minor counts)
  - Detailed NC table with color-coded types
  - Verification options checkboxes
  - Signature section

## Backend Refactoring (February 2026) - IN PROGRESS

### Completed Modular Extraction
The following components have been extracted from the monolithic `server.py`:

**Shared Modules:**
- `/app/backend/database.py` - MongoDB connection configuration
- `/app/backend/auth.py` - JWT authentication utilities
- `/app/backend/utils/email.py` - Email sending functions

**Pydantic Models (`/app/backend/models/`):**
- `user.py`, `application_form.py`, `proposal.py`, `agreement.py`
- `contract_review.py`, `job_order.py`, `audit_plan.py`, `meeting.py`
- `audit_report.py`, `certificate.py`, `auditor.py`, `invoice.py`
- `notification.py`, `template.py`, `document.py`, `site.py`
- `audit_schedule.py`, `contact.py`

**Route Modules - ACTIVE (`/app/backend/routes/`):**
The following routes are now being used by the application (imported in server.py):
- `auth.py` - Authentication endpoints (/api/auth/login, /api/auth/register, /api/auth/me)
- `notifications.py` - Notification endpoints (/api/notifications)
- `sites.py` - Site management endpoints (/api/sites)
- `contacts.py` - Contact history endpoints (/api/contacts)
- `documents.py` - Document management endpoints (/api/documents)

**Route Modules - INACTIVE (exist but not wired up):**
- `auditors.py` - Auditor management endpoints (using monolith version for now - has more complex business logic)
- `certificates.py` - Certificate endpoints (using monolith version - depends on helper functions)
- `templates.py` - Template management endpoints (using monolith version)
- `public_verify.py` - Public certificate verification (using monolith version)

**Architecture Documentation:**
- `/app/backend/ARCHITECTURE.md` - Complete refactoring guide and migration plan

### Refactoring Progress
- **Server.py Line Count**: Reduced from 9,161 to 8,915 lines (~246 lines extracted)
- **Modules Migrated**: 5 (auth, notifications, sites, contacts, documents)
- **Status**: ACTIVE - Routes are being used by the application

### Remaining Migration Tasks
- Application Forms routes
- Proposals routes
- Agreements routes
- Contract Reviews (BACF6-04) routes
- Audit Programs (BACF6-05) routes
- Job Orders (BACF6-06) routes
- Audit Plans (BACF6-07, BACF6-08) routes
- Meetings (BACF6-09) routes
- Audit Reports (BACF6-10, BACF6-11) routes
- Auditor Notes (BACF6-12) routes
- Non-Conformity Reports (BACF6-13) routes
- Certificate Data (BACF6-14) routes
- Reports & Analytics routes
- Integration routes (Calendar, SMS, Invoices)
- Auditors routes (complex, needs helper function migration)
- Certificates routes (complex, needs helper function migration)
- Templates routes

## Upcoming Tasks
- **Continue Modular Migration**: Migrate more routes incrementally from monolith
- **Phase 7: Multi-Level Approval Workflow** - Implement multi-step approval for contracts
- **Google Calendar Integration**: Pending user credentials (GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET)
- **Twilio SMS Integration**: Pending user credentials (TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER)

## Future Enhancements
- Enable real email sending (SendGrid integration)
- Customer Portal with login system
- Progressive Web App (PWA) for auditors
