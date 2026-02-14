import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { 
  Users, ArrowLeft, Plus, X, Phone, Mail, Calendar, 
  MessageSquare, CheckCircle, Clock, Trash2, Loader2,
  AlertCircle
} from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL + '/api';

const formatDate = (dateString) => {
  if (!dateString) return '-';
  return new Date(dateString).toLocaleDateString('en-GB', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  });
};

const ContactHistoryPage = () => {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const isRTL = i18n.language?.startsWith('ar');
  
  const [loading, setLoading] = useState(true);
  const [contacts, setContacts] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [filterCustomerId, setFilterCustomerId] = useState('all');
  
  const [formData, setFormData] = useState({
    customer_id: '',
    contact_type: 'call',
    subject: '',
    notes: '',
    contact_date: new Date().toISOString().split('T')[0],
    follow_up_date: ''
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const headers = { Authorization: `Bearer ${token}` };
      
      const [contactsRes, formsRes, proposalsRes] = await Promise.all([
        axios.get(`${API}/contacts`, { headers }),
        axios.get(`${API}/forms`, { headers }),
        axios.get(`${API}/proposals`, { headers })
      ]);
      
      setContacts(contactsRes.data);
      
      // Build customer list from forms and proposals
      const customerList = [];
      formsRes.data.forEach(form => {
        if (form.client_info?.company_name) {
          customerList.push({
            id: form.id,
            name: form.client_info.company_name,
            type: 'form'
          });
        }
      });
      proposalsRes.data.forEach(proposal => {
        if (proposal.organization_name) {
          customerList.push({
            id: proposal.id,
            name: proposal.organization_name,
            type: 'proposal'
          });
        }
      });
      setCustomers(customerList);
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateContact = async () => {
    try {
      const token = localStorage.getItem('token');
      const headers = { Authorization: `Bearer ${token}` };
      
      await axios.post(`${API}/contacts`, formData, { headers });
      setShowCreateModal(false);
      setFormData({
        customer_id: '',
        contact_type: 'call',
        subject: '',
        notes: '',
        contact_date: new Date().toISOString().split('T')[0],
        follow_up_date: ''
      });
      loadData();
    } catch (error) {
      console.error('Error creating contact:', error);
      alert(t('errorCreatingContact') || 'Error creating contact record');
    }
  };

  const handleDeleteContact = async (contactId) => {
    if (!window.confirm(t('confirmDeleteContact') || 'Are you sure you want to delete this contact record?')) return;
    
    try {
      const token = localStorage.getItem('token');
      const headers = { Authorization: `Bearer ${token}` };
      
      await axios.delete(`${API}/contacts/${contactId}`, { headers });
      loadData();
    } catch (error) {
      console.error('Error deleting contact:', error);
    }
  };

  const handleMarkFollowUpComplete = async (contactId) => {
    try {
      const token = localStorage.getItem('token');
      const headers = { Authorization: `Bearer ${token}` };
      
      await axios.put(`${API}/contacts/${contactId}/follow-up`, {}, { headers });
      loadData();
    } catch (error) {
      console.error('Error marking follow-up complete:', error);
    }
  };

  const filteredContacts = filterCustomerId === 'all' 
    ? contacts 
    : contacts.filter(c => c.customer_id === filterCustomerId);

  const getContactTypeIcon = (type) => {
    switch (type) {
      case 'call': return <Phone className="w-4 h-4" />;
      case 'email': return <Mail className="w-4 h-4" />;
      case 'meeting': return <Users className="w-4 h-4" />;
      default: return <MessageSquare className="w-4 h-4" />;
    }
  };

  const getContactTypeColor = (type) => {
    switch (type) {
      case 'call': return 'bg-blue-100 text-blue-700';
      case 'email': return 'bg-purple-100 text-purple-700';
      case 'meeting': return 'bg-emerald-100 text-emerald-700';
      default: return 'bg-slate-100 text-slate-700';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-bayan-navy" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50" dir={isRTL ? 'rtl' : 'ltr'}>
      {/* Header */}
      <div className="bg-white border-b px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className={`flex items-center gap-4 ${isRTL ? 'flex-row-reverse' : ''}`}>
            <Button 
              variant="ghost" 
              onClick={() => navigate('/dashboard')}
              className={isRTL ? 'flex-row-reverse' : ''}
              data-testid="back-to-dashboard-btn"
            >
              <ArrowLeft className={`w-4 h-4 ${isRTL ? 'ml-2 rotate-180' : 'mr-2'}`} />
              {t('backToDashboard')}
            </Button>
            <h1 className="text-2xl font-bold text-bayan-navy flex items-center gap-2">
              <Users className="w-6 h-6" />
              {t('contactHistory')}
            </h1>
          </div>
          <div className="flex items-center gap-3">
            {/* Customer Filter */}
            <select
              value={filterCustomerId}
              onChange={(e) => setFilterCustomerId(e.target.value)}
              className="h-10 px-3 rounded-md border border-input bg-background text-sm"
              data-testid="customer-filter"
            >
              <option value="all">{t('allCustomers') || 'All Customers'}</option>
              {customers.map((customer) => (
                <option key={customer.id} value={customer.id}>
                  {customer.name}
                </option>
              ))}
            </select>
            
            <Button 
              onClick={() => setShowCreateModal(true)}
              className="bg-bayan-navy hover:bg-bayan-navy-light"
              data-testid="add-contact-btn"
            >
              <Plus className="w-4 h-4 me-2" />
              {t('addContact')}
            </Button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {filteredContacts.length === 0 ? (
          <Card className="text-center py-12">
            <CardContent>
              <Users className="w-16 h-16 mx-auto text-slate-300 mb-4" />
              <h3 className="text-lg font-semibold text-slate-700 mb-2">{t('noContactRecords')}</h3>
              <p className="text-slate-500">{t('addFirstContact')}</p>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-4">
            {filteredContacts.map((contact) => (
              <Card 
                key={contact.id} 
                className="hover:shadow-md transition-shadow"
                data-testid={`contact-card-${contact.id}`}
              >
                <CardContent className="p-5">
                  <div className={`flex items-start justify-between ${isRTL ? 'flex-row-reverse' : ''}`}>
                    <div className={`flex-1 ${isRTL ? 'text-right' : 'text-left'}`}>
                      <div className={`flex items-center gap-3 mb-2 ${isRTL ? 'flex-row-reverse justify-end' : ''}`}>
                        <span className={`px-3 py-1 rounded-full text-sm font-medium flex items-center gap-1 ${getContactTypeColor(contact.contact_type)}`}>
                          {getContactTypeIcon(contact.contact_type)}
                          {t(contact.contact_type)}
                        </span>
                        <h3 className="font-semibold text-slate-900">{contact.customer_name}</h3>
                      </div>
                      
                      <h4 className="font-medium text-slate-800 mb-2">{contact.subject}</h4>
                      <p className="text-slate-600 text-sm mb-3">{contact.notes}</p>
                      
                      <div className={`flex flex-wrap gap-4 text-sm text-slate-500 ${isRTL ? 'flex-row-reverse justify-end' : ''}`}>
                        <span className={`flex items-center gap-1 ${isRTL ? 'flex-row-reverse' : ''}`}>
                          <Calendar className="w-4 h-4" />
                          {formatDate(contact.contact_date)}
                        </span>
                        
                        {contact.follow_up_date && (
                          <span className={`flex items-center gap-1 ${isRTL ? 'flex-row-reverse' : ''} ${contact.follow_up_completed ? 'text-emerald-600' : 'text-amber-600'}`}>
                            <Clock className="w-4 h-4" />
                            {t('followUpDate')}: {formatDate(contact.follow_up_date)}
                            {contact.follow_up_completed && <CheckCircle className="w-4 h-4" />}
                          </span>
                        )}
                      </div>
                    </div>
                    
                    <div className={`flex items-center gap-2 ${isRTL ? 'flex-row-reverse' : ''}`}>
                      {contact.follow_up_date && !contact.follow_up_completed && (
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleMarkFollowUpComplete(contact.id)}
                          className="text-emerald-600 border-emerald-300 hover:bg-emerald-50"
                          data-testid={`mark-complete-${contact.id}`}
                        >
                          <CheckCircle className="w-4 h-4 me-1" />
                          {t('markFollowUpComplete')}
                        </Button>
                      )}
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDeleteContact(contact.id)}
                        className="text-red-500 hover:text-red-700 hover:bg-red-50"
                        data-testid={`delete-contact-${contact.id}`}
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>

      {/* Create Contact Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <Card className="w-full max-w-lg max-h-[90vh] overflow-y-auto">
            <CardHeader className={isRTL ? 'text-right' : 'text-left'}>
              <div className={`flex justify-between items-center ${isRTL ? 'flex-row-reverse' : ''}`}>
                <CardTitle>{t('addContact')}</CardTitle>
                <Button variant="ghost" size="sm" onClick={() => setShowCreateModal(false)}>
                  <X className="w-4 h-4" />
                </Button>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Customer Selection */}
              <div className="space-y-2">
                <Label className={isRTL ? 'text-right block' : ''}>{t('selectCustomer') || 'Customer'} *</Label>
                <select
                  value={formData.customer_id}
                  onChange={(e) => setFormData({ ...formData, customer_id: e.target.value })}
                  className="w-full h-10 px-3 rounded-md border border-input bg-background"
                  data-testid="customer-select"
                >
                  <option value="">{t('selectCustomer') || 'Select Customer'}</option>
                  {customers.map((customer) => (
                    <option key={customer.id} value={customer.id}>
                      {customer.name}
                    </option>
                  ))}
                </select>
              </div>

              {/* Contact Type */}
              <div className="space-y-2">
                <Label className={isRTL ? 'text-right block' : ''}>{t('contactType')} *</Label>
                <select
                  value={formData.contact_type}
                  onChange={(e) => setFormData({ ...formData, contact_type: e.target.value })}
                  className="w-full h-10 px-3 rounded-md border border-input bg-background"
                >
                  <option value="call">{t('call')}</option>
                  <option value="email">{t('email')}</option>
                  <option value="meeting">{t('meeting')}</option>
                  <option value="other">{t('other')}</option>
                </select>
              </div>

              {/* Subject */}
              <div className="space-y-2">
                <Label className={isRTL ? 'text-right block' : ''}>{t('subject')} *</Label>
                <Input
                  value={formData.subject}
                  onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
                  placeholder={t('enterSubject') || 'Enter subject'}
                  data-testid="contact-subject-input"
                />
              </div>

              {/* Notes */}
              <div className="space-y-2">
                <Label className={isRTL ? 'text-right block' : ''}>{t('notes')}</Label>
                <Textarea
                  value={formData.notes}
                  onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                  placeholder={t('enterNotes') || 'Enter notes'}
                  rows={4}
                  data-testid="contact-notes-input"
                />
              </div>

              {/* Date Fields */}
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label className={isRTL ? 'text-right block' : ''}>{t('contactDate')} *</Label>
                  <Input
                    type="date"
                    value={formData.contact_date}
                    onChange={(e) => setFormData({ ...formData, contact_date: e.target.value })}
                    data-testid="contact-date-input"
                  />
                </div>
                <div className="space-y-2">
                  <Label className={isRTL ? 'text-right block' : ''}>{t('followUpDate')}</Label>
                  <Input
                    type="date"
                    value={formData.follow_up_date}
                    onChange={(e) => setFormData({ ...formData, follow_up_date: e.target.value })}
                    data-testid="follow-up-date-input"
                  />
                </div>
              </div>

              <div className={`flex gap-2 pt-4 ${isRTL ? 'flex-row-reverse' : ''}`}>
                <Button variant="outline" onClick={() => setShowCreateModal(false)}>
                  {t('cancel')}
                </Button>
                <Button 
                  onClick={handleCreateContact}
                  className="bg-bayan-navy hover:bg-bayan-navy-light"
                  disabled={!formData.customer_id || !formData.subject || !formData.contact_date}
                  data-testid="confirm-create-contact-btn"
                >
                  <Plus className="w-4 h-4 me-2" />
                  {t('addContact')}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
};

export default ContactHistoryPage;
