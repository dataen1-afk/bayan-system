import React from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { ArrowLeft, FileText } from 'lucide-react';
import DocumentManagementPage from '@/components/DocumentManagement';

const DocumentsPage = () => {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const isRTL = i18n.language?.startsWith('ar');

  return (
    <div className="min-h-screen bg-gray-50" dir={isRTL ? 'rtl' : 'ltr'}>
      {/* Header */}
      <div className="bg-white border-b px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className={`flex items-center gap-4 ${isRTL ? 'flex-row-reverse' : ''}`}>
            <Button 
              variant="ghost" 
              onClick={() => navigate('/dashboard')}
              className={isRTL ? 'flex-row-reverse' : ''}
              data-testid="back-to-dashboard-btn"
            >
              <ArrowLeft className={`w-4 h-4 ${isRTL ? 'ml-2 rotate-180' : 'mr-2'}`} />
              {t('backToDashboard')}
            </Button>
            <h1 className="text-2xl font-bold text-bayan-navy flex items-center gap-2">
              <FileText className="w-6 h-6" />
              {t('documents')}
            </h1>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        <DocumentManagementPage />
      </div>
    </div>
  );
};

export default DocumentsPage;
