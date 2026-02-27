import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import axios from 'axios';
import { 
  UserX, Plus, Eye, Edit, Trash2, Download, RefreshCw,
  AlertTriangle, CheckCircle, XCircle, Clock, FileSpreadsheet,
  RotateCcw, Ban
} from 'lucide-react';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '../components/ui/dialog';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../components/ui/select';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function SuspendedClientsPage() {
  const { t, i18n } = useTranslation();
  const isRTL = i18n.language === 'ar';
  
  const [clientsList, setClientsList] = useState([]);
  const [certifiedClients, setCertifiedClients] = useState([]);
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showViewModal, setShowViewModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showLiftModal, setShowLiftModal] = useState(false);
  const [selectedClient, setSelectedClient] = useState(null);
  const [syncing, setSyncing] = useState(false);
  const [statusFilter, setStatusFilter] = useState('all');
  
  const [formData, setFormData] = useState({
    client_id: '',
    client_name: '',
    client_name_ar: '',
    address: '',
    address_ar: '',
    registration_date: '',
    suspended_on: '',
    reason_for_suspension: '',
    reason_for_suspension_ar: '',
    future_action: 'under_review',
    remarks: '',
    linked_certified_client_id: ''
  });

  const [liftData, setLiftData] = useState({
    action: 'reinstate',
    reason: ''
  });

  const token = localStorage.getItem('token');
  const headers = { Authorization: `Bearer ${token}` };

  const futureActionOptions = [
    { value: 'reinstate', label: isRTL ? 'إعادة' : 'Reinstate' },
    { value: 'withdraw', label: isRTL ? 'سحب' : 'Withdraw' },
    { value: 'extend_suspension', label: isRTL ? 'تمديد التعليق' : 'Extend Suspension' },
    { value: 'under_review', label: isRTL ? 'قيد المراجعة' : 'Under Review' }
  ];

  useEffect(() => {
    fetchClients();
    fetchStats();
    fetchCertifiedClients();
  }, [statusFilter]);

  const fetchClients = async () => {
    try {
      const params = statusFilter !== 'all' ? `?status=${statusFilter}` : '';
      const response = await axios.get(`${API_URL}/api/suspended-clients${params}`, { headers });
      setClientsList(response.data);
    } catch (error) {
      console.error('Error fetching suspended clients:', error);
      toast.error(isRTL ? 'خطأ في جلب العملاء المعلقين' : 'Error fetching suspended clients');
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/suspended-clients/stats/overview`, { headers });
      setStats(response.data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const fetchCertifiedClients = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/certified-clients?status=active`, { headers });
      setCertifiedClients(response.data);
    } catch (error) {
      console.error('Error fetching certified clients:', error);
    }
  };

  const handleCreate = async () => {
    try {
      if (!formData.client_name) {
        toast.error(isRTL ? 'اسم العميل مطلوب' : 'Client name is required');
        return;
      }
      if (!formData.reason_for_suspension) {
        toast.error(isRTL ? 'سبب التعليق مطلوب' : 'Reason for suspension is required');
        return;
      }
      
      await axios.post(`${API_URL}/api/suspended-clients`, formData, { headers });
      toast.success(isRTL ? 'تم إضافة العميل المعلق' : 'Suspended client added');
      setShowCreateModal(false);
      resetForm();
      fetchClients();
      fetchStats();
    } catch (error) {
      console.error('Error creating suspended client:', error);
      toast.error(isRTL ? 'خطأ في إضافة العميل' : 'Error adding client');
    }
  };

  const handleUpdate = async () => {
    if (!selectedClient) return;
    
    try {
      await axios.put(`${API_URL}/api/suspended-clients/${selectedClient.id}`, selectedClient, { headers });
      toast.success(isRTL ? 'تم تحديث بيانات العميل' : 'Client updated successfully');
      setShowEditModal(false);
      fetchClients();
      fetchStats();
    } catch (error) {
      console.error('Error updating suspended client:', error);
      toast.error(isRTL ? 'خطأ في تحديث البيانات' : 'Error updating client');
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm(isRTL ? 'هل أنت متأكد من الحذف؟' : 'Are you sure you want to delete?')) return;
    
    try {
      await axios.delete(`${API_URL}/api/suspended-clients/${id}`, { headers });
      toast.success(isRTL ? 'تم حذف العميل' : 'Client deleted');
      fetchClients();
      fetchStats();
    } catch (error) {
      console.error('Error deleting suspended client:', error);
      toast.error(isRTL ? 'خطأ في حذف العميل' : 'Error deleting client');
    }
  };

  const handleLiftSuspension = async () => {
    if (!selectedClient) return;
    
    try {
      await axios.post(
        `${API_URL}/api/suspended-clients/${selectedClient.id}/lift-suspension?action=${liftData.action}&reason=${encodeURIComponent(liftData.reason)}`,
        {},
        { headers }
      );
      toast.success(isRTL ? 'تم رفع التعليق' : 'Suspension lifted successfully');
      setShowLiftModal(false);
      setLiftData({ action: 'reinstate', reason: '' });
      fetchClients();
      fetchStats();
    } catch (error) {
      console.error('Error lifting suspension:', error);
      toast.error(error.response?.data?.detail || (isRTL ? 'خطأ في رفع التعليق' : 'Error lifting suspension'));
    }
  };

  const handleSyncFromCertified = async () => {
    setSyncing(true);
    try {
      const response = await axios.post(`${API_URL}/api/suspended-clients/sync-from-certified`, {}, { headers });
      toast.success(response.data.message);
      fetchClients();
      fetchStats();
    } catch (error) {
      console.error('Error syncing:', error);
      toast.error(isRTL ? 'خطأ في المزامنة' : 'Error syncing');
    } finally {
      setSyncing(false);
    }
  };

  const handleExportExcel = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/suspended-clients/export/excel`, {
        headers,
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'suspended_clients_registry.xlsx');
      document.body.appendChild(link);
      link.click();
      link.remove();
      toast.success(isRTL ? 'تم تصدير البيانات' : 'Data exported successfully');
    } catch (error) {
      console.error('Error exporting Excel:', error);
      toast.error(isRTL ? 'خطأ في تصدير البيانات' : 'Error exporting data');
    }
  };

  const handleDownloadPDF = async (id) => {
    try {
      const response = await axios.get(`${API_URL}/api/suspended-clients/${id}/pdf`, {
        headers,
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `suspended_client_${id.substring(0, 8)}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error('Error downloading PDF:', error);
      toast.error(isRTL ? 'خطأ في تحميل PDF' : 'Error downloading PDF');
    }
  };

  const handleSelectCertifiedClient = (certId) => {
    const cert = certifiedClients.find(c => c.id === certId);
    if (cert) {
      setFormData({
        ...formData,
        client_id: cert.certificate_number || '',
        client_name: cert.client_name || '',
        client_name_ar: cert.client_name_ar || '',
        address: cert.address || '',
        registration_date: cert.issue_date || '',
        linked_certified_client_id: cert.id
      });
    }
  };

  const resetForm = () => {
    setFormData({
      client_id: '',
      client_name: '',
      client_name_ar: '',
      address: '',
      address_ar: '',
      registration_date: '',
      suspended_on: new Date().toISOString().split('T')[0],
      reason_for_suspension: '',
      reason_for_suspension_ar: '',
      future_action: 'under_review',
      remarks: '',
      linked_certified_client_id: ''
    });
  };

  const getStatusBadge = (status) => {
    const statusConfig = {
      suspended: { bg: 'bg-red-100', text: 'text-red-700', label: isRTL ? 'معلق' : 'Suspended', icon: AlertTriangle },
      reinstated: { bg: 'bg-green-100', text: 'text-green-700', label: isRTL ? 'تمت الإعادة' : 'Reinstated', icon: CheckCircle },
      withdrawn: { bg: 'bg-gray-100', text: 'text-gray-700', label: isRTL ? 'تم السحب' : 'Withdrawn', icon: XCircle }
    };
    const config = statusConfig[status] || statusConfig.suspended;
    const Icon = config.icon;
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${config.bg} ${config.text} flex items-center gap-1`}>
        <Icon className="w-3 h-3" />
        {config.label}
      </span>
    );
  };

  const getFutureActionBadge = (action) => {
    const actionConfig = {
      reinstate: { bg: 'bg-green-50', text: 'text-green-600', label: isRTL ? 'إعادة' : 'Reinstate' },
      withdraw: { bg: 'bg-red-50', text: 'text-red-600', label: isRTL ? 'سحب' : 'Withdraw' },
      extend_suspension: { bg: 'bg-orange-50', text: 'text-orange-600', label: isRTL ? 'تمديد' : 'Extend' },
      under_review: { bg: 'bg-blue-50', text: 'text-blue-600', label: isRTL ? 'قيد المراجعة' : 'Under Review' }
    };
    const config = actionConfig[action] || actionConfig.under_review;
    return (
      <span className={`px-2 py-0.5 rounded text-xs font-medium ${config.bg} ${config.text}`}>
        {config.label}
      </span>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-600"></div>
      </div>
    );
  }

  return (
    <div className={`p-6 ${isRTL ? 'rtl' : 'ltr'}`} dir={isRTL ? 'rtl' : 'ltr'}>
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            {isRTL ? 'سجل العملاء المعلقين' : 'Suspended Clients Registry'}
          </h1>
          <p className="text-sm text-gray-500">
            BAC-F6-20 - {isRTL ? 'قائمة العملاء الذين تم تعليق شهاداتهم' : 'List of clients with suspended certifications'}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button 
            variant="outline" 
            onClick={handleSyncFromCertified}
            disabled={syncing}
            className="flex items-center gap-2"
          >
            <RefreshCw className={`w-4 h-4 ${syncing ? 'animate-spin' : ''}`} />
            {isRTL ? 'مزامنة من المعتمدين' : 'Sync from Certified'}
          </Button>
          <Button 
            variant="outline" 
            onClick={handleExportExcel}
            className="flex items-center gap-2"
          >
            <FileSpreadsheet className="w-4 h-4" />
            {isRTL ? 'تصدير Excel' : 'Export Excel'}
          </Button>
          <Button onClick={() => { resetForm(); setShowCreateModal(true); }} className="flex items-center gap-2 bg-red-600 hover:bg-red-700">
            <Plus className="w-4 h-4" />
            {isRTL ? 'إضافة معلق' : 'Add Suspended'}
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-6 gap-4 mb-6">
        <Card className="border-l-4 border-l-gray-500">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">{isRTL ? 'إجمالي' : 'Total'}</p>
                <p className="text-2xl font-bold">{stats.total || 0}</p>
              </div>
              <UserX className="w-8 h-8 text-gray-300" />
            </div>
          </CardContent>
        </Card>
        <Card className="border-l-4 border-l-red-500">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">{isRTL ? 'معلق' : 'Suspended'}</p>
                <p className="text-2xl font-bold text-red-600">{stats.suspended || 0}</p>
              </div>
              <AlertTriangle className="w-8 h-8 text-red-300" />
            </div>
          </CardContent>
        </Card>
        <Card className="border-l-4 border-l-green-500">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">{isRTL ? 'تمت الإعادة' : 'Reinstated'}</p>
                <p className="text-2xl font-bold text-green-600">{stats.reinstated || 0}</p>
              </div>
              <CheckCircle className="w-8 h-8 text-green-300" />
            </div>
          </CardContent>
        </Card>
        <Card className="border-l-4 border-l-gray-400">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">{isRTL ? 'تم السحب' : 'Withdrawn'}</p>
                <p className="text-2xl font-bold text-gray-600">{stats.withdrawn || 0}</p>
              </div>
              <XCircle className="w-8 h-8 text-gray-300" />
            </div>
          </CardContent>
        </Card>
        <Card className="border-l-4 border-l-blue-500">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">{isRTL ? 'بانتظار الإعادة' : 'Pending Reinstate'}</p>
                <p className="text-2xl font-bold text-blue-600">{stats.pending_reinstatement || 0}</p>
              </div>
              <RotateCcw className="w-8 h-8 text-blue-300" />
            </div>
          </CardContent>
        </Card>
        <Card className="border-l-4 border-l-orange-500">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">{isRTL ? 'قيد المراجعة' : 'Under Review'}</p>
                <p className="text-2xl font-bold text-orange-600">{stats.under_review || 0}</p>
              </div>
              <Clock className="w-8 h-8 text-orange-300" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filter */}
      <div className="mb-4 flex items-center gap-4">
        <Label>{isRTL ? 'تصفية حسب الحالة:' : 'Filter by Status:'}</Label>
        <Select value={statusFilter} onValueChange={setStatusFilter}>
          <SelectTrigger className="w-48">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">{isRTL ? 'الكل' : 'All'}</SelectItem>
            <SelectItem value="suspended">{isRTL ? 'معلق' : 'Suspended'}</SelectItem>
            <SelectItem value="reinstated">{isRTL ? 'تمت الإعادة' : 'Reinstated'}</SelectItem>
            <SelectItem value="withdrawn">{isRTL ? 'تم السحب' : 'Withdrawn'}</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Clients Table */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-red-700">
            <UserX className="w-5 h-5" />
            {isRTL ? 'جميع العملاء المعلقين' : 'All Suspended Clients'}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto" dir={isRTL ? 'rtl' : 'ltr'}>
            <table className="w-full table-fixed" data-testid="suspended-clients-table">
              <thead>
                <tr className={`border-b bg-red-50 ${isRTL ? 'text-right' : 'text-left'}`}>
                  <th className={`p-3 px-4 font-medium w-[70px] ${isRTL ? 'text-right' : 'text-left'}`}>{isRTL ? 'الرقم' : 'Sr. No.'}</th>
                  <th className={`p-3 px-4 font-medium w-[100px] ${isRTL ? 'text-right' : 'text-left'}`}>{isRTL ? 'رقم العميل' : 'Client ID'}</th>
                  <th className={`p-3 px-4 font-medium w-[160px] ${isRTL ? 'text-right' : 'text-left'}`}>{isRTL ? 'اسم العميل' : 'Client Name'}</th>
                  <th className={`p-3 px-4 font-medium w-[110px] ${isRTL ? 'text-right' : 'text-left'}`}>{isRTL ? 'تاريخ التعليق' : 'Suspended On'}</th>
                  <th className={`p-3 px-4 font-medium w-[150px] ${isRTL ? 'text-right' : 'text-left'}`}>{isRTL ? 'السبب' : 'Reason'}</th>
                  <th className={`p-3 px-4 font-medium w-[100px] ${isRTL ? 'text-right' : 'text-left'}`}>{isRTL ? 'الإجراء' : 'Future Action'}</th>
                  <th className={`p-3 px-4 font-medium w-[90px] ${isRTL ? 'text-right' : 'text-left'}`}>{isRTL ? 'الحالة' : 'Status'}</th>
                  <th className={`p-3 px-4 font-medium w-[150px] ${isRTL ? 'text-right' : 'text-left'}`}>{isRTL ? 'الإجراءات' : 'Actions'}</th>
                </tr>
              </thead>
              <tbody>
                {clientsList.map((client) => (
                  <tr key={client.id} className="border-b hover:bg-gray-50" data-testid={`suspended-row-${client.id}`}>
                    <td className={`p-3 px-4 font-mono text-sm ${isRTL ? 'text-right' : ''}`}>{client.serial_number}</td>
                    <td className={`p-3 px-4 font-mono text-sm ${isRTL ? 'text-right' : ''}`}>{client.client_id || '-'}</td>
                    <td className="p-3 px-4">
                      <div className={`font-medium ${isRTL ? 'text-right' : ''}`}>{isRTL ? (client.client_name_ar || client.client_name) : client.client_name}</div>
                      {!isRTL && client.client_name_ar && (
                        <div className="text-sm text-gray-500" dir="rtl">{client.client_name_ar}</div>
                      )}
                    </td>
                    <td className={`p-3 px-4 text-sm ${isRTL ? 'text-right' : ''}`} dir="ltr">{client.suspended_on || '-'}</td>
                    <td className={`p-3 px-4 text-sm max-w-[150px] truncate ${isRTL ? 'text-right' : ''}`} title={client.reason_for_suspension}>
                      {client.reason_for_suspension || '-'}
                    </td>
                    <td className={`p-3 px-4 ${isRTL ? 'text-right' : ''}`}>{getFutureActionBadge(client.future_action)}</td>
                    <td className={`p-3 px-4 ${isRTL ? 'text-right' : ''}`}>{getStatusBadge(client.status)}</td>
                    <td className="p-3 px-4">
                      <div className={`flex items-center gap-1 ${isRTL ? 'flex-row-reverse justify-end' : ''}`}>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => {
                            setSelectedClient(client);
                            setShowViewModal(true);
                          }}
                          title={isRTL ? 'عرض' : 'View'}
                          data-testid={`view-btn-${client.id}`}
                        >
                          <Eye className="w-4 h-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => {
                            setSelectedClient({...client});
                            setShowEditModal(true);
                          }}
                          title={isRTL ? 'تعديل' : 'Edit'}
                          data-testid={`edit-btn-${client.id}`}
                        >
                          <Edit className="w-4 h-4" />
                        </Button>
                        {client.status === 'suspended' && (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => {
                              setSelectedClient(client);
                              setShowLiftModal(true);
                            }}
                            title={isRTL ? 'رفع التعليق' : 'Lift Suspension'}
                            className="text-green-600 hover:text-green-700"
                            data-testid={`lift-btn-${client.id}`}
                          >
                            <RotateCcw className="w-4 h-4" />
                          </Button>
                        )}
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDownloadPDF(client.id)}
                          title={isRTL ? 'تحميل PDF' : 'Download PDF'}
                          className="text-blue-600 hover:text-blue-700"
                          data-testid={`pdf-btn-${client.id}`}
                        >
                          <Download className="w-4 h-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDelete(client.id)}
                          title={isRTL ? 'حذف' : 'Delete'}
                          className="text-red-600 hover:text-red-700"
                          data-testid={`delete-btn-${client.id}`}
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))}
                {clientsList.length === 0 && (
                  <tr>
                    <td colSpan={8} className="p-8 text-center text-gray-500">
                      {isRTL ? 'لا يوجد عملاء معلقين' : 'No suspended clients found'}
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Create Modal */}
      <Dialog open={showCreateModal} onOpenChange={setShowCreateModal}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="text-red-700">
              {isRTL ? 'إضافة عميل معلق جديد' : 'Add New Suspended Client'}
            </DialogTitle>
          </DialogHeader>
          
          <div className="space-y-4">
            {/* Link to Certified Client */}
            {certifiedClients.length > 0 && (
              <div className="p-3 bg-blue-50 rounded-lg">
                <Label className="mb-2 block">{isRTL ? 'اختيار من العملاء المعتمدين' : 'Select from Certified Clients'}</Label>
                <Select onValueChange={handleSelectCertifiedClient}>
                  <SelectTrigger>
                    <SelectValue placeholder={isRTL ? 'اختر عميل...' : 'Choose a client...'} />
                  </SelectTrigger>
                  <SelectContent>
                    {certifiedClients.map(cert => (
                      <SelectItem key={cert.id} value={cert.id}>
                        {cert.client_name} - {cert.certificate_number}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            )}

            {/* Client Information */}
            <div className="p-3 bg-gray-50 rounded-lg">
              <h3 className="font-medium mb-3">{isRTL ? 'معلومات العميل' : 'Client Information'}</h3>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>{isRTL ? 'رقم العميل' : 'Client ID'}</Label>
                  <Input
                    value={formData.client_id}
                    onChange={(e) => setFormData({ ...formData, client_id: e.target.value })}
                    data-testid="input-client-id"
                  />
                </div>
                <div className="space-y-2">
                  <Label>{isRTL ? 'تاريخ التسجيل' : 'Registration Date'}</Label>
                  <Input
                    type="date"
                    value={formData.registration_date}
                    onChange={(e) => setFormData({ ...formData, registration_date: e.target.value })}
                    data-testid="input-registration-date"
                  />
                </div>
                <div className="space-y-2">
                  <Label>{isRTL ? 'اسم العميل (إنجليزي)' : 'Client Name (English)'} *</Label>
                  <Input
                    value={formData.client_name}
                    onChange={(e) => setFormData({ ...formData, client_name: e.target.value })}
                    data-testid="input-client-name"
                  />
                </div>
                <div className="space-y-2">
                  <Label>{isRTL ? 'اسم العميل (عربي)' : 'Client Name (Arabic)'}</Label>
                  <Input
                    value={formData.client_name_ar}
                    onChange={(e) => setFormData({ ...formData, client_name_ar: e.target.value })}
                    dir="rtl"
                    data-testid="input-client-name-ar"
                  />
                </div>
                <div className="space-y-2 col-span-2">
                  <Label>{isRTL ? 'العنوان' : 'Address'}</Label>
                  <Textarea
                    value={formData.address}
                    onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                    data-testid="input-address"
                  />
                </div>
              </div>
            </div>

            {/* Suspension Details */}
            <div className="p-3 bg-red-50 rounded-lg border border-red-200">
              <h3 className="font-medium mb-3 text-red-700">{isRTL ? 'تفاصيل التعليق' : 'Suspension Details'}</h3>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>{isRTL ? 'تاريخ التعليق' : 'Suspended On'} *</Label>
                  <Input
                    type="date"
                    value={formData.suspended_on}
                    onChange={(e) => setFormData({ ...formData, suspended_on: e.target.value })}
                    data-testid="input-suspended-on"
                  />
                </div>
                <div className="space-y-2">
                  <Label>{isRTL ? 'الإجراء المستقبلي' : 'Future Action'}</Label>
                  <Select
                    value={formData.future_action}
                    onValueChange={(v) => setFormData({ ...formData, future_action: v })}
                  >
                    <SelectTrigger data-testid="select-future-action">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {futureActionOptions.map(opt => (
                        <SelectItem key={opt.value} value={opt.value}>{opt.label}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2 col-span-2">
                  <Label>{isRTL ? 'سبب التعليق' : 'Reason for Suspension'} *</Label>
                  <Textarea
                    value={formData.reason_for_suspension}
                    onChange={(e) => setFormData({ ...formData, reason_for_suspension: e.target.value })}
                    placeholder={isRTL ? 'أدخل سبب التعليق...' : 'Enter reason for suspension...'}
                    data-testid="input-reason"
                  />
                </div>
                <div className="space-y-2 col-span-2">
                  <Label>{isRTL ? 'ملاحظات' : 'Remarks'}</Label>
                  <Textarea
                    value={formData.remarks}
                    onChange={(e) => setFormData({ ...formData, remarks: e.target.value })}
                    placeholder={isRTL ? 'ملاحظات إضافية...' : 'Additional remarks...'}
                    data-testid="input-remarks"
                  />
                </div>
              </div>
            </div>

            <div className="flex justify-end gap-2 mt-4">
              <Button variant="outline" onClick={() => setShowCreateModal(false)}>
                {isRTL ? 'إلغاء' : 'Cancel'}
              </Button>
              <Button onClick={handleCreate} className="bg-red-600 hover:bg-red-700" data-testid="create-submit-btn">
                {isRTL ? 'إضافة' : 'Add Suspended Client'}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* View Modal */}
      <Dialog open={showViewModal} onOpenChange={setShowViewModal}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>
              {isRTL ? 'تفاصيل العميل المعلق' : 'Suspended Client Details'}
            </DialogTitle>
          </DialogHeader>
          
          {selectedClient && (
            <div className="space-y-6">
              {/* Status Banner */}
              <div className="flex justify-between items-center p-4 bg-red-50 rounded-lg border border-red-200">
                <div>
                  <span className="text-sm text-gray-500">Sr. No. {selectedClient.serial_number}</span>
                  <p className="font-mono text-lg font-bold">{selectedClient.client_id || 'N/A'}</p>
                </div>
                {getStatusBadge(selectedClient.status)}
              </div>

              {/* Client Info */}
              <div className="grid grid-cols-2 gap-4 p-4 bg-gray-50 rounded-lg">
                <div>
                  <p className="text-sm text-gray-500">{isRTL ? 'اسم العميل' : 'Client Name'}</p>
                  <p className="font-medium">{selectedClient.client_name}</p>
                  {selectedClient.client_name_ar && (
                    <p className="text-sm text-gray-600" dir="rtl">{selectedClient.client_name_ar}</p>
                  )}
                </div>
                <div>
                  <p className="text-sm text-gray-500">{isRTL ? 'تاريخ التسجيل' : 'Registration Date'}</p>
                  <p className="font-medium">{selectedClient.registration_date || '-'}</p>
                </div>
                <div className="col-span-2">
                  <p className="text-sm text-gray-500">{isRTL ? 'العنوان' : 'Address'}</p>
                  <p className="font-medium">{selectedClient.address || '-'}</p>
                </div>
              </div>

              {/* Suspension Details */}
              <div className="p-4 bg-red-50 rounded-lg border border-red-200">
                <h3 className="font-medium mb-3 text-red-700">{isRTL ? 'تفاصيل التعليق' : 'Suspension Details'}</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-gray-500">{isRTL ? 'تاريخ التعليق' : 'Suspended On'}</p>
                    <p className="font-medium">{selectedClient.suspended_on || '-'}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">{isRTL ? 'الإجراء المستقبلي' : 'Future Action'}</p>
                    {getFutureActionBadge(selectedClient.future_action)}
                  </div>
                  <div className="col-span-2">
                    <p className="text-sm text-gray-500">{isRTL ? 'سبب التعليق' : 'Reason for Suspension'}</p>
                    <p className="font-medium">{selectedClient.reason_for_suspension || '-'}</p>
                  </div>
                  <div className="col-span-2">
                    <p className="text-sm text-gray-500">{isRTL ? 'ملاحظات' : 'Remarks'}</p>
                    <p className="font-medium">{selectedClient.remarks || '-'}</p>
                  </div>
                </div>
              </div>

              {/* Resolution Details (if lifted) */}
              {selectedClient.status !== 'suspended' && (
                <div className={`p-4 rounded-lg border ${selectedClient.status === 'reinstated' ? 'bg-green-50 border-green-200' : 'bg-gray-50 border-gray-200'}`}>
                  <h3 className={`font-medium mb-3 ${selectedClient.status === 'reinstated' ? 'text-green-700' : 'text-gray-700'}`}>
                    {isRTL ? 'تفاصيل القرار' : 'Resolution Details'}
                  </h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm text-gray-500">{isRTL ? 'تاريخ الرفع' : 'Lifted On'}</p>
                      <p className="font-medium">{selectedClient.lifted_on || '-'}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">{isRTL ? 'سبب القرار' : 'Resolution Reason'}</p>
                      <p className="font-medium">{selectedClient.lifted_reason || '-'}</p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* Edit Modal */}
      <Dialog open={showEditModal} onOpenChange={setShowEditModal}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>
              {isRTL ? 'تعديل بيانات العميل المعلق' : 'Edit Suspended Client Record'}
            </DialogTitle>
          </DialogHeader>
          
          {selectedClient && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>{isRTL ? 'رقم العميل' : 'Client ID'}</Label>
                  <Input
                    value={selectedClient.client_id}
                    onChange={(e) => setSelectedClient({ ...selectedClient, client_id: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <Label>{isRTL ? 'اسم العميل' : 'Client Name'}</Label>
                  <Input
                    value={selectedClient.client_name}
                    onChange={(e) => setSelectedClient({ ...selectedClient, client_name: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <Label>{isRTL ? 'تاريخ التعليق' : 'Suspended On'}</Label>
                  <Input
                    type="date"
                    value={selectedClient.suspended_on}
                    onChange={(e) => setSelectedClient({ ...selectedClient, suspended_on: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <Label>{isRTL ? 'الإجراء المستقبلي' : 'Future Action'}</Label>
                  <Select
                    value={selectedClient.future_action}
                    onValueChange={(v) => setSelectedClient({ ...selectedClient, future_action: v })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {futureActionOptions.map(opt => (
                        <SelectItem key={opt.value} value={opt.value}>{opt.label}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="space-y-2">
                <Label>{isRTL ? 'سبب التعليق' : 'Reason for Suspension'}</Label>
                <Textarea
                  value={selectedClient.reason_for_suspension}
                  onChange={(e) => setSelectedClient({ ...selectedClient, reason_for_suspension: e.target.value })}
                />
              </div>

              <div className="space-y-2">
                <Label>{isRTL ? 'ملاحظات' : 'Remarks'}</Label>
                <Textarea
                  value={selectedClient.remarks || ''}
                  onChange={(e) => setSelectedClient({ ...selectedClient, remarks: e.target.value })}
                />
              </div>

              <div className="flex justify-end gap-2">
                <Button variant="outline" onClick={() => setShowEditModal(false)}>
                  {isRTL ? 'إلغاء' : 'Cancel'}
                </Button>
                <Button onClick={handleUpdate}>
                  {isRTL ? 'حفظ التغييرات' : 'Save Changes'}
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* Lift Suspension Modal */}
      <Dialog open={showLiftModal} onOpenChange={setShowLiftModal}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle className="text-green-700">
              {isRTL ? 'رفع التعليق' : 'Lift Suspension'}
            </DialogTitle>
          </DialogHeader>
          
          {selectedClient && (
            <div className="space-y-4">
              <p className="text-sm text-gray-600">
                {isRTL 
                  ? `أنت على وشك رفع تعليق العميل: ${selectedClient.client_name}`
                  : `You are about to lift the suspension for: ${selectedClient.client_name}`
                }
              </p>

              <div className="space-y-2">
                <Label>{isRTL ? 'الإجراء' : 'Action'}</Label>
                <Select
                  value={liftData.action}
                  onValueChange={(v) => setLiftData({ ...liftData, action: v })}
                >
                  <SelectTrigger data-testid="select-lift-action">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="reinstate">
                      <span className="flex items-center gap-2">
                        <CheckCircle className="w-4 h-4 text-green-600" />
                        {isRTL ? 'إعادة الشهادة' : 'Reinstate Certificate'}
                      </span>
                    </SelectItem>
                    <SelectItem value="withdraw">
                      <span className="flex items-center gap-2">
                        <Ban className="w-4 h-4 text-red-600" />
                        {isRTL ? 'سحب الشهادة' : 'Withdraw Certificate'}
                      </span>
                    </SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label>{isRTL ? 'سبب القرار' : 'Reason for Decision'}</Label>
                <Textarea
                  value={liftData.reason}
                  onChange={(e) => setLiftData({ ...liftData, reason: e.target.value })}
                  placeholder={isRTL ? 'أدخل سبب القرار...' : 'Enter reason for decision...'}
                  data-testid="input-lift-reason"
                />
              </div>

              <div className="flex justify-end gap-2">
                <Button variant="outline" onClick={() => setShowLiftModal(false)}>
                  {isRTL ? 'إلغاء' : 'Cancel'}
                </Button>
                <Button 
                  onClick={handleLiftSuspension}
                  className={liftData.action === 'reinstate' ? 'bg-green-600 hover:bg-green-700' : 'bg-red-600 hover:bg-red-700'}
                  data-testid="lift-submit-btn"
                >
                  {liftData.action === 'reinstate' 
                    ? (isRTL ? 'إعادة' : 'Reinstate')
                    : (isRTL ? 'سحب' : 'Withdraw')
                  }
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
