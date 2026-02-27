import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import axios from 'axios';
import { 
  ClipboardCheck, Plus, Eye, Edit, Trash2, Download, CheckCircle, XCircle,
  FileCheck, Calendar, User, Building, Tag, Award, AlertTriangle, Clock
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

export default function TechnicalReviewPage() {
  const { t, i18n } = useTranslation();
  const isRTL = i18n.language === 'ar';
  
  const [reviewsList, setReviewsList] = useState([]);
  const [stage2Reports, setStage2Reports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showViewModal, setShowViewModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDecisionModal, setShowDecisionModal] = useState(false);
  const [showApproveModal, setShowApproveModal] = useState(false);
  const [selectedReview, setSelectedReview] = useState(null);
  
  const [createMode, setCreateMode] = useState('stage2'); // 'stage2' or 'manual'
  const [selectedReportId, setSelectedReportId] = useState('');
  const [formData, setFormData] = useState({
    client_name: '',
    client_name_ar: '',
    location: '',
    scope: '',
    ea_code: '',
    standards: [],
    audit_type: '',
    audit_dates: '',
    audit_team_members: [],
    technical_expert: ''
  });

  const [decisionData, setDecisionData] = useState({
    certification_decision: '',
    decision_comments: ''
  });

  const [approvalData, setApprovalData] = useState({
    approved_by: '',
    approval_date: new Date().toISOString().split('T')[0]
  });

  const token = localStorage.getItem('token');
  const headers = { Authorization: `Bearer ${token}` };

  const auditTypes = [
    { value: 'CA', label: 'CA - Certification Audit', label_ar: 'تدقيق الاعتماد' },
    { value: 'SA', label: 'SA - Surveillance Audit', label_ar: 'تدقيق المراقبة' },
    { value: 'RA', label: 'RA - Recertification Audit', label_ar: 'تدقيق إعادة الاعتماد' },
    { value: 'TF', label: 'TF - Transfer Audit', label_ar: 'تدقيق النقل' },
    { value: 'SP', label: 'SP - Special Audit', label_ar: 'تدقيق خاص' }
  ];

  const standardOptions = [
    'ISO 9001:2015',
    'ISO 14001:2015',
    'ISO 45001:2018',
    'ISO 22000:2018',
    'ISO 27001:2022'
  ];

  useEffect(() => {
    fetchReviews();
    fetchStage2Reports();
  }, []);

  const fetchReviews = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/technical-reviews`, { headers });
      setReviewsList(response.data);
    } catch (error) {
      console.error('Error fetching technical reviews:', error);
      toast.error(isRTL ? 'خطأ في جلب المراجعات الفنية' : 'Error fetching technical reviews');
    } finally {
      setLoading(false);
    }
  };

  const fetchStage2Reports = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/stage2-audit-reports`, { headers });
      setStage2Reports(response.data.filter(r => r.status === 'approved'));
    } catch (error) {
      console.error('Error fetching Stage 2 reports:', error);
    }
  };

  const handleCreate = async () => {
    try {
      const payload = {
        stage2_report_id: createMode === 'stage2' ? selectedReportId : '',
        ...formData
      };
      
      if (!payload.client_name) {
        toast.error(isRTL ? 'اسم العميل مطلوب' : 'Client name is required');
        return;
      }
      
      await axios.post(`${API_URL}/api/technical-reviews`, payload, { headers });
      toast.success(isRTL ? 'تم إنشاء المراجعة الفنية' : 'Technical review created');
      setShowCreateModal(false);
      resetForm();
      fetchReviews();
    } catch (error) {
      console.error('Error creating technical review:', error);
      toast.error(isRTL ? 'خطأ في إنشاء المراجعة الفنية' : 'Error creating technical review');
    }
  };

  const handleUpdate = async () => {
    if (!selectedReview) return;
    
    try {
      await axios.put(`${API_URL}/api/technical-reviews/${selectedReview.id}`, selectedReview, { headers });
      toast.success(isRTL ? 'تم تحديث المراجعة الفنية' : 'Technical review updated');
      setShowEditModal(false);
      fetchReviews();
    } catch (error) {
      console.error('Error updating technical review:', error);
      toast.error(isRTL ? 'خطأ في تحديث المراجعة الفنية' : 'Error updating technical review');
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm(isRTL ? 'هل أنت متأكد من الحذف؟' : 'Are you sure you want to delete?')) return;
    
    try {
      await axios.delete(`${API_URL}/api/technical-reviews/${id}`, { headers });
      toast.success(isRTL ? 'تم حذف المراجعة الفنية' : 'Technical review deleted');
      fetchReviews();
    } catch (error) {
      console.error('Error deleting technical review:', error);
      toast.error(isRTL ? 'خطأ في حذف المراجعة الفنية' : 'Error deleting technical review');
    }
  };

  const handleMakeDecision = async () => {
    if (!selectedReview || !decisionData.certification_decision) return;
    
    try {
      await axios.post(`${API_URL}/api/technical-reviews/${selectedReview.id}/make-decision`, decisionData, { headers });
      toast.success(isRTL ? 'تم تسجيل القرار' : 'Decision recorded');
      setShowDecisionModal(false);
      fetchReviews();
    } catch (error) {
      console.error('Error making decision:', error);
      toast.error(isRTL ? 'خطأ في تسجيل القرار' : 'Error recording decision');
    }
  };

  const handleApprove = async () => {
    if (!selectedReview) return;
    
    try {
      const response = await axios.post(`${API_URL}/api/technical-reviews/${selectedReview.id}/approve`, approvalData, { headers });
      
      if (response.data.certificate) {
        toast.success(
          isRTL 
            ? `تمت الموافقة وإصدار الشهادة رقم ${response.data.certificate.certificate_number}` 
            : `Approved and certificate ${response.data.certificate.certificate_number} issued`
        );
      } else {
        toast.success(isRTL ? 'تمت الموافقة' : 'Approved');
      }
      
      setShowApproveModal(false);
      fetchReviews();
    } catch (error) {
      console.error('Error approving:', error);
      toast.error(isRTL ? 'خطأ في الموافقة' : 'Error approving');
    }
  };

  const handleDownloadPDF = async (id) => {
    try {
      const response = await axios.get(`${API_URL}/api/technical-reviews/${id}/pdf`, {
        headers,
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `technical_review_${id.substring(0, 8)}.pdf`);
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
      location: '',
      scope: '',
      ea_code: '',
      standards: [],
      audit_type: '',
      audit_dates: '',
      audit_team_members: [],
      technical_expert: ''
    });
    setSelectedReportId('');
    setCreateMode('stage2');
  };

  const handleReportSelect = async (reportId) => {
    setSelectedReportId(reportId);
    const report = stage2Reports.find(r => r.id === reportId);
    if (report) {
      setFormData({
        client_name: report.client_name || '',
        client_name_ar: report.client_name_ar || '',
        location: report.location || '',
        scope: report.scope || '',
        ea_code: report.ea_code || '',
        standards: report.standards || [],
        audit_type: report.audit_type || '',
        audit_dates: report.audit_dates || '',
        audit_team_members: report.team_leader ? [report.team_leader, ...(report.team_members || [])] : [],
        technical_expert: report.technical_expert || ''
      });
    }
  };

  const updateChecklistItem = (index, field, value) => {
    if (!selectedReview) return;
    const newChecklist = [...selectedReview.checklist_items];
    newChecklist[index] = { ...newChecklist[index], [field]: value };
    setSelectedReview({ ...selectedReview, checklist_items: newChecklist });
  };

  const getStatusBadge = (status) => {
    const statusConfig = {
      draft: { bg: 'bg-gray-100', text: 'text-gray-700', label: isRTL ? 'مسودة' : 'Draft' },
      under_review: { bg: 'bg-blue-100', text: 'text-blue-700', label: isRTL ? 'قيد المراجعة' : 'Under Review' },
      decision_made: { bg: 'bg-yellow-100', text: 'text-yellow-700', label: isRTL ? 'تم اتخاذ القرار' : 'Decision Made' },
      approved: { bg: 'bg-green-100', text: 'text-green-700', label: isRTL ? 'معتمد' : 'Approved' },
      certificate_issued: { bg: 'bg-purple-100', text: 'text-purple-700', label: isRTL ? 'تم إصدار الشهادة' : 'Certificate Issued' }
    };
    const config = statusConfig[status] || statusConfig.draft;
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${config.bg} ${config.text}`}>
        {config.label}
      </span>
    );
  };

  const getDecisionBadge = (decision) => {
    if (!decision) return null;
    const decisionConfig = {
      issue_certificate: { bg: 'bg-green-100', text: 'text-green-700', label: isRTL ? 'إصدار الشهادة' : 'Issue Certificate', icon: CheckCircle },
      reject_certificate: { bg: 'bg-red-100', text: 'text-red-700', label: isRTL ? 'رفض الشهادة' : 'Reject Certificate', icon: XCircle },
      needs_review: { bg: 'bg-orange-100', text: 'text-orange-700', label: isRTL ? 'يحتاج مراجعة' : 'Needs Review', icon: AlertTriangle }
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
    underReview: reviewsList.filter(r => r.status === 'under_review').length,
    decisionMade: reviewsList.filter(r => r.status === 'decision_made').length,
    certificateIssued: reviewsList.filter(r => r.status === 'certificate_issued').length
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
            {isRTL ? 'المراجعة الفنية وقرار الاعتماد' : 'Technical Review & Certification Decision'}
          </h1>
          <p className="text-sm text-gray-500">
            BAC-F6-15 - {isRTL ? 'مراجعة شاملة للتدقيق وقرار الاعتماد' : 'Comprehensive audit review and certification decision'}
          </p>
        </div>
        <Button onClick={() => setShowCreateModal(true)} className="flex items-center gap-2">
          <Plus className="w-4 h-4" />
          {isRTL ? 'إنشاء مراجعة فنية' : 'Create Technical Review'}
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">{isRTL ? 'إجمالي السجلات' : 'Total Records'}</p>
                <p className="text-2xl font-bold text-primary">{stats.total}</p>
              </div>
              <ClipboardCheck className="w-8 h-8 text-gray-300" />
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
              <FileCheck className="w-8 h-8 text-gray-300" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">{isRTL ? 'قيد المراجعة' : 'Under Review'}</p>
                <p className="text-2xl font-bold text-blue-600">{stats.underReview}</p>
              </div>
              <Clock className="w-8 h-8 text-blue-300" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">{isRTL ? 'تم اتخاذ القرار' : 'Decision Made'}</p>
                <p className="text-2xl font-bold text-yellow-600">{stats.decisionMade}</p>
              </div>
              <AlertTriangle className="w-8 h-8 text-yellow-300" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">{isRTL ? 'تم إصدار الشهادة' : 'Certificate Issued'}</p>
                <p className="text-2xl font-bold text-purple-600">{stats.certificateIssued}</p>
              </div>
              <Award className="w-8 h-8 text-purple-300" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Reviews Table */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <ClipboardCheck className="w-5 h-5" />
            {isRTL ? 'جميع سجلات المراجعة الفنية' : 'All Technical Review Records'}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto" dir={isRTL ? 'rtl' : 'ltr'}>
            <table className="w-full table-fixed">
              <thead>
                <tr className={`border-b bg-gray-50 ${isRTL ? 'text-right' : 'text-left'}`}>
                  <th className={`p-3 px-4 font-medium w-[180px] ${isRTL ? 'text-right' : 'text-left'}`}>{isRTL ? 'اسم العميل' : 'Client Name'}</th>
                  <th className={`p-3 px-4 font-medium w-[140px] ${isRTL ? 'text-right' : 'text-left'}`}>{isRTL ? 'المعايير' : 'Standards'}</th>
                  <th className={`p-3 px-4 font-medium w-[100px] ${isRTL ? 'text-right' : 'text-left'}`}>{isRTL ? 'نوع التدقيق' : 'Audit Type'}</th>
                  <th className={`p-3 px-4 font-medium w-[100px] ${isRTL ? 'text-right' : 'text-left'}`}>{isRTL ? 'الحالة' : 'Status'}</th>
                  <th className={`p-3 px-4 font-medium w-[100px] ${isRTL ? 'text-right' : 'text-left'}`}>{isRTL ? 'القرار' : 'Decision'}</th>
                  <th className={`p-3 px-4 font-medium w-[120px] ${isRTL ? 'text-right' : 'text-left'}`}>{isRTL ? 'رقم الشهادة' : 'Cert. No.'}</th>
                  <th className={`p-3 px-4 font-medium w-[150px] ${isRTL ? 'text-right' : 'text-left'}`}>{isRTL ? 'الإجراءات' : 'Actions'}</th>
                </tr>
              </thead>
              <tbody>
                {reviewsList.map((review) => (
                  <tr key={review.id} className="border-b hover:bg-gray-50">
                    <td className="p-3 px-4">
                      <div className={`font-medium ${isRTL ? 'text-right' : ''}`}>{isRTL ? (review.client_name_ar || review.client_name) : review.client_name}</div>
                      {!isRTL && review.client_name_ar && (
                        <div className="text-sm text-gray-500">{review.client_name_ar}</div>
                      )}
                    </td>
                    <td className="p-3 px-4">
                      <div className={`flex flex-wrap gap-1 ${isRTL ? 'justify-end' : ''}`}>
                        {(review.standards || []).map((std, idx) => (
                          <span key={idx} className="px-2 py-0.5 bg-blue-50 text-blue-700 rounded text-xs">
                            {std}
                          </span>
                        ))}
                      </div>
                    </td>
                    <td className={`p-3 px-4 ${isRTL ? 'text-right' : ''}`}>{review.audit_type || '-'}</td>
                    <td className={`p-3 px-4 ${isRTL ? 'text-right' : ''}`}>{getStatusBadge(review.status)}</td>
                    <td className={`p-3 px-4 ${isRTL ? 'text-right' : ''}`}>{getDecisionBadge(review.certification_decision)}</td>
                    <td className={`p-3 px-4 ${isRTL ? 'text-right' : ''}`}>
                      {review.certificate_number ? (
                        <span className="px-2 py-1 bg-green-50 text-green-700 rounded text-xs font-mono">
                          {review.certificate_number}
                        </span>
                      ) : '-'}
                    </td>
                    <td className="p-3 px-4">
                      <div className={`flex items-center gap-1 ${isRTL ? 'flex-row-reverse justify-end' : ''}`}>
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
                        {review.status === 'draft' || review.status === 'under_review' ? (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => {
                              setSelectedReview(review);
                              setDecisionData({ certification_decision: '', decision_comments: '' });
                              setShowDecisionModal(true);
                            }}
                            title={isRTL ? 'اتخاذ القرار' : 'Make Decision'}
                            className="text-yellow-600 hover:text-yellow-700"
                          >
                            <CheckCircle className="w-4 h-4" />
                          </Button>
                        ) : null}
                        {review.status === 'decision_made' ? (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => {
                              setSelectedReview(review);
                              setApprovalData({
                                approved_by: '',
                                approval_date: new Date().toISOString().split('T')[0]
                              });
                              setShowApproveModal(true);
                            }}
                            title={isRTL ? 'الموافقة' : 'Approve'}
                            className="text-green-600 hover:text-green-700"
                          >
                            <Award className="w-4 h-4" />
                          </Button>
                        ) : null}
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
                    <td colSpan={7} className="p-8 text-center text-gray-500">
                      {isRTL ? 'لا توجد سجلات' : 'No records found'}
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
              {isRTL ? 'إنشاء مراجعة فنية جديدة' : 'Create New Technical Review'}
            </DialogTitle>
          </DialogHeader>
          
          <div className="space-y-4">
            {/* Creation Mode */}
            <div className="space-y-2">
              <Label>{isRTL ? 'طريقة الإنشاء' : 'Creation Method'}</Label>
              <div className="flex gap-4">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="radio"
                    checked={createMode === 'stage2'}
                    onChange={() => setCreateMode('stage2')}
                    className="w-4 h-4"
                  />
                  <span>{isRTL ? 'من تقرير المرحلة 2' : 'From Stage 2 Report'}</span>
                </label>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="radio"
                    checked={createMode === 'manual'}
                    onChange={() => setCreateMode('manual')}
                    className="w-4 h-4"
                  />
                  <span>{isRTL ? 'إدخال يدوي' : 'Manual Entry'}</span>
                </label>
              </div>
            </div>

            {createMode === 'stage2' && (
              <div className="space-y-2">
                <Label>{isRTL ? 'تقرير تدقيق المرحلة 2' : 'Stage 2 Audit Report'}</Label>
                <Select value={selectedReportId} onValueChange={handleReportSelect}>
                  <SelectTrigger>
                    <SelectValue placeholder={isRTL ? 'اختر التقرير' : 'Select report'} />
                  </SelectTrigger>
                  <SelectContent>
                    {stage2Reports.map(report => (
                      <SelectItem key={report.id} value={report.id}>
                        {report.client_name} - {(report.standards || []).join(', ')}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            )}

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>{isRTL ? 'اسم العميل (إنجليزي)' : 'Client Name (English)'}</Label>
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
            </div>

            <div className="space-y-2">
              <Label>{isRTL ? 'الموقع' : 'Location'}</Label>
              <Input
                value={formData.location}
                onChange={(e) => setFormData({ ...formData, location: e.target.value })}
              />
            </div>

            <div className="space-y-2">
              <Label>{isRTL ? 'نطاق العمل' : 'Scope'}</Label>
              <Textarea
                value={formData.scope}
                onChange={(e) => setFormData({ ...formData, scope: e.target.value })}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>{isRTL ? 'رمز EA' : 'EA Code'}</Label>
                <Input
                  value={formData.ea_code}
                  onChange={(e) => setFormData({ ...formData, ea_code: e.target.value })}
                />
              </div>
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
            </div>

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

            <div className="space-y-2">
              <Label>{isRTL ? 'تاريخ التدقيق' : 'Audit Dates'}</Label>
              <Input
                value={formData.audit_dates}
                onChange={(e) => setFormData({ ...formData, audit_dates: e.target.value })}
                placeholder="e.g., 2026-02-15 to 2026-02-17"
              />
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
              {isRTL ? 'عرض المراجعة الفنية' : 'View Technical Review'}
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
                  <p className="text-sm text-gray-500">{isRTL ? 'المعايير' : 'Standards'}</p>
                  <p className="font-medium">{(selectedReview.standards || []).join(', ')}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">{isRTL ? 'نوع التدقيق' : 'Audit Type'}</p>
                  <p className="font-medium">{selectedReview.audit_type || '-'}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">{isRTL ? 'الحالة' : 'Status'}</p>
                  {getStatusBadge(selectedReview.status)}
                </div>
              </div>

              {/* Decision Section */}
              {selectedReview.certification_decision && (
                <div className="p-4 bg-blue-50 rounded-lg">
                  <h3 className="font-medium mb-2">{isRTL ? 'قرار الاعتماد' : 'Certification Decision'}</h3>
                  <div className="flex items-center gap-4">
                    {getDecisionBadge(selectedReview.certification_decision)}
                    {selectedReview.certificate_number && (
                      <span className="px-3 py-1 bg-green-100 text-green-800 rounded font-mono">
                        {selectedReview.certificate_number}
                      </span>
                    )}
                  </div>
                  {selectedReview.decision_comments && (
                    <p className="mt-2 text-sm text-gray-600">{selectedReview.decision_comments}</p>
                  )}
                </div>
              )}

              {/* Checklist */}
              <div>
                <h3 className="font-medium mb-3">{isRTL ? 'قائمة التقييم' : 'Assessment Checklist'}</h3>
                <div className="border rounded-lg overflow-hidden">
                  <table className="w-full text-sm">
                    <thead className="bg-gray-100">
                      <tr>
                        <th className="text-start p-2">{isRTL ? 'البند' : 'Item'}</th>
                        <th className="text-center p-2 w-20">{isRTL ? 'نعم/لا' : 'Y/N'}</th>
                        <th className="text-start p-2">{isRTL ? 'ملاحظات' : 'Remarks'}</th>
                      </tr>
                    </thead>
                    <tbody>
                      {(selectedReview.checklist_items || []).map((item, idx) => (
                        <tr key={idx} className="border-t">
                          <td className="p-2">
                            <div>{item.item}</div>
                            <div className="text-xs text-gray-500" dir="rtl">{item.item_ar}</div>
                          </td>
                          <td className="p-2 text-center">
                            {item.checked === true && <span className="text-green-600 font-bold">Y</span>}
                            {item.checked === false && <span className="text-red-600 font-bold">N</span>}
                            {item.checked === null && <span className="text-gray-400">-</span>}
                          </td>
                          <td className="p-2 text-gray-600">{item.remarks || '-'}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Approval Info */}
              {selectedReview.approved_by && (
                <div className="p-4 bg-green-50 rounded-lg">
                  <h3 className="font-medium mb-2">{isRTL ? 'الموافقة' : 'Approval'}</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm text-gray-500">{isRTL ? 'الموافق' : 'Approved By'}</p>
                      <p className="font-medium">{selectedReview.approved_by}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">{isRTL ? 'تاريخ الموافقة' : 'Approval Date'}</p>
                      <p className="font-medium">{selectedReview.approval_date}</p>
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
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>
              {isRTL ? 'تعديل المراجعة الفنية' : 'Edit Technical Review'}
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
                  <Label>{isRTL ? 'الموقع' : 'Location'}</Label>
                  <Input
                    value={selectedReview.location}
                    onChange={(e) => setSelectedReview({ ...selectedReview, location: e.target.value })}
                  />
                </div>
              </div>

              {/* Technical Reviewer */}
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>{isRTL ? 'المراجع الفني' : 'Technical Reviewer'}</Label>
                  <Input
                    value={selectedReview.technical_reviewer || ''}
                    onChange={(e) => setSelectedReview({ ...selectedReview, technical_reviewer: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <Label>{isRTL ? 'تاريخ المراجعة' : 'Review Date'}</Label>
                  <Input
                    type="date"
                    value={selectedReview.review_date || ''}
                    onChange={(e) => setSelectedReview({ ...selectedReview, review_date: e.target.value })}
                  />
                </div>
              </div>

              {/* Checklist */}
              <div>
                <h3 className="font-medium mb-3">{isRTL ? 'قائمة التقييم' : 'Assessment Checklist'}</h3>
                <div className="border rounded-lg overflow-hidden max-h-96 overflow-y-auto">
                  <table className="w-full text-sm">
                    <thead className="bg-gray-100 sticky top-0">
                      <tr>
                        <th className="text-start p-2">{isRTL ? 'البند' : 'Item'}</th>
                        <th className="text-center p-2 w-24">{isRTL ? 'نعم/لا' : 'Y/N'}</th>
                        <th className="text-start p-2 w-48">{isRTL ? 'ملاحظات' : 'Remarks'}</th>
                      </tr>
                    </thead>
                    <tbody>
                      {(selectedReview.checklist_items || []).map((item, idx) => (
                        <tr key={idx} className="border-t">
                          <td className="p-2">
                            <div className="text-sm">{item.item}</div>
                          </td>
                          <td className="p-2">
                            <Select
                              value={item.checked === true ? 'yes' : item.checked === false ? 'no' : 'na'}
                              onValueChange={(v) => updateChecklistItem(idx, 'checked', v === 'yes' ? true : v === 'no' ? false : null)}
                            >
                              <SelectTrigger className="h-8">
                                <SelectValue />
                              </SelectTrigger>
                              <SelectContent>
                                <SelectItem value="yes">Y</SelectItem>
                                <SelectItem value="no">N</SelectItem>
                                <SelectItem value="na">-</SelectItem>
                              </SelectContent>
                            </Select>
                          </td>
                          <td className="p-2">
                            <Input
                              className="h-8 text-sm"
                              value={item.remarks || ''}
                              onChange={(e) => updateChecklistItem(idx, 'remarks', e.target.value)}
                              placeholder={isRTL ? 'ملاحظات' : 'Remarks'}
                            />
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
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
              {isRTL ? 'قرار الاعتماد' : 'Certification Decision'}
            </DialogTitle>
          </DialogHeader>
          
          <div className="space-y-4">
            <div className="space-y-3">
              <Label>{isRTL ? 'اختر القرار' : 'Select Decision'}</Label>
              
              <label className="flex items-center gap-3 p-3 border rounded-lg cursor-pointer hover:bg-green-50">
                <input
                  type="radio"
                  name="decision"
                  checked={decisionData.certification_decision === 'issue_certificate'}
                  onChange={() => setDecisionData({ ...decisionData, certification_decision: 'issue_certificate' })}
                  className="w-4 h-4"
                />
                <CheckCircle className="w-5 h-5 text-green-600" />
                <span>{isRTL ? 'إصدار الشهادة' : 'Issue Certificate'}</span>
              </label>
              
              <label className="flex items-center gap-3 p-3 border rounded-lg cursor-pointer hover:bg-red-50">
                <input
                  type="radio"
                  name="decision"
                  checked={decisionData.certification_decision === 'reject_certificate'}
                  onChange={() => setDecisionData({ ...decisionData, certification_decision: 'reject_certificate' })}
                  className="w-4 h-4"
                />
                <XCircle className="w-5 h-5 text-red-600" />
                <span>{isRTL ? 'رفض الشهادة' : 'Reject Certificate'}</span>
              </label>
              
              <label className="flex items-center gap-3 p-3 border rounded-lg cursor-pointer hover:bg-orange-50">
                <input
                  type="radio"
                  name="decision"
                  checked={decisionData.certification_decision === 'needs_review'}
                  onChange={() => setDecisionData({ ...decisionData, certification_decision: 'needs_review' })}
                  className="w-4 h-4"
                />
                <AlertTriangle className="w-5 h-5 text-orange-600" />
                <span>{isRTL ? 'يحتاج مراجعة فنية إضافية' : 'Needs Further Technical Review'}</span>
              </label>
            </div>

            <div className="space-y-2">
              <Label>{isRTL ? 'ملاحظات القرار' : 'Decision Comments'}</Label>
              <Textarea
                value={decisionData.decision_comments}
                onChange={(e) => setDecisionData({ ...decisionData, decision_comments: e.target.value })}
                placeholder={isRTL ? 'أضف ملاحظات...' : 'Add comments...'}
              />
            </div>

            <div className="flex justify-end gap-2">
              <Button variant="outline" onClick={() => setShowDecisionModal(false)}>
                {isRTL ? 'إلغاء' : 'Cancel'}
              </Button>
              <Button onClick={handleMakeDecision} disabled={!decisionData.certification_decision}>
                {isRTL ? 'تأكيد القرار' : 'Confirm Decision'}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* Approve Modal */}
      <Dialog open={showApproveModal} onOpenChange={setShowApproveModal}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>
              {isRTL ? 'الموافقة على المراجعة الفنية' : 'Approve Technical Review'}
            </DialogTitle>
          </DialogHeader>
          
          {selectedReview && (
            <div className="space-y-4">
              {selectedReview.certification_decision === 'issue_certificate' && (
                <div className="p-3 bg-green-50 border border-green-200 rounded-lg">
                  <p className="text-green-800 text-sm">
                    {isRTL 
                      ? 'سيتم إصدار الشهادة تلقائياً عند الموافقة' 
                      : 'Certificate will be automatically issued upon approval'}
                  </p>
                </div>
              )}

              <div className="space-y-2">
                <Label>{isRTL ? 'الموافق' : 'Approved By'}</Label>
                <Input
                  value={approvalData.approved_by}
                  onChange={(e) => setApprovalData({ ...approvalData, approved_by: e.target.value })}
                  placeholder={isRTL ? 'اسم الموافق' : 'Approver name'}
                />
              </div>

              <div className="space-y-2">
                <Label>{isRTL ? 'تاريخ الموافقة' : 'Approval Date'}</Label>
                <Input
                  type="date"
                  value={approvalData.approval_date}
                  onChange={(e) => setApprovalData({ ...approvalData, approval_date: e.target.value })}
                />
              </div>

              <div className="flex justify-end gap-2">
                <Button variant="outline" onClick={() => setShowApproveModal(false)}>
                  {isRTL ? 'إلغاء' : 'Cancel'}
                </Button>
                <Button onClick={handleApprove} className="bg-green-600 hover:bg-green-700">
                  {isRTL ? 'موافقة' : 'Approve'}
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
