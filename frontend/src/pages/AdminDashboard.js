import React, { useState, useEffect, useContext } from 'react';
import axios from 'axios';
import { useTranslation } from 'react-i18next';
import { API, AuthContext } from '@/App';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { LogOut, FileText, DollarSign, FileCheck, FolderOpen, BarChart3, Settings, Plus, Eye, X, Send } from 'lucide-react';
import LanguageSwitcher from '@/components/LanguageSwitcher';
import Sidebar from '@/components/Sidebar';
import ApplicationForm from '@/components/ApplicationForm';

const AdminDashboard = () => {
  const { t, i18n } = useTranslation();
  const [isRTL, setIsRTL] = useState(() => {
    return i18n.language?.startsWith('ar') || document.documentElement.dir === 'rtl';
  });
  const { user, logout } = useContext(AuthContext);
  const [activeTab, setActiveTab] = useState('forms');
  const [forms, setForms] = useState([]);
  const [applicationForms, setApplicationForms] = useState([]);
  const [quotations, setQuotations] = useState([]);
  const [contracts, setContracts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [clients, setClients] = useState([]);

  // Application Form Modal state
  const [showApplicationForm, setShowApplicationForm] = useState(false);
  const [selectedApplicationForm, setSelectedApplicationForm] = useState(null);
  const [assignFormModal, setAssignFormModal] = useState(false);
  const [selectedClientForForm, setSelectedClientForForm] = useState('');

  // Form creation state (legacy simple forms)
  const [newForm, setNewForm] = useState({
    client_id: '',
    fields: [{ label: '', type: 'text', required: true }]
  });

  // Quotation creation state
  const [newQuotation, setNewQuotation] = useState({
    form_id: '',
    client_id: '',
    client_email: '',
    price: '',
    details: ''
  });

  // Track RTL state changes
  useEffect(() => {
    const checkRTL = () => {
      const isArabic = i18n.language?.startsWith('ar') || document.documentElement.dir === 'rtl';
      setIsRTL(isArabic);
    };
    i18n.on('languageChanged', checkRTL);
    return () => i18n.off('languageChanged', checkRTL);
  }, [i18n]);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [formsRes, quotationsRes, contractsRes] = await Promise.all([
        axios.get(`${API}/forms`),
        axios.get(`${API}/quotations`),
        axios.get(`${API}/contracts`)
      ]);
      setForms(formsRes.data);
      setQuotations(quotationsRes.data);
      setContracts(contractsRes.data);
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const addFormField = () => {
    setNewForm({
      ...newForm,
      fields: [...newForm.fields, { label: '', type: 'text', required: true }]
    });
  };

  const updateFormField = (index, key, value) => {
    const updatedFields = [...newForm.fields];
    updatedFields[index][key] = value;
    setNewForm({ ...newForm, fields: updatedFields });
  };

  const removeFormField = (index) => {
    const updatedFields = newForm.fields.filter((_, i) => i !== index);
    setNewForm({ ...newForm, fields: updatedFields });
  };

  const handleCreateForm = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/forms`, newForm);
      alert(t('formCreatedSuccess'));
      setNewForm({ client_id: '', fields: [{ label: '', type: 'text', required: true }] });
      loadData();
    } catch (error) {
      alert(t('errorCreatingForm') + ' ' + (error.response?.data?.detail || error.message));
    }
  };

  const handleCreateQuotation = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/quotations`, {
        ...newQuotation,
        price: parseFloat(newQuotation.price)
      });
      alert(t('quotationCreatedSuccess'));
      setNewQuotation({ form_id: '', client_id: '', client_email: '', price: '', details: '' });
      loadData();
    } catch (error) {
      alert(t('errorCreatingQuotation') + ' ' + (error.response?.data?.detail || error.message));
    }
  };

  const downloadContract = async (contractId) => {
    try {
      const response = await axios.get(`${API}/contracts/${contractId}/download`, {
        responseType: 'blob'
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `contract_${contractId}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      alert(t('errorDownloadingContract') + ' ' + error.message);
    }
  };

  // Empty state component
  const EmptyState = ({ icon: Icon, title, description, helpText }) => (
    <div className="text-center py-12">
      <div className="mb-4">
        <Icon className="w-16 h-16 mx-auto text-gray-300" />
      </div>
      <h3 className="text-lg font-semibold text-gray-700 mb-2">{title}</h3>
      <p className="text-sm text-gray-500 mb-6">{description}</p>
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 max-w-md mx-auto">
        <p className="text-xs text-blue-800 leading-relaxed">
          💡 {helpText}
        </p>
      </div>
    </div>
  );

  // Coming Soon component for new features
  const ComingSoon = ({ icon: Icon, title }) => (
    <div className="text-center py-16">
      <div className="mb-4">
        <Icon className="w-20 h-20 mx-auto text-gray-300" />
      </div>
      <h3 className="text-xl font-semibold text-gray-700 mb-2">{title}</h3>
      <p className="text-sm text-gray-500 mb-4">{t('comingSoon')}</p>
      <div className="inline-block px-4 py-2 bg-gradient-to-r from-blue-500 to-purple-500 text-white text-sm font-medium rounded-full">
        {t('stayTuned')}
      </div>
    </div>
  );

  // Render content based on active tab
  const renderContent = () => {
    switch (activeTab) {
      case 'forms':
        return (
          <div className="space-y-6">
            <Card>
              <CardHeader className={isRTL ? 'text-right' : 'text-left'}>
                <CardTitle>{t('createNewForm')}</CardTitle>
                <CardDescription>{t('createCustomForm')}</CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleCreateForm} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="client_id" className={isRTL ? 'block text-right' : ''}>{t('clientId')}</Label>
                    <Input
                      id="client_id"
                      value={newForm.client_id}
                      onChange={(e) => setNewForm({ ...newForm, client_id: e.target.value })}
                      placeholder={t('enterClientId')}
                      required
                      data-testid="form-client-id-input"
                      className={isRTL ? 'text-right' : ''}
                      dir={isRTL ? 'rtl' : 'ltr'}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label className={isRTL ? 'block text-right' : ''}>{t('formFields')}</Label>
                    {newForm.fields.map((field, index) => (
                      <div key={index} className={`flex gap-2 items-end ${isRTL ? 'flex-row-reverse' : ''}`}>
                        <div className="flex-1">
                          <Input
                            placeholder={t('fieldLabel')}
                            value={field.label}
                            onChange={(e) => updateFormField(index, 'label', e.target.value)}
                            required
                            data-testid={`field-label-${index}`}
                            className={isRTL ? 'text-right' : ''}
                            dir={isRTL ? 'rtl' : 'ltr'}
                          />
                        </div>
                        <div className="w-40">
                          <Select
                            value={field.type}
                            onValueChange={(value) => updateFormField(index, 'type', value)}
                          >
                            <SelectTrigger data-testid={`field-type-${index}`}>
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="text">{t('text')}</SelectItem>
                              <SelectItem value="textarea">{t('textarea')}</SelectItem>
                              <SelectItem value="email">{t('email')}</SelectItem>
                              <SelectItem value="number">{t('number')}</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                        {newForm.fields.length > 1 && (
                          <Button
                            type="button"
                            variant="destructive"
                            onClick={() => removeFormField(index)}
                            data-testid={`remove-field-${index}`}
                          >
                            {t('remove')}
                          </Button>
                        )}
                      </div>
                    ))}
                    <Button type="button" variant="outline" onClick={addFormField} data-testid="add-field-button">
                      {t('addField')}
                    </Button>
                  </div>

                  <Button type="submit" data-testid="create-form-button">{t('createForm')}</Button>
                </form>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className={isRTL ? 'text-right' : 'text-left'}>
                <CardTitle>{t('allForms')}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2" data-testid="forms-list">
                  {forms.length === 0 ? (
                    <EmptyState
                      icon={FileText}
                      title={t('noFormsYet')}
                      description={t('createFirstForm')}
                      helpText={t('formsEmptyStateHelp')}
                    />
                  ) : (
                    forms.map((form) => (
                      <div key={form.id} className="p-4 border rounded-lg hover:bg-gray-50 transition-colors" data-testid={`form-${form.id}`}>
                        <div className={`flex justify-between ${isRTL ? 'flex-row-reverse' : ''}`}>
                          <div className={isRTL ? 'text-right' : 'text-left'}>
                            <p className="font-semibold">{t('formId')}: {form.id}</p>
                            <p className="text-sm text-gray-600">{t('client')}: {form.client_id}</p>
                            <p className="text-sm text-gray-600">{t('status')}: {t(form.status)}</p>
                            <p className="text-sm text-gray-600">{t('fields')}: {form.fields.length}</p>
                          </div>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        );

      case 'quotations':
        return (
          <div className="space-y-6">
            <Card>
              <CardHeader className={isRTL ? 'text-right' : 'text-left'}>
                <CardTitle>{t('createQuotation')}</CardTitle>
                <CardDescription>{t('createQuotationFor')}</CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleCreateQuotation} className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="form_id" className={isRTL ? 'block text-right' : ''}>{t('formId')}</Label>
                      <Input
                        id="form_id"
                        value={newQuotation.form_id}
                        onChange={(e) => setNewQuotation({ ...newQuotation, form_id: e.target.value })}
                        placeholder={t('enterFormId')}
                        required
                        data-testid="quotation-form-id-input"
                        className={isRTL ? 'text-right' : ''}
                        dir={isRTL ? 'rtl' : 'ltr'}
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="q_client_id" className={isRTL ? 'block text-right' : ''}>{t('clientId')}</Label>
                      <Input
                        id="q_client_id"
                        value={newQuotation.client_id}
                        onChange={(e) => setNewQuotation({ ...newQuotation, client_id: e.target.value })}
                        placeholder={t('enterClientId')}
                        required
                        data-testid="quotation-client-id-input"
                        className={isRTL ? 'text-right' : ''}
                        dir={isRTL ? 'rtl' : 'ltr'}
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="client_email" className={isRTL ? 'block text-right' : ''}>{t('clientEmail')}</Label>
                      <Input
                        id="client_email"
                        type="email"
                        value={newQuotation.client_email}
                        onChange={(e) => setNewQuotation({ ...newQuotation, client_email: e.target.value })}
                        placeholder="client@example.com"
                        required
                        data-testid="quotation-client-email-input"
                        dir="ltr"
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="price" className={isRTL ? 'block text-right' : ''}>{t('price')}</Label>
                      <Input
                        id="price"
                        type="number"
                        step="0.01"
                        value={newQuotation.price}
                        onChange={(e) => setNewQuotation({ ...newQuotation, price: e.target.value })}
                        placeholder="1000.00"
                        required
                        data-testid="quotation-price-input"
                        dir="ltr"
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="details" className={isRTL ? 'block text-right' : ''}>{t('details')}</Label>
                    <Textarea
                      id="details"
                      value={newQuotation.details}
                      onChange={(e) => setNewQuotation({ ...newQuotation, details: e.target.value })}
                      placeholder={t('serviceDetails')}
                      rows={4}
                      required
                      data-testid="quotation-details-input"
                      className={isRTL ? 'text-right' : ''}
                      dir={isRTL ? 'rtl' : 'ltr'}
                    />
                  </div>

                  <Button type="submit" data-testid="create-quotation-button">{t('createQuotation')}</Button>
                </form>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className={isRTL ? 'text-right' : 'text-left'}>
                <CardTitle>{t('allQuotations')}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2" data-testid="quotations-list">
                  {quotations.length === 0 ? (
                    <EmptyState
                      icon={DollarSign}
                      title={t('noQuotationsYet')}
                      description={t('createFirstQuotation')}
                      helpText={t('quotationsEmptyStateHelp')}
                    />
                  ) : (
                    quotations.map((quotation) => (
                      <div key={quotation.id} className="p-4 border rounded-lg hover:bg-gray-50 transition-colors" data-testid={`quotation-${quotation.id}`}>
                        <div className={`flex justify-between ${isRTL ? 'flex-row-reverse' : ''}`}>
                          <div className={isRTL ? 'text-right' : 'text-left'}>
                            <p className="font-semibold">{t('quotationId')}: {quotation.id}</p>
                            <p className="text-sm text-gray-600">{t('form')}: {quotation.form_id}</p>
                            <p className="text-sm text-gray-600">{t('client')}: {quotation.client_id}</p>
                            <p className="text-lg font-bold text-green-600">${quotation.price}</p>
                            <p className="text-sm mt-2">{quotation.details}</p>
                            <span className={`inline-block mt-2 px-2 py-1 text-xs rounded ${
                              quotation.status === 'approved' ? 'bg-green-100 text-green-800' :
                              quotation.status === 'rejected' ? 'bg-red-100 text-red-800' :
                              quotation.status === 'modifications_requested' ? 'bg-blue-100 text-blue-800' :
                              'bg-yellow-100 text-yellow-800'
                            }`}>
                              {t(quotation.status)}
                            </span>
                          </div>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        );

      case 'contracts':
        return (
          <Card>
            <CardHeader className={isRTL ? 'text-right' : 'text-left'}>
              <CardTitle>{t('allContracts')}</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2" data-testid="contracts-list">
                {contracts.length === 0 ? (
                  <EmptyState
                    icon={FileCheck}
                    title={t('noContractsYet')}
                    description={t('contractsAutoGenerated')}
                    helpText={t('contractsEmptyStateHelp')}
                  />
                ) : (
                  contracts.map((contract) => (
                    <div key={contract.id} className={`p-4 border rounded-lg flex justify-between items-center hover:bg-gray-50 transition-colors ${isRTL ? 'flex-row-reverse' : ''}`} data-testid={`contract-${contract.id}`}>
                      <div className={isRTL ? 'text-right' : 'text-left'}>
                        <p className="font-semibold">{t('contractId')}: {contract.id}</p>
                        <p className="text-sm text-gray-600">{t('quotation')}: {contract.quotation_id}</p>
                        <p className="text-sm text-gray-600">{t('client')}: {contract.client_id}</p>
                      </div>
                      <Button onClick={() => downloadContract(contract.id)} data-testid={`download-contract-${contract.id}`}>
                        {t('downloadPdf')}
                      </Button>
                    </div>
                  ))
                )}
              </div>
            </CardContent>
          </Card>
        );

      case 'templates':
        return (
          <Card>
            <CardContent className="py-8">
              <ComingSoon icon={FolderOpen} title={t('templates')} />
            </CardContent>
          </Card>
        );

      case 'reports':
        return (
          <Card>
            <CardContent className="py-8">
              <ComingSoon icon={BarChart3} title={t('reports')} />
            </CardContent>
          </Card>
        );

      case 'settings':
        return (
          <Card>
            <CardContent className="py-8">
              <ComingSoon icon={Settings} title={t('settings')} />
            </CardContent>
          </Card>
        );

      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-gray-50 to-blue-50" data-testid="admin-dashboard">
      {/* Fixed Header */}
      <header className="fixed top-0 left-0 right-0 z-40 bg-white shadow-md">
        {/* Main Header Content */}
        <div className="dashboard-header max-w-full mx-auto px-4 py-3 sm:px-6 lg:px-8 flex justify-between items-center">
          <div className="dashboard-header-left flex items-center gap-4">
            <div className="-my-2">
              <img src="/bayan-logo.png" alt="Bayan" className="h-20 w-auto object-contain" />
            </div>
          </div>
          <div className="dashboard-header-right flex gap-2 items-center">
            <LanguageSwitcher />
            <Button variant="outline" onClick={logout} data-testid="logout-button" className="bg-bayan-navy text-white hover:bg-bayan-navy-light border-bayan-navy font-semibold">
              <LogOut className="btn-icon w-4 h-4" />
              {t('logout')}
            </Button>
          </div>
        </div>
        {/* Navy Accent Bar */}
        <div className="h-1.5 bg-gradient-to-r from-bayan-navy via-bayan-navy-light to-bayan-navy"></div>
      </header>

      {/* Layout with Sidebar */}
      <div className="flex pt-[102px]">
        <Sidebar 
          activeTab={activeTab} 
          onTabChange={setActiveTab}
          userRole="admin"
          userName={user?.name}
          dashboardTitle={t('adminDashboard')}
        />
        
        {/* Main Content */}
        <main className="flex-1 p-6 lg:p-8 min-h-screen">
          <div className="max-w-6xl mx-auto">
            {/* Page Title */}
            <div className={`mb-6 ${isRTL ? 'text-right' : 'text-left'}`}>
              <h2 className="text-2xl font-bold text-gray-800">
                {activeTab === 'forms' && t('forms')}
                {activeTab === 'quotations' && t('quotations')}
                {activeTab === 'contracts' && t('contracts')}
                {activeTab === 'templates' && t('templates')}
                {activeTab === 'reports' && t('reports')}
                {activeTab === 'settings' && t('settings')}
              </h2>
            </div>
            
            {/* Content */}
            {renderContent()}
          </div>
        </main>
      </div>
    </div>
  );
};

export default AdminDashboard;
