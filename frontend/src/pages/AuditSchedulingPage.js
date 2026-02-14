import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { 
  Calendar, ArrowLeft, Plus, X, MapPin, Clock, Users, Building2,
  ChevronLeft, ChevronRight, Loader2, AlertCircle, CheckCircle,
  Edit2, Trash2, Eye
} from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL + '/api';

// Calendar helper functions
const getDaysInMonth = (year, month) => new Date(year, month + 1, 0).getDate();
const getFirstDayOfMonth = (year, month) => new Date(year, month, 1).getDay();

const formatDate = (dateString) => {
  if (!dateString) return '';
  return new Date(dateString).toLocaleDateString('en-GB', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  });
};

const AuditSchedulingPage = () => {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const isRTL = i18n.language?.startsWith('ar');
  
  const [loading, setLoading] = useState(true);
  const [audits, setAudits] = useState([]);
  const [sites, setSites] = useState([]);
  const [contracts, setContracts] = useState([]);
  
  // Calendar state
  const [currentDate, setCurrentDate] = useState(new Date());
  const [selectedDate, setSelectedDate] = useState(null);
  const [viewMode, setViewMode] = useState('calendar'); // 'calendar' or 'list'
  
  // Modal states
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showViewModal, setShowViewModal] = useState(false);
  const [selectedAudit, setSelectedAudit] = useState(null);
  
  // Form state
  const [formData, setFormData] = useState({
    contract_id: '',
    site_id: '',
    audit_type: 'initial',
    scheduled_date: '',
    scheduled_time: '09:00',
    duration_days: 1,
    auditors: '',
    notes: ''
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const headers = { Authorization: `Bearer ${token}` };
      
      const [auditsRes, sitesRes, proposalsRes] = await Promise.all([
        axios.get(`${API}/audit-schedules`, { headers }),
        axios.get(`${API}/sites`, { headers }),
        axios.get(`${API}/proposals`, { headers })
      ]);
      
      setAudits(auditsRes.data);
      setSites(sitesRes.data);
      // Filter only signed contracts
      setContracts(proposalsRes.data.filter(p => p.status === 'agreement_signed'));
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateAudit = async () => {
    try {
      const token = localStorage.getItem('token');
      const headers = { Authorization: `Bearer ${token}` };
      
      await axios.post(`${API}/audit-schedules`, formData, { headers });
      setShowCreateModal(false);
      setFormData({
        contract_id: '',
        site_id: '',
        audit_type: 'initial',
        scheduled_date: '',
        scheduled_time: '09:00',
        duration_days: 1,
        auditors: '',
        notes: ''
      });
      loadData();
    } catch (error) {
      console.error('Error creating audit:', error);
      alert(t('errorCreatingAudit'));
    }
  };

  const handleDeleteAudit = async (auditId) => {
    if (!window.confirm(t('confirmDeleteAudit'))) return;
    
    try {
      const token = localStorage.getItem('token');
      const headers = { Authorization: `Bearer ${token}` };
      
      await axios.delete(`${API}/audit-schedules/${auditId}`, { headers });
      loadData();
    } catch (error) {
      console.error('Error deleting audit:', error);
      alert(t('errorDeletingAudit'));
    }
  };

  // Calendar navigation
  const goToPreviousMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1, 1));
  };

  const goToNextMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 1));
  };

  const goToToday = () => {
    setCurrentDate(new Date());
  };

  // Get audits for a specific date
  const getAuditsForDate = (date) => {
    const dateStr = date.toISOString().split('T')[0];
    return audits.filter(a => a.scheduled_date?.startsWith(dateStr));
  };

  // Render calendar
  const renderCalendar = () => {
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();
    const daysInMonth = getDaysInMonth(year, month);
    const firstDay = getFirstDayOfMonth(year, month);
    
    const days = [];
    const weekDays = isRTL 
      ? ['السبت', 'الجمعة', 'الخميس', 'الأربعاء', 'الثلاثاء', 'الإثنين', 'الأحد']
      : ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    
    // Empty cells before first day
    for (let i = 0; i < firstDay; i++) {
      days.push(<div key={`empty-${i}`} className="h-24 bg-slate-50/50" />);
    }
    
    // Days of month
    for (let day = 1; day <= daysInMonth; day++) {
      const date = new Date(year, month, day);
      const dayAudits = getAuditsForDate(date);
      const isToday = new Date().toDateString() === date.toDateString();
      const isSelected = selectedDate?.toDateString() === date.toDateString();
      
      days.push(
        <div
          key={day}
          onClick={() => setSelectedDate(date)}
          className={`
            h-24 p-2 border-t border-slate-100 cursor-pointer transition-all
            hover:bg-blue-50/50
            ${isToday ? 'bg-bayan-navy/5' : 'bg-white'}
            ${isSelected ? 'ring-2 ring-bayan-navy ring-inset' : ''}
          `}
        >
          <div className={`
            text-sm font-medium mb-1
            ${isToday ? 'text-bayan-navy font-bold' : 'text-slate-700'}
          `}>
            {day}
          </div>
          <div className="space-y-1 overflow-hidden">
            {dayAudits.slice(0, 2).map((audit, idx) => (
              <div
                key={audit.id}
                className={`
                  text-xs px-1.5 py-0.5 rounded truncate
                  ${audit.audit_type === 'initial' ? 'bg-blue-100 text-blue-700' :
                    audit.audit_type === 'surveillance' ? 'bg-amber-100 text-amber-700' :
                    'bg-emerald-100 text-emerald-700'}
                `}
                onClick={(e) => {
                  e.stopPropagation();
                  setSelectedAudit(audit);
                  setShowViewModal(true);
                }}
              >
                {audit.organization_name?.substring(0, 15)}...
              </div>
            ))}
            {dayAudits.length > 2 && (
              <div className="text-xs text-slate-500 px-1">
                +{dayAudits.length - 2} {t('more')}
              </div>
            )}
          </div>
        </div>
      );
    }
    
    return (
      <div className="grid grid-cols-7 border border-slate-200 rounded-lg overflow-hidden">
        {/* Week day headers */}
        {weekDays.map((day) => (
          <div key={day} className="py-3 text-center text-sm font-semibold text-slate-600 bg-slate-50 border-b border-slate-200">
            {day}
          </div>
        ))}
        {days}
      </div>
    );
  };

  // Render list view
  const renderListView = () => {
    const sortedAudits = [...audits].sort((a, b) => 
      new Date(a.scheduled_date) - new Date(b.scheduled_date)
    );
    
    return (
      <div className="space-y-3">
        {sortedAudits.length === 0 ? (
          <div className="text-center py-12">
            <Calendar className="w-16 h-16 mx-auto text-slate-300 mb-4" />
            <h3 className="text-lg font-semibold text-slate-700 mb-2">{t('noAuditsScheduled')}</h3>
            <p className="text-slate-500">{t('createFirstAudit')}</p>
          </div>
        ) : (
          sortedAudits.map((audit) => (
            <Card 
              key={audit.id} 
              className="hover:shadow-md transition-shadow cursor-pointer"
              onClick={() => {
                setSelectedAudit(audit);
                setShowViewModal(true);
              }}
              data-testid={`audit-card-${audit.id}`}
            >
              <CardContent className="p-4">
                <div className={`flex items-start justify-between ${isRTL ? 'flex-row-reverse' : ''}`}>
                  <div className={`flex-1 ${isRTL ? 'text-right' : 'text-left'}`}>
                    <div className={`flex items-center gap-2 mb-2 ${isRTL ? 'flex-row-reverse justify-end' : ''}`}>
                      <h3 className="font-semibold text-slate-900">{audit.organization_name}</h3>
                      <span className={`
                        px-2 py-0.5 text-xs font-medium rounded-full
                        ${audit.audit_type === 'initial' ? 'bg-blue-100 text-blue-700' :
                          audit.audit_type === 'surveillance' ? 'bg-amber-100 text-amber-700' :
                          'bg-emerald-100 text-emerald-700'}
                      `}>
                        {t(audit.audit_type)}
                      </span>
                    </div>
                    
                    <div className={`flex flex-wrap gap-4 text-sm text-slate-600 ${isRTL ? 'flex-row-reverse justify-end' : ''}`}>
                      <span className={`flex items-center gap-1 ${isRTL ? 'flex-row-reverse' : ''}`}>
                        <Calendar className="w-4 h-4" />
                        {formatDate(audit.scheduled_date)}
                      </span>
                      <span className={`flex items-center gap-1 ${isRTL ? 'flex-row-reverse' : ''}`}>
                        <Clock className="w-4 h-4" />
                        {audit.scheduled_time || '09:00'}
                      </span>
                      <span className={`flex items-center gap-1 ${isRTL ? 'flex-row-reverse' : ''}`}>
                        <MapPin className="w-4 h-4" />
                        {audit.site_name || t('mainSite')}
                      </span>
                    </div>
                  </div>
                  
                  <div className={`flex items-center gap-2 ${isRTL ? 'flex-row-reverse' : ''}`}>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDeleteAudit(audit.id);
                      }}
                      className="text-red-500 hover:text-red-700 hover:bg-red-50"
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    );
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-bayan-navy" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50" dir={isRTL ? 'rtl' : 'ltr'}>
      {/* Header */}
      <div className="bg-white border-b px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className={`flex items-center gap-4 ${isRTL ? 'flex-row-reverse' : ''}`}>
            <Button 
              variant="ghost" 
              onClick={() => navigate('/dashboard')}
              className={isRTL ? 'flex-row-reverse' : ''}
              data-testid="back-to-dashboard-btn"
            >
              <ArrowLeft className={`w-4 h-4 ${isRTL ? 'ml-2 rotate-180' : 'mr-2'}`} />
              {t('backToDashboard')}
            </Button>
            <h1 className="text-2xl font-bold text-bayan-navy flex items-center gap-2">
              <Calendar className="w-6 h-6" />
              {t('auditScheduling')}
            </h1>
          </div>
          <div className="flex items-center gap-2">
            {/* View Toggle */}
            <div className="flex bg-slate-100 rounded-lg p-1">
              <Button
                variant={viewMode === 'calendar' ? 'default' : 'ghost'}
                size="sm"
                onClick={() => setViewMode('calendar')}
                className={viewMode === 'calendar' ? 'bg-white shadow-sm' : ''}
              >
                <Calendar className="w-4 h-4 me-1" />
                {t('calendar')}
              </Button>
              <Button
                variant={viewMode === 'list' ? 'default' : 'ghost'}
                size="sm"
                onClick={() => setViewMode('list')}
                className={viewMode === 'list' ? 'bg-white shadow-sm' : ''}
              >
                <Users className="w-4 h-4 me-1" />
                {t('list')}
              </Button>
            </div>
            
            <Button 
              onClick={() => setShowCreateModal(true)}
              className="bg-bayan-navy hover:bg-bayan-navy-light"
              data-testid="create-audit-btn"
            >
              <Plus className="w-4 h-4 me-2" />
              {t('scheduleAudit')}
            </Button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {viewMode === 'calendar' ? (
          <>
            {/* Calendar Controls */}
            <div className={`flex items-center justify-between mb-6 ${isRTL ? 'flex-row-reverse' : ''}`}>
              <div className={`flex items-center gap-4 ${isRTL ? 'flex-row-reverse' : ''}`}>
                <Button variant="outline" size="sm" onClick={goToPreviousMonth}>
                  <ChevronLeft className="w-4 h-4" />
                </Button>
                <h2 className="text-xl font-semibold text-slate-800 min-w-[200px] text-center">
                  {currentDate.toLocaleDateString(isRTL ? 'ar-SA' : 'en-US', { month: 'long', year: 'numeric' })}
                </h2>
                <Button variant="outline" size="sm" onClick={goToNextMonth}>
                  <ChevronRight className="w-4 h-4" />
                </Button>
              </div>
              <Button variant="outline" onClick={goToToday}>
                {t('today')}
              </Button>
            </div>
            
            {/* Calendar Grid */}
            {renderCalendar()}
            
            {/* Selected Date Audits */}
            {selectedDate && (
              <Card className="mt-6" data-testid="selected-date-audits">
                <CardHeader className={isRTL ? 'text-right' : 'text-left'}>
                  <CardTitle>
                    {t('auditsFor')} {formatDate(selectedDate.toISOString())}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {getAuditsForDate(selectedDate).length === 0 ? (
                    <p className="text-slate-500 text-center py-4">{t('noAuditsOnThisDate')}</p>
                  ) : (
                    <div className="space-y-3">
                      {getAuditsForDate(selectedDate).map((audit) => (
                        <div 
                          key={audit.id}
                          className={`p-4 bg-slate-50 rounded-lg ${isRTL ? 'text-right' : 'text-left'}`}
                        >
                          <div className={`flex items-center justify-between ${isRTL ? 'flex-row-reverse' : ''}`}>
                            <div>
                              <h4 className="font-semibold text-slate-900">{audit.organization_name}</h4>
                              <p className="text-sm text-slate-600">
                                {audit.scheduled_time} - {audit.site_name || t('mainSite')}
                              </p>
                            </div>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => {
                                setSelectedAudit(audit);
                                setShowViewModal(true);
                              }}
                            >
                              <Eye className="w-4 h-4 me-1" />
                              {t('view')}
                            </Button>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            )}
          </>
        ) : (
          renderListView()
        )}
      </div>

      {/* Create Audit Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <Card className="w-full max-w-lg max-h-[90vh] overflow-y-auto">
            <CardHeader className={isRTL ? 'text-right' : 'text-left'}>
              <div className={`flex justify-between items-center ${isRTL ? 'flex-row-reverse' : ''}`}>
                <CardTitle>{t('scheduleNewAudit')}</CardTitle>
                <Button variant="ghost" size="sm" onClick={() => setShowCreateModal(false)}>
                  <X className="w-4 h-4" />
                </Button>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Contract Selection */}
              <div className="space-y-2">
                <Label className={isRTL ? 'text-right block' : ''}>{t('selectContract')} *</Label>
                <select
                  value={formData.contract_id}
                  onChange={(e) => setFormData({ ...formData, contract_id: e.target.value })}
                  className="w-full h-10 px-3 rounded-md border border-input bg-background"
                  data-testid="contract-select"
                >
                  <option value="">{t('selectContract')}</option>
                  {contracts.map((contract) => (
                    <option key={contract.id} value={contract.id}>
                      {contract.organization_name} - {contract.standards?.join(', ')}
                    </option>
                  ))}
                </select>
              </div>

              {/* Audit Type */}
              <div className="space-y-2">
                <Label className={isRTL ? 'text-right block' : ''}>{t('auditType')} *</Label>
                <select
                  value={formData.audit_type}
                  onChange={(e) => setFormData({ ...formData, audit_type: e.target.value })}
                  className="w-full h-10 px-3 rounded-md border border-input bg-background"
                >
                  <option value="initial">{t('initialAudit')}</option>
                  <option value="surveillance">{t('surveillanceAudit')}</option>
                  <option value="recertification">{t('recertificationAudit')}</option>
                </select>
              </div>

              {/* Date and Time */}
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label className={isRTL ? 'text-right block' : ''}>{t('date')} *</Label>
                  <Input
                    type="date"
                    value={formData.scheduled_date}
                    onChange={(e) => setFormData({ ...formData, scheduled_date: e.target.value })}
                    data-testid="audit-date-input"
                  />
                </div>
                <div className="space-y-2">
                  <Label className={isRTL ? 'text-right block' : ''}>{t('time')}</Label>
                  <Input
                    type="time"
                    value={formData.scheduled_time}
                    onChange={(e) => setFormData({ ...formData, scheduled_time: e.target.value })}
                  />
                </div>
              </div>

              {/* Duration */}
              <div className="space-y-2">
                <Label className={isRTL ? 'text-right block' : ''}>{t('durationDays')}</Label>
                <Input
                  type="number"
                  min="1"
                  value={formData.duration_days}
                  onChange={(e) => setFormData({ ...formData, duration_days: parseInt(e.target.value) || 1 })}
                />
              </div>

              {/* Auditors */}
              <div className="space-y-2">
                <Label className={isRTL ? 'text-right block' : ''}>{t('auditors')}</Label>
                <Input
                  value={formData.auditors}
                  onChange={(e) => setFormData({ ...formData, auditors: e.target.value })}
                  placeholder={t('enterAuditorNames')}
                />
              </div>

              {/* Notes */}
              <div className="space-y-2">
                <Label className={isRTL ? 'text-right block' : ''}>{t('notes')}</Label>
                <Textarea
                  value={formData.notes}
                  onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                  placeholder={t('additionalNotes')}
                  rows={3}
                />
              </div>

              <div className={`flex gap-2 pt-4 ${isRTL ? 'flex-row-reverse' : ''}`}>
                <Button variant="outline" onClick={() => setShowCreateModal(false)}>
                  {t('cancel')}
                </Button>
                <Button 
                  onClick={handleCreateAudit}
                  className="bg-bayan-navy hover:bg-bayan-navy-light"
                  disabled={!formData.contract_id || !formData.scheduled_date}
                  data-testid="confirm-create-audit-btn"
                >
                  <Plus className="w-4 h-4 me-2" />
                  {t('scheduleAudit')}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* View Audit Modal */}
      {showViewModal && selectedAudit && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <Card className="w-full max-w-lg">
            <CardHeader className={isRTL ? 'text-right' : 'text-left'}>
              <div className={`flex justify-between items-center ${isRTL ? 'flex-row-reverse' : ''}`}>
                <CardTitle>{t('auditDetails')}</CardTitle>
                <Button variant="ghost" size="sm" onClick={() => setShowViewModal(false)}>
                  <X className="w-4 h-4" />
                </Button>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className={`space-y-3 ${isRTL ? 'text-right' : 'text-left'}`}>
                <div>
                  <Label className="text-slate-500">{t('organization')}</Label>
                  <p className="font-semibold text-lg">{selectedAudit.organization_name}</p>
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label className="text-slate-500">{t('auditType')}</Label>
                    <p className="font-medium">{t(selectedAudit.audit_type)}</p>
                  </div>
                  <div>
                    <Label className="text-slate-500">{t('duration')}</Label>
                    <p className="font-medium">{selectedAudit.duration_days} {t('days')}</p>
                  </div>
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label className="text-slate-500">{t('date')}</Label>
                    <p className="font-medium">{formatDate(selectedAudit.scheduled_date)}</p>
                  </div>
                  <div>
                    <Label className="text-slate-500">{t('time')}</Label>
                    <p className="font-medium">{selectedAudit.scheduled_time || '09:00'}</p>
                  </div>
                </div>
                
                {selectedAudit.site_name && (
                  <div>
                    <Label className="text-slate-500">{t('site')}</Label>
                    <p className="font-medium">{selectedAudit.site_name}</p>
                  </div>
                )}
                
                {selectedAudit.auditors && (
                  <div>
                    <Label className="text-slate-500">{t('auditors')}</Label>
                    <p className="font-medium">{selectedAudit.auditors}</p>
                  </div>
                )}
                
                {selectedAudit.notes && (
                  <div>
                    <Label className="text-slate-500">{t('notes')}</Label>
                    <p className="text-slate-700">{selectedAudit.notes}</p>
                  </div>
                )}
              </div>
              
              <div className={`flex gap-2 pt-4 ${isRTL ? 'flex-row-reverse' : ''}`}>
                <Button variant="outline" onClick={() => setShowViewModal(false)}>
                  {t('close')}
                </Button>
                <Button 
                  variant="destructive"
                  onClick={() => {
                    handleDeleteAudit(selectedAudit.id);
                    setShowViewModal(false);
                  }}
                >
                  <Trash2 className="w-4 h-4 me-2" />
                  {t('delete')}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
};

export default AuditSchedulingPage;
