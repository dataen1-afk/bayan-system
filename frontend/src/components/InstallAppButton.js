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
    // Dismiss tooltip when button is clicked
    setShowTooltip(false);
    setShouldPulse(false);
    localStorage.setItem('pwa-install-tooltip-seen', 'true');
    
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

  // Default variant - header button with pulsing animation and tooltip
  return (
    <div className="relative">
      {/* Pulsing Button */}
      <motion.div
        animate={shouldPulse ? {
          scale: [1, 1.05, 1],
          boxShadow: [
            '0 0 0 0 rgba(16, 185, 129, 0)',
            '0 0 0 8px rgba(16, 185, 129, 0.3)',
            '0 0 0 0 rgba(16, 185, 129, 0)'
          ]
        } : {}}
        transition={{
          duration: 2,
          repeat: shouldPulse ? Infinity : 0,
          ease: "easeInOut"
        }}
        className="rounded-md"
      >
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
      </motion.div>

      {/* Tooltip for first-time visitors */}
      <AnimatePresence>
        {showTooltip && (
          <motion.div
            initial={{ opacity: 0, y: 10, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 10, scale: 0.9 }}
            transition={{ type: 'spring', damping: 20, stiffness: 300 }}
            className={`absolute top-full mt-3 z-50 ${isRTL ? 'left-0' : 'left-0'}`}
            style={{ minWidth: '200px' }}
          >
            <div className="bg-[#1e3a5f] text-white px-4 py-3 rounded-xl shadow-2xl relative">
              {/* Arrow */}
              <div 
                className={`absolute -top-2 w-4 h-4 bg-[#1e3a5f] transform rotate-45 ${isRTL ? 'right-4' : 'left-4'}`}
              />
              <p className={`text-sm leading-relaxed relative z-10 ${isRTL ? 'text-right' : 'text-left'}`}>
                {isRTL 
                  ? 'ثبّت التطبيق للوصول السريع' 
                  : 'Install for quick access'}
              </p>
              <button
                onClick={() => {
                  setShowTooltip(false);
                  setShouldPulse(false);
                  localStorage.setItem('pwa-install-tooltip-seen', 'true');
                }}
                className={`mt-2 text-xs text-emerald-300 hover:text-emerald-200 font-medium ${isRTL ? 'text-right w-full block' : ''}`}
              >
                {isRTL ? 'حسناً' : 'Got it'}
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <InstallGuideDialog 
        isOpen={showGuide} 
        onClose={() => setShowGuide(false)} 
        onInstall={handleInstall}
        isRTL={isRTL}
        benefits={benefits}
        deferredPrompt={deferredPrompt}
        isInstalling={isInstalling}
      />
    </div>
  );
};

// Installation Guide Dialog Component - With Desktop Shortcut Download & Mobile Support
const InstallGuideDialog = ({ isOpen, onClose, onInstall, isRTL, benefits, deferredPrompt, isInstalling }) => {
  const [showMobileGuide, setShowMobileGuide] = useState(false);
  
  const isIOS = /iPhone|iPad|iPod/i.test(navigator.userAgent);
  const isAndroid = /Android/i.test(navigator.userAgent);
  const isMac = /Mac/i.test(navigator.userAgent) && !isIOS;
  const isWindows = /Win/i.test(navigator.userAgent);
  const isMobile = isIOS || isAndroid;

  // Get the current site URL for the shortcut
  const siteUrl = window.location.origin + '/portal';
  const siteName = 'بيان للتحقق والمطابقة (BAC)';

  // Download desktop shortcut for Windows (.url file)
  const downloadWindowsShortcut = () => {
    const content = `[InternetShortcut]
URL=${siteUrl}
IconIndex=0
`;
    const blob = new Blob([content], { type: 'application/internet-shortcut' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${siteName}.url`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    onClose();
  };

  // Download desktop shortcut for Mac (.webloc file)
  const downloadMacShortcut = () => {
    const content = `<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>URL</key>
    <string>${siteUrl}</string>
</dict>
</plist>`;
    const blob = new Blob([content], { type: 'application/x-apple-plist' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${siteName}.webloc`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    onClose();
  };

  const handleInstallClick = () => {
    if (deferredPrompt) {
      // Native PWA install available (works on Android Chrome)
      onInstall();
    } else if (isMobile) {
      // Show mobile instructions
      setShowMobileGuide(true);
    } else if (isWindows) {
      downloadWindowsShortcut();
    } else if (isMac) {
      downloadMacShortcut();
    } else {
      downloadWindowsShortcut();
    }
  };

  // Mobile Guide View
  if (showMobileGuide) {
    return (
      <Dialog open={isOpen} onOpenChange={onClose}>
        <DialogContent className={`sm:max-w-md ${isRTL ? 'rtl' : 'ltr'}`}>
          <DialogHeader>
            <DialogTitle className={`flex items-center gap-3 ${isRTL ? 'flex-row-reverse text-right' : ''}`}>
              <div className="w-14 h-14 bg-gradient-to-br from-[#1e3a5f] to-[#2a4a6f] rounded-2xl flex items-center justify-center shadow-lg">
                <Smartphone className="w-7 h-7 text-white" />
              </div>
              <div>
                <h3 className="text-xl font-bold text-[#1e3a5f]">
                  {isRTL ? 'إضافة للشاشة الرئيسية' : 'Add to Home Screen'}
                </h3>
                <p className="text-sm text-slate-500 font-normal">
                  {isIOS ? 'Safari' : 'Chrome'}
                </p>
              </div>
            </DialogTitle>
            <DialogDescription className="sr-only">
              {isRTL ? 'إضافة التطبيق للشاشة الرئيسية' : 'Add app to home screen'}
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 pt-4">
            {isIOS ? (
              // iOS Instructions
              <div className={`space-y-4 ${isRTL ? 'text-right' : 'text-left'}`}>
                <div className={`flex items-start gap-4 p-4 bg-slate-50 rounded-xl ${isRTL ? 'flex-row-reverse' : ''}`}>
                  <div className="w-10 h-10 bg-blue-500 rounded-xl flex items-center justify-center flex-shrink-0 text-white text-xl">
                    ⬆️
                  </div>
                  <div>
                    <p className="font-semibold text-slate-800 mb-1">
                      {isRTL ? 'الخطوة 1: اضغط على زر المشاركة' : 'Step 1: Tap Share button'}
                    </p>
                    <p className="text-sm text-slate-600">
                      {isRTL ? 'في أسفل الشاشة (Safari)' : 'At the bottom of screen (Safari)'}
                    </p>
                  </div>
                </div>
                
                <div className={`flex items-start gap-4 p-4 bg-slate-50 rounded-xl ${isRTL ? 'flex-row-reverse' : ''}`}>
                  <div className="w-10 h-10 bg-green-500 rounded-xl flex items-center justify-center flex-shrink-0 text-white text-xl">
                    ➕
                  </div>
                  <div>
                    <p className="font-semibold text-slate-800 mb-1">
                      {isRTL ? 'الخطوة 2: إضافة للشاشة الرئيسية' : 'Step 2: Add to Home Screen'}
                    </p>
                    <p className="text-sm text-slate-600">
                      {isRTL ? 'مرر للأسفل واضغط "إضافة إلى الشاشة الرئيسية"' : 'Scroll down and tap "Add to Home Screen"'}
                    </p>
                  </div>
                </div>

                <div className={`flex items-start gap-4 p-4 bg-slate-50 rounded-xl ${isRTL ? 'flex-row-reverse' : ''}`}>
                  <div className="w-10 h-10 bg-amber-500 rounded-xl flex items-center justify-center flex-shrink-0 text-white text-xl">
                    ✓
                  </div>
                  <div>
                    <p className="font-semibold text-slate-800 mb-1">
                      {isRTL ? 'الخطوة 3: اضغط إضافة' : 'Step 3: Tap Add'}
                    </p>
                    <p className="text-sm text-slate-600">
                      {isRTL ? 'سيظهر الأيقونة على شاشتك الرئيسية' : 'The icon will appear on your home screen'}
                    </p>
                  </div>
                </div>
              </div>
            ) : (
              // Android Instructions
              <div className={`space-y-4 ${isRTL ? 'text-right' : 'text-left'}`}>
                <div className={`flex items-start gap-4 p-4 bg-slate-50 rounded-xl ${isRTL ? 'flex-row-reverse' : ''}`}>
                  <div className="w-10 h-10 bg-blue-500 rounded-xl flex items-center justify-center flex-shrink-0 text-white text-xl font-bold">
                    ⋮
                  </div>
                  <div>
                    <p className="font-semibold text-slate-800 mb-1">
                      {isRTL ? 'الخطوة 1: اضغط على القائمة' : 'Step 1: Tap menu'}
                    </p>
                    <p className="text-sm text-slate-600">
                      {isRTL ? 'النقاط الثلاث في أعلى المتصفح' : 'Three dots at top of browser'}
                    </p>
                  </div>
                </div>
                
                <div className={`flex items-start gap-4 p-4 bg-slate-50 rounded-xl ${isRTL ? 'flex-row-reverse' : ''}`}>
                  <div className="w-10 h-10 bg-green-500 rounded-xl flex items-center justify-center flex-shrink-0 text-white text-xl">
                    📲
                  </div>
                  <div>
                    <p className="font-semibold text-slate-800 mb-1">
                      {isRTL ? 'الخطوة 2: تثبيت التطبيق' : 'Step 2: Install app'}
                    </p>
                    <p className="text-sm text-slate-600">
                      {isRTL ? 'اختر "تثبيت التطبيق" أو "إضافة إلى الشاشة الرئيسية"' : 'Select "Install app" or "Add to Home Screen"'}
                    </p>
                  </div>
                </div>

                <div className={`flex items-start gap-4 p-4 bg-slate-50 rounded-xl ${isRTL ? 'flex-row-reverse' : ''}`}>
                  <div className="w-10 h-10 bg-amber-500 rounded-xl flex items-center justify-center flex-shrink-0 text-white text-xl">
                    ✓
                  </div>
                  <div>
                    <p className="font-semibold text-slate-800 mb-1">
                      {isRTL ? 'الخطوة 3: تأكيد التثبيت' : 'Step 3: Confirm install'}
                    </p>
                    <p className="text-sm text-slate-600">
                      {isRTL ? 'سيظهر الأيقونة على شاشتك الرئيسية' : 'The icon will appear on your home screen'}
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Close Button */}
            <Button
              onClick={onClose}
              className="w-full h-12 bg-[#1e3a5f] hover:bg-[#152a45] text-white font-semibold"
            >
              {isRTL ? 'فهمت' : 'Got it'}
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    );
  }

  // Main Dialog View
  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className={`sm:max-w-md ${isRTL ? 'rtl' : 'ltr'}`}>
        <DialogHeader>
          <DialogTitle className={`flex items-center gap-3 ${isRTL ? 'flex-row-reverse text-right' : ''}`}>
            <div className="w-14 h-14 bg-gradient-to-br from-[#1e3a5f] to-[#2a4a6f] rounded-2xl flex items-center justify-center shadow-lg">
              <Download className="w-7 h-7 text-white" />
            </div>
            <div>
              <h3 className="text-xl font-bold text-[#1e3a5f]">
                {isMobile 
                  ? (isRTL ? 'إضافة للشاشة الرئيسية' : 'Add to Home Screen')
                  : (isRTL ? 'تحميل التطبيق' : 'Download App')
                }
              </h3>
              <p className="text-sm text-slate-500 font-normal">
                {isMobile
                  ? (isRTL ? 'أضف أيقونة للوصول السريع' : 'Add icon for quick access')
                  : (isRTL ? 'أضف اختصار لسطح المكتب' : 'Add shortcut to desktop')
                }
              </p>
            </div>
          </DialogTitle>
          <DialogDescription className="sr-only">
            {isRTL ? 'تحميل اختصار التطبيق' : 'Download app shortcut'}
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6 pt-4">
          {/* Benefits */}
          <div className={`space-y-3 ${isRTL ? 'text-right' : 'text-left'}`}>
            {benefits.map((benefit, idx) => (
              <div 
                key={idx} 
                className={`flex items-center gap-3 ${isRTL ? 'flex-row-reverse' : ''}`}
              >
                <div className="w-10 h-10 bg-emerald-100 rounded-xl flex items-center justify-center flex-shrink-0">
                  <benefit.icon className="w-5 h-5 text-emerald-600" />
                </div>
                <span className="text-sm text-slate-700 font-medium">{benefit.text}</span>
              </div>
            ))}
          </div>

          {/* Info box - different message for mobile vs desktop */}
          <div className={`p-4 bg-blue-50 border border-blue-100 rounded-xl ${isRTL ? 'text-right' : 'text-left'}`}>
            <p className="text-sm text-blue-800">
              {isMobile 
                ? (isRTL 
                    ? 'أضف أيقونة التطبيق إلى شاشتك الرئيسية للوصول السريع في أي وقت.'
                    : 'Add the app icon to your home screen for quick access anytime.')
                : (isRTL 
                    ? 'سيتم تحميل اختصار يمكنك وضعه على سطح المكتب. يمكنك أيضاً فتح الموقع في المتصفح في أي وقت.'
                    : 'A shortcut will be downloaded that you can place on your desktop. You can also open the site in the browser anytime.')
              }
            </p>
          </div>

          {/* Download/Install Button */}
          <Button
            onClick={handleInstallClick}
            disabled={isInstalling}
            className="w-full h-14 bg-[#1e3a5f] hover:bg-[#152a45] text-white text-lg font-semibold shadow-lg"
            data-testid="install-now-btn"
          >
            {isInstalling ? (
              <span className="animate-pulse">{isRTL ? 'جاري التحميل...' : 'Downloading...'}</span>
            ) : (
              <>
                <Download className={`w-5 h-5 ${isRTL ? 'ml-3' : 'mr-3'}`} />
                {isMobile
                  ? (isRTL ? 'إضافة للشاشة الرئيسية' : 'Add to Home Screen')
                  : (isRTL ? 'تحميل الآن' : 'Download Now')
                }
              </>
            )}
          </Button>

          {/* Close link */}
          <button
            onClick={onClose}
            className="w-full text-center text-sm text-slate-500 hover:text-slate-700"
          >
            {isRTL ? 'ليس الآن' : 'Not now'}
          </button>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default InstallAppButton;
