import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import axios from 'axios';
import { 
  FileText, Plus, Eye, Edit, Trash2, Download, CheckCircle,
  ClipboardList, Calendar, User, MapPin, Building, Tag
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

export default function AuditorNotesPage() {
  const { t, i18n } = useTranslation();
  const isRTL = i18n.language === 'ar';
  
  const [notesList, setNotesList] = useState([]);
  const [stage2Reports, setStage2Reports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showViewModal, setShowViewModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [selectedNotes, setSelectedNotes] = useState(null);
  
  // Create form state
  const [createMode, setCreateMode] = useState('report'); // 'report' or 'manual'
  const [selectedReportId, setSelectedReportId] = useState('');
  const [formData, setFormData] = useState({
    client_name: '',
    location: '',
    standards: [],
    auditor_name: '',
    audit_type: '',
    audit_date: '',
    department: '',
    notes: '',
    notes_ar: ''
  });

  const token = localStorage.getItem('token');
  const headers = { Authorization: `Bearer ${token}` };

  useEffect(() => {
    fetchNotes();
    fetchStage2Reports();
  }, []);

  const fetchNotes = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/auditor-notes`, { headers });
      setNotesList(response.data);
    } catch (error) {
      console.error('Error fetching auditor notes:', error);
      toast.error(t('auditorNotes.fetchError'));
    } finally {
      setLoading(false);
    }
  };

  const fetchStage2Reports = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/stage2-audit-reports`, { headers });
      // Filter to show only approved reports
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
      
      const response = await axios.post(`${API_URL}/api/auditor-notes`, payload, { headers });
      setNotesList([response.data, ...notesList]);
      setShowCreateModal(false);
      resetForm();
      toast.success(t('auditorNotes.createSuccess'));
    } catch (error) {
      console.error('Error creating auditor notes:', error);
      toast.error(t('auditorNotes.createError'));
    }
  };

  const handleUpdate = async () => {
    if (!selectedNotes) return;
    
    try {
      const response = await axios.put(
        `${API_URL}/api/auditor-notes/${selectedNotes.id}`,
        formData,
        { headers }
      );
      setNotesList(notesList.map(n => n.id === selectedNotes.id ? response.data : n));
      setShowEditModal(false);
      toast.success(t('auditorNotes.updateSuccess'));
    } catch (error) {
      console.error('Error updating auditor notes:', error);
      toast.error(t('auditorNotes.updateError'));
    }
  };

  const handleDelete = async (notesId) => {
    if (!window.confirm(t('auditorNotes.confirmDelete'))) return;
    
    try {
      await axios.delete(`${API_URL}/api/auditor-notes/${notesId}`, { headers });
      setNotesList(notesList.filter(n => n.id !== notesId));
      toast.success(t('auditorNotes.deleteSuccess'));
    } catch (error) {
      console.error('Error deleting auditor notes:', error);
      toast.error(t('auditorNotes.deleteError'));
    }
  };

  const handleComplete = async (notesId) => {
    try {
      await axios.post(`${API_URL}/api/auditor-notes/${notesId}/complete`, {}, { headers });
      setNotesList(notesList.map(n => 
        n.id === notesId ? { ...n, status: 'completed' } : n
      ));
      toast.success(t('auditorNotes.completeSuccess'));
    } catch (error) {
      console.error('Error completing auditor notes:', error);
      toast.error(t('auditorNotes.completeError'));
    }
  };

  const handleDownloadPDF = async (notesId) => {
    try {
      const response = await axios.get(
        `${API_URL}/api/auditor-notes/${notesId}/pdf`,
        { headers, responseType: 'blob' }
      );
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `auditor_notes_${notesId.slice(0, 8)}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error('Error downloading PDF:', error);
      toast.error(t('auditorNotes.pdfError'));
    }
  };

  const resetForm = () => {
    setFormData({
      client_name: '',
      location: '',
      standards: [],
      auditor_name: '',
      audit_type: '',
      audit_date: '',
      department: '',
      notes: '',
      notes_ar: ''
    });
    setSelectedReportId('');
    setCreateMode('report');
  };

  const openEditModal = (notes) => {
    setSelectedNotes(notes);
    setFormData({
      client_name: notes.client_name || '',
      location: notes.location || '',
      standards: notes.standards || [],
      auditor_name: notes.auditor_name || '',
      audit_type: notes.audit_type || '',
      audit_date: notes.audit_date || '',
      department: notes.department || '',
      notes: notes.notes || '',
      notes_ar: notes.notes_ar || ''
    });
    setShowEditModal(true);
  };

  const openViewModal = (notes) => {
    setSelectedNotes(notes);
    setShowViewModal(true);
  };

  // Stats
  const stats = {
    total: notesList.length,
    draft: notesList.filter(n => n.status === 'draft').length,
    completed: notesList.filter(n => n.status === 'completed').length
  };

  const getStatusBadge = (status) => {
    const styles = {
      draft: 'bg-yellow-100 text-yellow-800',
      completed: 'bg-green-100 text-green-800'
    };
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${styles[status] || 'bg-gray-100'}`}>
        {t(`auditorNotes.status.${status}`)}
      </span>
    );
  };

  return (
    <div className={`p-6 space-y-6 ${isRTL ? 'rtl' : 'ltr'}`} dir={isRTL ? 'rtl' : 'ltr'}>
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            {t('auditorNotes.title')}
          </h1>
          <p className="text-gray-500 mt-1">{t('auditorNotes.subtitle')}</p>
        </div>
        <Button onClick={() => setShowCreateModal(true)} data-testid="create-auditor-notes-btn">
          <Plus className="w-4 h-4 mr-2" />
          {t('auditorNotes.create')}
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-500">
              {t('auditorNotes.stats.total')}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.total}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-500">
              {t('auditorNotes.stats.draft')}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">{stats.draft}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-500">
              {t('auditorNotes.stats.completed')}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{stats.completed}</div>
          </CardContent>
        </Card>
      </div>

      {/* Notes List */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <ClipboardList className="w-5 h-5" />
            {t('auditorNotes.listTitle')}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8 text-gray-500">{t('common.loading')}</div>
          ) : notesList.length === 0 ? (
            <div className="text-center py-8 text-gray-500">{t('auditorNotes.empty')}</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full" data-testid="auditor-notes-table">
                <thead>
                  <tr className="border-b">
                    <th className="text-start p-3 font-medium">{t('auditorNotes.clientName')}</th>
                    <th className="text-start p-3 font-medium">{t('auditorNotes.auditType')}</th>
                    <th className="text-start p-3 font-medium">{t('auditorNotes.auditor')}</th>
                    <th className="text-start p-3 font-medium">{t('auditorNotes.date')}</th>
                    <th className="text-start p-3 font-medium">{t('auditorNotes.statusLabel')}</th>
                    <th className="text-start p-3 font-medium">{t('actions')}</th>
                  </tr>
                </thead>
                <tbody>
                  {notesList.map((notes) => (
                    <tr key={notes.id} className="border-b hover:bg-gray-50">
                      <td className="p-3">
                        <div className="font-medium">{notes.client_name}</div>
                        <div className="text-sm text-gray-500">{notes.location}</div>
                      </td>
                      <td className="p-3">{notes.audit_type}</td>
                      <td className="p-3">{notes.auditor_name}</td>
                      <td className="p-3">{notes.audit_date}</td>
                      <td className="p-3">{getStatusBadge(notes.status)}</td>
                      <td className="p-3">
                        <div className="flex gap-1">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => openViewModal(notes)}
                            title={t('common.view')}
                          >
                            <Eye className="w-4 h-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => openEditModal(notes)}
                            title={t('common.edit')}
                          >
                            <Edit className="w-4 h-4" />
                          </Button>
                          {notes.status === 'draft' && (
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleComplete(notes.id)}
                              title={t('auditorNotes.markComplete')}
                              className="text-green-600"
                            >
                              <CheckCircle className="w-4 h-4" />
                            </Button>
                          )}
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleDownloadPDF(notes.id)}
                            title={t('common.downloadPDF')}
                            className="text-blue-600"
                          >
                            <Download className="w-4 h-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleDelete(notes.id)}
                            title={t('common.delete')}
                            className="text-red-600"
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
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>{t('auditorNotes.createTitle')}</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            {/* Creation Mode Selection */}
            <div className="space-y-2">
              <Label>{t('auditorNotes.createMode')}</Label>
              <Select value={createMode} onValueChange={setCreateMode}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="report">{t('auditorNotes.fromReport')}</SelectItem>
                  <SelectItem value="manual">{t('auditorNotes.manual')}</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {createMode === 'report' ? (
              <div className="space-y-2">
                <Label>{t('auditorNotes.selectReport')}</Label>
                <Select value={selectedReportId} onValueChange={setSelectedReportId}>
                  <SelectTrigger>
                    <SelectValue placeholder={t('auditorNotes.selectReportPlaceholder')} />
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
                    <Label>{t('auditorNotes.clientName')}</Label>
                    <Input
                      value={formData.client_name}
                      onChange={(e) => setFormData({ ...formData, client_name: e.target.value })}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>{t('auditorNotes.location')}</Label>
                    <Input
                      value={formData.location}
                      onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                    />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>{t('auditorNotes.auditor')}</Label>
                    <Input
                      value={formData.auditor_name}
                      onChange={(e) => setFormData({ ...formData, auditor_name: e.target.value })}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>{t('auditorNotes.auditType')}</Label>
                    <Select 
                      value={formData.audit_type} 
                      onValueChange={(v) => setFormData({ ...formData, audit_type: v })}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
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
                    <Label>{t('auditorNotes.date')}</Label>
                    <Input
                      type="date"
                      value={formData.audit_date}
                      onChange={(e) => setFormData({ ...formData, audit_date: e.target.value })}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>{t('auditorNotes.department')}</Label>
                    <Input
                      value={formData.department}
                      onChange={(e) => setFormData({ ...formData, department: e.target.value })}
                    />
                  </div>
                </div>
              </>
            )}

            <div className="flex justify-end gap-2 pt-4">
              <Button variant="outline" onClick={() => setShowCreateModal(false)}>
                {t('common.cancel')}
              </Button>
              <Button 
                onClick={handleCreate}
                disabled={createMode === 'report' && !selectedReportId}
              >
                {t('common.create')}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* View Modal */}
      <Dialog open={showViewModal} onOpenChange={setShowViewModal}>
        <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>{t('auditorNotes.viewTitle')}</DialogTitle>
          </DialogHeader>
          {selectedNotes && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1">
                  <div className="text-sm text-gray-500 flex items-center gap-2">
                    <Building className="w-4 h-4" />
                    {t('auditorNotes.clientName')}
                  </div>
                  <div className="font-medium">{selectedNotes.client_name || '—'}</div>
                </div>
                <div className="space-y-1">
                  <div className="text-sm text-gray-500 flex items-center gap-2">
                    <MapPin className="w-4 h-4" />
                    {t('auditorNotes.location')}
                  </div>
                  <div className="font-medium">{selectedNotes.location || '—'}</div>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1">
                  <div className="text-sm text-gray-500 flex items-center gap-2">
                    <Tag className="w-4 h-4" />
                    {t('auditorNotes.standards')}
                  </div>
                  <div className="font-medium">{selectedNotes.standards?.join(', ') || '—'}</div>
                </div>
                <div className="space-y-1">
                  <div className="text-sm text-gray-500 flex items-center gap-2">
                    <User className="w-4 h-4" />
                    {t('auditorNotes.auditor')}
                  </div>
                  <div className="font-medium">{selectedNotes.auditor_name || '—'}</div>
                </div>
              </div>
              <div className="grid grid-cols-3 gap-4">
                <div className="space-y-1">
                  <div className="text-sm text-gray-500">{t('auditorNotes.auditType')}</div>
                  <div className="font-medium">{selectedNotes.audit_type || '—'}</div>
                </div>
                <div className="space-y-1">
                  <div className="text-sm text-gray-500 flex items-center gap-2">
                    <Calendar className="w-4 h-4" />
                    {t('auditorNotes.date')}
                  </div>
                  <div className="font-medium">{selectedNotes.audit_date || '—'}</div>
                </div>
                <div className="space-y-1">
                  <div className="text-sm text-gray-500">{t('auditorNotes.department')}</div>
                  <div className="font-medium">{selectedNotes.department || '—'}</div>
                </div>
              </div>
              
              {/* Notes Content */}
              <div className="border-t pt-4">
                <div className="text-sm text-gray-500 mb-2 flex items-center gap-2">
                  <FileText className="w-4 h-4" />
                  {t('auditorNotes.notesContent')}
                </div>
                <div className="bg-gray-50 p-4 rounded-lg whitespace-pre-wrap min-h-[100px]">
                  {selectedNotes.notes || t('auditorNotes.noNotes')}
                </div>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* Edit Modal */}
      <Dialog open={showEditModal} onOpenChange={setShowEditModal}>
        <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>{t('auditorNotes.editTitle')}</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>{t('auditorNotes.clientName')}</Label>
                <Input
                  value={formData.client_name}
                  onChange={(e) => setFormData({ ...formData, client_name: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label>{t('auditorNotes.location')}</Label>
                <Input
                  value={formData.location}
                  onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>{t('auditorNotes.auditor')}</Label>
                <Input
                  value={formData.auditor_name}
                  onChange={(e) => setFormData({ ...formData, auditor_name: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label>{t('auditorNotes.auditType')}</Label>
                <Select 
                  value={formData.audit_type} 
                  onValueChange={(v) => setFormData({ ...formData, audit_type: v })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
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
                <Label>{t('auditorNotes.date')}</Label>
                <Input
                  type="date"
                  value={formData.audit_date}
                  onChange={(e) => setFormData({ ...formData, audit_date: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label>{t('auditorNotes.department')}</Label>
                <Input
                  value={formData.department}
                  onChange={(e) => setFormData({ ...formData, department: e.target.value })}
                />
              </div>
            </div>
            
            {/* Notes Text Area */}
            <div className="space-y-2">
              <Label>{t('auditorNotes.notesContent')}</Label>
              <Textarea
                value={formData.notes}
                onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                rows={8}
                placeholder={t('auditorNotes.notesPlaceholder')}
              />
            </div>

            <div className="flex justify-end gap-2 pt-4">
              <Button variant="outline" onClick={() => setShowEditModal(false)}>
                {t('common.cancel')}
              </Button>
              <Button onClick={handleUpdate}>
                {t('common.save')}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
