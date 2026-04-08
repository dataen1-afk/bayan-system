import React, { useState, useEffect } from 'react';
import '@/App.css';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import axios from 'axios';
import { Toaster, toast } from 'sonner';
import { Loader2 } from 'lucide-react';
import '@/i18n'; // Initialize i18n
import { useTranslation } from 'react-i18next';
import LoginPage from '@/pages/LoginPage';
import AdminDashboard from '@/pages/AdminDashboard';
import PublicFormPage from '@/pages/PublicFormPage';
import PublicProposalPage from '@/pages/PublicProposalPage';
import CreateProposalPage from '@/pages/CreateProposalPage';
import CertificationAgreementPage from '@/pages/CertificationAgreementPage';
import ReportsPage from '@/pages/ReportsPage';
import TemplatesPage from '@/pages/TemplatesPage';
import CustomerPortalPage from '@/pages/CustomerPortalPage';
import AuditSchedulingPage from '@/pages/AuditSchedulingPage';
import InvoicesPage from '@/pages/InvoicesPage';
import AuditorsPage from '@/pages/AuditorsPage';
import CertificatesPage from '@/pages/CertificatesPage';
import ExpirationAlertsPage from '@/pages/ExpirationAlertsPage';
import AnalyticsDashboardPage from '@/pages/AnalyticsDashboardPage';
import ContractReviewsPage from '@/pages/ContractReviewsPage';
import PublicContractReviewPage from '@/pages/PublicContractReviewPage';
import AuditProgramsPage from '@/pages/AuditProgramsPage';
import JobOrdersPage from '@/pages/JobOrdersPage';
import PublicJobOrderConfirmPage from '@/pages/PublicJobOrderConfirmPage';
import Stage1AuditPlansPage from '@/pages/Stage1AuditPlansPage';
import PublicStage1PlanReviewPage from '@/pages/PublicStage1PlanReviewPage';
import Stage2AuditPlansPage from '@/pages/Stage2AuditPlansPage';
import PublicStage2PlanReviewPage from '@/pages/PublicStage2PlanReviewPage';
import AuditPlansPage from '@/pages/AuditPlansPage';
import OpeningClosingMeetingsPage from '@/pages/OpeningClosingMeetingsPage';
import PublicMeetingFormPage from '@/pages/PublicMeetingFormPage';
import Stage1AuditReportsPage from '@/pages/Stage1AuditReportsPage';
import Stage2AuditReportsPage from '@/pages/Stage2AuditReportsPage';
import AuditReportsPage from '@/pages/AuditReportsPage';
import AuditorNotesPage from '@/pages/AuditorNotesPage';
import NonconformityReportsPage from '@/pages/NonconformityReportsPage';
import CertificateDataPage from '@/pages/CertificateDataPage';
import TechnicalReviewPage from '@/pages/TechnicalReviewPage';
import CustomerFeedbackPage from '@/pages/CustomerFeedbackPage';
import PublicFeedbackPage from '@/pages/PublicFeedbackPage';
import PublicCertificateDataConfirmPage from '@/pages/PublicCertificateDataConfirmPage';
import PreTransferReviewPage from '@/pages/PreTransferReviewPage';
import CertifiedClientsPage from '@/pages/CertifiedClientsPage';
import SuspendedClientsPage from '@/pages/SuspendedClientsPage';
import RFQRequestsPage from '@/pages/RFQRequestsPage';
import ContactMessagesPage from '@/pages/ContactMessagesPage';
import ApprovalsPage from '@/pages/ApprovalsPage';
import SettingsPage from '@/pages/SettingsPage';
import AdminLayout from '@/components/AdminLayout';
import { API } from '@/lib/apiConfig';

export { API };

// Set up axios defaults
axios.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Staff roles that can access admin pages
const STAFF_ROLES = [
  'system_admin', 'admin', 'ceo', 'general_manager',
  'quality_manager', 'certification_manager', 'operation_coordinator',
  'marketing_manager', 'financial_manager', 'hr_manager',
  'lead_auditor', 'auditor', 'technical_expert'
];

// Helper function to check if user is staff
const isStaff = (user) => user && STAFF_ROLES.includes(user.role);

export const AuthContext = React.createContext();

