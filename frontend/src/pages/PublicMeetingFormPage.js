import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import axios from 'axios';
import { API } from '@/lib/apiConfig';
import {
  FileText, CheckCircle, Building, Calendar,
  Users, Clock, AlertCircle, Plus, Trash2
} from 'lucide-react';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { Textarea } from '../components/ui/textarea';
import { Label } from '../components/ui/label';



export default function PublicMeetingFormPage() {
  const { accessToken } = useParams();
  const { t, i18n } = useTranslation();
  const isRTL = i18n.language === 'ar';
  
  const [meeting, setMeeting] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  
  // Form state
  const [attendees, setAttendees] = useState([]);
  const [openingMeetingNotes, setOpeningMeetingNotes] = useState('');
  const [closingMeetingNotes, setClosingMeetingNotes] = useState('');
  
  useEffect(() => {
    fetchMeeting();
  }, [accessToken]);
  
  const fetchMeeting = async () => {
    try {
      const response = await axios.get(`${API}/public/opening-closing-meetings/${accessToken}`);
      setMeeting(response.data);
      
      // Initialize attendees from response or create 5 empty slots
      const existingAttendees = response.data.attendees || [];
      if (existingAttendees.length > 0) {
        setAttendees(existingAttendees);
      } else {
        setAttendees([
          { name: '', designation: '', opening_meeting_date: '', closing_meeting_date: '' },
          { name: '', designation: '', opening_meeting_date: '', closing_meeting_date: '' },
          { name: '', designation: '', opening_meeting_date: '', closing_meeting_date: '' },
          { name: '', designation: '', opening_meeting_date: '', closing_meeting_date: '' },
          { name: '', designation: '', opening_meeting_date: '', closing_meeting_date: '' }
        ]);
      }
      
      setOpeningMeetingNotes(response.data.opening_meeting_notes || '');
      setClosingMeetingNotes(response.data.closing_meeting_notes || '');
      
      if (response.data.status === 'submitted') {
        setSubmitted(true);
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Meeting form not found or not yet available');
    } finally {
      setLoading(false);
    }
  };
  
  const updateAttendee = (index, field, value) => {
    const newAttendees = [...attendees];
    newAttendees[index] = { ...newAttendees[index], [field]: value };
    setAttendees(newAttendees);
  };
  
  const addAttendee = () => {
    setAttendees([
      ...attendees,
      { name: '', designation: '', opening_meeting_date: '', closing_meeting_date: '' }
    ]);
  };
  
  const removeAttendee = (index) => {
    if (attendees.length > 1) {
      const newAttendees = attendees.filter((_, i) => i !== index);
      setAttendees(newAttendees);
    }
  };
  
  const handleSubmit = async () => {
    // Validate at least one attendee has name
    const filledAttendees = attendees.filter(a => a.name.trim());
    if (filledAttendees.length === 0) {
      alert(t('atLeastOneAttendee') || 'Please add at least one attendee');
      return;
    }
    
    setSubmitting(true);
    try {
      await axios.post(`${API}/public/opening-closing-meetings/${accessToken}/submit`, {
        attendees: attendees,
        opening_meeting_notes: openingMeetingNotes,
        closing_meeting_notes: closingMeetingNotes
      });
      setSubmitted(true);
      fetchMeeting();
    } catch (err) {
      alert(err.response?.data?.detail || 'Error submitting form');
    } finally {
      setSubmitting(false);
    }
  };
  
  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-600 mx-auto mb-4"></div>
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
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-cyan-600 rounded-full flex items-center justify-center mx-auto mb-4">
            <Users className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900">{t('openingClosingMeeting') || 'Opening & Closing Meeting'}</h1>
          <p className="text-gray-500">BACF6-09 - {t('meetingAttendanceRecord') || 'Meeting Attendance Record'}</p>
        </div>
        
        {/* Form */}
        <Card className="mb-6">
          <CardHeader className="bg-gradient-to-r from-cyan-600 to-teal-600 text-white rounded-t-lg">
            <CardTitle className="flex items-center gap-2">
              <FileText className="w-5 h-5" />
              {meeting?.organization_name}
            </CardTitle>
            <CardDescription className="text-cyan-100">
              {t('fillMeetingAttendance') || 'Please fill in the meeting attendance information'}
            </CardDescription>
          </CardHeader>
          <CardContent className="p-6">
            {meeting && (
              <div className="space-y-6">
                {/* Company Info */}
                <div className="grid grid-cols-2 gap-4 p-4 bg-gray-50 rounded-lg">
                  <div className="flex items-center gap-2">
                    <Building className="w-4 h-4 text-gray-400" />
                    <div>
                      <p className="text-sm text-gray-500">{t('company') || 'Company'}</p>
                      <p className="font-medium">{meeting.organization_name}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Calendar className="w-4 h-4 text-gray-400" />
                    <div>
                      <p className="text-sm text-gray-500">{t('auditDate') || 'Audit Date'}</p>
                      <p className="font-medium">{meeting.audit_date || '-'}</p>
                    </div>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">{t('auditType') || 'Audit Type'}</p>
                    <p className="font-medium">{meeting.audit_type}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">{t('standards') || 'Standards'}</p>
                    <p className="font-medium">{meeting.standards?.join(', ') || '-'}</p>
                  </div>
                </div>
                
                {submitted ? (
                  <div className="p-8 bg-green-50 rounded-lg text-center">
                    <CheckCircle className="w-16 h-16 text-green-600 mx-auto mb-4" />
                    <h3 className="text-xl font-bold text-green-800 mb-2">{t('formSubmitted') || 'Form Submitted'}</h3>
                    <p className="text-green-700">{t('meetingSubmitSuccess') || 'Thank you! The meeting attendance form has been submitted successfully.'}</p>
                  </div>
                ) : (
                  <>
                    {/* Attendees Table */}
                    <div>
                      <div className="flex justify-between items-center mb-3">
                        <h3 className="font-semibold flex items-center gap-2">
                          <Users className="w-4 h-4" />
                          {t('attendees') || 'Attendees'}
                        </h3>
                        <Button size="sm" variant="outline" onClick={addAttendee}>
                          <Plus className="w-4 h-4 mr-1" />
                          {t('addAttendee') || 'Add Attendee'}
                        </Button>
                      </div>
                      
                      <div className="overflow-x-auto">
                        <table className="w-full text-sm border rounded-lg overflow-hidden">
                          <thead className="bg-cyan-600 text-white">
                            <tr>
                              <th className="p-2 text-left w-10">S.N</th>
                              <th className="p-2 text-left">{t('name') || 'Name'}</th>
                              <th className="p-2 text-left">{t('designation') || 'Designation'}</th>
                              <th className="p-2 text-left">{t('openingMeetingDate') || 'Opening Meeting Date'}</th>
                              <th className="p-2 text-left">{t('closingMeetingDate') || 'Closing Meeting Date'}</th>
                              <th className="p-2 w-10"></th>
                            </tr>
                          </thead>
                          <tbody>
                            {attendees.map((attendee, idx) => (
                              <tr key={idx} className={idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                                <td className="p-2 border">{idx + 1}</td>
                                <td className="p-1 border">
                                  <Input
                                    value={attendee.name}
                                    onChange={(e) => updateAttendee(idx, 'name', e.target.value)}
                                    placeholder={t('enterName') || 'Enter name'}
                                    className="h-8"
                                  />
                                </td>
                                <td className="p-1 border">
                                  <Input
                                    value={attendee.designation}
                                    onChange={(e) => updateAttendee(idx, 'designation', e.target.value)}
                                    placeholder={t('enterDesignation') || 'Designation'}
                                    className="h-8"
                                  />
                                </td>
                                <td className="p-1 border">
                                  <Input
                                    type="date"
                                    value={attendee.opening_meeting_date}
                                    onChange={(e) => updateAttendee(idx, 'opening_meeting_date', e.target.value)}
                                    className="h-8"
                                  />
                                </td>
                                <td className="p-1 border">
                                  <Input
                                    type="date"
                                    value={attendee.closing_meeting_date}
                                    onChange={(e) => updateAttendee(idx, 'closing_meeting_date', e.target.value)}
                                    className="h-8"
                                  />
                                </td>
                                <td className="p-1 border">
                                  {attendees.length > 1 && (
                                    <Button 
                                      size="sm" 
                                      variant="ghost" 
                                      onClick={() => removeAttendee(idx)}
                                      className="text-red-500 h-8 w-8 p-0"
                                    >
                                      <Trash2 className="w-4 h-4" />
                                    </Button>
                                  )}
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                    
                    {/* Meeting Notes */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <Label>{t('openingMeetingNotes') || 'Opening Meeting Notes'}</Label>
                        <Textarea
                          value={openingMeetingNotes}
                          onChange={(e) => setOpeningMeetingNotes(e.target.value)}
                          placeholder={t('openingNotesPlaceholder') || 'Enter any notes from the opening meeting...'}
                          rows={4}
                          className="mt-2"
                        />
                      </div>
                      <div>
                        <Label>{t('closingMeetingNotes') || 'Closing Meeting Notes'}</Label>
                        <Textarea
                          value={closingMeetingNotes}
                          onChange={(e) => setClosingMeetingNotes(e.target.value)}
                          placeholder={t('closingNotesPlaceholder') || 'Enter any notes from the closing meeting...'}
                          rows={4}
                          className="mt-2"
                        />
                      </div>
                    </div>
                    
                    {/* Submit Button */}
                    <div className="flex justify-center pt-4">
                      <Button 
                        onClick={handleSubmit}
                        disabled={submitting}
                        className="bg-cyan-600 hover:bg-cyan-700 px-8 py-6 text-lg"
                        data-testid="submit-meeting-form"
                      >
                        <CheckCircle className="w-5 h-5 mr-2" />
                        {submitting ? t('submitting') || 'Submitting...' : t('submitForm') || 'Submit Form'}
                      </Button>
                    </div>
                  </>
                )}
              </div>
            )}
          </CardContent>
        </Card>
        
        {/* Footer */}
        <div className="text-center text-sm text-gray-500">
          <p>BAYAN for Verification and Conformity</p>
          <p className="mt-1">{t('meetingFooter') || 'Opening & Closing Meeting - BACF6-09'}</p>
        </div>
      </div>
    </div>
  );
}
