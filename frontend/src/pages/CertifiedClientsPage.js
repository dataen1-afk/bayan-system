import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import axios from 'axios';
import { 
  Users, Plus, Eye, Edit, Trash2, Download, RefreshCw,
  Building, Calendar, FileText, AlertTriangle, CheckCircle,
  Clock, XCircle, FileSpreadsheet
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
import { Checkbox } from '../components/ui/checkbox';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function CertifiedClientsPage() {
  const { t, i18n } = useTranslation();
  const isRTL = i18n.language === 'ar';
  
  const [clientsList, setClientsList] = useState([]);
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showViewModal, setShowViewModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [selectedClient, setSelectedClient] = useState(null);
  const [syncing, setSyncing] = useState(false);
  const [statusFilter, setStatusFilter] = useState('all');
  
  const [formData, setFormData] = useState({
    client_name: '',
    client_name_ar: '',
    address: '',
    address_ar: '',
    contact_person: '',
    contact_number: '',
    scope: '',
    scope_ar: '',
    accreditation: [],
    ea_code: '',
    certificate_number: '',
    issue_date: '',
    expiry_date: '',
    surveillance_1_date: '',
    surveillance_2_date: '',
    recertification_date: ''
  });

  const token = localStorage.getItem('token');
  const headers = { Authorization: `Bearer ${token}` };

  const standardOptions = [
    'ISO 9001:2015',
    'ISO 14001:2015',
    'ISO 45001:2018',
    'ISO 22000:2018',
    'ISO 27001:2022'
  ];

  useEffect(() => {
    fetchClients();
    fetchStats();
  }, [statusFilter]);

  const fetchClients = async () => {
    try {
      const params = statusFilter !== 'all' ? `?status=${statusFilter}` : '';
      const response = await axios.get(`${API_URL}/api/certified-clients${params}`, { headers });
      setClientsList(response.data);
    } catch (error) {
      console.error('Error fetching certified clients:', error);
      toast.error(isRTL ? 'خطأ في جلب العملاء المعتمدين' : 'Error fetching certified clients');
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/certified-clients/stats/overview`, { headers });
      setStats(response.data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const handleCreate = async () => {
    try {
      if (!formData.client_name) {
        toast.error(isRTL ? 'اسم العميل مطلوب' : 'Client name is required');
        return;
      }
      
      await axios.post(`${API_URL}/api/certified-clients`, formData, { headers });
      toast.success(isRTL ? 'تم إضافة العميل المعتمد' : 'Certified client added');
      setShowCreateModal(false);
      resetForm();
      fetchClients();
      fetchStats();
    } catch (error) {
      console.error('Error creating certified client:', error);
      toast.error(isRTL ? 'خطأ في إضافة العميل' : 'Error adding client');
    }
  };

  const handleUpdate = async () => {
    if (!selectedClient) return;
    
    try {
      await axios.put(`${API_URL}/api/certified-clients/${selectedClient.id}`, selectedClient, { headers });
      toast.success(isRTL ? 'تم تحديث بيانات العميل' : 'Client updated successfully');
      setShowEditModal(false);
      fetchClients();
      fetchStats();
    } catch (error) {
      console.error('Error updating certified client:', error);
      toast.error(isRTL ? 'خطأ في تحديث البيانات' : 'Error updating client');
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm(isRTL ? 'هل أنت متأكد من الحذف؟' : 'Are you sure you want to delete?')) return;
    
    try {
      await axios.delete(`${API_URL}/api/certified-clients/${id}`, { headers });
      toast.success(isRTL ? 'تم حذف العميل' : 'Client deleted');
      fetchClients();
      fetchStats();
    } catch (error) {
      console.error('Error deleting certified client:', error);
      toast.error(isRTL ? 'خطأ في حذف العميل' : 'Error deleting client');
    }
  };

  const handleSyncFromCertificates = async () => {
    setSyncing(true);
    try {
      const response = await axios.post(`${API_URL}/api/certified-clients/sync-from-certificates`, {}, { headers });
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
      const response = await axios.get(`${API_URL}/api/certified-clients/export/excel`, {
        headers,
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'certified_clients_registry.xlsx');
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
      const response = await axios.get(`${API_URL}/api/certified-clients/${id}/pdf`, {
        headers,
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `certified_client_${id.substring(0, 8)}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error('Error downloading PDF:', error);
      toast.error(isRTL ? 'خطأ في تحميل PDF' : 'Error downloading PDF');
    }
  };

  const resetForm = () => {
    setFormData({
      client_name: '',
      client_name_ar: '',
      address: '',
      address_ar: '',
      contact_person: '',
      contact_number: '',
      scope: '',
      scope_ar: '',
      accreditation: [],
      ea_code: '',
      certificate_number: '',
      issue_date: '',
      expiry_date: '',
      surveillance_1_date: '',
      surveillance_2_date: '',
      recertification_date: ''
    });
  };

  const getStatusBadge = (status) => {
    const statusConfig = {
      active: { bg: 'bg-green-100', text: 'text-green-700', label: isRTL ? 'نشط' : 'Active', icon: CheckCircle },
      suspended: { bg: 'bg-yellow-100', text: 'text-yellow-700', label: isRTL ? 'موقوف' : 'Suspended', icon: AlertTriangle },
      withdrawn: { bg: 'bg-red-100', text: 'text-red-700', label: isRTL ? 'ملغى' : 'Withdrawn', icon: XCircle },
      expired: { bg: 'bg-gray-100', text: 'text-gray-700', label: isRTL ? 'منتهي' : 'Expired', icon: Clock }
    };
    const config = statusConfig[status] || statusConfig.active;
    const Icon = config.icon;
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${config.bg} ${config.text} flex items-center gap-1`}>
        <Icon className="w-3 h-3" />
        {config.label}
      </span>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className={`p-6 ${isRTL ? 'rtl' : 'ltr'}`} dir={isRTL ? 'rtl' : 'ltr'}>
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            {isRTL ? 'سجل العملاء المعتمدين' : 'Certified Clients Registry'}
          </h1>
          <p className="text-sm text-gray-500">
            BAC-F6-19 - {isRTL ? 'قائمة العملاء الحاصلين على الشهادات' : 'List of clients with active certifications'}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button 
            variant="outline" 
            onClick={handleSyncFromCertificates}
            disabled={syncing}
            className="flex items-center gap-2"
          >
            <RefreshCw className={`w-4 h-4 ${syncing ? 'animate-spin' : ''}`} />
            {isRTL ? 'مزامنة من الشهادات' : 'Sync from Certificates'}
          </Button>
          <Button 
            variant="outline" 
            onClick={handleExportExcel}
            className="flex items-center gap-2"
          >
            <FileSpreadsheet className="w-4 h-4" />
            {isRTL ? 'تصدير Excel' : 'Export Excel'}
          </Button>
          <Button onClick={() => setShowCreateModal(true)} className="flex items-center gap-2">
            <Plus className="w-4 h-4" />
            {isRTL ? 'إضافة عميل' : 'Add Client'}
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-6 gap-4 mb-6">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">{isRTL ? 'إجمالي العملاء' : 'Total Clients'}</p>
                <p className="text-2xl font-bold text-primary">{stats.total || 0}</p>
              </div>
              <Users className="w-8 h-8 text-gray-300" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">{isRTL ? 'نشط' : 'Active'}</p>
                <p className="text-2xl font-bold text-green-600">{stats.active || 0}</p>
              </div>
              <CheckCircle className="w-8 h-8 text-green-300" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">{isRTL ? 'ينتهي قريباً' : 'Expiring Soon'}</p>
                <p className="text-2xl font-bold text-orange-600">{stats.expiring_soon || 0}</p>
              </div>
              <AlertTriangle className="w-8 h-8 text-orange-300" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">{isRTL ? 'منتهي' : 'Expired'}</p>
                <p className="text-2xl font-bold text-gray-600">{stats.expired || 0}</p>
              </div>
              <Clock className="w-8 h-8 text-gray-300" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">{isRTL ? 'مراقبة 1 قادمة' : 'Surv. 1 Due'}</p>
                <p className="text-2xl font-bold text-blue-600">{stats.surveillance_1_upcoming || 0}</p>
              </div>
              <Calendar className="w-8 h-8 text-blue-300" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">{isRTL ? 'مراقبة 2 قادمة' : 'Surv. 2 Due'}</p>
                <p className="text-2xl font-bold text-purple-600">{stats.surveillance_2_upcoming || 0}</p>
              </div>
              <Calendar className="w-8 h-8 text-purple-300" />
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
            <SelectItem value="active">{isRTL ? 'نشط' : 'Active'}</SelectItem>
            <SelectItem value="suspended">{isRTL ? 'موقوف' : 'Suspended'}</SelectItem>
            <SelectItem value="expired">{isRTL ? 'منتهي' : 'Expired'}</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Clients Table */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Users className="w-5 h-5" />
            {isRTL ? 'جميع العملاء المعتمدين' : 'All Certified Clients'}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto" dir={isRTL ? 'rtl' : 'ltr'}>
            <table className="w-full table-fixed" data-testid="certified-clients-table">
              <thead>
                <tr className={`border-b bg-gray-50 ${isRTL ? 'text-right' : 'text-left'}`}>
                  <th className={`p-3 px-4 font-medium w-[80px] ${isRTL ? 'text-right' : 'text-left'}`}>{isRTL ? 'الرقم' : 'S.No.'}</th>
                  <th className={`p-3 px-4 font-medium w-[180px] ${isRTL ? 'text-right' : 'text-left'}`}>{isRTL ? 'اسم العميل' : 'Client Name'}</th>
                  <th className={`p-3 px-4 font-medium w-[140px] ${isRTL ? 'text-right' : 'text-left'}`}>{isRTL ? 'الاعتماد' : 'Accreditation'}</th>
                  <th className={`p-3 px-4 font-medium w-[120px] ${isRTL ? 'text-right' : 'text-left'}`}>{isRTL ? 'رقم الشهادة' : 'Cert. No.'}</th>
                  <th className={`p-3 px-4 font-medium w-[110px] ${isRTL ? 'text-right' : 'text-left'}`}>{isRTL ? 'تاريخ الإصدار' : 'Issue Date'}</th>
                  <th className={`p-3 px-4 font-medium w-[110px] ${isRTL ? 'text-right' : 'text-left'}`}>{isRTL ? 'تاريخ الانتهاء' : 'Expiry Date'}</th>
                  <th className={`p-3 px-4 font-medium w-[100px] ${isRTL ? 'text-right' : 'text-left'}`}>{isRTL ? 'الحالة' : 'Status'}</th>
                  <th className={`p-3 px-4 font-medium w-[150px] ${isRTL ? 'text-right' : 'text-left'}`}>{isRTL ? 'الإجراءات' : 'Actions'}</th>
                </tr>
              </thead>
              <tbody>
                {clientsList.map((client) => (
                  <tr key={client.id} className="border-b hover:bg-gray-50" data-testid={`client-row-${client.id}`}>
                    <td className={`p-3 px-4 font-mono text-sm ${isRTL ? 'text-right' : ''}`}>{client.serial_number}</td>
                    <td className="p-3 px-4">
                      <div className={`font-medium ${isRTL ? 'text-right' : ''}`}>{isRTL ? (client.client_name_ar || client.client_name) : client.client_name}</div>
                      {!isRTL && client.client_name_ar && (
                        <div className="text-sm text-gray-500" dir="rtl">{client.client_name_ar}</div>
                      )}
                    </td>
                    <td className="p-3 px-4">
                      <div className={`flex flex-wrap gap-1 ${isRTL ? 'flex-row-reverse justify-start' : ''}`}>
                        {(client.accreditation || []).slice(0, 2).map((std, idx) => (
                          <span key={idx} className="px-2 py-0.5 bg-blue-50 text-blue-700 rounded text-xs">
                            {std}
                          </span>
                        ))}
                        {(client.accreditation || []).length > 2 && (
                          <span className="text-xs text-gray-500">+{client.accreditation.length - 2}</span>
                        )}
                      </div>
                    </td>
                    <td className={`p-3 px-4 ${isRTL ? 'text-right' : ''}`}>
                      <span className="font-mono text-sm" dir="ltr">{client.certificate_number || '-'}</span>
                    </td>
                    <td className={`p-3 px-4 text-sm ${isRTL ? 'text-left' : ''}`} dir="ltr">{client.issue_date || '-'}</td>
                    <td className={`p-3 px-4 text-sm ${isRTL ? 'text-left' : ''}`} dir="ltr">{client.expiry_date || '-'}</td>
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
                      {isRTL ? 'لا يوجد عملاء معتمدون بعد' : 'No certified clients found'}
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
        <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>
              {isRTL ? 'إضافة عميل معتمد جديد' : 'Add New Certified Client'}
            </DialogTitle>
          </DialogHeader>
          
          <div className="space-y-4">
            {/* Client Information */}
            <div className="p-3 bg-blue-50 rounded-lg">
              <h3 className="font-medium mb-3">{isRTL ? 'معلومات العميل' : 'Client Information'}</h3>
              <div className="grid grid-cols-2 gap-4">
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
                <div className="space-y-2">
                  <Label>{isRTL ? 'مسؤول الاتصال' : 'Contact Person'}</Label>
                  <Input
                    value={formData.contact_person}
                    onChange={(e) => setFormData({ ...formData, contact_person: e.target.value })}
                    data-testid="input-contact-person"
                  />
                </div>
                <div className="space-y-2">
                  <Label>{isRTL ? 'رقم الاتصال' : 'Contact Number'}</Label>
                  <Input
                    value={formData.contact_number}
                    onChange={(e) => setFormData({ ...formData, contact_number: e.target.value })}
                    data-testid="input-contact-number"
                  />
                </div>
              </div>
            </div>

            {/* Certification Details */}
            <div className="p-3 bg-green-50 rounded-lg">
              <h3 className="font-medium mb-3">{isRTL ? 'تفاصيل الشهادة' : 'Certification Details'}</h3>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2 col-span-2">
                  <Label>{isRTL ? 'نطاق العمل' : 'Scope'}</Label>
                  <Textarea
                    value={formData.scope}
                    onChange={(e) => setFormData({ ...formData, scope: e.target.value })}
                    data-testid="input-scope"
                  />
                </div>
                <div className="space-y-2 col-span-2">
                  <Label>{isRTL ? 'المعايير' : 'Accreditation/Standards'}</Label>
                  <div className="flex flex-wrap gap-3">
                    {standardOptions.map(std => (
                      <label key={std} className="flex items-center gap-2 cursor-pointer">
                        <Checkbox
                          checked={formData.accreditation.includes(std)}
                          onCheckedChange={(checked) => {
                            if (checked) {
                              setFormData({ ...formData, accreditation: [...formData.accreditation, std] });
                            } else {
                              setFormData({ ...formData, accreditation: formData.accreditation.filter(s => s !== std) });
                            }
                          }}
                        />
                        <span className="text-sm">{std}</span>
                      </label>
                    ))}
                  </div>
                </div>
                <div className="space-y-2">
                  <Label>{isRTL ? 'رمز EA / فئة الغذاء' : 'EA Code / Food Category'}</Label>
                  <Input
                    value={formData.ea_code}
                    onChange={(e) => setFormData({ ...formData, ea_code: e.target.value })}
                    data-testid="input-ea-code"
                  />
                </div>
                <div className="space-y-2">
                  <Label>{isRTL ? 'رقم الشهادة' : 'Certificate Number'}</Label>
                  <Input
                    value={formData.certificate_number}
                    onChange={(e) => setFormData({ ...formData, certificate_number: e.target.value })}
                    data-testid="input-certificate-number"
                  />
                </div>
              </div>
            </div>

            {/* Important Dates */}
            <div className="p-3 bg-yellow-50 rounded-lg">
              <h3 className="font-medium mb-3">{isRTL ? 'التواريخ المهمة' : 'Important Dates'}</h3>
              <div className="grid grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label>{isRTL ? 'تاريخ الإصدار' : 'Issue Date'}</Label>
                  <Input
                    type="date"
                    value={formData.issue_date}
                    onChange={(e) => setFormData({ ...formData, issue_date: e.target.value })}
                    data-testid="input-issue-date"
                  />
                </div>
                <div className="space-y-2">
                  <Label>{isRTL ? 'تاريخ الانتهاء' : 'Expiry Date'}</Label>
                  <Input
                    type="date"
                    value={formData.expiry_date}
                    onChange={(e) => setFormData({ ...formData, expiry_date: e.target.value })}
                    data-testid="input-expiry-date"
                  />
                </div>
                <div className="space-y-2">
                  <Label>{isRTL ? 'إعادة الاعتماد' : 'Recertification'}</Label>
                  <Input
                    type="date"
                    value={formData.recertification_date}
                    onChange={(e) => setFormData({ ...formData, recertification_date: e.target.value })}
                    data-testid="input-recert-date"
                  />
                </div>
                <div className="space-y-2">
                  <Label>{isRTL ? 'المراقبة الأولى' : 'Surveillance 1'}</Label>
                  <Input
                    type="date"
                    value={formData.surveillance_1_date}
                    onChange={(e) => setFormData({ ...formData, surveillance_1_date: e.target.value })}
                    data-testid="input-surv1-date"
                  />
                </div>
                <div className="space-y-2">
                  <Label>{isRTL ? 'المراقبة الثانية' : 'Surveillance 2'}</Label>
                  <Input
                    type="date"
                    value={formData.surveillance_2_date}
                    onChange={(e) => setFormData({ ...formData, surveillance_2_date: e.target.value })}
                    data-testid="input-surv2-date"
                  />
                </div>
              </div>
            </div>

            <div className="flex justify-end gap-2 mt-4">
              <Button variant="outline" onClick={() => setShowCreateModal(false)}>
                {isRTL ? 'إلغاء' : 'Cancel'}
              </Button>
              <Button onClick={handleCreate} data-testid="create-submit-btn">
                {isRTL ? 'إضافة' : 'Add Client'}
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
              {isRTL ? 'تفاصيل العميل المعتمد' : 'Certified Client Details'}
            </DialogTitle>
          </DialogHeader>
          
          {selectedClient && (
            <div className="space-y-6">
              {/* Status Badge */}
              <div className="flex justify-between items-center">
                <span className="font-mono text-lg font-bold">{selectedClient.certificate_number || 'N/A'}</span>
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
                  <p className="text-sm text-gray-500">{isRTL ? 'مسؤول الاتصال' : 'Contact Person'}</p>
                  <p className="font-medium">{selectedClient.contact_person || '-'}</p>
                  <p className="text-sm">{selectedClient.contact_number || '-'}</p>
                </div>
                <div className="col-span-2">
                  <p className="text-sm text-gray-500">{isRTL ? 'العنوان' : 'Address'}</p>
                  <p className="font-medium">{selectedClient.address || '-'}</p>
                </div>
              </div>

              {/* Certification Details */}
              <div className="p-4 bg-blue-50 rounded-lg">
                <h3 className="font-medium mb-3">{isRTL ? 'تفاصيل الشهادة' : 'Certification Details'}</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-gray-500">{isRTL ? 'نطاق العمل' : 'Scope'}</p>
                    <p className="font-medium">{selectedClient.scope || '-'}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">{isRTL ? 'رمز EA' : 'EA Code'}</p>
                    <p className="font-medium">{selectedClient.ea_code || '-'}</p>
                  </div>
                  <div className="col-span-2">
                    <p className="text-sm text-gray-500">{isRTL ? 'المعايير' : 'Standards'}</p>
                    <div className="flex flex-wrap gap-2 mt-1">
                      {(selectedClient.accreditation || []).map((std, idx) => (
                        <span key={idx} className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-sm">
                          {std}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              {/* Important Dates */}
              <div className="p-4 bg-yellow-50 rounded-lg">
                <h3 className="font-medium mb-3">{isRTL ? 'التواريخ المهمة' : 'Important Dates'}</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-gray-500">{isRTL ? 'تاريخ الإصدار' : 'Issue Date'}</p>
                    <p className="font-medium">{selectedClient.issue_date || '-'}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">{isRTL ? 'تاريخ الانتهاء' : 'Expiry Date'}</p>
                    <p className="font-medium">{selectedClient.expiry_date || '-'}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">{isRTL ? 'المراقبة الأولى' : 'Surveillance 1'}</p>
                    <p className="font-medium">{selectedClient.surveillance_1_date || '-'}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">{isRTL ? 'المراقبة الثانية' : 'Surveillance 2'}</p>
                    <p className="font-medium">{selectedClient.surveillance_2_date || '-'}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">{isRTL ? 'إعادة الاعتماد' : 'Recertification'}</p>
                    <p className="font-medium">{selectedClient.recertification_date || '-'}</p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* Edit Modal */}
      <Dialog open={showEditModal} onOpenChange={setShowEditModal}>
        <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>
              {isRTL ? 'تعديل بيانات العميل' : 'Edit Client Record'}
            </DialogTitle>
          </DialogHeader>
          
          {selectedClient && (
            <div className="space-y-4">
              {/* Client Information */}
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>{isRTL ? 'اسم العميل' : 'Client Name'}</Label>
                  <Input
                    value={selectedClient.client_name}
                    onChange={(e) => setSelectedClient({ ...selectedClient, client_name: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <Label>{isRTL ? 'رقم الشهادة' : 'Certificate Number'}</Label>
                  <Input
                    value={selectedClient.certificate_number}
                    onChange={(e) => setSelectedClient({ ...selectedClient, certificate_number: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <Label>{isRTL ? 'مسؤول الاتصال' : 'Contact Person'}</Label>
                  <Input
                    value={selectedClient.contact_person}
                    onChange={(e) => setSelectedClient({ ...selectedClient, contact_person: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <Label>{isRTL ? 'رقم الاتصال' : 'Contact Number'}</Label>
                  <Input
                    value={selectedClient.contact_number}
                    onChange={(e) => setSelectedClient({ ...selectedClient, contact_number: e.target.value })}
                  />
                </div>
              </div>

              {/* Status */}
              <div className="space-y-2">
                <Label>{isRTL ? 'الحالة' : 'Status'}</Label>
                <Select
                  value={selectedClient.status}
                  onValueChange={(v) => setSelectedClient({ ...selectedClient, status: v })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="active">{isRTL ? 'نشط' : 'Active'}</SelectItem>
                    <SelectItem value="suspended">{isRTL ? 'موقوف' : 'Suspended'}</SelectItem>
                    <SelectItem value="withdrawn">{isRTL ? 'ملغى' : 'Withdrawn'}</SelectItem>
                    <SelectItem value="expired">{isRTL ? 'منتهي' : 'Expired'}</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Dates */}
              <div className="grid grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label>{isRTL ? 'تاريخ الإصدار' : 'Issue Date'}</Label>
                  <Input
                    type="date"
                    value={selectedClient.issue_date}
                    onChange={(e) => setSelectedClient({ ...selectedClient, issue_date: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <Label>{isRTL ? 'تاريخ الانتهاء' : 'Expiry Date'}</Label>
                  <Input
                    type="date"
                    value={selectedClient.expiry_date}
                    onChange={(e) => setSelectedClient({ ...selectedClient, expiry_date: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <Label>{isRTL ? 'إعادة الاعتماد' : 'Recertification'}</Label>
                  <Input
                    type="date"
                    value={selectedClient.recertification_date}
                    onChange={(e) => setSelectedClient({ ...selectedClient, recertification_date: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <Label>{isRTL ? 'المراقبة الأولى' : 'Surveillance 1'}</Label>
                  <Input
                    type="date"
                    value={selectedClient.surveillance_1_date}
                    onChange={(e) => setSelectedClient({ ...selectedClient, surveillance_1_date: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <Label>{isRTL ? 'المراقبة الثانية' : 'Surveillance 2'}</Label>
                  <Input
                    type="date"
                    value={selectedClient.surveillance_2_date}
                    onChange={(e) => setSelectedClient({ ...selectedClient, surveillance_2_date: e.target.value })}
                  />
                </div>
              </div>

              {/* Notes */}
              <div className="space-y-2">
                <Label>{isRTL ? 'ملاحظات' : 'Notes'}</Label>
                <Textarea
                  value={selectedClient.notes || ''}
                  onChange={(e) => setSelectedClient({ ...selectedClient, notes: e.target.value })}
                  placeholder={isRTL ? 'أضف ملاحظات...' : 'Add notes...'}
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
    </div>
  );
}
