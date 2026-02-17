import React, { useState, useEffect } from 'react';
import '@/App.css';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import axios from 'axios';
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
import OpeningClosingMeetingsPage from '@/pages/OpeningClosingMeetingsPage';
import PublicMeetingFormPage from '@/pages/PublicMeetingFormPage';
import Stage1AuditReportsPage from '@/pages/Stage1AuditReportsPage';
import Stage2AuditReportsPage from '@/pages/Stage2AuditReportsPage';
import AuditorNotesPage from '@/pages/AuditorNotesPage';
import NonconformityReportsPage from '@/pages/NonconformityReportsPage';
import CertificateDataPage from '@/pages/CertificateDataPage';
import TechnicalReviewPage from '@/pages/TechnicalReviewPage';
import CustomerFeedbackPage from '@/pages/CustomerFeedbackPage';
import PublicFeedbackPage from '@/pages/PublicFeedbackPage';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
export const API = `${BACKEND_URL}/api`;

// Set up axios defaults
axios.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const AuthContext = React.createContext();

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const { i18n } = useTranslation();

  useEffect(() => {
    // Set initial direction based on stored or default language
    const storedLang = localStorage.getItem('language') || 'ar';
    i18n.changeLanguage(storedLang);
    document.documentElement.dir = storedLang === 'ar' ? 'rtl' : 'ltr';
    document.documentElement.lang = storedLang;
    
    const token = localStorage.getItem('token');
    if (token) {
      // Verify token and get user info
      axios.get(`${API}/auth/me`)
        .then(response => {
          setUser(response.data);
        })
        .catch(() => {
          localStorage.removeItem('token');
        })
        .finally(() => {
          setLoading(false);
        });
    } else {
      setLoading(false);
    }
  }, [i18n]);

  const login = (token, userData) => {
    localStorage.setItem('token', token);
    setUser(userData);
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-xl">Loading...</div>
      </div>
    );
  }

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      <div className="App">
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
            <Route 
              path="/contract-reviews" 
              element={user?.role === 'admin' ? <ContractReviewsPage /> : <Navigate to="/login" />} 
            />
            <Route 
              path="/audit-programs" 
              element={user?.role === 'admin' ? <AuditProgramsPage /> : <Navigate to="/login" />} 
            />
            <Route 
              path="/job-orders" 
              element={user?.role === 'admin' ? <JobOrdersPage /> : <Navigate to="/login" />} 
            />
            <Route 
              path="/stage1-audit-plans" 
              element={user?.role === 'admin' ? <Stage1AuditPlansPage /> : <Navigate to="/login" />} 
            />
            <Route 
              path="/stage2-audit-plans" 
              element={user?.role === 'admin' ? <Stage2AuditPlansPage /> : <Navigate to="/login" />} 
            />
            <Route 
              path="/opening-closing-meetings" 
              element={user?.role === 'admin' ? <OpeningClosingMeetingsPage /> : <Navigate to="/login" />} 
            />
            <Route 
              path="/stage1-audit-reports" 
              element={user?.role === 'admin' ? <Stage1AuditReportsPage /> : <Navigate to="/login" />} 
            />
            <Route 
              path="/stage2-audit-reports" 
              element={user?.role === 'admin' ? <Stage2AuditReportsPage /> : <Navigate to="/login" />} 
            />
            <Route 
              path="/auditor-notes" 
              element={user?.role === 'admin' ? <AuditorNotesPage /> : <Navigate to="/login" />} 
            />
            <Route 
              path="/nonconformity-reports" 
              element={user?.role === 'admin' ? <NonconformityReportsPage /> : <Navigate to="/login" />} 
            />
            <Route 
              path="/certificate-data" 
              element={user?.role === 'admin' ? <CertificateDataPage /> : <Navigate to="/login" />} 
            />
            <Route 
              path="/technical-reviews" 
              element={user?.role === 'admin' ? <TechnicalReviewPage /> : <Navigate to="/login" />} 
            />
            <Route 
              path="/customer-feedback" 
              element={user?.role === 'admin' ? <CustomerFeedbackPage /> : <Navigate to="/login" />} 
            />
            <Route 
              path="/feedback/:accessToken" 
              element={<PublicFeedbackPage />} 
            />
            <Route 
              path="/create-proposal/:formId" 
              element={user?.role === 'admin' ? <CreateProposalPage /> : <Navigate to="/login" />} 
            />
            <Route 
              path="/reports" 
              element={user?.role === 'admin' ? <ReportsPage /> : <Navigate to="/login" />} 
            />
            <Route 
              path="/templates" 
              element={user?.role === 'admin' ? <TemplatesPage /> : <Navigate to="/login" />} 
            />
            <Route 
              path="/audit-scheduling" 
              element={user?.role === 'admin' ? <AuditSchedulingPage /> : <Navigate to="/login" />} 
            />
            <Route 
              path="/invoices" 
              element={user?.role === 'admin' ? <InvoicesPage /> : <Navigate to="/login" />} 
            />
            <Route 
              path="/auditors" 
              element={user?.role === 'admin' ? <AuditorsPage /> : <Navigate to="/login" />} 
            />
            <Route 
              path="/certificates" 
              element={user?.role === 'admin' ? <CertificatesPage /> : <Navigate to="/login" />} 
            />
            <Route 
              path="/alerts" 
              element={user?.role === 'admin' ? <ExpirationAlertsPage /> : <Navigate to="/login" />} 
            />
            <Route 
              path="/analytics" 
              element={user?.role === 'admin' ? <AnalyticsDashboardPage /> : <Navigate to="/login" />} 
            />
            <Route path="/" element={<Navigate to={user ? "/dashboard" : "/login"} />} />
          </Routes>
        </BrowserRouter>
      </div>
    </AuthContext.Provider>
  );
}

export default App;
