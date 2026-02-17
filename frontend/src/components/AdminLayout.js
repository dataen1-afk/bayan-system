import React, { useState, useContext } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import Sidebar from './Sidebar';
import Header from './Header';
import { AuthContext } from '../App';

const AdminLayout = ({ children }) => {
  const { i18n } = useTranslation();
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useContext(AuthContext);
  const [activeTab, setActiveTab] = useState('dashboard');
  const isRTL = i18n.language === 'ar';

  // Map routes to tab IDs for highlighting active menu item
  const routeToTabMap = {
    '/dashboard': 'forms',
    '/contract-reviews': 'contract-reviews',
    '/audit-programs': 'audit-programs',
    '/job-orders': 'job-orders',
    '/stage1-audit-plans': 'stage1-audit-plans',
    '/stage2-audit-plans': 'stage2-audit-plans',
    '/opening-closing-meetings': 'opening-closing-meetings',
    '/stage1-audit-reports': 'stage1-audit-reports',
    '/stage2-audit-reports': 'stage2-audit-reports',
    '/auditor-notes': 'auditor-notes',
    '/nonconformity-reports': 'nc-reports',
    '/certificate-data': 'cert-data',
    '/technical-reviews': 'technical-reviews',
    '/customer-feedback': 'customer-feedback',
    '/pre-transfer-reviews': 'pre-transfer-reviews',
    '/certified-clients': 'certified-clients',
    '/suspended-clients': 'suspended-clients',
    '/audit-scheduling': 'audit-scheduling',
    '/auditors': 'auditors',
    '/invoices': 'invoices',
    '/certificates': 'certificates',
    '/alerts': 'alerts',
    '/analytics': 'analytics',
    '/templates': 'templates',
    '/reports': 'reports',
  };

  const currentTab = routeToTabMap[location.pathname] || 'forms';

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className={`min-h-screen bg-gray-50 ${isRTL ? 'rtl' : 'ltr'}`} dir={isRTL ? 'rtl' : 'ltr'}>
      {/* Header */}
      <Header user={user} onLogout={handleLogout} />
      
      {/* Layout with Sidebar */}
      <div className="flex pt-[102px]">
        <Sidebar 
          activeTab={currentTab} 
          onTabChange={setActiveTab}
          userRole="admin"
          userName={user?.name}
        />
        
        {/* Main Content */}
        <main className="flex-1 min-h-[calc(100vh-102px)]">
          {children}
        </main>
      </div>
    </div>
  );
};

export default AdminLayout;
