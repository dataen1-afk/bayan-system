import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { 
  FileText, 
  DollarSign, 
  FileCheck, 
  FolderOpen, 
  BarChart3, 
  Settings,
  ChevronLeft,
  ChevronRight,
  Menu
} from 'lucide-react';
import { cn } from '@/lib/utils';

const Sidebar = ({ activeTab, onTabChange, userRole = 'admin' }) => {
  const { t, i18n } = useTranslation();
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [isMobileOpen, setIsMobileOpen] = useState(false);
  
  // Check for RTL
  const isRTL = i18n.language?.startsWith('ar') || document.documentElement.dir === 'rtl';

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
    { id: 'forms', icon: FileText, label: t('forms'), color: 'text-blue-600' },
    { id: 'quotations', icon: DollarSign, label: t('quotations'), color: 'text-green-600' },
    { id: 'contracts', icon: FileCheck, label: t('contracts'), color: 'text-purple-600' },
    { id: 'templates', icon: FolderOpen, label: t('templates'), color: 'text-orange-600' },
    { id: 'reports', icon: BarChart3, label: t('reports'), color: 'text-cyan-600' },
  ] : [
    { id: 'forms', icon: FileText, label: t('myForms'), color: 'text-blue-600' },
    { id: 'quotations', icon: DollarSign, label: t('quotations'), color: 'text-green-600' },
    { id: 'contracts', icon: FileCheck, label: t('contracts'), color: 'text-purple-600' },
  ];

  const bottomMenuItems = [
    { id: 'settings', icon: Settings, label: t('settings'), color: 'text-gray-600' },
  ];

  const MenuItem = ({ item, isBottom = false }) => {
    const isActive = activeTab === item.id;
    const Icon = item.icon;
    
    return (
      <button
        onClick={() => {
          onTabChange(item.id);
          setIsMobileOpen(false);
        }}
        data-testid={`sidebar-${item.id}`}
        className={cn(
          "sidebar-menu-item w-full flex items-center gap-3 px-3 py-3 rounded-lg transition-all duration-200",
          "hover:bg-slate-100 hover:text-bayan-navy",
          isActive && "bg-slate-100 text-bayan-navy font-semibold shadow-sm",
          !isActive && "text-gray-600",
          isCollapsed && "justify-center px-2",
          isRTL && "flex-row-reverse"
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

        {/* Logo/Brand Section */}
        <div className={cn(
          "px-4 pt-8 pb-4 border-b border-gray-100",
          isCollapsed && "px-2"
        )}>
          {!isCollapsed ? (
            <div className={cn("flex items-center gap-2", isRTL && "flex-row-reverse")}>
              <div className="w-9 h-9 bg-bayan-navy rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-xs">BA</span>
              </div>
              <span className="font-semibold text-bayan-navy text-sm">{t('navigation')}</span>
            </div>
          ) : (
            <div className="w-9 h-9 bg-bayan-navy rounded-lg flex items-center justify-center mx-auto">
              <span className="text-white font-bold text-xs">BA</span>
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
