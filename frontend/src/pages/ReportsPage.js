import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { 
  BarChart3, TrendingUp, FileText, DollarSign, CheckCircle, 
  XCircle, Clock, ArrowLeft, RefreshCw, Loader2 
} from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL + '/api';

const ReportsPage = () => {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const isRTL = i18n.language?.startsWith('ar');
  
  const [loading, setLoading] = useState(true);
  const [submissionStats, setSubmissionStats] = useState(null);
  const [revenueStats, setRevenueStats] = useState(null);

  useEffect(() => {
    loadAllStats();
  }, []);

  const loadAllStats = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const headers = { Authorization: `Bearer ${token}` };
      
      const [submissionRes, revenueRes] = await Promise.all([
        axios.get(`${API}/reports/submissions`, { headers }),
        axios.get(`${API}/reports/revenue`, { headers })
      ]);
      
      setSubmissionStats(submissionRes.data);
      setRevenueStats(revenueRes.data);
    } catch (error) {
      console.error('Error loading stats:', error);
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
              className={`${isRTL ? 'flex-row-reverse' : ''}`}
            >
              <ArrowLeft className={`w-4 h-4 ${isRTL ? 'ml-2 rotate-180' : 'mr-2'}`} />
              {t('backToDashboard')}
            </Button>
            <h1 className="text-2xl font-bold text-bayan-navy flex items-center gap-2">
              <BarChart3 className="w-6 h-6" />
              {t('reportsAnalytics')}
            </h1>
          </div>
          <Button variant="outline" onClick={loadAllStats}>
            <RefreshCw className="w-4 h-4 mr-2" />
            {t('refresh')}
          </Button>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {/* Total Forms */}
          <Card className="bg-white">
            <CardContent className="pt-6">
              <div className={`flex items-center justify-between ${isRTL ? 'flex-row-reverse' : ''}`}>
                <div className={isRTL ? 'text-right' : ''}>
                  <p className="text-sm text-gray-500">{t('totalForms')}</p>
                  <p className="text-3xl font-bold text-gray-800">{submissionStats?.total_forms || 0}</p>
                </div>
                <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                  <FileText className="w-6 h-6 text-blue-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Submitted Forms */}
          <Card className="bg-white">
            <CardContent className="pt-6">
              <div className={`flex items-center justify-between ${isRTL ? 'flex-row-reverse' : ''}`}>
                <div className={isRTL ? 'text-right' : ''}>
                  <p className="text-sm text-gray-500">{t('submittedForms')}</p>
                  <p className="text-3xl font-bold text-green-600">{submissionStats?.submitted_forms || 0}</p>
                </div>
                <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
                  <CheckCircle className="w-6 h-6 text-green-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Conversion Rate */}
          <Card className="bg-white">
            <CardContent className="pt-6">
              <div className={`flex items-center justify-between ${isRTL ? 'flex-row-reverse' : ''}`}>
                <div className={isRTL ? 'text-right' : ''}>
                  <p className="text-sm text-gray-500">{t('conversionRate')}</p>
                  <p className="text-3xl font-bold text-purple-600">{submissionStats?.conversion_rate || 0}%</p>
                </div>
                <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center">
                  <TrendingUp className="w-6 h-6 text-purple-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Total Contracts */}
          <Card className="bg-white">
            <CardContent className="pt-6">
              <div className={`flex items-center justify-between ${isRTL ? 'flex-row-reverse' : ''}`}>
                <div className={isRTL ? 'text-right' : ''}>
                  <p className="text-sm text-gray-500">{t('totalContracts')}</p>
                  <p className="text-3xl font-bold text-bayan-navy">{revenueStats?.total_contracts || 0}</p>
                </div>
                <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                  <DollarSign className="w-6 h-6 text-bayan-navy" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Revenue Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Revenue Overview */}
          <Card>
            <CardHeader className={isRTL ? 'text-right' : ''}>
              <CardTitle className="flex items-center gap-2">
                <DollarSign className="w-5 h-5 text-green-600" />
                {t('revenueOverview')}
              </CardTitle>
              <CardDescription>{t('revenueBreakdown')}</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {/* Total Quoted */}
                <div className={`flex justify-between items-center p-3 bg-gray-50 rounded-lg ${isRTL ? 'flex-row-reverse' : ''}`}>
                  <span className="text-gray-600">{t('totalQuoted')}</span>
                  <span className="font-semibold text-gray-800">{formatCurrency(revenueStats?.total_quoted)}</span>
                </div>
                
                {/* Accepted Revenue */}
                <div className={`flex justify-between items-center p-3 bg-green-50 rounded-lg ${isRTL ? 'flex-row-reverse' : ''}`}>
                  <span className="text-green-700 flex items-center gap-2">
                    <CheckCircle className="w-4 h-4" />
                    {t('acceptedRevenue')}
                  </span>
                  <span className="font-semibold text-green-700">{formatCurrency(revenueStats?.accepted_revenue)}</span>
                </div>
                
                {/* Pending Revenue */}
                <div className={`flex justify-between items-center p-3 bg-yellow-50 rounded-lg ${isRTL ? 'flex-row-reverse' : ''}`}>
                  <span className="text-yellow-700 flex items-center gap-2">
                    <Clock className="w-4 h-4" />
                    {t('pendingRevenue')}
                  </span>
                  <span className="font-semibold text-yellow-700">{formatCurrency(revenueStats?.pending_revenue)}</span>
                </div>
                
                {/* Rejected Revenue */}
                <div className={`flex justify-between items-center p-3 bg-red-50 rounded-lg ${isRTL ? 'flex-row-reverse' : ''}`}>
                  <span className="text-red-700 flex items-center gap-2">
                    <XCircle className="w-4 h-4" />
                    {t('rejectedRevenue')}
                  </span>
                  <span className="font-semibold text-red-700">{formatCurrency(revenueStats?.rejected_revenue)}</span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Proposal Stats */}
          <Card>
            <CardHeader className={isRTL ? 'text-right' : ''}>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="w-5 h-5 text-blue-600" />
                {t('proposalStatistics')}
              </CardTitle>
              <CardDescription>{t('proposalOverview')}</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {/* Total Proposals */}
                <div className={`flex justify-between items-center ${isRTL ? 'flex-row-reverse' : ''}`}>
                  <span className="text-gray-600">{t('totalProposals')}</span>
                  <span className="font-semibold text-gray-800">{submissionStats?.total_proposals || 0}</span>
                </div>
                
                {/* Accepted */}
                <div className={`flex justify-between items-center ${isRTL ? 'flex-row-reverse' : ''}`}>
                  <span className="text-green-600">{t('accepted')}</span>
                  <span className="font-semibold text-green-600">{submissionStats?.accepted_proposals || 0}</span>
                </div>
                
                {/* Pending Forms */}
                <div className={`flex justify-between items-center ${isRTL ? 'flex-row-reverse' : ''}`}>
                  <span className="text-yellow-600">{t('pendingForms')}</span>
                  <span className="font-semibold text-yellow-600">{submissionStats?.pending_forms || 0}</span>
                </div>

                {/* Conversion Progress */}
                <div className="mt-4 pt-4 border-t">
                  <div className={`flex justify-between items-center mb-2 ${isRTL ? 'flex-row-reverse' : ''}`}>
                    <span className="text-sm text-gray-500">{t('conversionProgress')}</span>
                    <span className="text-sm font-medium">{submissionStats?.conversion_rate || 0}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-green-500 h-2 rounded-full transition-all"
                      style={{ width: `${submissionStats?.conversion_rate || 0}%` }}
                    />
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Monthly Stats */}
        <Card>
          <CardHeader className={isRTL ? 'text-right' : ''}>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-blue-600" />
              {t('monthlySubmissions')}
            </CardTitle>
            <CardDescription>{t('lastSixMonths')}</CardDescription>
          </CardHeader>
          <CardContent>
            <div className={`flex items-end gap-4 h-48 ${isRTL ? 'flex-row-reverse' : ''}`}>
              {submissionStats?.monthly_stats?.map((stat, index) => {
                const maxCount = Math.max(...submissionStats.monthly_stats.map(s => s.count), 1);
                const height = (stat.count / maxCount) * 100;
                
                return (
                  <div key={index} className="flex-1 flex flex-col items-center">
                    <div className="w-full flex flex-col items-center justify-end h-40">
                      <span className="text-sm font-medium text-gray-600 mb-1">{stat.count}</span>
                      <div 
                        className="w-full bg-blue-500 rounded-t transition-all hover:bg-blue-600"
                        style={{ height: `${Math.max(height, 5)}%` }}
                      />
                    </div>
                    <span className="text-xs text-gray-500 mt-2">{stat.month}</span>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default ReportsPage;
