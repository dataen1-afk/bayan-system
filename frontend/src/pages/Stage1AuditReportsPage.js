import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import axios from 'axios';
import { 
  FileText, Plus, Download, Eye, Trash2, Save,
  CheckCircle, Clock, AlertCircle, Building, Calendar,
  Users, X, Check, ClipboardCheck, FileCheck
} from 'lucide-react';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '../components/ui/dialog';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function Stage1AuditReportsPage({ embedded = false }) {
  const { t, i18n } = useTranslation();
  const isRTL = i18n.language === 'ar';
  
  const [reports, setReports] = useState([]);
  const [stage1Plans, setStage1Plans] = useState([]);
  const [meetings, setMeetings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [selectedReport, setSelectedReport] = useState(null);
  const [selectedStage1Id, setSelectedStage1Id] = useState('');
  const [selectedMeetingId, setSelectedMeetingId] = useState('');
  
  // Edit form state
  const [editForm, setEditForm] = useState({
    employee_change: '',
    scope_change: '',
    integrated_system: '',
    additional_info: '',
    man_days_adequate: true,
    positive_findings: [],
    areas_of_concern: [],
    declarations: {},
    recommendation: '',
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
      
      const [reportsRes, plansRes, meetingsRes] = await Promise.all([
        axios.get(`${API_URL}/api/stage1-audit-reports`, { headers }),
        axios.get(`${API_URL}/api/stage1-audit-plans`, { headers }),
        axios.get(`${API_URL}/api/opening-closing-meetings`, { headers })
      ]);
      
      setReports(reportsRes.data);
      setStage1Plans(plansRes.data.filter(p => p.status === 'client_accepted'));
      setMeetings(meetingsRes.data.filter(m => m.status === 'submitted'));
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const createReport = async () => {
    if (!selectedStage1Id) {
      alert(t('selectStage1Plan') || 'Please select a Stage 1 plan');
      return;
    }
    
    try {
      const token = localStorage.getItem('token');
      await axios.post(
        `${API_URL}/api/stage1-audit-reports`,
        { 
          stage1_plan_id: selectedStage1Id,
          meeting_id: selectedMeetingId || null
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setShowCreateModal(false);
      setSelectedStage1Id('');
      setSelectedMeetingId('');
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
        `${API_URL}/api/stage1-audit-reports/${selectedReport.id}`,
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
      await axios.delete(`${API_URL}/api/stage1-audit-reports/${id}`, {
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
        `${API_URL}/api/stage1-audit-reports/${reportId}/complete`,
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
        `${API_URL}/api/stage1-audit-reports/${reportId}/approve`,
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
        `${API_URL}/api/stage1-audit-reports/${report.id}/pdf`,
        { 
          headers: { Authorization: `Bearer ${token}` },
          responseType: 'blob'
        }
      );
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `stage1_audit_report_${report.organization_name.replace(/\s+/g, '_')}.pdf`);
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
      man_days_adequate: report.man_days_adequate !== false,
      positive_findings: report.positive_findings || [],
      areas_of_concern: report.areas_of_concern || [],
      declarations: report.declarations || {},
      recommendation: report.recommendation || '',
      checklist_items: report.checklist_items || [],
      notes: report.notes || ''
    });
    setShowEditModal(true);
  };
  
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
    const newFindings = editForm.positive_findings.filter((_, i) => i !== index);
    setEditForm({ ...editForm, positive_findings: newFindings });
  };
  
  const addConcern = () => {
    setEditForm({
      ...editForm,
      areas_of_concern: [...editForm.areas_of_concern, { department: '', concern: '', rating: 1 }]
    });
  };
  
  const updateConcern = (index, field, value) => {
    const newConcerns = [...editForm.areas_of_concern];
    newConcerns[index] = { ...newConcerns[index], [field]: value };
    setEditForm({ ...editForm, areas_of_concern: newConcerns });
  };
  
  const removeConcern = (index) => {
    const newConcerns = editForm.areas_of_concern.filter((_, i) => i !== index);
    setEditForm({ ...editForm, areas_of_concern: newConcerns });
  };
  
  const updateChecklistItem = (index, field, value) => {
    const newItems = [...editForm.checklist_items];
    newItems[index] = { ...newItems[index], [field]: value };
    setEditForm({ ...editForm, checklist_items: newItems });
  };
  
  const toggleDeclaration = (key) => {
    setEditForm({
      ...editForm,
      declarations: {
        ...editForm.declarations,
        [key]: !editForm.declarations[key]
      }
    });
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
      'proceed': { color: 'bg-green-100 text-green-800', label: 'Proceed to Stage 2' },
      'not_proceed': { color: 'bg-orange-100 text-orange-800', label: 'Not Proceed' },
      'further_stage1': { color: 'bg-red-100 text-red-800', label: 'Further Stage 1' }
    };
    const c = config[rec] || config['proceed'];
    return <span className={`px-2 py-1 rounded text-xs font-medium ${c.color}`}>{c.label}</span>;
  };
  
  // Get available Stage 1 plans
  const availableStage1Plans = stage1Plans.filter(
    p => !reports.some(r => r.stage1_plan_id === p.id)
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
          <h1 className="text-2xl font-bold text-gray-900">{t('stage1AuditReports') || 'Stage 1 Audit Reports'}</h1>
          <p className="text-gray-500">BACF6-10 - {t('auditReportDescription') || 'Stage 1 audit findings and recommendations'}</p>
        </div>
        <Button onClick={() => setShowCreateModal(true)} className="bg-red-600 hover:bg-red-700" data-testid="create-report-btn">
          <Plus className="w-4 h-4 mr-2" />
          {t('createReport') || 'Create Report'}
        </Button>
      </div>
      
      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <Card>
          <CardContent className="p-4 flex items-center gap-4">
            <div className="p-3 bg-red-100 rounded-lg">
              <FileText className="w-6 h-6 text-red-600" />
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
              <CheckCircle className="w-6 h-6 text-green-600" />
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
            {t('stage1AuditReports') || 'Stage 1 Audit Reports'}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8">Loading...</div>
          ) : reports.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <FileText className="w-12 h-12 mx-auto mb-4 opacity-50" />
              <p>{t('noAuditReports') || 'No audit reports yet'}</p>
              <p className="text-sm mt-2">{t('createFromStage1') || 'Create a report from a completed Stage 1 audit'}</p>
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
                      <td className="p-3">{getRecommendationBadge(report.recommendation)}</td>
                      <td className="p-3">{getStatusBadge(report.status)}</td>
                      <td className="p-3">
                        <div className="flex gap-2">
                          <Button 
                            size="sm" 
                            variant="outline"
                            onClick={() => openEditModal(report)}
                            data-testid={`edit-report-${report.id}`}
                          >
                            <Eye className="w-4 h-4" />
                          </Button>
                          
                          {report.status === 'draft' && report.recommendation && (
                            <Button 
                              size="sm" 
                              variant="outline"
                              onClick={() => completeReport(report.id)}
                              className="text-blue-600 hover:text-blue-700"
                              data-testid={`complete-report-${report.id}`}
                            >
                              <FileCheck className="w-4 h-4" />
                            </Button>
                          )}
                          
                          {report.status === 'completed' && (
                            <Button 
                              size="sm" 
                              variant="outline"
                              onClick={() => approveReport(report.id)}
                              className="text-green-600 hover:text-green-700"
                              data-testid={`approve-report-${report.id}`}
                            >
                              <Check className="w-4 h-4" />
                            </Button>
                          )}
                          
                          <Button 
                            size="sm" 
                            className="bg-red-600 hover:bg-red-700"
                            onClick={() => downloadPDF(report)}
                            data-testid={`download-pdf-${report.id}`}
                          >
                            <Download className="w-4 h-4" />
                          </Button>
                          
                          {report.status === 'draft' && (
                            <Button 
                              size="sm" 
                              variant="destructive"
                              onClick={() => deleteReport(report.id)}
                              data-testid={`delete-report-${report.id}`}
                            >
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
            <DialogDescription>{t('selectStage1Audit') || 'Select a completed Stage 1 audit'}</DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label>{t('stage1Plan') || 'Stage 1 Plan'} *</Label>
              <Select value={selectedStage1Id} onValueChange={setSelectedStage1Id}>
                <SelectTrigger data-testid="select-stage1-plan">
                  <SelectValue placeholder={t('selectStage1') || 'Select Stage 1 plan...'} />
                </SelectTrigger>
                <SelectContent>
                  {availableStage1Plans.map(plan => (
                    <SelectItem key={plan.id} value={plan.id}>
                      {plan.organization_name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            
            <div>
              <Label>{t('meetingForm') || 'Meeting Form'} ({t('optional') || 'optional'})</Label>
              <Select value={selectedMeetingId} onValueChange={setSelectedMeetingId}>
                <SelectTrigger>
                  <SelectValue placeholder={t('selectMeeting') || 'Select meeting...'} />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">None</SelectItem>
                  {meetings.map(meeting => (
                    <SelectItem key={meeting.id} value={meeting.id}>
                      {meeting.organization_name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            
            <div className="flex gap-2 justify-end">
              <Button variant="outline" onClick={() => setShowCreateModal(false)}>{t('cancel') || 'Cancel'}</Button>
              <Button 
                onClick={createReport} 
                disabled={!selectedStage1Id}
                data-testid="create-report-submit"
                className="bg-red-600 hover:bg-red-700"
              >
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
            <DialogTitle>{t('stage1AuditReport') || 'Stage 1 Audit Report'}</DialogTitle>
            <DialogDescription>{selectedReport?.organization_name} - BACF6-10</DialogDescription>
          </DialogHeader>
          {selectedReport && (
            <div className="space-y-6">
              {/* Organization Info (read-only) */}
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
                    <Label>{t('employeeChange') || 'Employee change since application?'}</Label>
                    <Input
                      value={editForm.employee_change}
                      onChange={(e) => setEditForm({...editForm, employee_change: e.target.value})}
                      placeholder="No / Yes (details)"
                    />
                  </div>
                  <div>
                    <Label>{t('scopeChange') || 'Scope change since application?'}</Label>
                    <Input
                      value={editForm.scope_change}
                      onChange={(e) => setEditForm({...editForm, scope_change: e.target.value})}
                      placeholder="No / Yes (details)"
                    />
                  </div>
                  <div>
                    <Label>{t('integratedSystem') || 'Integrated system?'}</Label>
                    <Input
                      value={editForm.integrated_system}
                      onChange={(e) => setEditForm({...editForm, integrated_system: e.target.value})}
                      placeholder="No / Yes (details)"
                    />
                  </div>
                  <div className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={editForm.man_days_adequate}
                      onChange={(e) => setEditForm({...editForm, man_days_adequate: e.target.checked})}
                      className="w-4 h-4"
                    />
                    <Label>{t('manDaysAdequate') || 'Man-days adequate?'}</Label>
                  </div>
                </div>
              </div>
              
              {/* Positive Findings */}
              <div>
                <div className="flex justify-between items-center mb-3">
                  <h3 className="font-semibold text-green-700">{t('positiveFindings') || 'Positive Findings'}</h3>
                  <Button size="sm" variant="outline" onClick={addPositiveFinding}>
                    <Plus className="w-4 h-4 mr-1" />
                    {t('add') || 'Add'}
                  </Button>
                </div>
                <div className="space-y-2">
                  {editForm.positive_findings.map((finding, idx) => (
                    <div key={idx} className="flex gap-2 items-center p-2 bg-green-50 rounded">
                      <Input
                        value={finding.department}
                        onChange={(e) => updatePositiveFinding(idx, 'department', e.target.value)}
                        placeholder="Department"
                        className="w-32"
                      />
                      <Input
                        value={finding.finding}
                        onChange={(e) => updatePositiveFinding(idx, 'finding', e.target.value)}
                        placeholder="Finding"
                        className="flex-1"
                      />
                      <Button size="sm" variant="ghost" onClick={() => removePositiveFinding(idx)} className="text-red-500">
                        <X className="w-4 h-4" />
                      </Button>
                    </div>
                  ))}
                </div>
              </div>
              
              {/* Areas of Concern */}
              <div>
                <div className="flex justify-between items-center mb-3">
                  <div>
                    <h3 className="font-semibold text-orange-700">{t('areasOfConcern') || 'Areas of Concern'}</h3>
                    <p className="text-xs text-gray-500">Rating: 1=OFI, 2=Probable NC, 3=Not Ready</p>
                  </div>
                  <Button size="sm" variant="outline" onClick={addConcern}>
                    <Plus className="w-4 h-4 mr-1" />
                    {t('add') || 'Add'}
                  </Button>
                </div>
                <div className="space-y-2">
                  {editForm.areas_of_concern.map((concern, idx) => (
                    <div key={idx} className="flex gap-2 items-center p-2 bg-orange-50 rounded">
                      <Input
                        value={concern.department}
                        onChange={(e) => updateConcern(idx, 'department', e.target.value)}
                        placeholder="Department"
                        className="w-32"
                      />
                      <Input
                        value={concern.concern}
                        onChange={(e) => updateConcern(idx, 'concern', e.target.value)}
                        placeholder="Concern"
                        className="flex-1"
                      />
                      <Select value={String(concern.rating)} onValueChange={(v) => updateConcern(idx, 'rating', parseInt(v))}>
                        <SelectTrigger className="w-20">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="1">1</SelectItem>
                          <SelectItem value="2">2</SelectItem>
                          <SelectItem value="3">3</SelectItem>
                        </SelectContent>
                      </Select>
                      <Button size="sm" variant="ghost" onClick={() => removeConcern(idx)} className="text-red-500">
                        <X className="w-4 h-4" />
                      </Button>
                    </div>
                  ))}
                </div>
              </div>
              
              {/* Team Leader Declarations */}
              <div>
                <h3 className="font-semibold mb-3">{t('declarations') || 'Team Leader Declarations'}</h3>
                <div className="grid grid-cols-2 gap-2">
                  {[
                    { key: 'sampling', label: 'Auditing based on sampling process' },
                    { key: 'combined', label: 'Audit is combined/joint/integrated' },
                    { key: 'corrective_actions', label: 'Corrective actions effective' },
                    { key: 'outcomes_effective', label: 'Outcomes effective and complying' },
                    { key: 'internal_audit', label: 'Internal audit process effective' },
                    { key: 'scope_appropriate', label: 'Scope of certification appropriate' },
                    { key: 'capability', label: 'Management system capable' },
                    { key: 'objectives_fulfilled', label: 'Audit objectives fulfilled' }
                  ].map(({ key, label }) => (
                    <div key={key} className="flex items-center gap-2 p-2 bg-gray-50 rounded">
                      <input
                        type="checkbox"
                        checked={editForm.declarations[key] || false}
                        onChange={() => toggleDeclaration(key)}
                        className="w-4 h-4"
                      />
                      <span className="text-sm">{label}</span>
                    </div>
                  ))}
                </div>
              </div>
              
              {/* Recommendation */}
              <div>
                <h3 className="font-semibold mb-3">{t('recommendation') || 'Recommendation'} *</h3>
                <div className="space-y-2">
                  {[
                    { value: 'proceed', label: 'Recommended proceeding with Stage 2 (within 60 days)', color: 'bg-green-100 border-green-500' },
                    { value: 'not_proceed', label: 'Not proceeding to Stage 2 until evidence submitted', color: 'bg-orange-100 border-orange-500' },
                    { value: 'further_stage1', label: 'Not proceeding without further Stage 1 visit', color: 'bg-red-100 border-red-500' }
                  ].map(({ value, label, color }) => (
                    <div 
                      key={value}
                      onClick={() => setEditForm({...editForm, recommendation: value})}
                      className={`p-3 rounded border-2 cursor-pointer ${editForm.recommendation === value ? color : 'bg-white border-gray-200'}`}
                    >
                      <div className="flex items-center gap-2">
                        <div className={`w-4 h-4 rounded-full border-2 ${editForm.recommendation === value ? 'bg-current' : ''}`} />
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
                        <SelectTrigger className="w-20">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="C">C</SelectItem>
                          <SelectItem value="NC">NC</SelectItem>
                          <SelectItem value="O">O</SelectItem>
                        </SelectContent>
                      </Select>
                      <Input
                        value={item.comments}
                        onChange={(e) => updateChecklistItem(idx, 'comments', e.target.value)}
                        placeholder="Comments"
                        className="w-32"
                      />
                    </div>
                  ))}
                </div>
              </details>
              
              {/* Notes */}
              <div>
                <Label>{t('additionalNotes') || 'Additional Notes'}</Label>
                <Textarea
                  value={editForm.notes}
                  onChange={(e) => setEditForm({...editForm, notes: e.target.value})}
                  rows={3}
                />
              </div>
              
              <div className="flex gap-2 justify-end">
                <Button variant="outline" onClick={() => setShowEditModal(false)}>{t('cancel') || 'Cancel'}</Button>
                <Button onClick={updateReport} data-testid="save-report-btn" className="bg-red-600 hover:bg-red-700">
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
