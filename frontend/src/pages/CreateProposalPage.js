import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { ArrowLeft, ArrowRight, Save, Send, FileText, Building, DollarSign, Clock, Check } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL + '/api';

const CreateProposalPage = () => {
  const { formId } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  const { t, i18n } = useTranslation();
  const isRTL = i18n.language?.startsWith('ar');
  
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [applicationForm, setApplicationForm] = useState(null);
  
  // Proposal form data
  const [formData, setFormData] = useState({
    organization_name: '',
    organization_address: '',
    organization_phone: '',
    contact_person: '',
    contact_position: '',
    contact_email: '',
    standards: [],
    scope: '',
    total_employees: 0,
    number_of_sites: 1,
    audit_duration: {
      stage_1: 0,
      stage_2: 0,
      surveillance_1: 0,
      surveillance_2: 0,
      recertification: 0
    },
    service_fees: {
      initial_certification: 0,
      surveillance_1: 0,
      surveillance_2: 0,
      recertification: 0,
      currency: 'SAR'
    },
    notes: '',
    validity_days: 30,
    // First Party (Bayan) authorized signatory
    issuer_name: 'Abdullah Al-Rashid',
    issuer_designation: 'General Manager',
    issuer_signature: '',
    issuer_stamp: ''
  });

  useEffect(() => {
    if (formId) {
      loadApplicationForm();
      loadDefaultSignatory();
    }
  }, [formId]);

  const loadDefaultSignatory = async () => {
    try {
      const response = await axios.get(`${API}/defaults/signatory`);
      const defaults = response.data;
      setFormData(prev => ({
        ...prev,
        issuer_name: defaults.issuer_name || prev.issuer_name,
        issuer_designation: defaults.issuer_designation || prev.issuer_designation,
        issuer_signature: defaults.issuer_signature || prev.issuer_signature,
        issuer_stamp: defaults.issuer_stamp || prev.issuer_stamp
      }));
    } catch (error) {
      console.error('Error loading default signatory:', error);
    }
  };

  const loadApplicationForm = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/application-forms/${formId}`);
      const form = response.data;
      setApplicationForm(form);
      
      // Pre-fill data from application form
      const auditCalc = form.audit_calculation || {};
      const phases = auditCalc.phases || {};
      
      setFormData(prev => ({
        ...prev,
        organization_name: form.company_data?.companyName || form.client_info?.company_name || '',
        organization_address: form.company_data?.address || '',
        organization_phone: form.company_data?.mobileNumber || form.company_data?.phoneNumber || form.client_info?.mobile || form.client_info?.phone || '',
        contact_person: form.company_data?.contactPerson || form.client_info?.name || '',
        contact_position: form.company_data?.designation || '',
        contact_email: form.company_data?.contactEmail || form.client_info?.email || '',
        standards: form.company_data?.certificationSchemes || [],
        scope: form.company_data?.keyBusinessProcesses || '',
        total_employees: parseInt(form.company_data?.totalEmployees) || 0,
        number_of_sites: parseInt(form.company_data?.numberOfSites) || 1,
        audit_duration: {
          stage_1: phases.stage_1 || 0,
          stage_2: phases.stage_2 || 0,
          surveillance_1: phases.surveillance || 0,
          surveillance_2: phases.surveillance || 0,
          recertification: phases.recertification || 0
        }
      }));
    } catch (error) {
      console.error('Error loading application form:', error);
      alert(t('errorLoadingForm'));
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleAuditDurationChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      audit_duration: { ...prev.audit_duration, [field]: parseFloat(value) || 0 }
    }));
  };

  const handleServiceFeesChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      service_fees: { ...prev.service_fees, [field]: parseFloat(value) || 0 }
    }));
  };

  const calculateTotal = () => {
    const fees = formData.service_fees;
    return fees.initial_certification + fees.surveillance_1 + fees.surveillance_2 + fees.recertification;
  };

  const handleSaveAndSend = async () => {
    // Validation
    if (!formData.organization_name || !formData.contact_email) {
      alert(t('pleaseEnterRequiredFields'));
      return;
    }

    setSaving(true);
    try {
      // Create proposal
      const response = await axios.post(`${API}/proposals`, {
        application_form_id: formId,
        ...formData
      });

      // Send to client
      await axios.post(`${API}/proposals/${response.data.id}/send`);
      
      alert(t('proposalCreatedAndSent'));
      navigate('/dashboard');
    } catch (error) {
      console.error('Error creating proposal:', error);
      let errorMessage = '';
      if (error.response?.data?.detail) {
        const detail = error.response.data.detail;
        if (typeof detail === 'string') {
          errorMessage = detail;
        } else if (Array.isArray(detail)) {
          // Handle Pydantic validation errors
          errorMessage = detail.map(err => `${err.loc?.join(' -> ') || 'Field'}: ${err.msg}`).join('\n');
        } else {
          errorMessage = JSON.stringify(detail);
        }
      } else if (error.response?.status) {
        errorMessage = `Server error: ${error.response.status} ${error.response.statusText || ''}`;
      } else if (error.message) {
        errorMessage = error.message;
      } else if (error.code) {
        errorMessage = `Network error: ${error.code}`;
      } else {
        errorMessage = String(error) || 'Unknown error occurred';
      }
      alert(t('errorCreatingProposal') + '\n' + errorMessage);
    } finally {
      setSaving(false);
    }
  };

  const handleSaveOnly = async () => {
    if (!formData.organization_name || !formData.contact_email) {
      alert(t('pleaseEnterRequiredFields'));
      return;
    }

    setSaving(true);
    try {
      await axios.post(`${API}/proposals`, {
        application_form_id: formId,
        ...formData
      });
      
      alert(t('proposalCreated'));
      navigate('/dashboard');
    } catch (error) {
      console.error('Error creating proposal:', error);
      let errorMessage = '';
      if (error.response?.data?.detail) {
        const detail = error.response.data.detail;
        if (typeof detail === 'string') {
          errorMessage = detail;
        } else if (Array.isArray(detail)) {
          // Handle Pydantic validation errors
          errorMessage = detail.map(err => `${err.loc?.join(' -> ') || 'Field'}: ${err.msg}`).join('\n');
        } else {
          errorMessage = JSON.stringify(detail);
        }
      } else if (error.response?.status) {
        errorMessage = `Server error: ${error.response.status} ${error.response.statusText || ''}`;
      } else if (error.message) {
        errorMessage = error.message;
      } else if (error.code) {
        errorMessage = `Network error: ${error.code}`;
      } else {
        errorMessage = String(error) || 'Unknown error occurred';
      }
      alert(t('errorCreatingProposal') + '\n' + errorMessage);
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-bayan-navy border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">{t('loadingForm')}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-4 lg:p-6" dir={isRTL ? 'rtl' : 'ltr'}>
      <div className="max-w-4xl mx-auto space-y-6">
          {/* Page Title */}
          <div className={`flex items-center gap-3 ${isRTL ? 'flex-row-reverse' : ''}`}>
            <FileText className="w-8 h-8 text-bayan-navy" />
            <div>
              <h1 className="text-2xl font-bold text-bayan-navy">{t('createProposal')}</h1>
              <p className="text-gray-500">{t('proposalFor')}: {formData.organization_name}</p>
            </div>
          </div>

          {/* Facility Details */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Building className="w-5 h-5" />
                {t('organizationDetails')}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>{t('organizationName')} *</Label>
                  <Input
                    value={formData.organization_name}
                    onChange={(e) => handleInputChange('organization_name', e.target.value)}
                  />
                </div>
                <div className="space-y-2">
                  <Label>{t('address')}</Label>
                  <Input
                    value={formData.organization_address}
                    onChange={(e) => handleInputChange('organization_address', e.target.value)}
                  />
                </div>
                <div className="space-y-2">
                  <Label>{t('phone')}</Label>
                  <Input
                    value={formData.organization_phone}
                    onChange={(e) => handleInputChange('organization_phone', e.target.value)}
                  />
                </div>
                <div className="space-y-2">
                  <Label>{t('contactPerson')}</Label>
                  <Input
                    value={formData.contact_person}
                    onChange={(e) => handleInputChange('contact_person', e.target.value)}
                  />
                </div>
                <div className="space-y-2">
                  <Label>{t('position')}</Label>
                  <Input
                    value={formData.contact_position}
                    onChange={(e) => handleInputChange('contact_position', e.target.value)}
                  />
                </div>
                <div className="space-y-2">
                  <Label>{t('email')} *</Label>
                  <Input
                    type="email"
                    value={formData.contact_email}
                    onChange={(e) => handleInputChange('contact_email', e.target.value)}
                  />
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Service Details */}
          <Card>
            <CardHeader>
              <CardTitle>{t('serviceDetails')}</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label>{t('certificationStandards')}</Label>
                  <div className="flex flex-wrap gap-2">
                    {formData.standards.map((std, idx) => (
                      <span key={idx} className="px-3 py-1 bg-bayan-navy text-white rounded-full text-sm">
                        {std}
                      </span>
                    ))}
                  </div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>{t('totalEmployees')}</Label>
                    <Input
                      type="number"
                      value={formData.total_employees}
                      onChange={(e) => handleInputChange('total_employees', parseInt(e.target.value) || 0)}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>{t('numberOfSites')}</Label>
                    <Input
                      type="number"
                      value={formData.number_of_sites}
                      onChange={(e) => handleInputChange('number_of_sites', parseInt(e.target.value) || 1)}
                    />
                  </div>
                </div>
                <div className="space-y-2">
                  <Label>{t('tentativeScope')}</Label>
                  <Textarea
                    value={formData.scope}
                    onChange={(e) => handleInputChange('scope', e.target.value)}
                    rows={3}
                  />
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Audit Duration */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Clock className="w-5 h-5" />
                {t('auditDuration')} ({t('manDays')})
              </CardTitle>
              <CardDescription>{t('auditDurationFromCalculation')}</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                <div className="space-y-2">
                  <Label>Stage 1</Label>
                  <Input
                    type="number"
                    step="0.5"
                    value={formData.audit_duration.stage_1}
                    onChange={(e) => handleAuditDurationChange('stage_1', e.target.value)}
                  />
                </div>
                <div className="space-y-2">
                  <Label>Stage 2</Label>
                  <Input
                    type="number"
                    step="0.5"
                    value={formData.audit_duration.stage_2}
                    onChange={(e) => handleAuditDurationChange('stage_2', e.target.value)}
                  />
                </div>
                <div className="space-y-2">
                  <Label>Surveillance 1</Label>
                  <Input
                    type="number"
                    step="0.5"
                    value={formData.audit_duration.surveillance_1}
                    onChange={(e) => handleAuditDurationChange('surveillance_1', e.target.value)}
                  />
                </div>
                <div className="space-y-2">
                  <Label>Surveillance 2</Label>
                  <Input
                    type="number"
                    step="0.5"
                    value={formData.audit_duration.surveillance_2}
                    onChange={(e) => handleAuditDurationChange('surveillance_2', e.target.value)}
                  />
                </div>
                <div className="space-y-2">
                  <Label>{t('recertification')}</Label>
                  <Input
                    type="number"
                    step="0.5"
                    value={formData.audit_duration.recertification}
                    onChange={(e) => handleAuditDurationChange('recertification', e.target.value)}
                  />
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Service Fees */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <DollarSign className="w-5 h-5" />
                {t('serviceFees')} (SAR)
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>{t('initialCertification')}</Label>
                  <Input
                    type="number"
                    value={formData.service_fees.initial_certification}
                    onChange={(e) => handleServiceFeesChange('initial_certification', e.target.value)}
                  />
                </div>
                <div className="space-y-2">
                  <Label>Surveillance 1</Label>
                  <Input
                    type="number"
                    value={formData.service_fees.surveillance_1}
                    onChange={(e) => handleServiceFeesChange('surveillance_1', e.target.value)}
                  />
                </div>
                <div className="space-y-2">
                  <Label>Surveillance 2</Label>
                  <Input
                    type="number"
                    value={formData.service_fees.surveillance_2}
                    onChange={(e) => handleServiceFeesChange('surveillance_2', e.target.value)}
                  />
                </div>
                <div className="space-y-2">
                  <Label>{t('recertification')}</Label>
                  <Input
                    type="number"
                    value={formData.service_fees.recertification}
                    onChange={(e) => handleServiceFeesChange('recertification', e.target.value)}
                  />
                </div>
              </div>
              
              {/* Total */}
              <div className="mt-6 p-4 bg-green-50 rounded-lg flex justify-between items-center">
                <span className="text-lg font-bold">{t('totalAmount')}</span>
                <span className="text-2xl font-bold text-green-700">
                  {new Intl.NumberFormat('en-US').format(calculateTotal())} SAR
                </span>
              </div>
            </CardContent>
          </Card>

          {/* Additional Notes */}
          <Card>
            <CardHeader>
              <CardTitle>{t('additionalNotes')}</CardTitle>
            </CardHeader>
            <CardContent>
              <Textarea
                value={formData.notes}
                onChange={(e) => handleInputChange('notes', e.target.value)}
                rows={4}
                placeholder={t('enterAdditionalNotes')}
              />
              <div className="mt-4 space-y-2">
                <Label>{t('proposalValidity')} ({t('days')})</Label>
                <Input
                  type="number"
                  value={formData.validity_days}
                  onChange={(e) => handleInputChange('validity_days', parseInt(e.target.value) || 30)}
                  className="w-32"
                />
              </div>
            </CardContent>
          </Card>

          {/* Authorized Signatory (First Party - Bayan) */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="w-5 h-5" />
                {t('authorizedSignatory')}
              </CardTitle>
              <CardDescription>{t('firstPartySignatoryDetails')}</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>{t('signatoryName')}</Label>
                  <Input
                    value={formData.issuer_name}
                    onChange={(e) => handleInputChange('issuer_name', e.target.value)}
                    placeholder="Abdullah Al-Rashid"
                  />
                </div>
                <div className="space-y-2">
                  <Label>{t('jobTitle')}</Label>
                  <Input
                    value={formData.issuer_designation}
                    onChange={(e) => handleInputChange('issuer_designation', e.target.value)}
                    placeholder="General Manager"
                  />
                </div>
              </div>
              
              {/* Signature and Stamp Upload */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                <div className="space-y-2">
                  <Label>{t('signature')}</Label>
                  <div className="border-2 border-dashed border-slate-300 rounded-lg p-4 text-center">
                    {formData.issuer_signature ? (
                      <div className="relative">
                        <img 
                          src={formData.issuer_signature} 
                          alt="Signature" 
                          className="max-h-20 mx-auto"
                        />
                        <Button
                          type="button"
                          variant="ghost"
                          size="sm"
                          className="absolute top-0 right-0"
                          onClick={() => handleInputChange('issuer_signature', '')}
                        >
                          ✕
                        </Button>
                      </div>
                    ) : (
                      <label className="cursor-pointer">
                        <input
                          type="file"
                          accept="image/*"
                          className="hidden"
                          onChange={(e) => {
                            const file = e.target.files[0];
                            if (file) {
                              const reader = new FileReader();
                              reader.onloadend = () => {
                                handleInputChange('issuer_signature', reader.result);
                              };
                              reader.readAsDataURL(file);
                            }
                          }}
                        />
                        <div className="text-slate-500 text-sm">
                          {t('uploadSignature')}
                        </div>
                      </label>
                    )}
                  </div>
                </div>
                <div className="space-y-2">
                  <Label>{t('stamp')}</Label>
                  <div className="border-2 border-dashed border-slate-300 rounded-lg p-4 text-center">
                    {formData.issuer_stamp ? (
                      <div className="relative">
                        <img 
                          src={formData.issuer_stamp} 
                          alt="Stamp" 
                          className="max-h-20 mx-auto"
                        />
                        <Button
                          type="button"
                          variant="ghost"
                          size="sm"
                          className="absolute top-0 right-0"
                          onClick={() => handleInputChange('issuer_stamp', '')}
                        >
                          ✕
                        </Button>
                      </div>
                    ) : (
                      <label className="cursor-pointer">
                        <input
                          type="file"
                          accept="image/*"
                          className="hidden"
                          onChange={(e) => {
                            const file = e.target.files[0];
                            if (file) {
                              const reader = new FileReader();
                              reader.onloadend = () => {
                                handleInputChange('issuer_stamp', reader.result);
                              };
                              reader.readAsDataURL(file);
                            }
                          }}
                        />
                        <div className="text-slate-500 text-sm">
                          {t('uploadStamp')}
                        </div>
                      </label>
                    )}
                  </div>
                </div>
              </div>
              
              <p className="text-sm text-slate-500 mt-3">
                {t('signatoryDetailsNote')}
              </p>
            </CardContent>
          </Card>

          {/* Action Buttons */}
          <div className="flex gap-4 justify-end">
            <Button
              variant="outline"
              onClick={() => navigate('/dashboard')}
            >
              {t('cancel')}
            </Button>
            <Button
              variant="outline"
              onClick={handleSaveOnly}
              disabled={saving}
            >
              <Save className="w-4 h-4 mr-2" />
              {t('saveOnly')}
            </Button>
            <Button
              onClick={handleSaveAndSend}
              disabled={saving}
              className="bg-green-600 hover:bg-green-700"
            >
              <Send className="w-4 h-4 mr-2" />
              {t('saveAndSend')}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CreateProposalPage;
