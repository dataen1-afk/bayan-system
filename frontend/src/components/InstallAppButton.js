import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Download, X, Smartphone, Monitor, CheckCircle2, Zap, Home } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog';

const InstallAppButton = ({ isRTL, variant = 'default', className = '' }) => {
  const [deferredPrompt, setDeferredPrompt] = useState(null);
  const [isInstalled, setIsInstalled] = useState(false);
  const [showGuide, setShowGuide] = useState(false);
  const [isInstalling, setIsInstalling] = useState(false);
  const [showTooltip, setShowTooltip] = useState(false);
  const [shouldPulse, setShouldPulse] = useState(false);

  useEffect(() => {
    // Check if already installed
    if (window.matchMedia('(display-mode: standalone)').matches) {
      setIsInstalled(true);
      return;
    }

    // Check if this is first visit (for tooltip)
    const hasSeenTooltip = localStorage.getItem('pwa-install-tooltip-seen');
    if (!hasSeenTooltip) {
      // Show tooltip after a short delay
      const tooltipTimer = setTimeout(() => {
        setShowTooltip(true);
        setShouldPulse(true);
      }, 2000);

      // Auto-hide tooltip after 6 seconds
      const hideTimer = setTimeout(() => {
        setShowTooltip(false);
        localStorage.setItem('pwa-install-tooltip-seen', 'true');
      }, 8000);

      return () => {
        clearTimeout(tooltipTimer);
        clearTimeout(hideTimer);
      };
    }

    // Check if prompt was already captured globally
    if (window.deferredPWAPrompt) {
      setDeferredPrompt(window.deferredPWAPrompt);
    }

    const handleBeforeInstall = (e) => {
      e.preventDefault();
      setDeferredPrompt(e);
      window.deferredPWAPrompt = e;
    };

    const handlePromptAvailable = () => {
      if (window.deferredPWAPrompt) {
        setDeferredPrompt(window.deferredPWAPrompt);
      }
    };

    const handleAppInstalled = () => {
      setIsInstalled(true);
      setDeferredPrompt(null);
      window.deferredPWAPrompt = null;
      setShowGuide(false);
      setShowTooltip(false);
      setShouldPulse(false);
    };

    window.addEventListener('beforeinstallprompt', handleBeforeInstall);
    window.addEventListener('pwaPromptAvailable', handlePromptAvailable);
    window.addEventListener('appinstalled', handleAppInstalled);

    return () => {
      window.removeEventListener('beforeinstallprompt', handleBeforeInstall);
      window.removeEventListener('pwaPromptAvailable', handlePromptAvailable);
      window.removeEventListener('appinstalled', handleAppInstalled);
    };
  }, []);

  // Also check for deferred prompt on mount
  useEffect(() => {
    if (window.deferredPWAPrompt) {
      setDeferredPrompt(window.deferredPWAPrompt);
    }
  }, []);

  const handleInstall = async () => {
    if (!deferredPrompt) {
      // Show guide if browser doesn't support native install
      setShowGuide(true);
      return;
    }

    setIsInstalling(true);
    try {
      deferredPrompt.prompt();
      const { outcome } = await deferredPrompt.userChoice;
      
      if (outcome === 'accepted') {
        setIsInstalled(true);
      }
      setDeferredPrompt(null);
      window.deferredPWAPrompt = null;
    } catch (error) {
      console.error('Install error:', error);
    } finally {
      setIsInstalling(false);
      setShowGuide(false);
    }
  };

  const handleButtonClick = () => {
    if (deferredPrompt) {
      handleInstall();
    } else {
      setShowGuide(true);
    }
  };

  // Don't render if already installed
  if (isInstalled) return null;

  const benefits = [
    { icon: Home, text: isRTL ? 'وصول سريع من الشاشة الرئيسية' : 'Quick access from home screen' },
    { icon: Zap, text: isRTL ? 'تحميل أسرع وأداء أفضل' : 'Faster loading & performance' },
    { icon: Smartphone, text: isRTL ? 'تجربة تطبيق متكاملة' : 'Full app-like experience' },
  ];

  // Sidebar variant - compact button
  if (variant === 'sidebar') {
    return (
      <>
        <button
          onClick={handleButtonClick}
          data-testid="install-app-sidebar-btn"
          className={`w-full flex items-center gap-3 px-3 py-3 rounded-lg transition-all duration-200 hover:bg-emerald-50 text-emerald-600 ${className}`}
        >
          <Download className="w-5 h-5 flex-shrink-0" />
          <span className="truncate text-sm font-medium">
            {isRTL ? 'تثبيت التطبيق' : 'Install App'}
          </span>
        </button>

        <InstallGuideDialog 
          isOpen={showGuide} 
          onClose={() => setShowGuide(false)} 
          onInstall={handleInstall}
          isRTL={isRTL}
          benefits={benefits}
          deferredPrompt={deferredPrompt}
          isInstalling={isInstalling}
        />
      </>
    );
  }

  // Sidebar collapsed variant - icon only
  if (variant === 'sidebar-collapsed') {
    return (
      <>
        <button
          onClick={handleButtonClick}
          data-testid="install-app-sidebar-collapsed-btn"
          title={isRTL ? 'تثبيت التطبيق' : 'Install App'}
          className={`w-full flex justify-center px-2 py-3 rounded-lg transition-all duration-200 hover:bg-emerald-50 text-emerald-600 ${className}`}
        >
          <Download className="w-5 h-5" />
        </button>

        <InstallGuideDialog 
          isOpen={showGuide} 
          onClose={() => setShowGuide(false)} 
          onInstall={handleInstall}
          isRTL={isRTL}
          benefits={benefits}
          deferredPrompt={deferredPrompt}
          isInstalling={isInstalling}
        />
      </>
    );
  }

  // Default variant - header button
  return (
    <>
      <Button
        onClick={handleButtonClick}
        variant="outline"
        size="sm"
        data-testid="install-app-header-btn"
        className={`border-emerald-500 text-emerald-600 hover:bg-emerald-50 hover:text-emerald-700 gap-2 ${className}`}
      >
        <Download className="w-4 h-4" />
        <span className="hidden sm:inline">
          {isRTL ? 'تثبيت التطبيق' : 'Install App'}
        </span>
      </Button>

      <InstallGuideDialog 
        isOpen={showGuide} 
        onClose={() => setShowGuide(false)} 
        onInstall={handleInstall}
        isRTL={isRTL}
        benefits={benefits}
        deferredPrompt={deferredPrompt}
        isInstalling={isInstalling}
      />
    </>
  );
};

