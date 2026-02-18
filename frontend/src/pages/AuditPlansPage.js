import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useSearchParams } from 'react-router-dom';
import { FileSpreadsheet, FileStack } from 'lucide-react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import Stage1AuditPlansContent from './Stage1AuditPlansPage';
import Stage2AuditPlansContent from './Stage2AuditPlansPage';

export default function AuditPlansPage() {
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
          {t('auditPlans')}
        </h1>
        <p className="text-slate-500">
          {isRTL ? 'إدارة خطط التدقيق للمرحلة الأولى والثانية' : 'Manage Stage 1 and Stage 2 audit plans'}
        </p>
      </div>

      <Tabs value={activeTab} onValueChange={handleTabChange} className="w-full">
        <TabsList className={`grid w-full max-w-md grid-cols-2 mb-6 ${isRTL ? 'mr-0 ml-auto' : ''}`}>
          {isRTL ? (
            <>
              <TabsTrigger 
                value="stage2" 
                className="flex items-center gap-2 flex-row-reverse"
                data-testid="audit-plans-stage2-tab"
              >
                <FileStack className="w-4 h-4" />
                {t('stage2Tab')}
              </TabsTrigger>
              <TabsTrigger 
                value="stage1" 
                className="flex items-center gap-2 flex-row-reverse"
                data-testid="audit-plans-stage1-tab"
              >
                <FileSpreadsheet className="w-4 h-4" />
                {t('stage1Tab')}
              </TabsTrigger>
            </>
          ) : (
            <>
              <TabsTrigger 
                value="stage1" 
                className="flex items-center gap-2"
                data-testid="audit-plans-stage1-tab"
              >
                <FileSpreadsheet className="w-4 h-4" />
                {t('stage1Tab')}
              </TabsTrigger>
              <TabsTrigger 
                value="stage2" 
                className="flex items-center gap-2"
                data-testid="audit-plans-stage2-tab"
              >
                <FileStack className="w-4 h-4" />
                {t('stage2Tab')}
              </TabsTrigger>
            </>
          )}
        </TabsList>

        <TabsContent value="stage1">
          <Stage1AuditPlansContent embedded={true} />
        </TabsContent>

        <TabsContent value="stage2">
          <Stage2AuditPlansContent embedded={true} />
        </TabsContent>
      </Tabs>
    </div>
  );
}
