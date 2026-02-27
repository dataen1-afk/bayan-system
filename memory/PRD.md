# Service Contract Management System - PRD

## Latest Update: Feb 27, 2026

### E2E Workflow Test - COMPLETED ✅ (Feb 27, 2026)

#### Full Workflow Tested Successfully:
1. ✅ Application Form Created (طلبات المنح)
2. ✅ Quote/Proposal Created (عروض الأسعار) - SAR 20,000 for ISO 27001:2022
3. ✅ Proposal Accepted (via public endpoint)
4. ✅ Certification Agreement Signed → Contract visible
5. ✅ Contract Review Created & Completed
6. ✅ Audit Program Created & Approved  
7. ✅ Job Order Created (assigned to Ahmed Al-Rashid)
8. ✅ Certificate Generated (CERT-2026-0001)

#### Bug Fixes Applied:
- Fixed RTL layout for "Auditor Workload Distribution" widget
- Fixed `create_notification()` to accept optional `title_ar`, `message_ar` params
- Fixed `generate_certificate_pdf()` call - updated to use new function signature (returns bytes)

#### Test Data Created:
- Company: شركة العلي للتقنية (Al-Ali Technology)
- Standard: ISO 27001:2022
- Contract Value: SAR 20,000
- Certificate Number: CERT-2026-0001
- Auditor: أحمد الراشد (Ahmed Al-Rashid)

### Current System Users (as of Feb 27, 2026):
1. Admin User (admin@test.com) - system_admin
2. Eslam Abdulaal (islam@ies.sa) - system_admin  
3. Test User (test@example.com) - auditor

---

## Original Problem Statement
Build a full-stack application for managing service contracts for Bayan for Verification and Conformity with the following workflow:
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

## Sidebar Simplification - COMPLETED ✅ (Feb 18, 2026)

### Summary
Simplified the admin sidebar by combining Stage 1 and Stage 2 audit items into single unified menu entries with tabbed navigation, and refactored all admin pages to use a shared AdminLayout component.

### Changes Made
1. **Combined Menu Items**:
   - "Stage 1 Audit Plans" + "Stage 2 Audit Plans" → "Audit Plans" (`/audit-plans`)
   - "Stage 1 Audit Reports" + "Stage 2 Audit Reports" → "Audit Reports" (`/audit-reports`)

2. **New Container Pages**:
   - `/app/frontend/src/pages/AuditPlansPage.js` - Container with Stage 1/Stage 2 tabs
   - `/app/frontend/src/pages/AuditReportsPage.js` - Container with Stage 1/Stage 2 tabs

3. **Tab Order Fixed for RTL**:
   - Stage 1 tab appears on the RIGHT in Arabic mode
   - Stage 2 tab appears on the LEFT in Arabic mode

4. **Sidebar Navigation Fixes**:
   - Fixed active item detection using `useLocation` hook
   - Fixed sidebar scroll position preservation when navigating
   - Dashboard menu item now shows in Arabic as "لوحة التحكم"

5. **Page Refactoring (Full Refactoring)**:
   - Removed duplicate header/sidebar from: InvoicesPage, AuditorsPage, CertificatesPage, ExpirationAlertsPage, AnalyticsDashboardPage, CreateProposalPage
   - All pages now use shared AdminLayout from App.js routing
   - Consistent sidebar across all admin pages

### Files Modified
- `/app/frontend/src/components/Sidebar.js` - Added location-based active detection, scroll preservation
- `/app/frontend/src/pages/InvoicesPage.js` - Removed duplicate header/sidebar
- `/app/frontend/src/pages/AuditorsPage.js` - Removed duplicate header/sidebar
- `/app/frontend/src/pages/CertificatesPage.js` - Removed duplicate header/sidebar
- `/app/frontend/src/pages/ExpirationAlertsPage.js` - Removed duplicate header/sidebar
- `/app/frontend/src/pages/AnalyticsDashboardPage.js` - Removed duplicate header/sidebar
- `/app/frontend/src/pages/CreateProposalPage.js` - Removed duplicate header/sidebar
- `/app/frontend/src/i18n.js` - Added "dashboard" translation key

### Testing Status
- ✅ Sidebar navigation works correctly
- ✅ Tab switching between Stage 1 and Stage 2 works
- ✅ RTL layout maintained correctly
- ✅ Scroll position preserved when navigating
- ✅ All refactored pages display correctly with shared sidebar
- ✅ Mobile sidebar works correctly (z-index fix applied Feb 19, 2026)

