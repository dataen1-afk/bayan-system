import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import axios from 'axios';
import { 
  FileText, CheckCircle, XCircle, Building, Calendar,
  User, AlertCircle, Shield, Lock
} from 'lucide-react';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Textarea } from '../components/ui/textarea';
import { Label } from '../components/ui/label';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function PublicJobOrderConfirmPage() {
  const { accessToken } = useParams();
  const { t, i18n } = useTranslation();
  const isRTL = i18n.language === 'ar';
  
  const [jobOrder, setJobOrder] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [rejectReason, setRejectReason] = useState('');
  const [showRejectForm, setShowRejectForm] = useState(false);
  
  useEffect(() => {
    fetchJobOrder();
  }, [accessToken]);
  
  const fetchJobOrder = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/public/job-orders/${accessToken}`);
      setJobOrder(response.data);
      if (response.data.auditor_confirmed || response.data.status === 'rejected') {
        setSubmitted(true);
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Job order not found or not yet approved');
    } finally {
      setLoading(false);
    }
  };
  
  const handleConfirm = async () => {
    setSubmitting(true);
    try {
      await axios.post(`${API_URL}/api/public/job-orders/${accessToken}/confirm`, {
        confirmed: true,
        unable_reason: ''
      });
      setSubmitted(true);
      fetchJobOrder();
    } catch (err) {
      alert(err.response?.data?.detail || 'Error confirming job order');
    } finally {
      setSubmitting(false);
    }
  };
  
  const handleReject = async () => {
    if (!rejectReason.trim()) {
      alert(t('pleaseProvideReason') || 'Please provide a reason for declining');
      return;
    }
    
    setSubmitting(true);
    try {
      await axios.post(`${API_URL}/api/public/job-orders/${accessToken}/confirm`, {
        confirmed: false,
        unable_reason: rejectReason
      });
      setSubmitted(true);
      fetchJobOrder();
    } catch (err) {
      alert(err.response?.data?.detail || 'Error rejecting job order');
    } finally {
      setSubmitting(false);
    }
  };
  
  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-600 mx-auto mb-4"></div>
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
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-emerald-600 rounded-full flex items-center justify-center mx-auto mb-4">
            <FileText className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900">{t('jobOrderConfirmation') || 'Job Order Confirmation'}</h1>
          <p className="text-gray-500">BACF6-06</p>
        </div>
        
        {/* Job Order Details */}
        <Card className="mb-6">
          <CardHeader className="bg-gradient-to-r from-emerald-600 to-teal-600 text-white rounded-t-lg">
            <CardTitle className="flex items-center gap-2">
              <User className="w-5 h-5" />
              {t('appointmentDetails') || 'Appointment Details'}
            </CardTitle>
            <CardDescription className="text-emerald-100">
              {t('reviewAndConfirm') || 'Please review the details and confirm your appointment'}
            </CardDescription>
          </CardHeader>
          <CardContent className="p-6">
            {jobOrder && (
              <div className="space-y-6">
                {/* Auditor Info */}
                <div className="p-4 bg-blue-50 rounded-lg">
                  <h3 className="font-semibold text-blue-800 mb-3 flex items-center gap-2">
                    <User className="w-4 h-4" />
                    {t('yourAppointment') || 'Your Appointment'}
                  </h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm text-gray-500">{t('name') || 'Name'}</p>
                      <p className="font-medium">{jobOrder.auditor_name}</p>
                      {jobOrder.auditor_name_ar && <p className="text-sm text-gray-600">{jobOrder.auditor_name_ar}</p>}
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">{t('position') || 'Position'}</p>
                      <p className="font-medium">{jobOrder.position}</p>
                    </div>
                  </div>
                </div>
                
                {/* Audit Details */}
                <div className="p-4 bg-gray-50 rounded-lg">
                  <h3 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
                    <Building className="w-4 h-4" />
                    {t('auditDetails') || 'Audit Details'}
                  </h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm text-gray-500">{t('organization') || 'Organization'}</p>
                      <p className="font-medium">{jobOrder.organization_name}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">{t('standards') || 'Standards'}</p>
                      <p className="font-medium">{(jobOrder.standards || []).join(', ')}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">{t('auditType') || 'Audit Type'}</p>
                      <p className="font-medium">{jobOrder.audit_type || '-'}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">{t('auditDate') || 'Audit Date'}</p>
                      <p className="font-medium flex items-center gap-1">
                        <Calendar className="w-4 h-4" />
                        {jobOrder.audit_date || '-'}
                      </p>
                    </div>
                  </div>
                  {jobOrder.scope_of_services && (
                    <div className="mt-3">
                      <p className="text-sm text-gray-500">{t('scope') || 'Scope'}</p>
                      <p className="text-sm">{jobOrder.scope_of_services}</p>
                    </div>
                  )}
                </div>
                
                {/* Issued By */}
                <div className="p-4 bg-emerald-50 rounded-lg">
                  <h3 className="font-semibold text-emerald-800 mb-2">{t('issuedBy') || 'Issued By'}</h3>
                  <p><strong>{t('certificationManager') || 'Certification Manager'}:</strong> {jobOrder.certification_manager}</p>
                  <p><strong>{t('date') || 'Date'}:</strong> {jobOrder.manager_approval_date}</p>
                </div>
                
                {/* Declaration */}
                <div className="p-4 bg-yellow-50 rounded-lg border border-yellow-200">
                  <h3 className="font-semibold text-yellow-800 mb-3 flex items-center gap-2">
                    <Shield className="w-4 h-4" />
                    {t('declaration') || 'Declaration'}
                  </h3>
                  <ul className="space-y-2 text-sm text-gray-700">
                    <li className="flex items-start gap-2">
                      <CheckCircle className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
                      {t('declarationIndependence') || 'I am aware of facts which may influence my independence and objectiveness against the auditee.'}
                    </li>
                    <li className="flex items-start gap-2">
                      <Lock className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
                      {t('declarationConfidentiality') || 'Information and data collected during audit will not be provided to third parties nor used for personal benefits.'}
                    </li>
                    <li className="flex items-start gap-2">
                      <CheckCircle className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
                      {t('declarationNoInterest') || 'I confirm that I have no commercial or other interests in the above stated company.'}
                    </li>
                    <li className="flex items-start gap-2">
                      <CheckCircle className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
                      {t('declarationNoConsultancy') || 'I have not acted as a consultant for this company within the last two years.'}
                    </li>
                  </ul>
                </div>
                
                {/* Status / Actions */}
                {submitted ? (
                  <div className={`p-6 rounded-lg text-center ${jobOrder.auditor_confirmed ? 'bg-green-50' : 'bg-red-50'}`}>
                    {jobOrder.auditor_confirmed ? (
                      <>
                        <CheckCircle className="w-16 h-16 text-green-600 mx-auto mb-4" />
                        <h3 className="text-xl font-bold text-green-800 mb-2">{t('confirmed') || 'Confirmed'}</h3>
                        <p className="text-green-700">{t('confirmationSuccess') || 'You have successfully confirmed this job order.'}</p>
                        <p className="text-sm text-green-600 mt-2">{t('confirmationDate') || 'Confirmation Date'}: {jobOrder.auditor_confirmation_date}</p>
                      </>
                    ) : (
                      <>
                        <XCircle className="w-16 h-16 text-red-600 mx-auto mb-4" />
                        <h3 className="text-xl font-bold text-red-800 mb-2">{t('declined') || 'Declined'}</h3>
                        <p className="text-red-700">{t('declineMessage') || 'You have declined this job order.'}</p>
                      </>
                    )}
                  </div>
                ) : (
                  <div className="space-y-4">
                    {showRejectForm ? (
                      <div className="p-4 bg-red-50 rounded-lg">
                        <Label className="text-red-800">{t('reasonForDeclining') || 'Reason for Declining'} *</Label>
                        <Textarea
                          value={rejectReason}
                          onChange={(e) => setRejectReason(e.target.value)}
                          placeholder={t('explainReason') || 'Please explain why you are unable to carry out this assignment...'}
                          className="mt-2"
                          rows={4}
                        />
                        <div className="flex gap-2 mt-4">
                          <Button variant="outline" onClick={() => setShowRejectForm(false)} disabled={submitting}>
                            {t('cancel') || 'Cancel'}
                          </Button>
                          <Button variant="destructive" onClick={handleReject} disabled={submitting}>
                            {submitting ? t('submitting') || 'Submitting...' : t('confirmDecline') || 'Confirm Decline'}
                          </Button>
                        </div>
                      </div>
                    ) : (
                      <div className="flex gap-4">
                        <Button 
                          onClick={handleConfirm} 
                          disabled={submitting}
                          className="flex-1 bg-emerald-600 hover:bg-emerald-700 py-6 text-lg"
                          data-testid="confirm-job-order-btn"
                        >
                          <CheckCircle className="w-5 h-5 mr-2" />
                          {submitting ? t('confirming') || 'Confirming...' : t('confirmAppointment') || 'Confirm Appointment'}
                        </Button>
                        <Button 
                          variant="outline"
                          onClick={() => setShowRejectForm(true)}
                          disabled={submitting}
                          className="flex-1 py-6 text-lg border-red-300 text-red-600 hover:bg-red-50"
                          data-testid="decline-job-order-btn"
                        >
                          <XCircle className="w-5 h-5 mr-2" />
                          {t('decline') || 'Decline'}
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
          <p className="mt-1">{t('jobOrderFooter') || 'Internal Audit Plan - Job Order BACF6-06'}</p>
        </div>
      </div>
    </div>
  );
}