const DEBUG_BOOT = process.env.NODE_ENV === 'development';

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const { t, i18n } = useTranslation();

  // Mount-only bootstrap: avoid [i18n] deps (would re-run /auth/me if i18n instance identity changes).
  useEffect(() => {
    const t0 = typeof performance !== 'undefined' ? performance.now() : 0;
    if (DEBUG_BOOT) {
      console.info('[bayan-bootstrap] start');
    }

    const storedLang = localStorage.getItem('language') || 'ar';
    i18n.changeLanguage(storedLang);
    document.documentElement.dir = storedLang === 'ar' ? 'rtl' : 'ltr';
    document.documentElement.lang = storedLang;

    const token = localStorage.getItem('token');
    if (token) {
      if (DEBUG_BOOT) {
        console.info(`[bayan-bootstrap] auth/me request start (+${(performance.now() - t0).toFixed(0)}ms)`);
      }
      axios
        .get(`${API}/auth/me`)
        .then((response) => {
          setUser(response.data);
          if (DEBUG_BOOT) {
            console.info(`[bayan-bootstrap] auth/me ok (+${(performance.now() - t0).toFixed(0)}ms)`);
          }
        })
        .catch(() => {
          localStorage.removeItem('token');
          if (DEBUG_BOOT) {
            console.info(`[bayan-bootstrap] auth/me failed (+${(performance.now() - t0).toFixed(0)}ms)`);
          }
        })
        .finally(() => {
          setLoading(false);
          if (DEBUG_BOOT) {
            console.info(`[bayan-bootstrap] shell ready (+${(performance.now() - t0).toFixed(0)}ms)`);
          }
        });
    } else {
      setLoading(false);
      if (DEBUG_BOOT) {
        console.info(`[bayan-bootstrap] no token, shell ready (+${(performance.now() - t0).toFixed(0)}ms)`);
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps -- intentional one-shot bootstrap
  }, []);

  const login = (token, userData) => {
    localStorage.setItem('token', token);
    setUser(userData);
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
    toast.success(
      i18n.language?.startsWith('ar') ? 'تم تسجيل الخروج بنجاح' : 'Signed out successfully'
    );
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen gap-3 bg-slate-50 text-slate-600">
        <Loader2 className="h-10 w-10 animate-spin text-[#1e3a5f]" aria-hidden />
        <p className="text-lg">{t('loading')}</p>
      </div>
    );
  }

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      <div className="App">
        <Toaster richColors closeButton position="top-center" />
        <BrowserRouter>
          <Routes>
            {/* Public routes - no authentication required */}
            <Route path="/form/:accessToken" element={<PublicFormPage />} />
            <Route path="/proposal/:accessToken" element={<PublicProposalPage />} />
            <Route path="/agreement/:accessToken" element={<CertificationAgreementPage />} />
            <Route path="/contract-review/:accessToken" element={<PublicContractReviewPage />} />
            <Route path="/job-order-confirm/:accessToken" element={<PublicJobOrderConfirmPage />} />
            <Route path="/stage1-plan-review/:accessToken" element={<PublicStage1PlanReviewPage />} />
            <Route path="/stage2-plan-review/:accessToken" element={<PublicStage2PlanReviewPage />} />
            <Route path="/meeting-form/:accessToken" element={<PublicMeetingFormPage />} />
            <Route
              path="/certificate-data-confirm/:accessToken"
              element={<PublicCertificateDataConfirmPage />}
            />
            <Route path="/portal" element={<CustomerPortalPage />} />
            <Route path="/track" element={<CustomerPortalPage />} />
            <Route path="/track/:trackingId" element={<CustomerPortalPage />} />
            
            {/* Authenticated routes */}
            <Route path="/login" element={!user ? <LoginPage /> : <Navigate to="/dashboard" />} />
            <Route 
              path="/dashboard" 
              element={
                user ? <AdminDashboard /> : <Navigate to="/login" />
              } 
            />
            {/* Admin pages - wrapped with AdminLayout */}
            <Route 
              path="/invoices" 
              element={isStaff(user) ? <AdminLayout><InvoicesPage /></AdminLayout> : <Navigate to="/login" />} 
            />
            <Route 
              path="/auditors" 
              element={isStaff(user) ? <AdminLayout><AuditorsPage /></AdminLayout> : <Navigate to="/login" />} 
            />
            <Route 
              path="/settings" 
              element={isStaff(user) ? <AdminLayout><SettingsPage /></AdminLayout> : <Navigate to="/login" />} 
            />
            <Route 
              path="/certificates" 
              element={isStaff(user) ? <AdminLayout><CertificatesPage /></AdminLayout> : <Navigate to="/login" />} 
            />
            <Route 
              path="/alerts" 
              element={isStaff(user) ? <AdminLayout><ExpirationAlertsPage /></AdminLayout> : <Navigate to="/login" />} 
            />
            <Route 
              path="/analytics" 
              element={isStaff(user) ? <AdminLayout><AnalyticsDashboardPage /></AdminLayout> : <Navigate to="/login" />} 
            />
            <Route 
              path="/create-proposal/:formId" 
              element={isStaff(user) ? <AdminLayout><CreateProposalPage /></AdminLayout> : <Navigate to="/login" />} 
            />
            {/* More admin pages with AdminLayout */}
            <Route 
              path="/contract-reviews" 
              element={isStaff(user) ? <AdminLayout><ContractReviewsPage /></AdminLayout> : <Navigate to="/login" />} 
            />
            <Route 
              path="/audit-programs" 
              element={isStaff(user) ? <AdminLayout><AuditProgramsPage /></AdminLayout> : <Navigate to="/login" />} 
            />
            <Route 
              path="/job-orders" 
              element={isStaff(user) ? <AdminLayout><JobOrdersPage /></AdminLayout> : <Navigate to="/login" />} 
            />
            <Route 
              path="/audit-plans" 
              element={isStaff(user) ? <AdminLayout><AuditPlansPage /></AdminLayout> : <Navigate to="/login" />} 
            />
            <Route 
              path="/stage1-audit-plans" 
              element={isStaff(user) ? <AdminLayout><Stage1AuditPlansPage /></AdminLayout> : <Navigate to="/login" />} 
            />
            <Route 
              path="/stage2-audit-plans" 
              element={isStaff(user) ? <AdminLayout><Stage2AuditPlansPage /></AdminLayout> : <Navigate to="/login" />} 
            />
            <Route 
              path="/opening-closing-meetings" 
              element={isStaff(user) ? <AdminLayout><OpeningClosingMeetingsPage /></AdminLayout> : <Navigate to="/login" />} 
            />
            <Route 
              path="/audit-reports" 
              element={isStaff(user) ? <AdminLayout><AuditReportsPage /></AdminLayout> : <Navigate to="/login" />} 
            />
            <Route 
              path="/stage1-audit-reports" 
              element={isStaff(user) ? <AdminLayout><Stage1AuditReportsPage /></AdminLayout> : <Navigate to="/login" />} 
            />
            <Route 
              path="/stage2-audit-reports" 
              element={isStaff(user) ? <AdminLayout><Stage2AuditReportsPage /></AdminLayout> : <Navigate to="/login" />} 
            />
            <Route 
              path="/auditor-notes" 
              element={isStaff(user) ? <AdminLayout><AuditorNotesPage /></AdminLayout> : <Navigate to="/login" />} 
            />
            <Route 
              path="/nonconformity-reports" 
              element={isStaff(user) ? <AdminLayout><NonconformityReportsPage /></AdminLayout> : <Navigate to="/login" />} 
            />
            <Route 
              path="/certificate-data" 
              element={isStaff(user) ? <AdminLayout><CertificateDataPage /></AdminLayout> : <Navigate to="/login" />} 
            />
            <Route 
              path="/technical-reviews" 
              element={isStaff(user) ? <AdminLayout><TechnicalReviewPage /></AdminLayout> : <Navigate to="/login" />} 
            />
            <Route 
              path="/customer-feedback" 
              element={isStaff(user) ? <AdminLayout><CustomerFeedbackPage /></AdminLayout> : <Navigate to="/login" />} 
            />
            <Route 
              path="/feedback/:accessToken" 
              element={<PublicFeedbackPage />} 
            />
            <Route 
              path="/pre-transfer-reviews" 
              element={isStaff(user) ? <AdminLayout><PreTransferReviewPage /></AdminLayout> : <Navigate to="/login" />} 
            />
            <Route 
              path="/certified-clients" 
              element={isStaff(user) ? <AdminLayout><CertifiedClientsPage /></AdminLayout> : <Navigate to="/login" />} 
            />
            <Route 
              path="/suspended-clients" 
              element={isStaff(user) ? <AdminLayout><SuspendedClientsPage /></AdminLayout> : <Navigate to="/login" />} 
            />
            <Route 
              path="/rfq-requests" 
              element={isStaff(user) ? <AdminLayout><RFQRequestsPage /></AdminLayout> : <Navigate to="/login" />} 
            />
            <Route 
              path="/contact-messages" 
              element={isStaff(user) ? <AdminLayout><ContactMessagesPage /></AdminLayout> : <Navigate to="/login" />} 
            />
            <Route 
              path="/approvals" 
              element={isStaff(user) ? <AdminLayout><ApprovalsPage /></AdminLayout> : <Navigate to="/login" />} 
            />
            <Route 
              path="/reports" 
              element={isStaff(user) ? <AdminLayout><ReportsPage /></AdminLayout> : <Navigate to="/login" />} 
            />
            <Route 
              path="/templates" 
              element={isStaff(user) ? <AdminLayout><TemplatesPage /></AdminLayout> : <Navigate to="/login" />} 
            />
            <Route 
              path="/audit-scheduling" 
              element={isStaff(user) ? <AdminLayout><AuditSchedulingPage /></AdminLayout> : <Navigate to="/login" />} 
            />
            <Route path="/" element={<Navigate to={user ? "/dashboard" : "/login"} />} />
          </Routes>
        </BrowserRouter>
      </div>
    </AuthContext.Provider>
  );
}

export default App;