## Mobile Sidebar Bug Fix - COMPLETED ✅ (Feb 19, 2026)

### Issue
On mobile viewports, opening the sidebar caused a dark overlay to appear on top of the sidebar itself, blocking all menu item interactions.

### Root Cause
Z-index stacking order issue:
- Overlay element: `z-40`
- Sidebar element: `z-30` (lower than overlay)

### Fix Applied
Changed sidebar `z-index` from `z-30` to `z-50` in `/app/frontend/src/components/Sidebar.js`

### Testing
Verified with mobile viewport (375x812):
- Sidebar opens correctly
- Menu items are visible and clickable
- Navigation works as expected

## Deployment Health Check Fix - COMPLETED ✅ (Feb 19, 2026)

### Issue
Deployment health checks failing with 404 errors on `/health` and `/api/health` endpoints.

### Fix Applied
Added health check endpoints to `/app/backend/server.py`:
```python
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "contract-audit-hub"}

@app.get("/api/health")
async def api_health_check():
    return {"status": "healthy", "service": "contract-audit-hub"}
```

### Testing
Verified endpoint returns: `{"status":"healthy","service":"contract-audit-hub"}`

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
- **Login Page Redesign (Feb 2026)**: Professional split-screen design with Kingdom Centre Tower (Saudi landmark) background, gradient overlay, company stats, SAC accreditation badge, icons for form fields, show/hide password toggle
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

### Progressive Web App (PWA) ✅ (NEW - Feb 2026)
- **Purpose**: Enable auditors to use the app offline and install it on devices
- **Files Created**:
  - `/app/frontend/public/manifest.json` - PWA manifest with app metadata
  - `/app/frontend/public/service-worker.js` - Service worker for caching/offline
  - `/app/frontend/src/components/PWAInstallPrompt.js` - Install prompt banner component
