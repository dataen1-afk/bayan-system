import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useSearchParams } from 'react-router-dom';
import { FileWarning, FileBadge } from 'lucide-react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import Stage1AuditReportsContent from './Stage1AuditReportsPage';
import Stage2AuditReportsContent from './Stage2AuditReportsPage';

export default function AuditReportsPage() {
  const { t, i18n } = useTranslation();
  const isRTL = i18n.language === 'ar';
  const [searchParams, setSearchParams] = useSearchParams();
  const defaultTab = searchParams.get('stage') || 'stage1';
  const [activeTab, setActiveTab] = useState(defaultTab);

  const handleTabChange = (value) => {
    setActiveTab(value);
    setSearchParams({ stage: value });
  };

  return (
    <div className="p-6" dir={isRTL ? 'rtl' : 'ltr'}>
      <div className={`mb-6 ${isRTL ? 'text-right' : 'text-left'}`}>
        <h1 className="text-2xl font-bold text-slate-800 mb-2">
          {t('auditReports')}
        </h1>
        <p className="text-slate-500">
          {isRTL ? 'إدارة تقارير التدقيق للمرحلة الأولى والثانية' : 'Manage Stage 1 and Stage 2 audit reports'}
        </p>
      </div>

      <Tabs value={activeTab} onValueChange={handleTabChange} className="w-full">
        <TabsList className={`grid w-full max-w-md grid-cols-2 mb-6 ${isRTL ? 'mr-0 ml-auto' : ''}`}>
          {isRTL ? (
            <>
              <TabsTrigger 
                value="stage2" 
                className="flex items-center gap-2 flex-row-reverse"
                data-testid="audit-reports-stage2-tab"
              >
                <FileBadge className="w-4 h-4" />
                {t('stage2Tab')}
              </TabsTrigger>
              <TabsTrigger 
                value="stage1" 
                className="flex items-center gap-2 flex-row-reverse"
                data-testid="audit-reports-stage1-tab"
              >
                <FileWarning className="w-4 h-4" />
                {t('stage1Tab')}
              </TabsTrigger>
            </>
          ) : (
            <>
              <TabsTrigger 
                value="stage1" 
                className="flex items-center gap-2"
                data-testid="audit-reports-stage1-tab"
              >
                <FileWarning className="w-4 h-4" />
                {t('stage1Tab')}
              </TabsTrigger>
              <TabsTrigger 
                value="stage2" 
                className="flex items-center gap-2"
                data-testid="audit-reports-stage2-tab"
              >
                <FileBadge className="w-4 h-4" />
                {t('stage2Tab')}
              </TabsTrigger>
            </>
          )}
        </TabsList>

        <TabsContent value="stage1">
          <Stage1AuditReportsContent embedded={true} />
        </TabsContent>

        <TabsContent value="stage2">
          <Stage2AuditReportsContent embedded={true} />
        </TabsContent>
      </Tabs>
    </div>
  );
}
