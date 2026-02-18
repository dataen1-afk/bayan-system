import React, { useState, useEffect, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate, useLocation } from 'react-router-dom';
import { 
  FileText, 
  DollarSign, 
  FileCheck, 
  FolderOpen, 
  BarChart3, 
  Settings,
  ChevronLeft,
  ChevronRight,
  Menu,
  Calendar,
  ExternalLink,
  Receipt,
  Users,
  Award,
  Bell,
  TrendingUp,
  ClipboardList,
  ClipboardCheck,
  FileSignature,
  FileSpreadsheet,
  UsersRound,
  FileBadge,
  NotebookPen,
  AlertTriangle,
  FileOutput,
  ShieldCheck,
  MessageSquare,
  ArrowRightLeft,
  UserX,
  FileQuestion,
  Mail,
  CheckSquare,
  LayoutDashboard
} from 'lucide-react';
import { cn } from '@/lib/utils';

const Sidebar = ({ activeTab, onTabChange, userRole = 'admin', userName, dashboardTitle }) => {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const location = useLocation();
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [isMobileOpen, setIsMobileOpen] = useState(false);
  
  // Check for RTL
  const isRTL = i18n.language?.startsWith('ar') || document.documentElement.dir === 'rtl';

  // Determine active item based on current route or activeTab prop
  const getActiveItemId = () => {
    const currentPath = location.pathname;
    
    // Check if current path matches any menu item's route
    const routeBasedItems = [
      { id: 'contract-reviews', route: '/contract-reviews' },
      { id: 'audit-programs', route: '/audit-programs' },
      { id: 'job-orders', route: '/job-orders' },
      { id: 'audit-plans', route: '/audit-plans' },
      { id: 'opening-closing-meetings', route: '/opening-closing-meetings' },
      { id: 'audit-reports', route: '/audit-reports' },
      { id: 'auditor-notes', route: '/auditor-notes' },
      { id: 'nc-reports', route: '/nonconformity-reports' },
      { id: 'cert-data', route: '/certificate-data' },
      { id: 'technical-reviews', route: '/technical-reviews' },
      { id: 'customer-feedback', route: '/customer-feedback' },
      { id: 'pre-transfer-reviews', route: '/pre-transfer-reviews' },
      { id: 'certified-clients', route: '/certified-clients' },
      { id: 'suspended-clients', route: '/suspended-clients' },
      { id: 'rfq-requests', route: '/rfq-requests' },
      { id: 'contact-messages', route: '/contact-messages' },
      { id: 'approvals', route: '/approvals' },
      { id: 'audit-scheduling', route: '/audit-scheduling' },
      { id: 'auditors', route: '/auditors' },
      { id: 'invoices', route: '/invoices' },
      { id: 'certificates', route: '/certificates' },
      { id: 'alerts', route: '/alerts' },
      { id: 'analytics', route: '/analytics' },
      { id: 'reports', route: '/reports' },
      { id: 'templates', route: '/templates' },
    ];
    
    const matchedItem = routeBasedItems.find(item => currentPath === item.route);
    if (matchedItem) {
      return matchedItem.id;
    }
    
    // Fall back to activeTab prop for dashboard tabs
    return activeTab;
  };
  
  const currentActiveId = getActiveItemId();

  // Listen for language changes
  useEffect(() => {
    const handleLanguageChange = () => {
      // Force re-render on language change
    };
    i18n.on('languageChanged', handleLanguageChange);
    return () => i18n.off('languageChanged', handleLanguageChange);
  }, [i18n]);

  // Menu items based on user role
  const menuItems = userRole === 'admin' ? [
    { id: 'dashboard', icon: LayoutDashboard, label: t('dashboard'), color: 'text-slate-700' },
    { id: 'forms', icon: FileText, label: t('forms'), color: 'text-blue-600' },
    { id: 'quotations', icon: DollarSign, label: t('quotations'), color: 'text-green-600' },
    { id: 'contracts', icon: FileCheck, label: t('contracts'), color: 'text-purple-600' },
    { id: 'contract-reviews', icon: ClipboardList, label: t('contractReviews'), color: 'text-pink-600', route: '/contract-reviews' },
    { id: 'audit-programs', icon: ClipboardCheck, label: t('auditPrograms'), color: 'text-cyan-600', route: '/audit-programs' },
    { id: 'job-orders', icon: FileSignature, label: t('jobOrders'), color: 'text-violet-600', route: '/job-orders' },
    { id: 'audit-plans', icon: FileSpreadsheet, label: t('auditPlans'), color: 'text-rose-600', route: '/audit-plans' },
    { id: 'opening-closing-meetings', icon: UsersRound, label: t('openingClosingMeetings'), color: 'text-cyan-600', route: '/opening-closing-meetings' },
    { id: 'audit-reports', icon: FileBadge, label: t('auditReports'), color: 'text-red-600', route: '/audit-reports' },
    { id: 'auditor-notes', icon: NotebookPen, label: t('auditorNotes'), color: 'text-emerald-600', route: '/auditor-notes' },
    { id: 'nc-reports', icon: AlertTriangle, label: t('ncReports'), color: 'text-red-600', route: '/nonconformity-reports' },
    { id: 'cert-data', icon: FileOutput, label: t('certData'), color: 'text-teal-600', route: '/certificate-data' },
    { id: 'technical-reviews', icon: ShieldCheck, label: t('technicalReviews'), color: 'text-indigo-600', route: '/technical-reviews' },
    { id: 'customer-feedback', icon: MessageSquare, label: t('customerFeedback'), color: 'text-pink-600', route: '/customer-feedback' },
    { id: 'pre-transfer-reviews', icon: ArrowRightLeft, label: t('preTransferReviews'), color: 'text-amber-600', route: '/pre-transfer-reviews' },
    { id: 'certified-clients', icon: Award, label: t('certifiedClients'), color: 'text-emerald-600', route: '/certified-clients' },
    { id: 'suspended-clients', icon: UserX, label: t('suspendedClients'), color: 'text-red-600', route: '/suspended-clients' },
    { id: 'rfq-requests', icon: FileQuestion, label: t('rfqRequests'), color: 'text-orange-600', route: '/rfq-requests' },
    { id: 'contact-messages', icon: Mail, label: t('contactMessages'), color: 'text-cyan-600', route: '/contact-messages' },
    { id: 'approvals', icon: CheckSquare, label: t('approvals'), color: 'text-indigo-600', route: '/approvals' },
    { id: 'templates', icon: FolderOpen, label: t('templates'), color: 'text-orange-600' },
    { id: 'reports', icon: BarChart3, label: t('reports'), color: 'text-cyan-600' },
    { id: 'audit-scheduling', icon: Calendar, label: t('auditScheduling'), color: 'text-indigo-600', route: '/audit-scheduling' },
    { id: 'auditors', icon: Users, label: t('auditors'), color: 'text-teal-600', route: '/auditors' },
    { id: 'invoices', icon: Receipt, label: t('invoices'), color: 'text-amber-600', route: '/invoices' },
    { id: 'certificates', icon: Award, label: t('certificates'), color: 'text-yellow-600', route: '/certificates' },
    { id: 'alerts', icon: Bell, label: t('expirationAlerts'), color: 'text-red-600', route: '/alerts' },
    { id: 'analytics', icon: TrendingUp, label: t('analytics'), color: 'text-indigo-600', route: '/analytics' },
    { id: 'customer-portal', icon: ExternalLink, label: t('customerPortal'), color: 'text-emerald-600', route: '/track', external: true },
  ] : [
    { id: 'forms', icon: FileText, label: t('myForms'), color: 'text-blue-600' },
    { id: 'quotations', icon: DollarSign, label: t('quotations'), color: 'text-green-600' },
    { id: 'contracts', icon: FileCheck, label: t('contracts'), color: 'text-purple-600' },
  ];

  const bottomMenuItems = [
    { id: 'settings', icon: Settings, label: t('settings'), color: 'text-gray-600' },
  ];

  const handleMenuClick = (item) => {
    if (item.route) {
      if (item.external) {
        window.open(item.route, '_blank');
      } else {
        navigate(item.route);
      }
    } else {
      // Navigate to dashboard with tab parameter for items without routes
      navigate(`/dashboard?tab=${item.id}`);
      onTabChange(item.id);
    }
    setIsMobileOpen(false);
  };

  const MenuItem = ({ item, isBottom = false }) => {
    const isActive = currentActiveId === item.id;
    const Icon = item.icon;
    
    return (
      <button
        onClick={() => handleMenuClick(item)}
        data-testid={`sidebar-${item.id}`}
        className={cn(
          "sidebar-menu-item w-full flex items-center gap-3 px-3 py-3 rounded-lg transition-all duration-200",
          "hover:bg-slate-100 hover:text-bayan-navy",
          isActive && "bg-slate-100 text-bayan-navy font-semibold shadow-sm",
          !isActive && "text-gray-600",
          isCollapsed && "justify-center px-2"
        )}
        title={isCollapsed ? item.label : ''}
      >
        <Icon className={cn("w-5 h-5 flex-shrink-0", isActive ? 'text-bayan-navy' : item.color)} />
        {!isCollapsed && (
          <span className="truncate text-sm">{item.label}</span>
        )}
        {isActive && !isCollapsed && (
          <div className={cn(
            "w-1 h-6 bg-bayan-navy rounded-full",
            isRTL ? "mr-auto" : "ml-auto"
          )} />
        )}
      </button>
    );
  };

  // Mobile menu button
  const MobileMenuButton = () => (
    <button
      onClick={() => setIsMobileOpen(!isMobileOpen)}
      className="lg:hidden fixed top-20 z-50 p-2 bg-white rounded-lg shadow-lg border border-gray-200"
      style={{ [isRTL ? 'right' : 'left']: '1rem' }}
      data-testid="mobile-menu-toggle"
    >
      <Menu className="w-6 h-6 text-gray-600" />
    </button>
  );

  // Collapse toggle icon based on RTL
  const CollapseIcon = isRTL 
    ? (isCollapsed ? ChevronLeft : ChevronRight)
    : (isCollapsed ? ChevronRight : ChevronLeft);

  return (
    <>
      <MobileMenuButton />
      
      {/* Overlay for mobile */}
      {isMobileOpen && (
        <div 
          className="lg:hidden fixed inset-0 bg-black/50 z-40"
          onClick={() => setIsMobileOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        data-testid="sidebar"
        className={cn(
          "sidebar-container bg-white border-gray-200 shadow-lg z-30 transition-all duration-300 flex flex-col border-t border-t-gray-200",
          isRTL ? "border-l" : "border-r",
          isCollapsed ? "w-16" : "w-64",
          // Desktop: fixed position, Mobile: slide in/out
          "fixed lg:sticky lg:top-0",
          isMobileOpen ? "translate-x-0" : (isRTL ? "translate-x-full lg:translate-x-0" : "-translate-x-full lg:translate-x-0"),
        )}
        style={{
          top: '96px', // Below header
          height: 'calc(100vh - 96px)',
          [isRTL ? 'right' : 'left']: 0,
        }}
      >
        {/* Collapse Toggle Button */}
        <button
          onClick={() => setIsCollapsed(!isCollapsed)}
          data-testid="sidebar-toggle"
          className={cn(
            "hidden lg:flex absolute w-6 h-6 bg-white border border-gray-300 rounded-full items-center justify-center shadow-md hover:bg-gray-50 transition-colors",
            isRTL ? "-left-3" : "-right-3"
          )}
          style={{ top: '38px' }}
        >
          <CollapseIcon className="w-4 h-4 text-gray-600" />
        </button>

        {/* Dashboard Title Section */}
        <div className={cn(
          "px-4 pt-8 pb-4 border-b border-gray-100",
          isCollapsed && "px-2"
        )}>
          {!isCollapsed ? (
            <div className={isRTL ? "text-right" : "text-left"}>
              <h2 className="text-lg font-bold text-bayan-navy" data-testid="sidebar-dashboard-title">{dashboardTitle}</h2>
              <p className="text-sm text-bayan-gray-medium mt-1">{t('welcome')}, {userName}</p>
            </div>
          ) : (
            <div className="w-9 h-9 bg-bayan-navy rounded-full flex items-center justify-center mx-auto" title={`${dashboardTitle} - ${userName}`}>
              <span className="text-white font-bold text-xs">
                {userName?.charAt(0)?.toUpperCase() || 'U'}
              </span>
            </div>
          )}
        </div>

        {/* Main Menu */}
        <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
          {menuItems.map((item) => (
            <MenuItem key={item.id} item={item} />
          ))}
        </nav>

        {/* Divider */}
        <div className="px-3">
          <div className="border-t border-gray-200" />
        </div>

        {/* Bottom Menu */}
        <nav className="px-3 py-4 space-y-1">
          {bottomMenuItems.map((item) => (
            <MenuItem key={item.id} item={item} isBottom />
          ))}
        </nav>

        {/* Collapse indicator for mobile */}
        {!isCollapsed && (
          <div className={cn(
            "px-4 py-3 text-xs text-gray-400 border-t border-gray-100",
            isRTL ? "text-right" : "text-left"
          )}>
            {t('collapseHint')}
          </div>
        )}
      </aside>
    </>
  );
};

export default Sidebar;
