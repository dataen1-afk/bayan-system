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
import { Badge } from '@/components/ui/badge';
import { 
  ArrowLeft, Plus, Award, Download, Eye, QrCode, CheckCircle, AlertCircle,
  XCircle, Clock, Search, Filter, Building2, Calendar, FileText, LogOut
} from 'lucide-react';
import Sidebar from '@/components/Sidebar';
import LanguageSwitcher from '@/components/LanguageSwitcher';
import NotificationBell from '@/components/NotificationBell';
import { AuthContext } from '@/App';

const API = process.env.REACT_APP_BACKEND_URL + '/api';

const CertificatesPage = () => {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const { user, logout } = useContext(AuthContext);
  const isRTL = i18n.language?.startsWith('ar');
  
  const [certificates, setCertificates] = useState([]);
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showViewModal, setShowViewModal] = useState(false);
  const [selectedCert, setSelectedCert] = useState(null);
  const [contracts, setContracts] = useState([]);
  
  const [formData, setFormData] = useState({
    contract_id: '',
    standards: [],
    scope: '',
    scope_ar: '',
    lead_auditor: '',
    audit_team: []
  });
  
  const token = localStorage.getItem('token');
  const headers = { Authorization: `Bearer ${token}` };
  
  useEffect(() => {
    fetchCertificates();
    fetchStats();
    fetchContracts();
  }, []);
  
  const fetchCertificates = async () => {
    try {
      const response = await axios.get(`${API}/certificates`, { headers });
      setCertificates(response.data);
    } catch (error) {
      console.error('Error fetching certificates:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API}/certificates/stats`, { headers });
      setStats(response.data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };
  
  const fetchContracts = async () => {
    try {
      const response = await axios.get(`${API}/certification-agreements`, { headers });
      // Include all agreements that are submitted or have contracts generated
      setContracts(response.data.filter(c => c.status === 'signed' || c.status === 'submitted' || c.status === 'contract_generated'));
    } catch (error) {
      console.error('Error fetching contracts:', error);
    }
  };
  
  const handleCreateCertificate = async () => {
    if (!formData.contract_id) {
      alert(t('selectContract'));
      return;
    }
    
    try {
      const response = await axios.post(`${API}/certificates`, formData, { headers });
      alert(`${t('certificateCreated')}: ${response.data.certificate_number}`);
      setShowCreateModal(false);
      fetchCertificates();
      fetchStats();
      setFormData({
        contract_id: '',
        standards: [],
        scope: '',
        scope_ar: '',
        lead_auditor: '',
        audit_team: []
      });
    } catch (error) {
      alert(error.response?.data?.detail || t('errorCreatingCertificate'));
    }
  };
  
  const handleUpdateStatus = async (certId, newStatus) => {
    if (!window.confirm(t('confirmStatusChange'))) return;
    
    try {
      await axios.put(`${API}/certificates/${certId}/status`, { status: newStatus }, { headers });
      fetchCertificates();
      fetchStats();
    } catch (error) {
      alert(error.response?.data?.detail || t('errorUpdatingStatus'));
    }
  };
  
  const handleDownloadPDF = async (certId, certNumber) => {
    try {
      const response = await axios.get(`${API}/certificates/${certId}/pdf`, {
        headers,
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `certificate_${certNumber}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      alert(t('errorDownloadingCertificate'));
    }
  };
  
  const getStatusBadge = (status) => {
    const statusConfig = {
      active: { color: 'bg-green-100 text-green-800', icon: CheckCircle, label: t('active') },
      suspended: { color: 'bg-yellow-100 text-yellow-800', icon: AlertCircle, label: t('suspended') },
      withdrawn: { color: 'bg-red-100 text-red-800', icon: XCircle, label: t('withdrawn') },
      expired: { color: 'bg-gray-100 text-gray-800', icon: Clock, label: t('expired') }
    };
    
    const config = statusConfig[status] || statusConfig.active;
    const Icon = config.icon;
    
    return (
      <Badge className={`${config.color} flex items-center gap-1`}>
        <Icon className="w-3 h-3" />
        {config.label}
      </Badge>
    );
  };
  
  const filteredCertificates = certificates.filter(cert => {
    const matchesStatus = statusFilter === 'all' || cert.status === statusFilter;
    const matchesSearch = !searchQuery || 
      cert.certificate_number?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      cert.organization_name?.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesStatus && matchesSearch;
  });
  
  const standardOptions = ['ISO 9001', 'ISO 14001', 'ISO 45001', 'ISO 22000', 'ISO 27001', 'ISO 50001'];
  
  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-gray-50 to-blue-50 flex items-center justify-center">
        <div className="text-xl">{t('loading')}...</div>
      </div>
    );
  }
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-gray-50 to-blue-50" dir={isRTL ? 'rtl' : 'ltr'}>
      {/* Fixed Header */}
      <header className="fixed top-0 left-0 right-0 z-40 bg-white shadow-md">
        <div className="max-w-full mx-auto px-4 py-3 sm:px-6 lg:px-8 flex justify-between items-center">
          <div className={`flex gap-3 items-center ${isRTL ? 'order-first' : 'order-last'}`}>
            <NotificationBell />
            <LanguageSwitcher />
            <Button variant="outline" onClick={logout} className="bg-bayan-navy text-white hover:bg-bayan-navy-light border-bayan-navy font-semibold">
              <LogOut className="w-4 h-4" />
              {t('logout')}
            </Button>
          </div>
          <div className={isRTL ? 'order-last' : 'order-first'}>
            <div className="-my-2">
              <img src="/bayan-logo.png" alt="Bayan" className="h-20 w-auto object-contain" />
            </div>
          </div>
        </div>
        <div className="h-1.5 bg-gradient-to-r from-bayan-navy via-bayan-navy-light to-bayan-navy"></div>
      </header>

      {/* Layout with Sidebar */}
      <div className="flex pt-[102px]">
        <Sidebar 
          activeTab="certificates" 
          onTabChange={(tab) => {
            if (tab === 'forms' || tab === 'quotations' || tab === 'contracts' || tab === 'templates' || tab === 'reports') {
              navigate(`/dashboard?tab=${tab}`);
            }
          }}
          userRole="admin"
          userName={user?.name}
          dashboardTitle={t('adminDashboard')}
        />
        
        {/* Main Content */}
        <main className="flex-1 p-4 lg:p-6 min-h-screen">
          <div className="w-full">
            {/* Header */}
            <div className={`flex items-center justify-between mb-6 ${isRTL ? 'flex-row-reverse' : ''}`}>
              <div className={`flex items-center gap-4 ${isRTL ? 'flex-row-reverse' : ''}`}>
                <Button variant="ghost" onClick={() => navigate('/dashboard')} className={`${isRTL ? 'flex-row-reverse' : ''}`}>
                  <ArrowLeft className={`w-4 h-4 ${isRTL ? 'rotate-180 ml-2' : 'mr-2'}`} />
                  {t('backToDashboard')}
                </Button>
                <div>
                  <h1 className={`text-2xl font-bold text-slate-900 flex items-center gap-2 ${isRTL ? 'flex-row-reverse' : ''}`}>
                    <Award className="w-7 h-7 text-bayan-navy" />
                    {t('certificates')}
                  </h1>
                </div>
              </div>
              
              <Button onClick={() => setShowCreateModal(true)} className="bg-bayan-primary hover:bg-bayan-primary/90" data-testid="create-certificate-btn">
                <Plus className={`w-4 h-4 ${isRTL ? 'ml-2' : 'mr-2'}`} />
                {t('issueCertificate')}
              </Button>
            </div>
            
            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
              <Card className="border-slate-200">
                <CardContent className="p-4">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-blue-100 rounded-lg">
                      <Award className="w-5 h-5 text-blue-600" />
                    </div>
                    <div>
                      <p className="text-2xl font-bold">{stats.total_certificates || 0}</p>
                      <p className="text-sm text-gray-500">{t('totalCertificates')}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
              
              <Card className="border-slate-200">
                <CardContent className="p-4">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-green-100 rounded-lg">
                      <CheckCircle className="w-5 h-5 text-green-600" />
                    </div>
                    <div>
                      <p className="text-2xl font-bold">{stats.active_count || 0}</p>
                      <p className="text-sm text-gray-500">{t('activeCertificates')}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
              
              <Card className="border-slate-200">
                <CardContent className="p-4">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-yellow-100 rounded-lg">
                      <AlertCircle className="w-5 h-5 text-yellow-600" />
                    </div>
                    <div>
                      <p className="text-2xl font-bold">{stats.expiring_soon_count || 0}</p>
                      <p className="text-sm text-gray-500">{t('expiringSoon')}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
              
              <Card className="border-slate-200">
                <CardContent className="p-4">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-orange-100 rounded-lg">
                      <Clock className="w-5 h-5 text-orange-600" />
                    </div>
                    <div>
                      <p className="text-2xl font-bold">{stats.suspended_count || 0}</p>
                      <p className="text-sm text-gray-500">{t('suspendedCertificates')}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
              
              <Card className="border-slate-200">
                <CardContent className="p-4">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-gray-100 rounded-lg">
                      <XCircle className="w-5 h-5 text-gray-600" />
                    </div>
                    <div>
                      <p className="text-2xl font-bold">{stats.expired_count || 0}</p>
                      <p className="text-sm text-gray-500">{t('expiredCertificates')}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
            
            {/* Filters */}
            <Card className="mb-6 border-slate-200">
              <CardContent className="p-4">
                <div className={`flex gap-4 items-center ${isRTL ? 'flex-row-reverse' : ''}`}>
                  <div className="relative flex-1 max-w-md">
                    <Search className={`absolute top-1/2 -translate-y-1/2 text-gray-400 w-4 h-4 ${isRTL ? 'right-3' : 'left-3'}`} />
                    <Input
                      placeholder={t('searchCertificates')}
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className={isRTL ? 'pr-10' : 'pl-10'}
                    />
                  </div>
                  
                  <Select value={statusFilter} onValueChange={setStatusFilter}>
                    <SelectTrigger className="w-[180px]">
                      <Filter className={`w-4 h-4 ${isRTL ? 'ml-2' : 'mr-2'}`} />
                      <SelectValue placeholder={t('allStatuses')} />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">{t('allStatuses')}</SelectItem>
                      <SelectItem value="active">{t('active')}</SelectItem>
                      <SelectItem value="suspended">{t('suspended')}</SelectItem>
                      <SelectItem value="expired">{t('expired')}</SelectItem>
                      <SelectItem value="withdrawn">{t('withdrawn')}</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </CardContent>
            </Card>
            
            {/* Certificates Grid */}
            {filteredCertificates.length === 0 ? (
              <Card className="border-slate-200">
                <CardContent className="p-8 text-center">
                  <Award className="w-16 h-16 mx-auto text-gray-300 mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">{t('noCertificates')}</h3>
                  <p className="text-gray-500">{t('issueCertificateToStart')}</p>
                </CardContent>
              </Card>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {filteredCertificates.map((cert) => (
                  <Card key={cert.id} className="border-slate-200 hover:shadow-md transition-shadow">
                    <CardContent className="p-4">
                      <div className={`flex justify-between items-start mb-3 ${isRTL ? 'flex-row-reverse' : ''}`}>
                        <div>
                          <p className="font-mono text-sm text-bayan-navy font-semibold">{cert.certificate_number}</p>
                          {getStatusBadge(cert.status)}
                        </div>
                        <QrCode className="w-8 h-8 text-gray-400" />
                      </div>
                      
                      <h3 className={`font-semibold text-lg mb-1 ${isRTL ? 'text-right' : ''}`}>{cert.organization_name}</h3>
                      {cert.organization_name_ar && (
                        <p className="text-gray-600 text-sm mb-2">{cert.organization_name_ar}</p>
                      )}
                      
                      <div className="flex flex-wrap gap-1 mb-3">
                        {cert.standards?.map((std, idx) => (
                          <Badge key={idx} variant="outline" className="text-xs">{std}</Badge>
                        ))}
                      </div>
                      
                      <div className="space-y-1 text-sm text-gray-600 mb-4">
                        <div className={`flex items-center gap-2 ${isRTL ? 'flex-row-reverse' : ''}`}>
                          <Calendar className="w-4 h-4" />
                          <span>{t('issued')}: {cert.issue_date}</span>
                        </div>
                        <div className={`flex items-center gap-2 ${isRTL ? 'flex-row-reverse' : ''}`}>
                          <Clock className="w-4 h-4" />
                          <span>{t('expires')}: {cert.expiry_date}</span>
                        </div>
                      </div>
                      
                      <div className={`flex gap-2 ${isRTL ? 'flex-row-reverse' : ''}`}>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => { setSelectedCert(cert); setShowViewModal(true); }}
                        >
                          <Eye className="w-4 h-4" />
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleDownloadPDF(cert.id, cert.certificate_number)}
                        >
                          <Download className="w-4 h-4" />
                        </Button>
                        {cert.status === 'active' && (
                          <Button
                            variant="outline"
                            size="sm"
                            className="text-yellow-600 hover:text-yellow-700"
                            onClick={() => handleUpdateStatus(cert.id, 'suspended')}
                          >
                            {t('suspend')}
                          </Button>
                        )}
                        {cert.status === 'suspended' && (
                          <Button
                            variant="outline"
                            size="sm"
                            className="text-green-600 hover:text-green-700"
                            onClick={() => handleUpdateStatus(cert.id, 'active')}
                          >
                            {t('reactivate')}
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

      {/* Create Certificate Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <Card className="w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <CardHeader>
              <CardTitle className={`flex items-center gap-2 ${isRTL ? 'flex-row-reverse' : ''}`}>
                <Award className="w-5 h-5" />
                {t('issueCertificate')}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label>{t('selectContract')} *</Label>
                <Select value={formData.contract_id} onValueChange={(v) => setFormData({...formData, contract_id: v})}>
                  <SelectTrigger>
                    <SelectValue placeholder={t('selectContract')} />
                  </SelectTrigger>
                  <SelectContent>
                    {contracts.map(c => (
                      <SelectItem key={c.id} value={c.id}>
                        {c.organizationName || c.organization_name || 'Unknown'} - {c.id.slice(0, 8)}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              
              <div>
                <Label>{t('standards')}</Label>
                <div className="flex flex-wrap gap-2 mt-2">
                  {standardOptions.map(std => (
                    <Button
                      key={std}
                      type="button"
                      variant={formData.standards.includes(std) ? 'default' : 'outline'}
                      size="sm"
                      onClick={() => {
                        const newStandards = formData.standards.includes(std)
                          ? formData.standards.filter(s => s !== std)
                          : [...formData.standards, std];
                        setFormData({...formData, standards: newStandards});
                      }}
                    >
                      {std}
                    </Button>
                  ))}
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>{t('scope')}</Label>
                  <Textarea
                    value={formData.scope}
                    onChange={(e) => setFormData({...formData, scope: e.target.value})}
                    placeholder={t('scopePlaceholder')}
                    rows={3}
                  />
                </div>
                <div>
                  <Label>{t('scopeArabic')}</Label>
                  <Textarea
                    value={formData.scope_ar}
                    onChange={(e) => setFormData({...formData, scope_ar: e.target.value})}
                    placeholder={t('scopeArabicPlaceholder')}
                    rows={3}
                    dir="rtl"
                  />
                </div>
              </div>
              
              <div>
                <Label>{t('leadAuditor')}</Label>
                <Input
                  value={formData.lead_auditor}
                  onChange={(e) => setFormData({...formData, lead_auditor: e.target.value})}
                  placeholder={t('leadAuditorName')}
                />
              </div>
              
              <div className={`flex gap-2 pt-4 ${isRTL ? 'flex-row-reverse' : ''}`}>
                <Button onClick={() => setShowCreateModal(false)} variant="outline">
                  {t('cancel')}
                </Button>
                <Button onClick={handleCreateCertificate} className="bg-bayan-primary hover:bg-bayan-primary/90">
                  {t('issueCertificate')}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* View Certificate Modal */}
      {showViewModal && selectedCert && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <Card className="w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <CardHeader>
              <div className={`flex justify-between items-start ${isRTL ? 'flex-row-reverse' : ''}`}>
                <div>
                  <CardTitle className="flex items-center gap-2">
                    <Award className="w-5 h-5 text-bayan-navy" />
                    {selectedCert.certificate_number}
                  </CardTitle>
                  <CardDescription>{selectedCert.organization_name}</CardDescription>
                </div>
                {getStatusBadge(selectedCert.status)}
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label className="text-gray-500">{t('organization')}</Label>
                  <p className="font-medium">{selectedCert.organization_name}</p>
                  {selectedCert.organization_name_ar && (
                    <p className="text-gray-600">{selectedCert.organization_name_ar}</p>
                  )}
                </div>
                <div>
                  <Label className="text-gray-500">{t('standards')}</Label>
                  <div className="flex flex-wrap gap-1">
                    {selectedCert.standards?.map((std, idx) => (
                      <Badge key={idx} variant="secondary">{std}</Badge>
                    ))}
                  </div>
                </div>
              </div>
              
              <div>
                <Label className="text-gray-500">{t('scope')}</Label>
                <p>{selectedCert.scope || '-'}</p>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label className="text-gray-500">{t('issueDate')}</Label>
                  <p className="font-medium">{selectedCert.issue_date}</p>
                </div>
                <div>
                  <Label className="text-gray-500">{t('expiryDate')}</Label>
                  <p className="font-medium">{selectedCert.expiry_date}</p>
                </div>
              </div>
              
              {selectedCert.lead_auditor && (
                <div>
                  <Label className="text-gray-500">{t('leadAuditor')}</Label>
                  <p className="font-medium">{selectedCert.lead_auditor}</p>
                </div>
              )}
              
              {selectedCert.qr_code_data && (
                <div className="text-center">
                  <Label className="text-gray-500">{t('verificationQR')}</Label>
                  <div className="mt-2">
                    <img 
                      src={`data:image/png;base64,${selectedCert.qr_code_data}`}
                      alt="QR Code"
                      className="mx-auto w-32 h-32"
                    />
                    <p className="text-xs text-gray-500 mt-1">{t('scanToVerify')}</p>
                  </div>
                </div>
              )}
              
              <div className={`flex gap-2 pt-4 ${isRTL ? 'flex-row-reverse' : ''}`}>
                <Button onClick={() => setShowViewModal(false)} variant="outline">
                  {t('close')}
                </Button>
                <Button onClick={() => handleDownloadPDF(selectedCert.id, selectedCert.certificate_number)}>
                  <Download className="w-4 h-4 mr-2" />
                  {t('downloadPDF')}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
};

export default CertificatesPage;
