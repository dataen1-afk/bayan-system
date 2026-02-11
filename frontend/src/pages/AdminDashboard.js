import React, { useState, useEffect, useContext } from 'react';
import axios from 'axios';
import { API, AuthContext } from '@/App';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { LogOut, FileText, DollarSign, FileCheck } from 'lucide-react';

const AdminDashboard = () => {
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
      alert('Form created successfully!');
      setNewForm({ client_id: '', fields: [{ label: '', type: 'text', required: true }] });
      loadData();
    } catch (error) {
      alert('Error creating form: ' + (error.response?.data?.detail || error.message));
    }
  };

  const handleCreateQuotation = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/quotations`, {
        ...newQuotation,
        price: parseFloat(newQuotation.price)
      });
      alert('Quotation created and email sent!');
      setNewQuotation({ form_id: '', client_id: '', client_email: '', price: '', details: '' });
      loadData();
    } catch (error) {
      alert('Error creating quotation: ' + (error.response?.data?.detail || error.message));
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
    <div className="min-h-screen bg-gray-50" data-testid="admin-dashboard">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8 flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900" data-testid="admin-dashboard-title">Admin Dashboard</h1>
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
              Forms
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
            <Card>
              <CardHeader>
                <CardTitle>Create New Form</CardTitle>
                <CardDescription>Create a custom form for a client</CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleCreateForm} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="client_id">Client ID</Label>
                    <Input
                      id="client_id"
                      value={newForm.client_id}
                      onChange={(e) => setNewForm({ ...newForm, client_id: e.target.value })}
                      placeholder="Enter client user ID"
                      required
                      data-testid="form-client-id-input"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label>Form Fields</Label>
                    {newForm.fields.map((field, index) => (
                      <div key={index} className="flex gap-2 items-end">
                        <div className="flex-1">
                          <Input
                            placeholder="Field label"
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
                              <SelectItem value="text">Text</SelectItem>
                              <SelectItem value="textarea">Textarea</SelectItem>
                              <SelectItem value="email">Email</SelectItem>
                              <SelectItem value="number">Number</SelectItem>
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
                            Remove
                          </Button>
                        )}
                      </div>
                    ))}
                    <Button type="button" variant="outline" onClick={addFormField} data-testid="add-field-button">
                      Add Field
                    </Button>
                  </div>

                  <Button type="submit" data-testid="create-form-button">Create Form</Button>
                </form>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>All Forms</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2" data-testid="forms-list">
                  {forms.length === 0 ? (
                    <p className="text-gray-500">No forms created yet</p>
                  ) : (
                    forms.map((form) => (
                      <div key={form.id} className="p-4 border rounded-lg" data-testid={`form-${form.id}`}>
                        <div className="flex justify-between">
                          <div>
                            <p className="font-semibold">Form ID: {form.id}</p>
                            <p className="text-sm text-gray-600">Client: {form.client_id}</p>
                            <p className="text-sm text-gray-600">Status: {form.status}</p>
                            <p className="text-sm text-gray-600">Fields: {form.fields.length}</p>
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
                <CardTitle>Create Quotation</CardTitle>
                <CardDescription>Create a quotation for a submitted form</CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleCreateQuotation} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="form_id">Form ID</Label>
                    <Input
                      id="form_id"
                      value={newQuotation.form_id}
                      onChange={(e) => setNewQuotation({ ...newQuotation, form_id: e.target.value })}
                      placeholder="Enter form ID"
                      required
                      data-testid="quotation-form-id-input"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="q_client_id">Client ID</Label>
                    <Input
                      id="q_client_id"
                      value={newQuotation.client_id}
                      onChange={(e) => setNewQuotation({ ...newQuotation, client_id: e.target.value })}
                      placeholder="Enter client ID"
                      required
                      data-testid="quotation-client-id-input"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="client_email">Client Email</Label>
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
                    <Label htmlFor="price">Price</Label>
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
                    <Label htmlFor="details">Details</Label>
                    <Textarea
                      id="details"
                      value={newQuotation.details}
                      onChange={(e) => setNewQuotation({ ...newQuotation, details: e.target.value })}
                      placeholder="Service details..."
                      rows={4}
                      required
                      data-testid="quotation-details-input"
                    />
                  </div>

                  <Button type="submit" data-testid="create-quotation-button">Create Quotation</Button>
                </form>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>All Quotations</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2" data-testid="quotations-list">
                  {quotations.length === 0 ? (
                    <p className="text-gray-500">No quotations created yet</p>
                  ) : (
                    quotations.map((quotation) => (
                      <div key={quotation.id} className="p-4 border rounded-lg" data-testid={`quotation-${quotation.id}`}>
                        <div className="flex justify-between">
                          <div>
                            <p className="font-semibold">Quotation ID: {quotation.id}</p>
                            <p className="text-sm text-gray-600">Form: {quotation.form_id}</p>
                            <p className="text-sm text-gray-600">Client: {quotation.client_id}</p>
                            <p className="text-lg font-bold text-green-600">${quotation.price}</p>
                            <p className="text-sm mt-2">{quotation.details}</p>
                            <span className={`inline-block mt-2 px-2 py-1 text-xs rounded ${
                              quotation.status === 'approved' ? 'bg-green-100 text-green-800' :
                              quotation.status === 'rejected' ? 'bg-red-100 text-red-800' :
                              'bg-yellow-100 text-yellow-800'
                            }`}>
                              {quotation.status}
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
                <CardTitle>All Contracts</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2" data-testid="contracts-list">
                  {contracts.length === 0 ? (
                    <p className="text-gray-500">No contracts generated yet</p>
                  ) : (
                    contracts.map((contract) => (
                      <div key={contract.id} className="p-4 border rounded-lg flex justify-between items-center" data-testid={`contract-${contract.id}`}>
                        <div>
                          <p className="font-semibold">Contract ID: {contract.id}</p>
                          <p className="text-sm text-gray-600">Quotation: {contract.quotation_id}</p>
                          <p className="text-sm text-gray-600">Client: {contract.client_id}</p>
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

export default AdminDashboard;
