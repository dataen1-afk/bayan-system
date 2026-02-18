import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Download, X, Smartphone } from 'lucide-react';
import { Button } from '@/components/ui/button';

const PWAInstallPrompt = ({ isRTL }) => {
  const [deferredPrompt, setDeferredPrompt] = useState(null);
  const [showPrompt, setShowPrompt] = useState(false);
  const [isInstalled, setIsInstalled] = useState(false);

  useEffect(() => {
    // Check if already installed
    if (window.matchMedia('(display-mode: standalone)').matches) {
      setIsInstalled(true);
      return;
    }

    // Check if user dismissed the prompt before
    const dismissed = localStorage.getItem('pwa-prompt-dismissed');
    if (dismissed) {
      const dismissedTime = parseInt(dismissed, 10);
      const daysSinceDismissed = (Date.now() - dismissedTime) / (1000 * 60 * 60 * 24);
      // Show again after 7 days
      if (daysSinceDismissed < 7) {
        return;
      }
    }

    const handleBeforeInstall = (e) => {
      e.preventDefault();
      setDeferredPrompt(e);
      // Show prompt after a short delay for better UX
      setTimeout(() => setShowPrompt(true), 2000);
    };

    const handleAppInstalled = () => {
      setIsInstalled(true);
      setShowPrompt(false);
      setDeferredPrompt(null);
    };

    window.addEventListener('beforeinstallprompt', handleBeforeInstall);
    window.addEventListener('appinstalled', handleAppInstalled);

    return () => {
      window.removeEventListener('beforeinstallprompt', handleBeforeInstall);
      window.removeEventListener('appinstalled', handleAppInstalled);
    };
  }, []);

  const handleInstall = async () => {
    if (!deferredPrompt) return;

    deferredPrompt.prompt();
    const { outcome } = await deferredPrompt.userChoice;
    
    if (outcome === 'accepted') {
      setShowPrompt(false);
    }
    setDeferredPrompt(null);
  };

  const handleDismiss = () => {
    setShowPrompt(false);
    localStorage.setItem('pwa-prompt-dismissed', Date.now().toString());
  };

  if (isInstalled || !showPrompt) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, y: 100 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: 100 }}
        transition={{ type: 'spring', damping: 25, stiffness: 300 }}
        className="fixed bottom-4 left-4 right-4 md:left-auto md:right-4 md:w-96 z-50"
      >
        <div className="bg-white rounded-2xl shadow-2xl border border-slate-200 overflow-hidden">
          {/* Header gradient */}
          <div className="bg-gradient-to-r from-[#1e3a5f] to-[#2a4a6f] px-4 py-3">
            <div className={`flex items-center justify-between ${isRTL ? 'flex-row-reverse' : ''}`}>
              <div className={`flex items-center gap-3 ${isRTL ? 'flex-row-reverse' : ''}`}>
                <div className="w-10 h-10 bg-white/20 rounded-xl flex items-center justify-center">
                  <Smartphone className="w-5 h-5 text-white" />
                </div>
                <div className={isRTL ? 'text-right' : 'text-left'}>
                  <h3 className="text-white font-semibold text-sm">
                    {isRTL ? 'تثبيت التطبيق' : 'Install App'}
                  </h3>
                  <p className="text-white/70 text-xs">
                    {isRTL ? 'بيان للتدقيق والمطابقة' : 'Bayan Audit'}
                  </p>
                </div>
              </div>
              <button
                onClick={handleDismiss}
                className="p-1.5 hover:bg-white/10 rounded-lg transition-colors"
                aria-label="Dismiss"
              >
                <X className="w-4 h-4 text-white/70" />
              </button>
            </div>
          </div>

          {/* Content */}
          <div className="p-4">
            <p className={`text-slate-600 text-sm mb-4 leading-relaxed ${isRTL ? 'text-right' : 'text-left'}`}>
              {isRTL 
                ? 'قم بتثبيت التطبيق للوصول السريع والعمل بدون اتصال بالإنترنت'
                : 'Install the app for quick access and offline functionality'}
            </p>

            <div className={`flex gap-3 ${isRTL ? 'flex-row-reverse' : ''}`}>
              <Button
                onClick={handleInstall}
                className="flex-1 bg-[#c9a55c] hover:bg-[#b08d45] text-white font-medium"
                data-testid="pwa-install-btn"
              >
                <Download className={`w-4 h-4 ${isRTL ? 'ml-2' : 'mr-2'}`} />
                {isRTL ? 'تثبيت' : 'Install'}
              </Button>
              <Button
                onClick={handleDismiss}
                variant="outline"
                className="border-slate-200 text-slate-600 hover:bg-slate-50"
                data-testid="pwa-dismiss-btn"
              >
                {isRTL ? 'لاحقاً' : 'Later'}
              </Button>
            </div>

            {/* Install benefits */}
            <div className={`mt-4 pt-4 border-t border-slate-100 ${isRTL ? 'text-right' : 'text-left'}`}>
              <p className="text-xs text-slate-400 mb-2">
                {isRTL ? 'المميزات:' : 'Benefits:'}
              </p>
              <ul className={`text-xs text-slate-500 space-y-1 ${isRTL ? 'pr-4' : 'pl-4'}`}>
                <li className={`flex items-center gap-2 ${isRTL ? 'flex-row-reverse' : ''}`}>
                  <span className="w-1 h-1 bg-[#c9a55c] rounded-full"></span>
                  {isRTL ? 'وصول سريع من الشاشة الرئيسية' : 'Quick access from home screen'}
                </li>
                <li className={`flex items-center gap-2 ${isRTL ? 'flex-row-reverse' : ''}`}>
                  <span className="w-1 h-1 bg-[#c9a55c] rounded-full"></span>
                  {isRTL ? 'العمل بدون اتصال' : 'Works offline'}
                </li>
                <li className={`flex items-center gap-2 ${isRTL ? 'flex-row-reverse' : ''}`}>
                  <span className="w-1 h-1 bg-[#c9a55c] rounded-full"></span>
                  {isRTL ? 'تجربة أسرع وأفضل' : 'Faster experience'}
                </li>
              </ul>
            </div>
          </div>
        </div>
      </motion.div>
    </AnimatePresence>
  );
};

export default PWAInstallPrompt;
