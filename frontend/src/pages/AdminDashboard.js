import React, { useState, useEffect, useContext } from 'react';
import axios from 'axios';
import { useTranslation } from 'react-i18next';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { API, AuthContext } from '@/App';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { LogOut, FileText, DollarSign, FileCheck, FolderOpen, BarChart3, Settings, Plus, Eye, X, Send, Copy, Mail, Link, CheckCircle, Download, Clock, Building2, User, Calendar } from 'lucide-react';
import LanguageSwitcher from '@/components/LanguageSwitcher';
import Sidebar from '@/components/Sidebar';
import ApplicationForm from '@/components/ApplicationForm';
import NotificationBell from '@/components/NotificationBell';
import StatusTimeline from '@/components/StatusTimeline';
import DataTable from '@/components/DataTable';

// Format currency with Western Arabic numerals and SAR
const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-US', { 
    minimumFractionDigits: 0,
    maximumFractionDigits: 0 
  }).format(amount || 0) + ' SAR';
};

// Format date with Western Arabic numerals
const formatDate = (dateString) => {
  if (!dateString) return '';
  return new Date(dateString).toLocaleDateString('en-GB', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  });
};

const AdminDashboard = () => {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const [isRTL, setIsRTL] = useState(() => {
    return i18n.language?.startsWith('ar') || document.documentElement.dir === 'rtl';
  });
  const { user, logout } = useContext(AuthContext);
  const [activeTab, setActiveTab] = useState(() => {
    // Initialize from URL params if available
    const tabParam = new URLSearchParams(window.location.search).get('tab');
    return tabParam || 'forms';
  });
  const [highlightedId, setHighlightedId] = useState(null);
  const [forms, setForms] = useState([]);
  const [applicationForms, setApplicationForms] = useState([]);
  const [quotations, setQuotations] = useState([]);
  const [contracts, setContracts] = useState([]);
  const [proposals, setProposals] = useState([]);
  const [loading, setLoading] = useState(false);

  // Application Form Modal state
  const [showApplicationForm, setShowApplicationForm] = useState(false);
  const [selectedApplicationForm, setSelectedApplicationForm] = useState(null);
  const [createFormModal, setCreateFormModal] = useState(false);
  const [linkCopied, setLinkCopied] = useState(false);
  const [showFormLinkModal, setShowFormLinkModal] = useState(false);
  const [createdFormLink, setCreatedFormLink] = useState('');
  const [sendingEmail, setSendingEmail] = useState(false);

  // New client info for form creation
  const [newClientInfo, setNewClientInfo] = useState({
    name: '',
    company_name: '',
    email: '',
    phone: ''
  });

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

  // Handle URL params for tab switching and highlighting from notifications
  useEffect(() => {
    const tabParam = searchParams.get('tab');
    const highlightParam = searchParams.get('highlight');
    
    if (tabParam && ['forms', 'quotations', 'contracts'].includes(tabParam)) {
      setActiveTab(tabParam);
    }
    
    if (highlightParam) {
      setHighlightedId(highlightParam);
      // Clear the highlight after 3 seconds
      const timer = setTimeout(() => {
        setHighlightedId(null);
        // Clear URL params after highlight fades
        setSearchParams({});
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, [searchParams, setSearchParams]);

  // Handle navigation for reports and templates tabs
  useEffect(() => {
    if (activeTab === 'reports') {
      navigate('/reports');
    } else if (activeTab === 'templates') {
      navigate('/templates');
    }
  }, [activeTab, navigate]);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [formsRes, quotationsRes, contractsRes, applicationFormsRes, proposalsRes] = await Promise.all([
        axios.get(`${API}/forms`),
        axios.get(`${API}/quotations`),
        axios.get(`${API}/contracts`),
        axios.get(`${API}/application-forms`),
        axios.get(`${API}/proposals`)
      ]);
      setForms(formsRes.data);
      setQuotations(quotationsRes.data);
      setContracts(contractsRes.data);
      setApplicationForms(applicationFormsRes.data);
      setProposals(proposalsRes.data);
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

  // Handle creating quotation from submitted application form
  const handleCreateQuotationFromForm = (form) => {
    // Navigate to create proposal page
    navigate(`/create-proposal/${form.id}`);
  };

  // Handle creating a new application form for a client
  const handleCreateApplicationForm = async () => {
    if (!newClientInfo.name || !newClientInfo.company_name || !newClientInfo.email || !newClientInfo.phone) {
      alert(t('fillAllClientFields'));
      return;
    }
    try {
      const response = await axios.post(`${API}/application-forms`, {
        client_info: newClientInfo
      });
      const formLink = `${window.location.origin}/form/${response.data.access_token}`;
      setCreatedFormLink(formLink);
      setShowFormLinkModal(true);
      setCreateFormModal(false);
      setNewClientInfo({ name: '', company_name: '', email: '', phone: '' });
      loadData();
    } catch (error) {
      alert(t('errorCreatingForm') + ' ' + (error.response?.data?.detail || error.message));
    }
  };

  // Copy form link to clipboard
  const handleCopyLink = async () => {
    try {
      await navigator.clipboard.writeText(createdFormLink);
      setLinkCopied(true);
      setTimeout(() => setLinkCopied(false), 2000);
    } catch (error) {
      alert(t('errorCopyingLink'));
    }
  };

  // Send form link via email
  const handleSendEmail = async (formId) => {
    setSendingEmail(true);
    try {
      const response = await axios.post(`${API}/application-forms/${formId}/send-email`);
      alert(t('emailSentSuccess'));
    } catch (error) {
      alert(t('errorSendingEmail') + ' ' + (error.response?.data?.detail || error.message));
    } finally {
      setSendingEmail(false);
    }
  };

  // Get form link for a specific form
  const getFormLink = (form) => {
    return `${window.location.origin}/form/${form.access_token}`;
  };

  // Copy specific form link
  const copyFormLink = async (form) => {
    const link = getFormLink(form);
    try {
      await navigator.clipboard.writeText(link);
      alert(t('linkCopied'));
    } catch (error) {
      alert(t('errorCopyingLink'));
    }
  };

  // View submitted application form
  const handleViewApplicationForm = (form) => {
    setSelectedApplicationForm(form);
    setShowApplicationForm(true);
  };

  // Download contract PDF
  const handleDownloadContract = async (formId, bilingual = false) => {
    try {
      // First find the agreement for this form
      const proposalsRes = await axios.get(`${API}/proposals`);
      const proposal = proposalsRes.data.find(p => p.application_form_id === formId && p.status === 'agreement_signed');
      
      if (!proposal) {
        alert(t('noAgreementFound'));
        return;
      }
      
      // Download PDF using the agreement endpoint (bilingual or standard)
      const endpoint = bilingual 
        ? `${API}/public/contracts/${proposal.access_token}/pdf/bilingual`
        : `${API}/public/contracts/${proposal.access_token}/pdf`;
        
      const response = await axios.get(endpoint, {
        responseType: 'blob'
      });
      
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      const suffix = bilingual ? '_bilingual' : '';
      link.setAttribute('download', `contract${suffix}_${formId.substring(0, 8)}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error downloading contract:', error);
      alert(t('errorDownloadingContract'));
    }
  };

  // Download bilingual form PDF
  const handleDownloadFormBilingual = async (formId) => {
    try {
      const response = await axios.get(`${API}/forms/${formId}/bilingual_pdf`, {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `form_bilingual_${formId.substring(0, 8)}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error downloading bilingual form:', error);
      alert(t('errorDownloadingPDF') || 'Error downloading PDF');
    }
  };

  // Download bilingual proposal PDF
  const handleDownloadProposalBilingual = async (proposalId) => {
    try {
      const response = await axios.get(`${API}/proposals/${proposalId}/bilingual_pdf`, {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `proposal_bilingual_${proposalId.substring(0, 8)}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error downloading bilingual proposal:', error);
      alert(t('errorDownloadingPDF') || 'Error downloading PDF');
    }
  };

  // Get status badge color
  const getStatusBadgeColor = (status) => {
    switch (status) {
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'submitted': return 'bg-blue-100 text-blue-800';
      case 'under_review': return 'bg-purple-100 text-purple-800';
      case 'approved': return 'bg-green-100 text-green-800';
      case 'rejected': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
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

  // Status filter options for forms
  const formStatusOptions = [
    { value: 'pending', label: t('pending') },
    { value: 'submitted', label: t('submitted') },
    { value: 'under_review', label: t('under_review') || 'Under Review' },
    { value: 'approved', label: t('approved') || 'Approved' },
    { value: 'agreement_signed', label: t('agreement_signed') || 'Agreement Signed' }
  ];

  // Status filter options for proposals
  const proposalStatusOptions = [
    { value: 'pending', label: t('pending') },
    { value: 'sent', label: t('sent') || 'Sent' },
    { value: 'accepted', label: t('accepted') },
    { value: 'rejected', label: t('rejected') },
    { value: 'modification_requested', label: t('modificationRequested') || 'Modification Requested' },
    { value: 'agreement_signed', label: t('agreement_signed') || 'Agreement Signed' }
  ];

  // Render content based on active tab
  const renderContent = () => {
    switch (activeTab) {
      case 'forms':
        // Calculate quick stats for forms
        const totalForms = applicationForms.length;
        const pendingForms = applicationForms.filter(f => f.status === 'pending').length;
        const submittedForms = applicationForms.filter(f => f.status === 'submitted').length;
        const completedForms = applicationForms.filter(f => ['approved', 'agreement_signed'].includes(f.status)).length;
        
        // DataTable columns for forms - optimized for full-width display
        const formColumns = [
          { key: 'company', label: t('companyName'), width: 'min-w-[220px] w-[22%]', sortAccessor: (item) => item.client_info?.company_name || '' },
          { key: 'contact', label: t('contact'), width: 'min-w-[150px] w-[15%]', sortAccessor: (item) => item.client_info?.name || '' },
          { key: 'email', label: t('email'), width: 'min-w-[200px] w-[20%]' },
          { key: 'status', label: t('status'), width: 'min-w-[130px] w-[12%]', sortAccessor: (item) => item.status },
          { key: 'date', label: t('date'), width: 'min-w-[110px] w-[11%]', sortAccessor: (item) => new Date(item.created_at || 0).getTime() },
          { key: 'actions', label: t('actions'), width: 'min-w-[200px] w-[20%]' }
        ];

        // Searchable columns for forms
        const formSearchableColumns = [
          { accessor: (item) => item.client_info?.company_name },
          { accessor: (item) => item.client_info?.name },
          { accessor: (item) => item.client_info?.email }
        ];

        // Filter options for forms
        const formFilterOptions = [
          { key: 'status', label: t('status'), accessor: (item) => item.status, options: formStatusOptions }
        ];
        
        return (
          <div className="space-y-6">
            {/* Quick Stats Header - Order: Total, Completed, Submitted, Pending (right to left in RTL) */}
            <div className={`grid grid-cols-2 md:grid-cols-4 gap-4 ${isRTL ? 'text-right' : 'text-left'}`}>
              {/* Total Forms */}
              <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-4 hover:shadow-md transition-shadow">
                <div className={`flex items-center gap-3 ${isRTL ? 'flex-row-reverse' : ''}`}>
                  <div className="p-2 bg-slate-100 rounded-lg">
                    <FileText className="w-5 h-5 text-slate-600" />
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-slate-900">{totalForms}</p>
                    <p className="text-xs font-medium text-slate-500 uppercase tracking-wider">{t('totalForms')}</p>
                  </div>
                </div>
              </div>
              {/* Completed */}
              <div className="bg-white rounded-xl border border-emerald-200 shadow-sm p-4 hover:shadow-md transition-shadow">
                <div className={`flex items-center gap-3 ${isRTL ? 'flex-row-reverse' : ''}`}>
                  <div className="p-2 bg-emerald-50 rounded-lg">
                    <CheckCircle className="w-5 h-5 text-emerald-600" />
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-emerald-700">{completedForms}</p>
                    <p className="text-xs font-medium text-slate-500 uppercase tracking-wider">{t('completed')}</p>
                  </div>
                </div>
              </div>
              {/* Submitted */}
              <div className="bg-white rounded-xl border border-blue-200 shadow-sm p-4 hover:shadow-md transition-shadow">
                <div className={`flex items-center gap-3 ${isRTL ? 'flex-row-reverse' : ''}`}>
                  <div className="p-2 bg-blue-50 rounded-lg">
                    <Eye className="w-5 h-5 text-blue-600" />
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-blue-700">{submittedForms}</p>
                    <p className="text-xs font-medium text-slate-500 uppercase tracking-wider">{t('submitted')}</p>
                  </div>
                </div>
              </div>
              {/* Pending */}
              <div className="bg-white rounded-xl border border-amber-200 shadow-sm p-4 hover:shadow-md transition-shadow">
                <div className={`flex items-center gap-3 ${isRTL ? 'flex-row-reverse' : ''}`}>
                  <div className="p-2 bg-amber-50 rounded-lg">
                    <Clock className="w-5 h-5 text-amber-600" />
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-amber-700">{pendingForms}</p>
                    <p className="text-xs font-medium text-slate-500 uppercase tracking-wider">{t('pending')}</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Certification Application Forms Data Table */}
            <DataTable
              data={applicationForms}
              columns={formColumns}
              searchableColumns={formSearchableColumns}
              filterOptions={formFilterOptions}
              isRTL={isRTL}
              defaultSort={{ key: 'date', direction: 'desc' }}
              title={t('certificationApplicationForms')}
              description={t('manageClientApplications')}
              headerActions={
                <Button 
                  onClick={() => setCreateFormModal(true)} 
                  data-testid="create-form-button"
                  className="bg-bayan-navy hover:bg-bayan-navy-light shadow-sm h-9"
                >
                  <Plus className="w-4 h-4 me-2" />
                  {t('createNewApplicationForm')}
                </Button>
              }
              emptyState={
                <div className="text-center py-16 px-4">
                  <div className="w-20 h-20 mx-auto mb-4 bg-slate-100 rounded-full flex items-center justify-center">
                    <FileText className="w-10 h-10 text-slate-400" />
                  </div>
                  <h3 className="text-lg font-semibold text-slate-700 mb-2">{t('noApplicationFormsYet')}</h3>
                  <p className="text-sm text-slate-500 mb-6 max-w-sm mx-auto">{t('createFirstApplicationForm')}</p>
                  <Button 
                    onClick={() => setCreateFormModal(true)} 
                    className="bg-bayan-navy hover:bg-bayan-navy-light"
                  >
                    <Plus className="w-4 h-4 me-2" />
                    {t('createNewApplicationForm')}
                  </Button>
                </div>
              }
              renderRow={(form, index, rtl) => (
                <div 
                  key={form.id} 
                  className={`group flex flex-col lg:flex-row lg:items-center p-4 lg:px-5 lg:py-4 hover:bg-slate-50/80 transition-all duration-500 ${
                    highlightedId === form.id ? 'bg-yellow-100 ring-2 ring-yellow-400' : ''
                  }`}
                  data-testid={`application-form-${form.id}`}
                >
                  {/* Company */}
                  <div className="lg:min-w-[220px] lg:w-[22%] min-w-0 text-start">
                    <div className="flex items-center gap-2">
                      <Building2 className="w-4 h-4 text-slate-400 flex-shrink-0" />
                      <span className="font-semibold text-slate-900 truncate" title={form.client_info?.company_name}>
                        {form.client_info?.company_name || t('unknownCompany')}
                      </span>
                    </div>
                    {/* Standards badges on mobile */}
                    {form.company_data?.certificationSchemes?.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-1 lg:hidden">
                        {form.company_data.certificationSchemes.slice(0, 2).map((cert) => (
                          <span key={cert} className="px-1.5 py-0.5 bg-slate-100 text-slate-600 text-xs rounded">
                            {cert}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                  
                  {/* Contact */}
                  <div className="lg:min-w-[150px] lg:w-[15%] min-w-0 mt-2 lg:mt-0 text-start">
                    <div className="flex items-center gap-2">
                      <User className="w-4 h-4 text-slate-400 flex-shrink-0 hidden lg:block" />
                      <span className="text-sm text-slate-700 truncate" title={form.client_info?.name}>{form.client_info?.name || '-'}</span>
                    </div>
                  </div>
                  
                  {/* Email */}
                  <div className="lg:min-w-[200px] lg:w-[20%] min-w-0 hidden lg:block text-start">
                    <span className="text-sm text-slate-500 truncate block" title={form.client_info?.email}>{form.client_info?.email || '-'}</span>
                  </div>
                  
                  {/* Status */}
                  <div className="lg:min-w-[130px] lg:w-[12%] mt-2 lg:mt-0 text-start">
                    <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium border whitespace-nowrap ${
                      form.status === 'pending' ? 'bg-amber-50 text-amber-700 border-amber-200' :
                      form.status === 'submitted' ? 'bg-blue-50 text-blue-700 border-blue-200' :
                      form.status === 'under_review' ? 'bg-purple-50 text-purple-700 border-purple-200' :
                      form.status === 'approved' || form.status === 'agreement_signed' ? 'bg-emerald-50 text-emerald-700 border-emerald-200' :
                      'bg-slate-50 text-slate-700 border-slate-200'
                    }`}>
                      {t(form.status)}
                    </span>
                  </div>
                  
                  {/* Date */}
                  <div className="lg:min-w-[110px] lg:w-[11%] hidden lg:block text-start">
                    <div className="flex items-center gap-1 text-sm text-slate-500 whitespace-nowrap">
                      <Calendar className="w-3.5 h-3.5 flex-shrink-0" />
                      {formatDate(form.created_at)}
                    </div>
                  </div>
                  
                  {/* Actions - Professional layout with proper spacing */}
                  <div className="lg:min-w-[200px] lg:w-[20%] flex items-center gap-2 mt-3 lg:mt-0 justify-end" dir="ltr">
                    {form.status === 'pending' && (
                      <div className="flex items-center gap-2">
                        <Button 
                          variant="outline" 
                          size="sm"
                          onClick={() => copyFormLink(form)}
                          data-testid={`copy-link-${form.id}`}
                          className="h-9 w-9 p-0 text-slate-600 hover:text-bayan-navy hover:border-bayan-navy"
                          title={t('copyLink')}
                        >
                          <Copy className="w-4 h-4" />
                        </Button>
                        <Button 
                          variant="outline" 
                          size="sm"
                          onClick={() => handleSendEmail(form.id)}
                          disabled={sendingEmail}
                          data-testid={`send-email-${form.id}`}
                          className="h-9 w-9 p-0 text-slate-600 hover:text-bayan-navy hover:border-bayan-navy"
                          title={t('sendEmail')}
                        >
                          <Mail className="w-4 h-4" />
                        </Button>
                      </div>
                    )}
                    {(form.status === 'submitted' || form.status === 'under_review' || form.status === 'approved' || form.status === 'agreement_signed') && form.status !== 'pending' && (
                      <div className="flex items-center gap-2">
                        <Button 
                          variant="outline" 
                          size="sm"
                          onClick={() => handleViewApplicationForm(form)}
                          data-testid={`view-form-${form.id}`}
                          className="h-9 w-9 p-0"
                          title={t('view')}
                        >
                          <Eye className="w-4 h-4" />
                        </Button>
                        <Button 
                          size="sm"
                          onClick={() => handleDownloadFormBilingual(form.id)}
                          data-testid={`download-form-${form.id}`}
                          className="h-9 px-3 bg-bayan-navy hover:bg-bayan-navy-light"
                          title={t('downloadFormPDF') || 'Download Form PDF'}
                        >
                          <Download className="w-4 h-4" />
                          <span className="ms-1">{t('download')}</span>
                        </Button>
                        {form.status === 'submitted' && (
                          <Button 
                            size="sm"
                            onClick={() => handleCreateQuotationFromForm(form)}
                            data-testid={`create-quote-${form.id}`}
                            className="h-9 px-3 bg-emerald-600 hover:bg-emerald-700"
                          >
                            <DollarSign className="w-4 h-4" />
                            <span className="ms-1">{t('quote')}</span>
                          </Button>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              )}
            />
          </div>
        );

      case 'quotations':
        // Calculate stats for quotations
        const totalProposals = proposals.length;
        const pendingProposals = proposals.filter(p => p.status === 'pending' || p.status === 'sent').length;
        const acceptedProposals = proposals.filter(p => ['accepted', 'agreement_signed'].includes(p.status)).length;
        const totalQuotedValue = proposals.reduce((sum, p) => sum + (p.total_amount || 0), 0);
        
        // DataTable columns for proposals - optimized for full-width display
        const proposalColumns = [
          { key: 'organization', label: t('organization'), width: 'min-w-[220px] w-[22%]', sortAccessor: (item) => item.organization_name || '' },
          { key: 'contact', label: t('contact'), width: 'min-w-[150px] w-[14%]', sortAccessor: (item) => item.contact_person || '' },
          { key: 'standards', label: t('standards'), width: 'min-w-[100px] w-[10%]' },
          { key: 'status', label: t('status'), width: 'min-w-[140px] w-[14%]', sortAccessor: (item) => item.status },
          { key: 'amount', label: t('amount'), width: 'min-w-[120px] w-[12%]', sortAccessor: (item) => item.total_amount || 0 },
          { key: 'date', label: t('date'), width: 'min-w-[110px] w-[10%]', sortAccessor: (item) => new Date(item.issued_date || 0).getTime() },
          { key: 'actions', label: t('actions'), width: 'min-w-[180px] w-[18%]' }
        ];

        // Searchable columns for proposals
        const proposalSearchableColumns = [
          { accessor: (item) => item.organization_name },
          { accessor: (item) => item.contact_person },
          { accessor: (item) => item.contact_email }
        ];

        // Filter options for proposals
        const proposalFilterOptions = [
          { key: 'status', label: t('status'), accessor: (item) => item.status, options: proposalStatusOptions }
        ];
        
        return (
          <div className="space-y-6">
            {/* Quick Stats Header - Order: Total, Accepted, Under Review, Total Quoted (right to left in RTL) */}
            <div className={`grid grid-cols-2 md:grid-cols-4 gap-4 ${isRTL ? 'text-right' : 'text-left'}`}>
              {/* Total Proposals */}
              <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-4 hover:shadow-md transition-shadow">
                <div className={`flex items-center gap-3 ${isRTL ? 'flex-row-reverse' : ''}`}>
                  <div className="p-2 bg-slate-100 rounded-lg">
                    <DollarSign className="w-5 h-5 text-slate-600" />
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-slate-900">{totalProposals}</p>
                    <p className="text-xs font-medium text-slate-500 uppercase tracking-wider">{t('totalProposals')}</p>
                  </div>
                </div>
              </div>
              {/* Accepted */}
              <div className="bg-white rounded-xl border border-emerald-200 shadow-sm p-4 hover:shadow-md transition-shadow">
                <div className={`flex items-center gap-3 ${isRTL ? 'flex-row-reverse' : ''}`}>
                  <div className="p-2 bg-emerald-50 rounded-lg">
                    <CheckCircle className="w-5 h-5 text-emerald-600" />
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-emerald-700">{acceptedProposals}</p>
                    <p className="text-xs font-medium text-slate-500 uppercase tracking-wider">{t('accepted')}</p>
                  </div>
                </div>
              </div>
              {/* Under Review / Pending */}
              <div className="bg-white rounded-xl border border-amber-200 shadow-sm p-4 hover:shadow-md transition-shadow">
                <div className={`flex items-center gap-3 ${isRTL ? 'flex-row-reverse' : ''}`}>
                  <div className="p-2 bg-amber-50 rounded-lg">
                    <Clock className="w-5 h-5 text-amber-600" />
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-amber-700">{pendingProposals}</p>
                    <p className="text-xs font-medium text-slate-500 uppercase tracking-wider">{t('pendingReview')}</p>
                  </div>
                </div>
              </div>
              {/* Total Quoted Value */}
              <div className="bg-white rounded-xl border border-blue-200 shadow-sm p-4 hover:shadow-md transition-shadow">
                <div className={`flex items-center gap-3 ${isRTL ? 'flex-row-reverse' : ''}`}>
                  <div className="p-2 bg-blue-50 rounded-lg">
                    <BarChart3 className="w-5 h-5 text-blue-600" />
                  </div>
                  <div>
                    <p className="text-xl font-bold text-blue-700">
                      {formatCurrency(totalQuotedValue)}
                    </p>
                    <p className="text-xs font-medium text-slate-500 uppercase tracking-wider">{t('totalQuoted')}</p>
                  </div>
                </div>
              </div>
            </div>
            
            {/* Proposals/Quotations Data Table */}
            <DataTable
              data={proposals}
              columns={proposalColumns}
              searchableColumns={proposalSearchableColumns}
              filterOptions={proposalFilterOptions}
              isRTL={isRTL}
              defaultSort={{ key: 'date', direction: 'desc' }}
              title={t('allProposals')}
              description={t('trackProposalStatus')}
              emptyState={
                <div className="text-center py-16 px-4">
                  <div className="w-20 h-20 mx-auto mb-4 bg-slate-100 rounded-full flex items-center justify-center">
                    <DollarSign className="w-10 h-10 text-slate-400" />
                  </div>
                  <h3 className="text-lg font-semibold text-slate-700 mb-2">{t('noProposalsYet')}</h3>
                  <p className="text-sm text-slate-500 mb-2 max-w-sm mx-auto">{t('createProposalFromForms')}</p>
                </div>
              }
              renderRow={(proposal, index, rtl) => (
                <div 
                  key={proposal.id} 
                  className={`group flex flex-col lg:flex-row lg:items-center p-4 lg:px-5 lg:py-4 hover:bg-slate-50/80 transition-all duration-500 ${
                    highlightedId === proposal.id ? 'bg-yellow-100 ring-2 ring-yellow-400' : ''
                  }`}
                  data-testid={`proposal-${proposal.id}`}
                >
                  {/* Organization */}
                  <div className="lg:min-w-[220px] lg:w-[22%] min-w-0 text-start">
                    <div className="flex items-center gap-2">
                      <Building2 className="w-4 h-4 text-slate-400 flex-shrink-0" />
                      <span className="font-semibold text-slate-900 truncate" title={proposal.organization_name}>
                        {proposal.organization_name}
                      </span>
                    </div>
                  </div>
                  
                  {/* Contact */}
                  <div className="lg:min-w-[150px] lg:w-[14%] min-w-0 mt-2 lg:mt-0 text-start">
                    <div className="flex items-center gap-2">
                      <User className="w-4 h-4 text-slate-400 flex-shrink-0 hidden lg:block" />
                      <span className="text-sm text-slate-700 truncate" title={proposal.contact_person}>{proposal.contact_person || '-'}</span>
                    </div>
                    <span className="text-xs text-slate-500 truncate block lg:hidden">{proposal.contact_email}</span>
                  </div>
                  
                  {/* Standards */}
                  <div className="lg:min-w-[100px] lg:w-[10%] min-w-0 mt-2 lg:mt-0 text-start">
                    <div className="flex flex-wrap gap-1">
                      {proposal.standards?.slice(0, 2).map((std) => (
                        <span key={std} className="px-1.5 py-0.5 bg-bayan-navy/10 text-bayan-navy text-xs font-medium rounded">
                          {std}
                        </span>
                      ))}
                      {proposal.standards?.length > 2 && (
                        <span className="text-xs text-slate-400">+{proposal.standards.length - 2}</span>
                      )}
                    </div>
                  </div>
                  
                  {/* Status */}
                  <div className="lg:min-w-[140px] lg:w-[14%] mt-2 lg:mt-0 text-start">
                    <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium border whitespace-nowrap ${
                      proposal.status === 'accepted' || proposal.status === 'agreement_signed' ? 'bg-emerald-50 text-emerald-700 border-emerald-200' :
                      proposal.status === 'rejected' ? 'bg-red-50 text-red-700 border-red-200' :
                      proposal.status === 'sent' ? 'bg-blue-50 text-blue-700 border-blue-200' :
                      proposal.status === 'modification_requested' ? 'bg-orange-50 text-orange-700 border-orange-200' :
                      'bg-amber-50 text-amber-700 border-amber-200'
                    }`}>
                      {t(proposal.status)}
                    </span>
                  </div>
                  
                  {/* Amount */}
                  <div className="lg:min-w-[120px] lg:w-[12%] min-w-0 mt-2 lg:mt-0 text-start">
                    <span className="font-bold text-slate-900 whitespace-nowrap">
                      {formatCurrency(proposal.total_amount)}
                    </span>
                  </div>
                  
                  {/* Date */}
                  <div className="lg:min-w-[110px] lg:w-[10%] hidden lg:block text-start">
                    <div className="flex items-center gap-1 text-sm text-slate-500 whitespace-nowrap">
                      <Calendar className="w-3.5 h-3.5 flex-shrink-0" />
                      {formatDate(proposal.issued_date)}
                    </div>
                  </div>
                  
                  {/* Actions - Professional layout with proper spacing */}
                  <div className="lg:min-w-[180px] lg:w-[18%] flex items-center gap-2 mt-3 lg:mt-0 justify-end" dir="ltr">
                    {proposal.access_token && (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => {
                          const url = `${window.location.origin}/proposal/${proposal.access_token}`;
                          window.open(url, '_blank');
                        }}
                        className="h-9 w-9 p-0"
                        title={t('viewProposal')}
                      >
                        <Eye className="w-4 h-4" />
                      </Button>
                    )}
                    
                    {proposal.status === 'agreement_signed' && (
                      <Button
                        size="sm"
                        onClick={async () => {
                          try {
                            const response = await axios.get(`${API}/public/contracts/${proposal.access_token}/pdf`, {
                              responseType: 'blob'
                            });
                            const url = window.URL.createObjectURL(new Blob([response.data]));
                            const link = document.createElement('a');
                            link.href = url;
                            link.setAttribute('download', `contract_${proposal.id.substring(0, 8)}.pdf`);
                            document.body.appendChild(link);
                            link.click();
                            link.remove();
                          } catch (error) {
                            console.error('Error downloading contract:', error);
                          }
                        }}
                        className="h-9 px-3 bg-emerald-600 hover:bg-emerald-700"
                      >
                        <Download className="w-4 h-4" />
                        <span className="ms-1">{t('pdf')}</span>
                      </Button>
                    )}
                  </div>
                </div>
              )}
            />
          </div>
        );

      case 'contracts':
        // Filter proposals that have been signed (converted to contracts)
        const signedContracts = proposals.filter(p => p.status === 'agreement_signed');
        
        // Calculate statistics
        const totalContractsValue = signedContracts.reduce((sum, c) => sum + (c.total_amount || 0), 0);
        const mostRecentContract = signedContracts.length > 0 
          ? signedContracts.sort((a, b) => new Date(b.client_response_date) - new Date(a.client_response_date))[0]
          : null;
        
        // DataTable columns for contracts - optimized for full-width display
        const contractColumns = [
          { key: 'organization', label: t('organization'), width: 'min-w-[220px] w-[22%]', sortAccessor: (item) => item.organization_name || '' },
          { key: 'contact', label: t('contact'), width: 'min-w-[150px] w-[14%]', sortAccessor: (item) => item.contact_person || '' },
          { key: 'standards', label: t('standards'), width: 'min-w-[130px] w-[13%]' },
          { key: 'amount', label: t('contractValue'), width: 'min-w-[140px] w-[15%]', sortAccessor: (item) => item.total_amount || 0 },
          { key: 'date', label: t('signedDate'), width: 'min-w-[120px] w-[12%]', sortAccessor: (item) => new Date(item.client_response_date || 0).getTime() },
          { key: 'actions', label: t('actions'), width: 'min-w-[220px] w-[24%]' }
        ];

        // Searchable columns for contracts
        const contractSearchableColumns = [
          { accessor: (item) => item.organization_name },
          { accessor: (item) => item.contact_person },
          { accessor: (item) => item.contact_email }
        ];
        
        return (
          <div className="space-y-6">
            {/* Contract Statistics Summary Cards */}
            <div className={`grid grid-cols-1 md:grid-cols-3 gap-4 ${isRTL ? 'text-right' : 'text-left'}`}>
              {/* Total Contracts */}
              <div className="bg-white rounded-xl border border-emerald-200 shadow-sm p-6 hover:shadow-md transition-shadow">
                <div className={`flex items-center justify-between ${isRTL ? 'flex-row-reverse' : ''}`}>
                  <div>
                    <p className="text-xs font-medium text-emerald-600 uppercase tracking-wider mb-1">{t('totalContracts')}</p>
                    <p className="text-4xl font-bold text-slate-900">{signedContracts.length}</p>
                    <p className="text-sm text-slate-500 mt-1">{t('signedAgreements')}</p>
                  </div>
                  <div className="p-4 bg-emerald-50 rounded-xl">
                    <FileCheck className="w-8 h-8 text-emerald-600" />
                  </div>
                </div>
              </div>
              
              {/* Total Revenue */}
              <div className="bg-white rounded-xl border border-blue-200 shadow-sm p-6 hover:shadow-md transition-shadow">
                <div className={`flex items-center justify-between ${isRTL ? 'flex-row-reverse' : ''}`}>
                  <div>
                    <p className="text-xs font-medium text-blue-600 uppercase tracking-wider mb-1">{t('totalRevenue')}</p>
                    <p className="text-3xl font-bold text-slate-900">
                      {formatCurrency(totalContractsValue)}
                    </p>
                    <p className="text-sm text-slate-500 mt-1">{t('contractValue')}</p>
                  </div>
                  <div className="p-4 bg-blue-50 rounded-xl">
                    <DollarSign className="w-8 h-8 text-blue-600" />
                  </div>
                </div>
              </div>
              
              {/* Most Recent Contract */}
              <div className="bg-white rounded-xl border border-purple-200 shadow-sm p-6 hover:shadow-md transition-shadow">
                <div className={`flex items-center justify-between ${isRTL ? 'flex-row-reverse' : ''}`}>
                  <div className="min-w-0 flex-1">
                    <p className="text-xs font-medium text-purple-600 uppercase tracking-wider mb-1">{t('mostRecentContract')}</p>
                    {mostRecentContract ? (
                      <>
                        <p className="text-lg font-bold text-slate-900 truncate">
                          {mostRecentContract.organization_name}
                        </p>
                        <p className="text-sm text-slate-500">
                          {formatDate(mostRecentContract.client_response_date)}
                        </p>
                      </>
                    ) : (
                      <p className="text-lg font-bold text-slate-400">-</p>
                    )}
                  </div>
                  <div className="p-4 bg-purple-50 rounded-xl ms-4">
                    <Clock className="w-8 h-8 text-purple-600" />
                  </div>
                </div>
              </div>
            </div>
            
            {/* Contracts Data Table */}
            <DataTable
              data={signedContracts}
              columns={contractColumns}
              searchableColumns={contractSearchableColumns}
              filterOptions={[]}
              isRTL={isRTL}
              defaultSort={{ key: 'date', direction: 'desc' }}
              title={t('allContracts')}
              description={t('contractsAutoGenerated')}
              showFilters={false}
              emptyState={
                <div className="text-center py-16 px-4">
                  <div className="w-20 h-20 mx-auto mb-4 bg-slate-100 rounded-full flex items-center justify-center">
                    <FileCheck className="w-10 h-10 text-slate-400" />
                  </div>
                  <h3 className="text-lg font-semibold text-slate-700 mb-2">{t('noContractsYet')}</h3>
                  <p className="text-sm text-slate-500 max-w-sm mx-auto">{t('contractsAutoGenerated')}</p>
                </div>
              }
              renderRow={(contract, index, rtl) => (
                <div 
                  key={contract.id} 
                  className={`group flex flex-col lg:flex-row lg:items-center p-4 lg:px-5 lg:py-4 hover:bg-slate-50/80 transition-all duration-500 ${
                    highlightedId === contract.id ? 'bg-yellow-100 ring-2 ring-yellow-400' : ''
                  }`}
                  data-testid={`contract-${contract.id}`}
                >
                  {/* Organization */}
                  <div className="lg:min-w-[220px] lg:w-[22%] min-w-0 text-start">
                    <div className="flex items-center gap-2">
                      <Building2 className="w-4 h-4 text-emerald-500 flex-shrink-0" />
                      <span className="font-semibold text-slate-900 truncate" title={contract.organization_name}>
                        {contract.organization_name}
                      </span>
                    </div>
                  </div>
                  
                  {/* Contact */}
                  <div className="lg:min-w-[150px] lg:w-[14%] min-w-0 mt-2 lg:mt-0 text-start">
                    <div className="flex items-center gap-2">
                      <User className="w-4 h-4 text-slate-400 flex-shrink-0 hidden lg:block" />
                      <span className="text-sm text-slate-700 truncate" title={contract.contact_person}>{contract.contact_person || '-'}</span>
                    </div>
                    <span className="text-xs text-slate-500 truncate block lg:hidden">{contract.contact_email}</span>
                  </div>
                  
                  {/* Standards */}
                  <div className="lg:min-w-[130px] lg:w-[13%] min-w-0 mt-2 lg:mt-0 text-start">
                    <div className="flex flex-wrap gap-1">
                      {contract.standards?.slice(0, 2).map((std) => (
                        <span key={std} className="px-1.5 py-0.5 bg-emerald-50 text-emerald-700 text-xs font-medium rounded border border-emerald-100">
                          {std}
                        </span>
                      ))}
                      {contract.standards?.length > 2 && (
                        <span className="text-xs text-slate-400">+{contract.standards.length - 2}</span>
                      )}
                    </div>
                  </div>
                  
                  {/* Amount */}
                  <div className="lg:min-w-[140px] lg:w-[15%] min-w-0 mt-2 lg:mt-0 text-start">
                    <span className="font-bold text-emerald-600 text-lg whitespace-nowrap">
                      {formatCurrency(contract.total_amount)}
                    </span>
                  </div>
                  
                  {/* Date */}
                  <div className="lg:min-w-[120px] lg:w-[12%] hidden lg:block text-start">
                    <div className="flex items-center gap-1 text-sm text-slate-500 whitespace-nowrap">
                      <Calendar className="w-3.5 h-3.5 flex-shrink-0" />
                      {formatDate(contract.client_response_date)}
                    </div>
                  </div>
                  
                  {/* Actions - Professional layout with proper spacing */}
                  <div className="lg:min-w-[220px] lg:w-[24%] flex items-center gap-2 mt-3 lg:mt-0 justify-end" dir="ltr">
                    {contract.access_token && (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => {
                          const url = `${window.location.origin}/proposal/${contract.access_token}`;
                          window.open(url, '_blank');
                        }}
                        className="h-9 w-9 p-0"
                        title={t('viewProposal')}
                      >
                        <Eye className="w-4 h-4" />
                      </Button>
                    )}
                    
                    {/* Bilingual PDF Download (AR/EN) */}
                    <Button
                      size="sm"
                      onClick={async () => {
                        try {
                          const response = await axios.get(`${API}/public/contracts/${contract.access_token}/pdf/bilingual`, {
                            responseType: 'blob'
                          });
                          const url = window.URL.createObjectURL(new Blob([response.data]));
                          const link = document.createElement('a');
                          link.href = url;
                          link.setAttribute('download', `contract_${contract.organization_name.replace(/\s+/g, '_')}_${contract.id.substring(0, 8)}.pdf`);
                          document.body.appendChild(link);
                          link.click();
                          link.remove();
                          window.URL.revokeObjectURL(url);
                        } catch (error) {
                          console.error('Error downloading contract:', error);
                        }
                      }}
                      className="h-9 px-3 bg-emerald-600 hover:bg-emerald-700"
                      data-testid={`download-contract-${contract.id}`}
                    >
                      <Download className="w-4 h-4" />
                      <span className="ms-1">{t('download')}</span>
                    </Button>
                  </div>
                </div>
              )}
            />
          </div>
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
        // Navigation handled by useEffect
        return null;

      case 'templates':
        // Navigation handled by useEffect
        return null;

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
          {/* User Controls - Left side in RTL, Right side in LTR */}
          <div className={`dashboard-header-controls flex gap-3 items-center ${isRTL ? 'order-first' : 'order-last'}`}>
            <NotificationBell />
            <LanguageSwitcher />
            <Button variant="outline" onClick={logout} data-testid="logout-button" className="bg-bayan-navy text-white hover:bg-bayan-navy-light border-bayan-navy font-semibold">
              <LogOut className="btn-icon w-4 h-4" />
              {t('logout')}
            </Button>
          </div>
          {/* Logo - Right side in RTL, Left side in LTR */}
          <div className={`dashboard-header-logo ${isRTL ? 'order-last' : 'order-first'}`}>
            <div className="-my-2">
              <img src="/bayan-logo.png" alt="Bayan" className="h-20 w-auto object-contain" />
            </div>
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
        
        {/* Main Content - Full width utilization */}
        <main className="flex-1 p-4 lg:p-6 min-h-screen">
          <div className="w-full">
            {/* Page Title */}
            <div className={`mb-4 ${isRTL ? 'text-right' : 'text-left'}`}>
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

      {/* Create Application Form Modal */}
      {createFormModal && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <Card className="w-full max-w-lg">
            <CardHeader className={isRTL ? 'text-right' : 'text-left'}>
              <div className={`flex justify-between items-center ${isRTL ? 'flex-row-reverse' : ''}`}>
                <CardTitle>{t('createNewApplicationForm')}</CardTitle>
                <Button variant="ghost" size="sm" onClick={() => setCreateFormModal(false)}>
                  <X className="w-4 h-4" />
                </Button>
              </div>
              <CardDescription>{t('enterClientInfoToCreateForm')}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label className={isRTL ? 'text-right block' : ''}>{t('clientName')} *</Label>
                <Input
                  value={newClientInfo.name}
                  onChange={(e) => setNewClientInfo({ ...newClientInfo, name: e.target.value })}
                  placeholder={t('enterClientName')}
                  data-testid="client-name-input"
                  className={isRTL ? 'text-right' : ''}
                  dir={isRTL ? 'rtl' : 'ltr'}
                />
              </div>
              <div className="space-y-2">
                <Label className={isRTL ? 'text-right block' : ''}>{t('companyName')} *</Label>
                <Input
                  value={newClientInfo.company_name}
                  onChange={(e) => setNewClientInfo({ ...newClientInfo, company_name: e.target.value })}
                  placeholder={t('enterCompanyName')}
                  data-testid="company-name-input"
                  className={isRTL ? 'text-right' : ''}
                  dir={isRTL ? 'rtl' : 'ltr'}
                />
              </div>
              <div className="space-y-2">
                <Label className={isRTL ? 'text-right block' : ''}>{t('email')} *</Label>
                <Input
                  type="email"
                  value={newClientInfo.email}
                  onChange={(e) => setNewClientInfo({ ...newClientInfo, email: e.target.value })}
                  placeholder={t('enterEmail')}
                  data-testid="client-email-input"
                  dir="ltr"
                />
              </div>
              <div className="space-y-2">
                <Label className={isRTL ? 'text-right block' : ''}>{t('phone')} *</Label>
                <Input
                  type="tel"
                  value={newClientInfo.phone}
                  onChange={(e) => setNewClientInfo({ ...newClientInfo, phone: e.target.value })}
                  placeholder={t('enterPhone')}
                  data-testid="client-phone-input"
                  dir="ltr"
                />
              </div>
              <div className={`flex gap-2 pt-4 ${isRTL ? 'flex-row-reverse' : ''}`}>
                <Button variant="outline" onClick={() => setCreateFormModal(false)}>
                  {t('cancel')}
                </Button>
                <Button 
                  onClick={handleCreateApplicationForm}
                  className="bg-bayan-navy hover:bg-bayan-navy-light"
                  data-testid="confirm-create-form"
                >
                  <Plus className="w-4 h-4 mr-2" />
                  {t('createForm')}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Form Link Modal (after creation) */}
      {showFormLinkModal && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <Card className="w-full max-w-lg">
            <CardHeader className={isRTL ? 'text-right' : 'text-left'}>
              <div className={`flex justify-between items-center ${isRTL ? 'flex-row-reverse' : ''}`}>
                <div className="flex items-center gap-2">
                  <CheckCircle className="w-6 h-6 text-green-500" />
                  <CardTitle>{t('formCreatedSuccess')}</CardTitle>
                </div>
                <Button variant="ghost" size="sm" onClick={() => setShowFormLinkModal(false)}>
                  <X className="w-4 h-4" />
                </Button>
              </div>
              <CardDescription>{t('shareFormLinkWithClient')}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label className={isRTL ? 'text-right block' : ''}>{t('formLink')}</Label>
                <div className="flex gap-2">
                  <Input
                    value={createdFormLink}
                    readOnly
                    className="flex-1 bg-gray-50"
                    dir="ltr"
                  />
                  <Button 
                    onClick={handleCopyLink}
                    variant={linkCopied ? "default" : "outline"}
                    className={linkCopied ? "bg-green-500 hover:bg-green-600" : ""}
                  >
                    {linkCopied ? <CheckCircle className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                  </Button>
                </div>
              </div>
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <p className="text-sm text-blue-800">
                  💡 {t('formLinkInstructions')}
                </p>
              </div>
              <div className={`flex gap-2 pt-2 ${isRTL ? 'flex-row-reverse' : ''}`}>
                <Button variant="outline" onClick={() => setShowFormLinkModal(false)}>
                  {t('close')}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* View Application Form Modal */}
      {showApplicationForm && selectedApplicationForm && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4 overflow-y-auto">
          <div className="bg-white rounded-lg w-full max-w-5xl max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white border-b p-4 flex justify-between items-center z-10">
              <h2 className="text-xl font-bold text-bayan-navy">
                {t('applicationFormDetails')} - {selectedApplicationForm.company_data?.companyName || selectedApplicationForm.client_info?.company_name || t('unknownCompany')}
              </h2>
              <Button variant="ghost" size="sm" onClick={() => setShowApplicationForm(false)}>
                <X className="w-5 h-5" />
              </Button>
            </div>
            <div className="p-6">
              <ApplicationForm 
                initialData={selectedApplicationForm.company_data}
                readOnly={true}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminDashboard;
