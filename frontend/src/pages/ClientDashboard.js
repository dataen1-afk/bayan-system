import React, { useState, useEffect, useContext } from 'react';
import axios from 'axios';
import { useTranslation } from 'react-i18next';
import { API, AuthContext } from '@/App';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { LogOut, FileText, DollarSign, FileCheck, CheckCircle, XCircle, Edit } from 'lucide-react';
import LanguageSwitcher from '@/components/LanguageSwitcher';

const ClientDashboard = () => {
  const { t, i18n } = useTranslation();
  const isRTL = i18n.language === 'ar';
  const { user, logout } = useContext(AuthContext);
  const [forms, setForms] = useState([]);
  const [quotations, setQuotations] = useState([]);
  const [contracts, setContracts] = useState([]);
  const [selectedForm, setSelectedForm] = useState(null);
  const [formResponses, setFormResponses] = useState({});
  const [loading, setLoading] = useState(false);

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

  const handleSubmitForm = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/forms/${selectedForm.id}/submit`, {
        responses: formResponses
      });
      alert(t('formSubmittedSuccess'));
      setSelectedForm(null);
      setFormResponses({});
      loadData();
    } catch (error) {
      alert(t('errorSubmittingForm') + ' ' + (error.response?.data?.detail || error.message));
    }
  };

  const handleRespondToQuotation = async (quotationId, status) => {
    try {
      await axios.post(`${API}/quotations/${quotationId}/respond`, { status });
      const messageKey = status === 'approved' ? 'quotationApproved' : 
                         status === 'rejected' ? 'quotationRejected' : 
                         'modificationsRequested';
      alert(t(messageKey));
      loadData();
    } catch (error) {
      alert(t('errorRespondingQuotation') + ' ' + (error.response?.data?.detail || error.message));
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

  // Status badge component
  const StatusBadge = ({ status }) => {
    const statusStyles = {
      approved: 'bg-green-100 text-green-800',
      rejected: 'bg-red-100 text-red-800',
      modifications_requested: 'bg-blue-100 text-blue-800',
      pending: 'bg-yellow-100 text-yellow-800',
      submitted: 'bg-green-100 text-green-800'
    };
    
    return (
      <span className={`inline-block px-2 py-1 text-xs rounded font-medium ${statusStyles[status] || 'bg-gray-100 text-gray-800'}`}>
        {t(status)}
      </span>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-gray-50 to-blue-50" data-testid="client-dashboard">
      {/* Header */}
      <header className="bg-gradient-to-r from-bayan-blue to-blue-600 shadow-lg border-b-4 border-blue-700">
        <div className={`max-w-7xl mx-auto px-4 py-5 sm:px-6 lg:px-8 flex justify-between items-center ${isRTL ? 'flex-row-reverse' : ''}`}>
          <div className={`flex items-center gap-4 ${isRTL ? 'flex-row-reverse' : ''}`}>
            <div className="bg-white rounded-lg p-2 shadow-sm">
              <img src="/bayan-logo.png" alt="Bayan" className="h-10 w-auto object-contain" />
            </div>
            <div className={isRTL ? 'text-right' : 'text-left'}>
              <h1 className="text-2xl font-bold text-white" data-testid="client-dashboard-title">{t('clientDashboard')}</h1>
              <p className="text-sm text-blue-100">{t('welcome')}, {user?.name}</p>
            </div>
          </div>
          <div className={`flex gap-2 ${isRTL ? 'flex-row-reverse' : ''}`}>
            <LanguageSwitcher />
            <Button variant="outline" onClick={logout} data-testid="logout-button" className="bg-white text-bayan-blue hover:bg-blue-50 border-2 border-white font-semibold">
              <LogOut className={`w-4 h-4 ${isRTL ? 'ml-2' : 'mr-2'}`} />
              {t('logout')}
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        <Tabs defaultValue="forms" className="space-y-6" dir={isRTL ? 'rtl' : 'ltr'}>
          {/* RTL-aware tabs container */}
          <div className={`flex ${isRTL ? 'justify-end' : 'justify-start'}`}>
            <TabsList className="bg-white shadow-sm border">
              <TabsTrigger value="forms" data-testid="forms-tab" className={`flex items-center gap-2 ${isRTL ? 'flex-row-reverse' : ''}`}>
                <FileText className="w-4 h-4" />
                <span>{t('myForms')}</span>
              </TabsTrigger>
              <TabsTrigger value="quotations" data-testid="quotations-tab" className={`flex items-center gap-2 ${isRTL ? 'flex-row-reverse' : ''}`}>
                <DollarSign className="w-4 h-4" />
                <span>{t('quotations')}</span>
              </TabsTrigger>
              <TabsTrigger value="contracts" data-testid="contracts-tab" className={`flex items-center gap-2 ${isRTL ? 'flex-row-reverse' : ''}`}>
                <FileCheck className="w-4 h-4" />
                <span>{t('contracts')}</span>
              </TabsTrigger>
            </TabsList>
          </div>

          {/* Forms Tab */}
          <TabsContent value="forms" className="space-y-4">
            {selectedForm ? (
              <Card>
                <CardHeader className={isRTL ? 'text-right' : 'text-left'}>
                  <CardTitle>{t('submitForm')}</CardTitle>
                  <CardDescription>{t('fillOutForm')}</CardDescription>
                </CardHeader>
                <CardContent>
                  <form onSubmit={handleSubmitForm} className="space-y-4">
                    {selectedForm.fields.map((field, index) => (
                      <div key={index} className="space-y-2">
                        <Label htmlFor={`field-${index}`} className={isRTL ? 'block text-right' : ''}>
                          {field.label} {field.required && <span className="text-red-500">*</span>}
                        </Label>
                        {field.type === 'textarea' ? (
                          <Textarea
                            id={`field-${index}`}
                            value={formResponses[field.label] || ''}
                            onChange={(e) => setFormResponses({ ...formResponses, [field.label]: e.target.value })}
                            required={field.required}
                            data-testid={`response-${index}`}
                            className={isRTL ? 'text-right' : ''}
                            dir={isRTL ? 'rtl' : 'ltr'}
                          />
                        ) : (
                          <Input
                            id={`field-${index}`}
                            type={field.type}
                            value={formResponses[field.label] || ''}
                            onChange={(e) => setFormResponses({ ...formResponses, [field.label]: e.target.value })}
                            required={field.required}
                            data-testid={`response-${index}`}
                            className={isRTL ? 'text-right' : ''}
                            dir={field.type === 'email' || field.type === 'number' ? 'ltr' : (isRTL ? 'rtl' : 'ltr')}
                          />
                        )}
                      </div>
                    ))}
                    <div className={`flex gap-2 ${isRTL ? 'flex-row-reverse' : ''}`}>
                      <Button type="submit" data-testid="submit-form-button">{t('submitForm')}</Button>
                      <Button type="button" variant="outline" onClick={() => setSelectedForm(null)} data-testid="cancel-form-button">
                        {t('cancel')}
                      </Button>
                    </div>
                  </form>
                </CardContent>
              </Card>
            ) : (
              <Card>
                <CardHeader className={isRTL ? 'text-right' : 'text-left'}>
                  <CardTitle>{t('myForms')}</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2" data-testid="forms-list">
                    {forms.length === 0 ? (
                      <EmptyState
                        icon={FileText}
                        title={t('noFormsYetClient')}
                        description={t('formsWillAppearHere')}
                        helpText={t('clientFormsEmptyStateHelp')}
                      />
                    ) : (
                      forms.map((form) => (
                        <div key={form.id} className={`p-4 border rounded-lg flex justify-between items-center hover:bg-gray-50 transition-colors ${isRTL ? 'flex-row-reverse' : ''}`} data-testid={`form-${form.id}`}>
                          <div className={isRTL ? 'text-right' : 'text-left'}>
                            <p className="font-semibold">{t('formId')}: {form.id}</p>
                            <p className="text-sm text-gray-600">{t('fields')}: {form.fields.length}</p>
                            <div className="mt-1">
                              <StatusBadge status={form.status} />
                            </div>
                          </div>
                          {form.status === 'pending' && (
                            <Button onClick={() => setSelectedForm(form)} data-testid={`fill-form-${form.id}`}>
                              {t('fillForm')}
                            </Button>
                          )}
                        </div>
                      ))
                    )}
                  </div>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* Quotations Tab */}
          <TabsContent value="quotations">
            <Card>
              <CardHeader className={isRTL ? 'text-right' : 'text-left'}>
                <CardTitle>{t('myQuotations')}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4" data-testid="quotations-list">
                  {quotations.length === 0 ? (
                    <EmptyState
                      icon={DollarSign}
                      title={t('noQuotationsYetClient')}
                      description={t('quotationsWillAppearHere')}
                      helpText={t('clientQuotationsEmptyStateHelp')}
                    />
                  ) : (
                    quotations.map((quotation) => (
                      <div key={quotation.id} className="p-4 border rounded-lg hover:bg-gray-50 transition-colors" data-testid={`quotation-${quotation.id}`}>
                        <div className={`flex justify-between items-start ${isRTL ? 'flex-row-reverse' : ''}`}>
                          <div className={`flex-1 ${isRTL ? 'text-right' : 'text-left'}`}>
                            <p className="font-semibold">{t('quotationId')}: {quotation.id}</p>
                            <p className="text-sm text-gray-600">{t('form')}: {quotation.form_id}</p>
                            <p className="text-2xl font-bold text-green-600 mt-2">${quotation.price}</p>
                            <p className="text-sm mt-2 text-gray-700">{quotation.details}</p>
                            <div className="mt-2">
                              <StatusBadge status={quotation.status} />
                            </div>
                          </div>
                          {quotation.status === 'pending' && (
                            <div className={`flex flex-col gap-2 ${isRTL ? 'mr-4' : 'ml-4'}`}>
                              <Button 
                                onClick={() => handleRespondToQuotation(quotation.id, 'approved')}
                                data-testid={`approve-quotation-${quotation.id}`}
                                className="bg-green-600 hover:bg-green-700 text-white font-semibold shadow-md"
                              >
                                <CheckCircle className={`w-4 h-4 ${isRTL ? 'ml-2' : 'mr-2'}`} />
                                {t('approve')}
                              </Button>
                              <Button 
                                variant="outline"
                                onClick={() => handleRespondToQuotation(quotation.id, 'modifications_requested')}
                                data-testid={`modify-quotation-${quotation.id}`}
                                className="border-2 border-bayan-blue text-bayan-blue hover:bg-blue-50 font-semibold shadow-md"
                              >
                                <Edit className={`w-4 h-4 ${isRTL ? 'ml-2' : 'mr-2'}`} />
                                {t('requestModifications')}
                              </Button>
                              <Button 
                                variant="destructive"
                                onClick={() => handleRespondToQuotation(quotation.id, 'rejected')}
                                data-testid={`reject-quotation-${quotation.id}`}
                                className="bg-red-600 hover:bg-red-700 font-semibold shadow-md"
                              >
                                <XCircle className={`w-4 h-4 ${isRTL ? 'ml-2' : 'mr-2'}`} />
                                {t('reject')}
                              </Button>
                            </div>
                          )}
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Contracts Tab */}
          <TabsContent value="contracts">
            <Card>
              <CardHeader className={isRTL ? 'text-right' : 'text-left'}>
                <CardTitle>{t('myContracts')}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2" data-testid="contracts-list">
                  {contracts.length === 0 ? (
                    <EmptyState
                      icon={FileCheck}
                      title={t('noContractsYetClient')}
                      description={t('contractsWillAppearHere')}
                      helpText={t('clientContractsEmptyStateHelp')}
                    />
                  ) : (
                    contracts.map((contract) => (
                      <div key={contract.id} className={`p-4 border rounded-lg flex justify-between items-center hover:bg-gray-50 transition-colors ${isRTL ? 'flex-row-reverse' : ''}`} data-testid={`contract-${contract.id}`}>
                        <div className={isRTL ? 'text-right' : 'text-left'}>
                          <p className="font-semibold">{t('contractId')}: {contract.id}</p>
                          <p className="text-sm text-gray-600">{t('quotation')}: {contract.quotation_id}</p>
                          <p className="text-sm text-gray-500">{t('created')}: {new Date(contract.created_at).toLocaleDateString(isRTL ? 'ar-SA' : 'en-US')}</p>
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
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
};

export default ClientDashboard;