- **Features**:
  - App installable on mobile/desktop devices
  - Offline capability with smart caching strategy
  - Push notification support (prepared for future use)
  - Standalone display mode (no browser chrome)
  - Theme color matching Bayan brand (#1e3a5f)
  - **Install Prompt Banner**: Shows on mobile devices with:
    - Bilingual text (Arabic/English)
    - Install and "Later" buttons
    - Benefits list (quick access, works offline, faster experience)
    - Smart dismissal (remembers for 7 days if dismissed)
    - Auto-detects if already installed
- **Service Worker Strategy**:
  - Static assets cached on install
  - Network-first for API calls (always fresh data)
  - Cache-first with background update for UI assets
  - Offline fallback to /portal
- **index.html Updates**:
  - Added manifest.json link
  - Added apple-touch-icon for iOS
  - Added apple-mobile-web-app-* meta tags
  - Updated theme-color to #1e3a5f
  - Updated title to "Bayan Auditing & Conformity"
- **Service Worker Registration**: Added in `/app/frontend/src/index.js`

### Customer Portal ✅ (REDESIGNED - Feb 2026)
- **Professional public-facing portal**: `/portal`
- **Hero Section**: Branded banner with SAC accreditation badge, call-to-action buttons, stats bar (500+ companies, 15+ years, 50+ auditors, 99% satisfaction)
- **Services Showcase**: 5 ISO certification services with icons, descriptions:
  - ISO 9001:2015 - Quality Management System
  - ISO 14001:2015 - Environmental Management System
  - ISO 45001:2018 - Occupational Health & Safety
  - ISO 22000:2018 - Food Safety Management System
  - ISO 27001:2022 - Information Security Management
- **Order Tracking**: Enhanced tracking with visual timeline (6 steps: Form Created → Submitted → Under Review → Proposal Accepted → Agreement Signed → Contract Ready)
- **Request for Quotation (RFQ) Form**: Company info, contact details, employee count, sites, standards checkboxes, message - submits to `/api/public/rfq`
- **FAQ Section**: 6 accordion-style Q&A about certification process, costs, validity, preparation
- **Contact Section**: Contact form + contact info (address, phone, email, hours) - submits to `/api/public/contact`
- **Footer**: Quick links, certification list, copyright
- **Login Page Update**: Added prominent Customer Portal link card for easy access
- **Full bilingual support**: English/Arabic with RTL layout

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

### Technical Review and Certification Decision (BAC-F6-15) ✅ (NEW - Feb 2026)
- **Purpose**: Comprehensive technical review checklist before making certification decision
- **Workflow**:
  1. Create technical review (from Stage 2 Audit Report or manually)
  2. Admin fills 22-item assessment checklist with Y/N and remarks
  3. Technical reviewer reviews and adds comments
  4. Make certification decision (Issue Certificate / Reject / Needs Further Review)
  5. Approval with signature
  6. **AUTO-CERTIFICATE GENERATION**: If decision is "issue_certificate" and approved, certificate is automatically created
- **Checklist Categories**: General, Application, Quotation, Man Days, Audit Team, Stage 1, Stage 2, Other
- **Backend API Endpoints**:
  - `POST /api/technical-reviews` - Create technical review (supports both Stage 2 link and manual)
  - `GET /api/technical-reviews` - List all reviews
  - `GET /api/technical-reviews/{id}` - Get specific review with checklist
  - `PUT /api/technical-reviews/{id}` - Update review and checklist items
  - `DELETE /api/technical-reviews/{id}` - Delete review
  - `POST /api/technical-reviews/{id}/make-decision` - Make certification decision
  - `POST /api/technical-reviews/{id}/approve` - Approve (auto-generates certificate if issue_certificate)
  - `GET /api/technical-reviews/{id}/pdf` - Generate bilingual PDF
- **Frontend Pages**:
  - `/technical-reviews` - Admin page with stats (Total, Draft, Under Review, Decision Made, Certificate Issued)
  - Create modal with "From Stage 2 Report" or "Manual Entry" modes
  - Edit modal with checklist table (Y/N dropdowns)
  - Decision modal with 3 radio options
  - Approve modal (shows auto-certificate message when applicable)
- **Status Flow**: draft → under_review → decision_made → approved → certificate_issued
- **PDF Generator**: `/app/backend/technical_review_generator.py` - Bilingual PDF with:
  - Client information header
  - Audit team details
  - Assessment checklist table
  - Technical review section
  - Certification decision with checkboxes
  - Approval signature section

### Customer Feedback (BAC-F6-16) ✅ (NEW - Feb 2026)
- **Purpose**: Customer satisfaction survey sent after audits to gather feedback
- **Workflow**:
  1. Admin creates feedback form (optionally linked to certificate)
  2. System generates **public link** for client access (no login required)
  3. Client completes survey with **13 questions** rated 1-5 stars (or N/A)
  4. System auto-calculates score as percentage
  5. Admin reviews feedback and adds comments
  6. Generate bilingual PDF report
- **Question Categories** (6):
  - BAC Office (3 questions)
  - Audit Preparation (2 questions)
  - Punctuality (1 question)
  - Audit (4 questions)
  - Ethics (2 questions)
  - Effectiveness (1 question)
- **Evaluation Formula**:
  - Score = (sum of ratings / (rated questions × 5)) × 100
  - Excellent: ≥90%, Good: 75-89%, Average: 60-74%, Unsatisfactory: <60%
- **Backend API Endpoints**:
  - `POST /api/customer-feedback` - Create feedback form
  - `GET /api/customer-feedback` - List all feedback
  - `GET /api/customer-feedback/{id}` - Get specific feedback
  - `PUT /api/customer-feedback/{id}` - Update feedback
  - `DELETE /api/customer-feedback/{id}` - Delete feedback
  - `POST /api/customer-feedback/{id}/review` - Mark as reviewed
  - `GET /api/customer-feedback/{id}/pdf` - Generate PDF
  - `GET /api/public/feedback/{token}` - Get form for client (no auth)
  - `POST /api/public/feedback/{token}/submit` - Submit feedback (no auth)
- **Frontend Pages**:
  - `/customer-feedback` - Admin page with stats (Total, Pending, Submitted, Reviewed, Avg Score)
  - `/feedback/{accessToken}` - Public page for client submission
  - Create/View/Review modals
  - Star rating component with N/A option
- **Status Flow**: pending → submitted → reviewed
- **PDF Generator**: `/app/backend/customer_feedback_generator.py` - Bilingual PDF with:
  - Client and audit information
  - Question ratings with visual indicators
  - Overall score with evaluation badge
  - Suggestions and respondent info
  - Internal review section

### Pre-Transfer Review (BAC-F6-17) ✅ (NEW - Feb 2026)
- **Purpose**: Evaluate certificate transfer requests from clients moving from another certification body
- **Workflow**:
  1. Admin creates transfer review for a client requesting to transfer their certification
  2. Fills in client information (name EN/AR, address, phone, enquiry reference)
  3. Records transfer details (reason, existing CB, certificate number, validity, scope, sites, EAC code)
  4. Completes compliance checklist (8 items)
  5. Makes transfer decision (approve/reject)
  6. Generates bilingual PDF report
- **Compliance Checklist Items**:
  - Certificate under suspension?
  - Under threat of suspension?
  - Any minor non-conformity outstanding?
  - Any major non-conformity outstanding?
  - Engaged in legal representation?
  - Complaints appropriately handled?
  - Activities within BAC accreditation scope?
  - Previous assessment reports available?
- **Backend API Endpoints**:
  - `POST /api/pre-transfer-reviews` - Create transfer review
  - `GET /api/pre-transfer-reviews` - List all reviews (optional status filter)
  - `GET /api/pre-transfer-reviews/{id}` - Get specific review
  - `PUT /api/pre-transfer-reviews/{id}` - Update review (including checklist)
  - `DELETE /api/pre-transfer-reviews/{id}` - Delete review
  - `POST /api/pre-transfer-reviews/{id}/make-decision` - Set decision (approved/rejected)
  - `GET /api/pre-transfer-reviews/{id}/pdf` - Generate bilingual PDF
- **Frontend Page**: `/pre-transfer-reviews`
  - Stats cards (Total, Draft, Pending, Approved, Rejected)
  - Data table with all transfer requests
  - Create modal with client info and transfer details
  - Edit modal with checklist Yes/No/N/A dropdowns
  - Decision modal with approval/rejection options
  - PDF download button
- **Status Flow**: draft → under_review → decision_made
- **PDF Generator**: `/app/backend/pre_transfer_review_generator.py` - Bilingual PDF with:
  - Client information (English and Arabic)
  - Transfer details and reason
  - Compliance checklist results
  - Decision and reviewer information

### Certified Clients Registry (BAC-F6-19) ✅ (NEW - Feb 2026)
- **Purpose**: Central registry to track all certified clients with their certificate information
- **Data Structure** (from original Excel template):
  - S.No. (auto-incremented serial number)
  - Client Information: name (EN/AR), address, contact person, phone
  - Certification Details: scope, accreditation standards, EA code/food category
  - Certificate Details: certificate number, issue date, expiry date
  - Audit Schedule: surveillance 1 date, surveillance 2 date, recertification date
  - Status: active, suspended, withdrawn, expired
- **Backend API Endpoints**:
  - `GET /api/certified-clients` - List all clients (with status filter)
  - `POST /api/certified-clients` - Add new client record
  - `GET /api/certified-clients/{id}` - Get single client details
  - `PUT /api/certified-clients/{id}` - Update client record
  - `DELETE /api/certified-clients/{id}` - Delete client record
  - `GET /api/certified-clients/stats/overview` - Dashboard statistics
  - `POST /api/certified-clients/sync-from-certificates` - Auto-sync from system certificates
  - `GET /api/certified-clients/export/excel` - Export to Excel (XLSX)
  - `GET /api/certified-clients/{id}/pdf` - Generate PDF for single client
- **Frontend Page**: `/certified-clients`
  - Stats cards: Total, Active, Expiring Soon, Expired, Surv. 1 Due, Surv. 2 Due
  - Filterable data table with all clients
  - Create modal with all fields (client info, certification details, dates)
  - View modal with grouped details display
  - Edit modal with status change and notes
  - Action buttons: View, Edit, Download PDF, Delete
  - Export buttons: Excel (full registry), Sync from Certificates
- **Auto-Expiry**: System automatically marks certificates as expired when expiry_date < today
- **PDF Generator**: `/app/backend/certified_clients_generator.py` - Bilingual PDF with:
  - Company header with logo area
  - Certificate number and status badge
  - Client information section
  - Certification details (scope, standards, EA code)
  - Important dates (issue, expiry, surveillance, recertification)
- **Excel Export**: Professional XLSX with styled headers and full client data

### Suspended Clients Registry (BAC-F6-20) ✅ (NEW - Feb 2026)
- **Purpose**: Track all clients whose certifications have been suspended with full lifecycle management
- **Data Structure** (from original Excel template):
  - Sr. No. (auto-incremented serial number)
  - Client ID, Client Name (EN/AR), Address
  - Date of Registration (original certification date)
  - Suspended On (suspension date)
  - Reason for Suspension
  - Future Action (reinstate, withdraw, extend_suspension, under_review)
  - Remarks
  - Status: suspended, reinstated, withdrawn
- **Backend API Endpoints**:
  - `GET /api/suspended-clients` - List all clients (with status filter)
  - `POST /api/suspended-clients` - Add new suspended client record
  - `GET /api/suspended-clients/{id}` - Get single client details
  - `PUT /api/suspended-clients/{id}` - Update client record
  - `DELETE /api/suspended-clients/{id}` - Delete client record
  - `GET /api/suspended-clients/stats/overview` - Dashboard statistics
  - `POST /api/suspended-clients/{id}/lift-suspension` - Reinstate or withdraw certification
  - `POST /api/suspended-clients/sync-from-certified` - Sync from certified clients with suspended status
  - `GET /api/suspended-clients/export/excel` - Export to Excel (XLSX)
  - `GET /api/suspended-clients/{id}/pdf` - Generate PDF for single client
- **Frontend Page**: `/suspended-clients`
  - Stats cards: Total, Suspended, Reinstated, Withdrawn, Pending Reinstate, Under Review
  - Filterable data table with all suspended clients
  - Create modal with option to link from certified clients
  - View modal showing suspension and resolution details
  - Edit modal for updating suspension details
  - Lift Suspension modal with reinstate/withdraw options
  - Action buttons: View, Edit, Lift, Download PDF, Delete
  - Export buttons: Excel (full registry), Sync from Certified
- **Lift Suspension Workflow**:
  - Admin can lift suspension with two options: Reinstate or Withdraw
  - Records lifted_on date and reason
  - Automatically updates linked certified client status
- **PDF Generator**: `/app/backend/suspended_clients_generator.py` - Bilingual PDF with:
  - Red-themed header indicating suspension
  - Large status badge (Suspended/Reinstated/Withdrawn)
  - Client information section
  - Suspension details (date, reason, future action)
  - Resolution details (if lifted)

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
- **COMPLETED: Backend Modular Refactoring (Feb 18, 2026)** ✅
- **Phase 7: Multi-Level Approval Workflow** - Implement multi-step approval for contracts
- **Admin Pages for Portal Forms**: Create admin pages to view/manage RFQ and Contact messages
- **Google Calendar Integration**: Pending user credentials (GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET)
- **Twilio SMS Integration**: Pending user credentials (TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER)

## Backend Modular Refactoring - COMPLETED ✅ (Feb 18, 2026)

### Summary
Successfully refactored the monolithic `server.py` (originally 10,964 lines) into modular route files, reducing it to 8,955 lines (a reduction of 2,009 lines).

### New Modular Route Files Created
1. **`/app/backend/routes/technical_reviews.py`** (428 lines)
   - BAC-F6-15 Technical Review endpoints
   - Certification decision workflow
   - PDF generation

2. **`/app/backend/routes/customer_feedback.py`** (283 lines)
   - BAC-F6-16 Customer Feedback endpoints
   - Admin CRUD operations
   - Score calculation
   - PDF generation

3. **`/app/backend/routes/customer_feedback_public.py`** (131 lines)
   - Public feedback submission endpoints (no auth required)
   - Token-based access for clients

4. **`/app/backend/routes/pre_transfer_reviews.py`** (283 lines)
   - BAC-F6-17 Pre-Transfer Review endpoints
   - Transfer decision workflow
   - PDF generation

5. **`/app/backend/routes/certified_clients.py`** (390 lines)
   - BAC-F6-19 Certified Clients Registry endpoints
   - CRUD operations
   - Excel export
   - Sync from certificates
   - Statistics

6. **`/app/backend/routes/suspended_clients.py`** (416 lines)
   - BAC-F6-20 Suspended Clients Registry endpoints
   - CRUD operations
   - Lift suspension workflow
   - Excel export
   - Sync from certified clients
   - Statistics

7. **`/app/backend/routes/portal.py`** (182 lines)
   - Customer Portal public endpoints
   - RFQ form submission
   - Contact form submission
   - Admin management endpoints for RFQ and Contact messages

8. **`/app/backend/dependencies.py`** (135 lines)
   - Shared dependencies to avoid circular imports
   - Database connection
   - Authentication helpers (get_current_user, require_admin)
   - Notification helper (create_notification)
   - Certificate helpers (generate_certificate_number, get_qr_code_base64)
   - Shared Pydantic models (Notification, Certificate)

### Architecture Benefits
- **Modular Structure**: Each feature area has its own dedicated route file
- **No Circular Imports**: Shared dependencies in `dependencies.py`
- **Maintainability**: Easier to locate, modify, and test specific features
- **Code Reuse**: Common utilities centralized in dependencies
- **Reduced server.py**: Core server now only contains remaining routes and middleware

### API Endpoints - Modular Routes
All endpoints continue to work exactly as before:
- `GET/POST /api/technical-reviews` - Technical Reviews
- `GET/POST /api/customer-feedback` - Customer Feedback
- `GET/POST /api/public/feedback/{token}` - Public Feedback
- `GET/POST /api/pre-transfer-reviews` - Pre-Transfer Reviews
- `GET/POST /api/certified-clients` - Certified Clients
- `GET/POST /api/suspended-clients` - Suspended Clients
- `POST /api/public/rfq` - Public RFQ submission
- `POST /api/public/contact` - Public Contact submission
- `GET /api/rfq-requests` - Admin RFQ management
- `GET /api/contact-messages` - Admin Contact management

## Bilingual Notification System - COMPLETED ✅ (Feb 18, 2026)

### Summary
Updated the notification system to support bilingual content (English/Arabic). All new notifications now include both `title`/`message` (English) and `title_ar`/`message_ar` (Arabic) fields.

### Changes Made
1. **Backend (`dependencies.py`)**: Updated `Notification` model and `create_notification()` function to accept `title_ar` and `message_ar` parameters
2. **All Route Files**: Updated all `create_notification()` calls to include Arabic translations
3. **Frontend (`NotificationBell.js`)**: Updated to display Arabic title/message when UI is in Arabic mode (RTL)

### Notification Types with Arabic Support
- Form submissions
- Proposal acceptance/rejection
- Agreement signing
- Technical reviews
- Customer feedback
- Pre-transfer reviews
- Certified/Suspended clients
- RFQ and Contact form submissions

### Note
Existing notifications created before this update will continue to display in English. Only new notifications will show bilingual content.

## Admin Pages for Portal Forms - COMPLETED ✅ (Feb 18, 2026)

### Summary
Created two new admin pages to manage incoming RFQ requests and Contact messages from the customer portal.

### New Pages Created
1. **RFQ Requests Page** (`/rfq-requests`)
   - View all quote requests from the customer portal
   - Filter by status (New, In Progress, Quoted, Closed)
   - Search by company name or contact
   - Update request status
   - View detailed request information
   - Delete requests
   - Export to CSV
   - Statistics dashboard with counts by status

2. **Contact Messages Page** (`/contact-messages`)
   - View all contact messages from the customer portal
   - Filter by status (Unread, Read, Replied, Archived)
   - Search by name or subject
   - Update message status (auto-marks as read when opened)
   - Reply via email (opens email client)
   - Archive messages
   - Delete messages
   - Export to CSV
   - Statistics dashboard with counts by status

### Files Created
- `/app/frontend/src/pages/RFQRequestsPage.js` - RFQ management page
- `/app/frontend/src/pages/ContactMessagesPage.js` - Contact messages management page

### Updated Files
- `/app/frontend/src/App.js` - Added routes for new pages
- `/app/frontend/src/components/Sidebar.js` - Added navigation items
- `/app/frontend/src/i18n.js` - Added translations (English and Arabic)

### Features
- Full RTL support (Arabic)
- Bilingual interface
- Responsive design
- Real-time statistics
- CSV export functionality
- Status management workflow

## Phase 7: Multi-Level Approval Workflow - COMPLETED ✅ (Feb 18, 2026)

### Summary
Implemented a comprehensive multi-level approval workflow system for managing document approvals through multiple authorization levels.

### Features
1. **Configurable Approval Levels**
   - Support for 1-3+ approval levels per document type
   - Default configurations for: Contract Review, Job Order, Audit Plan, Technical Review, Certificate, Pre-Transfer

2. **Approval Roles**
   - Technical Reviewer (المراجع الفني)
   - Manager (المدير)
   - Certification Manager (مدير الشهادات)
   - Director (المدير العام)

3. **Workflow Status Tracking**
   - In Progress (قيد التنفيذ)
   - Approved (تمت الموافقة)
   - Rejected (مرفوض)
   - Cancelled (ملغي)

4. **Admin Dashboard**
   - Statistics overview (total, in-progress, approved, rejected, avg completion time)
   - Filter by status and document type
   - Search functionality
   - Visual approval progress indicator

5. **Approval Actions**
   - Approve with optional comments
   - Reject with optional comments
   - Automatic progression to next level
   - Source document status update on completion

### API Endpoints
- `GET /api/approvals` - List all approval workflows
- `GET /api/approvals/pending` - Get pending approvals for current user
- `GET /api/approvals/stats` - Get approval statistics
- `GET /api/approvals/configs` - Get default approval configurations
- `POST /api/approvals` - Create new approval workflow
- `GET /api/approvals/{id}` - Get specific workflow
- `POST /api/approvals/{id}/decide` - Submit approval/rejection decision
- `POST /api/approvals/{id}/cancel` - Cancel a workflow
- `DELETE /api/approvals/{id}` - Delete a workflow

### Files Created
- `/app/backend/routes/approvals.py` - Approval workflow backend routes
- `/app/frontend/src/pages/ApprovalsPage.js` - Approval management frontend page

### Bilingual Support
- Full RTL Arabic support
- All labels and messages in both English and Arabic
- Bilingual notifications for approval events

## Future Enhancements
- Enable real email sending (SendGrid integration)
- Customer Portal with login system

## Phase 8: Dashboard Analytics Widgets & Login Page Redesign - COMPLETED ✅ (Feb 18, 2026)

### Login Page Redesign (Dark Glass Design)
- **Full-screen desert background**: Custom AI-generated Saudi desert dunes image
- **Dark glassmorphism card**: Semi-transparent dark card with backdrop blur (`bg-[#1e3a5f]/40 backdrop-blur-xl`)
- **White enlarged logo**: Positioned in upper-right corner with inverted color filter
- **Powerful Arabic text**: "شريكك الموثوق في رحلة التميز المؤسسي" - centered on right side
- **Gold submit button**: Amber/gold colored button (#c9a55c) matching Bayan brand
- **Semi-transparent inputs**: White/10 background with white/30 borders
- **Remember me checkbox**: Right-aligned within the form
- **Demo credentials display**: Shows test login credentials
- **Customer portal link**: Quick access to public customer portal
- **Bilingual support**: Full Arabic/English with RTL layout

### Dashboard Analytics Widgets
New dashboard home screen with interactive widgets:

1. **Certificate Expiration Widget** (`data-testid="cert-expiration-widget"`)
   - Shows certificates expiring in 30/60/90 days
   - Color-coded urgency (red for 30 days, amber for 60, yellow for 90)
   - "View Details" button navigates to expiration alerts page

2. **Quick Actions Card** (`data-testid="quick-actions-widget"`)
   - Create Form - Opens form creation
   - Pending Approvals - Shows pending count badge, navigates to approvals
   - Audit Programs - Quick access to audit programs
   - Certificates - Quick access to certificates page

3. **Revenue Target Progress** (`data-testid="revenue-widget"`)
   - Monthly revenue display in SAR
   - Target amount (configurable, default 500,000 SAR)
   - Progress bar with percentage
   - Total revenue summary

4. **Today's Activity** (`data-testid="activity-widget"`)
   - New forms count
   - New proposals count
   - Recent notifications list

5. **Auditor Workload Chart** (`data-testid="auditor-workload-widget"`)
   - Visual bar chart showing task distribution
   - Per-auditor breakdown (job orders, stage 1, stage 2)
   - Color-coded progress bars
   - Arabic name support (name_ar)

### New API Endpoints
- `GET /api/dashboard/stats` - Comprehensive dashboard statistics
  - Returns: certificates (expiring counts), forms, proposals, approvals, revenue, auditor_workload, today_activity
- `GET /api/dashboard/quick-actions` - Quick action badge counts

### Files Created/Updated
- `/app/backend/routes/dashboard.py` - Dashboard analytics API
- `/app/frontend/src/components/DashboardWidgets.js` - Dashboard widgets component
- `/app/frontend/src/pages/AdminDashboard.js` - Integrated widgets, added dashboard tab as default
- `/app/frontend/src/components/Sidebar.js` - Added LayoutDashboard icon and dashboard menu item
- `/app/frontend/src/pages/LoginPage.js` - Complete redesign with dark glass effect

### Arabic Font Status
- **Font**: IBM Plex Sans Arabic (400, 500, 600, 700 weights)
- **Status**: Working correctly - no console errors
- **Setup**: Using @fontsource/ibm-plex-sans-arabic package
- **Note**: Previous handoff mentioned "Almarai" font issues - this was already resolved by using IBM Plex Sans Arabic instead

## Sidebar Simplification - COMPLETED ✅ (Feb 18, 2026)

### Summary
Simplified the admin sidebar by combining Stage 1 and Stage 2 audit items into single unified menu entries with tabbed navigation.

### Changes Made
1. **Combined Menu Items**:
   - "Stage 1 Audit Plans" + "Stage 2 Audit Plans" → "Audit Plans" (`/audit-plans`)
   - "Stage 1 Audit Reports" + "Stage 2 Audit Reports" → "Audit Reports" (`/audit-reports`)

2. **New Container Pages**:
   - `/app/frontend/src/pages/AuditPlansPage.js` - Container with Stage 1/Stage 2 tabs
   - `/app/frontend/src/pages/AuditReportsPage.js` - Container with Stage 1/Stage 2 tabs

3. **Tab Navigation**:
   - Both pages use shadcn/ui Tabs component
   - "المرحلة الأولى" (Stage 1) tab - shows Stage 1 content
   - "المرحلة الثانية" (Stage 2) tab - shows Stage 2 content
   - URL updates with `?stage=stage1` or `?stage=stage2` parameter

4. **Embedded Components**:
   - Existing Stage1/Stage2 page components embedded with `embedded={true}` prop
   - Hides individual page titles when embedded

### Files Modified
- `/app/frontend/src/components/Sidebar.js` - Removed separate Stage 1/2 items, kept combined items
- `/app/frontend/src/App.js` - Added routes for `/audit-plans` and `/audit-reports`
- `/app/frontend/src/pages/AuditPlansPage.js` - NEW
- `/app/frontend/src/pages/AuditReportsPage.js` - NEW

### Testing Status
- ✅ Sidebar navigation to `/audit-plans` works
- ✅ Sidebar navigation to `/audit-reports` works
- ✅ Tab switching between Stage 1 and Stage 2 works
- ✅ Content updates correctly when switching tabs
- ✅ RTL layout maintained correctly
- ✅ Full bilingual support (Arabic/English)



## PWA Install App Button - COMPLETED ✅ (Feb 19, 2026)

### Summary
Added a manual "Install App" button as a fallback option for PWA installation, plus new professional 3D PWA app icons.

### Features Implemented
1. **Install App Button in Customer Portal Header**
   - Visible on both mobile and desktop
   - Shows download icon with green border
   - On mobile: icon only (compact)
   - On desktop: icon + "تثبيت التطبيق" / "Install App" text
   - **Pulsing animation** on first visit to attract attention
   - **Tooltip hint** explaining the install feature (auto-dismisses after 6 seconds)

2. **Install App Button in Admin Dashboard Sidebar**
   - Positioned below main menu items, above Settings
   - Green download icon with text
   - Responsive: icon only when sidebar collapsed

3. **Professional Installation Guide Dialog**
   - Opens when clicking Install App button
   - Shows app benefits:
     - Quick access from home screen
     - Faster loading & performance
     - Full app-like experience
   - Device-specific installation instructions:
     - iOS: Share icon → Add to Home Screen
     - Android: Menu → Install app
     - Desktop: Install icon in address bar or browser menu
   - "Install Now" button (if browser supports native install)
   - Close button

4. **New PWA App Icons**
   - 3D design with rounded corners
   - Navy blue background (#1e3a5f)
   - White "B" fingerprint logo centered
   - Generated sizes: 192x192 and 512x512

### First-Time Visitor Experience
- Tooltip appears after 2 seconds on first visit
- Button pulses with green glow to attract attention
- Tooltip auto-dismisses after 6 seconds
- "Got it" button to manually dismiss
- State saved in localStorage (won't show again)

### Files Created/Modified
- `/app/frontend/src/components/InstallAppButton.js` - NEW component with pulsing + tooltip
- `/app/frontend/src/pages/CustomerPortalPage.js` - Added InstallAppButton to header
- `/app/frontend/src/components/Sidebar.js` - Added InstallAppButton to sidebar
- `/app/frontend/public/manifest.json` - Updated icon paths
- `/app/frontend/public/pwa-icon-192.png` - NEW 3D icon
- `/app/frontend/public/pwa-icon-512.png` - NEW 3D icon

### Technical Details
- Button hidden when app is already installed (uses `window.matchMedia('(display-mode: standalone)')`)
- Three variants: default (header), sidebar, sidebar-collapsed
- Full RTL support with isRTL prop
- Accessibility: Added DialogDescription for screen readers
- data-testid attributes for testing
- localStorage used to track first-visit tooltip state

### Testing Status
- ✅ Button visible in Customer Portal header (desktop & mobile)
- ✅ Button visible in Admin Dashboard sidebar
- ✅ Pulsing animation works on first visit
- ✅ Tooltip appears and auto-dismisses
- ✅ Installation dialog opens with benefits and steps
- ✅ Close button works correctly
- ✅ PWA icons accessible at correct URLs

