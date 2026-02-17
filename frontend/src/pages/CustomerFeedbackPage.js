import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import axios from 'axios';
import { 
  MessageSquare, Plus, Eye, Edit, Trash2, Download, Send, CheckCircle,
  Star, Calendar, User, Building, ExternalLink, ClipboardCheck
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

export default function CustomerFeedbackPage() {
  const { t, i18n } = useTranslation();
  const isRTL = i18n.language === 'ar';
  
  const [feedbackList, setFeedbackList] = useState([]);
  const [certificates, setCertificates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showViewModal, setShowViewModal] = useState(false);
  const [showReviewModal, setShowReviewModal] = useState(false);
  const [selectedFeedback, setSelectedFeedback] = useState(null);
  
  const [formData, setFormData] = useState({
    certificate_id: '',
    organization_name: '',
    organization_name_ar: '',
    audit_type: '',
    standards: [],
    audit_date: '',
    lead_auditor: '',
    auditor: ''
  });

  const [reviewData, setReviewData] = useState({
    reviewed_by: '',
    review_date: new Date().toISOString().split('T')[0],
    review_comments: ''
  });

  const token = localStorage.getItem('token');
  const headers = { Authorization: `Bearer ${token}` };

  const auditTypes = [
    { value: 'Initial', label: 'Initial Certification', label_ar: 'الاعتماد الأولي' },
    { value: '1st Surveillance', label: '1st Surveillance', label_ar: 'المراقبة الأولى' },
    { value: '2nd Surveillance', label: '2nd Surveillance', label_ar: 'المراقبة الثانية' },
    { value: 'Re-Certification', label: 'Re-Certification', label_ar: 'إعادة الاعتماد' }
  ];

  const standardOptions = [
    'ISO 9001:2015',
    'ISO 14001:2015',
    'ISO 45001:2018',
    'ISO 22000:2018',
    'ISO 27001:2022'
  ];

  useEffect(() => {
    fetchFeedback();
    fetchCertificates();
  }, []);

  const fetchFeedback = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/customer-feedback`, { headers });
      setFeedbackList(response.data);
    } catch (error) {
      console.error('Error fetching feedback:', error);
      toast.error(isRTL ? 'خطأ في جلب الملاحظات' : 'Error fetching feedback');
    } finally {
      setLoading(false);
    }
  };

  const fetchCertificates = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/certificates`, { headers });
      setCertificates(response.data.filter(c => c.status === 'active'));
    } catch (error) {
      console.error('Error fetching certificates:', error);
    }
  };

  const handleCreate = async () => {
    try {
      if (!formData.organization_name) {
        toast.error(isRTL ? 'اسم المنظمة مطلوب' : 'Organization name is required');
        return;
      }
      
      const response = await axios.post(`${API_URL}/api/customer-feedback`, formData, { headers });
      toast.success(isRTL ? 'تم إنشاء نموذج الملاحظات' : 'Feedback form created');
      
      // Show the public URL
      const publicUrl = `${window.location.origin}/feedback/${response.data.access_token}`;
      navigator.clipboard.writeText(publicUrl);
      toast.success(isRTL ? 'تم نسخ الرابط العام' : 'Public URL copied to clipboard');
      
      setShowCreateModal(false);
      resetForm();
      fetchFeedback();
    } catch (error) {
      console.error('Error creating feedback:', error);
      toast.error(isRTL ? 'خطأ في إنشاء الملاحظات' : 'Error creating feedback');
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm(isRTL ? 'هل أنت متأكد من الحذف؟' : 'Are you sure you want to delete?')) return;
    
    try {
      await axios.delete(`${API_URL}/api/customer-feedback/${id}`, { headers });
      toast.success(isRTL ? 'تم حذف الملاحظات' : 'Feedback deleted');
      fetchFeedback();
    } catch (error) {
      console.error('Error deleting feedback:', error);
      toast.error(isRTL ? 'خطأ في حذف الملاحظات' : 'Error deleting feedback');
    }
  };

  const handleReview = async () => {
    if (!selectedFeedback) return;
    
    try {
      await axios.post(`${API_URL}/api/customer-feedback/${selectedFeedback.id}/review`, reviewData, { headers });
      toast.success(isRTL ? 'تم مراجعة الملاحظات' : 'Feedback reviewed');
      setShowReviewModal(false);
      fetchFeedback();
    } catch (error) {
      console.error('Error reviewing feedback:', error);
      toast.error(isRTL ? 'خطأ في المراجعة' : 'Error reviewing');
    }
  };

  const handleDownloadPDF = async (id) => {
    try {
      const response = await axios.get(`${API_URL}/api/customer-feedback/${id}/pdf`, {
        headers,
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `customer_feedback_${id.substring(0, 8)}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error('Error downloading PDF:', error);
      toast.error(isRTL ? 'خطأ في تحميل PDF' : 'Error downloading PDF');
    }
  };

  const copyPublicLink = (accessToken) => {
    const publicUrl = `${window.location.origin}/feedback/${accessToken}`;
    navigator.clipboard.writeText(publicUrl);
    toast.success(isRTL ? 'تم نسخ الرابط' : 'Link copied to clipboard');
  };

  const resetForm = () => {
    setFormData({
      certificate_id: '',
      organization_name: '',
      organization_name_ar: '',
      audit_type: '',
      standards: [],
      audit_date: '',
      lead_auditor: '',
      auditor: ''
    });
  };

  const handleCertificateSelect = (certId) => {
    const cert = certificates.find(c => c.id === certId);
    if (cert) {
      setFormData({
        ...formData,
        certificate_id: certId,
        organization_name: cert.organization_name || '',
        organization_name_ar: cert.organization_name_ar || '',
        standards: cert.standards || [],
        lead_auditor: cert.lead_auditor || ''
      });
    }
  };

  const getStatusBadge = (status) => {
    const statusConfig = {
      pending: { bg: 'bg-yellow-100', text: 'text-yellow-700', label: isRTL ? 'قيد الانتظار' : 'Pending' },
      submitted: { bg: 'bg-blue-100', text: 'text-blue-700', label: isRTL ? 'تم التقديم' : 'Submitted' },
      reviewed: { bg: 'bg-green-100', text: 'text-green-700', label: isRTL ? 'تمت المراجعة' : 'Reviewed' }
    };
    const config = statusConfig[status] || statusConfig.pending;
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${config.bg} ${config.text}`}>
        {config.label}
      </span>
    );
  };

  const getScoreBadge = (score, evaluation) => {
    if (!score && score !== 0) return null;
    
    const evalConfig = {
      excellent: { bg: 'bg-green-100', text: 'text-green-700' },
      good: { bg: 'bg-blue-100', text: 'text-blue-700' },
      average: { bg: 'bg-yellow-100', text: 'text-yellow-700' },
      unsatisfactory: { bg: 'bg-red-100', text: 'text-red-700' }
    };
    const config = evalConfig[evaluation] || evalConfig.average;
    
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-bold ${config.bg} ${config.text}`}>
        {score.toFixed(1)}%
      </span>
    );
  };

  const renderStarRating = (rating) => {
    if (!rating) return <span className="text-gray-400">N/A</span>;
    return (
      <div className="flex items-center gap-1">
        {[1, 2, 3, 4, 5].map((star) => (
          <Star
            key={star}
            className={`w-4 h-4 ${star <= rating ? 'fill-yellow-400 text-yellow-400' : 'text-gray-300'}`}
          />
        ))}
        <span className="text-sm text-gray-600 ml-1">({rating}/5)</span>
      </div>
    );
  };

  // Stats
  const stats = {
    total: feedbackList.length,
    pending: feedbackList.filter(f => f.status === 'pending').length,
    submitted: feedbackList.filter(f => f.status === 'submitted').length,
    reviewed: feedbackList.filter(f => f.status === 'reviewed').length,
    avgScore: feedbackList.filter(f => f.overall_score > 0).length > 0
      ? (feedbackList.filter(f => f.overall_score > 0).reduce((sum, f) => sum + f.overall_score, 0) / 
         feedbackList.filter(f => f.overall_score > 0).length).toFixed(1)
      : 0
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
            {isRTL ? 'ملاحظات العملاء' : 'Customer Feedback'}
          </h1>
          <p className="text-sm text-gray-500">
            BAC-F6-16 - {isRTL ? 'استبيان رضا العملاء' : 'Customer Satisfaction Survey'}
          </p>
        </div>
        <Button onClick={() => setShowCreateModal(true)} className="flex items-center gap-2">
          <Plus className="w-4 h-4" />
          {isRTL ? 'إنشاء نموذج ملاحظات' : 'Create Feedback Form'}
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">{isRTL ? 'إجمالي النماذج' : 'Total Forms'}</p>
                <p className="text-2xl font-bold text-primary">{stats.total}</p>
              </div>
              <MessageSquare className="w-8 h-8 text-gray-300" />
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
              <Send className="w-8 h-8 text-yellow-300" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">{isRTL ? 'تم التقديم' : 'Submitted'}</p>
                <p className="text-2xl font-bold text-blue-600">{stats.submitted}</p>
              </div>
              <CheckCircle className="w-8 h-8 text-blue-300" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">{isRTL ? 'تمت المراجعة' : 'Reviewed'}</p>
                <p className="text-2xl font-bold text-green-600">{stats.reviewed}</p>
              </div>
              <ClipboardCheck className="w-8 h-8 text-green-300" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">{isRTL ? 'متوسط التقييم' : 'Avg Score'}</p>
                <p className="text-2xl font-bold text-purple-600">{stats.avgScore}%</p>
              </div>
              <Star className="w-8 h-8 text-purple-300" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Feedback Table */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <MessageSquare className="w-5 h-5" />
            {isRTL ? 'جميع نماذج الملاحظات' : 'All Feedback Forms'}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b bg-gray-50">
                  <th className="text-start p-3 font-medium">{isRTL ? 'المنظمة' : 'Organization'}</th>
                  <th className="text-start p-3 font-medium">{isRTL ? 'نوع التدقيق' : 'Audit Type'}</th>
                  <th className="text-start p-3 font-medium">{isRTL ? 'التاريخ' : 'Date'}</th>
                  <th className="text-start p-3 font-medium">{isRTL ? 'الحالة' : 'Status'}</th>
                  <th className="text-start p-3 font-medium">{isRTL ? 'التقييم' : 'Score'}</th>
                  <th className="text-start p-3 font-medium">{isRTL ? 'الإجراءات' : 'Actions'}</th>
                </tr>
              </thead>
              <tbody>
                {feedbackList.map((feedback) => (
                  <tr key={feedback.id} className="border-b hover:bg-gray-50">
                    <td className="p-3">
                      <div className="font-medium">{feedback.organization_name}</div>
                      <div className="text-sm text-gray-500">{feedback.organization_name_ar}</div>
                    </td>
                    <td className="p-3">{feedback.audit_type || '-'}</td>
                    <td className="p-3">{feedback.audit_date || '-'}</td>
                    <td className="p-3">{getStatusBadge(feedback.status)}</td>
                    <td className="p-3">
                      {feedback.status !== 'pending' 
                        ? getScoreBadge(feedback.overall_score, feedback.evaluation_result)
                        : '-'}
                    </td>
                    <td className="p-3">
                      <div className="flex items-center gap-1">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => {
                            setSelectedFeedback(feedback);
                            setShowViewModal(true);
                          }}
                          title={isRTL ? 'عرض' : 'View'}
                        >
                          <Eye className="w-4 h-4" />
                        </Button>
                        {feedback.status === 'pending' && (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => copyPublicLink(feedback.access_token)}
                            title={isRTL ? 'نسخ الرابط' : 'Copy Link'}
                            className="text-blue-600 hover:text-blue-700"
                          >
                            <ExternalLink className="w-4 h-4" />
                          </Button>
                        )}
                        {feedback.status === 'submitted' && (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => {
                              setSelectedFeedback(feedback);
                              setReviewData({
                                reviewed_by: '',
                                review_date: new Date().toISOString().split('T')[0],
                                review_comments: ''
                              });
                              setShowReviewModal(true);
                            }}
                            title={isRTL ? 'مراجعة' : 'Review'}
                            className="text-green-600 hover:text-green-700"
                          >
                            <ClipboardCheck className="w-4 h-4" />
                          </Button>
                        )}
                        {feedback.status !== 'pending' && (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleDownloadPDF(feedback.id)}
                            title={isRTL ? 'تحميل PDF' : 'Download PDF'}
                            className="text-purple-600 hover:text-purple-700"
                          >
                            <Download className="w-4 h-4" />
                          </Button>
                        )}
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDelete(feedback.id)}
                          title={isRTL ? 'حذف' : 'Delete'}
                          className="text-red-600 hover:text-red-700"
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))}
                {feedbackList.length === 0 && (
                  <tr>
                    <td colSpan={6} className="p-8 text-center text-gray-500">
                      {isRTL ? 'لا توجد نماذج ملاحظات' : 'No feedback forms found'}
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
              {isRTL ? 'إنشاء نموذج ملاحظات جديد' : 'Create New Feedback Form'}
            </DialogTitle>
          </DialogHeader>
          
          <div className="space-y-4">
            {/* Link to Certificate (optional) */}
            <div className="space-y-2">
              <Label>{isRTL ? 'الشهادة (اختياري)' : 'Certificate (Optional)'}</Label>
              <Select value={formData.certificate_id || "none"} onValueChange={handleCertificateSelect}>
                <SelectTrigger>
                  <SelectValue placeholder={isRTL ? 'اختر الشهادة' : 'Select certificate'} />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="none">{isRTL ? 'بدون ربط' : 'No link'}</SelectItem>
                  {certificates.map(cert => (
                    <SelectItem key={cert.id} value={cert.id}>
                      {cert.certificate_number} - {cert.organization_name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>{isRTL ? 'اسم المنظمة (إنجليزي)' : 'Organization Name (English)'} *</Label>
                <Input
                  value={formData.organization_name}
                  onChange={(e) => setFormData({ ...formData, organization_name: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label>{isRTL ? 'اسم المنظمة (عربي)' : 'Organization Name (Arabic)'}</Label>
                <Input
                  value={formData.organization_name_ar}
                  onChange={(e) => setFormData({ ...formData, organization_name_ar: e.target.value })}
                  dir="rtl"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>{isRTL ? 'نوع التدقيق' : 'Audit Type'}</Label>
                <Select
                  value={formData.audit_type}
                  onValueChange={(v) => setFormData({ ...formData, audit_type: v })}
                >
                  <SelectTrigger>
                    <SelectValue placeholder={isRTL ? 'اختر النوع' : 'Select type'} />
                  </SelectTrigger>
                  <SelectContent>
                    {auditTypes.map(type => (
                      <SelectItem key={type.value} value={type.value}>
                        {isRTL ? type.label_ar : type.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label>{isRTL ? 'تاريخ التدقيق' : 'Audit Date'}</Label>
                <Input
                  type="date"
                  value={formData.audit_date}
                  onChange={(e) => setFormData({ ...formData, audit_date: e.target.value })}
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>{isRTL ? 'المدقق الرئيسي' : 'Lead Auditor'}</Label>
                <Input
                  value={formData.lead_auditor}
                  onChange={(e) => setFormData({ ...formData, lead_auditor: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label>{isRTL ? 'المدقق' : 'Auditor'}</Label>
                <Input
                  value={formData.auditor}
                  onChange={(e) => setFormData({ ...formData, auditor: e.target.value })}
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label>{isRTL ? 'المعايير' : 'Standards'}</Label>
              <div className="flex flex-wrap gap-2">
                {standardOptions.map(std => (
                  <label key={std} className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={formData.standards.includes(std)}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setFormData({ ...formData, standards: [...formData.standards, std] });
                        } else {
                          setFormData({ ...formData, standards: formData.standards.filter(s => s !== std) });
                        }
                      }}
                      className="w-4 h-4"
                    />
                    <span className="text-sm">{std}</span>
                  </label>
                ))}
              </div>
            </div>

            <div className="p-3 bg-blue-50 rounded-lg">
              <p className="text-sm text-blue-800">
                {isRTL 
                  ? 'سيتم إنشاء رابط عام لإرساله للعميل لملء الاستبيان' 
                  : 'A public link will be created to send to the client for filling the survey'}
              </p>
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
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>
              {isRTL ? 'عرض الملاحظات' : 'View Feedback'}
            </DialogTitle>
          </DialogHeader>
          
          {selectedFeedback && (
            <div className="space-y-6">
              {/* Organization Info */}
              <div className="grid grid-cols-2 gap-4 p-4 bg-gray-50 rounded-lg">
                <div>
                  <p className="text-sm text-gray-500">{isRTL ? 'المنظمة' : 'Organization'}</p>
                  <p className="font-medium">{selectedFeedback.organization_name}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">{isRTL ? 'نوع التدقيق' : 'Audit Type'}</p>
                  <p className="font-medium">{selectedFeedback.audit_type || '-'}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">{isRTL ? 'المعايير' : 'Standards'}</p>
                  <p className="font-medium">{(selectedFeedback.standards || []).join(', ') || '-'}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">{isRTL ? 'الحالة' : 'Status'}</p>
                  {getStatusBadge(selectedFeedback.status)}
                </div>
              </div>

              {/* Score Summary */}
              {selectedFeedback.status !== 'pending' && (
                <div className="p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-medium mb-1">{isRTL ? 'التقييم العام' : 'Overall Score'}</h3>
                      <p className="text-3xl font-bold text-primary">{selectedFeedback.overall_score?.toFixed(1)}%</p>
                    </div>
                    <div className="text-right">
                      <span className={`px-4 py-2 rounded-full text-sm font-bold ${
                        selectedFeedback.evaluation_result === 'excellent' ? 'bg-green-100 text-green-700' :
                        selectedFeedback.evaluation_result === 'good' ? 'bg-blue-100 text-blue-700' :
                        selectedFeedback.evaluation_result === 'average' ? 'bg-yellow-100 text-yellow-700' :
                        'bg-red-100 text-red-700'
                      }`}>
                        {selectedFeedback.evaluation_result === 'excellent' ? (isRTL ? 'ممتاز' : 'Excellent') :
                         selectedFeedback.evaluation_result === 'good' ? (isRTL ? 'جيد' : 'Good') :
                         selectedFeedback.evaluation_result === 'average' ? (isRTL ? 'متوسط' : 'Average') :
                         (isRTL ? 'غير مرضٍ' : 'Unsatisfactory')}
                      </span>
                    </div>
                  </div>
                </div>
              )}

              {/* Questions & Ratings */}
              {selectedFeedback.status !== 'pending' && selectedFeedback.questions?.length > 0 && (
                <div>
                  <h3 className="font-medium mb-3">{isRTL ? 'تقييمات الأسئلة' : 'Question Ratings'}</h3>
                  <div className="border rounded-lg overflow-hidden">
                    <table className="w-full text-sm">
                      <thead className="bg-gray-100">
                        <tr>
                          <th className="text-start p-2">{isRTL ? 'السؤال' : 'Question'}</th>
                          <th className="text-center p-2 w-40">{isRTL ? 'التقييم' : 'Rating'}</th>
                        </tr>
                      </thead>
                      <tbody>
                        {selectedFeedback.questions.map((q, idx) => (
                          <tr key={idx} className="border-t">
                            <td className="p-2">
                              <div className="text-sm">{q.question}</div>
                              <div className="text-xs text-gray-500" dir="rtl">{q.question_ar}</div>
                            </td>
                            <td className="p-2 text-center">
                              {renderStarRating(q.rating)}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* Additional Info */}
              {selectedFeedback.status !== 'pending' && (
                <div className="grid grid-cols-2 gap-4">
                  <div className="p-3 bg-gray-50 rounded-lg">
                    <p className="text-sm text-gray-500">{isRTL ? 'هل تريد نفس الفريق؟' : 'Want Same Team?'}</p>
                    <p className="font-medium">
                      {selectedFeedback.want_same_team === true ? (isRTL ? 'نعم' : 'Yes') :
                       selectedFeedback.want_same_team === false ? (isRTL ? 'لا' : 'No') : '-'}
                    </p>
                  </div>
                  <div className="p-3 bg-gray-50 rounded-lg">
                    <p className="text-sm text-gray-500">{isRTL ? 'المستجيب' : 'Respondent'}</p>
                    <p className="font-medium">{selectedFeedback.respondent_name || '-'}</p>
                    <p className="text-sm text-gray-500">{selectedFeedback.respondent_designation}</p>
                  </div>
                </div>
              )}

              {/* Suggestions */}
              {selectedFeedback.suggestions && (
                <div className="p-3 bg-yellow-50 rounded-lg">
                  <p className="text-sm text-gray-500 mb-1">{isRTL ? 'اقتراحات' : 'Suggestions'}</p>
                  <p className="text-gray-700">{selectedFeedback.suggestions}</p>
                </div>
              )}

              {/* Review Info */}
              {selectedFeedback.reviewed_by && (
                <div className="p-3 bg-green-50 rounded-lg">
                  <p className="text-sm text-gray-500 mb-1">{isRTL ? 'المراجعة' : 'Review'}</p>
                  <p className="font-medium">{selectedFeedback.reviewed_by} - {selectedFeedback.review_date}</p>
                  {selectedFeedback.review_comments && (
                    <p className="text-sm text-gray-600 mt-1">{selectedFeedback.review_comments}</p>
                  )}
                </div>
              )}
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* Review Modal */}
      <Dialog open={showReviewModal} onOpenChange={setShowReviewModal}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>
              {isRTL ? 'مراجعة الملاحظات' : 'Review Feedback'}
            </DialogTitle>
          </DialogHeader>
          
          <div className="space-y-4">
            <div className="space-y-2">
              <Label>{isRTL ? 'المراجع' : 'Reviewed By'}</Label>
              <Input
                value={reviewData.reviewed_by}
                onChange={(e) => setReviewData({ ...reviewData, reviewed_by: e.target.value })}
              />
            </div>

            <div className="space-y-2">
              <Label>{isRTL ? 'تاريخ المراجعة' : 'Review Date'}</Label>
              <Input
                type="date"
                value={reviewData.review_date}
                onChange={(e) => setReviewData({ ...reviewData, review_date: e.target.value })}
              />
            </div>

            <div className="space-y-2">
              <Label>{isRTL ? 'ملاحظات المراجعة' : 'Review Comments'}</Label>
              <Textarea
                value={reviewData.review_comments}
                onChange={(e) => setReviewData({ ...reviewData, review_comments: e.target.value })}
                placeholder={isRTL ? 'أضف ملاحظاتك...' : 'Add your comments...'}
              />
            </div>

            <div className="flex justify-end gap-2">
              <Button variant="outline" onClick={() => setShowReviewModal(false)}>
                {isRTL ? 'إلغاء' : 'Cancel'}
              </Button>
              <Button onClick={handleReview} className="bg-green-600 hover:bg-green-700">
                {isRTL ? 'إكمال المراجعة' : 'Complete Review'}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
