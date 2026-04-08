import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import axios from 'axios';
import { API } from '@/lib/apiConfig';
import {
  AlertTriangle, Plus, Eye, Edit, Trash2, Download, CheckCircle, XCircle,
  FileWarning, Calendar, User, Building, Tag, ClipboardCheck
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



export default function NonconformityReportsPage() {
  const { t, i18n } = useTranslation();
  const isRTL = i18n.language === 'ar';
  
  const [reportsList, setReportsList] = useState([]);
  const [stage2Reports, setStage2Reports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showViewModal, setShowViewModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showNCModal, setShowNCModal] = useState(false);
  const [selectedReport, setSelectedReport] = useState(null);
  const [editingNC, setEditingNC] = useState(null);
  
  const [createMode, setCreateMode] = useState('report');
  const [selectedReportId, setSelectedReportId] = useState('');
  const [formData, setFormData] = useState({
    client_name: '',
    certificate_no: '',
    standards: [],
    audit_type: '',
    audit_date: '',
    lead_auditor: '',
    management_representative: '',
    submission_deadline: '',
    verification_options: {
      corrections_appropriate: false,
      corrections_verified: false,
      verify_next_audit: false,
      re_audit_performed: false
    }
  });
  
  const [ncFormData, setNCFormData] = useState({
    standard_clause: '',
    description: '',
    nc_type: 'minor',
    root_cause: '',
    corrections: '',
    corrective_actions: '',
    verification_evidence: '',
    verification_decision: '',
    status: 'open'
  });

  const token = localStorage.getItem('token');
  const headers = { Authorization: `Bearer ${token}` };

  useEffect(() => {
    fetchReports();
    fetchStage2Reports();
  }, []);

  const fetchReports = async () => {
    try {
      const response = await axios.get(`${API}/nonconformity-reports`, { headers });
      setReportsList(response.data);
    } catch (error) {
      console.error('Error fetching nonconformity reports:', error);
      toast.error(t('ncReports.fetchError'));
    } finally {
      setLoading(false);
    }
  };

  const fetchStage2Reports = async () => {
    try {
      const response = await axios.get(`${API}/stage2-audit-reports`, { headers });
      setStage2Reports(response.data.filter(r => r.status === 'approved'));
    } catch (error) {
      console.error('Error fetching Stage 2 reports:', error);
    }
  };

  const handleCreate = async () => {
    try {
      const payload = createMode === 'report' 
        ? { stage2_report_id: selectedReportId }
        : formData;
      
      const response = await axios.post(`${API}/nonconformity-reports`, payload, { headers });
      setReportsList([response.data, ...reportsList]);
      setShowCreateModal(false);
      resetForm();
      toast.success(t('ncReports.createSuccess'));
    } catch (error) {
      console.error('Error creating report:', error);
      toast.error(t('ncReports.createError'));
    }
  };

  const handleUpdate = async () => {
    if (!selectedReport) return;
    
    try {
      const response = await axios.put(
        `${API}/nonconformity-reports/${selectedReport.id}`,
        formData,
        { headers }
      );
      setReportsList(reportsList.map(r => r.id === selectedReport.id ? response.data : r));
      setShowEditModal(false);
      toast.success(t('ncReports.updateSuccess'));
    } catch (error) {
      console.error('Error updating report:', error);
      toast.error(t('ncReports.updateError'));
    }
  };

  const handleDelete = async (reportId) => {
    if (!window.confirm(t('ncReports.confirmDelete'))) return;
    
    try {
      await axios.delete(`${API}/nonconformity-reports/${reportId}`, { headers });
      setReportsList(reportsList.filter(r => r.id !== reportId));
      toast.success(t('ncReports.deleteSuccess'));
    } catch (error) {
      console.error('Error deleting report:', error);
      toast.error(t('ncReports.deleteError'));
    }
  };

  const handleCloseReport = async (reportId) => {
    try {
      await axios.post(`${API}/nonconformity-reports/${reportId}/close`, {}, { headers });
      setReportsList(reportsList.map(r => 
        r.id === reportId ? { ...r, status: 'closed' } : r
      ));
      toast.success(t('ncReports.closeSuccess'));
    } catch (error) {
      console.error('Error closing report:', error);
      toast.error(t('ncReports.closeError'));
    }
  };

  const handleDownloadPDF = async (reportId) => {
    try {
      const response = await axios.get(
        `${API}/nonconformity-reports/${reportId}/pdf`,
        { headers, responseType: 'blob' }
      );
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `nc_report_${reportId.slice(0, 8)}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error('Error downloading PDF:', error);
      toast.error(t('ncReports.pdfError'));
    }
  };

  const handleAddNC = async () => {
    if (!selectedReport) return;
    
    try {
      await axios.post(
        `${API}/nonconformity-reports/${selectedReport.id}/add-nc`,
        ncFormData,
        { headers }
      );
      await fetchReports();
      setShowNCModal(false);
      resetNCForm();
      toast.success(t('ncReports.ncAddSuccess'));
    } catch (error) {
      console.error('Error adding NC:', error);
      toast.error(t('ncReports.ncAddError'));
    }
  };

  const handleUpdateNC = async () => {
    if (!selectedReport || !editingNC) return;
    
    try {
      await axios.put(
        `${API}/nonconformity-reports/${selectedReport.id}/nc/${editingNC.id}`,
        ncFormData,
        { headers }
      );
      await fetchReports();
      setShowNCModal(false);
      setEditingNC(null);
      resetNCForm();
      toast.success(t('ncReports.ncUpdateSuccess'));
    } catch (error) {
      console.error('Error updating NC:', error);
      toast.error(t('ncReports.ncUpdateError'));
    }
  };

  const handleDeleteNC = async (reportId, ncId) => {
    if (!window.confirm(t('ncReports.confirmDeleteNC'))) return;
    
    try {
      await axios.delete(`${API}/nonconformity-reports/${reportId}/nc/${ncId}`, { headers });
      await fetchReports();
      toast.success(t('ncReports.ncDeleteSuccess'));
    } catch (error) {
      console.error('Error deleting NC:', error);
      toast.error(t('ncReports.ncDeleteError'));
    }
  };

  const resetForm = () => {
    setFormData({
      client_name: '',
      certificate_no: '',
      standards: [],
      audit_type: '',
      audit_date: '',
      lead_auditor: '',
      management_representative: '',
      submission_deadline: '',
      verification_options: {
        corrections_appropriate: false,
        corrections_verified: false,
        verify_next_audit: false,
        re_audit_performed: false
      }
    });
    setSelectedReportId('');
    setCreateMode('report');
  };

  const resetNCForm = () => {
    setNCFormData({
      standard_clause: '',
      description: '',
      nc_type: 'minor',
      root_cause: '',
      corrections: '',
      corrective_actions: '',
      verification_evidence: '',
      verification_decision: '',
      status: 'open'
    });
  };

  const openEditModal = (report) => {
    setSelectedReport(report);
    setFormData({
      client_name: report.client_name || '',
      certificate_no: report.certificate_no || '',
      standards: report.standards || [],
      audit_type: report.audit_type || '',
      audit_date: report.audit_date || '',
      lead_auditor: report.lead_auditor || '',
      management_representative: report.management_representative || '',
      submission_deadline: report.submission_deadline || '',
      verification_options: report.verification_options || {}
    });
    setShowEditModal(true);
  };

  const openViewModal = (report) => {
    setSelectedReport(report);
    setShowViewModal(true);
  };

  const openAddNCModal = (report) => {
    setSelectedReport(report);
    setEditingNC(null);
    resetNCForm();
    setShowNCModal(true);
  };

  const openEditNCModal = (report, nc) => {
    setSelectedReport(report);
    setEditingNC(nc);
    setNCFormData({
      standard_clause: nc.standard_clause || '',
      description: nc.description || '',
      nc_type: nc.nc_type || 'minor',
      root_cause: nc.root_cause || '',
      corrections: nc.corrections || '',
      corrective_actions: nc.corrective_actions || '',
      verification_evidence: nc.verification_evidence || '',
      verification_decision: nc.verification_decision || '',
      status: nc.status || 'open'
    });
    setShowNCModal(true);
  };

  // Stats
  const stats = {
    total: reportsList.length,
    open: reportsList.filter(r => r.status !== 'closed').length,
    closed: reportsList.filter(r => r.status === 'closed').length,
    totalMajor: reportsList.reduce((sum, r) => sum + (r.total_major || 0), 0),
    totalMinor: reportsList.reduce((sum, r) => sum + (r.total_minor || 0), 0)
  };

  const getStatusBadge = (status) => {
    const styles = {
      draft: 'bg-gray-100 text-gray-800',
      sent_to_client: 'bg-blue-100 text-blue-800',
      pending_verification: 'bg-yellow-100 text-yellow-800',
      closed: 'bg-green-100 text-green-800'
    };
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${styles[status] || 'bg-gray-100'}`}>
        {t(`ncReports.status.${status}`)}
      </span>
    );
  };

  const getNCTypeBadge = (ncType) => {
    return ncType === 'major' 
      ? <span className="px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">MJ - Major</span>
      : <span className="px-2 py-1 rounded-full text-xs font-medium bg-orange-100 text-orange-800">MN - Minor</span>;
  };

  return (
    <div className={`p-6 space-y-6 ${isRTL ? 'rtl' : 'ltr'}`} dir={isRTL ? 'rtl' : 'ltr'}>
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{t('ncReports.title')}</h1>
          <p className="text-gray-500 mt-1">{t('ncReports.subtitle')}</p>
        </div>
        <Button onClick={() => setShowCreateModal(true)} data-testid="create-nc-report-btn">
          <Plus className="w-4 h-4 mr-2" />
          {t('ncReports.create')}
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-500">{t('ncReports.stats.total')}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.total}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-500">{t('ncReports.stats.open')}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">{stats.open}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-500">{t('ncReports.stats.closed')}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{stats.closed}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-500">{t('ncReports.stats.majorNCs')}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{stats.totalMajor}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-500">{t('ncReports.stats.minorNCs')}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-600">{stats.totalMinor}</div>
          </CardContent>
        </Card>
      </div>

      {/* Reports List */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileWarning className="w-5 h-5" />
            {t('ncReports.listTitle')}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8 text-gray-500">{t('loading')}</div>
          ) : reportsList.length === 0 ? (
            <div className="text-center py-8 text-gray-500">{t('ncReports.empty')}</div>
          ) : (
            <div className="overflow-x-auto" dir={isRTL ? 'rtl' : 'ltr'}>
              <table className="w-full table-fixed" data-testid="nc-reports-table">
                <thead>
                  <tr className={`border-b ${isRTL ? 'text-right' : 'text-left'}`}>
                    <th className={`p-3 px-4 font-medium w-[180px] ${isRTL ? 'text-right' : 'text-left'}`}>{t('ncReports.clientName')}</th>
                    <th className={`p-3 px-4 font-medium w-[100px] ${isRTL ? 'text-right' : 'text-left'}`}>{t('ncReports.auditType')}</th>
                    <th className={`p-3 px-4 font-medium w-[180px] ${isRTL ? 'text-right' : 'text-left'}`}>{t('ncReports.ncs')}</th>
                    <th className={`p-3 px-4 font-medium w-[100px] ${isRTL ? 'text-right' : 'text-left'}`}>{t('ncReports.date')}</th>
                    <th className={`p-3 px-4 font-medium w-[100px] ${isRTL ? 'text-right' : 'text-left'}`}>{t('ncReports.statusLabel')}</th>
                    <th className={`p-3 px-4 font-medium w-[180px] ${isRTL ? 'text-right' : 'text-left'}`}>{t('actions')}</th>
                  </tr>
                </thead>
                <tbody>
                  {reportsList.map((report) => (
                    <tr key={report.id} className="border-b hover:bg-gray-50">
                      <td className="p-3 px-4">
                        <div className={`font-medium ${isRTL ? 'text-right' : ''}`}>{report.client_name}</div>
                        <div className={`text-sm text-gray-500 ${isRTL ? 'text-right' : ''}`}>{report.standards?.join(', ')}</div>
                      </td>
                      <td className={`p-3 px-4 ${isRTL ? 'text-right' : ''}`}>{report.audit_type}</td>
                      <td className="p-3 px-4">
                        <div className={`flex gap-2 text-sm ${isRTL ? 'flex-row-reverse justify-end' : ''}`}>
                          <span className="text-red-600 font-medium">MJ: {report.total_major || 0}</span>
                          <span className="text-orange-600 font-medium">MN: {report.total_minor || 0}</span>
                          <span className="text-green-600">({report.closed_count || 0} {t('ncReports.closedLabel')})</span>
                        </div>
                      </td>
                      <td className={`p-3 px-4 ${isRTL ? 'text-right' : ''}`} dir="ltr">{report.audit_date}</td>
                      <td className={`p-3 px-4 ${isRTL ? 'text-right' : ''}`}>{getStatusBadge(report.status)}</td>
                      <td className="p-3 px-4">
                        <div className={`flex gap-1 ${isRTL ? 'flex-row-reverse justify-end' : ''}`}>
                          <Button variant="ghost" size="sm" onClick={() => openViewModal(report)} title={t('view')}>
                            <Eye className="w-4 h-4" />
                          </Button>
                          <Button variant="ghost" size="sm" onClick={() => openEditModal(report)} title={t('edit')}>
                            <Edit className="w-4 h-4" />
                          </Button>
                          <Button variant="ghost" size="sm" onClick={() => openAddNCModal(report)} title={t('ncReports.addNC')} className="text-orange-600">
                            <Plus className="w-4 h-4" />
                          </Button>
                          {report.status !== 'closed' && (
                            <Button variant="ghost" size="sm" onClick={() => handleCloseReport(report.id)} title={t('ncReports.closeReport')} className="text-green-600">
                              <CheckCircle className="w-4 h-4" />
                            </Button>
                          )}
                          <Button variant="ghost" size="sm" onClick={() => handleDownloadPDF(report.id)} title={t('downloadPDF')} className="text-blue-600">
                            <Download className="w-4 h-4" />
                          </Button>
                          <Button variant="ghost" size="sm" onClick={() => handleDelete(report.id)} title={t('delete')} className="text-red-600">
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
            <DialogTitle>{t('ncReports.createTitle')}</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label>{t('ncReports.createMode')}</Label>
              <Select value={createMode} onValueChange={setCreateMode}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="report">{t('ncReports.fromReport')}</SelectItem>
                  <SelectItem value="manual">{t('ncReports.manual')}</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {createMode === 'report' ? (
              <div className="space-y-2">
                <Label>{t('ncReports.selectReport')}</Label>
                <Select value={selectedReportId} onValueChange={setSelectedReportId}>
                  <SelectTrigger>
                    <SelectValue placeholder={t('ncReports.selectReportPlaceholder')} />
                  </SelectTrigger>
                  <SelectContent>
                    {stage2Reports.map((report) => (
                      <SelectItem key={report.id} value={report.id}>
                        {report.organization_name} - {report.standards?.join(', ')}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            ) : (
              <>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>{t('ncReports.clientName')}</Label>
                    <Input
                      value={formData.client_name}
                      onChange={(e) => setFormData({ ...formData, client_name: e.target.value })}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>{t('ncReports.certificateNo')}</Label>
                    <Input
                      value={formData.certificate_no}
                      onChange={(e) => setFormData({ ...formData, certificate_no: e.target.value })}
                    />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>{t('ncReports.leadAuditor')}</Label>
                    <Input
                      value={formData.lead_auditor}
                      onChange={(e) => setFormData({ ...formData, lead_auditor: e.target.value })}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>{t('ncReports.auditType')}</Label>
                    <Select value={formData.audit_type} onValueChange={(v) => setFormData({ ...formData, audit_type: v })}>
                      <SelectTrigger><SelectValue /></SelectTrigger>
                      <SelectContent>
                        <SelectItem value="Stage 1">Stage 1</SelectItem>
                        <SelectItem value="Stage 2">Stage 2</SelectItem>
                        <SelectItem value="Surveillance 1">Surveillance 1</SelectItem>
                        <SelectItem value="Surveillance 2">Surveillance 2</SelectItem>
                        <SelectItem value="Recertification">Recertification</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>{t('ncReports.date')}</Label>
                    <Input type="date" value={formData.audit_date} onChange={(e) => setFormData({ ...formData, audit_date: e.target.value })} />
                  </div>
                  <div className="space-y-2">
                    <Label>{t('ncReports.managementRep')}</Label>
                    <Input value={formData.management_representative} onChange={(e) => setFormData({ ...formData, management_representative: e.target.value })} />
                  </div>
                </div>
              </>
            )}

            <div className="flex justify-end gap-2 pt-4">
              <Button variant="outline" onClick={() => setShowCreateModal(false)}>{t('cancel')}</Button>
              <Button onClick={handleCreate} disabled={createMode === 'report' && !selectedReportId}>{t('create')}</Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* View Modal */}
      <Dialog open={showViewModal} onOpenChange={setShowViewModal}>
        <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>{t('ncReports.viewTitle')}</DialogTitle>
          </DialogHeader>
          {selectedReport && (
            <div className="space-y-6">
              {/* Header Info */}
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4 p-4 bg-gray-50 rounded-lg">
                <div>
                  <div className="text-sm text-gray-500">{t('ncReports.clientName')}</div>
                  <div className="font-medium">{selectedReport.client_name || '—'}</div>
                </div>
                <div>
                  <div className="text-sm text-gray-500">{t('ncReports.certificateNo')}</div>
                  <div className="font-medium">{selectedReport.certificate_no || '—'}</div>
                </div>
                <div>
                  <div className="text-sm text-gray-500">{t('ncReports.standards')}</div>
                  <div className="font-medium">{selectedReport.standards?.join(', ') || '—'}</div>
                </div>
                <div>
                  <div className="text-sm text-gray-500">{t('ncReports.auditType')}</div>
                  <div className="font-medium">{selectedReport.audit_type || '—'}</div>
                </div>
                <div>
                  <div className="text-sm text-gray-500">{t('ncReports.date')}</div>
                  <div className="font-medium">{selectedReport.audit_date || '—'}</div>
                </div>
                <div>
                  <div className="text-sm text-gray-500">{t('ncReports.leadAuditor')}</div>
                  <div className="font-medium">{selectedReport.lead_auditor || '—'}</div>
                </div>
              </div>

              {/* NC Summary */}
              <div className="flex gap-4">
                <div className="px-4 py-2 bg-red-50 rounded-lg">
                  <span className="text-red-700 font-medium">Major: {selectedReport.total_major || 0}</span>
                </div>
                <div className="px-4 py-2 bg-orange-50 rounded-lg">
                  <span className="text-orange-700 font-medium">Minor: {selectedReport.total_minor || 0}</span>
                </div>
                <div className="px-4 py-2 bg-green-50 rounded-lg">
                  <span className="text-green-700 font-medium">Closed: {selectedReport.closed_count || 0}</span>
                </div>
              </div>

              {/* Nonconformities List */}
              <div className="border rounded-lg">
                <div className="p-3 bg-gray-100 font-medium flex justify-between items-center">
                  <span>{t('ncReports.nonconformities')}</span>
                  <Button size="sm" onClick={() => openAddNCModal(selectedReport)}>
                    <Plus className="w-4 h-4 mr-1" /> {t('ncReports.addNC')}
                  </Button>
                </div>
                {selectedReport.nonconformities?.length === 0 ? (
                  <div className="p-4 text-center text-gray-500">{t('ncReports.noNCs')}</div>
                ) : (
                  <div className="divide-y">
                    {selectedReport.nonconformities?.map((nc, index) => (
                      <div key={nc.id || index} className="p-4">
                        <div className="flex justify-between items-start mb-2">
                          <div className="flex gap-2 items-center">
                            <span className="font-bold">NC #{index + 1}</span>
                            {getNCTypeBadge(nc.nc_type)}
                            <span className={`px-2 py-0.5 rounded text-xs ${nc.status === 'closed' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}`}>
                              {nc.status === 'closed' ? 'CLOSED' : 'OPEN'}
                            </span>
                          </div>
                          <div className="flex gap-1">
                            <Button variant="ghost" size="sm" onClick={() => openEditNCModal(selectedReport, nc)}>
                              <Edit className="w-4 h-4" />
                            </Button>
                            <Button variant="ghost" size="sm" className="text-red-600" onClick={() => handleDeleteNC(selectedReport.id, nc.id)}>
                              <Trash2 className="w-4 h-4" />
                            </Button>
                          </div>
                        </div>
                        <div className="grid gap-2 text-sm">
                          <div><span className="text-gray-500">Clause:</span> {nc.standard_clause}</div>
                          <div><span className="text-gray-500">Description:</span> {nc.description}</div>
                          {nc.root_cause && <div><span className="text-gray-500">Root Cause:</span> {nc.root_cause}</div>}
                          {nc.corrections && <div><span className="text-gray-500">Corrections:</span> {nc.corrections}</div>}
                          {nc.corrective_actions && <div><span className="text-gray-500">Corrective Actions:</span> {nc.corrective_actions}</div>}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* Edit Modal */}
      <Dialog open={showEditModal} onOpenChange={setShowEditModal}>
        <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>{t('ncReports.editTitle')}</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>{t('ncReports.clientName')}</Label>
                <Input value={formData.client_name} onChange={(e) => setFormData({ ...formData, client_name: e.target.value })} />
              </div>
              <div className="space-y-2">
                <Label>{t('ncReports.certificateNo')}</Label>
                <Input value={formData.certificate_no} onChange={(e) => setFormData({ ...formData, certificate_no: e.target.value })} />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>{t('ncReports.leadAuditor')}</Label>
                <Input value={formData.lead_auditor} onChange={(e) => setFormData({ ...formData, lead_auditor: e.target.value })} />
              </div>
              <div className="space-y-2">
                <Label>{t('ncReports.managementRep')}</Label>
                <Input value={formData.management_representative} onChange={(e) => setFormData({ ...formData, management_representative: e.target.value })} />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>{t('ncReports.date')}</Label>
                <Input type="date" value={formData.audit_date} onChange={(e) => setFormData({ ...formData, audit_date: e.target.value })} />
              </div>
              <div className="space-y-2">
                <Label>{t('ncReports.deadline')}</Label>
                <Input type="date" value={formData.submission_deadline} onChange={(e) => setFormData({ ...formData, submission_deadline: e.target.value })} />
              </div>
            </div>
            
            {/* Verification Options */}
            <div className="space-y-2">
              <Label>{t('ncReports.verificationOptions')}</Label>
              <div className="space-y-2 p-4 border rounded-lg">
                {[
                  { key: 'corrections_appropriate', label: t('ncReports.vo.appropriate') },
                  { key: 'corrections_verified', label: t('ncReports.vo.verified') },
                  { key: 'verify_next_audit', label: t('ncReports.vo.nextAudit') },
                  { key: 're_audit_performed', label: t('ncReports.vo.reAudit') }
                ].map(({ key, label }) => (
                  <div key={key} className="flex items-center gap-2">
                    <Checkbox 
                      checked={formData.verification_options?.[key] || false}
                      onCheckedChange={(checked) => setFormData({
                        ...formData,
                        verification_options: { ...formData.verification_options, [key]: checked }
                      })}
                    />
                    <span className="text-sm">{label}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="flex justify-end gap-2 pt-4">
              <Button variant="outline" onClick={() => setShowEditModal(false)}>{t('cancel')}</Button>
              <Button onClick={handleUpdate}>{t('save')}</Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* Add/Edit NC Modal */}
      <Dialog open={showNCModal} onOpenChange={setShowNCModal}>
        <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>{editingNC ? t('ncReports.editNC') : t('ncReports.addNC')}</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>{t('ncReports.clause')}</Label>
                <Input value={ncFormData.standard_clause} onChange={(e) => setNCFormData({ ...ncFormData, standard_clause: e.target.value })} placeholder="e.g., 7.1.5" />
              </div>
              <div className="space-y-2">
                <Label>{t('ncReports.ncType')}</Label>
                <Select value={ncFormData.nc_type} onValueChange={(v) => setNCFormData({ ...ncFormData, nc_type: v })}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="minor">MN - Minor</SelectItem>
                    <SelectItem value="major">MJ - Major</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div className="space-y-2">
              <Label>{t('ncReports.description')}</Label>
              <Textarea value={ncFormData.description} onChange={(e) => setNCFormData({ ...ncFormData, description: e.target.value })} rows={2} />
            </div>
            <div className="space-y-2">
              <Label>{t('ncReports.rootCause')}</Label>
              <Textarea value={ncFormData.root_cause} onChange={(e) => setNCFormData({ ...ncFormData, root_cause: e.target.value })} rows={2} />
            </div>
            <div className="space-y-2">
              <Label>{t('ncReports.corrections')}</Label>
              <Textarea value={ncFormData.corrections} onChange={(e) => setNCFormData({ ...ncFormData, corrections: e.target.value })} rows={2} />
            </div>
            <div className="space-y-2">
              <Label>{t('ncReports.correctiveActions')}</Label>
              <Textarea value={ncFormData.corrective_actions} onChange={(e) => setNCFormData({ ...ncFormData, corrective_actions: e.target.value })} rows={2} />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>{t('ncReports.verificationDecision')}</Label>
                <Input value={ncFormData.verification_decision} onChange={(e) => setNCFormData({ ...ncFormData, verification_decision: e.target.value })} />
              </div>
              <div className="space-y-2">
                <Label>{t('ncReports.ncStatus')}</Label>
                <Select value={ncFormData.status} onValueChange={(v) => setNCFormData({ ...ncFormData, status: v })}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="open">Open</SelectItem>
                    <SelectItem value="pending_verification">Pending Verification</SelectItem>
                    <SelectItem value="closed">Closed</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="flex justify-end gap-2 pt-4">
              <Button variant="outline" onClick={() => setShowNCModal(false)}>{t('cancel')}</Button>
              <Button onClick={editingNC ? handleUpdateNC : handleAddNC}>
                {editingNC ? t('save') : t('ncReports.addNC')}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
