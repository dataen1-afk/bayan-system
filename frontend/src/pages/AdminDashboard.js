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
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { LogOut, FileText, DollarSign, FileCheck } from 'lucide-react';
import LanguageSwitcher from '@/components/LanguageSwitcher';

const AdminDashboard = () => {
  const { t } = useTranslation();
  const { user, logout } = useContext(AuthContext);
  const [forms, setForms] = useState([]);
  const [quotations, setQuotations] = useState([]);
  const [contracts, setContracts] = useState([]);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);

  // Form creation state
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

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-gray-50 to-blue-50" data-testid="admin-dashboard">
      {/* Header */}
      <header className="bg-gradient-to-r from-bayan-blue to-blue-600 shadow-lg border-b-4 border-blue-700">
        <div className="max-w-7xl mx-auto px-4 py-5 sm:px-6 lg:px-8 flex justify-between items-center">
          <div className="flex items-center gap-4">
            <div className="bg-white p-2 rounded-lg shadow-md">
              <img src="/bayan-logo.png" alt="Bayan" className="h-10 w-auto object-contain" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white" data-testid="admin-dashboard-title">{t('adminDashboard')}</h1>
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
              {t('forms')}
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
            <Card>
              <CardHeader>
                <CardTitle>{t('createNewForm')}</CardTitle>
                <CardDescription>{t('createCustomForm')}</CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleCreateForm} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="client_id">{t('clientId')}</Label>
                    <Input
                      id="client_id"
                      value={newForm.client_id}
                      onChange={(e) => setNewForm({ ...newForm, client_id: e.target.value })}
                      placeholder={t('enterClientId')}
                      required
                      data-testid="form-client-id-input"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label>{t('formFields')}</Label>
                    {newForm.fields.map((field, index) => (
                      <div key={index} className="flex gap-2 items-end">
                        <div className="flex-1">
                          <Input
                            placeholder={t('fieldLabel')}
                            value={field.label}
                            onChange={(e) => updateFormField(index, 'label', e.target.value)}
                            required
                            data-testid={`field-label-${index}`}
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
              <CardHeader>
                <CardTitle>{t('allForms')}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2" data-testid="forms-list">
                  {forms.length === 0 ? (
                    <p className="text-gray-500">{t('noFormsCreated')}</p>
                  ) : (
                    forms.map((form) => (
                      <div key={form.id} className="p-4 border rounded-lg" data-testid={`form-${form.id}`}>
                        <div className="flex justify-between">
                          <div>
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
          </TabsContent>

          {/* Quotations Tab */}
          <TabsContent value="quotations" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>{t('createQuotation')}</CardTitle>
                <CardDescription>{t('createQuotationFor')}</CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleCreateQuotation} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="form_id">{t('formId')}</Label>
                    <Input
                      id="form_id"
                      value={newQuotation.form_id}
                      onChange={(e) => setNewQuotation({ ...newQuotation, form_id: e.target.value })}
                      placeholder={t('enterFormId')}
                      required
                      data-testid="quotation-form-id-input"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="q_client_id">{t('clientId')}</Label>
                    <Input
                      id="q_client_id"
                      value={newQuotation.client_id}
                      onChange={(e) => setNewQuotation({ ...newQuotation, client_id: e.target.value })}
                      placeholder={t('enterClientId')}
                      required
                      data-testid="quotation-client-id-input"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="client_email">{t('clientEmail')}</Label>
                    <Input
                      id="client_email"
                      type="email"
                      value={newQuotation.client_email}
                      onChange={(e) => setNewQuotation({ ...newQuotation, client_email: e.target.value })}
                      placeholder="client@example.com"
                      required
                      data-testid="quotation-client-email-input"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="price">{t('price')}</Label>
                    <Input
                      id="price"
                      type="number"
                      step="0.01"
                      value={newQuotation.price}
                      onChange={(e) => setNewQuotation({ ...newQuotation, price: e.target.value })}
                      placeholder="1000.00"
                      required
                      data-testid="quotation-price-input"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="details">{t('details')}</Label>
                    <Textarea
                      id="details"
                      value={newQuotation.details}
                      onChange={(e) => setNewQuotation({ ...newQuotation, details: e.target.value })}
                      placeholder={t('serviceDetails')}
                      rows={4}
                      required
                      data-testid="quotation-details-input"
                    />
                  </div>

                  <Button type="submit" data-testid="create-quotation-button">{t('createQuotation')}</Button>
                </form>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>{t('allQuotations')}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2" data-testid="quotations-list">
                  {quotations.length === 0 ? (
                    <p className="text-gray-500">{t('noQuotationsCreated')}</p>
                  ) : (
                    quotations.map((quotation) => (
                      <div key={quotation.id} className="p-4 border rounded-lg" data-testid={`quotation-${quotation.id}`}>
                        <div className="flex justify-between">
                          <div>
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
          </TabsContent>

          {/* Contracts Tab */}
          <TabsContent value="contracts">
            <Card>
              <CardHeader>
                <CardTitle>{t('allContracts')}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2" data-testid="contracts-list">
                  {contracts.length === 0 ? (
                    <p className="text-gray-500">{t('noContractsGenerated')}</p>
                  ) : (
                    contracts.map((contract) => (
                      <div key={contract.id} className="p-4 border rounded-lg flex justify-between items-center" data-testid={`contract-${contract.id}`}>
                        <div>
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
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
};

export default AdminDashboard;
