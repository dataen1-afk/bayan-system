import React from 'react';
import { useTranslation } from 'react-i18next';
import { LogOut } from 'lucide-react';
import { Button } from './ui/button';

// Language Switcher Component
const LanguageSwitcher = () => {
  const { i18n } = useTranslation();
  
  const toggleLanguage = () => {
    const newLang = i18n.language === 'ar' ? 'en' : 'ar';
    i18n.changeLanguage(newLang);
    localStorage.setItem('language', newLang);
    document.documentElement.dir = newLang === 'ar' ? 'rtl' : 'ltr';
    document.documentElement.lang = newLang;
  };

  return (
    <Button
      variant="outline"
      size="sm"
      onClick={toggleLanguage}
      className="px-3"
      data-testid="language-switcher"
    >
      {i18n.language === 'ar' ? 'EN' : 'عربي'}
    </Button>
  );
};

const Header = ({ user, onLogout }) => {
  const { t, i18n } = useTranslation();
  const isRTL = i18n.language === 'ar';

  return (
    <header className="fixed top-0 left-0 right-0 z-40 bg-white shadow-md">
      {/* Main Header Content */}
      <div className="dashboard-header max-w-full mx-auto px-4 py-3 sm:px-6 lg:px-8 flex justify-between items-center">
        {/* User Controls - Left side in RTL, Right side in LTR */}
        <div className={`dashboard-header-controls flex gap-3 items-center ${isRTL ? 'order-first' : 'order-last'}`}>
          <LanguageSwitcher />
          <Button 
            variant="outline" 
            onClick={onLogout} 
            data-testid="logout-button" 
            className="bg-bayan-navy text-white hover:bg-bayan-navy-light border-bayan-navy font-semibold"
          >
            <LogOut className="btn-icon w-4 h-4" />
            {t('logout')}
          </Button>
        </div>
        {/* Logo - Right side in RTL, Left side in LTR */}
        <div className={`dashboard-header-logo ${isRTL ? 'order-last' : 'order-first'}`}>
          <div className="-my-2">
            <img src="/bayan-logo.png" alt="Bayan" className="h-20 w-auto object-contain" />
          </div>
        </div>
      </div>
      {/* Navy Accent Bar */}
      <div className="h-1.5 bg-gradient-to-r from-bayan-navy via-bayan-navy-light to-bayan-navy"></div>
    </header>
  );
};

export default Header;
