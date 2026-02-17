import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import axios from 'axios';
import { 
  FileText, CheckCircle, XCircle, Building, Calendar,
  User, Users, Clock, AlertCircle, ClipboardList
} from 'lucide-react';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Textarea } from '../components/ui/textarea';
import { Label } from '../components/ui/label';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function PublicStage2PlanReviewPage() {
  const { accessToken } = useParams();
  const { t, i18n } = useTranslation();
  const isRTL = i18n.language === 'ar';
  
  const [plan, setPlan] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [showChangeForm, setShowChangeForm] = useState(false);
  const [changeRequests, setChangeRequests] = useState('');
  
  useEffect(() => {
    fetchPlan();
  }, [accessToken]);
  
  const fetchPlan = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/public/stage2-audit-plans/${accessToken}`);
      setPlan(response.data);
      if (response.data.client_accepted || response.data.status === 'changes_requested') {
        setSubmitted(true);
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Audit plan not found or not yet available');
    } finally {
      setLoading(false);
    }
  };
  
  const handleAccept = async () => {
    setSubmitting(true);
    try {
      await axios.post(`${API_URL}/api/public/stage2-audit-plans/${accessToken}/respond`, {
        accepted: true,
        change_requests: ''
      });
      setSubmitted(true);
      fetchPlan();
    } catch (err) {
      alert(err.response?.data?.detail || 'Error accepting plan');
    } finally {
      setSubmitting(false);
    }
  };
  
  const handleRequestChanges = async () => {
    if (!changeRequests.trim()) {
      alert(t('pleaseProvideDetails') || 'Please provide details of requested changes');
      return;
    }
    
    setSubmitting(true);
    try {
      await axios.post(`${API_URL}/api/public/stage2-audit-plans/${accessToken}/respond`, {
        accepted: false,
        change_requests: changeRequests
      });
      setSubmitted(true);
      fetchPlan();
    } catch (err) {
      alert(err.response?.data?.detail || 'Error submitting changes');
    } finally {
      setSubmitting(false);
    }
  };
  
  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-violet-600 mx-auto mb-4"></div>
          <p className="text-gray-600">{t('loading') || 'Loading...'}</p>
        </div>
      </div>
    );
  }
  
  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 flex items-center justify-center p-4">
        <Card className="max-w-md w-full">
          <CardContent className="p-8 text-center">
            <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
            <h2 className="text-xl font-bold text-gray-900 mb-2">{t('error') || 'Error'}</h2>
            <p className="text-gray-600">{error}</p>
          </CardContent>
        </Card>
      </div>
    );
  }
  
  return (
    <div className={`min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 py-8 px-4 ${isRTL ? 'rtl' : 'ltr'}`} dir={isRTL ? 'rtl' : 'ltr'}>
      <div className="max-w-3xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-violet-600 rounded-full flex items-center justify-center mx-auto mb-4">
            <FileText className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900">{t('stage2AuditPlanReview') || 'Stage 2 Audit Plan Review'}</h1>
          <p className="text-gray-500">BACF6-08</p>
        </div>
        
        {/* Plan Details */}
        <Card className="mb-6">
          <CardHeader className="bg-gradient-to-r from-violet-600 to-purple-600 text-white rounded-t-lg">
            <CardTitle className="flex items-center gap-2">
              <ClipboardList className="w-5 h-5" />
              {t('auditPlanDetails') || 'Audit Plan Details'}
            </CardTitle>
            <CardDescription className="text-violet-100">
              {t('reviewPlanDetails') || 'Please review the proposed audit plan'}
            </CardDescription>
          </CardHeader>
          <CardContent className="p-6">
            {plan && (
              <div className="space-y-6">
                {/* Basic Info */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="p-4 bg-violet-50 rounded-lg">
                    <h3 className="font-semibold text-violet-800 mb-3 flex items-center gap-2">
                      <Building className="w-4 h-4" />
                      {t('clientInfo') || 'Client Information'}
                    </h3>
                    <p><strong>{t('organization') || 'Organization'}:</strong> {plan.organization_name}</p>
                  </div>
                  
                  <div className="p-4 bg-gray-50 rounded-lg">
                    <h3 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
                      <Calendar className="w-4 h-4" />
                      {t('auditDetails') || 'Audit Details'}
                    </h3>
                    <p><strong>{t('type') || 'Type'}:</strong> {plan.audit_type}</p>
                    <p><strong>{t('dates') || 'Dates'}:</strong> {plan.audit_date_from} - {plan.audit_date_to || 'TBD'}</p>
                    <p><strong>{t('standards') || 'Standards'}:</strong> {(plan.standards || []).join(', ')}</p>
                  </div>
                </div>
                
                {/* Scope */}
                {plan.scope && (
                  <div className="p-4 bg-gray-50 rounded-lg">
                    <h3 className="font-semibold mb-2">{t('scope') || 'Scope'}</h3>
                    <p className="text-gray-700">{plan.scope}</p>
                  </div>
                )}
                
                {/* Stage 2 Objectives */}
                <div className="p-4 bg-purple-50 rounded-lg">
                  <h3 className="font-semibold text-purple-800 mb-3">{t('stage2Objectives') || 'Stage 2 Audit Objectives'}</h3>
                  <ul className="text-sm space-y-1 text-gray-700">
                    <li>- Verify conformity to all requirements of the applicable management system standard</li>
                    <li>- Performance monitoring, measuring, reporting and reviewing against key performance objectives</li>
                    <li>- Organization's management system and performance as regards legal compliance</li>
                    <li>- Operational control of the Organization's processes</li>
                    <li>- Internal auditing and management review effectiveness</li>
                    <li>- Management responsibility for the Organization's policies</li>
                  </ul>
                </div>
                
                {/* Audit Team */}
                <div className="p-4 bg-violet-50 rounded-lg">
                  <h3 className="font-semibold text-violet-800 mb-3 flex items-center gap-2">
                    <Users className="w-4 h-4" />
                    {t('auditTeam') || 'Audit Team'}
                  </h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm text-gray-500">{t('teamLeader') || 'Team Leader'}</p>
                      <p className="font-medium">{plan.team_leader?.name}</p>
                      {plan.team_leader?.name_ar && <p className="text-sm text-gray-600">{plan.team_leader.name_ar}</p>}
                    </div>
                    {plan.team_members && plan.team_members.length > 0 && (
                      <div>
                        <p className="text-sm text-gray-500">{t('teamMembers') || 'Team Members'}</p>
                        {plan.team_members.map((m, i) => (
                          <p key={i} className="text-sm">{m.name} ({m.role})</p>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
                
                {/* Schedule */}
                {plan.schedule_entries && plan.schedule_entries.length > 0 && (
                  <div>
                    <h3 className="font-semibold mb-3 flex items-center gap-2">
                      <Clock className="w-4 h-4" />
                      {t('auditSchedule') || 'Audit Schedule'}
                    </h3>
                    <div className="overflow-x-auto">
                      <table className="w-full text-sm border rounded-lg overflow-hidden">
                        <thead className="bg-gray-100">
                          <tr>
                            <th className="p-2 text-left border">{t('dateTime') || 'Date/Time'}</th>
                            <th className="p-2 text-left border">{t('process') || 'Process'}</th>
                            <th className="p-2 text-left border">{t('processOwner') || 'Process Owner'}</th>
                            <th className="p-2 text-left border">{t('clauses') || 'Clauses'}</th>
                            <th className="p-2 text-left border">{t('auditor') || 'Auditor'}</th>
                          </tr>
                        </thead>
                        <tbody>
                          {plan.schedule_entries.map((entry, idx) => (
                            <tr key={idx} className={idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                              <td className="p-2 border">{entry.date_time || '-'}</td>
                              <td className="p-2 border">{entry.process || '-'}</td>
                              <td className="p-2 border">{entry.process_owner || '-'}</td>
                              <td className="p-2 border">{entry.clauses || '-'}</td>
                              <td className="p-2 border">{entry.auditor || '-'}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}
                
                {/* Approved By */}
                <div className="p-4 bg-blue-50 rounded-lg">
                  <h3 className="font-semibold text-blue-800 mb-2">{t('approvedBy') || 'Approved By'}</h3>
                  <p><strong>{t('manager') || 'Manager'}:</strong> {plan.manager_name}</p>
                  <p><strong>{t('date') || 'Date'}:</strong> {plan.manager_approval_date}</p>
                </div>
                
                {/* Acceptance Note */}
                <div className="p-4 bg-yellow-50 rounded-lg border border-yellow-200">
                  <p className="text-sm text-yellow-800">
                    {t('acceptanceNote') || 'We trust the proposed schedule and audit team is acceptable to you. If you have any objections to the audit team composition, please register your concerns. If no objections are received within 2 working days, the audit team shall be deemed accepted.'}
                  </p>
                </div>
                
                {/* Status / Actions */}
                {submitted ? (
                  <div className={`p-6 rounded-lg text-center ${plan.client_accepted ? 'bg-green-50' : 'bg-orange-50'}`}>
                    {plan.client_accepted ? (
                      <>
                        <CheckCircle className="w-16 h-16 text-green-600 mx-auto mb-4" />
                        <h3 className="text-xl font-bold text-green-800 mb-2">{t('planAccepted') || 'Plan Accepted'}</h3>
                        <p className="text-green-700">{t('acceptanceSuccess') || 'You have accepted this audit plan.'}</p>
                      </>
                    ) : (
                      <>
                        <AlertCircle className="w-16 h-16 text-orange-600 mx-auto mb-4" />
                        <h3 className="text-xl font-bold text-orange-800 mb-2">{t('changesRequested') || 'Changes Requested'}</h3>
                        <p className="text-orange-700">{t('changesSubmitted') || 'Your change requests have been submitted.'}</p>
                      </>
                    )}
                  </div>
                ) : (
                  <div className="space-y-4">
                    {showChangeForm ? (
                      <div className="p-4 bg-orange-50 rounded-lg">
                        <Label className="text-orange-800">{t('changeDetails') || 'Please describe the changes you need'} *</Label>
                        <Textarea
                          value={changeRequests}
                          onChange={(e) => setChangeRequests(e.target.value)}
                          placeholder={t('changeDetailsPlaceholder') || 'Describe the schedule changes or concerns about the audit team...'}
                          className="mt-2"
                          rows={4}
                        />
                        <div className="flex gap-2 mt-4">
                          <Button variant="outline" onClick={() => setShowChangeForm(false)} disabled={submitting}>
                            {t('cancel') || 'Cancel'}
                          </Button>
                          <Button onClick={handleRequestChanges} disabled={submitting} className="bg-orange-600 hover:bg-orange-700">
                            {submitting ? t('submitting') || 'Submitting...' : t('submitChanges') || 'Submit Changes'}
                          </Button>
                        </div>
                      </div>
                    ) : (
                      <div className="flex gap-4">
                        <Button 
                          onClick={handleAccept} 
                          disabled={submitting}
                          className="flex-1 bg-violet-600 hover:bg-violet-700 py-6 text-lg"
                          data-testid="accept-plan-btn"
                        >
                          <CheckCircle className="w-5 h-5 mr-2" />
                          {submitting ? t('accepting') || 'Accepting...' : t('acceptPlan') || 'Accept Plan'}
                        </Button>
                        <Button 
                          variant="outline"
                          onClick={() => setShowChangeForm(true)}
                          disabled={submitting}
                          className="flex-1 py-6 text-lg border-orange-300 text-orange-600 hover:bg-orange-50"
                          data-testid="request-changes-btn"
                        >
                          <XCircle className="w-5 h-5 mr-2" />
                          {t('requestChanges') || 'Request Changes'}
                        </Button>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}
          </CardContent>
        </Card>
        
        {/* Footer */}
        <div className="text-center text-sm text-gray-500">
          <p>BAYAN Auditing & Conformity</p>
          <p className="mt-1">{t('stage2Footer') || 'Stage 2 Audit Plan - BACF6-08'}</p>
        </div>
      </div>
    </div>
  );
}
