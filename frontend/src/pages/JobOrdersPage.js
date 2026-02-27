import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import axios from 'axios';
import { 
  FileText, Plus, Download, Eye, Trash2, Save, Send,
  CheckCircle, Clock, AlertCircle, Building, Calendar,
  Users, User, X, Check, XCircle, Copy
} from 'lucide-react';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '../components/ui/dialog';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function JobOrdersPage() {
  const { t, i18n } = useTranslation();
  const isRTL = i18n.language === 'ar';
  
  const [jobOrders, setJobOrders] = useState([]);
  const [auditPrograms, setAuditPrograms] = useState([]);
  const [auditors, setAuditors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showViewModal, setShowViewModal] = useState(false);
  const [showLinkModal, setShowLinkModal] = useState(false);
  const [selectedOrder, setSelectedOrder] = useState(null);
  const [confirmationLink, setConfirmationLink] = useState('');
  
  // Create form state
  const [createForm, setCreateForm] = useState({
    audit_program_id: '',
    auditor_id: '',
    position: 'Auditor',
    audit_type: '',
    audit_date: ''
  });
  
  useEffect(() => {
    fetchData();
  }, []);
  
  const fetchData = async () => {
    try {
      const token = localStorage.getItem('token');
      const headers = { Authorization: `Bearer ${token}` };
      
      const [ordersRes, programsRes, auditorsRes] = await Promise.all([
        axios.get(`${API_URL}/api/job-orders`, { headers }),
        axios.get(`${API_URL}/api/audit-programs`, { headers }),
        axios.get(`${API_URL}/api/auditors`, { headers })
      ]);
      
      setJobOrders(ordersRes.data);
      setAuditPrograms(programsRes.data);
      setAuditors(auditorsRes.data.filter(a => a.status === 'active'));
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const createJobOrder = async () => {
    if (!createForm.audit_program_id || !createForm.auditor_id) {
      alert(t('pleaseSelectRequired') || 'Please select audit program and auditor');
      return;
    }
    
    try {
      const token = localStorage.getItem('token');
      await axios.post(
        `${API_URL}/api/job-orders`,
        createForm,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setShowCreateModal(false);
      setCreateForm({
        audit_program_id: '',
        auditor_id: '',
        position: 'Auditor',
        audit_type: '',
        audit_date: ''
      });
      fetchData();
    } catch (error) {
      console.error('Error creating job order:', error);
      alert(error.response?.data?.detail || 'Error creating job order');
    }
  };
  
  const approveJobOrder = async (orderId) => {
    try {
      const token = localStorage.getItem('token');
      await axios.post(
        `${API_URL}/api/job-orders/${orderId}/approve`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      fetchData();
    } catch (error) {
      console.error('Error approving job order:', error);
    }
  };
  
  const sendToAuditor = async (order) => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        `${API_URL}/api/job-orders/${order.id}/send-to-auditor`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setConfirmationLink(response.data.link);
      setSelectedOrder(order);
      setShowLinkModal(true);
    } catch (error) {
      console.error('Error sending to auditor:', error);
      alert(error.response?.data?.detail || 'Error sending to auditor');
    }
  };
  
  const deleteJobOrder = async (id) => {
    if (!window.confirm(t('confirmDelete') || 'Are you sure you want to delete this job order?')) return;
    
    try {
      const token = localStorage.getItem('token');
      await axios.delete(`${API_URL}/api/job-orders/${id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      fetchData();
    } catch (error) {
      console.error('Error deleting job order:', error);
    }
  };
  
  const downloadPDF = async (order) => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(
        `${API_URL}/api/job-orders/${order.id}/pdf`,
        { 
          headers: { Authorization: `Bearer ${token}` },
          responseType: 'blob'
        }
      );
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `job_order_${order.auditor_name.replace(/\s+/g, '_')}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error('Error downloading PDF:', error);
    }
  };
  
  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    alert(t('linkCopied') || 'Link copied to clipboard!');
  };
  
  const getStatusBadge = (status, auditorConfirmed) => {
    const statusConfig = {
      'pending_approval': { color: 'bg-yellow-100 text-yellow-800', icon: Clock, label: t('pendingApproval') || 'Pending Approval' },
      'approved': { color: 'bg-blue-100 text-blue-800', icon: CheckCircle, label: t('approved') || 'Approved' },
      'pending_auditor': { color: 'bg-orange-100 text-orange-800', icon: Clock, label: t('pendingAuditor') || 'Pending Auditor' },
      'confirmed': { color: 'bg-green-100 text-green-800', icon: CheckCircle, label: t('confirmed') || 'Confirmed' },
      'rejected': { color: 'bg-red-100 text-red-800', icon: XCircle, label: t('rejected') || 'Rejected' },
      'completed': { color: 'bg-purple-100 text-purple-800', icon: CheckCircle, label: t('completed') || 'Completed' }
    };
    
    const config = statusConfig[status] || statusConfig['pending_approval'];
    const Icon = config.icon;
    
    return (
      <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${config.color}`}>
        <Icon className="w-3 h-3" />
        {config.label}
      </span>
    );
  };
  
  const getPositionLabel = (position) => {
    const labels = {
      'Auditor': t('auditor') || 'Auditor',
      'Lead Auditor': t('leadAuditor') || 'Lead Auditor',
      'Technical Expert': t('technicalExpert') || 'Technical Expert'
    };
    return labels[position] || position;
  };
  
  // Get available audit programs (approved ones)
  const availablePrograms = auditPrograms.filter(p => p.status === 'approved');
  
  const stats = {
    total: jobOrders.length,
    pending: jobOrders.filter(o => o.status === 'pending_approval' || o.status === 'pending_auditor').length,
    confirmed: jobOrders.filter(o => o.status === 'confirmed').length,
    rejected: jobOrders.filter(o => o.status === 'rejected').length
  };

  return (
    <div className={`p-6 ${isRTL ? 'rtl' : 'ltr'}`} dir={isRTL ? 'rtl' : 'ltr'}>
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{t('jobOrders') || 'Job Orders'}</h1>
          <p className="text-gray-500">BACF6-06 - {t('jobOrderDescription') || 'Auditor appointments and confirmations'}</p>
        </div>
        <Button onClick={() => setShowCreateModal(true)} className="bg-emerald-600 hover:bg-emerald-700" data-testid="create-job-order-btn">
          <Plus className="w-4 h-4 mr-2" />
          {t('createJobOrder') || 'Create Job Order'}
        </Button>
      </div>
      
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
            <div className="p-3 bg-yellow-100 rounded-lg">
              <Clock className="w-6 h-6 text-yellow-600" />
            </div>
            <div>
              <p className="text-2xl font-bold">{stats.pending}</p>
              <p className="text-sm text-gray-500">{t('pending') || 'Pending'}</p>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4 flex items-center gap-4">
            <div className="p-3 bg-green-100 rounded-lg">
              <CheckCircle className="w-6 h-6 text-green-600" />
            </div>
            <div>
              <p className="text-2xl font-bold">{stats.confirmed}</p>
              <p className="text-sm text-gray-500">{t('confirmed') || 'Confirmed'}</p>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4 flex items-center gap-4">
            <div className="p-3 bg-red-100 rounded-lg">
              <XCircle className="w-6 h-6 text-red-600" />
            </div>
            <div>
              <p className="text-2xl font-bold">{stats.rejected}</p>
              <p className="text-sm text-gray-500">{t('rejected') || 'Rejected'}</p>
            </div>
          </CardContent>
        </Card>
      </div>
      
      {/* Job Orders List */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="w-5 h-5" />
            {t('jobOrders') || 'Job Orders'}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8">Loading...</div>
          ) : jobOrders.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <FileText className="w-12 h-12 mx-auto mb-4 opacity-50" />
              <p>{t('noJobOrders') || 'No job orders yet'}</p>
              <p className="text-sm mt-2">{t('createFromAuditProgram') || 'Create a job order from an approved audit program'}</p>
            </div>
          ) : (
            <div className="overflow-x-auto" dir={isRTL ? 'rtl' : 'ltr'}>
              <table className="w-full table-fixed">
                <thead>
                  <tr className={`border-b ${isRTL ? 'text-right' : 'text-left'}`}>
                    <th className={`p-3 px-4 font-medium text-gray-600 w-[180px] ${isRTL ? 'text-right' : 'text-left'}`}>{t('auditor') || 'Auditor'}</th>
                    <th className={`p-3 px-4 font-medium text-gray-600 w-[100px] ${isRTL ? 'text-right' : 'text-left'}`}>{t('position') || 'Position'}</th>
                    <th className={`p-3 px-4 font-medium text-gray-600 w-[180px] ${isRTL ? 'text-right' : 'text-left'}`}>{t('organizationName') || 'Organization'}</th>
                    <th className={`p-3 px-4 font-medium text-gray-600 w-[100px] ${isRTL ? 'text-right' : 'text-left'}`}>{t('auditType') || 'Audit Type'}</th>
                    <th className={`p-3 px-4 font-medium text-gray-600 w-[110px] ${isRTL ? 'text-right' : 'text-left'}`}>{t('auditDate') || 'Audit Date'}</th>
                    <th className={`p-3 px-4 font-medium text-gray-600 w-[100px] ${isRTL ? 'text-right' : 'text-left'}`}>{t('status') || 'Status'}</th>
                    <th className={`p-3 px-4 font-medium text-gray-600 w-[180px] ${isRTL ? 'text-right' : 'text-left'}`}>{t('actions') || 'Actions'}</th>
                  </tr>
                </thead>
                <tbody>
                  {jobOrders.map(order => (
                    <tr key={order.id} className="border-b hover:bg-gray-50" data-testid={`job-order-row-${order.id}`}>
                      <td className="p-3 px-4">
                        <div className={`flex items-center gap-2 ${isRTL ? 'flex-row-reverse justify-end' : ''}`}>
                          <User className="w-4 h-4 text-gray-400 flex-shrink-0" />
                          <div className={isRTL ? 'text-right' : ''}>
                            <span className="font-medium">{order.auditor_name}</span>
                            {order.auditor_name_ar && (
                              <span className="text-gray-500 text-sm block">{order.auditor_name_ar}</span>
                            )}
                          </div>
                        </div>
                      </td>
                      <td className="p-3 px-4">
                        <span className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded whitespace-nowrap">
                          {getPositionLabel(order.position)}
                        </span>
                      </td>
                      <td className="p-3 px-4">
                        <div className={`flex items-center gap-2 ${isRTL ? 'flex-row-reverse justify-end' : ''}`}>
                          <Building className="w-4 h-4 text-gray-400 flex-shrink-0" />
                          <span className="truncate">{order.organization_name}</span>
                        </div>
                      </td>
                      <td className={`p-3 px-4 ${isRTL ? 'text-right' : ''}`}>{order.audit_type || '-'}</td>
                      <td className="p-3 px-4">
                        <div className={`flex items-center gap-1 ${isRTL ? 'flex-row-reverse justify-end' : ''}`}>
                          <Calendar className="w-4 h-4 text-gray-400 flex-shrink-0" />
                          <span dir="ltr">{order.audit_date || '-'}</span>
                        </div>
                      </td>
                      <td className={`p-3 px-4 ${isRTL ? 'text-right' : ''}`}>{getStatusBadge(order.status, order.auditor_confirmed)}</td>
                      <td className="p-3 px-4">
                        <div className={`flex gap-2 ${isRTL ? 'flex-row-reverse justify-end' : ''}`}>
                          <Button 
                            size="sm" 
                            variant="outline"
                            onClick={() => { setSelectedOrder(order); setShowViewModal(true); }}
                            data-testid={`view-order-${order.id}`}
                            title={t('view') || 'View'}
                          >
                            <Eye className="w-4 h-4" />
                          </Button>
                          
                          {order.status === 'pending_approval' && (
                            <Button 
                              size="sm" 
                              variant="outline"
                              onClick={() => approveJobOrder(order.id)}
                              data-testid={`approve-order-${order.id}`}
                              title={t('approve') || 'Approve'}
                              className="text-green-600 hover:text-green-700"
                            >
                              <Check className="w-4 h-4" />
                            </Button>
                          )}
                          
                          {order.manager_approved && !order.auditor_confirmed && order.status !== 'rejected' && (
                            <Button 
                              size="sm" 
                              variant="outline"
                              onClick={() => sendToAuditor(order)}
                              data-testid={`send-order-${order.id}`}
                              title={t('sendToAuditor') || 'Send to Auditor'}
                              className="text-blue-600 hover:text-blue-700"
                            >
                              <Send className="w-4 h-4" />
                            </Button>
                          )}
                          
                          <Button 
                            size="sm" 
                            className="bg-emerald-600 hover:bg-emerald-700"
                            onClick={() => downloadPDF(order)}
                            data-testid={`download-pdf-${order.id}`}
                            title={t('downloadPDF') || 'Download PDF'}
                          >
                            <Download className="w-4 h-4" />
                          </Button>
                          
                          <Button 
                            size="sm" 
                            variant="destructive"
                            onClick={() => deleteJobOrder(order.id)}
                            data-testid={`delete-order-${order.id}`}
                            title={t('delete') || 'Delete'}
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
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>{t('createJobOrder') || 'Create Job Order'}</DialogTitle>
            <DialogDescription>{t('selectAuditProgramAndAuditor') || 'Select an audit program and assign an auditor'}</DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label>{t('auditProgram') || 'Audit Program'} *</Label>
              <Select value={createForm.audit_program_id} onValueChange={(v) => setCreateForm({...createForm, audit_program_id: v})}>
                <SelectTrigger data-testid="select-audit-program">
                  <SelectValue placeholder={t('selectAuditProgram') || 'Select audit program...'} />
                </SelectTrigger>
                <SelectContent>
                  {availablePrograms.map(program => (
                    <SelectItem key={program.id} value={program.id}>
                      {program.organization_name} - {(program.standards || []).join(', ')}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {availablePrograms.length === 0 && (
                <p className="text-sm text-gray-500 mt-2">{t('noApprovedPrograms') || 'No approved audit programs available'}</p>
              )}
            </div>
            
            <div>
              <Label>{t('auditor') || 'Auditor'} *</Label>
              <Select value={createForm.auditor_id} onValueChange={(v) => setCreateForm({...createForm, auditor_id: v})}>
                <SelectTrigger data-testid="select-auditor">
                  <SelectValue placeholder={t('selectAuditor') || 'Select auditor...'} />
                </SelectTrigger>
                <SelectContent>
                  {auditors.map(auditor => (
                    <SelectItem key={auditor.id} value={auditor.id}>
                      {auditor.name} {auditor.name_ar ? `(${auditor.name_ar})` : ''} - {auditor.certification_level}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            
            <div>
              <Label>{t('position') || 'Position'}</Label>
              <Select value={createForm.position} onValueChange={(v) => setCreateForm({...createForm, position: v})}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Auditor">{t('auditor') || 'Auditor'}</SelectItem>
                  <SelectItem value="Lead Auditor">{t('leadAuditor') || 'Lead Auditor'}</SelectItem>
                  <SelectItem value="Technical Expert">{t('technicalExpert') || 'Technical Expert'}</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div>
              <Label>{t('auditType') || 'Audit Type'}</Label>
              <Select value={createForm.audit_type} onValueChange={(v) => setCreateForm({...createForm, audit_type: v})}>
                <SelectTrigger>
                  <SelectValue placeholder={t('selectAuditType') || 'Select audit type...'} />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Stage 1">Stage 1</SelectItem>
                  <SelectItem value="Stage 2">Stage 2</SelectItem>
                  <SelectItem value="Surveillance 1">Surveillance 1</SelectItem>
                  <SelectItem value="Surveillance 2">Surveillance 2</SelectItem>
                  <SelectItem value="Recertification">Recertification</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div>
              <Label>{t('auditDate') || 'Audit Date'}</Label>
              <Input
                type="date"
                value={createForm.audit_date}
                onChange={(e) => setCreateForm({...createForm, audit_date: e.target.value})}
              />
            </div>
            
            <div className="flex gap-2 justify-end">
              <Button variant="outline" onClick={() => setShowCreateModal(false)}>{t('cancel') || 'Cancel'}</Button>
              <Button onClick={createJobOrder} data-testid="create-order-submit">{t('create') || 'Create'}</Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
      
      {/* View Modal */}
      <Dialog open={showViewModal} onOpenChange={setShowViewModal}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>{t('jobOrderDetails') || 'Job Order Details'}</DialogTitle>
            <DialogDescription>BACF6-06</DialogDescription>
          </DialogHeader>
          {selectedOrder && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 bg-gray-50 rounded-lg">
                  <h3 className="font-semibold mb-2 flex items-center gap-2">
                    <User className="w-4 h-4" />
                    {t('auditorInfo') || 'Auditor Information'}
                  </h3>
                  <p><strong>{t('name') || 'Name'}:</strong> {selectedOrder.auditor_name}</p>
                  {selectedOrder.auditor_name_ar && <p><strong>{t('nameAr') || 'Name (AR)'}:</strong> {selectedOrder.auditor_name_ar}</p>}
                  <p><strong>{t('position') || 'Position'}:</strong> {getPositionLabel(selectedOrder.position)}</p>
                  <p><strong>{t('email') || 'Email'}:</strong> {selectedOrder.auditor_email}</p>
                </div>
                
                <div className="p-4 bg-gray-50 rounded-lg">
                  <h3 className="font-semibold mb-2 flex items-center gap-2">
                    <Building className="w-4 h-4" />
                    {t('clientInfo') || 'Client Information'}
                  </h3>
                  <p><strong>{t('organization') || 'Organization'}:</strong> {selectedOrder.organization_name}</p>
                  <p><strong>{t('standards') || 'Standards'}:</strong> {(selectedOrder.standards || []).join(', ')}</p>
                  <p><strong>{t('auditType') || 'Audit Type'}:</strong> {selectedOrder.audit_type || '-'}</p>
                  <p><strong>{t('auditDate') || 'Audit Date'}:</strong> {selectedOrder.audit_date || '-'}</p>
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 bg-blue-50 rounded-lg">
                  <h3 className="font-semibold mb-2">{t('managerApproval') || 'Manager Approval'}</h3>
                  <p><strong>{t('status') || 'Status'}:</strong> {selectedOrder.manager_approved ? '✓ Approved' : '⏳ Pending'}</p>
                  <p><strong>{t('manager') || 'Manager'}:</strong> {selectedOrder.certification_manager || '-'}</p>
                  <p><strong>{t('date') || 'Date'}:</strong> {selectedOrder.manager_approval_date || '-'}</p>
                </div>
                
                <div className={`p-4 rounded-lg ${selectedOrder.auditor_confirmed ? 'bg-green-50' : selectedOrder.status === 'rejected' ? 'bg-red-50' : 'bg-yellow-50'}`}>
                  <h3 className="font-semibold mb-2">{t('auditorConfirmation') || 'Auditor Confirmation'}</h3>
                  <p><strong>{t('status') || 'Status'}:</strong> {selectedOrder.auditor_confirmed ? '✓ Confirmed' : selectedOrder.status === 'rejected' ? '✗ Rejected' : '⏳ Pending'}</p>
                  <p><strong>{t('date') || 'Date'}:</strong> {selectedOrder.auditor_confirmation_date || '-'}</p>
                  {selectedOrder.unable_reason && (
                    <p><strong>{t('reason') || 'Reason'}:</strong> {selectedOrder.unable_reason}</p>
                  )}
                </div>
              </div>
              
              <div className="flex gap-2 justify-end">
                <Button variant="outline" onClick={() => setShowViewModal(false)}>{t('close') || 'Close'}</Button>
                <Button onClick={() => downloadPDF(selectedOrder)} className="bg-emerald-600 hover:bg-emerald-700">
                  <Download className="w-4 h-4 mr-2" />
                  {t('downloadPDF') || 'Download PDF'}
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
            <DialogTitle>{t('auditorConfirmationLink') || 'Auditor Confirmation Link'}</DialogTitle>
            <DialogDescription>{t('sendLinkToAuditor') || 'Send this link to the auditor to confirm the job order'}</DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            {selectedOrder && (
              <div className="p-4 bg-gray-50 rounded-lg">
                <p><strong>{t('auditor') || 'Auditor'}:</strong> {selectedOrder.auditor_name}</p>
                <p><strong>{t('email') || 'Email'}:</strong> {selectedOrder.auditor_email}</p>
                <p><strong>{t('organization') || 'Organization'}:</strong> {selectedOrder.organization_name}</p>
              </div>
            )}
            
            <div>
              <Label>{t('confirmationLink') || 'Confirmation Link'}</Label>
              <div className="flex gap-2">
                <Input value={confirmationLink} readOnly className="font-mono text-sm" />
                <Button variant="outline" onClick={() => copyToClipboard(confirmationLink)}>
                  <Copy className="w-4 h-4" />
                </Button>
              </div>
            </div>
            
            <p className="text-sm text-gray-500">
              {t('sendLinkInstructions') || 'Copy this link and send it to the auditor via email. They can use it to confirm or decline the job order.'}
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
