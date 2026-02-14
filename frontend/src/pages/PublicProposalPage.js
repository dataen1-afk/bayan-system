import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useParams, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { CheckCircle, AlertCircle, Loader2, FileText, Calendar, Users, Building, DollarSign, Clock, X, Edit3 } from 'lucide-react';
import LanguageSwitcher from '@/components/LanguageSwitcher';

const API = process.env.REACT_APP_BACKEND_URL + '/api';

const PublicProposalPage = () => {
  const { accessToken } = useParams();
  const navigate = useNavigate();
  const { t, i18n } = useTranslation();
  const isRTL = i18n.language?.startsWith('ar');
  
  const [proposal, setProposal] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [responding, setResponding] = useState(false);
  const [showAcceptModal, setShowAcceptModal] = useState(false);
  const [showRejectModal, setShowRejectModal] = useState(false);
  const [showModificationModal, setShowModificationModal] = useState(false);
  const [signatoryName, setSignatoryName] = useState('');
  const [signatoryDesignation, setSignatoryDesignation] = useState('');
  const [rejectionReason, setRejectionReason] = useState('');
  const [modificationComment, setModificationComment] = useState('');
  const [modificationChanges, setModificationChanges] = useState('');

  useEffect(() => {
    loadProposal();
  }, [accessToken]);

  const loadProposal = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await axios.get(`${API}/public/proposal/${accessToken}`);
      setProposal(response.data);
    } catch (error) {
      console.error('Error loading proposal:', error);
      if (error.response?.status === 404) {
        setError('proposalNotFound');
      } else {
        setError('errorLoadingProposal');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleAccept = async () => {
    if (!signatoryName || !signatoryDesignation) {
      alert(t('pleaseEnterSignatoryInfo'));
      return;
    }
    
    setResponding(true);
    try {
      await axios.post(`${API}/public/proposal/${accessToken}/respond`, {
        status: 'accepted',
        signatory_name: signatoryName,
        signatory_designation: signatoryDesignation
      });
      setShowAcceptModal(false);
      // Redirect to the certification agreement form
      navigate(`/agreement/${accessToken}`);
    } catch (error) {
      alert(t('errorRespondingToProposal') + ' ' + (error.response?.data?.detail || error.message));
    } finally {
      setResponding(false);
    }
  };

  const handleReject = async () => {
    setResponding(true);
    try {
      await axios.post(`${API}/public/proposal/${accessToken}/respond`, {
        status: 'rejected',
        signatory_name: signatoryName,
        signatory_designation: signatoryDesignation,
        rejection_reason: rejectionReason
      });
      setShowRejectModal(false);
      loadProposal();
    } catch (error) {
      alert(t('errorRespondingToProposal') + ' ' + (error.response?.data?.detail || error.message));
    } finally {
      setResponding(false);
    }
  };

  const handleRequestModification = async () => {
    if (!modificationComment.trim()) {
      alert(t('pleaseEnterModificationComment') || 'Please enter a comment explaining the requested modifications');
      return;
    }
    
    setResponding(true);
    try {
      await axios.post(`${API}/public/proposal/${accessToken}/request_modification`, {
        comment: modificationComment,
        requested_changes: modificationChanges
      });
      setShowModificationModal(false);
      loadProposal();
    } catch (error) {
      alert(t('errorRequestingModification') || 'Error requesting modification: ' + (error.response?.data?.detail || error.message));
    } finally {
      setResponding(false);
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat(isRTL ? 'ar-SA' : 'en-SA', {
      style: 'currency',
      currency: proposal?.service_fees?.currency || 'SAR'
    }).format(amount);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin text-bayan-navy mx-auto mb-4" />
          <p className="text-gray-600">{t('loadingProposal')}</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <Card className="w-full max-w-md">
          <CardContent className="pt-6">
            <div className="text-center">
              <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
              <h2 className="text-xl font-bold text-gray-800 mb-2">{t(error)}</h2>
              <p className="text-gray-600">{t('proposalLinkInvalid')}</p>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (proposal?.status === 'accepted' || proposal?.status === 'agreement_signed') {
    return (
      <div className="min-h-screen bg-gray-50" dir={isRTL ? 'rtl' : 'ltr'}>
        <Header isRTL={isRTL} />
        <main className="pt-28 pb-12 px-4">
          <div className="max-w-2xl mx-auto">
            <Card>
              <CardContent className="pt-8 pb-8">
                <div className="text-center">
                  <CheckCircle className="w-20 h-20 text-green-500 mx-auto mb-6" />
                  <h2 className="text-2xl font-bold text-gray-800 mb-4">{t('proposalAccepted')}</h2>
                  <p className="text-gray-600 mb-6">{t('thankYouForAccepting')}</p>
                  <div className="bg-green-50 border border-green-200 rounded-lg p-4 max-w-md mx-auto mb-6">
                    <p className="text-sm text-green-800">
                      {proposal?.status === 'agreement_signed' 
                        ? t('agreementAlreadySigned')
                        : t('pleaseCompleteAgreementForm')}
                    </p>
                  </div>
                  <Button 
                    onClick={() => navigate(`/agreement/${accessToken}`)}
                    size="lg"
                    className="bg-bayan-navy hover:bg-bayan-navy-light"
                    data-testid="continue-to-agreement-btn"
                  >
                    {proposal?.status === 'agreement_signed' 
                      ? t('viewAgreement') || t('continueToAgreement')
                      : t('continueToAgreement')}
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </main>
      </div>
    );
  }

  if (proposal?.status === 'rejected') {
    return (
      <div className="min-h-screen bg-gray-50" dir={isRTL ? 'rtl' : 'ltr'}>
        <Header isRTL={isRTL} />
        <main className="pt-28 pb-12 px-4">
          <div className="max-w-2xl mx-auto">
            <Card>
              <CardContent className="pt-8 pb-8">
                <div className="text-center">
                  <X className="w-20 h-20 text-red-500 mx-auto mb-6" />
                  <h2 className="text-2xl font-bold text-gray-800 mb-4">{t('proposalRejected')}</h2>
                  <p className="text-gray-600">{t('proposalWasRejected')}</p>
                </div>
              </CardContent>
            </Card>
          </div>
        </main>
      </div>
    );
  }

  if (proposal?.status === 'modification_requested') {
    return (
      <div className="min-h-screen bg-gray-50" dir={isRTL ? 'rtl' : 'ltr'}>
        <Header isRTL={isRTL} />
        <main className="pt-28 pb-12 px-4">
          <div className="max-w-2xl mx-auto">
            <Card>
              <CardContent className="pt-8 pb-8">
                <div className="text-center">
                  <Edit3 className="w-20 h-20 text-orange-500 mx-auto mb-6" />
                  <h2 className="text-2xl font-bold text-gray-800 mb-4">{t('modificationRequested') || 'Modification Requested'}</h2>
                  <p className="text-gray-600 mb-4">{t('modificationRequestSent') || 'Your modification request has been sent to the administrator.'}</p>
                  <div className="bg-orange-50 border border-orange-200 rounded-lg p-4 max-w-md mx-auto text-left">
                    <p className="text-sm text-orange-800 font-medium mb-2">{t('yourComment') || 'Your Comment'}:</p>
                    <p className="text-sm text-orange-700">{proposal?.modification_comment || '-'}</p>
                  </div>
                  <p className="text-gray-500 mt-4 text-sm">{t('waitingForResponse') || 'The administrator will review your request and respond shortly.'}</p>
                </div>
              </CardContent>
            </Card>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50" dir={isRTL ? 'rtl' : 'ltr'}>
      <Header isRTL={isRTL} />

      <main className="pt-28 pb-12 px-4">
        <div className="max-w-4xl mx-auto space-y-6">
          {/* Proposal Header */}
          <Card>
            <CardHeader className={isRTL ? 'text-right' : 'text-left'}>
              <CardTitle className="text-2xl text-bayan-navy flex items-center gap-2">
                <FileText className="w-6 h-6" />
                {t('proposalForCertification')}
              </CardTitle>
              <CardDescription>
                {t('proposalReference')}: {proposal?.id?.slice(0, 8)}
              </CardDescription>
            </CardHeader>
          </Card>

          {/* Organization Details */}
          <Card>
            <CardHeader className={isRTL ? 'text-right' : 'text-left'}>
              <CardTitle className="flex items-center gap-2">
                <Building className="w-5 h-5" />
                {t('organizationDetails')}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label className="text-gray-500">{t('organizationName')}</Label>
                  <p className="font-medium">{proposal?.organization_name}</p>
                </div>
                <div>
                  <Label className="text-gray-500">{t('contactPerson')}</Label>
                  <p className="font-medium">{proposal?.contact_person}</p>
                </div>
                <div>
                  <Label className="text-gray-500">{t('email')}</Label>
                  <p className="font-medium">{proposal?.contact_email}</p>
                </div>
                <div>
                  <Label className="text-gray-500">{t('totalEmployees')}</Label>
                  <p className="font-medium">{proposal?.total_employees}</p>
                </div>
                <div>
                  <Label className="text-gray-500">{t('numberOfSites')}</Label>
                  <p className="font-medium">{proposal?.number_of_sites}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Standards & Scope */}
          <Card>
            <CardHeader className={isRTL ? 'text-right' : 'text-left'}>
              <CardTitle className="flex items-center gap-2">
                <FileText className="w-5 h-5" />
                {t('standardsAndScope')}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <Label className="text-gray-500">{t('certificationStandards')}</Label>
                  <div className="flex flex-wrap gap-2 mt-1">
                    {proposal?.standards?.map((std, idx) => (
                      <span key={idx} className="px-3 py-1 bg-bayan-navy text-white rounded-full text-sm">
                        {std}
                      </span>
                    ))}
                  </div>
                </div>
                <div>
                  <Label className="text-gray-500">{t('tentativeScope')}</Label>
                  <p className="font-medium">{proposal?.scope || t('asPerApplication')}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Audit Duration */}
          <Card>
            <CardHeader className={isRTL ? 'text-right' : 'text-left'}>
              <CardTitle className="flex items-center gap-2">
                <Clock className="w-5 h-5" />
                {t('auditDuration')} ({t('manDays')})
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-5 gap-4 text-center">
                <div className="p-4 bg-gray-50 rounded-lg">
                  <p className="text-sm text-gray-500">Stage 1</p>
                  <p className="text-2xl font-bold text-bayan-navy">{proposal?.audit_duration?.stage_1 || 0}</p>
                </div>
                <div className="p-4 bg-gray-50 rounded-lg">
                  <p className="text-sm text-gray-500">Stage 2</p>
                  <p className="text-2xl font-bold text-bayan-navy">{proposal?.audit_duration?.stage_2 || 0}</p>
                </div>
                <div className="p-4 bg-gray-50 rounded-lg">
                  <p className="text-sm text-gray-500">Surveillance 1</p>
                  <p className="text-2xl font-bold text-bayan-navy">{proposal?.audit_duration?.surveillance_1 || 0}</p>
                </div>
                <div className="p-4 bg-gray-50 rounded-lg">
                  <p className="text-sm text-gray-500">Surveillance 2</p>
                  <p className="text-2xl font-bold text-bayan-navy">{proposal?.audit_duration?.surveillance_2 || 0}</p>
                </div>
                <div className="p-4 bg-gray-50 rounded-lg">
                  <p className="text-sm text-gray-500">{t('recertification')}</p>
                  <p className="text-2xl font-bold text-bayan-navy">{proposal?.audit_duration?.recertification || 0}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Service Fees */}
          <Card>
            <CardHeader className={isRTL ? 'text-right' : 'text-left'}>
              <CardTitle className="flex items-center gap-2">
                <DollarSign className="w-5 h-5" />
                {t('serviceFees')}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex justify-between items-center py-2 border-b">
                  <span>{t('initialCertification')}</span>
                  <span className="font-bold">{formatCurrency(proposal?.service_fees?.initial_certification || 0)}</span>
                </div>
                <div className="flex justify-between items-center py-2 border-b">
                  <span>Surveillance 1</span>
                  <span className="font-bold">{formatCurrency(proposal?.service_fees?.surveillance_1 || 0)}</span>
                </div>
                <div className="flex justify-between items-center py-2 border-b">
                  <span>Surveillance 2</span>
                  <span className="font-bold">{formatCurrency(proposal?.service_fees?.surveillance_2 || 0)}</span>
                </div>
                <div className="flex justify-between items-center py-3 bg-green-50 px-4 rounded-lg">
                  <span className="font-bold text-lg">{t('totalAmount')}</span>
                  <span className="font-bold text-xl text-green-700">{formatCurrency(proposal?.total_amount || 0)}</span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Terms and Conditions */}
          <Card>
            <CardHeader className={isRTL ? 'text-right' : 'text-left'}>
              <CardTitle>{t('termsAndConditions')}</CardTitle>
            </CardHeader>
            <CardContent>
              <ul className={`space-y-2 text-sm text-gray-600 ${isRTL ? 'list-disc pr-5' : 'list-disc pl-5'}`}>
                <li>{t('term1_payment')}</li>
                <li>{t('term2_tax')}</li>
                <li>{t('term3_travel')}</li>
                <li>{t('term4_validity')}</li>
                <li>{t('term5_cancellation')}</li>
              </ul>
            </CardContent>
          </Card>

          {/* Validity Notice */}
          <Card className="bg-yellow-50 border-yellow-200">
            <CardContent className="pt-6">
              <div className="flex items-center gap-3">
                <Calendar className="w-6 h-6 text-yellow-600" />
                <div>
                  <p className="font-medium text-yellow-800">{t('proposalValidity')}</p>
                  <p className="text-sm text-yellow-700">
                    {t('validFor')} {proposal?.validity_days} {t('days')}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Action Buttons */}
          <div className="flex gap-4 justify-center">
            <Button
              onClick={() => setShowRejectModal(true)}
              variant="outline"
              size="lg"
              className="px-8 border-red-300 text-red-600 hover:bg-red-50"
            >
              {t('rejectProposal')}
            </Button>
            <Button
              onClick={() => setShowAcceptModal(true)}
              size="lg"
              className="px-8 bg-green-600 hover:bg-green-700"
            >
              {t('acceptProposal')}
            </Button>
          </div>
        </div>
      </main>

      {/* Accept Modal */}
      {showAcceptModal && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <Card className="w-full max-w-md">
            <CardHeader>
              <CardTitle className="text-green-700">{t('acceptProposal')}</CardTitle>
              <CardDescription>{t('enterSignatoryDetails')}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label>{t('signatoryName')} *</Label>
                <Input
                  value={signatoryName}
                  onChange={(e) => setSignatoryName(e.target.value)}
                  placeholder={t('enterSignatoryName')}
                />
              </div>
              <div className="space-y-2">
                <Label>{t('signatoryDesignation')} *</Label>
                <Input
                  value={signatoryDesignation}
                  onChange={(e) => setSignatoryDesignation(e.target.value)}
                  placeholder={t('enterSignatoryDesignation')}
                />
              </div>
              <div className="flex gap-2 pt-4">
                <Button variant="outline" onClick={() => setShowAcceptModal(false)} className="flex-1">
                  {t('cancel')}
                </Button>
                <Button
                  onClick={handleAccept}
                  disabled={responding}
                  className="flex-1 bg-green-600 hover:bg-green-700"
                >
                  {responding ? <Loader2 className="w-4 h-4 animate-spin" /> : t('confirmAcceptance')}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Reject Modal */}
      {showRejectModal && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <Card className="w-full max-w-md">
            <CardHeader>
              <CardTitle className="text-red-700">{t('rejectProposal')}</CardTitle>
              <CardDescription>{t('pleaseProvideReason')}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label>{t('rejectionReason')}</Label>
                <Textarea
                  value={rejectionReason}
                  onChange={(e) => setRejectionReason(e.target.value)}
                  placeholder={t('enterRejectionReason')}
                  rows={3}
                />
              </div>
              <div className="flex gap-2 pt-4">
                <Button variant="outline" onClick={() => setShowRejectModal(false)} className="flex-1">
                  {t('cancel')}
                </Button>
                <Button
                  onClick={handleReject}
                  disabled={responding}
                  variant="destructive"
                  className="flex-1"
                >
                  {responding ? <Loader2 className="w-4 h-4 animate-spin" /> : t('confirmRejection')}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Footer */}
      <footer className="bg-bayan-navy text-white py-6 mt-12">
        <div className="max-w-7xl mx-auto px-4 text-center">
          <p className="text-sm opacity-80">
            © {new Date().getFullYear()} {t('bayanAuditingConformity')}. {t('allRightsReserved')}
          </p>
        </div>
      </footer>
    </div>
  );
};

// Header Component
const Header = ({ isRTL }) => (
  <header className="bg-white shadow-sm border-b fixed top-0 left-0 right-0 z-50">
    <div className="dashboard-header max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
      <div className="dashboard-header-left flex items-center gap-4">
        <img src="/Bayan-removebg-preview.png" alt="Bayan" className="h-16 w-auto object-contain" />
      </div>
      <div className="dashboard-header-right">
        <LanguageSwitcher />
      </div>
    </div>
    <div className="h-1.5 bg-gradient-to-r from-bayan-navy via-bayan-navy-light to-bayan-navy"></div>
  </header>
);

export default PublicProposalPage;
