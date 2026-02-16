import React, { useState, useEffect, useContext } from 'react';
import axios from 'axios';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { 
  ArrowLeft, Plus, X, FileText, DollarSign, Clock, CheckCircle, AlertCircle,
  Send, Eye, Trash2, CreditCard, Building2, Calendar, Search, Filter,
  TrendingUp, TrendingDown, Receipt, LogOut
} from 'lucide-react';
import Sidebar from '@/components/Sidebar';
import LanguageSwitcher from '@/components/LanguageSwitcher';
import NotificationBell from '@/components/NotificationBell';
import { AuthContext } from '@/App';

const API = process.env.REACT_APP_BACKEND_URL + '/api';

const formatCurrency = (amount, currency = 'SAR') => {
  return new Intl.NumberFormat('en-US', { 
    minimumFractionDigits: 2,
    maximumFractionDigits: 2 
  }).format(amount || 0) + ' ' + currency;
};

const formatDate = (dateString) => {
  if (!dateString) return '-';
  return new Date(dateString).toLocaleDateString('en-GB', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  });
};

const InvoicesPage = () => {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const { user, logout } = useContext(AuthContext);
  const isRTL = i18n.language?.startsWith('ar');
  
  const [loading, setLoading] = useState(true);
  const [invoices, setInvoices] = useState([]);
  const [contracts, setContracts] = useState([]);
  const [stats, setStats] = useState({});
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  
  // Modals
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showViewModal, setShowViewModal] = useState(false);
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [selectedInvoice, setSelectedInvoice] = useState(null);
  
  // Form state
  const [formData, setFormData] = useState({
    contract_id: '',
    tax_rate: 15,
    payment_terms: 'net_30',
    due_date: '',
    notes: ''
  });
  
  const [paymentData, setPaymentData] = useState({
    amount: 0,
    payment_date: new Date().toISOString().split('T')[0],
    payment_method: 'bank_transfer',
    reference: '',
    notes: ''
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const token = localStorage.getItem('token');
      const headers = { Authorization: `Bearer ${token}` };
      
      const [invoicesRes, statsRes, proposalsRes] = await Promise.all([
        axios.get(`${API}/invoices`, { headers }),
        axios.get(`${API}/invoices/stats`, { headers }),
        axios.get(`${API}/proposals`, { headers })
      ]);
      
      setInvoices(invoicesRes.data);
      setStats(statsRes.data);
      // Only show signed contracts
      setContracts(proposalsRes.data.filter(p => p.status === 'agreement_signed'));
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateInvoice = async () => {
    if (!formData.contract_id) {
      alert(t('selectContract'));
      return;
    }
    
    try {
      const token = localStorage.getItem('token');
      await axios.post(`${API}/invoices`, formData, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setShowCreateModal(false);
      setFormData({ contract_id: '', tax_rate: 15, payment_terms: 'net_30', due_date: '', notes: '' });
      loadData();
    } catch (error) {
      alert(t('errorCreatingInvoice') + ': ' + (error.response?.data?.detail || error.message));
    }
  };

  const handleSendInvoice = async (invoiceId) => {
    try {
      const token = localStorage.getItem('token');
      await axios.post(`${API}/invoices/${invoiceId}/send`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      loadData();
    } catch (error) {
      alert(t('errorSendingInvoice'));
    }
  };

  const handleRecordPayment = async () => {
    if (!selectedInvoice || paymentData.amount <= 0) {
      alert(t('enterValidAmount'));
      return;
    }
    
    try {
      const token = localStorage.getItem('token');
      await axios.post(`${API}/invoices/${selectedInvoice.id}/record-payment`, paymentData, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setShowPaymentModal(false);
      setPaymentData({ amount: 0, payment_date: new Date().toISOString().split('T')[0], payment_method: 'bank_transfer', reference: '', notes: '' });
      loadData();
    } catch (error) {
      alert(t('errorRecordingPayment'));
    }
  };

  const handleDeleteInvoice = async (invoiceId) => {
    if (!window.confirm(t('confirmDeleteInvoice'))) return;
    
    try {
      const token = localStorage.getItem('token');
      await axios.delete(`${API}/invoices/${invoiceId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      loadData();
    } catch (error) {
      alert(error.response?.data?.detail || t('errorDeletingInvoice'));
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      draft: 'bg-slate-100 text-slate-700 border-slate-200',
      sent: 'bg-blue-100 text-blue-700 border-blue-200',
      viewed: 'bg-purple-100 text-purple-700 border-purple-200',
      paid: 'bg-emerald-100 text-emerald-700 border-emerald-200',
      overdue: 'bg-red-100 text-red-700 border-red-200',
      cancelled: 'bg-gray-100 text-gray-700 border-gray-200'
    };
    return colors[status] || colors.draft;
  };

  const filteredInvoices = invoices.filter(inv => {
    const matchesSearch = inv.organization_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          inv.invoice_number?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'all' || inv.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-xl">{t('loading')}...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-gray-50 to-blue-50" dir={isRTL ? 'rtl' : 'ltr'}>
      {/* Fixed Header */}
      <header className="fixed top-0 left-0 right-0 z-40 bg-white shadow-md">
        <div className="max-w-full mx-auto px-4 py-3 sm:px-6 lg:px-8 flex justify-between items-center">
          <div className={`flex gap-3 items-center ${isRTL ? 'order-first' : 'order-last'}`}>
            <NotificationBell />
            <LanguageSwitcher />
            <Button variant="outline" onClick={logout} className="bg-bayan-navy text-white hover:bg-bayan-navy-light border-bayan-navy font-semibold">
              <LogOut className="w-4 h-4" />
              {t('logout')}
            </Button>
          </div>
          <div className={isRTL ? 'order-last' : 'order-first'}>
            <div className="-my-2">
              <img src="/bayan-logo.png" alt="Bayan" className="h-20 w-auto object-contain" />
            </div>
          </div>
        </div>
        <div className="h-1.5 bg-gradient-to-r from-bayan-navy via-bayan-navy-light to-bayan-navy"></div>
      </header>

      {/* Layout with Sidebar */}
      <div className="flex pt-[102px]">
        <Sidebar 
          activeTab="invoices" 
          onTabChange={(tab) => {
            if (tab === 'forms' || tab === 'quotations' || tab === 'contracts' || tab === 'templates' || tab === 'reports') {
              navigate(`/dashboard?tab=${tab}`);
            }
          }}
          userRole="admin"
          userName={user?.name}
          dashboardTitle={t('adminDashboard')}
        />
        
        {/* Main Content */}
        <main className="flex-1 p-4 lg:p-6 min-h-screen">
          <div className="w-full">
            {/* Header */}
            <div className={`flex items-center justify-between mb-6 ${isRTL ? 'flex-row-reverse' : ''}`}>
              <div className={`flex items-center gap-4 ${isRTL ? 'flex-row-reverse' : ''}`}>
                <Button variant="ghost" onClick={() => navigate('/dashboard')} className={`${isRTL ? 'flex-row-reverse' : ''}`}>
                  <ArrowLeft className={`w-4 h-4 ${isRTL ? 'rotate-180 ml-2' : 'mr-2'}`} />
                  {t('backToDashboard')}
                </Button>
                <div>
                  <h1 className={`text-2xl font-bold text-slate-900 flex items-center gap-2 ${isRTL ? 'flex-row-reverse' : ''}`}>
                    <Receipt className="w-7 h-7 text-bayan-navy" />
                    {t('invoices')}
                  </h1>
                </div>
              </div>
              
              <Button onClick={() => setShowCreateModal(true)} className="bg-bayan-primary hover:bg-bayan-primary/90" data-testid="create-invoice-btn">
                <Plus className={`w-4 h-4 ${isRTL ? 'ml-2' : 'mr-2'}`} />
                {t('createInvoice')}
              </Button>
            </div>

          {/* Stats Cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <Card className="border-slate-200">
              <CardContent className="pt-4">
                <div className={`flex items-center gap-3 ${isRTL ? 'flex-row-reverse' : ''}`}>
                  <div className="p-2 bg-blue-100 rounded-lg">
                    <FileText className="w-5 h-5 text-blue-600" />
                  </div>
                  <div className={isRTL ? 'text-right' : ''}>
                    <p className="text-2xl font-bold">{stats.total_invoices || 0}</p>
                    <p className="text-xs text-slate-500">{t('totalInvoices')}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
            
            <Card className="border-emerald-200">
              <CardContent className="pt-4">
                <div className={`flex items-center gap-3 ${isRTL ? 'flex-row-reverse' : ''}`}>
                  <div className="p-2 bg-emerald-100 rounded-lg">
                    <CheckCircle className="w-5 h-5 text-emerald-600" />
                  </div>
                  <div className={isRTL ? 'text-right' : ''}>
                    <p className="text-2xl font-bold text-emerald-700">{formatCurrency(stats.total_paid || 0)}</p>
                    <p className="text-xs text-slate-500">{t('totalPaid')}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
            
            <Card className="border-amber-200">
              <CardContent className="pt-4">
                <div className={`flex items-center gap-3 ${isRTL ? 'flex-row-reverse' : ''}`}>
                  <div className="p-2 bg-amber-100 rounded-lg">
                    <Clock className="w-5 h-5 text-amber-600" />
                  </div>
                  <div className={isRTL ? 'text-right' : ''}>
                    <p className="text-2xl font-bold text-amber-700">{formatCurrency(stats.total_pending || 0)}</p>
                    <p className="text-xs text-slate-500">{t('pending')}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
            
            <Card className="border-red-200">
              <CardContent className="pt-4">
                <div className={`flex items-center gap-3 ${isRTL ? 'flex-row-reverse' : ''}`}>
                  <div className="p-2 bg-red-100 rounded-lg">
                    <AlertCircle className="w-5 h-5 text-red-600" />
                  </div>
                  <div className={isRTL ? 'text-right' : ''}>
                    <p className="text-2xl font-bold text-red-700">{formatCurrency(stats.total_overdue || 0)}</p>
                    <p className="text-xs text-slate-500">{t('overdue')}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Filters */}
          <div className={`flex items-center gap-4 mb-6 ${isRTL ? 'flex-row-reverse' : ''}`}>
            <div className="relative flex-1 max-w-md">
              <Search className={`absolute top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 ${isRTL ? 'right-3' : 'left-3'}`} />
              <Input
                placeholder={t('searchInvoices')}
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className={isRTL ? 'pr-10' : 'pl-10'}
              />
            </div>
            
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-[180px]">
                <Filter className="w-4 h-4 mr-2" />
                <SelectValue placeholder={t('filterByStatus')} />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">{t('allStatuses')}</SelectItem>
                <SelectItem value="draft">{t('draft')}</SelectItem>
                <SelectItem value="sent">{t('sent')}</SelectItem>
                <SelectItem value="paid">{t('paid')}</SelectItem>
                <SelectItem value="overdue">{t('overdue')}</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Invoices List */}
          <Card>
            <CardContent className="p-0">
              {filteredInvoices.length === 0 ? (
                <div className="text-center py-16">
                  <Receipt className="w-16 h-16 mx-auto text-slate-300 mb-4" />
                  <h3 className="text-lg font-semibold text-slate-700 mb-2">{t('noInvoices')}</h3>
                  <p className="text-sm text-slate-500">{t('createFirstInvoice')}</p>
                </div>
              ) : (
                <div className="divide-y divide-slate-100">
                  {filteredInvoices.map((invoice) => (
                    <div 
                      key={invoice.id}
                      className={`p-4 hover:bg-slate-50 transition-colors ${isRTL ? 'text-right' : ''}`}
                    >
                      <div className={`flex items-center justify-between ${isRTL ? 'flex-row-reverse' : ''}`}>
                        <div className={`flex items-center gap-4 ${isRTL ? 'flex-row-reverse' : ''}`}>
                          <div className="p-2 bg-slate-100 rounded-lg">
                            <FileText className="w-5 h-5 text-slate-600" />
                          </div>
                          <div>
                            <div className={`flex items-center gap-2 ${isRTL ? 'flex-row-reverse' : ''}`}>
                              <span className="font-semibold text-slate-900">{invoice.invoice_number}</span>
                              <span className={`px-2 py-0.5 text-xs font-medium rounded-full border ${getStatusColor(invoice.status)}`}>
                                {t(invoice.status)}
                              </span>
                            </div>
                            <div className={`flex items-center gap-3 mt-1 text-sm text-slate-500 ${isRTL ? 'flex-row-reverse' : ''}`}>
                              <span className={`flex items-center gap-1 ${isRTL ? 'flex-row-reverse' : ''}`}>
                                <Building2 className="w-3 h-3" />
                                {invoice.organization_name}
                              </span>
                              <span className={`flex items-center gap-1 ${isRTL ? 'flex-row-reverse' : ''}`}>
                                <Calendar className="w-3 h-3" />
                                {t('due')}: {formatDate(invoice.due_date)}
                              </span>
                            </div>
                          </div>
                        </div>
                        
                        <div className={`flex items-center gap-4 ${isRTL ? 'flex-row-reverse' : ''}`}>
                          <div className={isRTL ? 'text-left' : 'text-right'}>
                            <p className="font-bold text-lg">{formatCurrency(invoice.total_amount, invoice.currency)}</p>
                            {invoice.paid_amount > 0 && invoice.status !== 'paid' && (
                              <p className="text-xs text-emerald-600">{t('paid')}: {formatCurrency(invoice.paid_amount, invoice.currency)}</p>
                            )}
                          </div>
                          
                          <div className={`flex items-center gap-2 ${isRTL ? 'flex-row-reverse' : ''}`}>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => { setSelectedInvoice(invoice); setShowViewModal(true); }}
                              title={t('view')}
                            >
                              <Eye className="w-4 h-4" />
                            </Button>
                            
                            {invoice.status === 'draft' && (
                              <>
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  onClick={() => handleSendInvoice(invoice.id)}
                                  className="text-blue-600 hover:text-blue-800"
                                  title={t('send')}
                                >
                                  <Send className="w-4 h-4" />
                                </Button>
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  onClick={() => handleDeleteInvoice(invoice.id)}
                                  className="text-red-600 hover:text-red-800"
                                  title={t('delete')}
                                >
                                  <Trash2 className="w-4 h-4" />
                                </Button>
                              </>
                            )}
                            
                            {['sent', 'viewed', 'overdue'].includes(invoice.status) && (
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => { 
                                  setSelectedInvoice(invoice); 
                                  setPaymentData({ ...paymentData, amount: invoice.total_amount - (invoice.paid_amount || 0) });
                                  setShowPaymentModal(true); 
                                }}
                                className="text-emerald-600 hover:text-emerald-800"
                                title={t('recordPayment')}
                              >
                                <CreditCard className="w-4 h-4" />
                              </Button>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
          </div>
        </main>
      </div>

      {/* Create Invoice Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <Card className="w-full max-w-lg">
            <CardHeader>
              <div className={`flex items-center justify-between ${isRTL ? 'flex-row-reverse' : ''}`}>
                <CardTitle>{t('createInvoice')}</CardTitle>
                <Button variant="ghost" size="sm" onClick={() => setShowCreateModal(false)}>
                  <X className="w-4 h-4" />
                </Button>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label>{t('selectContract')} *</Label>
                <Select value={formData.contract_id} onValueChange={(v) => setFormData({ ...formData, contract_id: v })}>
                  <SelectTrigger>
                    <SelectValue placeholder={t('selectContract')} />
                  </SelectTrigger>
                  <SelectContent>
                    {contracts.map((contract) => (
                      <SelectItem key={contract.id} value={contract.id}>
                        {contract.organization_name} - {formatCurrency(contract.total_amount)}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>{t('taxRate')} (%)</Label>
                  <Input
                    type="number"
                    value={formData.tax_rate}
                    onChange={(e) => setFormData({ ...formData, tax_rate: parseFloat(e.target.value) || 0 })}
                  />
                </div>
                <div className="space-y-2">
                  <Label>{t('paymentTerms')}</Label>
                  <Select value={formData.payment_terms} onValueChange={(v) => setFormData({ ...formData, payment_terms: v })}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="due_on_receipt">{t('dueOnReceipt')}</SelectItem>
                      <SelectItem value="net_15">{t('net15')}</SelectItem>
                      <SelectItem value="net_30">{t('net30')}</SelectItem>
                      <SelectItem value="net_60">{t('net60')}</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              
              <div className="space-y-2">
                <Label>{t('notes')}</Label>
                <Textarea
                  value={formData.notes}
                  onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                  placeholder={t('invoiceNotes')}
                />
              </div>
              
              <div className={`flex gap-2 pt-4 ${isRTL ? 'flex-row-reverse' : ''}`}>
                <Button onClick={handleCreateInvoice} className="flex-1 bg-bayan-primary hover:bg-bayan-primary/90">
                  {t('createInvoice')}
                </Button>
                <Button variant="outline" onClick={() => setShowCreateModal(false)}>
                  {t('cancel')}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Record Payment Modal */}
      {showPaymentModal && selectedInvoice && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <Card className="w-full max-w-lg">
            <CardHeader>
              <div className={`flex items-center justify-between ${isRTL ? 'flex-row-reverse' : ''}`}>
                <CardTitle>{t('recordPayment')}</CardTitle>
                <Button variant="ghost" size="sm" onClick={() => setShowPaymentModal(false)}>
                  <X className="w-4 h-4" />
                </Button>
              </div>
              <CardDescription>
                {selectedInvoice.invoice_number} - {selectedInvoice.organization_name}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="p-4 bg-slate-50 rounded-lg">
                <div className={`flex justify-between ${isRTL ? 'flex-row-reverse' : ''}`}>
                  <span className="text-slate-600">{t('totalAmount')}:</span>
                  <span className="font-bold">{formatCurrency(selectedInvoice.total_amount, selectedInvoice.currency)}</span>
                </div>
                <div className={`flex justify-between mt-2 ${isRTL ? 'flex-row-reverse' : ''}`}>
                  <span className="text-slate-600">{t('alreadyPaid')}:</span>
                  <span className="text-emerald-600">{formatCurrency(selectedInvoice.paid_amount || 0, selectedInvoice.currency)}</span>
                </div>
                <div className={`flex justify-between mt-2 border-t pt-2 ${isRTL ? 'flex-row-reverse' : ''}`}>
                  <span className="font-semibold">{t('remaining')}:</span>
                  <span className="font-bold text-red-600">{formatCurrency(selectedInvoice.total_amount - (selectedInvoice.paid_amount || 0), selectedInvoice.currency)}</span>
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>{t('amount')} *</Label>
                  <Input
                    type="number"
                    value={paymentData.amount}
                    onChange={(e) => setPaymentData({ ...paymentData, amount: parseFloat(e.target.value) || 0 })}
                  />
                </div>
                <div className="space-y-2">
                  <Label>{t('paymentDate')}</Label>
                  <Input
                    type="date"
                    value={paymentData.payment_date}
                    onChange={(e) => setPaymentData({ ...paymentData, payment_date: e.target.value })}
                  />
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>{t('paymentMethod')}</Label>
                  <Select value={paymentData.payment_method} onValueChange={(v) => setPaymentData({ ...paymentData, payment_method: v })}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="bank_transfer">{t('bankTransfer')}</SelectItem>
                      <SelectItem value="cash">{t('cash')}</SelectItem>
                      <SelectItem value="cheque">{t('cheque')}</SelectItem>
                      <SelectItem value="stripe">{t('stripe')}</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label>{t('reference')}</Label>
                  <Input
                    value={paymentData.reference}
                    onChange={(e) => setPaymentData({ ...paymentData, reference: e.target.value })}
                    placeholder={t('transactionId')}
                  />
                </div>
              </div>
              
              <div className={`flex gap-2 pt-4 ${isRTL ? 'flex-row-reverse' : ''}`}>
                <Button onClick={handleRecordPayment} className="flex-1 bg-emerald-600 hover:bg-emerald-700">
                  <CreditCard className={`w-4 h-4 ${isRTL ? 'ml-2' : 'mr-2'}`} />
                  {t('recordPayment')}
                </Button>
                <Button variant="outline" onClick={() => setShowPaymentModal(false)}>
                  {t('cancel')}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* View Invoice Modal */}
      {showViewModal && selectedInvoice && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <Card className="w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <CardHeader>
              <div className={`flex items-center justify-between ${isRTL ? 'flex-row-reverse' : ''}`}>
                <div>
                  <CardTitle className={`flex items-center gap-2 ${isRTL ? 'flex-row-reverse' : ''}`}>
                    {selectedInvoice.invoice_number}
                    <span className={`px-2 py-0.5 text-xs font-medium rounded-full border ${getStatusColor(selectedInvoice.status)}`}>
                      {t(selectedInvoice.status)}
                    </span>
                  </CardTitle>
                  <CardDescription>{selectedInvoice.organization_name}</CardDescription>
                </div>
                <Button variant="ghost" size="sm" onClick={() => setShowViewModal(false)}>
                  <X className="w-4 h-4" />
                </Button>
              </div>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Invoice Details */}
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-slate-500">{t('issueDate')}</p>
                  <p className="font-medium">{formatDate(selectedInvoice.issue_date)}</p>
                </div>
                <div>
                  <p className="text-slate-500">{t('dueDate')}</p>
                  <p className="font-medium">{formatDate(selectedInvoice.due_date)}</p>
                </div>
                <div>
                  <p className="text-slate-500">{t('email')}</p>
                  <p className="font-medium">{selectedInvoice.contact_email || '-'}</p>
                </div>
                <div>
                  <p className="text-slate-500">{t('phone')}</p>
                  <p className="font-medium" dir="ltr">{selectedInvoice.contact_phone || '-'}</p>
                </div>
              </div>
              
              {/* Items */}
              <div>
                <h4 className="font-semibold mb-3">{t('items')}</h4>
                <div className="border rounded-lg overflow-hidden">
                  <table className="w-full text-sm">
                    <thead className="bg-slate-50">
                      <tr>
                        <th className={`p-3 ${isRTL ? 'text-right' : 'text-left'}`}>{t('description')}</th>
                        <th className="p-3 text-center">{t('qty')}</th>
                        <th className={`p-3 ${isRTL ? 'text-left' : 'text-right'}`}>{t('unitPrice')}</th>
                        <th className={`p-3 ${isRTL ? 'text-left' : 'text-right'}`}>{t('total')}</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y">
                      {selectedInvoice.items?.map((item, idx) => (
                        <tr key={idx}>
                          <td className={`p-3 ${isRTL ? 'text-right' : ''}`}>
                            {item.description}
                            {item.description_ar && <span className="block text-xs text-slate-500">{item.description_ar}</span>}
                          </td>
                          <td className="p-3 text-center">{item.quantity}</td>
                          <td className={`p-3 ${isRTL ? 'text-left' : 'text-right'}`}>{formatCurrency(item.unit_price, selectedInvoice.currency)}</td>
                          <td className={`p-3 ${isRTL ? 'text-left' : 'text-right'}`}>{formatCurrency(item.total || item.unit_price * item.quantity, selectedInvoice.currency)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
              
              {/* Totals */}
              <div className={`${isRTL ? 'text-left' : 'text-right'} space-y-2`}>
                <div className={`flex justify-between ${isRTL ? 'flex-row-reverse' : ''}`}>
                  <span className="text-slate-600">{t('subtotal')}:</span>
                  <span>{formatCurrency(selectedInvoice.subtotal, selectedInvoice.currency)}</span>
                </div>
                <div className={`flex justify-between ${isRTL ? 'flex-row-reverse' : ''}`}>
                  <span className="text-slate-600">{t('tax')} ({selectedInvoice.tax_rate}%):</span>
                  <span>{formatCurrency(selectedInvoice.tax_amount, selectedInvoice.currency)}</span>
                </div>
                <div className={`flex justify-between text-lg font-bold border-t pt-2 ${isRTL ? 'flex-row-reverse' : ''}`}>
                  <span>{t('total')}:</span>
                  <span>{formatCurrency(selectedInvoice.total_amount, selectedInvoice.currency)}</span>
                </div>
                {selectedInvoice.paid_amount > 0 && (
                  <>
                    <div className={`flex justify-between text-emerald-600 ${isRTL ? 'flex-row-reverse' : ''}`}>
                      <span>{t('paid')}:</span>
                      <span>-{formatCurrency(selectedInvoice.paid_amount, selectedInvoice.currency)}</span>
                    </div>
                    <div className={`flex justify-between text-lg font-bold text-red-600 ${isRTL ? 'flex-row-reverse' : ''}`}>
                      <span>{t('balanceDue')}:</span>
                      <span>{formatCurrency(selectedInvoice.total_amount - selectedInvoice.paid_amount, selectedInvoice.currency)}</span>
                    </div>
                  </>
                )}
              </div>
              
              {selectedInvoice.notes && (
                <div>
                  <h4 className="font-semibold mb-2">{t('notes')}</h4>
                  <p className="text-sm text-slate-600 bg-slate-50 p-3 rounded-lg">{selectedInvoice.notes}</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
};

export default InvoicesPage;
