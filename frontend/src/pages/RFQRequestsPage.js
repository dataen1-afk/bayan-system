import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import axios from 'axios';
import { 
  FileText, 
  Mail, 
  Phone, 
  Building2, 
  Users, 
  MapPin,
  Calendar,
  Check,
  X,
  Trash2,
  Eye,
  Clock,
  Filter,
  Search,
  RefreshCw,
  Download
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { Badge } from '@/components/ui/badge';
import { toast } from 'sonner';

const API = process.env.REACT_APP_BACKEND_URL + '/api';

const RFQRequestsPage = () => {
  const { t, i18n } = useTranslation();
  const isRTL = i18n.language?.startsWith('ar');
  
  const [rfqs, setRfqs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedRfq, setSelectedRfq] = useState(null);
  const [viewDialogOpen, setViewDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);

  useEffect(() => {
    loadRfqs();
  }, [statusFilter]);

  const loadRfqs = async () => {
    setLoading(true);
    try {
      const params = statusFilter !== 'all' ? `?status=${statusFilter}` : '';
      const response = await axios.get(`${API}/rfq-requests${params}`);
      setRfqs(response.data);
    } catch (error) {
      console.error('Error loading RFQs:', error);
      toast.error(isRTL ? 'خطأ في تحميل الطلبات' : 'Error loading requests');
    } finally {
      setLoading(false);
    }
  };

  const updateStatus = async (rfqId, newStatus) => {
    try {
      await axios.put(`${API}/rfq-requests/${rfqId}?status=${newStatus}`);
      toast.success(isRTL ? 'تم تحديث الحالة' : 'Status updated');
      loadRfqs();
      setViewDialogOpen(false);
    } catch (error) {
      console.error('Error updating status:', error);
      toast.error(isRTL ? 'خطأ في تحديث الحالة' : 'Error updating status');
    }
  };

  const deleteRfq = async () => {
    if (!selectedRfq) return;
    try {
      await axios.delete(`${API}/rfq-requests/${selectedRfq.id}`);
      toast.success(isRTL ? 'تم حذف الطلب' : 'Request deleted');
      loadRfqs();
      setDeleteDialogOpen(false);
      setSelectedRfq(null);
    } catch (error) {
      console.error('Error deleting RFQ:', error);
      toast.error(isRTL ? 'خطأ في حذف الطلب' : 'Error deleting request');
    }
  };

  const getStatusBadge = (status) => {
    const statusConfig = {
      'new': { color: 'bg-blue-100 text-blue-800', label: isRTL ? 'جديد' : 'New' },
      'in_progress': { color: 'bg-yellow-100 text-yellow-800', label: isRTL ? 'قيد المعالجة' : 'In Progress' },
      'quoted': { color: 'bg-green-100 text-green-800', label: isRTL ? 'تم إرسال العرض' : 'Quoted' },
      'closed': { color: 'bg-gray-100 text-gray-800', label: isRTL ? 'مغلق' : 'Closed' },
    };
    const config = statusConfig[status] || statusConfig['new'];
    return <Badge className={config.color}>{config.label}</Badge>;
  };

  const formatDate = (dateString) => {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString(isRTL ? 'ar-SA' : 'en-GB', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const filteredRfqs = rfqs.filter(rfq => {
    if (!searchQuery) return true;
    const query = searchQuery.toLowerCase();
    return (
      rfq.company_name?.toLowerCase().includes(query) ||
      rfq.contact_name?.toLowerCase().includes(query) ||
      rfq.email?.toLowerCase().includes(query)
    );
  });

  const exportToCSV = () => {
    const headers = ['Company', 'Contact', 'Email', 'Phone', 'Standards', 'Status', 'Date'];
    const rows = filteredRfqs.map(rfq => [
      rfq.company_name,
      rfq.contact_name,
      rfq.email,
      rfq.phone,
      rfq.standards?.join(', '),
      rfq.status,
      formatDate(rfq.created_at)
    ]);
    
    const csvContent = [headers, ...rows].map(row => row.join(',')).join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `rfq_requests_${new Date().toISOString().split('T')[0]}.csv`;
    link.click();
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className={`flex items-center justify-between ${isRTL ? 'flex-row-reverse' : ''}`}>
        <div>
          <h1 className={`text-2xl font-bold text-gray-900 ${isRTL ? 'text-right' : ''}`}>
            {isRTL ? 'طلبات عروض الأسعار' : 'Quote Requests'}
          </h1>
          <p className={`text-gray-500 mt-1 ${isRTL ? 'text-right' : ''}`}>
            {isRTL ? 'إدارة طلبات عروض الأسعار من بوابة العملاء' : 'Manage quote requests from the customer portal'}
          </p>
        </div>
        <div className={`flex items-center gap-2 ${isRTL ? 'flex-row-reverse' : ''}`}>
          <Button variant="outline" onClick={loadRfqs} disabled={loading}>
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''} ${isRTL ? 'ml-2' : 'mr-2'}`} />
            {isRTL ? 'تحديث' : 'Refresh'}
          </Button>
          <Button variant="outline" onClick={exportToCSV}>
            <Download className={`w-4 h-4 ${isRTL ? 'ml-2' : 'mr-2'}`} />
            {isRTL ? 'تصدير' : 'Export'}
          </Button>
        </div>
      </div>

      {/* Filters */}
      <div className={`flex items-center gap-4 ${isRTL ? 'flex-row-reverse' : ''}`}>
        <div className="relative flex-1 max-w-md">
          <Search className={`absolute top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4 ${isRTL ? 'right-3' : 'left-3'}`} />
          <Input
            placeholder={isRTL ? 'البحث عن شركة أو جهة اتصال...' : 'Search company or contact...'}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className={isRTL ? 'pr-10 text-right' : 'pl-10'}
          />
        </div>
        <Select value={statusFilter} onValueChange={setStatusFilter}>
          <SelectTrigger className="w-48">
            <Filter className={`w-4 h-4 ${isRTL ? 'ml-2' : 'mr-2'}`} />
            <SelectValue placeholder={isRTL ? 'تصفية حسب الحالة' : 'Filter by status'} />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">{isRTL ? 'الكل' : 'All'}</SelectItem>
            <SelectItem value="new">{isRTL ? 'جديد' : 'New'}</SelectItem>
            <SelectItem value="in_progress">{isRTL ? 'قيد المعالجة' : 'In Progress'}</SelectItem>
            <SelectItem value="quoted">{isRTL ? 'تم إرسال العرض' : 'Quoted'}</SelectItem>
            <SelectItem value="closed">{isRTL ? 'مغلق' : 'Closed'}</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-blue-50 rounded-lg p-4 border border-blue-100">
          <div className={`flex items-center gap-3 ${isRTL ? 'flex-row-reverse' : ''}`}>
            <div className="p-2 bg-blue-100 rounded-lg">
              <FileText className="w-5 h-5 text-blue-600" />
            </div>
            <div className={isRTL ? 'text-right' : ''}>
              <p className="text-sm text-blue-600">{isRTL ? 'جديد' : 'New'}</p>
              <p className="text-2xl font-bold text-blue-800">
                {rfqs.filter(r => r.status === 'new').length}
              </p>
            </div>
          </div>
        </div>
        <div className="bg-yellow-50 rounded-lg p-4 border border-yellow-100">
          <div className={`flex items-center gap-3 ${isRTL ? 'flex-row-reverse' : ''}`}>
            <div className="p-2 bg-yellow-100 rounded-lg">
              <Clock className="w-5 h-5 text-yellow-600" />
            </div>
            <div className={isRTL ? 'text-right' : ''}>
              <p className="text-sm text-yellow-600">{isRTL ? 'قيد المعالجة' : 'In Progress'}</p>
              <p className="text-2xl font-bold text-yellow-800">
                {rfqs.filter(r => r.status === 'in_progress').length}
              </p>
            </div>
          </div>
        </div>
        <div className="bg-green-50 rounded-lg p-4 border border-green-100">
          <div className={`flex items-center gap-3 ${isRTL ? 'flex-row-reverse' : ''}`}>
            <div className="p-2 bg-green-100 rounded-lg">
              <Check className="w-5 h-5 text-green-600" />
            </div>
            <div className={isRTL ? 'text-right' : ''}>
              <p className="text-sm text-green-600">{isRTL ? 'تم إرسال العرض' : 'Quoted'}</p>
              <p className="text-2xl font-bold text-green-800">
                {rfqs.filter(r => r.status === 'quoted').length}
              </p>
            </div>
          </div>
        </div>
        <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
          <div className={`flex items-center gap-3 ${isRTL ? 'flex-row-reverse' : ''}`}>
            <div className="p-2 bg-gray-100 rounded-lg">
              <X className="w-5 h-5 text-gray-600" />
            </div>
            <div className={isRTL ? 'text-right' : ''}>
              <p className="text-sm text-gray-600">{isRTL ? 'مغلق' : 'Closed'}</p>
              <p className="text-2xl font-bold text-gray-800">
                {rfqs.filter(r => r.status === 'closed').length}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="bg-white rounded-lg border shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className={`px-4 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider ${isRTL ? 'text-right' : 'text-left'}`}>
                  {isRTL ? 'الشركة' : 'Company'}
                </th>
                <th className={`px-4 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider ${isRTL ? 'text-right' : 'text-left'}`}>
                  {isRTL ? 'جهة الاتصال' : 'Contact'}
                </th>
                <th className={`px-4 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider ${isRTL ? 'text-right' : 'text-left'}`}>
                  {isRTL ? 'المعايير' : 'Standards'}
                </th>
                <th className={`px-4 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider ${isRTL ? 'text-right' : 'text-left'}`}>
                  {isRTL ? 'الحالة' : 'Status'}
                </th>
                <th className={`px-4 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider ${isRTL ? 'text-right' : 'text-left'}`}>
                  {isRTL ? 'التاريخ' : 'Date'}
                </th>
                <th className={`px-4 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider ${isRTL ? 'text-right' : 'text-left'}`}>
                  {isRTL ? 'الإجراءات' : 'Actions'}
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {loading ? (
                <tr>
                  <td colSpan="6" className="px-4 py-8 text-center text-gray-500">
                    {isRTL ? 'جاري التحميل...' : 'Loading...'}
                  </td>
                </tr>
              ) : filteredRfqs.length === 0 ? (
                <tr>
                  <td colSpan="6" className="px-4 py-8 text-center text-gray-500">
                    {isRTL ? 'لا توجد طلبات' : 'No requests found'}
                  </td>
                </tr>
              ) : (
                filteredRfqs.map((rfq) => (
                  <tr key={rfq.id} className="hover:bg-gray-50">
                    <td className={`px-4 py-3 ${isRTL ? 'text-right' : ''}`}>
                      <div className="font-medium text-gray-900">{rfq.company_name}</div>
                      <div className="text-sm text-gray-500">{rfq.employees} {isRTL ? 'موظف' : 'employees'}</div>
                    </td>
                    <td className={`px-4 py-3 ${isRTL ? 'text-right' : ''}`}>
                      <div className="text-gray-900">{rfq.contact_name}</div>
                      <div className="text-sm text-gray-500">{rfq.email}</div>
                    </td>
                    <td className={`px-4 py-3 ${isRTL ? 'text-right' : ''}`}>
                      <div className="flex flex-wrap gap-1">
                        {rfq.standards?.slice(0, 2).map((std, idx) => (
                          <Badge key={idx} variant="outline" className="text-xs">{std}</Badge>
                        ))}
                        {rfq.standards?.length > 2 && (
                          <Badge variant="outline" className="text-xs">+{rfq.standards.length - 2}</Badge>
                        )}
                      </div>
                    </td>
                    <td className={`px-4 py-3 ${isRTL ? 'text-right' : ''}`}>
                      {getStatusBadge(rfq.status)}
                    </td>
                    <td className={`px-4 py-3 text-sm text-gray-500 ${isRTL ? 'text-right' : ''}`}>
                      {formatDate(rfq.created_at)}
                    </td>
                    <td className={`px-4 py-3 ${isRTL ? 'text-right' : ''}`}>
                      <div className={`flex items-center gap-2 ${isRTL ? 'flex-row-reverse' : ''}`}>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => { setSelectedRfq(rfq); setViewDialogOpen(true); }}
                        >
                          <Eye className="w-4 h-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="text-red-600 hover:text-red-700"
                          onClick={() => { setSelectedRfq(rfq); setDeleteDialogOpen(true); }}
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* View Dialog */}
      <Dialog open={viewDialogOpen} onOpenChange={setViewDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle className={isRTL ? 'text-right' : ''}>
              {isRTL ? 'تفاصيل طلب عرض السعر' : 'Quote Request Details'}
            </DialogTitle>
          </DialogHeader>
          {selectedRfq && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className={`space-y-1 ${isRTL ? 'text-right' : ''}`}>
                  <label className="text-sm font-medium text-gray-500">
                    {isRTL ? 'اسم الشركة' : 'Company Name'}
                  </label>
                  <p className="flex items-center gap-2">
                    <Building2 className="w-4 h-4 text-gray-400" />
                    {selectedRfq.company_name}
                  </p>
                </div>
                <div className={`space-y-1 ${isRTL ? 'text-right' : ''}`}>
                  <label className="text-sm font-medium text-gray-500">
                    {isRTL ? 'جهة الاتصال' : 'Contact Person'}
                  </label>
                  <p className="flex items-center gap-2">
                    <Users className="w-4 h-4 text-gray-400" />
                    {selectedRfq.contact_name}
                  </p>
                </div>
                <div className={`space-y-1 ${isRTL ? 'text-right' : ''}`}>
                  <label className="text-sm font-medium text-gray-500">
                    {isRTL ? 'البريد الإلكتروني' : 'Email'}
                  </label>
                  <p className="flex items-center gap-2">
                    <Mail className="w-4 h-4 text-gray-400" />
                    {selectedRfq.email}
                  </p>
                </div>
                <div className={`space-y-1 ${isRTL ? 'text-right' : ''}`}>
                  <label className="text-sm font-medium text-gray-500">
                    {isRTL ? 'الهاتف' : 'Phone'}
                  </label>
                  <p className="flex items-center gap-2">
                    <Phone className="w-4 h-4 text-gray-400" />
                    {selectedRfq.phone}
                  </p>
                </div>
                <div className={`space-y-1 ${isRTL ? 'text-right' : ''}`}>
                  <label className="text-sm font-medium text-gray-500">
                    {isRTL ? 'عدد الموظفين' : 'Employees'}
                  </label>
                  <p>{selectedRfq.employees}</p>
                </div>
                <div className={`space-y-1 ${isRTL ? 'text-right' : ''}`}>
                  <label className="text-sm font-medium text-gray-500">
                    {isRTL ? 'عدد المواقع' : 'Sites'}
                  </label>
                  <p>{selectedRfq.sites}</p>
                </div>
              </div>
              <div className={`space-y-1 ${isRTL ? 'text-right' : ''}`}>
                <label className="text-sm font-medium text-gray-500">
                  {isRTL ? 'المعايير المطلوبة' : 'Requested Standards'}
                </label>
                <div className="flex flex-wrap gap-2 mt-1">
                  {selectedRfq.standards?.map((std, idx) => (
                    <Badge key={idx} variant="secondary">{std}</Badge>
                  ))}
                </div>
              </div>
              {selectedRfq.message && (
                <div className={`space-y-1 ${isRTL ? 'text-right' : ''}`}>
                  <label className="text-sm font-medium text-gray-500">
                    {isRTL ? 'الرسالة' : 'Message'}
                  </label>
                  <p className="text-gray-700 bg-gray-50 p-3 rounded-lg">{selectedRfq.message}</p>
                </div>
              )}
              <div className={`space-y-1 ${isRTL ? 'text-right' : ''}`}>
                <label className="text-sm font-medium text-gray-500">
                  {isRTL ? 'تغيير الحالة' : 'Change Status'}
                </label>
                <div className={`flex gap-2 mt-2 ${isRTL ? 'flex-row-reverse' : ''}`}>
                  <Button
                    variant={selectedRfq.status === 'in_progress' ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => updateStatus(selectedRfq.id, 'in_progress')}
                  >
                    {isRTL ? 'قيد المعالجة' : 'In Progress'}
                  </Button>
                  <Button
                    variant={selectedRfq.status === 'quoted' ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => updateStatus(selectedRfq.id, 'quoted')}
                  >
                    {isRTL ? 'تم إرسال العرض' : 'Quoted'}
                  </Button>
                  <Button
                    variant={selectedRfq.status === 'closed' ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => updateStatus(selectedRfq.id, 'closed')}
                  >
                    {isRTL ? 'إغلاق' : 'Close'}
                  </Button>
                </div>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle className={isRTL ? 'text-right' : ''}>
              {isRTL ? 'تأكيد الحذف' : 'Confirm Delete'}
            </DialogTitle>
          </DialogHeader>
          <p className={`text-gray-600 ${isRTL ? 'text-right' : ''}`}>
            {isRTL 
              ? `هل أنت متأكد من حذف طلب ${selectedRfq?.company_name}؟`
              : `Are you sure you want to delete the request from ${selectedRfq?.company_name}?`
            }
          </p>
          <DialogFooter className={isRTL ? 'flex-row-reverse' : ''}>
            <Button variant="outline" onClick={() => setDeleteDialogOpen(false)}>
              {isRTL ? 'إلغاء' : 'Cancel'}
            </Button>
            <Button variant="destructive" onClick={deleteRfq}>
              {isRTL ? 'حذف' : 'Delete'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default RFQRequestsPage;
