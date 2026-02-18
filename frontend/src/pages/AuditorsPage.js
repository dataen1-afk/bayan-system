import React, { useState, useEffect, useContext } from 'react';
import axios from 'axios';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { 
  ArrowLeft, Plus, X, Users, User, Mail, Phone, Award, Calendar,
  Search, Filter, Edit, Trash2, CheckCircle, Clock, AlertCircle,
  Briefcase, Star, Shield
} from 'lucide-react';
import { AuthContext } from '@/App';

const API = process.env.REACT_APP_BACKEND_URL + '/api';

const AuditorsPage = () => {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const { user, logout } = useContext(AuthContext);
  const isRTL = i18n.language?.startsWith('ar');
  
  const [loading, setLoading] = useState(true);
  const [auditors, setAuditors] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [specializationFilter, setSpecializationFilter] = useState('all');
  
  // Modals
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showViewModal, setShowViewModal] = useState(false);
  const [showAvailabilityModal, setShowAvailabilityModal] = useState(false);
  const [selectedAuditor, setSelectedAuditor] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  
  // Form state
  const [formData, setFormData] = useState({
    employee_id: '',
    name: '',
    name_ar: '',
    email: '',
    phone: '',
    mobile: '',
    specializations: [],
    certification_level: 'auditor',
    years_experience: 0,
    certifications: [],
    max_audits_per_month: 10,
    notes: ''
  });
  
  const [availabilityData, setAvailabilityData] = useState({
    date: '',
    is_available: false,
    reason: ''
  });

  const standardOptions = ['ISO 9001', 'ISO 14001', 'ISO 45001', 'ISO 22000', 'ISO 27001', 'ISO 50001'];
  const certificationLevels = [
    { value: 'trainee', label: t('trainee') },
    { value: 'auditor', label: t('auditor') },
    { value: 'lead_auditor', label: t('leadAuditor') },
    { value: 'technical_expert', label: t('technicalExpert') }
  ];

  useEffect(() => {
    loadAuditors();
  }, []);

  const loadAuditors = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/auditors`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setAuditors(response.data);
    } catch (error) {
      console.error('Error loading auditors:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateAuditor = async () => {
    if (!formData.name || !formData.email) {
      alert(t('fillRequiredFields'));
      return;
    }
    
    try {
      const token = localStorage.getItem('token');
      
      if (isEditing && selectedAuditor) {
        await axios.put(`${API}/auditors/${selectedAuditor.id}`, formData, {
          headers: { Authorization: `Bearer ${token}` }
        });
      } else {
        await axios.post(`${API}/auditors`, formData, {
          headers: { Authorization: `Bearer ${token}` }
        });
      }
      
      setShowCreateModal(false);
      resetForm();
      loadAuditors();
    } catch (error) {
      alert(error.response?.data?.detail || t('errorSavingAuditor'));
    }
  };

  const handleDeleteAuditor = async (auditorId) => {
    if (!window.confirm(t('confirmDeactivateAuditor'))) return;
    
    try {
      const token = localStorage.getItem('token');
      await axios.delete(`${API}/auditors/${auditorId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      loadAuditors();
    } catch (error) {
      alert(error.response?.data?.detail || t('errorDeletingAuditor'));
    }
  };

  const handleSetAvailability = async () => {
    if (!availabilityData.date) {
      alert(t('selectDate'));
      return;
    }
    
    try {
      const token = localStorage.getItem('token');
      await axios.post(`${API}/auditors/${selectedAuditor.id}/availability`, availabilityData, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setShowAvailabilityModal(false);
      setAvailabilityData({ date: '', is_available: false, reason: '' });
      loadAuditors();
    } catch (error) {
      alert(t('errorSettingAvailability'));
    }
  };

  const resetForm = () => {
    setFormData({
      employee_id: '',
      name: '',
      name_ar: '',
      email: '',
      phone: '',
      mobile: '',
      specializations: [],
      certification_level: 'auditor',
      years_experience: 0,
      certifications: [],
      max_audits_per_month: 10,
      notes: ''
    });
    setIsEditing(false);
    setSelectedAuditor(null);
  };

  const openEditModal = (auditor) => {
    setFormData({
      employee_id: auditor.employee_id || '',
      name: auditor.name || '',
      name_ar: auditor.name_ar || '',
      email: auditor.email || '',
      phone: auditor.phone || '',
      mobile: auditor.mobile || '',
      specializations: auditor.specializations || [],
      certification_level: auditor.certification_level || 'auditor',
      years_experience: auditor.years_experience || 0,
      certifications: auditor.certifications || [],
      max_audits_per_month: auditor.max_audits_per_month || 10,
      notes: auditor.notes || ''
    });
    setSelectedAuditor(auditor);
    setIsEditing(true);
    setShowCreateModal(true);
  };

  const toggleSpecialization = (spec) => {
    setFormData(prev => ({
      ...prev,
      specializations: prev.specializations.includes(spec)
        ? prev.specializations.filter(s => s !== spec)
        : [...prev.specializations, spec]
    }));
  };

  const getStatusColor = (status) => {
    const colors = {
      active: 'bg-emerald-100 text-emerald-700 border-emerald-200',
      inactive: 'bg-slate-100 text-slate-700 border-slate-200',
      on_leave: 'bg-amber-100 text-amber-700 border-amber-200'
    };
    return colors[status] || colors.active;
  };

  const getLevelColor = (level) => {
    const colors = {
      trainee: 'bg-blue-100 text-blue-700',
      auditor: 'bg-purple-100 text-purple-700',
      lead_auditor: 'bg-indigo-100 text-indigo-700',
      technical_expert: 'bg-amber-100 text-amber-700'
    };
    return colors[level] || colors.auditor;
  };

  const filteredAuditors = auditors.filter(auditor => {
    const matchesSearch = auditor.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          auditor.email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          auditor.employee_id?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'all' || auditor.status === statusFilter;
    const matchesSpec = specializationFilter === 'all' || auditor.specializations?.includes(specializationFilter);
    return matchesSearch && matchesStatus && matchesSpec;
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-xl">{t('loading')}...</div>
      </div>
    );
  }

  return (
    <div className="p-4 lg:p-6" dir={isRTL ? 'rtl' : 'ltr'}>
      {/* Page Header */}
      <div className={`flex items-center justify-between mb-6 ${isRTL ? 'flex-row-reverse' : ''}`}>
        <div className={`flex items-center gap-4 ${isRTL ? 'flex-row-reverse' : ''}`}>
          <Button variant="ghost" onClick={() => navigate('/dashboard')} className={`${isRTL ? 'flex-row-reverse' : ''}`}>
            <ArrowLeft className={`w-4 h-4 ${isRTL ? 'rotate-180 ml-2' : 'mr-2'}`} />
            {t('backToDashboard')}
          </Button>
          <div>
            <h1 className={`text-2xl font-bold text-slate-900 flex items-center gap-2 ${isRTL ? 'flex-row-reverse' : ''}`}>
              <Users className="w-7 h-7 text-bayan-navy" />
              {t('auditorManagement')}
            </h1>
          </div>
        </div>
        
        <Button onClick={() => { resetForm(); setShowCreateModal(true); }} className="bg-bayan-primary hover:bg-bayan-primary/90" data-testid="add-auditor-btn">
          <Plus className={`w-4 h-4 ${isRTL ? 'ml-2' : 'mr-2'}`} />
          {t('addAuditor')}
        </Button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <Card className="border-slate-200">
          <CardContent className="pt-4">
            <div className={`flex items-center gap-3 ${isRTL ? 'flex-row-reverse' : ''}`}>
              <div className="p-2 bg-blue-100 rounded-lg">
                <Users className="w-5 h-5 text-blue-600" />
              </div>
              <div className={isRTL ? 'text-right' : ''}>
                <p className="text-2xl font-bold">{auditors.length}</p>
                <p className="text-xs text-slate-500">{t('totalAuditors')}</p>
              </div>
            </div>
          </CardContent>
        </Card>
            
            <Card className="border-emerald-200">
              <CardContent className="pt-4">
                <div className={`flex items-center gap-3 ${isRTL ? 'flex-row-reverse' : ''}`}>
                  <div className="p-2 bg-emerald-100 rounded-lg">
                    <CheckCircle className="w-5 h-5 text-emerald-600" />
                  </div>
                  <div className={isRTL ? 'text-right' : ''}>
                    <p className="text-2xl font-bold text-emerald-700">
                      {auditors.filter(a => a.status === 'active').length}
                    </p>
                    <p className="text-xs text-slate-500">{t('activeAuditors')}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
            
            <Card className="border-indigo-200">
              <CardContent className="pt-4">
                <div className={`flex items-center gap-3 ${isRTL ? 'flex-row-reverse' : ''}`}>
                  <div className="p-2 bg-indigo-100 rounded-lg">
                    <Star className="w-5 h-5 text-indigo-600" />
                  </div>
                  <div className={isRTL ? 'text-right' : ''}>
                    <p className="text-2xl font-bold text-indigo-700">
                      {auditors.filter(a => a.certification_level === 'lead_auditor').length}
                    </p>
                    <p className="text-xs text-slate-500">{t('leadAuditors')}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
            
            <Card className="border-amber-200">
              <CardContent className="pt-4">
                <div className={`flex items-center gap-3 ${isRTL ? 'flex-row-reverse' : ''}`}>
                  <div className="p-2 bg-amber-100 rounded-lg">
                    <Briefcase className="w-5 h-5 text-amber-600" />
                  </div>
                  <div className={isRTL ? 'text-right' : ''}>
                    <p className="text-2xl font-bold text-amber-700">
                      {auditors.reduce((sum, a) => sum + (a.current_assignments || 0), 0)}
                    </p>
                    <p className="text-xs text-slate-500">{t('activeAssignments')}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Filters */}
          <div className={`flex items-center gap-4 mb-6 flex-wrap ${isRTL ? 'flex-row-reverse' : ''}`}>
            <div className="relative flex-1 min-w-[200px] max-w-md">
              <Search className={`absolute top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 ${isRTL ? 'right-3' : 'left-3'}`} />
              <Input
                placeholder={t('searchAuditors')}
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className={isRTL ? 'pr-10' : 'pl-10'}
              />
            </div>
            
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-[160px]">
                <SelectValue placeholder={t('status')} />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">{t('allStatuses')}</SelectItem>
                <SelectItem value="active">{t('active')}</SelectItem>
                <SelectItem value="inactive">{t('inactive')}</SelectItem>
                <SelectItem value="on_leave">{t('onLeave')}</SelectItem>
              </SelectContent>
            </Select>
            
            <Select value={specializationFilter} onValueChange={setSpecializationFilter}>
              <SelectTrigger className="w-[160px]">
                <SelectValue placeholder={t('specialization')} />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">{t('allSpecializations')}</SelectItem>
                {standardOptions.map(std => (
                  <SelectItem key={std} value={std}>{std}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Auditors Grid */}
          {filteredAuditors.length === 0 ? (
            <Card className="p-16 text-center">
              <Users className="w-16 h-16 mx-auto text-slate-300 mb-4" />
              <h3 className="text-lg font-semibold text-slate-700 mb-2">{t('noAuditors')}</h3>
              <p className="text-sm text-slate-500">{t('addFirstAuditor')}</p>
            </Card>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {filteredAuditors.map((auditor) => (
                <Card key={auditor.id} className="border-slate-200 hover:border-bayan-primary/50 transition-colors">
                  <CardContent className="pt-4">
                    <div className={`flex items-start justify-between mb-3 ${isRTL ? 'flex-row-reverse' : ''}`}>
                      <div className={`flex items-center gap-3 ${isRTL ? 'flex-row-reverse' : ''}`}>
                        <div className="w-12 h-12 bg-gradient-to-br from-bayan-navy to-bayan-primary rounded-full flex items-center justify-center text-white font-bold">
                          {auditor.name?.charAt(0).toUpperCase()}
                        </div>
                        <div>
                          <h3 className={`font-semibold text-slate-900 ${isRTL ? 'text-right' : ''}`}>{auditor.name}</h3>
                          {auditor.name_ar && (
                            <p className="text-xs text-slate-500">{auditor.name_ar}</p>
                          )}
                        </div>
                      </div>
                      <span className={`px-2 py-0.5 text-xs font-medium rounded-full border ${getStatusColor(auditor.status)}`}>
                        {t(auditor.status)}
                      </span>
                    </div>
                    
                    <div className="space-y-2 text-sm">
                      <div className={`flex items-center gap-2 text-slate-600 ${isRTL ? 'flex-row-reverse' : ''}`}>
                        <Mail className="w-4 h-4 text-slate-400" />
                        <span className="truncate">{auditor.email}</span>
                      </div>
                      
                      {auditor.mobile && (
                        <div className={`flex items-center gap-2 text-slate-600 ${isRTL ? 'flex-row-reverse' : ''}`}>
                          <Phone className="w-4 h-4 text-slate-400" />
                          <span dir="ltr">{auditor.mobile}</span>
                        </div>
                      )}
                      
                      <div className={`flex items-center gap-2 ${isRTL ? 'flex-row-reverse' : ''}`}>
                        <Award className="w-4 h-4 text-slate-400" />
                        <span className={`px-2 py-0.5 text-xs font-medium rounded ${getLevelColor(auditor.certification_level)}`}>
                          {t(auditor.certification_level)}
                        </span>
                      </div>
                    </div>
                    
                    {/* Specializations */}
                    {auditor.specializations?.length > 0 && (
                      <div className={`flex flex-wrap gap-1 mt-3 ${isRTL ? 'justify-end' : ''}`}>
                        {auditor.specializations.slice(0, 3).map((spec) => (
                          <span key={spec} className="px-2 py-0.5 bg-slate-100 text-slate-600 text-xs rounded">
                            {spec}
                          </span>
                        ))}
                        {auditor.specializations.length > 3 && (
                          <span className="px-2 py-0.5 bg-slate-100 text-slate-600 text-xs rounded">
                            +{auditor.specializations.length - 3}
                          </span>
                        )}
                      </div>
                    )}
                    
                    {/* Stats */}
                    <div className={`flex items-center justify-between mt-4 pt-3 border-t text-xs ${isRTL ? 'flex-row-reverse' : ''}`}>
                      <span className="text-slate-500">
                        {t('assignments')}: <span className="font-semibold text-slate-700">{auditor.current_assignments || 0}</span>
                      </span>
                      <span className="text-slate-500">
                        {t('experience')}: <span className="font-semibold text-slate-700">{auditor.years_experience || 0} {t('years')}</span>
                      </span>
                    </div>
                    
                    {/* Actions */}
                    <div className={`flex items-center gap-2 mt-3 pt-3 border-t ${isRTL ? 'flex-row-reverse' : ''}`}>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => { setSelectedAuditor(auditor); setShowViewModal(true); }}
                        className="flex-1"
                      >
                        {t('view')}
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => openEditModal(auditor)}
                      >
                        <Edit className="w-4 h-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => { setSelectedAuditor(auditor); setShowAvailabilityModal(true); }}
                        title={t('setAvailability')}
                      >
                        <Calendar className="w-4 h-4" />
                      </Button>
                      {auditor.status === 'active' && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDeleteAuditor(auditor.id)}
                          className="text-red-600 hover:text-red-800"
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
          </div>
        </main>
      </div>

      {/* Create/Edit Auditor Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <Card className="w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <CardHeader>
              <div className={`flex items-center justify-between ${isRTL ? 'flex-row-reverse' : ''}`}>
                <CardTitle>{isEditing ? t('editAuditor') : t('addAuditor')}</CardTitle>
                <Button variant="ghost" size="sm" onClick={() => { setShowCreateModal(false); resetForm(); }}>
                  <X className="w-4 h-4" />
                </Button>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>{t('name')} *</Label>
                  <Input
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    placeholder={t('auditorName')}
                  />
                </div>
                <div className="space-y-2">
                  <Label>{t('nameArabic')}</Label>
                  <Input
                    value={formData.name_ar}
                    onChange={(e) => setFormData({ ...formData, name_ar: e.target.value })}
                    placeholder={t('auditorNameAr')}
                    dir="rtl"
                  />
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>{t('email')} *</Label>
                  <Input
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    placeholder={t('auditorEmail')}
                  />
                </div>
                <div className="space-y-2">
                  <Label>{t('employeeId')}</Label>
                  <Input
                    value={formData.employee_id}
                    onChange={(e) => setFormData({ ...formData, employee_id: e.target.value })}
                    placeholder={t('employeeIdPlaceholder')}
                  />
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>{t('phone')}</Label>
                  <Input
                    value={formData.phone}
                    onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                    placeholder={t('phoneNumber')}
                    dir="ltr"
                  />
                </div>
                <div className="space-y-2">
                  <Label>{t('mobile')}</Label>
                  <Input
                    value={formData.mobile}
                    onChange={(e) => setFormData({ ...formData, mobile: e.target.value })}
                    placeholder={t('mobileNumber')}
                    dir="ltr"
                  />
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>{t('certificationLevel')}</Label>
                  <Select value={formData.certification_level} onValueChange={(v) => setFormData({ ...formData, certification_level: v })}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {certificationLevels.map(level => (
                        <SelectItem key={level.value} value={level.value}>{level.label}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label>{t('yearsExperience')}</Label>
                  <Input
                    type="number"
                    value={formData.years_experience}
                    onChange={(e) => setFormData({ ...formData, years_experience: parseInt(e.target.value) || 0 })}
                    min={0}
                  />
                </div>
              </div>
              
              <div className="space-y-2">
                <Label>{t('specializations')}</Label>
                <div className={`flex flex-wrap gap-2 ${isRTL ? 'justify-end' : ''}`}>
                  {standardOptions.map(std => (
                    <Button
                      key={std}
                      type="button"
                      variant={formData.specializations.includes(std) ? 'default' : 'outline'}
                      size="sm"
                      onClick={() => toggleSpecialization(std)}
                      className={formData.specializations.includes(std) ? 'bg-bayan-primary' : ''}
                    >
                      {std}
                    </Button>
                  ))}
                </div>
              </div>
              
              <div className="space-y-2">
                <Label>{t('maxAuditsPerMonth')}</Label>
                <Input
                  type="number"
                  value={formData.max_audits_per_month}
                  onChange={(e) => setFormData({ ...formData, max_audits_per_month: parseInt(e.target.value) || 10 })}
                  min={1}
                  max={30}
                />
              </div>
              
              <div className="space-y-2">
                <Label>{t('notes')}</Label>
                <Textarea
                  value={formData.notes}
                  onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                  placeholder={t('auditorNotes')}
                />
              </div>
              
              <div className={`flex gap-2 pt-4 ${isRTL ? 'flex-row-reverse' : ''}`}>
                <Button onClick={handleCreateAuditor} className="flex-1 bg-bayan-primary hover:bg-bayan-primary/90">
                  {isEditing ? t('saveChanges') : t('addAuditor')}
                </Button>
                <Button variant="outline" onClick={() => { setShowCreateModal(false); resetForm(); }}>
                  {t('cancel')}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Set Availability Modal */}
      {showAvailabilityModal && selectedAuditor && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <Card className="w-full max-w-md">
            <CardHeader>
              <div className={`flex items-center justify-between ${isRTL ? 'flex-row-reverse' : ''}`}>
                <CardTitle>{t('setAvailability')}</CardTitle>
                <Button variant="ghost" size="sm" onClick={() => setShowAvailabilityModal(false)}>
                  <X className="w-4 h-4" />
                </Button>
              </div>
              <CardDescription>{selectedAuditor.name}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label>{t('date')} *</Label>
                <Input
                  type="date"
                  value={availabilityData.date}
                  onChange={(e) => setAvailabilityData({ ...availabilityData, date: e.target.value })}
                />
              </div>
              
              <div className="space-y-2">
                <Label>{t('availability')}</Label>
                <Select 
                  value={availabilityData.is_available ? 'available' : 'unavailable'}
                  onValueChange={(v) => setAvailabilityData({ ...availabilityData, is_available: v === 'available' })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="available">{t('available')}</SelectItem>
                    <SelectItem value="unavailable">{t('unavailable')}</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              {!availabilityData.is_available && (
                <div className="space-y-2">
                  <Label>{t('reason')}</Label>
                  <Select 
                    value={availabilityData.reason}
                    onValueChange={(v) => setAvailabilityData({ ...availabilityData, reason: v })}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder={t('selectReason')} />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="vacation">{t('vacation')}</SelectItem>
                      <SelectItem value="sick">{t('sickLeave')}</SelectItem>
                      <SelectItem value="training">{t('training')}</SelectItem>
                      <SelectItem value="other">{t('other')}</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              )}
              
              <div className={`flex gap-2 pt-4 ${isRTL ? 'flex-row-reverse' : ''}`}>
                <Button onClick={handleSetAvailability} className="flex-1 bg-bayan-primary hover:bg-bayan-primary/90">
                  {t('save')}
                </Button>
                <Button variant="outline" onClick={() => setShowAvailabilityModal(false)}>
                  {t('cancel')}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
};

export default AuditorsPage;
