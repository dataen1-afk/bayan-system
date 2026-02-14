import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import LanguageSwitcher from '@/components/LanguageSwitcher';
import { 
  Search, CheckCircle, Clock, FileText, DollarSign, FileCheck, 
  Loader2, AlertCircle, ArrowRight, Building2, Mail, Phone,
  Calendar, Download, Eye
} from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL + '/api';

// Format date with Western Arabic numerals
const formatDate = (dateString) => {
  if (!dateString) return '-';
  return new Date(dateString).toLocaleDateString('en-GB', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  });
};

// Format currency with Western Arabic numerals and SAR
const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-US', { 
    minimumFractionDigits: 0,
    maximumFractionDigits: 0 
  }).format(amount || 0) + ' SAR';
};

const CustomerPortalPage = () => {
  const { trackingId } = useParams();
  const { t, i18n } = useTranslation();
  const isRTL = i18n.language?.startsWith('ar');
  
  const [searchId, setSearchId] = useState(trackingId || '');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [orderData, setOrderData] = useState(null);
  const [searched, setSearched] = useState(false);

  useEffect(() => {
    if (trackingId) {
      handleSearch();
    }
  }, [trackingId]);

  const handleSearch = async () => {
    if (!searchId.trim()) {
      setError(t('pleaseEnterTrackingId'));
      return;
    }
    
    setLoading(true);
    setError('');
    setSearched(true);
    
    try {
      const response = await axios.get(`${API}/public/track/${searchId.trim()}`);
      setOrderData(response.data);
    } catch (err) {
      console.error('Tracking error:', err);
      if (err.response?.status === 404) {
        setError(t('orderNotFound'));
      } else {
        setError(t('errorTrackingOrder'));
      }
      setOrderData(null);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  // Get status step index for timeline
  const getStatusStep = (status) => {
    const steps = ['pending', 'submitted', 'under_review', 'accepted', 'agreement_signed', 'contract_generated'];
    return steps.indexOf(status);
  };

  // Timeline steps
  const timelineSteps = [
    { key: 'pending', label: t('formCreated'), icon: FileText, description: t('formCreatedDesc') },
    { key: 'submitted', label: t('formSubmitted'), icon: CheckCircle, description: t('formSubmittedDesc') },
    { key: 'under_review', label: t('underReview'), icon: Clock, description: t('underReviewDesc') },
    { key: 'accepted', label: t('proposalAccepted'), icon: DollarSign, description: t('proposalAcceptedDesc') },
    { key: 'agreement_signed', label: t('agreementSigned'), icon: FileCheck, description: t('agreementSignedDesc') },
    { key: 'contract_generated', label: t('contractReady'), icon: Download, description: t('contractReadyDesc') }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-slate-50" dir={isRTL ? 'rtl' : 'ltr'}>
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-5xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className={`flex items-center gap-4 ${isRTL ? 'flex-row-reverse' : ''}`}>
            <img src="/bayan-logo.png" alt="Bayan" className="h-16 w-auto object-contain" />
          </div>
          <LanguageSwitcher />
        </div>
        <div className="h-1.5 bg-gradient-to-r from-bayan-navy via-bayan-navy-light to-bayan-navy"></div>
      </header>

      <main className="max-w-5xl mx-auto px-4 py-8">
        {/* Hero Section */}
        <div className={`text-center mb-8 ${isRTL ? 'text-right' : 'text-left'} md:text-center`}>
          <h1 className="text-3xl md:text-4xl font-bold text-bayan-navy mb-3">
            {t('customerPortal')}
          </h1>
          <p className="text-slate-600 text-lg">
            {t('trackYourApplicationStatus')}
          </p>
        </div>

        {/* Search Card */}
        <Card className="mb-8 border-slate-200 shadow-lg" data-testid="tracking-search-card">
          <CardHeader className={isRTL ? 'text-right' : 'text-left'}>
            <CardTitle className={`flex items-center gap-2 ${isRTL ? 'flex-row-reverse' : ''}`}>
              <Search className="w-5 h-5 text-bayan-navy" />
              {t('trackYourOrder')}
            </CardTitle>
            <CardDescription>{t('enterTrackingIdToViewStatus')}</CardDescription>
          </CardHeader>
          <CardContent>
            <div className={`flex gap-3 ${isRTL ? 'flex-row-reverse' : ''}`}>
              <div className="flex-1">
                <Input
                  type="text"
                  value={searchId}
                  onChange={(e) => setSearchId(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder={t('enterTrackingIdPlaceholder')}
                  className="h-12 text-lg"
                  data-testid="tracking-id-input"
                  dir="ltr"
                />
              </div>
              <Button 
                onClick={handleSearch} 
                disabled={loading}
                className="h-12 px-6 bg-bayan-navy hover:bg-bayan-navy-light"
                data-testid="search-tracking-btn"
              >
                {loading ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : (
                  <>
                    <Search className="w-5 h-5 me-2" />
                    {t('search')}
                  </>
                )}
              </Button>
            </div>
            
            {error && (
              <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center gap-3" data-testid="tracking-error">
                <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0" />
                <p className="text-red-700">{error}</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Order Status Results */}
        {orderData && (
          <div className="space-y-6" data-testid="tracking-results">
            {/* Order Summary Card */}
            <Card className="border-slate-200 shadow-lg">
              <CardHeader className={`bg-gradient-to-r from-bayan-navy to-bayan-navy-light text-white rounded-t-lg ${isRTL ? 'text-right' : 'text-left'}`}>
                <CardTitle className={`flex items-center gap-3 ${isRTL ? 'flex-row-reverse' : ''}`}>
                  <Building2 className="w-6 h-6" />
                  {orderData.company_name}
                </CardTitle>
                <CardDescription className="text-white/80">
                  {t('trackingId')}: <span className="font-mono font-semibold">{orderData.tracking_id}</span>
                </CardDescription>
              </CardHeader>
              <CardContent className="pt-6">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  {/* Contact Info */}
                  <div className={`space-y-3 ${isRTL ? 'text-right' : 'text-left'}`}>
                    <h4 className="font-semibold text-slate-700 mb-2">{t('contactInfo')}</h4>
                    <div className={`flex items-center gap-2 text-slate-600 ${isRTL ? 'flex-row-reverse' : ''}`}>
                      <Mail className="w-4 h-4 text-slate-400" />
                      <span>{orderData.contact_email || '-'}</span>
                    </div>
                    <div className={`flex items-center gap-2 text-slate-600 ${isRTL ? 'flex-row-reverse' : ''}`}>
                      <Phone className="w-4 h-4 text-slate-400" />
                      <span dir="ltr">{orderData.contact_phone || '-'}</span>
                    </div>
                  </div>
                  
                  {/* Application Date */}
                  <div className={`space-y-3 ${isRTL ? 'text-right' : 'text-left'}`}>
                    <h4 className="font-semibold text-slate-700 mb-2">{t('applicationDate')}</h4>
                    <div className={`flex items-center gap-2 text-slate-600 ${isRTL ? 'flex-row-reverse' : ''}`}>
                      <Calendar className="w-4 h-4 text-slate-400" />
                      <span>{formatDate(orderData.created_at)}</span>
                    </div>
                    {orderData.submitted_at && (
                      <p className="text-sm text-slate-500">
                        {t('submittedOn')}: {formatDate(orderData.submitted_at)}
                      </p>
                    )}
                  </div>
                  
                  {/* Standards */}
                  <div className={`space-y-3 ${isRTL ? 'text-right' : 'text-left'}`}>
                    <h4 className="font-semibold text-slate-700 mb-2">{t('certificationStandards')}</h4>
                    <div className={`flex flex-wrap gap-2 ${isRTL ? 'justify-end' : ''}`}>
                      {orderData.standards?.length > 0 ? (
                        orderData.standards.map((std) => (
                          <span key={std} className="px-3 py-1 bg-bayan-navy/10 text-bayan-navy text-sm font-medium rounded-full">
                            {std}
                          </span>
                        ))
                      ) : (
                        <span className="text-slate-400">{t('notSpecified')}</span>
                      )}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Status Timeline */}
            <Card className="border-slate-200 shadow-lg" data-testid="status-timeline-card">
              <CardHeader className={isRTL ? 'text-right' : 'text-left'}>
                <CardTitle className={`flex items-center gap-2 ${isRTL ? 'flex-row-reverse' : ''}`}>
                  <Clock className="w-5 h-5 text-bayan-navy" />
                  {t('applicationTimeline')}
                </CardTitle>
                <CardDescription>{t('trackProgressOfApplication')}</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="relative">
                  {/* Timeline Line */}
                  <div className={`absolute ${isRTL ? 'right-6' : 'left-6'} top-0 bottom-0 w-0.5 bg-slate-200`} />
                  
                  {/* Timeline Steps */}
                  <div className="space-y-6">
                    {timelineSteps.map((step, index) => {
                      const currentStep = getStatusStep(orderData.current_status);
                      const isCompleted = index <= currentStep;
                      const isCurrent = index === currentStep;
                      const Icon = step.icon;
                      
                      return (
                        <div 
                          key={step.key}
                          className={`relative flex items-start gap-4 ${isRTL ? 'flex-row-reverse' : ''}`}
                          data-testid={`timeline-step-${step.key}`}
                        >
                          {/* Step Circle */}
                          <div className={`
                            relative z-10 flex items-center justify-center w-12 h-12 rounded-full border-2 transition-all
                            ${isCompleted 
                              ? 'bg-emerald-500 border-emerald-500 text-white' 
                              : 'bg-white border-slate-300 text-slate-400'}
                            ${isCurrent ? 'ring-4 ring-emerald-100' : ''}
                          `}>
                            <Icon className="w-5 h-5" />
                          </div>
                          
                          {/* Step Content */}
                          <div className={`flex-1 pb-6 ${isRTL ? 'text-right' : 'text-left'}`}>
                            <div className={`flex items-center gap-2 ${isRTL ? 'flex-row-reverse justify-end' : ''}`}>
                              <h4 className={`font-semibold ${isCompleted ? 'text-slate-900' : 'text-slate-400'}`}>
                                {step.label}
                              </h4>
                              {isCurrent && (
                                <span className="px-2 py-0.5 bg-emerald-100 text-emerald-700 text-xs font-medium rounded-full">
                                  {t('current')}
                                </span>
                              )}
                            </div>
                            <p className={`text-sm mt-1 ${isCompleted ? 'text-slate-600' : 'text-slate-400'}`}>
                              {step.description}
                            </p>
                            {isCompleted && orderData.timeline_dates?.[step.key] && (
                              <p className="text-xs text-slate-500 mt-1">
                                {formatDate(orderData.timeline_dates[step.key])}
                              </p>
                            )}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Proposal/Contract Details if available */}
            {orderData.proposal && (
              <Card className="border-slate-200 shadow-lg" data-testid="proposal-details-card">
                <CardHeader className={isRTL ? 'text-right' : 'text-left'}>
                  <CardTitle className={`flex items-center gap-2 ${isRTL ? 'flex-row-reverse' : ''}`}>
                    <DollarSign className="w-5 h-5 text-bayan-navy" />
                    {t('proposalDetails')}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className={`space-y-3 ${isRTL ? 'text-right' : 'text-left'}`}>
                      <div className={`flex justify-between ${isRTL ? 'flex-row-reverse' : ''}`}>
                        <span className="text-slate-600">{t('totalAmount')}:</span>
                        <span className="font-bold text-xl text-bayan-navy">
                          {formatCurrency(orderData.proposal.total_amount)}
                        </span>
                      </div>
                      <div className={`flex justify-between ${isRTL ? 'flex-row-reverse' : ''}`}>
                        <span className="text-slate-600">{t('proposalStatus')}:</span>
                        <span className={`font-medium ${
                          orderData.proposal.status === 'accepted' || orderData.proposal.status === 'agreement_signed' 
                            ? 'text-emerald-600' 
                            : 'text-amber-600'
                        }`}>
                          {t(orderData.proposal.status)}
                        </span>
                      </div>
                    </div>
                    
                    {/* Action Buttons */}
                    <div className={`flex items-center gap-3 ${isRTL ? 'justify-start' : 'justify-end'}`}>
                      {orderData.proposal.access_token && (
                        <Button
                          variant="outline"
                          onClick={() => window.open(`/proposal/${orderData.proposal.access_token}`, '_blank')}
                          data-testid="view-proposal-btn"
                        >
                          <Eye className="w-4 h-4 me-2" />
                          {t('viewProposal')}
                        </Button>
                      )}
                      
                      {orderData.contract_available && orderData.proposal.access_token && (
                        <Button
                          onClick={async () => {
                            try {
                              const response = await axios.get(
                                `${API}/public/contracts/${orderData.proposal.access_token}/pdf`,
                                { responseType: 'blob' }
                              );
                              const url = window.URL.createObjectURL(new Blob([response.data]));
                              const link = document.createElement('a');
                              link.href = url;
                              link.setAttribute('download', `contract_${orderData.tracking_id}.pdf`);
                              document.body.appendChild(link);
                              link.click();
                              link.remove();
                            } catch (err) {
                              console.error('Error downloading contract:', err);
                            }
                          }}
                          className="bg-emerald-600 hover:bg-emerald-700"
                          data-testid="download-contract-btn"
                        >
                          <Download className="w-4 h-4 me-2" />
                          {t('downloadContract')}
                        </Button>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Help Section */}
            <Card className="border-blue-200 bg-blue-50/50">
              <CardContent className="pt-6">
                <div className={`flex items-start gap-4 ${isRTL ? 'flex-row-reverse text-right' : ''}`}>
                  <div className="p-3 bg-blue-100 rounded-full">
                    <Mail className="w-6 h-6 text-blue-600" />
                  </div>
                  <div>
                    <h4 className="font-semibold text-slate-800 mb-1">{t('needHelp')}</h4>
                    <p className="text-slate-600 text-sm mb-3">{t('contactUsForAssistance')}</p>
                    <a 
                      href="mailto:info@bayanauditing.com" 
                      className="text-bayan-navy hover:underline font-medium"
                    >
                      info@bayanauditing.com
                    </a>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Empty State when searched but no results */}
        {searched && !orderData && !loading && !error && (
          <Card className="border-slate-200">
            <CardContent className="py-12 text-center">
              <Search className="w-16 h-16 mx-auto text-slate-300 mb-4" />
              <h3 className="text-lg font-semibold text-slate-700 mb-2">{t('noResultsFound')}</h3>
              <p className="text-slate-500">{t('tryDifferentTrackingId')}</p>
            </CardContent>
          </Card>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t mt-12 py-6">
        <div className="max-w-5xl mx-auto px-4 text-center">
          <p className="text-slate-500 text-sm">
            © {new Date().getFullYear()} {t('bayanAuditingConformity')}. {t('allRightsReserved')}
          </p>
        </div>
      </footer>
    </div>
  );
};

export default CustomerPortalPage;
