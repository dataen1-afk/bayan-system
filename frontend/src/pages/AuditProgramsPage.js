import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import axios from 'axios';
import { 
  ClipboardCheck, Plus, Download, Eye, Trash2, Save,
  CheckCircle, Clock, AlertCircle, Building, Calendar,
  Users, FileText, X, Check
} from 'lucide-react';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '../components/ui/dialog';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function AuditProgramsPage() {
  const { t, i18n } = useTranslation();
  const isRTL = i18n.language === 'ar';
  
  const [programs, setPrograms] = useState([]);
  const [contractReviews, setContractReviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [selectedProgram, setSelectedProgram] = useState(null);
  const [selectedReviewId, setSelectedReviewId] = useState('');
  
  // Form state for editing
  const [editForm, setEditForm] = useState({
    num_shifts: 1,
    activities: [],
    certification_manager: '',
    approval_date: '',
    notes: ''
  });
  
  useEffect(() => {
    fetchData();
  }, []);
  
  const fetchData = async () => {
    try {
      const token = localStorage.getItem('token');
      const headers = { Authorization: `Bearer ${token}` };
      
      const [programsRes, reviewsRes] = await Promise.all([
        axios.get(`${API_URL}/api/audit-programs`, { headers }),
        axios.get(`${API_URL}/api/contract-reviews`, { headers })
      ]);
      
      setPrograms(programsRes.data);
      setContractReviews(reviewsRes.data);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const createAuditProgram = async () => {
    if (!selectedReviewId) return;
    
    try {
      const token = localStorage.getItem('token');
      await axios.post(
        `${API_URL}/api/audit-programs`,
        { contract_review_id: selectedReviewId },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setShowCreateModal(false);
      setSelectedReviewId('');
      fetchData();
    } catch (error) {
      console.error('Error creating audit program:', error);
      alert(error.response?.data?.detail || 'Error creating audit program');
    }
  };
  
  const updateAuditProgram = async () => {
    if (!selectedProgram) return;
    
    try {
      const token = localStorage.getItem('token');
      await axios.put(
        `${API_URL}/api/audit-programs/${selectedProgram.id}`,
        editForm,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setShowEditModal(false);
      fetchData();
    } catch (error) {
      console.error('Error updating audit program:', error);
    }
  };
  
  const deleteAuditProgram = async (id) => {
    if (!window.confirm(t('confirmDelete') || 'Are you sure you want to delete this audit program?')) return;
    
    try {
      const token = localStorage.getItem('token');
      await axios.delete(`${API_URL}/api/audit-programs/${id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      fetchData();
    } catch (error) {
      console.error('Error deleting audit program:', error);
    }
  };
  
  const approveAuditProgram = async (id) => {
    try {
      const token = localStorage.getItem('token');
      await axios.post(
        `${API_URL}/api/audit-programs/${id}/approve`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      fetchData();
    } catch (error) {
      console.error('Error approving audit program:', error);
    }
  };
  
  const downloadPDF = async (program) => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(
        `${API_URL}/api/audit-programs/${program.id}/pdf`,
        { 
          headers: { Authorization: `Bearer ${token}` },
          responseType: 'blob'
        }
      );
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `audit_program_${program.organization_name.replace(/\s+/g, '_')}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error('Error downloading PDF:', error);
    }
  };
  
  const openEditModal = (program) => {
    setSelectedProgram(program);
    setEditForm({
      num_shifts: program.num_shifts || 1,
      activities: program.activities || [],
      certification_manager: program.certification_manager || '',
      approval_date: program.approval_date || '',
      notes: program.notes || ''
    });
    setShowEditModal(true);
  };
  
  const addActivity = () => {
    setEditForm({
      ...editForm,
      activities: [
        ...editForm.activities,
        { activity: '', audit_type: '', stage1: '', stage2: '', sur1: '', sur2: '', rc: '', planned_date: '' }
      ]
    });
  };
  
  const updateActivity = (index, field, value) => {
    const newActivities = [...editForm.activities];
    newActivities[index] = { ...newActivities[index], [field]: value };
    setEditForm({ ...editForm, activities: newActivities });
  };
  
  const removeActivity = (index) => {
    const newActivities = editForm.activities.filter((_, i) => i !== index);
    setEditForm({ ...editForm, activities: newActivities });
  };
  
  const getStatusBadge = (status) => {
    const statusConfig = {
      'draft': { color: 'bg-gray-100 text-gray-800', icon: Clock, label: t('draft') || 'Draft' },
      'approved': { color: 'bg-green-100 text-green-800', icon: CheckCircle, label: t('approved') || 'Approved' },
      'in_progress': { color: 'bg-blue-100 text-blue-800', icon: AlertCircle, label: t('inProgress') || 'In Progress' },
      'completed': { color: 'bg-purple-100 text-purple-800', icon: CheckCircle, label: t('completed') || 'Completed' }
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
  
  // Get contract reviews that don't have an audit program yet
  const availableReviews = contractReviews.filter(
    r => r.status === 'completed' && !programs.some(p => p.contract_review_id === r.id)
  );
  
  const stats = {
    total: programs.length,
    draft: programs.filter(p => p.status === 'draft').length,
    approved: programs.filter(p => p.status === 'approved').length,
    completed: programs.filter(p => p.status === 'completed').length
  };

  return (
    <div className={`p-6 ${isRTL ? 'rtl' : 'ltr'}`} dir={isRTL ? 'rtl' : 'ltr'}>
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{t('auditPrograms') || 'Audit Programs'}</h1>
          <p className="text-gray-500">BACF6-05 - {t('auditProgramDescription') || 'Schedule audit stages and activities'}</p>
        </div>
        <Button onClick={() => setShowCreateModal(true)} className="bg-emerald-600 hover:bg-emerald-700" data-testid="create-audit-program-btn">
          <Plus className="w-4 h-4 mr-2" />
          {t('createAuditProgram') || 'Create Audit Program'}
        </Button>
      </div>
      
      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <Card>
          <CardContent className="p-4 flex items-center gap-4">
            <div className="p-3 bg-blue-100 rounded-lg">
              <ClipboardCheck className="w-6 h-6 text-blue-600" />
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
            <div className="p-3 bg-green-100 rounded-lg">
              <CheckCircle className="w-6 h-6 text-green-600" />
            </div>
            <div>
              <p className="text-2xl font-bold">{stats.approved}</p>
              <p className="text-sm text-gray-500">{t('approved') || 'Approved'}</p>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4 flex items-center gap-4">
            <div className="p-3 bg-purple-100 rounded-lg">
              <FileText className="w-6 h-6 text-purple-600" />
            </div>
            <div>
              <p className="text-2xl font-bold">{stats.completed}</p>
              <p className="text-sm text-gray-500">{t('completed') || 'Completed'}</p>
            </div>
          </CardContent>
        </Card>
      </div>
      
      {/* Programs List */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <ClipboardCheck className="w-5 h-5" />
            {t('auditPrograms') || 'Audit Programs'}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8">Loading...</div>
          ) : programs.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <ClipboardCheck className="w-12 h-12 mx-auto mb-4 opacity-50" />
              <p>{t('noAuditPrograms') || 'No audit programs yet'}</p>
              <p className="text-sm mt-2">{t('createFromContractReview') || 'Create an audit program from a completed contract review'}</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left p-3 font-medium text-gray-600">{t('organizationName') || 'Organization'}</th>
                    <th className="text-left p-3 font-medium text-gray-600">{t('standards') || 'Standards'}</th>
                    <th className="text-left p-3 font-medium text-gray-600">{t('activities') || 'Activities'}</th>
                    <th className="text-left p-3 font-medium text-gray-600">{t('status') || 'Status'}</th>
                    <th className="text-left p-3 font-medium text-gray-600">{t('actions') || 'Actions'}</th>
                  </tr>
                </thead>
                <tbody>
                  {programs.map(program => (
                    <tr key={program.id} className="border-b hover:bg-gray-50" data-testid={`audit-program-row-${program.id}`}>
                      <td className="p-3">
                        <div className="flex items-center gap-2">
                          <Building className="w-4 h-4 text-gray-400" />
                          <span className="font-medium">{program.organization_name}</span>
                        </div>
                      </td>
                      <td className="p-3">
                        <div className="flex flex-wrap gap-1">
                          {(program.standards || []).map((std, idx) => (
                            <span key={idx} className="px-2 py-0.5 bg-blue-100 text-blue-800 text-xs rounded">
                              {std}
                            </span>
                          ))}
                        </div>
                      </td>
                      <td className="p-3">
                        <span className="text-gray-600">{(program.activities || []).length} {t('activities') || 'activities'}</span>
                      </td>
                      <td className="p-3">{getStatusBadge(program.status)}</td>
                      <td className="p-3">
                        <div className="flex gap-2">
                          <Button 
                            size="sm" 
                            variant="outline"
                            onClick={() => openEditModal(program)}
                            data-testid={`edit-program-${program.id}`}
                            title={t('edit') || 'Edit'}
                          >
                            <Eye className="w-4 h-4" />
                          </Button>
                          {program.status === 'draft' && (
                            <Button 
                              size="sm" 
                              variant="outline"
                              onClick={() => approveAuditProgram(program.id)}
                              data-testid={`approve-program-${program.id}`}
                              title={t('approve') || 'Approve'}
                              className="text-green-600 hover:text-green-700"
                            >
                              <Check className="w-4 h-4" />
                            </Button>
                          )}
                          <Button 
                            size="sm" 
                            className="bg-emerald-600 hover:bg-emerald-700"
                            onClick={() => downloadPDF(program)}
                            data-testid={`download-pdf-${program.id}`}
                            title={t('downloadPDF') || 'Download PDF'}
                          >
                            <Download className="w-4 h-4" />
                          </Button>
                          <Button 
                            size="sm" 
                            variant="destructive"
                            onClick={() => deleteAuditProgram(program.id)}
                            data-testid={`delete-program-${program.id}`}
                            title={t('delete') || 'Delete'}
                          >
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
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>{t('createAuditProgram') || 'Create Audit Program'}</DialogTitle>
            <DialogDescription>{t('selectContractReview') || 'Select a completed contract review to create an audit program'}</DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label>{t('selectContractReview') || 'Select Contract Review'}</Label>
              <Select value={selectedReviewId} onValueChange={setSelectedReviewId}>
                <SelectTrigger data-testid="select-contract-review">
                  <SelectValue placeholder={t('selectContractReview') || 'Select a contract review...'} />
                </SelectTrigger>
                <SelectContent>
                  {availableReviews.map(review => (
                    <SelectItem key={review.id} value={review.id}>
                      {review.organization_name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {availableReviews.length === 0 && (
                <p className="text-sm text-gray-500 mt-2">{t('noCompletedReviews') || 'No completed contract reviews available'}</p>
              )}
            </div>
            <div className="flex gap-2 justify-end">
              <Button variant="outline" onClick={() => setShowCreateModal(false)}>{t('cancel') || 'Cancel'}</Button>
              <Button onClick={createAuditProgram} disabled={!selectedReviewId} data-testid="create-program-submit">{t('create') || 'Create'}</Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
      
      {/* Edit Modal */}
      <Dialog open={showEditModal} onOpenChange={setShowEditModal}>
        <DialogContent className="max-w-5xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>{t('auditProgramDetails') || 'Audit Program Details'}</DialogTitle>
            <DialogDescription>{selectedProgram?.organization_name}</DialogDescription>
          </DialogHeader>
          <div className="space-y-6">
            {/* Basic Info */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>{t('organizationName') || 'Organization Name'}</Label>
                <Input value={selectedProgram?.organization_name || ''} disabled />
              </div>
              <div>
                <Label>{t('standards') || 'Standards'}</Label>
                <Input value={(selectedProgram?.standards || []).join(', ')} disabled />
              </div>
              <div>
                <Label>{t('numShifts') || 'Number of Shifts'}</Label>
                <Input
                  type="number"
                  value={editForm.num_shifts}
                  onChange={(e) => setEditForm({...editForm, num_shifts: parseInt(e.target.value) || 1})}
                  min="1"
                />
              </div>
            </div>
            
            {/* Activities Table */}
            <div className="border-t pt-4">
              <div className="flex justify-between items-center mb-3">
                <h3 className="font-semibold">{t('auditActivities') || 'Audit Activities'}</h3>
                <Button size="sm" variant="outline" onClick={addActivity}>
                  <Plus className="w-4 h-4 mr-1" />
                  {t('addActivity') || 'Add Activity'}
                </Button>
              </div>
              
              <div className="overflow-x-auto">
                <table className="w-full text-sm border">
                  <thead>
                    <tr className="bg-gray-100">
                      <th className="p-2 border text-left">{t('activity') || 'Activity'}</th>
                      <th className="p-2 border text-left">{t('auditType') || 'Audit Type'}</th>
                      <th className="p-2 border text-center">Stage 1</th>
                      <th className="p-2 border text-center">Stage 2</th>
                      <th className="p-2 border text-center">SUR 1</th>
                      <th className="p-2 border text-center">SUR 2</th>
                      <th className="p-2 border text-center">RC</th>
                      <th className="p-2 border text-center">{t('plannedDate') || 'Planned Date'}</th>
                      <th className="p-2 border"></th>
                    </tr>
                  </thead>
                  <tbody>
                    {editForm.activities.map((activity, idx) => (
                      <tr key={idx} className="hover:bg-gray-50">
                        <td className="p-1 border">
                          <Input
                            value={activity.activity}
                            onChange={(e) => updateActivity(idx, 'activity', e.target.value)}
                            className="h-8"
                            placeholder="Activity name"
                          />
                        </td>
                        <td className="p-1 border">
                          <Select value={activity.audit_type} onValueChange={(v) => updateActivity(idx, 'audit_type', v)}>
                            <SelectTrigger className="h-8">
                              <SelectValue placeholder="Type" />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="Desktop">Desktop</SelectItem>
                              <SelectItem value="On-site">On-site</SelectItem>
                              <SelectItem value="Remote">Remote</SelectItem>
                            </SelectContent>
                          </Select>
                        </td>
                        <td className="p-1 border">
                          <Input
                            value={activity.stage1}
                            onChange={(e) => updateActivity(idx, 'stage1', e.target.value)}
                            className="h-8 w-16 text-center"
                            placeholder="Days"
                          />
                        </td>
                        <td className="p-1 border">
                          <Input
                            value={activity.stage2}
                            onChange={(e) => updateActivity(idx, 'stage2', e.target.value)}
                            className="h-8 w-16 text-center"
                            placeholder="Days"
                          />
                        </td>
                        <td className="p-1 border">
                          <Input
                            value={activity.sur1}
                            onChange={(e) => updateActivity(idx, 'sur1', e.target.value)}
                            className="h-8 w-16 text-center"
                            placeholder="Days"
                          />
                        </td>
                        <td className="p-1 border">
                          <Input
                            value={activity.sur2}
                            onChange={(e) => updateActivity(idx, 'sur2', e.target.value)}
                            className="h-8 w-16 text-center"
                            placeholder="Days"
                          />
                        </td>
                        <td className="p-1 border">
                          <Input
                            value={activity.rc}
                            onChange={(e) => updateActivity(idx, 'rc', e.target.value)}
                            className="h-8 w-16 text-center"
                            placeholder="Days"
                          />
                        </td>
                        <td className="p-1 border">
                          <Input
                            type="date"
                            value={activity.planned_date}
                            onChange={(e) => updateActivity(idx, 'planned_date', e.target.value)}
                            className="h-8"
                          />
                        </td>
                        <td className="p-1 border">
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => removeActivity(idx)}
                            className="h-8 w-8 p-0 text-red-500 hover:text-red-700"
                          >
                            <X className="w-4 h-4" />
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
            
            {/* Approval Section */}
            <div className="border-t pt-4">
              <h3 className="font-semibold mb-3">{t('approval') || 'Approval'}</h3>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>{t('certificationManager') || 'Certification Manager'}</Label>
                  <Input
                    value={editForm.certification_manager}
                    onChange={(e) => setEditForm({...editForm, certification_manager: e.target.value})}
                    placeholder="Enter name..."
                  />
                </div>
                <div>
                  <Label>{t('approvalDate') || 'Approval Date'}</Label>
                  <Input
                    type="date"
                    value={editForm.approval_date}
                    onChange={(e) => setEditForm({...editForm, approval_date: e.target.value})}
                  />
                </div>
                <div className="col-span-2">
                  <Label>{t('notes') || 'Notes'}</Label>
                  <Textarea
                    value={editForm.notes}
                    onChange={(e) => setEditForm({...editForm, notes: e.target.value})}
                    placeholder="Additional notes..."
                    rows={3}
                  />
                </div>
              </div>
            </div>
            
            <div className="flex gap-2 justify-end">
              <Button variant="outline" onClick={() => setShowEditModal(false)}>{t('cancel') || 'Cancel'}</Button>
              <Button onClick={updateAuditProgram} data-testid="save-program-btn">
                <Save className="w-4 h-4 mr-2" />
                {t('saveChanges') || 'Save Changes'}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
