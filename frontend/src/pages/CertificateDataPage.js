import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import axios from 'axios';
import { 
  Award, Plus, Eye, Edit, Trash2, Download, Send, CheckCircle,
  FileCheck, Calendar, User, Building, Tag, ExternalLink
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

export default function CertificateDataPage() {
  const { t, i18n } = useTranslation();
  const isRTL = i18n.language === 'ar';
  
  const [recordsList, setRecordsList] = useState([]);
  const [ncReports, setNCReports] = useState([]);
  const [stage2Reports, setStage2Reports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showViewModal, setShowViewModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [selectedRecord, setSelectedRecord] = useState(null);
  
  const [createMode, setCreateMode] = useState('nc');
  const [selectedNCId, setSelectedNCId] = useState('');
  const [selectedReportId, setSelectedReportId] = useState('');
  const [formData, setFormData] = useState({
    client_name: '',
    standards: [],
    lead_auditor: '',
    audit_type: '',
    audit_date: '',
    agreed_certification_scope: '',
    ea_code: '',
    technical_category: '',
    company_data_local: '',
    certification_scope_local: '',
    company_data_english: '',
    certification_scope_english: ''
  });

  const token = localStorage.getItem('token');
  const headers = { Authorization: `Bearer ${token}` };

  useEffect(() => {
    fetchRecords();
    fetchNCReports();
    fetchStage2Reports();
  }, []);

  const fetchRecords = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/certificate-data`, { headers });
      setRecordsList(response.data);
    } catch (error) {
      console.error('Error fetching certificate data:', error);
      toast.error(t('certData.fetchError'));
    } finally {
      setLoading(false);
    }
  };

  const fetchNCReports = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/nonconformity-reports`, { headers });
      setNCReports(response.data.filter(r => r.status === 'closed'));
    } catch (error) {
      console.error('Error fetching NC reports:', error);
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
      let payload = {};
      if (createMode === 'nc' && selectedNCId) {
        payload = { nc_report_id: selectedNCId };
      } else if (createMode === 'report' && selectedReportId) {
        payload = { stage2_report_id: selectedReportId };
      } else {
        payload = formData;
      }
      
      const response = await axios.post(`${API_URL}/api/certificate-data`, payload, { headers });
      setRecordsList([response.data, ...recordsList]);
      setShowCreateModal(false);
      resetForm();
      toast.success(t('certData.createSuccess'));
    } catch (error) {
      console.error('Error creating certificate data:', error);
      toast.error(t('certData.createError'));
    }
  };

  const handleUpdate = async () => {
    if (!selectedRecord) return;
    
    try {
      const response = await axios.put(
        `${API_URL}/api/certificate-data/${selectedRecord.id}`,
        formData,
        { headers }
      );
      setRecordsList(recordsList.map(r => r.id === selectedRecord.id ? response.data : r));
      setShowEditModal(false);
      toast.success(t('certData.updateSuccess'));
    } catch (error) {
      console.error('Error updating certificate data:', error);
      toast.error(t('certData.updateError'));
    }
  };

  const handleDelete = async (recordId) => {
    if (!window.confirm(t('certData.confirmDelete'))) return;
    
    try {
      await axios.delete(`${API_URL}/api/certificate-data/${recordId}`, { headers });
      setRecordsList(recordsList.filter(r => r.id !== recordId));
      toast.success(t('certData.deleteSuccess'));
    } catch (error) {
      console.error('Error deleting certificate data:', error);
      toast.error(t('certData.deleteError'));
    }
  };

  const handleSendToClient = async (recordId) => {
    try {
      const response = await axios.post(
        `${API_URL}/api/certificate-data/${recordId}/send-to-client`,
        {},
        { headers }
      );
      setRecordsList(recordsList.map(r => 
        r.id === recordId ? { ...r, status: 'sent_to_client' } : r
      ));
      
      // Copy URL to clipboard
      navigator.clipboard.writeText(response.data.public_url);
      toast.success(t('certData.sentSuccess') + ' - URL copied to clipboard!');
    } catch (error) {
      console.error('Error sending to client:', error);
      toast.error(t('certData.sentError'));
    }
  };

  const handleIssueCertificate = async (recordId) => {
    try {
      const response = await axios.post(
        `${API_URL}/api/certificate-data/${recordId}/issue-certificate`,
        {},
        { headers }
      );
      await fetchRecords();
      toast.success(`${t('certData.certIssued')} - ${response.data.certificate_number}`);
    } catch (error) {
      console.error('Error issuing certificate:', error);
      toast.error(error.response?.data?.detail || t('certData.certError'));
    }
  };

  const handleDownloadPDF = async (recordId) => {
    try {
      const response = await axios.get(
        `${API_URL}/api/certificate-data/${recordId}/pdf`,
        { headers, responseType: 'blob' }
      );
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `certificate_data_${recordId.slice(0, 8)}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error('Error downloading PDF:', error);
      toast.error(t('certData.pdfError'));
    }
  };

  const resetForm = () => {
    setFormData({
      client_name: '',
      standards: [],
      lead_auditor: '',
      audit_type: '',
      audit_date: '',
      agreed_certification_scope: '',
      ea_code: '',
      technical_category: '',
      company_data_local: '',
      certification_scope_local: '',
      company_data_english: '',
      certification_scope_english: ''
    });
    setSelectedNCId('');
    setSelectedReportId('');
    setCreateMode('nc');
  };

  const openEditModal = (record) => {
    setSelectedRecord(record);
    setFormData({
      client_name: record.client_name || '',
      standards: record.standards || [],
      lead_auditor: record.lead_auditor || '',
      audit_type: record.audit_type || '',
      audit_date: record.audit_date || '',
      agreed_certification_scope: record.agreed_certification_scope || '',
      ea_code: record.ea_code || '',
      technical_category: record.technical_category || '',
      company_data_local: record.company_data_local || '',
      certification_scope_local: record.certification_scope_local || '',
      company_data_english: record.company_data_english || '',
      certification_scope_english: record.certification_scope_english || ''
    });
    setShowEditModal(true);
  };

  const openViewModal = (record) => {
    setSelectedRecord(record);
    setShowViewModal(true);
  };

  // Stats
  const stats = {
    total: recordsList.length,
    draft: recordsList.filter(r => r.status === 'draft').length,
    sentToClient: recordsList.filter(r => r.status === 'sent_to_client').length,
    confirmed: recordsList.filter(r => r.status === 'client_confirmed').length,
    issued: recordsList.filter(r => r.status === 'certificate_issued').length
  };

  const getStatusBadge = (status) => {
    const styles = {
      draft: 'bg-gray-100 text-gray-800',
      sent_to_client: 'bg-blue-100 text-blue-800',
      client_confirmed: 'bg-yellow-100 text-yellow-800',
      certificate_issued: 'bg-green-100 text-green-800'
    };
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${styles[status] || 'bg-gray-100'}`}>
        {t(`certData.status.${status}`)}
      </span>
    );
  };

  return (
    <div className={`p-6 space-y-6 ${isRTL ? 'rtl' : 'ltr'}`} dir={isRTL ? 'rtl' : 'ltr'}>
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{t('certData.title')}</h1>
          <p className="text-gray-500 mt-1">{t('certData.subtitle')}</p>
        </div>
        <Button onClick={() => setShowCreateModal(true)} data-testid="create-cert-data-btn">
          <Plus className="w-4 h-4 mr-2" />
          {t('certData.create')}
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-500">{t('certData.stats.total')}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.total}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-500">{t('certData.stats.draft')}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-gray-600">{stats.draft}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-500">{t('certData.stats.sentToClient')}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">{stats.sentToClient}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-500">{t('certData.stats.confirmed')}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">{stats.confirmed}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-500">{t('certData.stats.issued')}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{stats.issued}</div>
          </CardContent>
        </Card>
      </div>

      {/* Records List */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileCheck className="w-5 h-5" />
            {t('certData.listTitle')}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8 text-gray-500">{t('loading')}</div>
          ) : recordsList.length === 0 ? (
            <div className="text-center py-8 text-gray-500">{t('certData.empty')}</div>
          ) : (
            <div className="overflow-x-auto" dir={isRTL ? 'rtl' : 'ltr'}>
              <table className="w-full table-fixed" data-testid="cert-data-table">
                <thead>
                  <tr className={`border-b ${isRTL ? 'text-right' : 'text-left'}`}>
                    <th className={`p-3 px-4 font-medium w-[180px] ${isRTL ? 'text-right' : 'text-left'}`}>{t('certData.clientName')}</th>
                    <th className={`p-3 px-4 font-medium w-[140px] ${isRTL ? 'text-right' : 'text-left'}`}>{t('certData.standards')}</th>
                    <th className={`p-3 px-4 font-medium w-[100px] ${isRTL ? 'text-right' : 'text-left'}`}>{t('certData.auditType')}</th>
                    <th className={`p-3 px-4 font-medium w-[120px] ${isRTL ? 'text-right' : 'text-left'}`}>{t('certData.certificateNo')}</th>
                    <th className={`p-3 px-4 font-medium w-[100px] ${isRTL ? 'text-right' : 'text-left'}`}>{t('certData.statusLabel')}</th>
                    <th className={`p-3 px-4 font-medium w-[180px] ${isRTL ? 'text-right' : 'text-left'}`}>{t('actions')}</th>
                  </tr>
                </thead>
                <tbody>
                  {recordsList.map((record) => (
                    <tr key={record.id} className="border-b hover:bg-gray-50">
                      <td className="p-3 px-4">
                        <div className={`font-medium ${isRTL ? 'text-right' : ''}`}>{record.client_name}</div>
                      </td>
                      <td className={`p-3 px-4 ${isRTL ? 'text-right' : ''}`}>{record.standards?.join(', ')}</td>
                      <td className={`p-3 px-4 ${isRTL ? 'text-right' : ''}`}>{record.audit_type}</td>
                      <td className={`p-3 px-4 ${isRTL ? 'text-right' : ''}`}>
                        {record.certificate_number ? (
                          <span className="text-green-600 font-medium">{record.certificate_number}</span>
                        ) : '—'}
                      </td>
                      <td className={`p-3 px-4 ${isRTL ? 'text-right' : ''}`}>{getStatusBadge(record.status)}</td>
                      <td className="p-3 px-4">
                        <div className={`flex gap-1 ${isRTL ? 'flex-row-reverse justify-end' : ''}`}>
                          <Button variant="ghost" size="sm" onClick={() => openViewModal(record)} title={t('view')}>
                            <Eye className="w-4 h-4" />
                          </Button>
                          <Button variant="ghost" size="sm" onClick={() => openEditModal(record)} title={t('edit')}>
                            <Edit className="w-4 h-4" />
                          </Button>
                          {record.status === 'draft' && (
                            <Button variant="ghost" size="sm" onClick={() => handleSendToClient(record.id)} title={t('certData.sendToClient')} className="text-blue-600">
                              <Send className="w-4 h-4" />
                            </Button>
                          )}
                          {record.status === 'client_confirmed' && !record.certificate_generated && (
                            <Button variant="ghost" size="sm" onClick={() => handleIssueCertificate(record.id)} title={t('certData.issueCert')} className="text-green-600">
                              <Award className="w-4 h-4" />
                            </Button>
                          )}
                          <Button variant="ghost" size="sm" onClick={() => handleDownloadPDF(record.id)} title={t('downloadPDF')} className="text-blue-600">
                            <Download className="w-4 h-4" />
                          </Button>
                          <Button variant="ghost" size="sm" onClick={() => handleDelete(record.id)} title={t('delete')} className="text-red-600">
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
            <DialogTitle>{t('certData.createTitle')}</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label>{t('certData.createMode')}</Label>
              <Select value={createMode} onValueChange={setCreateMode}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="nc">{t('certData.fromNC')}</SelectItem>
                  <SelectItem value="report">{t('certData.fromReport')}</SelectItem>
                  <SelectItem value="manual">{t('certData.manual')}</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {createMode === 'nc' && (
              <div className="space-y-2">
                <Label>{t('certData.selectNC')}</Label>
                <Select value={selectedNCId} onValueChange={setSelectedNCId}>
                  <SelectTrigger><SelectValue placeholder={t('certData.selectNCPlaceholder')} /></SelectTrigger>
                  <SelectContent>
                    {ncReports.map((nc) => (
                      <SelectItem key={nc.id} value={nc.id}>
                        {nc.client_name} - {nc.standards?.join(', ')}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            )}

            {createMode === 'report' && (
              <div className="space-y-2">
                <Label>{t('certData.selectReport')}</Label>
                <Select value={selectedReportId} onValueChange={setSelectedReportId}>
                  <SelectTrigger><SelectValue placeholder={t('certData.selectReportPlaceholder')} /></SelectTrigger>
                  <SelectContent>
                    {stage2Reports.map((report) => (
                      <SelectItem key={report.id} value={report.id}>
                        {report.organization_name} - {report.standards?.join(', ')}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            )}

            {createMode === 'manual' && (
              <>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>{t('certData.clientName')}</Label>
                    <Input value={formData.client_name} onChange={(e) => setFormData({ ...formData, client_name: e.target.value })} />
                  </div>
                  <div className="space-y-2">
                    <Label>{t('certData.leadAuditor')}</Label>
                    <Input value={formData.lead_auditor} onChange={(e) => setFormData({ ...formData, lead_auditor: e.target.value })} />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>{t('certData.auditType')}</Label>
                    <Select value={formData.audit_type} onValueChange={(v) => setFormData({ ...formData, audit_type: v })}>
                      <SelectTrigger><SelectValue /></SelectTrigger>
                      <SelectContent>
                        <SelectItem value="CA - Certification Audit">CA - Certification Audit</SelectItem>
                        <SelectItem value="RA - Recertification Audit">RA - Recertification Audit</SelectItem>
                        <SelectItem value="Surveillance">Surveillance</SelectItem>
                        <SelectItem value="Extension">Extension</SelectItem>
                        <SelectItem value="Special">Special</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label>{t('certData.date')}</Label>
                    <Input type="date" value={formData.audit_date} onChange={(e) => setFormData({ ...formData, audit_date: e.target.value })} />
                  </div>
                </div>
              </>
            )}

            <div className="flex justify-end gap-2 pt-4">
              <Button variant="outline" onClick={() => setShowCreateModal(false)}>{t('cancel')}</Button>
              <Button 
                onClick={handleCreate}
                disabled={(createMode === 'nc' && !selectedNCId) || (createMode === 'report' && !selectedReportId)}
              >
                {t('create')}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* View Modal */}
      <Dialog open={showViewModal} onOpenChange={setShowViewModal}>
        <DialogContent className="max-w-3xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>{t('certData.viewTitle')}</DialogTitle>
          </DialogHeader>
          {selectedRecord && (
            <div className="space-y-6">
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4 p-4 bg-gray-50 rounded-lg">
                <div>
                  <div className="text-sm text-gray-500">{t('certData.clientName')}</div>
                  <div className="font-medium">{selectedRecord.client_name || '—'}</div>
                </div>
                <div>
                  <div className="text-sm text-gray-500">{t('certData.standards')}</div>
                  <div className="font-medium">{selectedRecord.standards?.join(', ') || '—'}</div>
                </div>
                <div>
                  <div className="text-sm text-gray-500">{t('certData.leadAuditor')}</div>
                  <div className="font-medium">{selectedRecord.lead_auditor || '—'}</div>
                </div>
                <div>
                  <div className="text-sm text-gray-500">{t('certData.auditType')}</div>
                  <div className="font-medium">{selectedRecord.audit_type || '—'}</div>
                </div>
                <div>
                  <div className="text-sm text-gray-500">{t('certData.date')}</div>
                  <div className="font-medium">{selectedRecord.audit_date || '—'}</div>
                </div>
                <div>
                  <div className="text-sm text-gray-500">{t('certData.eaCode')}</div>
                  <div className="font-medium">{selectedRecord.ea_code || '—'}</div>
                </div>
              </div>

              {selectedRecord.agreed_certification_scope && (
                <div className="p-4 border rounded-lg">
                  <div className="text-sm text-gray-500 mb-2">{t('certData.agreedScope')}</div>
                  <div>{selectedRecord.agreed_certification_scope}</div>
                </div>
              )}

              {selectedRecord.certificate_number && (
                <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                  <div className="text-green-800 font-bold mb-2">{t('certData.certificateIssued')}</div>
                  <div className="grid grid-cols-3 gap-4">
                    <div>
                      <div className="text-sm text-gray-500">{t('certData.certificateNo')}</div>
                      <div className="font-medium">{selectedRecord.certificate_number}</div>
                    </div>
                    <div>
                      <div className="text-sm text-gray-500">{t('certData.issueDate')}</div>
                      <div className="font-medium">{selectedRecord.issue_date}</div>
                    </div>
                    <div>
                      <div className="text-sm text-gray-500">{t('certData.expiryDate')}</div>
                      <div className="font-medium">{selectedRecord.expiry_date}</div>
                    </div>
                  </div>
                </div>
              )}

              {selectedRecord.client_confirmed && (
                <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg flex items-center gap-2">
                  <CheckCircle className="w-5 h-5 text-blue-600" />
                  <span className="text-blue-800 font-medium">{t('certData.clientConfirmed')} - {selectedRecord.client_signature_date}</span>
                </div>
              )}
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* Edit Modal */}
      <Dialog open={showEditModal} onOpenChange={setShowEditModal}>
        <DialogContent className="max-w-3xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>{t('certData.editTitle')}</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>{t('certData.clientName')}</Label>
                <Input value={formData.client_name} onChange={(e) => setFormData({ ...formData, client_name: e.target.value })} />
              </div>
              <div className="space-y-2">
                <Label>{t('certData.leadAuditor')}</Label>
                <Input value={formData.lead_auditor} onChange={(e) => setFormData({ ...formData, lead_auditor: e.target.value })} />
              </div>
            </div>
            <div className="grid grid-cols-3 gap-4">
              <div className="space-y-2">
                <Label>{t('certData.auditType')}</Label>
                <Select value={formData.audit_type} onValueChange={(v) => setFormData({ ...formData, audit_type: v })}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="CA - Certification Audit">CA - Certification Audit</SelectItem>
                    <SelectItem value="RA - Recertification Audit">RA - Recertification Audit</SelectItem>
                    <SelectItem value="Surveillance">Surveillance</SelectItem>
                    <SelectItem value="Extension">Extension</SelectItem>
                    <SelectItem value="Special">Special</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label>{t('certData.date')}</Label>
                <Input type="date" value={formData.audit_date} onChange={(e) => setFormData({ ...formData, audit_date: e.target.value })} />
              </div>
              <div className="space-y-2">
                <Label>{t('certData.eaCode')}</Label>
                <Input value={formData.ea_code} onChange={(e) => setFormData({ ...formData, ea_code: e.target.value })} placeholder="e.g., EA 17" />
              </div>
            </div>
            <div className="space-y-2">
              <Label>{t('certData.agreedScope')}</Label>
              <Textarea value={formData.agreed_certification_scope} onChange={(e) => setFormData({ ...formData, agreed_certification_scope: e.target.value })} rows={3} />
            </div>
            
            <div className="border-t pt-4 mt-4">
              <h3 className="font-medium mb-4">{t('certData.companyDataLocal')}</h3>
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label>{t('certData.companyDataField')}</Label>
                  <Textarea value={formData.company_data_local} onChange={(e) => setFormData({ ...formData, company_data_local: e.target.value })} rows={2} dir="rtl" />
                </div>
                <div className="space-y-2">
                  <Label>{t('certData.scopeField')}</Label>
                  <Textarea value={formData.certification_scope_local} onChange={(e) => setFormData({ ...formData, certification_scope_local: e.target.value })} rows={2} dir="rtl" />
                </div>
              </div>
            </div>

            <div className="border-t pt-4 mt-4">
              <h3 className="font-medium mb-4">{t('certData.companyDataEnglish')}</h3>
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label>{t('certData.companyDataField')}</Label>
                  <Textarea value={formData.company_data_english} onChange={(e) => setFormData({ ...formData, company_data_english: e.target.value })} rows={2} />
                </div>
                <div className="space-y-2">
                  <Label>{t('certData.scopeField')}</Label>
                  <Textarea value={formData.certification_scope_english} onChange={(e) => setFormData({ ...formData, certification_scope_english: e.target.value })} rows={2} />
                </div>
              </div>
            </div>

            <div className="flex justify-end gap-2 pt-4">
              <Button variant="outline" onClick={() => setShowEditModal(false)}>{t('cancel')}</Button>
              <Button onClick={handleUpdate}>{t('save')}</Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
