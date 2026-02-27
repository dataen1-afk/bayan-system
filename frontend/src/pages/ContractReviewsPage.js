import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import axios from 'axios';
import { 
  FileText, Plus, Download, Send, Eye, Trash2, 
  CheckCircle, Clock, AlertCircle, Users, Calendar,
  Building, ClipboardList, UserCheck, X
} from 'lucide-react';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '../components/ui/dialog';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function ContractReviewsPage() {
  const { t, i18n } = useTranslation();
  const isRTL = i18n.language === 'ar';
  
  const [reviews, setReviews] = useState([]);
  const [agreements, setAgreements] = useState([]);
  const [auditors, setAuditors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showViewModal, setShowViewModal] = useState(false);
  const [selectedReview, setSelectedReview] = useState(null);
  const [selectedAgreementId, setSelectedAgreementId] = useState('');
  
  // Form state for admin editing
  const [editForm, setEditForm] = useState({
    contract_review_date: '',
    risk_category: '',
    complexity_category: '',
    integration_level_percent: 100,
    combined_audit_ability_percent: 100,
    auditor_code_matched: false,
    lead_auditor_id: '',
    lead_auditor_name: '',
    auditor_ids: [],
    auditor_names: [],
    other_team_members: '',
    technical_expert_needed: false,
    technical_expert_name: '',
    certification_decision_maker: '',
    prepared_by_name: '',
    prepared_by_date: '',
    reviewed_by_name: '',
    reviewed_by_date: ''
  });
  
  useEffect(() => {
    fetchData();
  }, []);
  
  const fetchData = async () => {
    try {
      const token = localStorage.getItem('token');
      const headers = { Authorization: `Bearer ${token}` };
      
      const [reviewsRes, agreementsRes, auditorsRes] = await Promise.all([
        axios.get(`${API_URL}/api/contract-reviews`, { headers }),
        axios.get(`${API_URL}/api/certification-agreements`, { headers }),
        axios.get(`${API_URL}/api/auditors`, { headers })
      ]);
      
      setReviews(reviewsRes.data);
      setAgreements(agreementsRes.data);
      setAuditors(auditorsRes.data);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const createContractReview = async () => {
    if (!selectedAgreementId) return;
    
    try {
      const token = localStorage.getItem('token');
      await axios.post(
        `${API_URL}/api/contract-reviews`,
        { agreement_id: selectedAgreementId },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setShowCreateModal(false);
      setSelectedAgreementId('');
      fetchData();
    } catch (error) {
      console.error('Error creating contract review:', error);
      alert(error.response?.data?.detail || 'Error creating contract review');
    }
  };
  
  const updateContractReview = async () => {
    if (!selectedReview) return;
    
    try {
      const token = localStorage.getItem('token');
      await axios.put(
        `${API_URL}/api/contract-reviews/${selectedReview.id}/admin`,
        editForm,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setShowEditModal(false);
      fetchData();
    } catch (error) {
      console.error('Error updating contract review:', error);
    }
  };
  
  const deleteContractReview = async (id) => {
    if (!window.confirm('Are you sure you want to delete this contract review?')) return;
    
    try {
      const token = localStorage.getItem('token');
      await axios.delete(`${API_URL}/api/contract-reviews/${id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      fetchData();
    } catch (error) {
      console.error('Error deleting contract review:', error);
    }
  };
  
  const sendLinkToClient = async (review) => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        `${API_URL}/api/contract-reviews/${review.id}/send-link`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      const { link, email, organization } = response.data;
      
      // Copy link to clipboard
      navigator.clipboard.writeText(link);
      alert(`Link copied to clipboard!\n\nOrganization: ${organization}\nEmail: ${email}\nLink: ${link}`);
    } catch (error) {
      console.error('Error sending link:', error);
    }
  };
  
  const downloadPDF = async (review) => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(
        `${API_URL}/api/contract-reviews/${review.id}/pdf`,
        { 
          headers: { Authorization: `Bearer ${token}` },
          responseType: 'blob'
        }
      );
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `contract_review_${review.organization_name.replace(/\s+/g, '_')}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error('Error downloading PDF:', error);
    }
  };
  
  const openEditModal = (review) => {
    setSelectedReview(review);
    setEditForm({
      contract_review_date: review.contract_review_date || new Date().toISOString().split('T')[0],
      risk_category: review.risk_category || '',
      complexity_category: review.complexity_category || '',
      integration_level_percent: review.integration_level_percent || 100,
      combined_audit_ability_percent: review.combined_audit_ability_percent || 100,
      auditor_code_matched: review.auditor_code_matched || false,
      lead_auditor_id: review.lead_auditor_id || '',
      lead_auditor_name: review.lead_auditor_name || '',
      auditor_ids: review.auditor_ids || [],
      auditor_names: review.auditor_names || [],
      other_team_members: review.other_team_members || '',
      technical_expert_needed: review.technical_expert_needed || false,
      technical_expert_name: review.technical_expert_name || '',
      certification_decision_maker: review.certification_decision_maker || '',
      prepared_by_name: review.prepared_by_name || '',
      prepared_by_date: review.prepared_by_date || '',
      reviewed_by_name: review.reviewed_by_name || '',
      reviewed_by_date: review.reviewed_by_date || ''
    });
    setShowEditModal(true);
  };
  
  const getStatusBadge = (status) => {
    const statusConfig = {
      'pending_client': { color: 'bg-yellow-100 text-yellow-800', icon: Clock, label: t('pendingClientSubmission') },
      'pending_review': { color: 'bg-blue-100 text-blue-800', icon: AlertCircle, label: t('pendingReview') },
      'completed': { color: 'bg-green-100 text-green-800', icon: CheckCircle, label: t('reviewCompleted') }
    };
    
    const config = statusConfig[status] || statusConfig['pending_client'];
    const Icon = config.icon;
    
    return (
      <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${config.color}`}>
        <Icon className="w-3 h-3" />
        {config.label}
      </span>
    );
  };
  
  // Get agreements that don't have a contract review yet
  const availableAgreements = agreements.filter(
    a => !reviews.some(r => r.agreement_id === a.id)
  );
  
  const stats = {
    total: reviews.length,
    pendingClient: reviews.filter(r => r.status === 'pending_client').length,
    pendingReview: reviews.filter(r => r.status === 'pending_review').length,
    completed: reviews.filter(r => r.status === 'completed').length
  };

  return (
    <div className={`p-6 ${isRTL ? 'rtl' : 'ltr'}`} dir={isRTL ? 'rtl' : 'ltr'}>
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{t('contractReviews')}</h1>
          <p className="text-gray-500">{t('auditProgram')} - BACF6-04</p>
        </div>
        <Button onClick={() => setShowCreateModal(true)} className="bg-emerald-600 hover:bg-emerald-700">
          <Plus className="w-4 h-4 mr-2" />
          {t('createContractReview')}
        </Button>
      </div>
      
      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <Card>
          <CardContent className="p-4 flex items-center gap-4">
            <div className="p-3 bg-blue-100 rounded-lg">
              <ClipboardList className="w-6 h-6 text-blue-600" />
            </div>
            <div>
              <p className="text-2xl font-bold">{stats.total}</p>
              <p className="text-sm text-gray-500">{t('total')}</p>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4 flex items-center gap-4">
            <div className="p-3 bg-yellow-100 rounded-lg">
              <Clock className="w-6 h-6 text-yellow-600" />
            </div>
            <div>
              <p className="text-2xl font-bold">{stats.pendingClient}</p>
              <p className="text-sm text-gray-500">{t('pendingClientSubmission')}</p>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4 flex items-center gap-4">
            <div className="p-3 bg-blue-100 rounded-lg">
              <AlertCircle className="w-6 h-6 text-blue-600" />
            </div>
            <div>
              <p className="text-2xl font-bold">{stats.pendingReview}</p>
              <p className="text-sm text-gray-500">{t('pendingReview')}</p>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4 flex items-center gap-4">
            <div className="p-3 bg-green-100 rounded-lg">
              <CheckCircle className="w-6 h-6 text-green-600" />
            </div>
            <div>
              <p className="text-2xl font-bold">{stats.completed}</p>
              <p className="text-sm text-gray-500">{t('reviewCompleted')}</p>
            </div>
          </CardContent>
        </Card>
      </div>
      
      {/* Reviews List */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="w-5 h-5" />
            {t('contractReviews')}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8">Loading...</div>
          ) : reviews.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <ClipboardList className="w-12 h-12 mx-auto mb-4 opacity-50" />
              <p>No contract reviews yet</p>
            </div>
          ) : (
            <div className="overflow-x-auto" dir={isRTL ? 'rtl' : 'ltr'}>
              <table className="w-full table-fixed">
                <thead>
                  <tr className={`border-b ${isRTL ? 'text-right' : 'text-left'}`}>
                    <th className={`p-3 px-4 font-medium text-gray-600 w-[220px] ${isRTL ? 'text-right' : 'text-left'}`}>{t('organizationName')}</th>
                    <th className={`p-3 px-4 font-medium text-gray-600 w-[180px] ${isRTL ? 'text-right' : 'text-left'}`}>{t('standards')}</th>
                    <th className={`p-3 px-4 font-medium text-gray-600 w-[140px] ${isRTL ? 'text-right' : 'text-left'}`}>{t('applicationDate')}</th>
                    <th className={`p-3 px-4 font-medium text-gray-600 w-[120px] ${isRTL ? 'text-right' : 'text-left'}`}>{t('status')}</th>
                    <th className={`p-3 px-4 font-medium text-gray-600 w-[200px] ${isRTL ? 'text-right' : 'text-left'}`}>{t('actions')}</th>
                  </tr>
                </thead>
                <tbody>
                  {reviews.map(review => (
                    <tr key={review.id} className="border-b hover:bg-gray-50">
                      <td className="p-3 px-4">
                        <div className={`flex items-center gap-2 ${isRTL ? 'flex-row-reverse justify-end' : ''}`}>
                          <Building className="w-4 h-4 text-gray-400 flex-shrink-0" />
                          <span className="font-medium truncate">{review.organization_name}</span>
                        </div>
                      </td>
                      <td className="p-3 px-4">
                        <div className={`flex flex-wrap gap-1 ${isRTL ? 'justify-end' : ''}`}>
                          {(review.standards || []).map((std, idx) => (
                            <span key={idx} className="px-2 py-0.5 bg-blue-100 text-blue-800 text-xs rounded">
                              {std}
                            </span>
                          ))}
                        </div>
                      </td>
                      <td className="p-3 px-4">
                        <div className={`flex items-center gap-1 text-gray-600 ${isRTL ? 'flex-row-reverse justify-end' : ''}`}>
                          <Calendar className="w-4 h-4 flex-shrink-0" />
                          <span dir="ltr">{review.application_date}</span>
                        </div>
                      </td>
                      <td className={`p-3 px-4 ${isRTL ? 'text-right' : ''}`}>{getStatusBadge(review.status)}</td>
                      <td className="p-3 px-4">
                        <div className={`flex gap-2 ${isRTL ? 'flex-row-reverse justify-end' : ''}`}>
                          <Button 
                            size="sm" 
                            variant="outline"
                            onClick={() => { setSelectedReview(review); setShowViewModal(true); }}
                            data-testid={`view-review-${review.id}`}
                          >
                            <Eye className="w-4 h-4" />
                          </Button>
                          <Button 
                            size="sm" 
                            variant="outline"
                            onClick={() => openEditModal(review)}
                            data-testid={`edit-review-${review.id}`}
                          >
                            <UserCheck className="w-4 h-4" />
                          </Button>
                          <Button 
                            size="sm" 
                            variant="outline"
                            onClick={() => sendLinkToClient(review)}
                            data-testid={`send-link-${review.id}`}
                          >
                            <Send className="w-4 h-4" />
                          </Button>
                          <Button 
                            size="sm" 
                            className="bg-emerald-600 hover:bg-emerald-700"
                            onClick={() => downloadPDF(review)}
                            data-testid={`download-pdf-${review.id}`}
                          >
                            <Download className="w-4 h-4" />
                          </Button>
                          <Button 
                            size="sm" 
                            variant="destructive"
                            onClick={() => deleteContractReview(review.id)}
                            data-testid={`delete-review-${review.id}`}
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
            <DialogTitle>{t('createContractReview')}</DialogTitle>
            <DialogDescription>Select a signed agreement to create a contract review</DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label>Select Agreement</Label>
              <Select value={selectedAgreementId} onValueChange={setSelectedAgreementId}>
                <SelectTrigger>
                  <SelectValue placeholder="Select an agreement..." />
                </SelectTrigger>
                <SelectContent>
                  {availableAgreements.map(agreement => (
                    <SelectItem key={agreement.id} value={agreement.id}>
                      {agreement.organization_name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {availableAgreements.length === 0 && (
                <p className="text-sm text-gray-500 mt-2">No agreements available for contract review</p>
              )}
            </div>
            <div className="flex gap-2 justify-end">
              <Button variant="outline" onClick={() => setShowCreateModal(false)}>Cancel</Button>
              <Button onClick={createContractReview} disabled={!selectedAgreementId}>Create</Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
      
      {/* Edit Modal */}
      <Dialog open={showEditModal} onOpenChange={setShowEditModal}>
        <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>{t('contractReviewDetails')}</DialogTitle>
            <DialogDescription>{selectedReview?.organization_name}</DialogDescription>
          </DialogHeader>
          <div className="space-y-6">
            {/* General Info */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>{t('contractReviewDate')}</Label>
                <Input
                  type="date"
                  value={editForm.contract_review_date}
                  onChange={(e) => setEditForm({...editForm, contract_review_date: e.target.value})}
                />
              </div>
              <div>
                <Label>{t('riskCategory')}</Label>
                <Select value={editForm.risk_category} onValueChange={(v) => setEditForm({...editForm, risk_category: v})}>
                  <SelectTrigger><SelectValue placeholder="Select..." /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Low">Low</SelectItem>
                    <SelectItem value="Medium">Medium</SelectItem>
                    <SelectItem value="High">High</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label>{t('complexityCategory')}</Label>
                <Select value={editForm.complexity_category} onValueChange={(v) => setEditForm({...editForm, complexity_category: v})}>
                  <SelectTrigger><SelectValue placeholder="Select..." /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Simple">Simple</SelectItem>
                    <SelectItem value="Standard">Standard</SelectItem>
                    <SelectItem value="Complex">Complex</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label>{t('integrationLevel')} (%)</Label>
                <Input
                  type="number"
                  value={editForm.integration_level_percent}
                  onChange={(e) => setEditForm({...editForm, integration_level_percent: parseFloat(e.target.value)})}
                />
              </div>
            </div>
            
            {/* Team Assignment */}
            <div className="border-t pt-4">
              <h3 className="font-semibold mb-3">{t('teamOfAuditors')}</h3>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>{t('leadAuditor')}</Label>
                  <Select 
                    value={editForm.lead_auditor_id} 
                    onValueChange={(v) => {
                      const auditor = auditors.find(a => a.id === v);
                      setEditForm({
                        ...editForm, 
                        lead_auditor_id: v,
                        lead_auditor_name: auditor ? auditor.name : ''
                      });
                    }}
                  >
                    <SelectTrigger><SelectValue placeholder="Select lead auditor..." /></SelectTrigger>
                    <SelectContent>
                      {auditors.filter(a => a.status === 'active').map(auditor => (
                        <SelectItem key={auditor.id} value={auditor.id}>{auditor.name}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label>{t('certificationDecisionMaker')}</Label>
                  <Input
                    value={editForm.certification_decision_maker}
                    onChange={(e) => setEditForm({...editForm, certification_decision_maker: e.target.value})}
                    placeholder="Enter name..."
                  />
                </div>
                <div className="col-span-2">
                  <Label>Other Team Members</Label>
                  <Input
                    value={editForm.other_team_members}
                    onChange={(e) => setEditForm({...editForm, other_team_members: e.target.value})}
                    placeholder="Enter names separated by comma..."
                  />
                </div>
                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={editForm.technical_expert_needed}
                    onChange={(e) => setEditForm({...editForm, technical_expert_needed: e.target.checked})}
                  />
                  <Label>{t('technicalExpertNeeded')}</Label>
                </div>
                {editForm.technical_expert_needed && (
                  <div>
                    <Label>Technical Expert Name</Label>
                    <Input
                      value={editForm.technical_expert_name}
                      onChange={(e) => setEditForm({...editForm, technical_expert_name: e.target.value})}
                    />
                  </div>
                )}
              </div>
            </div>
            
            {/* Approval */}
            <div className="border-t pt-4">
              <h3 className="font-semibold mb-3">Document Approval</h3>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>{t('preparedBy')}</Label>
                  <Input
                    value={editForm.prepared_by_name}
                    onChange={(e) => setEditForm({...editForm, prepared_by_name: e.target.value})}
                  />
                </div>
                <div>
                  <Label>Prepared Date</Label>
                  <Input
                    type="date"
                    value={editForm.prepared_by_date}
                    onChange={(e) => setEditForm({...editForm, prepared_by_date: e.target.value})}
                  />
                </div>
                <div>
                  <Label>{t('reviewedBy')}</Label>
                  <Input
                    value={editForm.reviewed_by_name}
                    onChange={(e) => setEditForm({...editForm, reviewed_by_name: e.target.value})}
                  />
                </div>
                <div>
                  <Label>Reviewed Date</Label>
                  <Input
                    type="date"
                    value={editForm.reviewed_by_date}
                    onChange={(e) => setEditForm({...editForm, reviewed_by_date: e.target.value})}
                  />
                </div>
              </div>
            </div>
            
            <div className="flex gap-2 justify-end">
              <Button variant="outline" onClick={() => setShowEditModal(false)}>Cancel</Button>
              <Button onClick={updateContractReview}>Save Changes</Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
      
      {/* View Modal */}
      <Dialog open={showViewModal} onOpenChange={setShowViewModal}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>{t('contractReviewDetails')}</DialogTitle>
          </DialogHeader>
          {selectedReview && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-500">{t('organizationName')}:</span>
                  <p className="font-medium">{selectedReview.organization_name}</p>
                </div>
                <div>
                  <span className="text-gray-500">{t('status')}:</span>
                  <p>{getStatusBadge(selectedReview.status)}</p>
                </div>
                <div>
                  <span className="text-gray-500">{t('standards')}:</span>
                  <p className="font-medium">{(selectedReview.standards || []).join(', ')}</p>
                </div>
                <div>
                  <span className="text-gray-500">{t('totalEmployees')}:</span>
                  <p className="font-medium">{selectedReview.total_employees}</p>
                </div>
                <div className="col-span-2">
                  <span className="text-gray-500">{t('scopeOfServices')}:</span>
                  <p className="font-medium">{selectedReview.scope_of_services}</p>
                </div>
                
                {selectedReview.client_submitted && (
                  <>
                    <div className="col-span-2 border-t pt-3">
                      <h4 className="font-semibold text-emerald-600">{t('clientDataSubmitted')}</h4>
                    </div>
                    <div>
                      <span className="text-gray-500">{t('consultantName')}:</span>
                      <p className="font-medium">{selectedReview.consultant_name || 'N/A'}</p>
                    </div>
                    <div>
                      <span className="text-gray-500">{t('exclusions')}:</span>
                      <p className="font-medium">{selectedReview.exclusions_justification || 'None'}</p>
                    </div>
                  </>
                )}
                
                {selectedReview.lead_auditor_name && (
                  <>
                    <div className="col-span-2 border-t pt-3">
                      <h4 className="font-semibold text-blue-600">{t('teamOfAuditors')}</h4>
                    </div>
                    <div>
                      <span className="text-gray-500">{t('leadAuditor')}:</span>
                      <p className="font-medium">{selectedReview.lead_auditor_name}</p>
                    </div>
                    <div>
                      <span className="text-gray-500">{t('certificationDecisionMaker')}:</span>
                      <p className="font-medium">{selectedReview.certification_decision_maker}</p>
                    </div>
                  </>
                )}
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
