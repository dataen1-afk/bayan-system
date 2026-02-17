import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import axios from 'axios';
import { 
  FileText, Plus, Download, Eye, Trash2, Save,
  CheckCircle, Clock, AlertCircle, Building, Calendar,
  X, Check, ClipboardCheck, FileCheck, Award
} from 'lucide-react';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '../components/ui/dialog';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function Stage2AuditReportsPage() {
  const { t, i18n } = useTranslation();
  const isRTL = i18n.language === 'ar';
  
  const [reports, setReports] = useState([]);
  const [stage2Plans, setStage2Plans] = useState([]);
  const [stage1Reports, setStage1Reports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [selectedReport, setSelectedReport] = useState(null);
  const [selectedStage2Id, setSelectedStage2Id] = useState('');
  const [selectedStage1ReportId, setSelectedStage1ReportId] = useState('');
  
  // Edit form state
  const [editForm, setEditForm] = useState({
    employee_change: '',
    scope_change: '',
    integrated_system: '',
    additional_info: '',
    positive_findings: [],
    opportunities_for_improvement: [],
    nonconformities: [],
    certification_recommendation: {},
    overall_recommendation: '',
    checklist_items: [],
    notes: ''
  });
  
  useEffect(() => {
    fetchData();
  }, []);
  
  const fetchData = async () => {
    try {
      const token = localStorage.getItem('token');
      const headers = { Authorization: `Bearer ${token}` };
      
      const [reportsRes, plansRes, stage1ReportsRes] = await Promise.all([
        axios.get(`${API_URL}/api/stage2-audit-reports`, { headers }),
        axios.get(`${API_URL}/api/stage2-audit-plans`, { headers }),
        axios.get(`${API_URL}/api/stage1-audit-reports`, { headers })
      ]);
      
      setReports(reportsRes.data);
      setStage2Plans(plansRes.data.filter(p => p.status === 'client_accepted'));
      setStage1Reports(stage1ReportsRes.data.filter(r => r.status === 'approved'));
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const createReport = async () => {
    if (!selectedStage2Id) {
      alert(t('selectStage2Plan') || 'Please select a Stage 2 plan');
      return;
    }
    
    try {
      const token = localStorage.getItem('token');
      await axios.post(
        `${API_URL}/api/stage2-audit-reports`,
        { 
          stage2_plan_id: selectedStage2Id,
          stage1_report_id: selectedStage1ReportId || null
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setShowCreateModal(false);
      setSelectedStage2Id('');
      setSelectedStage1ReportId('');
      fetchData();
    } catch (error) {
      console.error('Error creating report:', error);
      alert(error.response?.data?.detail || 'Error creating report');
    }
  };
  
  const updateReport = async () => {
    if (!selectedReport) return;
    
    try {
      const token = localStorage.getItem('token');
      await axios.put(
        `${API_URL}/api/stage2-audit-reports/${selectedReport.id}`,
        editForm,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setShowEditModal(false);
      fetchData();
    } catch (error) {
      console.error('Error updating report:', error);
    }
  };
  
  const deleteReport = async (id) => {
    if (!window.confirm(t('confirmDelete') || 'Are you sure you want to delete?')) return;
    
    try {
      const token = localStorage.getItem('token');
      await axios.delete(`${API_URL}/api/stage2-audit-reports/${id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      fetchData();
    } catch (error) {
      console.error('Error deleting report:', error);
    }
  };
  
  const completeReport = async (reportId) => {
    try {
      const token = localStorage.getItem('token');
      await axios.post(
        `${API_URL}/api/stage2-audit-reports/${reportId}/complete`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      fetchData();
    } catch (error) {
      console.error('Error completing report:', error);
      alert(error.response?.data?.detail || 'Error completing report');
    }
  };
  
  const approveReport = async (reportId) => {
    try {
      const token = localStorage.getItem('token');
      await axios.post(
        `${API_URL}/api/stage2-audit-reports/${reportId}/approve`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      fetchData();
    } catch (error) {
      console.error('Error approving report:', error);
      alert(error.response?.data?.detail || 'Error approving report');
    }
  };
  
  const downloadPDF = async (report) => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(
        `${API_URL}/api/stage2-audit-reports/${report.id}/pdf`,
        { 
          headers: { Authorization: `Bearer ${token}` },
          responseType: 'blob'
        }
      );
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `stage2_audit_report_${report.organization_name.replace(/\s+/g, '_')}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error('Error downloading PDF:', error);
    }
  };
  
  const openEditModal = (report) => {
    setSelectedReport(report);
    setEditForm({
      employee_change: report.employee_change || '',
      scope_change: report.scope_change || '',
      integrated_system: report.integrated_system || '',
      additional_info: report.additional_info || '',
      positive_findings: report.positive_findings || [],
      opportunities_for_improvement: report.opportunities_for_improvement || [],
      nonconformities: report.nonconformities || [],
      certification_recommendation: report.certification_recommendation || {},
      overall_recommendation: report.overall_recommendation || '',
      checklist_items: report.checklist_items || [],
      notes: report.notes || ''
    });
    setShowEditModal(true);
  };
  
  // Findings management
  const addPositiveFinding = () => {
    setEditForm({
      ...editForm,
      positive_findings: [...editForm.positive_findings, { department: '', finding: '' }]
    });
  };
  
  const updatePositiveFinding = (index, field, value) => {
    const newFindings = [...editForm.positive_findings];
    newFindings[index] = { ...newFindings[index], [field]: value };
    setEditForm({ ...editForm, positive_findings: newFindings });
  };
  
  const removePositiveFinding = (index) => {
    setEditForm({ ...editForm, positive_findings: editForm.positive_findings.filter((_, i) => i !== index) });
  };
  
  // OFI management
  const addOFI = () => {
    setEditForm({
      ...editForm,
      opportunities_for_improvement: [...editForm.opportunities_for_improvement, { department: '', recommendation: '' }]
    });
  };
  
  const updateOFI = (index, field, value) => {
    const newOFIs = [...editForm.opportunities_for_improvement];
    newOFIs[index] = { ...newOFIs[index], [field]: value };
    setEditForm({ ...editForm, opportunities_for_improvement: newOFIs });
  };
  
  const removeOFI = (index) => {
    setEditForm({ ...editForm, opportunities_for_improvement: editForm.opportunities_for_improvement.filter((_, i) => i !== index) });
  };
  
  // Nonconformity management
  const addNC = () => {
    setEditForm({
      ...editForm,
      nonconformities: [...editForm.nonconformities, { clause: '', description: '', rating: 1 }]
    });
  };
  
  const updateNC = (index, field, value) => {
    const newNCs = [...editForm.nonconformities];
    newNCs[index] = { ...newNCs[index], [field]: value };
    setEditForm({ ...editForm, nonconformities: newNCs });
  };
  
  const removeNC = (index) => {
    setEditForm({ ...editForm, nonconformities: editForm.nonconformities.filter((_, i) => i !== index) });
  };
  
  const toggleCertRecommendation = (key) => {
    setEditForm({
      ...editForm,
      certification_recommendation: {
        ...editForm.certification_recommendation,
        [key]: !editForm.certification_recommendation[key]
      }
    });
  };
  
  const updateChecklistItem = (index, field, value) => {
    const newItems = [...editForm.checklist_items];
    newItems[index] = { ...newItems[index], [field]: value };
    setEditForm({ ...editForm, checklist_items: newItems });
  };
  
  const getStatusBadge = (status) => {
    const statusConfig = {
      'draft': { color: 'bg-gray-100 text-gray-800', icon: Clock, label: t('draft') || 'Draft' },
      'completed': { color: 'bg-blue-100 text-blue-800', icon: FileCheck, label: t('completed') || 'Completed' },
      'approved': { color: 'bg-green-100 text-green-800', icon: CheckCircle, label: t('approved') || 'Approved' }
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
  
  const getRecommendationBadge = (rec) => {
    if (!rec) return null;
    const config = {
      'recommend_certification': { color: 'bg-green-100 text-green-800', label: 'Recommended' },
      'recommend_minor_nc': { color: 'bg-yellow-100 text-yellow-800', label: 'Minor NC' },
      'major_nc_evidence': { color: 'bg-orange-100 text-orange-800', label: 'Major NC' },
      'not_recommended': { color: 'bg-red-100 text-red-800', label: 'Not Recommended' }
    };
    const c = config[rec] || { color: 'bg-gray-100', label: rec };
    return <span className={`px-2 py-1 rounded text-xs font-medium ${c.color}`}>{c.label}</span>;
  };
  
  const availableStage2Plans = stage2Plans.filter(
    p => !reports.some(r => r.stage2_plan_id === p.id)
  );
  
  const stats = {
    total: reports.length,
    draft: reports.filter(r => r.status === 'draft').length,
    completed: reports.filter(r => r.status === 'completed').length,
    approved: reports.filter(r => r.status === 'approved').length
  };

  return (
    <div className={`p-6 ${isRTL ? 'rtl' : 'ltr'}`} dir={isRTL ? 'rtl' : 'ltr'}>
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{t('stage2AuditReports') || 'Stage 2 Audit Reports'}</h1>
          <p className="text-gray-500">BACF6-11 - {t('stage2ReportDescription') || 'Stage 2 audit findings and certification recommendation'}</p>
        </div>
        <Button onClick={() => setShowCreateModal(true)} className="bg-violet-600 hover:bg-violet-700" data-testid="create-report-btn">
          <Plus className="w-4 h-4 mr-2" />
          {t('createReport') || 'Create Report'}
        </Button>
      </div>
      
      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <Card>
          <CardContent className="p-4 flex items-center gap-4">
            <div className="p-3 bg-violet-100 rounded-lg">
              <FileText className="w-6 h-6 text-violet-600" />
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
              <FileCheck className="w-6 h-6 text-blue-600" />
            </div>
            <div>
              <p className="text-2xl font-bold">{stats.completed}</p>
              <p className="text-sm text-gray-500">{t('completed') || 'Completed'}</p>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4 flex items-center gap-4">
            <div className="p-3 bg-green-100 rounded-lg">
              <Award className="w-6 h-6 text-green-600" />
            </div>
            <div>
              <p className="text-2xl font-bold">{stats.approved}</p>
              <p className="text-sm text-gray-500">{t('approved') || 'Approved'}</p>
            </div>
          </CardContent>
        </Card>
      </div>
      
      {/* Reports List */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <ClipboardCheck className="w-5 h-5" />
            {t('stage2AuditReports') || 'Stage 2 Audit Reports'}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8">Loading...</div>
          ) : reports.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <FileText className="w-12 h-12 mx-auto mb-4 opacity-50" />
              <p>{t('noAuditReports') || 'No audit reports yet'}</p>
              <p className="text-sm mt-2">{t('createFromStage2') || 'Create a report from a completed Stage 2 audit'}</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left p-3 font-medium text-gray-600">{t('organization') || 'Organization'}</th>
                    <th className="text-left p-3 font-medium text-gray-600">{t('auditDate') || 'Audit Date'}</th>
                    <th className="text-left p-3 font-medium text-gray-600">{t('recommendation') || 'Recommendation'}</th>
                    <th className="text-left p-3 font-medium text-gray-600">{t('status') || 'Status'}</th>
                    <th className="text-left p-3 font-medium text-gray-600">{t('actions') || 'Actions'}</th>
                  </tr>
                </thead>
                <tbody>
                  {reports.map(report => (
                    <tr key={report.id} className="border-b hover:bg-gray-50" data-testid={`report-row-${report.id}`}>
                      <td className="p-3">
                        <div className="flex items-center gap-2">
                          <Building className="w-4 h-4 text-gray-400" />
                          <span className="font-medium">{report.organization_name}</span>
                        </div>
                      </td>
                      <td className="p-3">
                        <div className="flex items-center gap-1">
                          <Calendar className="w-4 h-4 text-gray-400" />
                          {report.start_date || '-'}
                        </div>
                      </td>
                      <td className="p-3">{getRecommendationBadge(report.overall_recommendation)}</td>
                      <td className="p-3">{getStatusBadge(report.status)}</td>
                      <td className="p-3">
                        <div className="flex gap-2">
                          <Button size="sm" variant="outline" onClick={() => openEditModal(report)} data-testid={`edit-report-${report.id}`}>
                            <Eye className="w-4 h-4" />
                          </Button>
                          
                          {report.status === 'draft' && report.overall_recommendation && (
                            <Button size="sm" variant="outline" onClick={() => completeReport(report.id)} className="text-blue-600" data-testid={`complete-report-${report.id}`}>
                              <FileCheck className="w-4 h-4" />
                            </Button>
                          )}
                          
                          {report.status === 'completed' && (
                            <Button size="sm" variant="outline" onClick={() => approveReport(report.id)} className="text-green-600" data-testid={`approve-report-${report.id}`}>
                              <Check className="w-4 h-4" />
                            </Button>
                          )}
                          
                          <Button size="sm" className="bg-violet-600 hover:bg-violet-700" onClick={() => downloadPDF(report)} data-testid={`download-pdf-${report.id}`}>
                            <Download className="w-4 h-4" />
                          </Button>
                          
                          {report.status === 'draft' && (
                            <Button size="sm" variant="destructive" onClick={() => deleteReport(report.id)} data-testid={`delete-report-${report.id}`}>
                              <Trash2 className="w-4 h-4" />
                            </Button>
                          )}
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
            <DialogTitle>{t('createAuditReport') || 'Create Audit Report'}</DialogTitle>
            <DialogDescription>{t('selectStage2Audit') || 'Select a completed Stage 2 audit'}</DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label>{t('stage2Plan') || 'Stage 2 Plan'} *</Label>
              <Select value={selectedStage2Id} onValueChange={setSelectedStage2Id}>
                <SelectTrigger data-testid="select-stage2-plan">
                  <SelectValue placeholder={t('selectStage2') || 'Select Stage 2 plan...'} />
                </SelectTrigger>
                <SelectContent>
                  {availableStage2Plans.map(plan => (
                    <SelectItem key={plan.id} value={plan.id}>{plan.organization_name}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            
            <div>
              <Label>{t('stage1Report') || 'Stage 1 Report'} ({t('optional') || 'optional'})</Label>
              <Select value={selectedStage1ReportId} onValueChange={setSelectedStage1ReportId}>
                <SelectTrigger>
                  <SelectValue placeholder={t('selectStage1Report') || 'Select Stage 1 report...'} />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">None</SelectItem>
                  {stage1Reports.map(r => (
                    <SelectItem key={r.id} value={r.id}>{r.organization_name}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            
            <div className="flex gap-2 justify-end">
              <Button variant="outline" onClick={() => setShowCreateModal(false)}>{t('cancel') || 'Cancel'}</Button>
              <Button onClick={createReport} disabled={!selectedStage2Id} data-testid="create-report-submit" className="bg-violet-600 hover:bg-violet-700">
                {t('create') || 'Create'}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
      
      {/* Edit Modal */}
      <Dialog open={showEditModal} onOpenChange={setShowEditModal}>
        <DialogContent className="max-w-5xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>{t('stage2AuditReport') || 'Stage 2 Audit Report'}</DialogTitle>
            <DialogDescription>{selectedReport?.organization_name} - BACF6-11</DialogDescription>
          </DialogHeader>
          {selectedReport && (
            <div className="space-y-6">
              {/* Organization Info */}
              <div className="p-4 bg-gray-50 rounded-lg">
                <h3 className="font-semibold mb-3">{t('organizationDetails') || 'Organization Details'}</h3>
                <div className="grid grid-cols-3 gap-4 text-sm">
                  <div><span className="text-gray-500">Standards:</span> {selectedReport.standards?.join(', ')}</div>
                  <div><span className="text-gray-500">Lead Auditor:</span> {selectedReport.audit_team?.lead_auditor}</div>
                  <div><span className="text-gray-500">Date:</span> {selectedReport.start_date} - {selectedReport.end_date}</div>
                </div>
              </div>
              
              {/* Change Details */}
              <div>
                <h3 className="font-semibold mb-3">{t('changeDetails') || 'Change Details'}</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label>{t('employeeChange') || 'Employee change?'}</Label>
                    <Input value={editForm.employee_change} onChange={(e) => setEditForm({...editForm, employee_change: e.target.value})} placeholder="No / Yes" />
                  </div>
                  <div>
                    <Label>{t('scopeChange') || 'Scope change?'}</Label>
                    <Input value={editForm.scope_change} onChange={(e) => setEditForm({...editForm, scope_change: e.target.value})} placeholder="No / Yes" />
                  </div>
                </div>
              </div>
              
              {/* Positive Findings */}
              <div>
                <div className="flex justify-between items-center mb-3">
                  <h3 className="font-semibold text-green-700">{t('positiveFindings') || 'Positive Findings'}</h3>
                  <Button size="sm" variant="outline" onClick={addPositiveFinding}><Plus className="w-4 h-4 mr-1" />{t('add') || 'Add'}</Button>
                </div>
                <div className="space-y-2">
                  {editForm.positive_findings.map((f, i) => (
                    <div key={i} className="flex gap-2 items-center p-2 bg-green-50 rounded">
                      <Input value={f.department} onChange={(e) => updatePositiveFinding(i, 'department', e.target.value)} placeholder="Department" className="w-32" />
                      <Input value={f.finding} onChange={(e) => updatePositiveFinding(i, 'finding', e.target.value)} placeholder="Finding" className="flex-1" />
                      <Button size="sm" variant="ghost" onClick={() => removePositiveFinding(i)} className="text-red-500"><X className="w-4 h-4" /></Button>
                    </div>
                  ))}
                </div>
              </div>
              
              {/* Opportunities for Improvement */}
              <div>
                <div className="flex justify-between items-center mb-3">
                  <h3 className="font-semibold text-orange-700">{t('opportunitiesForImprovement') || 'Opportunities for Improvement'}</h3>
                  <Button size="sm" variant="outline" onClick={addOFI}><Plus className="w-4 h-4 mr-1" />{t('add') || 'Add'}</Button>
                </div>
                <div className="space-y-2">
                  {editForm.opportunities_for_improvement.map((ofi, i) => (
                    <div key={i} className="flex gap-2 items-center p-2 bg-orange-50 rounded">
                      <Input value={ofi.department} onChange={(e) => updateOFI(i, 'department', e.target.value)} placeholder="Department" className="w-32" />
                      <Input value={ofi.recommendation} onChange={(e) => updateOFI(i, 'recommendation', e.target.value)} placeholder="Recommendation" className="flex-1" />
                      <Button size="sm" variant="ghost" onClick={() => removeOFI(i)} className="text-red-500"><X className="w-4 h-4" /></Button>
                    </div>
                  ))}
                </div>
              </div>
              
              {/* Nonconformities */}
              <div>
                <div className="flex justify-between items-center mb-3">
                  <div>
                    <h3 className="font-semibold text-red-700">{t('nonconformities') || 'Nonconformities'}</h3>
                    <p className="text-xs text-gray-500">Rating: 1=Minor NC, 2=Major NC</p>
                  </div>
                  <Button size="sm" variant="outline" onClick={addNC}><Plus className="w-4 h-4 mr-1" />{t('add') || 'Add'}</Button>
                </div>
                <div className="space-y-2">
                  {editForm.nonconformities.map((nc, i) => (
                    <div key={i} className="flex gap-2 items-center p-2 bg-red-50 rounded">
                      <Input value={nc.clause} onChange={(e) => updateNC(i, 'clause', e.target.value)} placeholder="Clause (e.g. 7.2)" className="w-24" />
                      <Input value={nc.description} onChange={(e) => updateNC(i, 'description', e.target.value)} placeholder="NC Description" className="flex-1" />
                      <Select value={String(nc.rating)} onValueChange={(v) => updateNC(i, 'rating', parseInt(v))}>
                        <SelectTrigger className="w-20"><SelectValue /></SelectTrigger>
                        <SelectContent>
                          <SelectItem value="1">1</SelectItem>
                          <SelectItem value="2">2</SelectItem>
                        </SelectContent>
                      </Select>
                      <Button size="sm" variant="ghost" onClick={() => removeNC(i)} className="text-red-500"><X className="w-4 h-4" /></Button>
                    </div>
                  ))}
                </div>
              </div>
              
              {/* Certification Recommendation */}
              <div>
                <h3 className="font-semibold mb-3">{t('certificationRecommendation') || 'Certification Recommendation'}</h3>
                <div className="grid grid-cols-2 gap-2">
                  {[
                    { key: 'issue_certificate', label: 'Issuance of certificate' },
                    { key: 'use_logo', label: 'Use of BAC & EGAC Logo' },
                    { key: 'refuse_certificate', label: 'Refusal of certificate' },
                    { key: 'post_audit', label: 'Post audit' },
                    { key: 'modify_certificate', label: 'Modification of certificate' },
                    { key: 'other', label: 'Other' }
                  ].map(({ key, label }) => (
                    <div key={key} className="flex items-center gap-2 p-2 bg-gray-50 rounded cursor-pointer" onClick={() => toggleCertRecommendation(key)}>
                      <input type="checkbox" checked={editForm.certification_recommendation[key] || false} onChange={() => {}} className="w-4 h-4" />
                      <span className="text-sm">{label}</span>
                    </div>
                  ))}
                </div>
              </div>
              
              {/* Overall Recommendation */}
              <div>
                <h3 className="font-semibold mb-3">{t('overallRecommendation') || 'Overall Recommendation'} *</h3>
                <div className="space-y-2">
                  {[
                    { value: 'recommend_certification', label: 'System complies - RECOMMENDED for certification', color: 'bg-green-100 border-green-500' },
                    { value: 'recommend_minor_nc', label: 'Minor NC - Corrective action required', color: 'bg-yellow-100 border-yellow-500' },
                    { value: 'major_nc_evidence', label: 'Major NC - Corrective action within 90 days', color: 'bg-orange-100 border-orange-500' },
                    { value: 'not_recommended', label: 'Not Recommended for certification', color: 'bg-red-100 border-red-500' }
                  ].map(({ value, label, color }) => (
                    <div 
                      key={value}
                      onClick={() => setEditForm({...editForm, overall_recommendation: value})}
                      className={`p-3 rounded border-2 cursor-pointer ${editForm.overall_recommendation === value ? color : 'bg-white border-gray-200'}`}
                    >
                      <div className="flex items-center gap-2">
                        <div className={`w-4 h-4 rounded-full border-2 ${editForm.overall_recommendation === value ? 'bg-current' : ''}`} />
                        <span className="text-sm">{label}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
              
              {/* Checklist (collapsed) */}
              <details className="border rounded-lg p-4">
                <summary className="font-semibold cursor-pointer">{t('auditChecklist') || 'Audit Checklist'} ({editForm.checklist_items.length} items)</summary>
                <div className="mt-4 space-y-2 max-h-60 overflow-y-auto">
                  {editForm.checklist_items.map((item, idx) => (
                    <div key={idx} className="flex gap-2 items-center p-2 bg-gray-50 rounded text-sm">
                      <span className="flex-1 truncate">{item.requirement}</span>
                      <Select value={item.status} onValueChange={(v) => updateChecklistItem(idx, 'status', v)}>
                        <SelectTrigger className="w-20"><SelectValue /></SelectTrigger>
                        <SelectContent>
                          <SelectItem value="C">C</SelectItem>
                          <SelectItem value="O">O</SelectItem>
                          <SelectItem value="NCR">NCR</SelectItem>
                        </SelectContent>
                      </Select>
                      <Input value={item.comments} onChange={(e) => updateChecklistItem(idx, 'comments', e.target.value)} placeholder="Comments" className="w-32" />
                    </div>
                  ))}
                </div>
              </details>
              
              {/* Notes */}
              <div>
                <Label>{t('additionalNotes') || 'Additional Notes'}</Label>
                <Textarea value={editForm.notes} onChange={(e) => setEditForm({...editForm, notes: e.target.value})} rows={3} />
              </div>
              
              <div className="flex gap-2 justify-end">
                <Button variant="outline" onClick={() => setShowEditModal(false)}>{t('cancel') || 'Cancel'}</Button>
                <Button onClick={updateReport} data-testid="save-report-btn" className="bg-violet-600 hover:bg-violet-700">
                  <Save className="w-4 h-4 mr-2" />
                  {t('saveChanges') || 'Save Changes'}
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
