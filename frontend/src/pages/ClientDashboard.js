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
      alert(t(status === 'approved' ? 'quotationApproved' : 'quotationRejected'));
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
    <div className="min-h-screen bg-gray-50" data-testid="client-dashboard">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8 flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900" data-testid="client-dashboard-title">Client Dashboard</h1>
            <p className="text-sm text-gray-600">Welcome, {user?.name}</p>
          </div>
          <Button variant="outline" onClick={logout} data-testid="logout-button">
            <LogOut className="w-4 h-4 mr-2" />
            Logout
          </Button>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        <Tabs defaultValue="forms" className="space-y-4">
          <TabsList>
            <TabsTrigger value="forms" data-testid="forms-tab">
              <FileText className="w-4 h-4 mr-2" />
              My Forms
            </TabsTrigger>
            <TabsTrigger value="quotations" data-testid="quotations-tab">
              <DollarSign className="w-4 h-4 mr-2" />
              Quotations
            </TabsTrigger>
            <TabsTrigger value="contracts" data-testid="contracts-tab">
              <FileCheck className="w-4 h-4 mr-2" />
              Contracts
            </TabsTrigger>
          </TabsList>

          {/* Forms Tab */}
          <TabsContent value="forms" className="space-y-4">
            {selectedForm ? (
              <Card>
                <CardHeader>
                  <CardTitle>Submit Form</CardTitle>
                  <CardDescription>Fill out the form below</CardDescription>
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
                      <Button type="submit" data-testid="submit-form-button">Submit Form</Button>
                      <Button type="button" variant="outline" onClick={() => setSelectedForm(null)} data-testid="cancel-form-button">
                        Cancel
                      </Button>
                    </div>
                  </form>
                </CardContent>
              </Card>
            ) : (
              <Card>
                <CardHeader>
                  <CardTitle>My Forms</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2" data-testid="forms-list">
                    {forms.length === 0 ? (
                      <p className="text-gray-500">No forms assigned to you yet</p>
                    ) : (
                      forms.map((form) => (
                        <div key={form.id} className="p-4 border rounded-lg flex justify-between items-center" data-testid={`form-${form.id}`}>
                          <div>
                            <p className="font-semibold">Form ID: {form.id}</p>
                            <p className="text-sm text-gray-600">Fields: {form.fields.length}</p>
                            <span className={`inline-block mt-1 px-2 py-1 text-xs rounded ${
                              form.status === 'submitted' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                            }`}>
                              {form.status}
                            </span>
                          </div>
                          {form.status === 'pending' && (
                            <Button onClick={() => setSelectedForm(form)} data-testid={`fill-form-${form.id}`}>
                              Fill Form
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
                <CardTitle>My Quotations</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2" data-testid="quotations-list">
                  {quotations.length === 0 ? (
                    <p className="text-gray-500">No quotations received yet</p>
                  ) : (
                    quotations.map((quotation) => (
                      <div key={quotation.id} className="p-4 border rounded-lg" data-testid={`quotation-${quotation.id}`}>
                        <div className="flex justify-between items-start">
                          <div className="flex-1">
                            <p className="font-semibold">Quotation ID: {quotation.id}</p>
                            <p className="text-sm text-gray-600">Form: {quotation.form_id}</p>
                            <p className="text-2xl font-bold text-green-600 mt-2">${quotation.price}</p>
                            <p className="text-sm mt-2 text-gray-700">{quotation.details}</p>
                            <span className={`inline-block mt-2 px-2 py-1 text-xs rounded ${
                              quotation.status === 'approved' ? 'bg-green-100 text-green-800' :
                              quotation.status === 'rejected' ? 'bg-red-100 text-red-800' :
                              'bg-yellow-100 text-yellow-800'
                            }`}>
                              {quotation.status}
                            </span>
                          </div>
                          {quotation.status === 'pending' && (
                            <div className="flex gap-2">
                              <Button 
                                onClick={() => handleRespondToQuotation(quotation.id, 'approved')}
                                data-testid={`approve-quotation-${quotation.id}`}
                              >
                                Approve
                              </Button>
                              <Button 
                                variant="destructive"
                                onClick={() => handleRespondToQuotation(quotation.id, 'rejected')}
                                data-testid={`reject-quotation-${quotation.id}`}
                              >
                                Reject
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
                <CardTitle>My Contracts</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2" data-testid="contracts-list">
                  {contracts.length === 0 ? (
                    <p className="text-gray-500">No contracts available yet</p>
                  ) : (
                    contracts.map((contract) => (
                      <div key={contract.id} className="p-4 border rounded-lg flex justify-between items-center" data-testid={`contract-${contract.id}`}>
                        <div>
                          <p className="font-semibold">Contract ID: {contract.id}</p>
                          <p className="text-sm text-gray-600">Quotation: {contract.quotation_id}</p>
                          <p className="text-sm text-gray-500">Created: {new Date(contract.created_at).toLocaleDateString()}</p>
                        </div>
                        <Button onClick={() => downloadContract(contract.id)} data-testid={`download-contract-${contract.id}`}>
                          Download PDF
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
