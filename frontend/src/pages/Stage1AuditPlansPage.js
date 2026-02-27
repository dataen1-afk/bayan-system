import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import axios from 'axios';
import { 
  FileText, Plus, Download, Eye, Trash2, Save, Send,
  CheckCircle, Clock, AlertCircle, Building, Calendar,
  Users, User, X, Check, Copy, UserPlus
} from 'lucide-react';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '../components/ui/dialog';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function Stage1AuditPlansPage({ embedded = false }) {
  const { t, i18n } = useTranslation();
  const isRTL = i18n.language === 'ar';
  
  const [plans, setPlans] = useState([]);
  const [jobOrders, setJobOrders] = useState([]);
  const [auditors, setAuditors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showLinkModal, setShowLinkModal] = useState(false);
  const [selectedPlan, setSelectedPlan] = useState(null);
  const [selectedJobOrderId, setSelectedJobOrderId] = useState('');
  const [clientLink, setClientLink] = useState('');
  
  // Edit form state
  const [editForm, setEditForm] = useState({
    contact_person: '',
    contact_phone: '',
    contact_designation: '',
    contact_email: '',
    audit_language: 'English',
    audit_date_from: '',
    audit_date_to: '',
    team_members: [],
    schedule_entries: [],
    notes: ''
  });
  
  useEffect(() => {
    fetchData();
  }, []);
  
  const fetchData = async () => {
    try {
      const token = localStorage.getItem('token');
      const headers = { Authorization: `Bearer ${token}` };
      
      const [plansRes, ordersRes, auditorsRes] = await Promise.all([
        axios.get(`${API_URL}/api/stage1-audit-plans`, { headers }),
        axios.get(`${API_URL}/api/job-orders`, { headers }),
        axios.get(`${API_URL}/api/auditors`, { headers })
      ]);
      
      setPlans(plansRes.data);
      setJobOrders(ordersRes.data.filter(o => o.status === 'confirmed'));
      setAuditors(auditorsRes.data.filter(a => a.status === 'active'));
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const createPlan = async () => {
    if (!selectedJobOrderId) return;
    
    try {
      const token = localStorage.getItem('token');
      await axios.post(
        `${API_URL}/api/stage1-audit-plans`,
        { job_order_id: selectedJobOrderId },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setShowCreateModal(false);
      setSelectedJobOrderId('');
      fetchData();
    } catch (error) {
      console.error('Error creating plan:', error);
      alert(error.response?.data?.detail || 'Error creating plan');
    }
  };
  
  const updatePlan = async () => {
    if (!selectedPlan) return;
    
    try {
      const token = localStorage.getItem('token');
      await axios.put(
        `${API_URL}/api/stage1-audit-plans/${selectedPlan.id}`,
        editForm,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setShowEditModal(false);
      fetchData();
    } catch (error) {
      console.error('Error updating plan:', error);
    }
  };
  
  const deletePlan = async (id) => {
    if (!window.confirm(t('confirmDelete') || 'Are you sure you want to delete?')) return;
    
    try {
      const token = localStorage.getItem('token');
      await axios.delete(`${API_URL}/api/stage1-audit-plans/${id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      fetchData();
    } catch (error) {
      console.error('Error deleting plan:', error);
    }
  };
  
  const managerApprove = async (planId) => {
    try {
      const token = localStorage.getItem('token');
      await axios.post(
        `${API_URL}/api/stage1-audit-plans/${planId}/manager-approve`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      fetchData();
    } catch (error) {
      console.error('Error approving plan:', error);
    }
  };
  
  const sendToClient = async (plan) => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        `${API_URL}/api/stage1-audit-plans/${plan.id}/send-to-client`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setClientLink(response.data.link);
      setSelectedPlan(plan);
      setShowLinkModal(true);
      fetchData();
    } catch (error) {
      console.error('Error sending to client:', error);
      alert(error.response?.data?.detail || 'Error sending to client');
    }
  };
  
  const downloadPDF = async (plan) => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(
        `${API_URL}/api/stage1-audit-plans/${plan.id}/pdf`,
        { 
          headers: { Authorization: `Bearer ${token}` },
          responseType: 'blob'
        }
      );
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `stage1_audit_plan_${plan.organization_name.replace(/\s+/g, '_')}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error('Error downloading PDF:', error);
    }
  };
  
  const openEditModal = (plan) => {
    setSelectedPlan(plan);
    setEditForm({
      contact_person: plan.contact_person || '',
      contact_phone: plan.contact_phone || '',
      contact_designation: plan.contact_designation || '',
      contact_email: plan.contact_email || '',
      audit_language: plan.audit_language || 'English',
      audit_date_from: plan.audit_date_from || '',
      audit_date_to: plan.audit_date_to || '',
      team_members: plan.team_members || [],
      schedule_entries: plan.schedule_entries || [],
      notes: plan.notes || ''
    });
    setShowEditModal(true);
  };
  
  const addTeamMember = () => {
    setEditForm({
      ...editForm,
      team_members: [
        ...editForm.team_members,
        { auditor_id: '', name: '', name_ar: '', role: 'Auditor' }
      ]
    });
  };
  
  const updateTeamMember = (index, field, value) => {
    const newMembers = [...editForm.team_members];
    if (field === 'auditor_id') {
      const auditor = auditors.find(a => a.id === value);
      if (auditor) {
        newMembers[index] = {
          ...newMembers[index],
          auditor_id: value,
          name: auditor.name,
          name_ar: auditor.name_ar || ''
        };
      }
    } else {
      newMembers[index] = { ...newMembers[index], [field]: value };
    }
    setEditForm({ ...editForm, team_members: newMembers });
  };
  
  const removeTeamMember = (index) => {
    const newMembers = editForm.team_members.filter((_, i) => i !== index);
    setEditForm({ ...editForm, team_members: newMembers });
  };
  
  const addScheduleEntry = () => {
    setEditForm({
      ...editForm,
      schedule_entries: [
        ...editForm.schedule_entries,
        { date_time: '', process: '', process_owner: '', clauses: '', auditor: '' }
      ]
    });
  };
  
  const updateScheduleEntry = (index, field, value) => {
    const newEntries = [...editForm.schedule_entries];
    newEntries[index] = { ...newEntries[index], [field]: value };
    setEditForm({ ...editForm, schedule_entries: newEntries });
  };
  
  const removeScheduleEntry = (index) => {
    const newEntries = editForm.schedule_entries.filter((_, i) => i !== index);
    setEditForm({ ...editForm, schedule_entries: newEntries });
  };
  
  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    alert(t('linkCopied') || 'Link copied!');
  };
  
  const getStatusBadge = (status) => {
    const statusConfig = {
      'draft': { color: 'bg-gray-100 text-gray-800', icon: Clock, label: t('draft') || 'Draft' },
      'pending_manager': { color: 'bg-yellow-100 text-yellow-800', icon: Clock, label: t('pendingManager') || 'Pending Manager' },
      'manager_approved': { color: 'bg-blue-100 text-blue-800', icon: CheckCircle, label: t('managerApproved') || 'Manager Approved' },
      'pending_client': { color: 'bg-orange-100 text-orange-800', icon: Clock, label: t('pendingClient') || 'Pending Client' },
      'client_accepted': { color: 'bg-green-100 text-green-800', icon: CheckCircle, label: t('clientAccepted') || 'Client Accepted' },
      'changes_requested': { color: 'bg-red-100 text-red-800', icon: AlertCircle, label: t('changesRequested') || 'Changes Requested' }
    };
    
    const config = statusConfig[status] || statusConfig['draft'];
    const Icon = config.icon;
    
    return (
      <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${config.color}`}>
        <Icon className="w-3 h-3" />
        {config.label}
      </span>
    );
  };
  
  // Get confirmed job orders that don't have a plan yet
  const availableJobOrders = jobOrders.filter(
    o => !plans.some(p => p.job_order_id === o.id)
  );
  
  const stats = {
    total: plans.length,
    draft: plans.filter(p => p.status === 'draft' || p.status === 'pending_manager').length,
    approved: plans.filter(p => p.status === 'manager_approved' || p.status === 'pending_client').length,
    accepted: plans.filter(p => p.status === 'client_accepted').length
  };

  return (
    <div className={`${embedded ? '' : 'p-6'} ${isRTL ? 'rtl' : 'ltr'}`} dir={isRTL ? 'rtl' : 'ltr'}>
      {/* Header - Only show when not embedded */}
      {!embedded && (
        <div className="flex justify-between items-center mb-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{t('stage1AuditPlans') || 'Stage 1 Audit Plans'}</h1>
            <p className="text-gray-500">BACF6-07 - {t('stage1Description') || 'Initial certification audit planning'}</p>
          </div>
          <Button onClick={() => setShowCreateModal(true)} className="bg-emerald-600 hover:bg-emerald-700" data-testid="create-stage1-plan-btn">
            <Plus className="w-4 h-4 mr-2" />
            {t('createPlan') || 'Create Plan'}
          </Button>
        </div>
      )}
      
      {/* Create Button when embedded */}
      {embedded && (
        <div className={`flex ${isRTL ? 'justify-start' : 'justify-end'} mb-4`}>
          <Button onClick={() => setShowCreateModal(true)} className="bg-emerald-600 hover:bg-emerald-700" data-testid="create-stage1-plan-btn">
            <Plus className="w-4 h-4 mr-2" />
            {t('createPlan') || 'Create Plan'}
          </Button>
        </div>
      )}
      
      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <Card>
          <CardContent className="p-4 flex items-center gap-4">
            <div className="p-3 bg-blue-100 rounded-lg">
              <FileText className="w-6 h-6 text-blue-600" />
            </div>
            <div>
              <p className="text-2xl font-bold">{stats.total}</p>
              <p className="text-sm text-gray-500">{t('total') || 'Total'}</p>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4 flex items-center gap-4">
            <div className="p-3 bg-gray-100 rounded-lg">
              <Clock className="w-6 h-6 text-gray-600" />
            </div>
            <div>
              <p className="text-2xl font-bold">{stats.draft}</p>
              <p className="text-sm text-gray-500">{t('draft') || 'Draft'}</p>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4 flex items-center gap-4">
            <div className="p-3 bg-blue-100 rounded-lg">
              <CheckCircle className="w-6 h-6 text-blue-600" />
            </div>
            <div>
              <p className="text-2xl font-bold">{stats.approved}</p>
              <p className="text-sm text-gray-500">{t('approved') || 'Approved'}</p>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4 flex items-center gap-4">
            <div className="p-3 bg-green-100 rounded-lg">
              <CheckCircle className="w-6 h-6 text-green-600" />
            </div>
            <div>
              <p className="text-2xl font-bold">{stats.accepted}</p>
              <p className="text-sm text-gray-500">{t('clientAccepted') || 'Client Accepted'}</p>
            </div>
          </CardContent>
        </Card>
      </div>
      
      {/* Plans List */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="w-5 h-5" />
            {t('stage1AuditPlans') || 'Stage 1 Audit Plans'}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8">Loading...</div>
          ) : plans.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <FileText className="w-12 h-12 mx-auto mb-4 opacity-50" />
              <p>{t('noStage1Plans') || 'No Stage 1 Audit Plans yet'}</p>
              <p className="text-sm mt-2">{t('createFromJobOrder') || 'Create a plan from a confirmed job order'}</p>
            </div>
          ) : (
            <div className="overflow-x-auto" dir={isRTL ? 'rtl' : 'ltr'}>
              <table className="w-full table-fixed">
                <thead>
                  <tr className={`border-b ${isRTL ? 'text-right' : 'text-left'}`}>
                    <th className={`p-3 px-4 font-medium text-gray-600 w-[200px] ${isRTL ? 'text-right' : 'text-left'}`}>{t('organization') || 'Organization'}</th>
                    <th className={`p-3 px-4 font-medium text-gray-600 w-[160px] ${isRTL ? 'text-right' : 'text-left'}`}>{t('teamLeader') || 'Team Leader'}</th>
                    <th className={`p-3 px-4 font-medium text-gray-600 w-[120px] ${isRTL ? 'text-right' : 'text-left'}`}>{t('auditDate') || 'Audit Date'}</th>
                    <th className={`p-3 px-4 font-medium text-gray-600 w-[100px] ${isRTL ? 'text-right' : 'text-left'}`}>{t('status') || 'Status'}</th>
                    <th className={`p-3 px-4 font-medium text-gray-600 w-[220px] ${isRTL ? 'text-right' : 'text-left'}`}>{t('actions') || 'Actions'}</th>
                  </tr>
                </thead>
                <tbody>
                  {plans.map(plan => (
                    <tr key={plan.id} className="border-b hover:bg-gray-50" data-testid={`stage1-plan-row-${plan.id}`}>
                      <td className="p-3 px-4">
                        <div className={`flex items-center gap-2 ${isRTL ? 'flex-row-reverse justify-end' : ''}`}>
                          <Building className="w-4 h-4 text-gray-400 flex-shrink-0" />
                          <span className="font-medium truncate">{plan.organization_name}</span>
                        </div>
                      </td>
                      <td className="p-3 px-4">
                        <div className={`flex items-center gap-2 ${isRTL ? 'flex-row-reverse justify-end' : ''}`}>
                          <User className="w-4 h-4 text-gray-400 flex-shrink-0" />
                          <span className="truncate">{plan.team_leader?.name || '-'}</span>
                        </div>
                      </td>
                      <td className="p-3 px-4">
                        <div className={`flex items-center gap-1 ${isRTL ? 'flex-row-reverse justify-end' : ''}`}>
                          <Calendar className="w-4 h-4 text-gray-400 flex-shrink-0" />
                          <span dir="ltr">{plan.audit_date_from || '-'}</span>
                        </div>
                      </td>
                      <td className={`p-3 px-4 ${isRTL ? 'text-right' : ''}`}>{getStatusBadge(plan.status)}</td>
                      <td className="p-3 px-4">
                        <div className={`flex gap-2 ${isRTL ? 'flex-row-reverse justify-end' : ''}`}>
                          <Button 
                            size="sm" 
                            variant="outline"
                            onClick={() => openEditModal(plan)}
                            data-testid={`edit-plan-${plan.id}`}
                          >
                            <Eye className="w-4 h-4" />
                          </Button>
                          
                          {!plan.manager_approved && (
                            <Button 
                              size="sm" 
                              variant="outline"
                              onClick={() => managerApprove(plan.id)}
                              className="text-green-600 hover:text-green-700"
                              data-testid={`approve-plan-${plan.id}`}
                            >
                              <Check className="w-4 h-4" />
                            </Button>
                          )}
                          
                          {plan.manager_approved && !plan.client_accepted && plan.status !== 'changes_requested' && (
                            <Button 
                              size="sm" 
                              variant="outline"
                              onClick={() => sendToClient(plan)}
                              className="text-blue-600 hover:text-blue-700"
                              data-testid={`send-plan-${plan.id}`}
                            >
                              <Send className="w-4 h-4" />
                            </Button>
                          )}
                          
                          <Button 
                            size="sm" 
                            className="bg-emerald-600 hover:bg-emerald-700"
                            onClick={() => downloadPDF(plan)}
                            data-testid={`download-pdf-${plan.id}`}
                          >
                            <Download className="w-4 h-4" />
                          </Button>
                          
                          <Button 
                            size="sm" 
                            variant="destructive"
                            onClick={() => deletePlan(plan.id)}
                            data-testid={`delete-plan-${plan.id}`}
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
      
      {/* Create Modal */}
      <Dialog open={showCreateModal} onOpenChange={setShowCreateModal}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>{t('createStage1Plan') || 'Create Stage 1 Audit Plan'}</DialogTitle>
            <DialogDescription>{t('selectJobOrder') || 'Select a confirmed job order'}</DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label>{t('jobOrder') || 'Job Order'}</Label>
              <Select value={selectedJobOrderId} onValueChange={setSelectedJobOrderId}>
                <SelectTrigger data-testid="select-job-order">
                  <SelectValue placeholder={t('selectJobOrder') || 'Select job order...'} />
                </SelectTrigger>
                <SelectContent>
                  {availableJobOrders.map(order => (
                    <SelectItem key={order.id} value={order.id}>
                      {order.organization_name} - {order.auditor_name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {availableJobOrders.length === 0 && (
                <p className="text-sm text-gray-500 mt-2">{t('noConfirmedOrders') || 'No confirmed job orders available'}</p>
              )}
            </div>
            <div className="flex gap-2 justify-end">
              <Button variant="outline" onClick={() => setShowCreateModal(false)}>{t('cancel') || 'Cancel'}</Button>
              <Button onClick={createPlan} disabled={!selectedJobOrderId} data-testid="create-plan-submit">{t('create') || 'Create'}</Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
      
      {/* Edit Modal */}
      <Dialog open={showEditModal} onOpenChange={setShowEditModal}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>{t('stage1PlanDetails') || 'Stage 1 Audit Plan Details'}</DialogTitle>
            <DialogDescription>{selectedPlan?.organization_name}</DialogDescription>
          </DialogHeader>
          {selectedPlan && (
            <div className="space-y-6">
              {/* Client Contact */}
              <div>
                <h3 className="font-semibold mb-3">{t('clientContact') || 'Client Contact'}</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label>{t('contactPerson') || 'Contact Person'}</Label>
                    <Input
                      value={editForm.contact_person}
                      onChange={(e) => setEditForm({...editForm, contact_person: e.target.value})}
                    />
                  </div>
                  <div>
                    <Label>{t('phone') || 'Phone'}</Label>
                    <Input
                      value={editForm.contact_phone}
                      onChange={(e) => setEditForm({...editForm, contact_phone: e.target.value})}
                    />
                  </div>
                  <div>
                    <Label>{t('designation') || 'Designation'}</Label>
                    <Input
                      value={editForm.contact_designation}
                      onChange={(e) => setEditForm({...editForm, contact_designation: e.target.value})}
                    />
                  </div>
                  <div>
                    <Label>{t('email') || 'Email'}</Label>
                    <Input
                      type="email"
                      value={editForm.contact_email}
                      onChange={(e) => setEditForm({...editForm, contact_email: e.target.value})}
                    />
                  </div>
                </div>
              </div>
              
              {/* Audit Details */}
              <div>
                <h3 className="font-semibold mb-3">{t('auditDetails') || 'Audit Details'}</h3>
                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <Label>{t('language') || 'Language'}</Label>
                    <Select value={editForm.audit_language} onValueChange={(v) => setEditForm({...editForm, audit_language: v})}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="English">English</SelectItem>
                        <SelectItem value="Arabic">Arabic</SelectItem>
                        <SelectItem value="Both">Both</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label>{t('dateFrom') || 'Date From'}</Label>
                    <Input
                      type="date"
                      value={editForm.audit_date_from}
                      onChange={(e) => setEditForm({...editForm, audit_date_from: e.target.value})}
                    />
                  </div>
                  <div>
                    <Label>{t('dateTo') || 'Date To'}</Label>
                    <Input
                      type="date"
                      value={editForm.audit_date_to}
                      onChange={(e) => setEditForm({...editForm, audit_date_to: e.target.value})}
                    />
                  </div>
                </div>
              </div>
              
              {/* Team Leader (read-only) */}
              <div className="p-4 bg-blue-50 rounded-lg">
                <h3 className="font-semibold mb-2">{t('teamLeader') || 'Team Leader'}</h3>
                <p>{selectedPlan.team_leader?.name} ({selectedPlan.team_leader?.role})</p>
              </div>
              
              {/* Team Members */}
              <div>
                <div className="flex justify-between items-center mb-3">
                  <h3 className="font-semibold">{t('teamMembers') || 'Team Members'}</h3>
                  <Button size="sm" variant="outline" onClick={addTeamMember}>
                    <UserPlus className="w-4 h-4 mr-1" />
                    {t('addMember') || 'Add Member'}
                  </Button>
                </div>
                <div className="space-y-2">
                  {editForm.team_members.map((member, idx) => (
                    <div key={idx} className="flex gap-2 items-center p-2 bg-gray-50 rounded">
                      <Select value={member.auditor_id} onValueChange={(v) => updateTeamMember(idx, 'auditor_id', v)}>
                        <SelectTrigger className="w-48">
                          <SelectValue placeholder="Select auditor" />
                        </SelectTrigger>
                        <SelectContent>
                          {auditors.map(a => (
                            <SelectItem key={a.id} value={a.id}>{a.name}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                      <Select value={member.role} onValueChange={(v) => updateTeamMember(idx, 'role', v)}>
                        <SelectTrigger className="w-40">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="Auditor">Auditor</SelectItem>
                          <SelectItem value="Technical Expert">Technical Expert</SelectItem>
                          <SelectItem value="Evaluator">Evaluator</SelectItem>
                        </SelectContent>
                      </Select>
                      <Button size="sm" variant="ghost" onClick={() => removeTeamMember(idx)} className="text-red-500">
                        <X className="w-4 h-4" />
                      </Button>
                    </div>
                  ))}
                </div>
              </div>
              
              {/* Schedule */}
              <div>
                <div className="flex justify-between items-center mb-3">
                  <h3 className="font-semibold">{t('auditSchedule') || 'Audit Schedule'}</h3>
                  <Button size="sm" variant="outline" onClick={addScheduleEntry}>
                    <Plus className="w-4 h-4 mr-1" />
                    {t('addEntry') || 'Add Entry'}
                  </Button>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm border">
                    <thead>
                      <tr className="bg-gray-100">
                        <th className="p-2 border text-left">{t('dateTime') || 'Date/Time'}</th>
                        <th className="p-2 border text-left">{t('process') || 'Process'}</th>
                        <th className="p-2 border text-left">{t('processOwner') || 'Process Owner'}</th>
                        <th className="p-2 border text-left">{t('clauses') || 'Clauses'}</th>
                        <th className="p-2 border text-left">{t('auditor') || 'Auditor'}</th>
                        <th className="p-2 border"></th>
                      </tr>
                    </thead>
                    <tbody>
                      {editForm.schedule_entries.map((entry, idx) => (
                        <tr key={idx} className="hover:bg-gray-50">
                          <td className="p-1 border">
                            <Input
                              value={entry.date_time}
                              onChange={(e) => updateScheduleEntry(idx, 'date_time', e.target.value)}
                              className="h-8"
                              placeholder="09:00 - 10:00"
                            />
                          </td>
                          <td className="p-1 border">
                            <Input
                              value={entry.process}
                              onChange={(e) => updateScheduleEntry(idx, 'process', e.target.value)}
                              className="h-8"
                              placeholder="Process name"
                            />
                          </td>
                          <td className="p-1 border">
                            <Input
                              value={entry.process_owner}
                              onChange={(e) => updateScheduleEntry(idx, 'process_owner', e.target.value)}
                              className="h-8"
                              placeholder="Owner"
                            />
                          </td>
                          <td className="p-1 border">
                            <Input
                              value={entry.clauses}
                              onChange={(e) => updateScheduleEntry(idx, 'clauses', e.target.value)}
                              className="h-8"
                              placeholder="4.1, 5.0"
                            />
                          </td>
                          <td className="p-1 border">
                            <Input
                              value={entry.auditor}
                              onChange={(e) => updateScheduleEntry(idx, 'auditor', e.target.value)}
                              className="h-8"
                              placeholder="Auditor"
                            />
                          </td>
                          <td className="p-1 border">
                            <Button size="sm" variant="ghost" onClick={() => removeScheduleEntry(idx)} className="text-red-500 h-8 w-8 p-0">
                              <X className="w-4 h-4" />
                            </Button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
              
              {/* Notes */}
              <div>
                <Label>{t('notes') || 'Notes'}</Label>
                <Textarea
                  value={editForm.notes}
                  onChange={(e) => setEditForm({...editForm, notes: e.target.value})}
                  rows={3}
                />
              </div>
              
              {/* Change Requests (if any) */}
              {selectedPlan.client_change_requests && (
                <div className="p-4 bg-red-50 rounded-lg">
                  <h3 className="font-semibold text-red-800 mb-2">{t('clientChangeRequests') || 'Client Change Requests'}</h3>
                  <p className="text-red-700">{selectedPlan.client_change_requests}</p>
                </div>
              )}
              
              <div className="flex gap-2 justify-end">
                <Button variant="outline" onClick={() => setShowEditModal(false)}>{t('cancel') || 'Cancel'}</Button>
                <Button onClick={updatePlan} data-testid="save-plan-btn">
                  <Save className="w-4 h-4 mr-2" />
                  {t('saveChanges') || 'Save Changes'}
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
      
      {/* Send Link Modal */}
      <Dialog open={showLinkModal} onOpenChange={setShowLinkModal}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>{t('clientReviewLink') || 'Client Review Link'}</DialogTitle>
            <DialogDescription>{t('sendLinkToClient') || 'Send this link to the client'}</DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            {selectedPlan && (
              <div className="p-4 bg-gray-50 rounded-lg">
                <p><strong>{t('organization') || 'Organization'}:</strong> {selectedPlan.organization_name}</p>
                <p><strong>{t('email') || 'Email'}:</strong> {selectedPlan.contact_email || 'N/A'}</p>
              </div>
            )}
            
            <div>
              <Label>{t('reviewLink') || 'Review Link'}</Label>
              <div className="flex gap-2">
                <Input value={clientLink} readOnly className="font-mono text-sm" />
                <Button variant="outline" onClick={() => copyToClipboard(clientLink)}>
                  <Copy className="w-4 h-4" />
                </Button>
              </div>
            </div>
            
            <p className="text-sm text-gray-500">
              {t('clientLinkInstructions') || 'Copy this link and send it to the client. They can review and accept or request changes.'}
            </p>
            
            <div className="flex gap-2 justify-end">
              <Button variant="outline" onClick={() => setShowLinkModal(false)}>{t('close') || 'Close'}</Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
