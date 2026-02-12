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
import { LogOut, FileText, DollarSign, FileCheck } from 'lucide-react';
import LanguageSwitcher from '@/components/LanguageSwitcher';

const ClientDashboard = () => {
  const { t } = useTranslation();
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
      alert('Error downloading contract: ' + error.message);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-gray-50 to-blue-50" data-testid="client-dashboard">
      {/* Header */}
      <header className="bg-gradient-to-r from-bayan-blue to-blue-600 shadow-lg border-b-4 border-blue-700">
        <div className="max-w-7xl mx-auto px-4 py-5 sm:px-6 lg:px-8 flex justify-between items-center">
          <div className="flex items-center gap-4">
            <img src="/bayan-logo.png" alt="Bayan" className="h-12 w-auto object-contain" />
            <div>
              <h1 className="text-2xl font-bold text-white" data-testid="client-dashboard-title">{t('clientDashboard')}</h1>
              <p className="text-sm text-blue-100">{t('welcome')}, {user?.name}</p>
            </div>
          </div>
          <div className="flex gap-2">
            <LanguageSwitcher />
            <Button variant="outline" onClick={logout} data-testid="logout-button" className="bg-white text-bayan-blue hover:bg-blue-50 border-2 border-white font-semibold">
              <LogOut className="w-4 h-4 mr-2" />
              {t('logout')}
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        <Tabs defaultValue="forms" className="space-y-4">
          <TabsList>
            <TabsTrigger value="forms" data-testid="forms-tab">
              <FileText className="w-4 h-4 mr-2" />
              {t('myForms')}
            </TabsTrigger>
            <TabsTrigger value="quotations" data-testid="quotations-tab">
              <DollarSign className="w-4 h-4 mr-2" />
              {t('quotations')}
            </TabsTrigger>
            <TabsTrigger value="contracts" data-testid="contracts-tab">
              <FileCheck className="w-4 h-4 mr-2" />
              {t('contracts')}
            </TabsTrigger>
          </TabsList>

          {/* Forms Tab */}
          <TabsContent value="forms" className="space-y-4">
            {selectedForm ? (
              <Card>
                <CardHeader>
                  <CardTitle>{t('submitForm')}</CardTitle>
                  <CardDescription>{t('fillOutForm')}</CardDescription>
                </CardHeader>
                <CardContent>
                  <form onSubmit={handleSubmitForm} className="space-y-4">
                    {selectedForm.fields.map((field, index) => (
                      <div key={index} className="space-y-2">
                        <Label htmlFor={`field-${index}`}>
                          {field.label} {field.required && <span className="text-red-500">*</span>}
                        </Label>
                        {field.type === 'textarea' ? (
                          <Textarea
                            id={`field-${index}`}
                            value={formResponses[field.label] || ''}
                            onChange={(e) => setFormResponses({ ...formResponses, [field.label]: e.target.value })}
                            required={field.required}
                            data-testid={`response-${index}`}
                          />
                        ) : (
                          <Input
                            id={`field-${index}`}
                            type={field.type}
                            value={formResponses[field.label] || ''}
                            onChange={(e) => setFormResponses({ ...formResponses, [field.label]: e.target.value })}
                            required={field.required}
                            data-testid={`response-${index}`}
                          />
                        )}
                      </div>
                    ))}
                    <div className="flex gap-2">
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
                <CardHeader>
                  <CardTitle>{t('myForms')}</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2" data-testid="forms-list">
                    {forms.length === 0 ? (
                      <p className="text-gray-500">{t('noFormsAssigned')}</p>
                    ) : (
                      forms.map((form) => (
                        <div key={form.id} className="p-4 border rounded-lg flex justify-between items-center" data-testid={`form-${form.id}`}>
                          <div>
                            <p className="font-semibold">{t('formId')}: {form.id}</p>
                            <p className="text-sm text-gray-600">{t('fields')}: {form.fields.length}</p>
                            <span className={`inline-block mt-1 px-2 py-1 text-xs rounded ${
                              form.status === 'submitted' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                            }`}>
                              {t(form.status)}
                            </span>
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
              <CardHeader>
                <CardTitle>{t('myQuotations')}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2" data-testid="quotations-list">
                  {quotations.length === 0 ? (
                    <p className="text-gray-500">{t('noQuotationsReceived')}</p>
                  ) : (
                    quotations.map((quotation) => (
                      <div key={quotation.id} className="p-4 border rounded-lg" data-testid={`quotation-${quotation.id}`}>
                        <div className="flex justify-between items-start">
                          <div className="flex-1">
                            <p className="font-semibold">{t('quotationId')}: {quotation.id}</p>
                            <p className="text-sm text-gray-600">{t('form')}: {quotation.form_id}</p>
                            <p className="text-2xl font-bold text-green-600 mt-2">${quotation.price}</p>
                            <p className="text-sm mt-2 text-gray-700">{quotation.details}</p>
                            <span className={`inline-block mt-2 px-2 py-1 text-xs rounded ${
                              quotation.status === 'approved' ? 'bg-green-100 text-green-800' :
                              quotation.status === 'rejected' ? 'bg-red-100 text-red-800' :
                              quotation.status === 'modifications_requested' ? 'bg-blue-100 text-blue-800' :
                              'bg-yellow-100 text-yellow-800'
                            }`}>
                              {t(quotation.status)}
                            </span>
                          </div>
                          {quotation.status === 'pending' && (
                            <div className="flex gap-2 flex-col">
                              <Button 
                                onClick={() => handleRespondToQuotation(quotation.id, 'approved')}
                                data-testid={`approve-quotation-${quotation.id}`}
                                className="bg-green-600 hover:bg-green-700 text-white font-semibold shadow-md"
                              >
                                ✓ {t('approve')}
                              </Button>
                              <Button 
                                variant="outline"
                                onClick={() => handleRespondToQuotation(quotation.id, 'modifications_requested')}
                                data-testid={`modify-quotation-${quotation.id}`}
                                className="border-2 border-bayan-blue text-bayan-blue hover:bg-blue-50 font-semibold shadow-md"
                              >
                                ✎ {t('requestModifications')}
                              </Button>
                              <Button 
                                variant="destructive"
                                onClick={() => handleRespondToQuotation(quotation.id, 'rejected')}
                                data-testid={`reject-quotation-${quotation.id}`}
                                className="bg-red-600 hover:bg-red-700 font-semibold shadow-md"
                              >
                                ✕ {t('reject')}
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
              <CardHeader>
                <CardTitle>{t('myContracts')}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2" data-testid="contracts-list">
                  {contracts.length === 0 ? (
                    <p className="text-gray-500">{t('noContractsAvailable')}</p>
                  ) : (
                    contracts.map((contract) => (
                      <div key={contract.id} className="p-4 border rounded-lg flex justify-between items-center" data-testid={`contract-${contract.id}`}>
                        <div>
                          <p className="font-semibold">{t('contractId')}: {contract.id}</p>
                          <p className="text-sm text-gray-600">{t('quotation')}: {contract.quotation_id}</p>
                          <p className="text-sm text-gray-500">{t('created')}: {new Date(contract.created_at).toLocaleDateString()}</p>
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
