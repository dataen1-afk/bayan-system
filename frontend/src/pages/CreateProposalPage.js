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
import LanguageSwitcher from '@/components/LanguageSwitcher';
import Sidebar from '@/components/Sidebar';

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
    issuer_designation: 'General Manager'
  });

  useEffect(() => {
    if (formId) {
      loadApplicationForm();
    }
  }, [formId]);

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
        organization_phone: form.company_data?.phoneNumber || form.client_info?.phone || '',
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
      alert(t('errorCreatingProposal') + ' ' + (error.response?.data?.detail || error.message));
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
      alert(t('errorCreatingProposal') + ' ' + (error.response?.data?.detail || error.message));
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-bayan-navy border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">{t('loadingForm')}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50" dir={isRTL ? 'rtl' : 'ltr'}>
      {/* Header */}
      <header className="bg-white shadow-sm border-b fixed top-0 left-0 right-0 z-50">
        <div className="dashboard-header max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="dashboard-header-left flex items-center gap-4">
            <img src="/Bayan-removebg-preview.png" alt="Bayan" className="h-16 w-auto object-contain" />
          </div>
          <div className="dashboard-header-right flex items-center gap-4">
            <LanguageSwitcher />
            <Button variant="outline" onClick={() => navigate('/dashboard')}>
              {isRTL ? <ArrowRight className="w-4 h-4 ml-2" /> : <ArrowLeft className="w-4 h-4 mr-2" />}
              {t('backToDashboard')}
            </Button>
          </div>
        </div>
        <div className="h-1.5 bg-gradient-to-r from-bayan-navy via-bayan-navy-light to-bayan-navy"></div>
      </header>

      <main className="pt-28 pb-12 px-4">
        <div className="max-w-4xl mx-auto space-y-6">
          {/* Page Title */}
          <div className={`flex items-center gap-3 ${isRTL ? 'flex-row-reverse' : ''}`}>
            <FileText className="w-8 h-8 text-bayan-navy" />
            <div>
              <h1 className="text-2xl font-bold text-bayan-navy">{t('createProposal')}</h1>
              <p className="text-gray-500">{t('proposalFor')}: {formData.organization_name}</p>
            </div>
          </div>

          {/* Organization Details */}
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
      </main>
    </div>
  );
};

export default CreateProposalPage;
