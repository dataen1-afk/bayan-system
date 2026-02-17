import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import axios from 'axios';
import { 
  ArrowRightLeft, Plus, Eye, Edit, Trash2, Download, CheckCircle, XCircle,
  Building, Calendar, FileText, AlertTriangle, Clock
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

export default function PreTransferReviewPage() {
  const { t, i18n } = useTranslation();
  const isRTL = i18n.language === 'ar';
  
  const [reviewsList, setReviewsList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showViewModal, setShowViewModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDecisionModal, setShowDecisionModal] = useState(false);
  const [selectedReview, setSelectedReview] = useState(null);
  
  const [formData, setFormData] = useState({
    client_name: '',
    client_name_ar: '',
    client_address: '',
    client_phone: '',
    enquiry_reference: '',
    transfer_reason: '',
    existing_cb: '',
    certificate_number: '',
    validity: '',
    scope: '',
    sites: '',
    eac_code: '',
    standards: []
  });

  const [decisionData, setDecisionData] = useState({
    transfer_decision: '',
    decision_reason: '',
    reviewed_by: '',
    review_date: new Date().toISOString().split('T')[0],
    approved_by: '',
    approval_date: new Date().toISOString().split('T')[0]
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

  const checklistItems = [
    { key: 'suspension_status', label: 'Certificate under suspension?', label_ar: 'الشهادة تحت التعليق؟' },
    { key: 'threat_of_suspension', label: 'Under threat of suspension?', label_ar: 'تحت تهديد بالتعليق؟' },
    { key: 'minor_nc_outstanding', label: 'Any minor non-conformity outstanding?', label_ar: 'هل توجد عدم مطابقة بسيطة معلقة؟' },
    { key: 'major_nc_outstanding', label: 'Any major non-conformity outstanding?', label_ar: 'هل توجد عدم مطابقة كبرى معلقة؟' },
    { key: 'legal_representation', label: 'Engaged in legal representation?', label_ar: 'مشارك في تمثيل قانوني؟' },
    { key: 'complaints_handled', label: 'Complaints appropriately handled?', label_ar: 'تم التعامل مع الشكاوى بشكل مناسب؟' },
    { key: 'within_bac_scope', label: 'Activities within BAC accreditation scope?', label_ar: 'الأنشطة ضمن نطاق اعتماد بيان؟' },
    { key: 'previous_reports_available', label: 'Previous assessment reports available?', label_ar: 'تقارير التقييم السابقة متوفرة؟' }
  ];

  useEffect(() => {
    fetchReviews();
  }, []);

  const fetchReviews = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/pre-transfer-reviews`, { headers });
      setReviewsList(response.data);
    } catch (error) {
      console.error('Error fetching pre-transfer reviews:', error);
      toast.error(isRTL ? 'خطأ في جلب مراجعات النقل' : 'Error fetching pre-transfer reviews');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async () => {
    try {
      if (!formData.client_name) {
        toast.error(isRTL ? 'اسم العميل مطلوب' : 'Client name is required');
        return;
      }
      
      await axios.post(`${API_URL}/api/pre-transfer-reviews`, formData, { headers });
      toast.success(isRTL ? 'تم إنشاء مراجعة النقل' : 'Pre-transfer review created');
      setShowCreateModal(false);
      resetForm();
      fetchReviews();
    } catch (error) {
      console.error('Error creating pre-transfer review:', error);
      toast.error(isRTL ? 'خطأ في إنشاء مراجعة النقل' : 'Error creating pre-transfer review');
    }
  };

  const handleUpdate = async () => {
    if (!selectedReview) return;
    
    try {
      await axios.put(`${API_URL}/api/pre-transfer-reviews/${selectedReview.id}`, selectedReview, { headers });
      toast.success(isRTL ? 'تم تحديث مراجعة النقل' : 'Pre-transfer review updated');
      setShowEditModal(false);
      fetchReviews();
    } catch (error) {
      console.error('Error updating pre-transfer review:', error);
      toast.error(isRTL ? 'خطأ في تحديث مراجعة النقل' : 'Error updating pre-transfer review');
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm(isRTL ? 'هل أنت متأكد من الحذف؟' : 'Are you sure you want to delete?')) return;
    
    try {
      await axios.delete(`${API_URL}/api/pre-transfer-reviews/${id}`, { headers });
      toast.success(isRTL ? 'تم حذف مراجعة النقل' : 'Pre-transfer review deleted');
      fetchReviews();
    } catch (error) {
      console.error('Error deleting pre-transfer review:', error);
      toast.error(isRTL ? 'خطأ في حذف مراجعة النقل' : 'Error deleting pre-transfer review');
    }
  };

  const handleMakeDecision = async () => {
    if (!selectedReview || !decisionData.transfer_decision) return;
    
    try {
      await axios.post(`${API_URL}/api/pre-transfer-reviews/${selectedReview.id}/make-decision`, decisionData, { headers });
      toast.success(isRTL ? 'تم تسجيل القرار' : 'Decision recorded');
      setShowDecisionModal(false);
      fetchReviews();
    } catch (error) {
      console.error('Error making decision:', error);
      toast.error(isRTL ? 'خطأ في تسجيل القرار' : 'Error recording decision');
    }
  };

  const handleDownloadPDF = async (id) => {
    try {
      const response = await axios.get(`${API_URL}/api/pre-transfer-reviews/${id}/pdf`, {
        headers,
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `pre_transfer_review_${id.substring(0, 8)}.pdf`);
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
      client_address: '',
      client_phone: '',
      enquiry_reference: '',
      transfer_reason: '',
      existing_cb: '',
      certificate_number: '',
      validity: '',
      scope: '',
      sites: '',
      eac_code: '',
      standards: []
    });
  };

  const updateChecklist = (key, value) => {
    if (!selectedReview) return;
    const newChecklist = { ...selectedReview.checklist, [key]: value };
    setSelectedReview({ ...selectedReview, checklist: newChecklist });
  };

  const getStatusBadge = (status) => {
    const statusConfig = {
      draft: { bg: 'bg-gray-100', text: 'text-gray-700', label: isRTL ? 'مسودة' : 'Draft' },
      under_review: { bg: 'bg-blue-100', text: 'text-blue-700', label: isRTL ? 'قيد المراجعة' : 'Under Review' },
      decision_made: { bg: 'bg-purple-100', text: 'text-purple-700', label: isRTL ? 'تم اتخاذ القرار' : 'Decision Made' }
    };
    const config = statusConfig[status] || statusConfig.draft;
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${config.bg} ${config.text}`}>
        {config.label}
      </span>
    );
  };

  const getDecisionBadge = (decision) => {
    if (!decision || decision === 'pending') return null;
    const decisionConfig = {
      approved: { bg: 'bg-green-100', text: 'text-green-700', label: isRTL ? 'تمت الموافقة' : 'Approved', icon: CheckCircle },
      rejected: { bg: 'bg-red-100', text: 'text-red-700', label: isRTL ? 'مرفوض' : 'Rejected', icon: XCircle }
    };
    const config = decisionConfig[decision];
    if (!config) return null;
    const Icon = config.icon;
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${config.bg} ${config.text} flex items-center gap-1`}>
        <Icon className="w-3 h-3" />
        {config.label}
      </span>
    );
  };

  // Stats
  const stats = {
    total: reviewsList.length,
    draft: reviewsList.filter(r => r.status === 'draft').length,
    approved: reviewsList.filter(r => r.transfer_decision === 'approved').length,
    rejected: reviewsList.filter(r => r.transfer_decision === 'rejected').length,
    pending: reviewsList.filter(r => !r.transfer_decision || r.transfer_decision === 'pending').length
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
            {isRTL ? 'مراجعة ما قبل النقل' : 'Pre-Transfer Review'}
          </h1>
          <p className="text-sm text-gray-500">
            BAC-F6-17 - {isRTL ? 'تقييم نقل الشهادة من جهة اعتماد أخرى' : 'Certificate transfer assessment from other CB'}
          </p>
        </div>
        <Button onClick={() => setShowCreateModal(true)} className="flex items-center gap-2">
          <Plus className="w-4 h-4" />
          {isRTL ? 'إنشاء مراجعة نقل' : 'Create Transfer Review'}
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">{isRTL ? 'إجمالي الطلبات' : 'Total Requests'}</p>
                <p className="text-2xl font-bold text-primary">{stats.total}</p>
              </div>
              <ArrowRightLeft className="w-8 h-8 text-gray-300" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">{isRTL ? 'مسودة' : 'Draft'}</p>
                <p className="text-2xl font-bold text-gray-600">{stats.draft}</p>
              </div>
              <FileText className="w-8 h-8 text-gray-300" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">{isRTL ? 'قيد الانتظار' : 'Pending'}</p>
                <p className="text-2xl font-bold text-yellow-600">{stats.pending}</p>
              </div>
              <Clock className="w-8 h-8 text-yellow-300" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">{isRTL ? 'تمت الموافقة' : 'Approved'}</p>
                <p className="text-2xl font-bold text-green-600">{stats.approved}</p>
              </div>
              <CheckCircle className="w-8 h-8 text-green-300" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">{isRTL ? 'مرفوض' : 'Rejected'}</p>
                <p className="text-2xl font-bold text-red-600">{stats.rejected}</p>
              </div>
              <XCircle className="w-8 h-8 text-red-300" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Reviews Table */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <ArrowRightLeft className="w-5 h-5" />
            {isRTL ? 'جميع طلبات النقل' : 'All Transfer Requests'}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b bg-gray-50">
                  <th className="text-start p-3 font-medium">{isRTL ? 'اسم العميل' : 'Client Name'}</th>
                  <th className="text-start p-3 font-medium">{isRTL ? 'جهة الاعتماد السابقة' : 'Previous CB'}</th>
                  <th className="text-start p-3 font-medium">{isRTL ? 'رقم الشهادة' : 'Cert. No.'}</th>
                  <th className="text-start p-3 font-medium">{isRTL ? 'الحالة' : 'Status'}</th>
                  <th className="text-start p-3 font-medium">{isRTL ? 'القرار' : 'Decision'}</th>
                  <th className="text-start p-3 font-medium">{isRTL ? 'الإجراءات' : 'Actions'}</th>
                </tr>
              </thead>
              <tbody>
                {reviewsList.map((review) => (
                  <tr key={review.id} className="border-b hover:bg-gray-50">
                    <td className="p-3">
                      <div className="font-medium">{review.client_name}</div>
                      <div className="text-sm text-gray-500">{review.client_name_ar}</div>
                    </td>
                    <td className="p-3">{review.existing_cb || '-'}</td>
                    <td className="p-3">
                      <span className="font-mono text-sm">{review.certificate_number || '-'}</span>
                    </td>
                    <td className="p-3">{getStatusBadge(review.status)}</td>
                    <td className="p-3">{getDecisionBadge(review.transfer_decision)}</td>
                    <td className="p-3">
                      <div className="flex items-center gap-1">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => {
                            setSelectedReview(review);
                            setShowViewModal(true);
                          }}
                          title={isRTL ? 'عرض' : 'View'}
                        >
                          <Eye className="w-4 h-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => {
                            setSelectedReview(review);
                            setShowEditModal(true);
                          }}
                          title={isRTL ? 'تعديل' : 'Edit'}
                        >
                          <Edit className="w-4 h-4" />
                        </Button>
                        {(!review.transfer_decision || review.transfer_decision === 'pending') && (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => {
                              setSelectedReview(review);
                              setDecisionData({
                                transfer_decision: '',
                                decision_reason: '',
                                reviewed_by: '',
                                review_date: new Date().toISOString().split('T')[0],
                                approved_by: '',
                                approval_date: new Date().toISOString().split('T')[0]
                              });
                              setShowDecisionModal(true);
                            }}
                            title={isRTL ? 'اتخاذ القرار' : 'Make Decision'}
                            className="text-purple-600 hover:text-purple-700"
                          >
                            <CheckCircle className="w-4 h-4" />
                          </Button>
                        )}
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDownloadPDF(review.id)}
                          title={isRTL ? 'تحميل PDF' : 'Download PDF'}
                          className="text-blue-600 hover:text-blue-700"
                        >
                          <Download className="w-4 h-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDelete(review.id)}
                          title={isRTL ? 'حذف' : 'Delete'}
                          className="text-red-600 hover:text-red-700"
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))}
                {reviewsList.length === 0 && (
                  <tr>
                    <td colSpan={6} className="p-8 text-center text-gray-500">
                      {isRTL ? 'لا توجد طلبات نقل' : 'No transfer requests found'}
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
            <DialogTitle>
              {isRTL ? 'إنشاء مراجعة نقل جديدة' : 'Create New Transfer Review'}
            </DialogTitle>
          </DialogHeader>
          
          <div className="space-y-4">
            {/* Client Info */}
            <div className="p-3 bg-blue-50 rounded-lg">
              <h3 className="font-medium mb-3">{isRTL ? 'معلومات العميل' : 'Client Information'}</h3>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>{isRTL ? 'اسم العميل (إنجليزي)' : 'Client Name (English)'} *</Label>
                  <Input
                    value={formData.client_name}
                    onChange={(e) => setFormData({ ...formData, client_name: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <Label>{isRTL ? 'اسم العميل (عربي)' : 'Client Name (Arabic)'}</Label>
                  <Input
                    value={formData.client_name_ar}
                    onChange={(e) => setFormData({ ...formData, client_name_ar: e.target.value })}
                    dir="rtl"
                  />
                </div>
                <div className="space-y-2 col-span-2">
                  <Label>{isRTL ? 'العنوان' : 'Address'}</Label>
                  <Input
                    value={formData.client_address}
                    onChange={(e) => setFormData({ ...formData, client_address: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <Label>{isRTL ? 'رقم الهاتف' : 'Phone'}</Label>
                  <Input
                    value={formData.client_phone}
                    onChange={(e) => setFormData({ ...formData, client_phone: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <Label>{isRTL ? 'رقم مرجع الاستفسار' : 'Enquiry Reference'}</Label>
                  <Input
                    value={formData.enquiry_reference}
                    onChange={(e) => setFormData({ ...formData, enquiry_reference: e.target.value })}
                  />
                </div>
              </div>
            </div>

            {/* Transfer Details */}
            <div className="p-3 bg-green-50 rounded-lg">
              <h3 className="font-medium mb-3">{isRTL ? 'تفاصيل النقل' : 'Transfer Details'}</h3>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2 col-span-2">
                  <Label>{isRTL ? 'سبب النقل' : 'Reason for Transfer'}</Label>
                  <Textarea
                    value={formData.transfer_reason}
                    onChange={(e) => setFormData({ ...formData, transfer_reason: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <Label>{isRTL ? 'جهة الاعتماد الحالية' : 'Existing CB'}</Label>
                  <Input
                    value={formData.existing_cb}
                    onChange={(e) => setFormData({ ...formData, existing_cb: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <Label>{isRTL ? 'رقم الشهادة' : 'Certificate Number'}</Label>
                  <Input
                    value={formData.certificate_number}
                    onChange={(e) => setFormData({ ...formData, certificate_number: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <Label>{isRTL ? 'الصلاحية' : 'Validity'}</Label>
                  <Input
                    value={formData.validity}
                    onChange={(e) => setFormData({ ...formData, validity: e.target.value })}
                    placeholder="e.g., 2024-01-01 to 2027-01-01"
                  />
                </div>
                <div className="space-y-2">
                  <Label>{isRTL ? 'رمز EAC' : 'EAC Code'}</Label>
                  <Input
                    value={formData.eac_code}
                    onChange={(e) => setFormData({ ...formData, eac_code: e.target.value })}
                  />
                </div>
                <div className="space-y-2 col-span-2">
                  <Label>{isRTL ? 'نطاق الأنشطة' : 'Scope of Activities'}</Label>
                  <Textarea
                    value={formData.scope}
                    onChange={(e) => setFormData({ ...formData, scope: e.target.value })}
                  />
                </div>
                <div className="space-y-2 col-span-2">
                  <Label>{isRTL ? 'المواقع' : 'Sites'}</Label>
                  <Input
                    value={formData.sites}
                    onChange={(e) => setFormData({ ...formData, sites: e.target.value })}
                  />
                </div>
              </div>
            </div>

            {/* Standards */}
            <div className="space-y-2">
              <Label>{isRTL ? 'المعايير' : 'Standards'}</Label>
              <div className="flex flex-wrap gap-2">
                {standardOptions.map(std => (
                  <label key={std} className="flex items-center gap-2 cursor-pointer">
                    <Checkbox
                      checked={formData.standards.includes(std)}
                      onCheckedChange={(checked) => {
                        if (checked) {
                          setFormData({ ...formData, standards: [...formData.standards, std] });
                        } else {
                          setFormData({ ...formData, standards: formData.standards.filter(s => s !== std) });
                        }
                      }}
                    />
                    <span className="text-sm">{std}</span>
                  </label>
                ))}
              </div>
            </div>

            <div className="flex justify-end gap-2 mt-4">
              <Button variant="outline" onClick={() => setShowCreateModal(false)}>
                {isRTL ? 'إلغاء' : 'Cancel'}
              </Button>
              <Button onClick={handleCreate}>
                {isRTL ? 'إنشاء' : 'Create'}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* View Modal */}
      <Dialog open={showViewModal} onOpenChange={setShowViewModal}>
        <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>
              {isRTL ? 'عرض مراجعة النقل' : 'View Transfer Review'}
            </DialogTitle>
          </DialogHeader>
          
          {selectedReview && (
            <div className="space-y-6">
              {/* Client Info */}
              <div className="grid grid-cols-2 gap-4 p-4 bg-gray-50 rounded-lg">
                <div>
                  <p className="text-sm text-gray-500">{isRTL ? 'اسم العميل' : 'Client Name'}</p>
                  <p className="font-medium">{selectedReview.client_name}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">{isRTL ? 'جهة الاعتماد السابقة' : 'Previous CB'}</p>
                  <p className="font-medium">{selectedReview.existing_cb || '-'}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">{isRTL ? 'رقم الشهادة' : 'Certificate No.'}</p>
                  <p className="font-medium font-mono">{selectedReview.certificate_number || '-'}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">{isRTL ? 'الحالة' : 'Status'}</p>
                  {getStatusBadge(selectedReview.status)}
                </div>
              </div>

              {/* Decision Section */}
              {selectedReview.transfer_decision && selectedReview.transfer_decision !== 'pending' && (
                <div className={`p-4 rounded-lg ${
                  selectedReview.transfer_decision === 'approved' ? 'bg-green-50' : 'bg-red-50'
                }`}>
                  <h3 className="font-medium mb-2">{isRTL ? 'قرار النقل' : 'Transfer Decision'}</h3>
                  <div className="flex items-center gap-4">
                    {getDecisionBadge(selectedReview.transfer_decision)}
                  </div>
                  {selectedReview.decision_reason && (
                    <p className="mt-2 text-sm text-gray-600">{selectedReview.decision_reason}</p>
                  )}
                </div>
              )}

              {/* Checklist */}
              <div>
                <h3 className="font-medium mb-3">{isRTL ? 'قائمة التحقق' : 'Compliance Checklist'}</h3>
                <div className="border rounded-lg overflow-hidden">
                  <table className="w-full text-sm">
                    <thead className="bg-gray-100">
                      <tr>
                        <th className="text-start p-2">{isRTL ? 'البند' : 'Item'}</th>
                        <th className="text-center p-2 w-20">{isRTL ? 'النتيجة' : 'Result'}</th>
                      </tr>
                    </thead>
                    <tbody>
                      {checklistItems.map((item) => (
                        <tr key={item.key} className="border-t">
                          <td className="p-2">{isRTL ? item.label_ar : item.label}</td>
                          <td className="p-2 text-center">
                            {selectedReview.checklist?.[item.key] === true && (
                              <span className="text-green-600 font-bold">Yes</span>
                            )}
                            {selectedReview.checklist?.[item.key] === false && (
                              <span className="text-red-600 font-bold">No</span>
                            )}
                            {selectedReview.checklist?.[item.key] === null && (
                              <span className="text-gray-400">N/A</span>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Approval Info */}
              {selectedReview.approved_by && (
                <div className="p-4 bg-blue-50 rounded-lg">
                  <h3 className="font-medium mb-2">{isRTL ? 'المراجعة والموافقة' : 'Review and Approval'}</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm text-gray-500">{isRTL ? 'تمت المراجعة بواسطة' : 'Reviewed By'}</p>
                      <p className="font-medium">{selectedReview.reviewed_by} - {selectedReview.review_date}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">{isRTL ? 'تمت الموافقة بواسطة' : 'Approved By'}</p>
                      <p className="font-medium">{selectedReview.approved_by} - {selectedReview.approval_date}</p>
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
        <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>
              {isRTL ? 'تعديل مراجعة النقل' : 'Edit Transfer Review'}
            </DialogTitle>
          </DialogHeader>
          
          {selectedReview && (
            <div className="space-y-6">
              {/* Basic Info */}
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>{isRTL ? 'اسم العميل' : 'Client Name'}</Label>
                  <Input
                    value={selectedReview.client_name}
                    onChange={(e) => setSelectedReview({ ...selectedReview, client_name: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <Label>{isRTL ? 'جهة الاعتماد السابقة' : 'Existing CB'}</Label>
                  <Input
                    value={selectedReview.existing_cb || ''}
                    onChange={(e) => setSelectedReview({ ...selectedReview, existing_cb: e.target.value })}
                  />
                </div>
              </div>

              {/* Checklist */}
              <div>
                <h3 className="font-medium mb-3">{isRTL ? 'قائمة التحقق' : 'Compliance Checklist'}</h3>
                <div className="border rounded-lg overflow-hidden">
                  <table className="w-full text-sm">
                    <thead className="bg-gray-100">
                      <tr>
                        <th className="text-start p-2">{isRTL ? 'البند' : 'Item'}</th>
                        <th className="text-center p-2 w-32">{isRTL ? 'الإجابة' : 'Answer'}</th>
                      </tr>
                    </thead>
                    <tbody>
                      {checklistItems.map((item) => (
                        <tr key={item.key} className="border-t">
                          <td className="p-2 text-sm">{isRTL ? item.label_ar : item.label}</td>
                          <td className="p-2">
                            <Select
                              value={
                                selectedReview.checklist?.[item.key] === true ? 'yes' :
                                selectedReview.checklist?.[item.key] === false ? 'no' : 'na'
                              }
                              onValueChange={(v) => updateChecklist(item.key, v === 'yes' ? true : v === 'no' ? false : null)}
                            >
                              <SelectTrigger className="h-8">
                                <SelectValue />
                              </SelectTrigger>
                              <SelectContent>
                                <SelectItem value="yes">Yes</SelectItem>
                                <SelectItem value="no">No</SelectItem>
                                <SelectItem value="na">N/A</SelectItem>
                              </SelectContent>
                            </Select>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Attachments */}
              <div className="grid grid-cols-2 gap-4">
                <label className="flex items-center gap-2 cursor-pointer">
                  <Checkbox
                    checked={selectedReview.has_previous_audit_report}
                    onCheckedChange={(checked) => setSelectedReview({ ...selectedReview, has_previous_audit_report: checked })}
                  />
                  <span className="text-sm">{isRTL ? 'تقرير التدقيق السابق متوفر' : 'Previous audit report available'}</span>
                </label>
                <label className="flex items-center gap-2 cursor-pointer">
                  <Checkbox
                    checked={selectedReview.has_previous_certificates}
                    onCheckedChange={(checked) => setSelectedReview({ ...selectedReview, has_previous_certificates: checked })}
                  />
                  <span className="text-sm">{isRTL ? 'نسخ الشهادات السابقة متوفرة' : 'Previous certificates available'}</span>
                </label>
              </div>

              {/* Certification Cycle Stage */}
              <div className="space-y-2">
                <Label>{isRTL ? 'مرحلة دورة الاعتماد الحالية' : 'Current Certification Cycle Stage'}</Label>
                <Input
                  value={selectedReview.certification_cycle_stage || ''}
                  onChange={(e) => setSelectedReview({ ...selectedReview, certification_cycle_stage: e.target.value })}
                  placeholder={isRTL ? 'مثال: بعد تدقيق المراقبة الأول' : 'e.g., After 1st Surveillance Audit'}
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

      {/* Decision Modal */}
      <Dialog open={showDecisionModal} onOpenChange={setShowDecisionModal}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>
              {isRTL ? 'قرار النقل' : 'Transfer Decision'}
            </DialogTitle>
          </DialogHeader>
          
          <div className="space-y-4">
            <div className="space-y-3">
              <Label>{isRTL ? 'اختر القرار' : 'Select Decision'}</Label>
              
              <label className="flex items-center gap-3 p-3 border rounded-lg cursor-pointer hover:bg-green-50">
                <input
                  type="radio"
                  name="decision"
                  checked={decisionData.transfer_decision === 'approved'}
                  onChange={() => setDecisionData({ ...decisionData, transfer_decision: 'approved' })}
                  className="w-4 h-4"
                />
                <CheckCircle className="w-5 h-5 text-green-600" />
                <span>{isRTL ? 'الموافقة على النقل' : 'Approve Transfer'}</span>
              </label>
              
              <label className="flex items-center gap-3 p-3 border rounded-lg cursor-pointer hover:bg-red-50">
                <input
                  type="radio"
                  name="decision"
                  checked={decisionData.transfer_decision === 'rejected'}
                  onChange={() => setDecisionData({ ...decisionData, transfer_decision: 'rejected' })}
                  className="w-4 h-4"
                />
                <XCircle className="w-5 h-5 text-red-600" />
                <span>{isRTL ? 'رفض النقل' : 'Reject Transfer'}</span>
              </label>
            </div>

            {decisionData.transfer_decision === 'rejected' && (
              <div className="space-y-2">
                <Label>{isRTL ? 'سبب الرفض' : 'Reason for Rejection'}</Label>
                <Textarea
                  value={decisionData.decision_reason}
                  onChange={(e) => setDecisionData({ ...decisionData, decision_reason: e.target.value })}
                />
              </div>
            )}

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>{isRTL ? 'تمت المراجعة بواسطة' : 'Reviewed By'}</Label>
                <Input
                  value={decisionData.reviewed_by}
                  onChange={(e) => setDecisionData({ ...decisionData, reviewed_by: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label>{isRTL ? 'تمت الموافقة بواسطة' : 'Approved By'}</Label>
                <Input
                  value={decisionData.approved_by}
                  onChange={(e) => setDecisionData({ ...decisionData, approved_by: e.target.value })}
                />
              </div>
            </div>

            <div className="flex justify-end gap-2">
              <Button variant="outline" onClick={() => setShowDecisionModal(false)}>
                {isRTL ? 'إلغاء' : 'Cancel'}
              </Button>
              <Button onClick={handleMakeDecision} disabled={!decisionData.transfer_decision}>
                {isRTL ? 'تأكيد القرار' : 'Confirm Decision'}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
