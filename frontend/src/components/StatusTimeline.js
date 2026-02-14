import React from 'react';
import { useTranslation } from 'react-i18next';
import { Check, Clock, FileText, Send, ThumbsUp, FileSignature, FileCheck } from 'lucide-react';

const StatusTimeline = ({ status, compact = false }) => {
  const { t, i18n } = useTranslation();
  const isRTL = i18n.language?.startsWith('ar');

  // Define all possible statuses in order
  const allSteps = [
    { key: 'created', label: t('formCreated'), labelAr: 'تم إنشاء النموذج', icon: FileText },
    { key: 'submitted', label: t('formSubmitted'), labelAr: 'تم تقديم الطلب', icon: Send },
    { key: 'proposal_sent', label: t('proposalSent'), labelAr: 'تم إرسال العرض', icon: Send },
    { key: 'approved', label: t('proposalAccepted'), labelAr: 'تم قبول العرض', icon: ThumbsUp },
    { key: 'agreement_signed', label: t('agreementSigned'), labelAr: 'تم توقيع الاتفاقية', icon: FileSignature },
    { key: 'contract_generated', label: t('contractGenerated'), labelAr: 'تم إنشاء العقد', icon: FileCheck },
  ];

  // Map status to step index
  const getStepIndex = (currentStatus) => {
    const statusMap = {
      'pending': 0,
      'draft': 0,
      'submitted': 1,
      'under_review': 1,
      'proposal_sent': 2,
      'sent': 2,
      'approved': 3,
      'accepted': 3,
      'agreement_signed': 4,
      'contract_generated': 5,
      'rejected': -1,
    };
    return statusMap[currentStatus] ?? 0;
  };

  const currentStep = getStepIndex(status);
  const isRejected = status === 'rejected';

  if (compact) {
    // Compact version - just show current status with indicator
    const currentStepData = allSteps[Math.max(0, currentStep)] || allSteps[0];
    const Icon = currentStepData.icon;
    
    return (
      <div className={`flex items-center gap-2 ${isRTL ? 'flex-row-reverse' : ''}`}>
        <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
          isRejected ? 'bg-red-100 text-red-600' : 
          currentStep >= allSteps.length - 1 ? 'bg-green-100 text-green-600' : 
          'bg-blue-100 text-blue-600'
        }`}>
          {isRejected ? '✕' : <Icon className="w-4 h-4" />}
        </div>
        <span className={`text-sm font-medium ${
          isRejected ? 'text-red-600' : 
          currentStep >= allSteps.length - 1 ? 'text-green-600' : 
          'text-blue-600'
        }`}>
          {isRejected ? (isRTL ? 'مرفوض' : 'Rejected') : (isRTL ? currentStepData.labelAr : currentStepData.label)}
        </span>
        <span className="text-xs text-gray-400">
          ({currentStep + 1}/{allSteps.length})
        </span>
      </div>
    );
  }

  // Full timeline version
  return (
    <div className="py-4">
      <div className={`flex items-center ${isRTL ? 'flex-row-reverse' : ''}`}>
        {allSteps.map((step, index) => {
          const Icon = step.icon;
          const isCompleted = !isRejected && currentStep >= index;
          const isCurrent = currentStep === index;
          
          return (
            <React.Fragment key={step.key}>
              {/* Step */}
              <div className="flex flex-col items-center">
                <div 
                  className={`w-10 h-10 rounded-full flex items-center justify-center transition-all ${
                    isRejected && index > 0 ? 'bg-gray-100 text-gray-400' :
                    isCompleted ? 'bg-green-500 text-white' : 
                    isCurrent ? 'bg-blue-500 text-white' : 
                    'bg-gray-200 text-gray-400'
                  }`}
                >
                  {isCompleted && !isCurrent ? (
                    <Check className="w-5 h-5" />
                  ) : (
                    <Icon className="w-5 h-5" />
                  )}
                </div>
                <span className={`text-xs mt-2 text-center max-w-[80px] ${
                  isCompleted ? 'text-green-600 font-medium' : 
                  isCurrent ? 'text-blue-600 font-medium' : 
                  'text-gray-400'
                }`}>
                  {isRTL ? step.labelAr : step.label}
                </span>
              </div>
              
              {/* Connector line */}
              {index < allSteps.length - 1 && (
                <div 
                  className={`flex-1 h-1 mx-1 ${
                    isRejected && index > 0 ? 'bg-gray-200' :
                    currentStep > index ? 'bg-green-500' : 'bg-gray-200'
                  }`}
                />
              )}
            </React.Fragment>
          );
        })}
      </div>
      
      {/* Rejected badge */}
      {isRejected && (
        <div className="mt-4 text-center">
          <span className="inline-flex items-center gap-1 px-3 py-1 bg-red-100 text-red-600 rounded-full text-sm">
            ✕ {isRTL ? 'تم رفض العرض' : 'Proposal Rejected'}
          </span>
        </div>
      )}
    </div>
  );
};

export default StatusTimeline;
