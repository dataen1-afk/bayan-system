import React, { useState, useEffect, useContext } from 'react';
import axios from 'axios';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  ArrowLeft, BarChart3, TrendingUp, TrendingDown, FileText, DollarSign, 
  Award, Calendar, Users, CheckCircle, Clock, Target, LogOut, RefreshCw,
  ArrowUpRight, ArrowDownRight
} from 'lucide-react';
import Sidebar from '@/components/Sidebar';
import LanguageSwitcher from '@/components/LanguageSwitcher';
import NotificationBell from '@/components/NotificationBell';
import { AuthContext } from '@/App';

const API = process.env.REACT_APP_BACKEND_URL + '/api';

const AnalyticsDashboardPage = () => {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const { user, logout } = useContext(AuthContext);
  const isRTL = i18n.language?.startsWith('ar');
  
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  
  const token = localStorage.getItem('token');
  const headers = { Authorization: `Bearer ${token}` };
  
  useEffect(() => {
    fetchAnalytics();
  }, []);
  
  const fetchAnalytics = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/dashboard/analytics`, { headers });
      setAnalytics(response.data);
    } catch (error) {
      console.error('Error fetching analytics:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const formatCurrency = (amount) => {
    return new Intl.NumberFormat(isRTL ? 'ar-SA' : 'en-SA', {
      style: 'currency',
      currency: 'SAR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount || 0);
  };
  
  const ConversionFunnel = ({ rates }) => {
    const stages = [
      { label: t('formToProposal'), value: rates?.form_to_proposal || 0, color: 'bg-blue-500' },
      { label: t('proposalToContract'), value: rates?.proposal_to_contract || 0, color: 'bg-green-500' },
      { label: t('overallConversion'), value: rates?.overall || 0, color: 'bg-purple-500' }
    ];
    
    return (
      <div className="space-y-4">
        {stages.map((stage, idx) => (
          <div key={idx}>
            <div className={`flex justify-between items-center mb-1 ${isRTL ? 'flex-row-reverse' : ''}`}>
              <span className="text-sm font-medium">{stage.label}</span>
              <span className="text-sm font-bold">{stage.value}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div 
                className={`${stage.color} h-3 rounded-full transition-all duration-500`}
                style={{ width: `${Math.min(stage.value, 100)}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    );
  };
  
  const MonthlyChart = ({ data }) => {
    if (!data || data.length === 0) return null;
    
    const maxValue = Math.max(...data.map(d => Math.max(d.forms, d.proposals, d.contracts)));
    const chartHeight = 120;
    
    return (
      <div className="mt-4">
        <div className={`flex items-end gap-2 justify-between ${isRTL ? 'flex-row-reverse' : ''}`} style={{ height: chartHeight }}>
          {data.map((month, idx) => {
            const formsHeight = maxValue > 0 ? (month.forms / maxValue) * chartHeight : 0;
            const proposalsHeight = maxValue > 0 ? (month.proposals / maxValue) * chartHeight : 0;
            const contractsHeight = maxValue > 0 ? (month.contracts / maxValue) * chartHeight : 0;
            
            return (
              <div key={idx} className="flex-1 flex flex-col items-center gap-1">
                <div className="flex gap-0.5 items-end" style={{ height: chartHeight }}>
                  <div 
                    className="w-2 bg-blue-400 rounded-t transition-all duration-300"
                    style={{ height: `${formsHeight}px` }}
                    title={`${t('forms')}: ${month.forms}`}
                  />
                  <div 
                    className="w-2 bg-green-400 rounded-t transition-all duration-300"
                    style={{ height: `${proposalsHeight}px` }}
                    title={`${t('proposals')}: ${month.proposals}`}
                  />
                  <div 
                    className="w-2 bg-purple-400 rounded-t transition-all duration-300"
                    style={{ height: `${contractsHeight}px` }}
                    title={`${t('contracts')}: ${month.contracts}`}
                  />
                </div>
                <span className="text-xs text-gray-500">{month.month.split(' ')[0]}</span>
              </div>
            );
          })}
        </div>
        <div className={`flex gap-4 justify-center mt-4 ${isRTL ? 'flex-row-reverse' : ''}`}>
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 bg-blue-400 rounded" />
            <span className="text-xs">{t('forms')}</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 bg-green-400 rounded" />
            <span className="text-xs">{t('proposals')}</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 bg-purple-400 rounded" />
            <span className="text-xs">{t('contracts')}</span>
          </div>
        </div>
      </div>
    );
  };
  
  const StandardsBreakdown = ({ data }) => {
    if (!data || Object.keys(data).length === 0) {
      return <p className="text-gray-500 text-sm">{t('noData')}</p>;
    }
    
    const total = Object.values(data).reduce((a, b) => a + b, 0);
    const sortedData = Object.entries(data).sort((a, b) => b[1] - a[1]);
    
    const colors = ['bg-blue-500', 'bg-green-500', 'bg-purple-500', 'bg-yellow-500', 'bg-red-500', 'bg-pink-500'];
    
    return (
      <div className="space-y-3">
        {sortedData.map(([standard, count], idx) => {
          const percentage = total > 0 ? (count / total * 100).toFixed(1) : 0;
          return (
            <div key={standard}>
              <div className={`flex justify-between items-center mb-1 ${isRTL ? 'flex-row-reverse' : ''}`}>
                <span className="text-sm font-medium">{standard}</span>
                <span className="text-sm text-gray-500">{count} ({percentage}%)</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className={`${colors[idx % colors.length]} h-2 rounded-full transition-all duration-500`}
                  style={{ width: `${percentage}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>
    );
  };
  
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
          activeTab="analytics" 
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
                    <BarChart3 className="w-7 h-7 text-bayan-navy" />
                    {t('analyticsOverview')}
                  </h1>
                </div>
              </div>
              
              <Button variant="outline" onClick={fetchAnalytics}>
                <RefreshCw className="w-4 h-4" />
              </Button>
            </div>
            
            {/* Overview Stats */}
            <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
              <Card className="border-slate-200">
                <CardContent className="p-4">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-blue-100 rounded-lg">
                      <FileText className="w-5 h-5 text-blue-600" />
                    </div>
                    <div>
                      <p className="text-2xl font-bold">{analytics?.overview?.total_forms || 0}</p>
                      <p className="text-sm text-gray-500">{t('totalForms')}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
              
              <Card className="border-slate-200">
                <CardContent className="p-4">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-green-100 rounded-lg">
                      <DollarSign className="w-5 h-5 text-green-600" />
                    </div>
                    <div>
                      <p className="text-2xl font-bold">{analytics?.overview?.total_proposals || 0}</p>
                      <p className="text-sm text-gray-500">{t('totalProposals')}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
              
              <Card className="border-slate-200">
                <CardContent className="p-4">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-purple-100 rounded-lg">
                      <CheckCircle className="w-5 h-5 text-purple-600" />
                    </div>
                    <div>
                      <p className="text-2xl font-bold">{analytics?.overview?.total_contracts || 0}</p>
                      <p className="text-sm text-gray-500">{t('totalContracts')}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
              
              <Card className="border-slate-200">
                <CardContent className="p-4">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-yellow-100 rounded-lg">
                      <Award className="w-5 h-5 text-yellow-600" />
                    </div>
                    <div>
                      <p className="text-2xl font-bold">{analytics?.overview?.total_certificates || 0}</p>
                      <p className="text-sm text-gray-500">{t('totalCertificates')}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
              
              <Card className="border-slate-200">
                <CardContent className="p-4">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-emerald-100 rounded-lg">
                      <Award className="w-5 h-5 text-emerald-600" />
                    </div>
                    <div>
                      <p className="text-2xl font-bold">{analytics?.overview?.active_certificates || 0}</p>
                      <p className="text-sm text-gray-500">{t('activeCertificates')}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
            
            {/* Revenue & Conversion */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
              {/* Revenue Card */}
              <Card className="border-slate-200">
                <CardHeader>
                  <CardTitle className={`flex items-center gap-2 ${isRTL ? 'flex-row-reverse' : ''}`}>
                    <DollarSign className="w-5 h-5" />
                    {t('revenueOverview')}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="p-4 bg-blue-50 rounded-lg">
                      <p className="text-sm text-gray-600">{t('totalQuoted')}</p>
                      <p className="text-xl font-bold text-blue-600">
                        {formatCurrency(analytics?.revenue?.total_quoted)}
                      </p>
                    </div>
                    <div className="p-4 bg-green-50 rounded-lg">
                      <p className="text-sm text-gray-600">{t('totalAccepted')}</p>
                      <p className="text-xl font-bold text-green-600">
                        {formatCurrency(analytics?.revenue?.total_accepted)}
                      </p>
                    </div>
                    <div className="p-4 bg-purple-50 rounded-lg">
                      <p className="text-sm text-gray-600">{t('totalInvoiced')}</p>
                      <p className="text-xl font-bold text-purple-600">
                        {formatCurrency(analytics?.revenue?.total_invoiced)}
                      </p>
                    </div>
                    <div className="p-4 bg-emerald-50 rounded-lg">
                      <p className="text-sm text-gray-600">{t('totalCollected')}</p>
                      <p className="text-xl font-bold text-emerald-600">
                        {formatCurrency(analytics?.revenue?.total_collected)}
                      </p>
                    </div>
                  </div>
                  
                  <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                    <div className={`flex justify-between items-center ${isRTL ? 'flex-row-reverse' : ''}`}>
                      <span className="text-sm text-gray-600">{t('collectionRate')}</span>
                      <span className={`text-lg font-bold ${
                        (analytics?.revenue?.collection_rate || 0) >= 80 ? 'text-green-600' :
                        (analytics?.revenue?.collection_rate || 0) >= 50 ? 'text-yellow-600' : 'text-red-600'
                      }`}>
                        {analytics?.revenue?.collection_rate || 0}%
                      </span>
                    </div>
                  </div>
                </CardContent>
              </Card>
              
              {/* Conversion Funnel */}
              <Card className="border-slate-200">
                <CardHeader>
                  <CardTitle className={`flex items-center gap-2 ${isRTL ? 'flex-row-reverse' : ''}`}>
                    <Target className="w-5 h-5" />
                    {t('conversionFunnel')}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ConversionFunnel rates={analytics?.conversion_rates} />
                </CardContent>
              </Card>
            </div>
            
            {/* Monthly Trends & Standards */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
              {/* Monthly Trends */}
              <Card className="border-slate-200">
                <CardHeader>
                  <CardTitle className={`flex items-center gap-2 ${isRTL ? 'flex-row-reverse' : ''}`}>
                    <TrendingUp className="w-5 h-5" />
                    {t('monthlyTrends')}
                  </CardTitle>
                  <CardDescription>{t('last6Months')}</CardDescription>
                </CardHeader>
                <CardContent>
                  <MonthlyChart data={analytics?.monthly_trends} />
                </CardContent>
              </Card>
              
              {/* Standards Breakdown */}
              <Card className="border-slate-200">
                <CardHeader>
                  <CardTitle className={`flex items-center gap-2 ${isRTL ? 'flex-row-reverse' : ''}`}>
                    <Award className="w-5 h-5" />
                    {t('standardsBreakdown')}
                  </CardTitle>
                  <CardDescription>{t('certificationsByStandard')}</CardDescription>
                </CardHeader>
                <CardContent>
                  <StandardsBreakdown data={analytics?.standards_breakdown} />
                </CardContent>
              </Card>
            </div>
            
            {/* Audit Statistics */}
            <Card className="border-slate-200">
              <CardHeader>
                <CardTitle className={`flex items-center gap-2 ${isRTL ? 'flex-row-reverse' : ''}`}>
                  <Calendar className="w-5 h-5" />
                  {t('auditStatistics')}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="text-center p-4 bg-blue-50 rounded-lg">
                    <p className="text-3xl font-bold text-blue-600">{analytics?.audits?.total || 0}</p>
                    <p className="text-sm text-gray-600">{t('totalAudits')}</p>
                  </div>
                  <div className="text-center p-4 bg-green-50 rounded-lg">
                    <p className="text-3xl font-bold text-green-600">{analytics?.audits?.completed || 0}</p>
                    <p className="text-sm text-gray-600">{t('completedAudits')}</p>
                  </div>
                  <div className="text-center p-4 bg-yellow-50 rounded-lg">
                    <p className="text-3xl font-bold text-yellow-600">{analytics?.audits?.scheduled || 0}</p>
                    <p className="text-sm text-gray-600">{t('scheduledAudits')}</p>
                  </div>
                  <div className="text-center p-4 bg-gray-50 rounded-lg">
                    <p className="text-3xl font-bold text-gray-600">{analytics?.audits?.pending || 0}</p>
                    <p className="text-sm text-gray-600">{t('pendingAudits')}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </main>
      </div>
    </div>
  );
};

export default AnalyticsDashboardPage;
