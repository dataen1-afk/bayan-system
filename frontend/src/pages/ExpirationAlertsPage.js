import React, { useState, useEffect, useContext } from 'react';
import axios from 'axios';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { 
  ArrowLeft, Bell, AlertTriangle, AlertCircle, Info, Award, Calendar,
  Clock, Building2, ChevronRight, RefreshCw
} from 'lucide-react';
import { AuthContext } from '@/App';

const API = process.env.REACT_APP_BACKEND_URL + '/api';

const ExpirationAlertsPage = () => {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const { user, logout } = useContext(AuthContext);
  const isRTL = i18n.language?.startsWith('ar');
  
  const [alerts, setAlerts] = useState({ critical: [], warning: [], info: [] });
  const [summary, setSummary] = useState({});
  const [loading, setLoading] = useState(true);
  const [daysFilter, setDaysFilter] = useState('90');
  
  const token = localStorage.getItem('token');
  const headers = { Authorization: `Bearer ${token}` };
  
  useEffect(() => {
    fetchAlerts();
  }, [daysFilter]);
  
  const fetchAlerts = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/alerts/expiring?days=${daysFilter}`, { headers });
      setAlerts(response.data.alerts);
      setSummary(response.data.summary);
    } catch (error) {
      console.error('Error fetching alerts:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const getAlertIcon = (type) => {
    switch (type) {
      case 'critical': return <AlertTriangle className="w-5 h-5 text-red-500" />;
      case 'warning': return <AlertCircle className="w-5 h-5 text-yellow-500" />;
      default: return <Info className="w-5 h-5 text-blue-500" />;
    }
  };
  
  const getAlertColor = (type) => {
    switch (type) {
      case 'critical': return 'border-l-4 border-l-red-500 bg-red-50';
      case 'warning': return 'border-l-4 border-l-yellow-500 bg-yellow-50';
      default: return 'border-l-4 border-l-blue-500 bg-blue-50';
    }
  };
  
  const getTypeIcon = (itemType) => {
    switch (itemType) {
      case 'certificate': return <Award className="w-4 h-4" />;
      case 'audit': return <Calendar className="w-4 h-4" />;
      default: return <Clock className="w-4 h-4" />;
    }
  };
  
  const handleNavigate = (item) => {
    if (item.type === 'certificate') {
      navigate('/certificates');
    } else if (item.type === 'audit') {
      navigate('/audit-scheduling');
    }
  };
  
  const AlertSection = ({ title, type, items }) => {
    if (items.length === 0) return null;
    
    return (
      <div className="mb-6">
        <h3 className={`text-lg font-semibold mb-3 flex items-center gap-2 ${isRTL ? 'flex-row-reverse' : ''}`}>
          {getAlertIcon(type)}
          {title} ({items.length})
        </h3>
        <div className="space-y-3">
          {items.map((item, idx) => (
            <Card 
              key={idx} 
              className={`${getAlertColor(type)} cursor-pointer hover:shadow-md transition-shadow`}
              onClick={() => handleNavigate(item)}
            >
              <CardContent className="p-4">
                <div className={`flex items-center justify-between ${isRTL ? 'flex-row-reverse' : ''}`}>
                  <div className={`flex items-center gap-3 ${isRTL ? 'flex-row-reverse' : ''}`}>
                    <div className="p-2 bg-white rounded-lg shadow-sm">
                      {getTypeIcon(item.type)}
                    </div>
                    <div>
                      <p className="font-medium">{item.organization || item.reference}</p>
                      <div className={`flex items-center gap-2 text-sm text-gray-600 ${isRTL ? 'flex-row-reverse' : ''}`}>
                        <Badge variant="outline" className="text-xs">
                          {item.type === 'certificate' ? t('certificate') : t('audit')}
                        </Badge>
                        {item.standards && item.standards.length > 0 && (
                          <span>{item.standards.join(', ')}</span>
                        )}
                        {item.audit_type && (
                          <span>{item.audit_type}</span>
                        )}
                      </div>
                    </div>
                  </div>
                  
                  <div className={`flex items-center gap-4 ${isRTL ? 'flex-row-reverse' : ''}`}>
                    <div className={`text-${isRTL ? 'left' : 'right'}`}>
                      <p className={`text-sm font-medium ${
                        type === 'critical' ? 'text-red-600' : 
                        type === 'warning' ? 'text-yellow-600' : 'text-blue-600'
                      }`}>
                        {item.days_until_expiry} {t('daysRemaining')}
                      </p>
                      <p className="text-xs text-gray-500">{item.expiry_date}</p>
                    </div>
                    <ChevronRight className={`w-5 h-5 text-gray-400 ${isRTL ? 'rotate-180' : ''}`} />
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  };
  
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
              <Bell className="w-7 h-7 text-bayan-navy" />
              {t('expirationAlerts')}
            </h1>
          </div>
        </div>
        
        <div className={`flex items-center gap-2 ${isRTL ? 'flex-row-reverse' : ''}`}>
          <Select value={daysFilter} onValueChange={setDaysFilter}>
            <SelectTrigger className="w-[180px]">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="30">{t('next30Days')}</SelectItem>
              <SelectItem value="60">{t('next60Days')}</SelectItem>
              <SelectItem value="90">{t('next90Days')}</SelectItem>
              <SelectItem value="180">{t('next180Days')}</SelectItem>
            </SelectContent>
          </Select>
          <Button variant="outline" onClick={fetchAlerts}>
            <RefreshCw className="w-4 h-4" />
          </Button>
        </div>
      </div>
      
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
              <Card className="border-slate-200">
                <CardContent className="p-4">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-blue-100 rounded-lg">
                      <Bell className="w-5 h-5 text-blue-600" />
                    </div>
                    <div>
                      <p className="text-2xl font-bold">{summary.total_alerts || 0}</p>
                      <p className="text-sm text-gray-500">{t('totalAlerts')}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
              
              <Card className="border-slate-200 border-l-4 border-l-red-500">
                <CardContent className="p-4">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-red-100 rounded-lg">
                      <AlertTriangle className="w-5 h-5 text-red-600" />
                    </div>
                    <div>
                      <p className="text-2xl font-bold text-red-600">{summary.critical_count || 0}</p>
                      <p className="text-sm text-gray-500">{t('criticalAlerts')}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
              
              <Card className="border-slate-200 border-l-4 border-l-yellow-500">
                <CardContent className="p-4">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-yellow-100 rounded-lg">
                      <AlertCircle className="w-5 h-5 text-yellow-600" />
                    </div>
                    <div>
                      <p className="text-2xl font-bold text-yellow-600">{summary.warning_count || 0}</p>
                      <p className="text-sm text-gray-500">{t('warningAlerts')}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
              
              <Card className="border-slate-200 border-l-4 border-l-blue-500">
                <CardContent className="p-4">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-blue-100 rounded-lg">
                      <Info className="w-5 h-5 text-blue-600" />
                    </div>
                    <div>
                      <p className="text-2xl font-bold text-blue-600">{summary.info_count || 0}</p>
                      <p className="text-sm text-gray-500">{t('infoAlerts')}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
            
            {/* Alert Lists */}
            {summary.total_alerts === 0 ? (
              <Card className="border-slate-200">
                <CardContent className="p-8 text-center">
                  <Bell className="w-16 h-16 mx-auto text-gray-300 mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">{t('noAlerts')}</h3>
                  <p className="text-gray-500">{t('allItemsUpToDate')}</p>
                </CardContent>
              </Card>
            ) : (
              <>
                <AlertSection 
                  title={t('criticalAlerts')} 
                  type="critical" 
                  items={alerts.critical} 
                />
                <AlertSection 
                  title={t('warningAlerts')} 
                  type="warning" 
                  items={alerts.warning} 
                />
                <AlertSection 
                  title={t('infoAlerts')} 
                  type="info" 
                  items={alerts.info} 
                />
              </>
            )}
    </div>
  );
};

export default ExpirationAlertsPage;
