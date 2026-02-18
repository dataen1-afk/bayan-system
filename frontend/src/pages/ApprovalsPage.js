import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import axios from 'axios';
import { 
  CheckCircle2, 
  XCircle, 
  Clock, 
  FileText,
  Users,
  Calendar,
  Filter,
  Search,
  RefreshCw,
  ChevronRight,
  AlertCircle,
  CheckCheck,
  ArrowRight,
  MessageSquare,
  Loader2,
  BarChart3
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
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

const ApprovalsPage = () => {
  const { t, i18n } = useTranslation();
  const isRTL = i18n.language?.startsWith('ar');
  
  const [workflows, setWorkflows] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('all');
  const [typeFilter, setTypeFilter] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedWorkflow, setSelectedWorkflow] = useState(null);
  const [viewDialogOpen, setViewDialogOpen] = useState(false);
  const [decisionDialogOpen, setDecisionDialogOpen] = useState(false);
  const [decisionType, setDecisionType] = useState('');
  const [comments, setComments] = useState('');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    loadData();
  }, [statusFilter, typeFilter]);

  const loadData = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (statusFilter !== 'all') params.append('status', statusFilter);
      if (typeFilter !== 'all') params.append('document_type', typeFilter);
      
      const [workflowsRes, statsRes] = await Promise.all([
        axios.get(`${API}/approvals?${params.toString()}`),
        axios.get(`${API}/approvals/stats`)
      ]);
      
      setWorkflows(workflowsRes.data);
      setStats(statsRes.data);
    } catch (error) {
      console.error('Error loading approvals:', error);
      toast.error(isRTL ? 'خطأ في تحميل البيانات' : 'Error loading data');
    } finally {
      setLoading(false);
    }
  };

  const submitDecision = async () => {
    if (!selectedWorkflow || !decisionType) return;
    
    setSubmitting(true);
    try {
      await axios.post(`${API}/approvals/${selectedWorkflow.id}/decide`, {
        status: decisionType,
        comments: comments,
        comments_ar: comments
      });
      
      toast.success(
        decisionType === 'approved'
          ? (isRTL ? 'تمت الموافقة بنجاح' : 'Approved successfully')
          : (isRTL ? 'تم الرفض' : 'Rejected')
      );
      
      setDecisionDialogOpen(false);
      setViewDialogOpen(false);
      setComments('');
      setDecisionType('');
      loadData();
    } catch (error) {
      console.error('Error submitting decision:', error);
      toast.error(isRTL ? 'خطأ في إرسال القرار' : 'Error submitting decision');
    } finally {
      setSubmitting(false);
    }
  };

  const getStatusBadge = (status) => {
    const statusConfig = {
      'in_progress': { color: 'bg-yellow-100 text-yellow-800', icon: Clock, label: isRTL ? 'قيد التنفيذ' : 'In Progress' },
      'approved': { color: 'bg-green-100 text-green-800', icon: CheckCircle2, label: isRTL ? 'تمت الموافقة' : 'Approved' },
      'rejected': { color: 'bg-red-100 text-red-800', icon: XCircle, label: isRTL ? 'مرفوض' : 'Rejected' },
      'cancelled': { color: 'bg-gray-100 text-gray-800', icon: XCircle, label: isRTL ? 'ملغي' : 'Cancelled' },
      'pending': { color: 'bg-blue-100 text-blue-800', icon: Clock, label: isRTL ? 'في انتظار' : 'Pending' },
    };
    const config = statusConfig[status] || statusConfig['pending'];
    const Icon = config.icon;
    return (
      <Badge className={`${config.color} flex items-center gap-1`}>
        <Icon className="w-3 h-3" />
        {config.label}
      </Badge>
    );
  };

  const getDocumentTypeLabel = (type) => {
    const labels = {
      'contract_review': isRTL ? 'مراجعة العقد' : 'Contract Review',
      'job_order': isRTL ? 'أمر العمل' : 'Job Order',
      'audit_plan': isRTL ? 'خطة التدقيق' : 'Audit Plan',
      'technical_review': isRTL ? 'المراجعة الفنية' : 'Technical Review',
      'certificate': isRTL ? 'الشهادة' : 'Certificate',
      'pre_transfer': isRTL ? 'ما قبل النقل' : 'Pre-Transfer'
    };
    return labels[type] || type;
  };

  const formatDate = (dateString) => {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString(isRTL ? 'ar-SA' : 'en-GB', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const filteredWorkflows = workflows.filter(wf => {
    if (!searchQuery) return true;
    const query = searchQuery.toLowerCase();
    return (
      wf.document_name?.toLowerCase().includes(query) ||
      wf.requested_by_name?.toLowerCase().includes(query)
    );
  });

  const openDecisionDialog = (type) => {
    setDecisionType(type);
    setDecisionDialogOpen(true);
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className={`flex items-center justify-between ${isRTL ? 'flex-row-reverse' : ''}`}>
        <div>
          <h1 className={`text-2xl font-bold text-gray-900 ${isRTL ? 'text-right' : ''}`}>
            {isRTL ? 'إدارة الموافقات' : 'Approval Management'}
          </h1>
          <p className={`text-gray-500 mt-1 ${isRTL ? 'text-right' : ''}`}>
            {isRTL ? 'سير عمل الموافقات متعددة المستويات' : 'Multi-level approval workflows'}
          </p>
        </div>
        <Button variant="outline" onClick={loadData} disabled={loading}>
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''} ${isRTL ? 'ml-2' : 'mr-2'}`} />
          {isRTL ? 'تحديث' : 'Refresh'}
        </Button>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          <div className="bg-white rounded-lg p-4 border shadow-sm">
            <div className={`flex items-center gap-3 ${isRTL ? 'flex-row-reverse' : ''}`}>
              <div className="p-2 bg-gray-100 rounded-lg">
                <FileText className="w-5 h-5 text-gray-600" />
              </div>
              <div className={isRTL ? 'text-right' : ''}>
                <p className="text-sm text-gray-500">{isRTL ? 'الإجمالي' : 'Total'}</p>
                <p className="text-2xl font-bold text-gray-800">{stats.total}</p>
              </div>
            </div>
          </div>
          <div className="bg-yellow-50 rounded-lg p-4 border border-yellow-100">
            <div className={`flex items-center gap-3 ${isRTL ? 'flex-row-reverse' : ''}`}>
              <div className="p-2 bg-yellow-100 rounded-lg">
                <Clock className="w-5 h-5 text-yellow-600" />
              </div>
              <div className={isRTL ? 'text-right' : ''}>
                <p className="text-sm text-yellow-600">{isRTL ? 'قيد التنفيذ' : 'In Progress'}</p>
                <p className="text-2xl font-bold text-yellow-800">{stats.in_progress}</p>
              </div>
            </div>
          </div>
          <div className="bg-green-50 rounded-lg p-4 border border-green-100">
            <div className={`flex items-center gap-3 ${isRTL ? 'flex-row-reverse' : ''}`}>
              <div className="p-2 bg-green-100 rounded-lg">
                <CheckCircle2 className="w-5 h-5 text-green-600" />
              </div>
              <div className={isRTL ? 'text-right' : ''}>
                <p className="text-sm text-green-600">{isRTL ? 'تمت الموافقة' : 'Approved'}</p>
                <p className="text-2xl font-bold text-green-800">{stats.approved}</p>
              </div>
            </div>
          </div>
          <div className="bg-red-50 rounded-lg p-4 border border-red-100">
            <div className={`flex items-center gap-3 ${isRTL ? 'flex-row-reverse' : ''}`}>
              <div className="p-2 bg-red-100 rounded-lg">
                <XCircle className="w-5 h-5 text-red-600" />
              </div>
              <div className={isRTL ? 'text-right' : ''}>
                <p className="text-sm text-red-600">{isRTL ? 'مرفوض' : 'Rejected'}</p>
                <p className="text-2xl font-bold text-red-800">{stats.rejected}</p>
              </div>
            </div>
          </div>
          <div className="bg-blue-50 rounded-lg p-4 border border-blue-100">
            <div className={`flex items-center gap-3 ${isRTL ? 'flex-row-reverse' : ''}`}>
              <div className="p-2 bg-blue-100 rounded-lg">
                <BarChart3 className="w-5 h-5 text-blue-600" />
              </div>
              <div className={isRTL ? 'text-right' : ''}>
                <p className="text-sm text-blue-600">{isRTL ? 'متوسط الأيام' : 'Avg. Days'}</p>
                <p className="text-2xl font-bold text-blue-800">{stats.average_completion_days}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className={`flex items-center gap-4 ${isRTL ? 'flex-row-reverse' : ''}`}>
        <div className="relative flex-1 max-w-md">
          <Search className={`absolute top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4 ${isRTL ? 'right-3' : 'left-3'}`} />
          <Input
            placeholder={isRTL ? 'البحث...' : 'Search...'}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className={isRTL ? 'pr-10 text-right' : 'pl-10'}
          />
        </div>
        <Select value={statusFilter} onValueChange={setStatusFilter}>
          <SelectTrigger className="w-48">
            <Filter className={`w-4 h-4 ${isRTL ? 'ml-2' : 'mr-2'}`} />
            <SelectValue placeholder={isRTL ? 'الحالة' : 'Status'} />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">{isRTL ? 'الكل' : 'All'}</SelectItem>
            <SelectItem value="in_progress">{isRTL ? 'قيد التنفيذ' : 'In Progress'}</SelectItem>
            <SelectItem value="approved">{isRTL ? 'تمت الموافقة' : 'Approved'}</SelectItem>
            <SelectItem value="rejected">{isRTL ? 'مرفوض' : 'Rejected'}</SelectItem>
          </SelectContent>
        </Select>
        <Select value={typeFilter} onValueChange={setTypeFilter}>
          <SelectTrigger className="w-48">
            <FileText className={`w-4 h-4 ${isRTL ? 'ml-2' : 'mr-2'}`} />
            <SelectValue placeholder={isRTL ? 'النوع' : 'Type'} />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">{isRTL ? 'الكل' : 'All Types'}</SelectItem>
            <SelectItem value="contract_review">{isRTL ? 'مراجعة العقد' : 'Contract Review'}</SelectItem>
            <SelectItem value="job_order">{isRTL ? 'أمر العمل' : 'Job Order'}</SelectItem>
            <SelectItem value="audit_plan">{isRTL ? 'خطة التدقيق' : 'Audit Plan'}</SelectItem>
            <SelectItem value="technical_review">{isRTL ? 'المراجعة الفنية' : 'Technical Review'}</SelectItem>
            <SelectItem value="certificate">{isRTL ? 'الشهادة' : 'Certificate'}</SelectItem>
            <SelectItem value="pre_transfer">{isRTL ? 'ما قبل النقل' : 'Pre-Transfer'}</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Workflows List */}
      <div className="bg-white rounded-lg border shadow-sm overflow-hidden">
        <div className="divide-y divide-gray-200">
          {loading ? (
            <div className="px-4 py-8 text-center text-gray-500">
              <Loader2 className="w-8 h-8 mx-auto mb-3 animate-spin text-gray-400" />
              {isRTL ? 'جاري التحميل...' : 'Loading...'}
            </div>
          ) : filteredWorkflows.length === 0 ? (
            <div className="px-4 py-8 text-center text-gray-500">
              <FileText className="w-12 h-12 mx-auto mb-3 text-gray-300" />
              <p>{isRTL ? 'لا توجد موافقات' : 'No approval workflows found'}</p>
            </div>
          ) : (
            filteredWorkflows.map((workflow) => (
              <div 
                key={workflow.id} 
                className="px-4 py-4 hover:bg-gray-50 cursor-pointer transition-colors"
                onClick={() => { setSelectedWorkflow(workflow); setViewDialogOpen(true); }}
              >
                <div className={`flex items-center gap-4 ${isRTL ? 'flex-row-reverse' : ''}`}>
                  <div className={`flex-1 ${isRTL ? 'text-right' : ''}`}>
                    <div className={`flex items-center gap-2 ${isRTL ? 'flex-row-reverse' : ''}`}>
                      <p className="font-medium text-gray-900">
                        {isRTL ? workflow.document_name_ar || workflow.document_name : workflow.document_name}
                      </p>
                      <Badge variant="outline">{getDocumentTypeLabel(workflow.document_type)}</Badge>
                      {getStatusBadge(workflow.status)}
                    </div>
                    <div className={`flex items-center gap-4 mt-2 text-sm text-gray-500 ${isRTL ? 'flex-row-reverse' : ''}`}>
                      <span className={`flex items-center gap-1 ${isRTL ? 'flex-row-reverse' : ''}`}>
                        <Users className="w-3 h-3" />
                        {workflow.requested_by_name}
                      </span>
                      <span className={`flex items-center gap-1 ${isRTL ? 'flex-row-reverse' : ''}`}>
                        <Calendar className="w-3 h-3" />
                        {formatDate(workflow.created_at)}
                      </span>
                    </div>
                    {/* Approval Progress */}
                    <div className={`flex items-center gap-2 mt-3 ${isRTL ? 'flex-row-reverse' : ''}`}>
                      {workflow.levels?.map((level, idx) => (
                        <React.Fragment key={idx}>
                          <div className={`flex items-center gap-1 px-2 py-1 rounded text-xs ${
                            level.status === 'approved' ? 'bg-green-100 text-green-700' :
                            level.status === 'rejected' ? 'bg-red-100 text-red-700' :
                            level.status === 'pending' && level.level === workflow.current_level ? 'bg-yellow-100 text-yellow-700' :
                            'bg-gray-100 text-gray-500'
                          }`}>
                            {level.status === 'approved' ? <CheckCircle2 className="w-3 h-3" /> :
                             level.status === 'rejected' ? <XCircle className="w-3 h-3" /> :
                             <Clock className="w-3 h-3" />}
                            <span>{isRTL ? level.role_ar || level.role : level.role}</span>
                          </div>
                          {idx < workflow.levels.length - 1 && (
                            <ArrowRight className={`w-4 h-4 text-gray-300 ${isRTL ? 'rotate-180' : ''}`} />
                          )}
                        </React.Fragment>
                      ))}
                    </div>
                  </div>
                  <ChevronRight className={`w-5 h-5 text-gray-400 ${isRTL ? 'rotate-180' : ''}`} />
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* View Workflow Dialog */}
      <Dialog open={viewDialogOpen} onOpenChange={setViewDialogOpen}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className={isRTL ? 'text-right' : ''}>
              {isRTL ? 'تفاصيل الموافقة' : 'Approval Details'}
            </DialogTitle>
          </DialogHeader>
          {selectedWorkflow && (
            <div className="space-y-6">
              {/* Document Info */}
              <div className={`space-y-2 ${isRTL ? 'text-right' : ''}`}>
                <h3 className="font-semibold text-gray-900">
                  {isRTL ? selectedWorkflow.document_name_ar || selectedWorkflow.document_name : selectedWorkflow.document_name}
                </h3>
                <div className={`flex items-center gap-2 ${isRTL ? 'flex-row-reverse' : ''}`}>
                  <Badge variant="outline">{getDocumentTypeLabel(selectedWorkflow.document_type)}</Badge>
                  {getStatusBadge(selectedWorkflow.status)}
                </div>
                <p className="text-sm text-gray-500">
                  {isRTL ? 'طلب بواسطة' : 'Requested by'}: {selectedWorkflow.requested_by_name}
                </p>
                <p className="text-sm text-gray-500">
                  {isRTL ? 'التاريخ' : 'Date'}: {formatDate(selectedWorkflow.created_at)}
                </p>
              </div>

              {/* Approval Levels */}
              <div className="space-y-3">
                <h4 className={`font-medium text-gray-700 ${isRTL ? 'text-right' : ''}`}>
                  {isRTL ? 'مستويات الموافقة' : 'Approval Levels'}
                </h4>
                <div className="space-y-3">
                  {selectedWorkflow.levels?.map((level, idx) => (
                    <div 
                      key={idx} 
                      className={`p-4 rounded-lg border ${
                        level.status === 'approved' ? 'bg-green-50 border-green-200' :
                        level.status === 'rejected' ? 'bg-red-50 border-red-200' :
                        level.level === selectedWorkflow.current_level ? 'bg-yellow-50 border-yellow-200' :
                        'bg-gray-50 border-gray-200'
                      }`}
                    >
                      <div className={`flex items-center justify-between ${isRTL ? 'flex-row-reverse' : ''}`}>
                        <div className={`flex items-center gap-2 ${isRTL ? 'flex-row-reverse' : ''}`}>
                          <span className={`w-6 h-6 rounded-full flex items-center justify-center text-sm font-medium ${
                            level.status === 'approved' ? 'bg-green-200 text-green-700' :
                            level.status === 'rejected' ? 'bg-red-200 text-red-700' :
                            'bg-gray-200 text-gray-600'
                          }`}>
                            {level.level}
                          </span>
                          <span className="font-medium">
                            {isRTL ? level.role_ar || level.role : level.role}
                          </span>
                        </div>
                        {getStatusBadge(level.status)}
                      </div>
                      {level.approver_name && (
                        <p className={`text-sm text-gray-600 mt-2 ${isRTL ? 'text-right' : ''}`}>
                          {isRTL ? 'بواسطة' : 'By'}: {level.approver_name}
                          {level.decision_date && ` - ${level.decision_date}`}
                        </p>
                      )}
                      {level.comments && (
                        <p className={`text-sm text-gray-500 mt-1 ${isRTL ? 'text-right' : ''}`}>
                          {isRTL ? 'التعليق' : 'Comment'}: {level.comments}
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              {/* Action Buttons */}
              {selectedWorkflow.status === 'in_progress' && (
                <div className={`flex gap-2 pt-4 border-t ${isRTL ? 'flex-row-reverse' : ''}`}>
                  <Button 
                    className="flex-1 bg-green-600 hover:bg-green-700"
                    onClick={() => openDecisionDialog('approved')}
                  >
                    <CheckCircle2 className={`w-4 h-4 ${isRTL ? 'ml-2' : 'mr-2'}`} />
                    {isRTL ? 'موافقة' : 'Approve'}
                  </Button>
                  <Button 
                    variant="destructive"
                    className="flex-1"
                    onClick={() => openDecisionDialog('rejected')}
                  >
                    <XCircle className={`w-4 h-4 ${isRTL ? 'ml-2' : 'mr-2'}`} />
                    {isRTL ? 'رفض' : 'Reject'}
                  </Button>
                </div>
              )}
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* Decision Dialog */}
      <Dialog open={decisionDialogOpen} onOpenChange={setDecisionDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle className={isRTL ? 'text-right' : ''}>
              {decisionType === 'approved' 
                ? (isRTL ? 'تأكيد الموافقة' : 'Confirm Approval')
                : (isRTL ? 'تأكيد الرفض' : 'Confirm Rejection')
              }
            </DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div className={`p-4 rounded-lg ${
              decisionType === 'approved' ? 'bg-green-50' : 'bg-red-50'
            }`}>
              <div className={`flex items-center gap-2 ${isRTL ? 'flex-row-reverse' : ''}`}>
                {decisionType === 'approved' 
                  ? <CheckCircle2 className="w-5 h-5 text-green-600" />
                  : <XCircle className="w-5 h-5 text-red-600" />
                }
                <p className={decisionType === 'approved' ? 'text-green-700' : 'text-red-700'}>
                  {decisionType === 'approved'
                    ? (isRTL ? 'أنت على وشك الموافقة على هذا الطلب' : 'You are about to approve this request')
                    : (isRTL ? 'أنت على وشك رفض هذا الطلب' : 'You are about to reject this request')
                  }
                </p>
              </div>
            </div>
            <div className={`space-y-2 ${isRTL ? 'text-right' : ''}`}>
              <label className="text-sm font-medium">
                {isRTL ? 'التعليقات (اختياري)' : 'Comments (optional)'}
              </label>
              <Textarea
                value={comments}
                onChange={(e) => setComments(e.target.value)}
                placeholder={isRTL ? 'أدخل تعليقاتك هنا...' : 'Enter your comments here...'}
                className={isRTL ? 'text-right' : ''}
                rows={3}
              />
            </div>
          </div>
          <DialogFooter className={isRTL ? 'flex-row-reverse' : ''}>
            <Button variant="outline" onClick={() => setDecisionDialogOpen(false)} disabled={submitting}>
              {isRTL ? 'إلغاء' : 'Cancel'}
            </Button>
            <Button 
              onClick={submitDecision}
              disabled={submitting}
              className={decisionType === 'approved' ? 'bg-green-600 hover:bg-green-700' : ''}
              variant={decisionType === 'rejected' ? 'destructive' : 'default'}
            >
              {submitting && <Loader2 className={`w-4 h-4 animate-spin ${isRTL ? 'ml-2' : 'mr-2'}`} />}
              {decisionType === 'approved' 
                ? (isRTL ? 'تأكيد الموافقة' : 'Confirm Approval')
                : (isRTL ? 'تأكيد الرفض' : 'Confirm Rejection')
              }
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default ApprovalsPage;