// Installation Guide Dialog Component
const InstallGuideDialog = ({ isOpen, onClose, onInstall, isRTL, benefits, deferredPrompt, isInstalling }) => {
  const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
  const isIOS = /iPhone|iPad|iPod/i.test(navigator.userAgent);
  const isAndroid = /Android/i.test(navigator.userAgent);

  const getInstallInstructions = () => {
    if (deferredPrompt) {
      return {
        title: isRTL ? 'جاهز للتثبيت' : 'Ready to Install',
        steps: [
          isRTL ? 'انقر على زر "تثبيت الآن" أدناه' : 'Click "Install Now" button below',
          isRTL ? 'اتبع تعليمات المتصفح' : 'Follow browser prompts',
          isRTL ? 'استمتع بالتطبيق من شاشتك الرئيسية' : 'Enjoy the app from your home screen',
        ],
      };
    }

    if (isIOS) {
      return {
        title: isRTL ? 'التثبيت على iOS' : 'Install on iOS',
        steps: [
          isRTL ? 'اضغط على أيقونة المشاركة في شريط المتصفح' : 'Tap the Share icon in the browser toolbar',
          isRTL ? 'مرر للأسفل واضغط "إضافة إلى الشاشة الرئيسية"' : 'Scroll down and tap "Add to Home Screen"',
          isRTL ? 'اضغط "إضافة" للتأكيد' : 'Tap "Add" to confirm',
        ],
      };
    }

    if (isAndroid) {
      return {
        title: isRTL ? 'التثبيت على Android' : 'Install on Android',
        steps: [
          isRTL ? 'اضغط على قائمة المتصفح (⋮)' : 'Tap browser menu (⋮)',
          isRTL ? 'اختر "تثبيت التطبيق" أو "إضافة إلى الشاشة الرئيسية"' : 'Select "Install app" or "Add to Home Screen"',
          isRTL ? 'اتبع التعليمات للتأكيد' : 'Follow prompts to confirm',
        ],
      };
    }

    // Desktop browsers
    return {
      title: isRTL ? 'التثبيت على الكمبيوتر' : 'Install on Desktop',
      steps: [
        isRTL ? 'ابحث عن أيقونة التثبيت في شريط العنوان' : 'Look for install icon in address bar',
        isRTL ? 'أو اضغط على قائمة المتصفح واختر "تثبيت..."' : 'Or click browser menu and select "Install..."',
        isRTL ? 'اتبع التعليمات للتأكيد' : 'Follow prompts to confirm',
      ],
    };
  };

  const instructions = getInstallInstructions();

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className={`sm:max-w-md ${isRTL ? 'rtl' : 'ltr'}`}>
        <DialogHeader>
          <DialogTitle className={`flex items-center gap-3 ${isRTL ? 'flex-row-reverse text-right' : ''}`}>
            <div className="w-12 h-12 bg-gradient-to-br from-[#1e3a5f] to-[#2a4a6f] rounded-xl flex items-center justify-center shadow-lg">
              <Smartphone className="w-6 h-6 text-white" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-[#1e3a5f]">
                {isRTL ? 'تثبيت بيان' : 'Install Bayan'}
              </h3>
              <p className="text-sm text-slate-500 font-normal">
                {instructions.title}
              </p>
            </div>
          </DialogTitle>
          <DialogDescription className="sr-only">
            {isRTL ? 'دليل تثبيت تطبيق بيان' : 'Bayan app installation guide'}
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6 pt-4">
          {/* Benefits */}
          <div className={`space-y-3 ${isRTL ? 'text-right' : 'text-left'}`}>
            <p className="text-sm font-medium text-slate-700">
              {isRTL ? 'مميزات التطبيق:' : 'App Benefits:'}
            </p>
            {benefits.map((benefit, idx) => (
              <div 
                key={idx} 
                className={`flex items-center gap-3 ${isRTL ? 'flex-row-reverse' : ''}`}
              >
                <div className="w-8 h-8 bg-emerald-100 rounded-lg flex items-center justify-center flex-shrink-0">
                  <benefit.icon className="w-4 h-4 text-emerald-600" />
                </div>
                <span className="text-sm text-slate-600">{benefit.text}</span>
              </div>
            ))}
          </div>

          {/* Installation Steps */}
          <div className={`space-y-3 ${isRTL ? 'text-right' : 'text-left'}`}>
            <p className="text-sm font-medium text-slate-700">
              {isRTL ? 'خطوات التثبيت:' : 'Installation Steps:'}
            </p>
            <div className="space-y-2">
              {instructions.steps.map((step, idx) => (
                <div 
                  key={idx} 
                  className={`flex items-start gap-3 ${isRTL ? 'flex-row-reverse' : ''}`}
                >
                  <div className="w-6 h-6 bg-[#1e3a5f] rounded-full flex items-center justify-center flex-shrink-0 text-white text-xs font-bold">
                    {idx + 1}
                  </div>
                  <span className="text-sm text-slate-600 pt-0.5">{step}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Action Buttons */}
          <div className={`flex gap-3 pt-2 ${isRTL ? 'flex-row-reverse' : ''}`}>
            {deferredPrompt ? (
              <Button
                onClick={onInstall}
                disabled={isInstalling}
                className="flex-1 bg-[#1e3a5f] hover:bg-[#152a45] text-white"
                data-testid="install-now-btn"
              >
                {isInstalling ? (
                  <span className="animate-pulse">{isRTL ? 'جاري التثبيت...' : 'Installing...'}</span>
                ) : (
                  <>
                    <Download className={`w-4 h-4 ${isRTL ? 'ml-2' : 'mr-2'}`} />
                    {isRTL ? 'تثبيت الآن' : 'Install Now'}
                  </>
                )}
              </Button>
            ) : null}
            <Button
              onClick={onClose}
              variant="outline"
              className={deferredPrompt ? '' : 'flex-1'}
            >
              {isRTL ? 'إغلاق' : 'Close'}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default InstallAppButton;
