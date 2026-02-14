import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useParams, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Checkbox } from '@/components/ui/checkbox';
import { CheckCircle, AlertCircle, Loader2, FileText, Building, Shield, Clock, Users, MapPin, FileSignature, Pen } from 'lucide-react';
import LanguageSwitcher from '@/components/LanguageSwitcher';
import SignaturePad from '@/components/SignaturePad';

const API = process.env.REACT_APP_BACKEND_URL + '/api';

const CertificationAgreementPage = () => {
  const { accessToken } = useParams();
  const navigate = useNavigate();
  const { t, i18n } = useTranslation();
  const isRTL = i18n.language?.startsWith('ar');
  
  const [proposal, setProposal] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [submitted, setSubmitted] = useState(false);
  
  // Agreement form data
  const [formData, setFormData] = useState({
    // Organization Details (pre-filled from proposal, editable)
    organizationName: '',
    organizationAddress: '',
    
    // Management System Standards (checkboxes)
    selectedStandards: [],
    otherStandard: '',
    
    // Scope of Services
    scopeOfServices: '',
    
    // Sites
    sites: [''],
    
    // Signatory Information
    signatoryName: '',
    signatoryPosition: '',
    signatoryDate: new Date().toISOString().split('T')[0],
    
    // Acknowledgements
    acknowledgements: {
      certificationRules: false,
      publicDirectory: false,
      certificationCommunication: false,
      surveillanceSchedule: false,
      nonconformityResolution: false,
      feesAndPayment: false
    },
    
    // Digital Signature
    signatureImage: null,
    stampImage: null
  });

  // Available ISO Standards
  const availableStandards = [
    { id: 'ISO9001', label: 'ISO 9001:2015 - Quality Management System' },
    { id: 'ISO14001', label: 'ISO 14001:2015 - Environmental Management System' },
    { id: 'ISO45001', label: 'ISO 45001:2018 - Occupational Health & Safety' },
    { id: 'ISO22000', label: 'ISO 22000:2018 - Food Safety Management System' },
    { id: 'ISO27001', label: 'ISO/IEC 27001:2022 - Information Security Management' },
    { id: 'ISO13485', label: 'ISO 13485:2016 - Medical Devices Quality Management' },
    { id: 'ISO50001', label: 'ISO 50001:2018 - Energy Management System' },
    { id: 'ISO22301', label: 'ISO 22301:2019 - Business Continuity Management' }
  ];

  useEffect(() => {
    loadProposal();
  }, [accessToken]);

  const loadProposal = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // First check if agreement already exists
      try {
        const agreementResponse = await axios.get(`${API}/public/agreement/${accessToken}`);
        if (agreementResponse.data.status === 'submitted') {
          // Agreement already submitted, show success
          setSubmitted(true);
          setLoading(false);
          return;
        }
      } catch (err) {
        // If 400 error, it means proposal not accepted yet - continue to check proposal
        if (err.response?.status !== 400) {
          console.error('Error checking agreement status:', err);
        }
      }
      
      const response = await axios.get(`${API}/public/proposal/${accessToken}`);
      const proposalData = response.data;
      
      // Check if proposal is accepted or agreement_signed (both are valid states)
      if (proposalData.status !== 'accepted' && proposalData.status !== 'agreement_signed') {
        setError('agreementNotAvailable');
        setLoading(false);
        return;
      }
      
      // If status is agreement_signed, the agreement was already submitted
      if (proposalData.status === 'agreement_signed') {
        setSubmitted(true);
        setLoading(false);
        return;
      }
      
      setProposal(proposalData);
      
      // Pre-fill form data from proposal
      setFormData(prev => ({
        ...prev,
        organizationName: proposalData.organization_name || '',
        organizationAddress: proposalData.organization_address || '',
        selectedStandards: proposalData.standards || [],
        scopeOfServices: proposalData.scope || '',
        sites: proposalData.number_of_sites > 1 ? Array(proposalData.number_of_sites).fill('') : ['']
      }));
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

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleStandardToggle = (standardId) => {
    setFormData(prev => ({
      ...prev,
      selectedStandards: prev.selectedStandards.includes(standardId)
        ? prev.selectedStandards.filter(s => s !== standardId)
        : [...prev.selectedStandards, standardId]
    }));
  };

  const handleAcknowledgementToggle = (key) => {
    setFormData(prev => ({
      ...prev,
      acknowledgements: {
        ...prev.acknowledgements,
        [key]: !prev.acknowledgements[key]
      }
    }));
  };

  const handleSiteChange = (index, value) => {
    const newSites = [...formData.sites];
    newSites[index] = value;
    setFormData(prev => ({ ...prev, sites: newSites }));
  };

  const addSite = () => {
    setFormData(prev => ({ ...prev, sites: [...prev.sites, ''] }));
  };

  const removeSite = (index) => {
    if (formData.sites.length > 1) {
      const newSites = formData.sites.filter((_, i) => i !== index);
      setFormData(prev => ({ ...prev, sites: newSites }));
    }
  };

  const validateForm = () => {
    // Required fields validation
    if (!formData.organizationName || !formData.organizationAddress) {
      alert(t('fillOrganizationDetails'));
      return false;
    }
    if (formData.selectedStandards.length === 0) {
      alert(t('selectAtLeastOneStandard'));
      return false;
    }
    if (!formData.scopeOfServices) {
      alert(t('fillScopeOfServices'));
      return false;
    }
    if (!formData.signatoryName || !formData.signatoryPosition) {
      alert(t('fillSignatoryDetails'));
      return false;
    }
    // Check all acknowledgements
    const allAcknowledged = Object.values(formData.acknowledgements).every(v => v);
    if (!allAcknowledged) {
      alert(t('acceptAllAcknowledgements'));
      return false;
    }
    // Check digital signature
    if (!formData.signatureImage) {
      alert(t('pleaseProvideSignature') || 'Please provide your digital signature');
      return false;
    }
    // Check company seal
    if (!formData.stampImage) {
      alert(t('pleaseProvideCompanySeal') || 'Please provide your company seal/stamp');
      return false;
    }
    return true;
  };

  const handleSubmit = async () => {
    if (!validateForm()) return;
    
    setSubmitting(true);
    try {
      await axios.post(`${API}/public/agreement/${accessToken}/submit`, {
        organization_name: formData.organizationName,
        organization_address: formData.organizationAddress,
        selected_standards: formData.selectedStandards,
        other_standard: formData.otherStandard,
        scope_of_services: formData.scopeOfServices,
        sites: formData.sites.filter(s => s.trim() !== ''),
        signatory_name: formData.signatoryName,
        signatory_position: formData.signatoryPosition,
        signatory_date: formData.signatoryDate,
        acknowledgements: formData.acknowledgements,
        signature_image: formData.signatureImage,
        stamp_image: formData.stampImage
      });
      setSubmitted(true);
    } catch (error) {
      console.error('Error submitting agreement:', error);
      alert(t('errorSubmittingAgreement') + ' ' + (error.response?.data?.detail || error.message));
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin text-bayan-navy mx-auto mb-4" />
          <p className="text-gray-600">{t('loadingAgreement')}</p>
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
              <p className="text-gray-600">{t('agreementLinkInvalid')}</p>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (submitted) {
    // Auto-redirect to Customer Portal after 5 seconds
    const redirectToPortal = () => {
      window.location.href = `/track/${accessToken}`;
    };

    return (
      <div className="min-h-screen bg-gray-50" dir={isRTL ? 'rtl' : 'ltr'}>
        <Header isRTL={isRTL} />
        <main className="pt-28 pb-12 px-4">
          <div className="max-w-2xl mx-auto">
            <Card>
              <CardContent className="pt-8 pb-8">
                <div className="text-center">
                  <CheckCircle className="w-20 h-20 text-green-500 mx-auto mb-6" />
                  <h2 className="text-2xl font-bold text-gray-800 mb-4">{t('agreementSubmitted')}</h2>
                  <p className="text-gray-600 mb-6">{t('thankYouForAgreement')}</p>
                  <div className="bg-green-50 border border-green-200 rounded-lg p-4 max-w-md mx-auto mb-6">
                    <p className="text-sm text-green-800">
                      {t('contractWillBePrepared')}
                    </p>
                  </div>
                  
                  {/* Redirect to Customer Portal */}
                  <div className="mt-6 space-y-4">
                    <p className="text-sm text-gray-500">
                      {t('redirectingToPortal') || 'You will be redirected to track your order...'}
                    </p>
                    <Button 
                      onClick={redirectToPortal}
                      className="bg-bayan-navy hover:bg-bayan-navy-light"
                      data-testid="go-to-portal-btn"
                    >
                      {t('trackYourOrder') || 'Track Your Order'}
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </main>
        <Footer />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50" dir={isRTL ? 'rtl' : 'ltr'}>
      <Header isRTL={isRTL} />

      <main className="pt-28 pb-12 px-4">
        <div className="max-w-4xl mx-auto space-y-6">
          {/* Page Header */}
          <Card className="bg-bayan-navy text-white">
            <CardContent className="pt-6 pb-6">
              <div className={`flex items-center gap-4 ${isRTL ? 'flex-row-reverse' : ''}`}>
                <FileSignature className="w-12 h-12" />
                <div className={isRTL ? 'text-right' : 'text-left'}>
                  <h1 className="text-2xl font-bold">{t('certificationAgreement')}</h1>
                  <p className="text-blue-100">{t('agreementSubtitle')}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Section 1: Parties to Agreement */}
          <Card>
            <CardHeader className={isRTL ? 'text-right' : 'text-left'}>
              <CardTitle className="flex items-center gap-2">
                <Shield className="w-5 h-5 text-bayan-navy" />
                {t('partiesToAgreement')}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {/* Certification Body (Read-only) */}
                <div className="p-4 bg-gray-50 rounded-lg">
                  <Label className="text-gray-500 text-sm">{t('certificationBody')}</Label>
                  <p className="font-semibold text-bayan-navy">BAYAN AUDITING & CONFORMITY (BAC)</p>
                  <p className="text-sm text-gray-600">Arabia Limited Certification Body</p>
                  <p className="text-sm text-gray-600">3879 Al Khadar Street, Riyadh, 12282, Saudi Arabia</p>
                </div>
                
                {/* Client Organization (Editable) */}
                <div className="space-y-4">
                  <div className="space-y-2">
                    <Label>{t('clientOrganization')} *</Label>
                    <Input
                      value={formData.organizationName}
                      onChange={(e) => handleInputChange('organizationName', e.target.value)}
                      placeholder={t('enterOrganizationName')}
                      className={isRTL ? 'text-right' : ''}
                      data-testid="organization-name-input"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>{t('organizationAddress')} *</Label>
                    <Textarea
                      value={formData.organizationAddress}
                      onChange={(e) => handleInputChange('organizationAddress', e.target.value)}
                      placeholder={t('enterOrganizationAddress')}
                      rows={2}
                      className={isRTL ? 'text-right' : ''}
                      data-testid="organization-address-input"
                    />
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Section 2: Purpose and Scope */}
          <Card>
            <CardHeader className={isRTL ? 'text-right' : 'text-left'}>
              <CardTitle className="flex items-center gap-2">
                <FileText className="w-5 h-5 text-bayan-navy" />
                {t('purposeAndScope')}
              </CardTitle>
              <CardDescription>{t('selectStandardsForCertification')}</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {/* Management System Standards */}
                <div className="space-y-3">
                  <Label className="text-base font-semibold">{t('managementSystemStandards')} *</Label>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {availableStandards.map((standard) => (
                      <label 
                        key={standard.id}
                        className={`flex items-start gap-3 p-3 border rounded-lg cursor-pointer transition-colors select-none ${
                          formData.selectedStandards.includes(standard.id) 
                            ? 'bg-blue-50 border-blue-300' 
                            : 'hover:bg-gray-50'
                        }`}
                        data-testid={`standard-${standard.id}`}
                      >
                        <Checkbox 
                          checked={formData.selectedStandards.includes(standard.id)}
                          onCheckedChange={() => handleStandardToggle(standard.id)}
                          className="mt-0.5"
                        />
                        <span className="text-sm">{standard.label}</span>
                      </label>
                    ))}
                  </div>
                  
                  {/* Other Standard */}
                  <div className="flex items-center gap-3 p-3 border rounded-lg">
                    <Checkbox 
                      checked={formData.otherStandard !== ''}
                      onCheckedChange={() => {}}
                    />
                    <span className="text-sm">{t('other')}:</span>
                    <Input
                      value={formData.otherStandard}
                      onChange={(e) => handleInputChange('otherStandard', e.target.value)}
                      placeholder={t('specifyOtherStandard')}
                      className="flex-1"
                      data-testid="other-standard-input"
                    />
                  </div>
                </div>

                {/* Scope of Services */}
                <div className="space-y-2">
                  <Label className="text-base font-semibold">{t('scopeOfServices')} *</Label>
                  <Textarea
                    value={formData.scopeOfServices}
                    onChange={(e) => handleInputChange('scopeOfServices', e.target.value)}
                    placeholder={t('describeScopeOfServices')}
                    rows={4}
                    className={isRTL ? 'text-right' : ''}
                    data-testid="scope-of-services-input"
                  />
                </div>

                {/* Sites */}
                <div className="space-y-3">
                  <Label className="text-base font-semibold flex items-center gap-2">
                    <MapPin className="w-4 h-4" />
                    {t('sitesForCertification')}
                  </Label>
                  {formData.sites.map((site, index) => (
                    <div key={index} className={`flex gap-2 ${isRTL ? 'flex-row-reverse' : ''}`}>
                      <Input
                        value={site}
                        onChange={(e) => handleSiteChange(index, e.target.value)}
                        placeholder={`${t('site')} ${index + 1} - ${t('enterAddress')}`}
                        className={`flex-1 ${isRTL ? 'text-right' : ''}`}
                        data-testid={`site-${index}-input`}
                      />
                      {formData.sites.length > 1 && (
                        <Button 
                          variant="outline" 
                          size="icon"
                          onClick={() => removeSite(index)}
                          className="text-red-500 hover:text-red-700"
                        >
                          ×
                        </Button>
                      )}
                    </div>
                  ))}
                  <Button variant="outline" size="sm" onClick={addSite} data-testid="add-site-btn">
                    + {t('addSite')}
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Section: Acknowledgements */}
          <Card>
            <CardHeader className={isRTL ? 'text-right' : 'text-left'}>
              <CardTitle className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-bayan-navy" />
                {t('acknowledgements')}
              </CardTitle>
              <CardDescription>{t('pleaseConfirmFollowing')}</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {[
                  { key: 'certificationRules', label: t('ack_certificationRules') },
                  { key: 'publicDirectory', label: t('ack_publicDirectory') },
                  { key: 'certificationCommunication', label: t('ack_certificationCommunication') },
                  { key: 'surveillanceSchedule', label: t('ack_surveillanceSchedule') },
                  { key: 'nonconformityResolution', label: t('ack_nonconformityResolution') },
                  { key: 'feesAndPayment', label: t('ack_feesAndPayment') }
                ].map((item) => (
                  <label 
                    key={item.key}
                    className={`flex items-start gap-3 p-3 border rounded-lg cursor-pointer transition-colors select-none ${
                      formData.acknowledgements[item.key] 
                        ? 'bg-green-50 border-green-300' 
                        : 'hover:bg-gray-50'
                    }`}
                    data-testid={`ack-${item.key}`}
                  >
                    <Checkbox 
                      checked={formData.acknowledgements[item.key]}
                      onCheckedChange={() => handleAcknowledgementToggle(item.key)}
                      className="mt-0.5"
                    />
                    <span className="text-sm">{item.label}</span>
                  </label>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Section: Signatory Information */}
          <Card>
            <CardHeader className={isRTL ? 'text-right' : 'text-left'}>
              <CardTitle className="flex items-center gap-2">
                <Users className="w-5 h-5 text-bayan-navy" />
                {t('signatoryInformation')}
              </CardTitle>
              <CardDescription>{t('authorizedSignatoryDetails')}</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>{t('signatoryName')} *</Label>
                  <Input
                    value={formData.signatoryName}
                    onChange={(e) => handleInputChange('signatoryName', e.target.value)}
                    placeholder={t('enterSignatoryName')}
                    className={isRTL ? 'text-right' : ''}
                    data-testid="signatory-name-input"
                  />
                </div>
                <div className="space-y-2">
                  <Label>{t('signatoryPosition')} *</Label>
                  <Input
                    value={formData.signatoryPosition}
                    onChange={(e) => handleInputChange('signatoryPosition', e.target.value)}
                    placeholder={t('enterSignatoryPosition')}
                    className={isRTL ? 'text-right' : ''}
                    data-testid="signatory-position-input"
                  />
                </div>
                <div className="space-y-2">
                  <Label>{t('date')}</Label>
                  <Input
                    type="date"
                    value={formData.signatoryDate}
                    onChange={(e) => handleInputChange('signatoryDate', e.target.value)}
                    data-testid="signatory-date-input"
                  />
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Section: Digital Signature */}
          <Card>
            <CardHeader className={isRTL ? 'text-right' : 'text-left'}>
              <CardTitle className="flex items-center gap-2">
                <Pen className="w-5 h-5 text-bayan-navy" />
                {t('digitalSignatureSection') || 'Digital Signature & Seal'}
              </CardTitle>
              <CardDescription>{t('signatureInstructions') || 'Please provide your digital signature. You can draw it or upload an image.'}</CardDescription>
            </CardHeader>
            <CardContent>
              <SignaturePad
                onSignatureChange={(signature) => handleInputChange('signatureImage', signature)}
                onStampChange={(stamp) => handleInputChange('stampImage', stamp)}
                initialSignature={formData.signatureImage}
                initialStamp={formData.stampImage}
                showStamp={true}
              />
            </CardContent>
          </Card>

          {/* Submit Button */}
          <div className="flex justify-center py-4">
            <Button
              onClick={handleSubmit}
              disabled={submitting}
              size="lg"
              className="px-12 bg-green-600 hover:bg-green-700"
              data-testid="submit-agreement-btn"
            >
              {submitting ? (
                <>
                  <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                  {t('submitting')}
                </>
              ) : (
                <>
                  <FileSignature className="w-5 h-5 mr-2" />
                  {t('submitAgreement')}
                </>
              )}
            </Button>
          </div>
        </div>
      </main>

      <Footer />
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

// Footer Component
const Footer = () => {
  const { t } = useTranslation();
  return (
    <footer className="bg-bayan-navy text-white py-6 mt-12">
      <div className="max-w-7xl mx-auto px-4 text-center">
        <p className="text-sm opacity-80">
          © {new Date().getFullYear()} {t('bayanAuditingConformity')}. {t('allRightsReserved')}
        </p>
      </div>
    </footer>
  );
};

export default CertificationAgreementPage;
