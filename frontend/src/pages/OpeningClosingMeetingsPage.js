import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import axios from 'axios';
import { 
  FileText, Plus, Download, Eye, Trash2, Send,
  CheckCircle, Clock, Building, Calendar,
  Users, Copy
} from 'lucide-react';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '../components/ui/dialog';
import { Label } from '../components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function OpeningClosingMeetingsPage() {
  const { t, i18n } = useTranslation();
  const isRTL = i18n.language === 'ar';
  
  const [meetings, setMeetings] = useState([]);
  const [stage1Plans, setStage1Plans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showLinkModal, setShowLinkModal] = useState(false);
  const [showViewModal, setShowViewModal] = useState(false);
  const [selectedMeeting, setSelectedMeeting] = useState(null);
  const [selectedStage1Id, setSelectedStage1Id] = useState('');
  const [clientLink, setClientLink] = useState('');
  
  useEffect(() => {
    fetchData();
  }, []);
  
  const fetchData = async () => {
    try {
      const token = localStorage.getItem('token');
      const headers = { Authorization: `Bearer ${token}` };
      
      const [meetingsRes, plansRes] = await Promise.all([
        axios.get(`${API_URL}/api/opening-closing-meetings`, { headers }),
        axios.get(`${API_URL}/api/stage1-audit-plans`, { headers })
      ]);
      
      setMeetings(meetingsRes.data);
      // Filter to client_accepted Stage 1 plans
      setStage1Plans(plansRes.data.filter(p => p.status === 'client_accepted'));
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const createMeeting = async () => {
    if (!selectedStage1Id) {
      alert(t('selectStage1Plan') || 'Please select a Stage 1 plan');
      return;
    }
    
    try {
      const token = localStorage.getItem('token');
      await axios.post(
        `${API_URL}/api/opening-closing-meetings`,
        { stage1_plan_id: selectedStage1Id },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setShowCreateModal(false);
      setSelectedStage1Id('');
      fetchData();
    } catch (error) {
      console.error('Error creating meeting form:', error);
      alert(error.response?.data?.detail || 'Error creating meeting form');
    }
  };
  
  const deleteMeeting = async (id) => {
    if (!window.confirm(t('confirmDelete') || 'Are you sure you want to delete?')) return;
    
    try {
      const token = localStorage.getItem('token');
      await axios.delete(`${API_URL}/api/opening-closing-meetings/${id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      fetchData();
    } catch (error) {
      console.error('Error deleting meeting:', error);
    }
  };
  
  const sendToClient = async (meeting) => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        `${API_URL}/api/opening-closing-meetings/${meeting.id}/send-to-client`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setClientLink(response.data.link);
      setSelectedMeeting(meeting);
      setShowLinkModal(true);
      fetchData();
    } catch (error) {
      console.error('Error sending to client:', error);
      alert(error.response?.data?.detail || 'Error sending to client');
    }
  };
  
  const downloadPDF = async (meeting) => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(
        `${API_URL}/api/opening-closing-meetings/${meeting.id}/pdf`,
        { 
          headers: { Authorization: `Bearer ${token}` },
          responseType: 'blob'
        }
      );
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `meeting_${meeting.organization_name.replace(/\s+/g, '_')}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error('Error downloading PDF:', error);
    }
  };
  
  const viewMeeting = (meeting) => {
    setSelectedMeeting(meeting);
    setShowViewModal(true);
  };
  
  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    alert(t('linkCopied') || 'Link copied!');
  };
  
  const getStatusBadge = (status, sentToClient) => {
    if (status === 'submitted') {
      return (
        <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
          <CheckCircle className="w-3 h-3" />
          {t('submitted') || 'Submitted'}
        </span>
      );
    } else if (sentToClient) {
      return (
        <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-orange-100 text-orange-800">
          <Clock className="w-3 h-3" />
          {t('pendingClient') || 'Pending Client'}
        </span>
      );
    } else {
      return (
        <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
          <Clock className="w-3 h-3" />
          {t('draft') || 'Draft'}
        </span>
      );
    }
  };
  
  // Get available Stage 1 plans that don't have a meeting form yet
  const availableStage1Plans = stage1Plans.filter(
    p => !meetings.some(m => m.stage1_plan_id === p.id)
  );
  
  const stats = {
    total: meetings.length,
    pending: meetings.filter(m => m.status === 'pending' && !m.sent_to_client).length,
    sentToClient: meetings.filter(m => m.status === 'pending' && m.sent_to_client).length,
    submitted: meetings.filter(m => m.status === 'submitted').length
  };

  return (
    <div className={`p-6 ${isRTL ? 'rtl' : 'ltr'}`} dir={isRTL ? 'rtl' : 'ltr'}>
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{t('openingClosingMeetings') || 'Opening & Closing Meetings'}</h1>
          <p className="text-gray-500">BACF6-09 - {t('meetingDescription') || 'Audit meeting attendance records'}</p>
        </div>
        <Button onClick={() => setShowCreateModal(true)} className="bg-cyan-600 hover:bg-cyan-700" data-testid="create-meeting-btn">
          <Plus className="w-4 h-4 mr-2" />
          {t('createForm') || 'Create Form'}
        </Button>
      </div>
      
      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <Card>
          <CardContent className="p-4 flex items-center gap-4">
            <div className="p-3 bg-cyan-100 rounded-lg">
              <FileText className="w-6 h-6 text-cyan-600" />
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
              <p className="text-2xl font-bold">{stats.pending}</p>
              <p className="text-sm text-gray-500">{t('draft') || 'Draft'}</p>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4 flex items-center gap-4">
            <div className="p-3 bg-orange-100 rounded-lg">
              <Send className="w-6 h-6 text-orange-600" />
            </div>
            <div>
              <p className="text-2xl font-bold">{stats.sentToClient}</p>
              <p className="text-sm text-gray-500">{t('sentToClient') || 'Sent to Client'}</p>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4 flex items-center gap-4">
            <div className="p-3 bg-green-100 rounded-lg">
              <CheckCircle className="w-6 h-6 text-green-600" />
            </div>
            <div>
              <p className="text-2xl font-bold">{stats.submitted}</p>
              <p className="text-sm text-gray-500">{t('submitted') || 'Submitted'}</p>
            </div>
          </CardContent>
        </Card>
      </div>
      
      {/* Meetings List */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Users className="w-5 h-5" />
            {t('openingClosingMeetings') || 'Opening & Closing Meetings'}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8">Loading...</div>
          ) : meetings.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <Users className="w-12 h-12 mx-auto mb-4 opacity-50" />
              <p>{t('noMeetingForms') || 'No meeting forms yet'}</p>
              <p className="text-sm mt-2">{t('createFromStage1') || 'Create a form from a completed Stage 1 audit'}</p>
            </div>
          ) : (
            <div className="overflow-x-auto" dir={isRTL ? 'rtl' : 'ltr'}>
              <table className="w-full table-fixed">
                <thead>
                  <tr className={`border-b ${isRTL ? 'text-right' : 'text-left'}`}>
                    <th className={`p-3 px-4 font-medium text-gray-600 w-[200px] ${isRTL ? 'text-right' : 'text-left'}`}>{t('organization') || 'Organization'}</th>
                    <th className={`p-3 px-4 font-medium text-gray-600 w-[100px] ${isRTL ? 'text-right' : 'text-left'}`}>{t('auditType') || 'Audit Type'}</th>
                    <th className={`p-3 px-4 font-medium text-gray-600 w-[110px] ${isRTL ? 'text-right' : 'text-left'}`}>{t('auditDate') || 'Audit Date'}</th>
                    <th className={`p-3 px-4 font-medium text-gray-600 w-[100px] ${isRTL ? 'text-right' : 'text-left'}`}>{t('attendees') || 'Attendees'}</th>
                    <th className={`p-3 px-4 font-medium text-gray-600 w-[100px] ${isRTL ? 'text-right' : 'text-left'}`}>{t('status') || 'Status'}</th>
                    <th className={`p-3 px-4 font-medium text-gray-600 w-[200px] ${isRTL ? 'text-right' : 'text-left'}`}>{t('actions') || 'Actions'}</th>
                  </tr>
                </thead>
                <tbody>
                  {meetings.map(meeting => (
                    <tr key={meeting.id} className="border-b hover:bg-gray-50" data-testid={`meeting-row-${meeting.id}`}>
                      <td className="p-3 px-4">
                        <div className={`flex items-center gap-2 ${isRTL ? 'flex-row-reverse justify-end' : ''}`}>
                          <Building className="w-4 h-4 text-gray-400 flex-shrink-0" />
                          <span className="font-medium truncate">{meeting.organization_name}</span>
                        </div>
                      </td>
                      <td className={`p-3 px-4 ${isRTL ? 'text-right' : ''}`}>
                        <span className="px-2 py-1 bg-cyan-100 text-cyan-800 rounded text-sm whitespace-nowrap">
                          {meeting.audit_type || 'Stage 1'}
                        </span>
                      </td>
                      <td className="p-3 px-4">
                        <div className={`flex items-center gap-1 ${isRTL ? 'flex-row-reverse justify-end' : ''}`}>
                          <Calendar className="w-4 h-4 text-gray-400 flex-shrink-0" />
                          <span dir="ltr">{meeting.audit_date || '-'}</span>
                        </div>
                      </td>
                      <td className={`p-3 px-4 ${isRTL ? 'text-right' : ''}`}>
                        <span className="text-gray-600">
                          {meeting.attendees?.filter(a => a.name).length || 0} / {meeting.attendees?.length || 5}
                        </span>
                      </td>
                      <td className={`p-3 px-4 ${isRTL ? 'text-right' : ''}`}>{getStatusBadge(meeting.status, meeting.sent_to_client)}</td>
                      <td className="p-3 px-4">
                        <div className={`flex gap-2 ${isRTL ? 'flex-row-reverse justify-end' : ''}`}>
                          <Button 
                            size="sm" 
                            variant="outline"
                            onClick={() => viewMeeting(meeting)}
                            data-testid={`view-meeting-${meeting.id}`}
                          >
                            <Eye className="w-4 h-4" />
                          </Button>
                          
                          {!meeting.sent_to_client && (
                            <Button 
                              size="sm" 
                              variant="outline"
                              onClick={() => sendToClient(meeting)}
                              className="text-blue-600 hover:text-blue-700"
                              data-testid={`send-meeting-${meeting.id}`}
                            >
                              <Send className="w-4 h-4" />
                            </Button>
                          )}
                          
                          <Button 
                            size="sm" 
                            className="bg-cyan-600 hover:bg-cyan-700"
                            onClick={() => downloadPDF(meeting)}
                            data-testid={`download-pdf-${meeting.id}`}
                          >
                            <Download className="w-4 h-4" />
                          </Button>
                          
                          <Button 
                            size="sm" 
                            variant="destructive"
                            onClick={() => deleteMeeting(meeting.id)}
                            data-testid={`delete-meeting-${meeting.id}`}
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
            <DialogTitle>{t('createMeetingForm') || 'Create Meeting Form'}</DialogTitle>
            <DialogDescription>{t('selectStage1Audit') || 'Select a completed Stage 1 audit'}</DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label>{t('stage1Plan') || 'Stage 1 Plan'}</Label>
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
              {availableStage1Plans.length === 0 && (
                <p className="text-sm text-gray-500 mt-2">{t('noAcceptedStage1') || 'No client-accepted Stage 1 plans available'}</p>
              )}
            </div>
            <div className="flex gap-2 justify-end">
              <Button variant="outline" onClick={() => setShowCreateModal(false)}>{t('cancel') || 'Cancel'}</Button>
              <Button 
                onClick={createMeeting} 
                disabled={!selectedStage1Id}
                data-testid="create-meeting-submit"
                className="bg-cyan-600 hover:bg-cyan-700"
              >
                {t('create') || 'Create'}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
      
      {/* View Modal */}
      <Dialog open={showViewModal} onOpenChange={setShowViewModal}>
        <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>{t('meetingDetails') || 'Meeting Details'}</DialogTitle>
            <DialogDescription>{selectedMeeting?.organization_name}</DialogDescription>
          </DialogHeader>
          {selectedMeeting && (
            <div className="space-y-6">
              {/* Info */}
              <div className="grid grid-cols-2 gap-4 p-4 bg-gray-50 rounded-lg">
                <div>
                  <p className="text-sm text-gray-500">{t('auditType') || 'Audit Type'}</p>
                  <p className="font-medium">{selectedMeeting.audit_type}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">{t('auditDate') || 'Audit Date'}</p>
                  <p className="font-medium">{selectedMeeting.audit_date || '-'}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">{t('standards') || 'Standards'}</p>
                  <p className="font-medium">{selectedMeeting.standards?.join(', ') || '-'}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">{t('status') || 'Status'}</p>
                  {getStatusBadge(selectedMeeting.status, selectedMeeting.sent_to_client)}
                </div>
              </div>
              
              {/* Attendees Table */}
              <div>
                <h3 className="font-semibold mb-3">{t('attendees') || 'Attendees'}</h3>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm border rounded-lg overflow-hidden">
                    <thead className="bg-gray-100">
                      <tr>
                        <th className="p-2 text-left border">S.N</th>
                        <th className="p-2 text-left border">{t('name') || 'Name'}</th>
                        <th className="p-2 text-left border">{t('designation') || 'Designation'}</th>
                        <th className="p-2 text-left border">{t('openingMeeting') || 'Opening Meeting'}</th>
                        <th className="p-2 text-left border">{t('closingMeeting') || 'Closing Meeting'}</th>
                      </tr>
                    </thead>
                    <tbody>
                      {(selectedMeeting.attendees || []).map((attendee, idx) => (
                        <tr key={idx} className={idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                          <td className="p-2 border">{idx + 1}</td>
                          <td className="p-2 border">{attendee.name || '-'}</td>
                          <td className="p-2 border">{attendee.designation || '-'}</td>
                          <td className="p-2 border">{attendee.opening_meeting_date || '-'}</td>
                          <td className="p-2 border">{attendee.closing_meeting_date || '-'}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
              
              {/* Notes */}
              {selectedMeeting.status === 'submitted' && (
                <>
                  <div className="p-4 bg-cyan-50 rounded-lg">
                    <h3 className="font-semibold text-cyan-800 mb-2">{t('openingMeetingNotes') || 'Opening Meeting Notes'}</h3>
                    <p className="text-gray-700">{selectedMeeting.opening_meeting_notes || '-'}</p>
                  </div>
                  <div className="p-4 bg-cyan-50 rounded-lg">
                    <h3 className="font-semibold text-cyan-800 mb-2">{t('closingMeetingNotes') || 'Closing Meeting Notes'}</h3>
                    <p className="text-gray-700">{selectedMeeting.closing_meeting_notes || '-'}</p>
                  </div>
                  {selectedMeeting.submitted_date && (
                    <p className="text-sm text-gray-500">
                      {t('submittedOn') || 'Submitted on'}: {selectedMeeting.submitted_date}
                    </p>
                  )}
                </>
              )}
              
              <div className="flex gap-2 justify-end">
                <Button variant="outline" onClick={() => setShowViewModal(false)}>{t('close') || 'Close'}</Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
      
      {/* Send Link Modal */}
      <Dialog open={showLinkModal} onOpenChange={setShowLinkModal}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>{t('clientFormLink') || 'Client Form Link'}</DialogTitle>
            <DialogDescription>{t('sendLinkToClient') || 'Send this link to the client'}</DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            {selectedMeeting && (
              <div className="p-4 bg-gray-50 rounded-lg">
                <p><strong>{t('organization') || 'Organization'}:</strong> {selectedMeeting.organization_name}</p>
              </div>
            )}
            
            <div>
              <Label>{t('formLink') || 'Form Link'}</Label>
              <div className="flex gap-2">
                <input 
                  value={clientLink} 
                  readOnly 
                  className="flex-1 px-3 py-2 border rounded-md font-mono text-sm bg-gray-50"
                />
                <Button variant="outline" onClick={() => copyToClipboard(clientLink)}>
                  <Copy className="w-4 h-4" />
                </Button>
              </div>
            </div>
            
            <p className="text-sm text-gray-500">
              {t('meetingLinkInstructions') || 'Copy this link and send it to the client. They will fill in the meeting attendance information.'}
            </p>
            
            <div className="flex gap-2 justify-end">
              <Button variant="outline" onClick={() => setShowLinkModal(false)}>{t('close') || 'Close'}</Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
