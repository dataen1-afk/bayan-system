import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { API } from '@/lib/apiConfig';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { 
  AlertTriangle, 
  Clock, 
  Award, 
  FileText, 
  DollarSign, 
  Users, 
  Plus, 
  Eye, 
  CheckCircle,
  Calendar,
  TrendingUp,
  Activity,
  ArrowRight
} from 'lucide-react';

// Format currency with SAR
const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-US', { 
    minimumFractionDigits: 0,
    maximumFractionDigits: 0 
  }).format(amount || 0) + ' SAR';
};

// Format date
const formatDate = (dateString) => {
  if (!dateString) return '';
  return new Date(dateString).toLocaleDateString('en-GB', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  });
};

const DashboardWidgets = ({ isRTL }) => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState(null);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    setLoadError(null);
    setLoading(true);
    try {
      const response = await axios.get(`${API}/dashboard/stats`, { timeout: 60000 });
      setStats(response.data);
    } catch (error) {
      console.error('Error loading dashboard stats:', error);
      const detail = error.response?.data?.detail;
      const message =
        typeof detail === 'string'
          ? detail
          : error.code === 'ECONNABORTED'
            ? (isRTL ? 'انتهت مهلة التحميل. حاول مرة أخرى.' : 'Request timed out. Please try again.')
            : (isRTL ? 'تعذر تحميل بيانات لوحة التحكم.' : 'Could not load dashboard data.');
      setLoadError(message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 animate-pulse">
        {[1, 2, 3, 4, 5, 6].map(i => (
          <div key={i} className="h-48 bg-slate-100 rounded-xl"></div>
        ))}
      </div>
    );
  }

  if (!stats) {
    return (
      <Card className="border-amber-200 bg-amber-50/80" dir={isRTL ? 'rtl' : 'ltr'}>
        <CardHeader>
          <CardTitle className="text-amber-900 text-base">
            {isRTL ? 'تعذر عرض الإحصائيات' : 'Dashboard unavailable'}
          </CardTitle>
          <CardDescription className="text-amber-800">
            {loadError ||
              (isRTL ? 'لم يتم استلام بيانات من الخادم.' : 'No data was returned from the server.')}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Button variant="outline" className="border-amber-300" onClick={() => loadStats()}>
            {isRTL ? 'إعادة المحاولة' : 'Retry'}
          </Button>
        </CardContent>
      </Card>
    );
  }

  const totalExpiring = (stats.certificates?.expiring_count?.['30_days'] || 0) +
                        (stats.certificates?.expiring_count?.['60_days'] || 0) +
                        (stats.certificates?.expiring_count?.['90_days'] || 0);

  const revenueProgress = stats.revenue?.monthly_target > 0 
    ? Math.min((stats.revenue?.monthly / stats.revenue?.monthly_target) * 100, 100) 
    : 0;

  return (
    <div className="space-y-6">
      {/* Top Row - Key Metrics (4 columns) */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        
        {/* Quick Actions Widget */}
        <Card className="border-blue-200 bg-gradient-to-br from-blue-50 to-white hover:shadow-lg transition-all" data-testid="quick-actions-widget" dir={isRTL ? 'rtl' : 'ltr'}>
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm font-medium text-blue-800">
                {isRTL ? 'إجراءات سريعة' : 'Quick Actions'}
              </CardTitle>
              <div className="p-2 bg-blue-100 rounded-lg">
                <Plus className="w-4 h-4 text-blue-600" />
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <Button 
                variant="outline" 
                size="sm" 
                className="w-full justify-between border-blue-200 hover:bg-blue-50"
                onClick={() => navigate('/admin?tab=forms')}
              >
                <span className="flex items-center gap-2">
                  <FileText className="w-4 h-4" />
                  {isRTL ? 'طلبات المنح' : 'Grant Requests'}
                </span>
                {stats.approvals?.pending > 0 && (
                  <span className="bg-amber-100 text-amber-700 text-xs px-2 py-0.5 rounded-full">
                    {stats.approvals.pending}
                  </span>
                )}
              </Button>
              <Button 
                variant="outline" 
                size="sm" 
                className="w-full justify-between border-blue-200 hover:bg-blue-50"
                onClick={() => navigate('/audit-programs')}
              >
                <span className="flex items-center gap-2">
                  <Calendar className="w-4 h-4" />
                  {isRTL ? 'برامج التدقيق' : 'Audit Programs'}
                </span>
              </Button>
              <Button 
                variant="outline" 
                size="sm" 
                className="w-full justify-between border-blue-200 hover:bg-blue-50"
                onClick={() => navigate('/certificates')}
              >
                <span className="flex items-center gap-2">
                  <Award className="w-4 h-4" />
                  {isRTL ? 'الشهادات' : 'Certificates'}
                </span>
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Revenue Target Progress */}
        <Card className="border-emerald-200 bg-gradient-to-br from-emerald-50 to-white hover:shadow-lg transition-all" data-testid="revenue-widget" dir={isRTL ? 'rtl' : 'ltr'}>
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm font-medium text-emerald-800">
                {isRTL ? 'الإيرادات الشهرية' : 'Monthly Revenue'}
              </CardTitle>
              <div className="p-2 bg-emerald-100 rounded-lg">
                <TrendingUp className="w-4 h-4 text-emerald-600" />
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div>
                <div className="flex items-baseline gap-2">
                  <span className="text-2xl font-bold text-emerald-700">
                    {formatCurrency(stats.revenue?.monthly)}
                  </span>
                </div>
                <p className="text-xs text-slate-500 mt-1">
                  {isRTL ? 'الهدف: ' : 'Target: '}{formatCurrency(stats.revenue?.monthly_target)}
                </p>
              </div>
              <div>
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-slate-600">{isRTL ? 'التقدم' : 'Progress'}</span>
                  <span className="font-semibold text-emerald-700">{Math.round(revenueProgress)}%</span>
                </div>
                <Progress value={revenueProgress} className="h-2 bg-emerald-100" />
              </div>
              <div className="flex justify-between text-sm pt-2 border-t border-emerald-100">
                <span className="text-slate-600">{isRTL ? 'الإجمالي' : 'Total Revenue'}</span>
                <span className="font-bold text-emerald-700">{formatCurrency(stats.revenue?.total)}</span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Active Certificates */}
        <Card className="border-green-200 bg-gradient-to-br from-green-50 to-white hover:shadow-lg transition-all" data-testid="active-certs-widget" dir={isRTL ? 'rtl' : 'ltr'}>
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm font-medium text-green-800">
                {isRTL ? 'الشهادات النشطة' : 'Active Certificates'}
              </CardTitle>
              <div className="p-2 bg-green-100 rounded-lg">
                <Award className="w-4 h-4 text-green-600" />
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="text-3xl font-bold text-green-700">
                {stats.certificates?.active || 0}
              </div>
              <p className="text-sm text-slate-600">
                {isRTL ? 'شهادة سارية المفعول' : 'Active certifications'}
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Total Clients */}
        <Card className="border-indigo-200 bg-gradient-to-br from-indigo-50 to-white hover:shadow-lg transition-all" data-testid="clients-widget" dir={isRTL ? 'rtl' : 'ltr'}>
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm font-medium text-indigo-800">
                {isRTL ? 'إجمالي العملاء' : 'Total Clients'}
              </CardTitle>
              <div className="p-2 bg-indigo-100 rounded-lg">
                <Users className="w-4 h-4 text-indigo-600" />
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="text-3xl font-bold text-indigo-700">
                {stats.clients?.total || 0}
              </div>
              <p className="text-sm text-slate-600">
                {isRTL ? 'عميل مسجل' : 'Registered clients'}
              </p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Second Row - Daily Activity (Right) & Certificates Expiring (Left) for RTL */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        
        {/* Daily Activity - On RIGHT for RTL (comes first in RTL grid) */}
        <Card className="border-purple-200 bg-gradient-to-br from-purple-50 to-white hover:shadow-lg transition-all" data-testid="daily-activity-widget" dir={isRTL ? 'rtl' : 'ltr'}>
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <CardTitle className="text-lg font-semibold text-purple-800">
                {isRTL ? 'نشاط اليوم' : "Today's Activity"}
              </CardTitle>
              <div className="p-2 bg-purple-100 rounded-lg">
                <Activity className="w-5 h-5 text-purple-600" />
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-3 bg-purple-50 rounded-lg">
                <span className="flex items-center gap-2 text-purple-700">
                  <FileText className="w-5 h-5" />
                  {isRTL ? 'طلبات جديدة' : 'New Requests'}
                </span>
                <span className="text-2xl font-bold text-purple-800">{stats.today_activity?.new_forms || 0}</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-purple-50 rounded-lg">
                <span className="flex items-center gap-2 text-purple-700">
                  <DollarSign className="w-5 h-5" />
                  {isRTL ? 'عروض أسعار' : 'Proposals'}
                </span>
                <span className="text-2xl font-bold text-purple-800">{stats.today_activity?.new_proposals || 0}</span>
              </div>
              {stats.today_activity?.notifications?.length > 0 && (
                <div className="pt-3 border-t border-purple-100">
                  <p className="text-sm text-purple-600 mb-2 font-medium">
                    {isRTL ? 'آخر الإشعارات' : 'Recent Notifications'}
                  </p>
                  <div className="space-y-2 max-h-32 overflow-y-auto">
                    {stats.today_activity.notifications.slice(0, 3).map((notif, idx) => (
                      <p key={idx} className="text-sm text-slate-600 p-2 bg-slate-50 rounded">
                        • {isRTL ? notif.title_ar || notif.title : notif.title}
                      </p>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Certificates Expiring Soon - On LEFT for RTL (comes second in RTL grid) */}
        <Card className="border-amber-200 bg-gradient-to-br from-amber-50 to-white hover:shadow-lg transition-all" data-testid="certs-expiring-widget" dir={isRTL ? 'rtl' : 'ltr'}>
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <CardTitle className="text-lg font-semibold text-amber-800">
                {isRTL ? 'الشهادات المنتهية قريباً' : 'Certificates Expiring Soon'}
              </CardTitle>
              <div className="p-2 bg-amber-100 rounded-lg">
                <AlertTriangle className="w-5 h-5 text-amber-600" />
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-3 bg-red-50 rounded-lg border border-red-200">
                <span className="flex items-center gap-2 text-red-700">
                  <AlertTriangle className="w-5 h-5" />
                  {isRTL ? 'خلال 30 يوم' : 'Within 30 days'}
                </span>
                <span className="text-2xl font-bold text-red-700">{stats.certificates?.expiring_count?.['30_days'] || 0}</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-amber-50 rounded-lg border border-amber-200">
                <span className="flex items-center gap-2 text-amber-700">
                  <Clock className="w-5 h-5" />
                  {isRTL ? 'خلال 60 يوم' : 'Within 60 days'}
                </span>
                <span className="text-2xl font-bold text-amber-700">{stats.certificates?.expiring_count?.['60_days'] || 0}</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-yellow-50 rounded-lg border border-yellow-200">
                <span className="flex items-center gap-2 text-yellow-700">
                  <Clock className="w-5 h-5" />
                  {isRTL ? 'خلال 90 يوم' : 'Within 90 days'}
                </span>
                <span className="text-2xl font-bold text-yellow-700">{stats.certificates?.expiring_count?.['90_days'] || 0}</span>
              </div>
              <div className="pt-3 border-t border-amber-200">
                <p className="text-sm text-amber-800 font-semibold">
                  {isRTL ? `إجمالي: ${totalExpiring} شهادة` : `Total: ${totalExpiring} certificates`}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Auditor Workload Chart */}
      <Card className="border-slate-200 hover:shadow-lg transition-all" dir={isRTL ? 'rtl' : 'ltr'} data-testid="auditor-workload-widget">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-lg font-semibold text-slate-800">
                {isRTL ? 'توزيع عبء العمل على المدققين' : 'Auditor Workload Distribution'}
              </CardTitle>
              <CardDescription>
                {isRTL ? 'عدد المهام المخصصة لكل مدقق' : 'Number of tasks assigned to each auditor'}
              </CardDescription>
            </div>
            <div className="p-2 bg-slate-100 rounded-lg">
              <Users className="w-5 h-5 text-slate-600" />
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {stats.auditor_workload?.length > 0 ? (
            <div className="space-y-3">
              {stats.auditor_workload.slice(0, 6).map((auditor, idx) => {
                const maxTasks = Math.max(...stats.auditor_workload.map(a => a.total_tasks), 1);
                const percentage = (auditor.total_tasks / maxTasks) * 100;
                const colors = [
                  'bg-blue-500', 'bg-emerald-500', 'bg-purple-500', 
                  'bg-amber-500', 'bg-rose-500', 'bg-cyan-500'
                ];
                
                return (
                  <div key={auditor.id || idx} className="space-y-1">
                    <div className="flex justify-between text-sm">
                      <span className="font-medium text-slate-700">
                        {isRTL ? auditor.name_ar || auditor.name : auditor.name}
                      </span>
                      <span className="text-slate-500">
                        {auditor.total_tasks} {isRTL ? 'مهمة' : 'tasks'}
                      </span>
                    </div>
                    <div className={`h-3 bg-slate-100 rounded-full overflow-hidden ${isRTL ? 'transform scale-x-[-1]' : ''}`}>
                      <div 
                        className={`h-full ${colors[idx % colors.length]} rounded-full transition-all`}
                        style={{ width: `${percentage}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="text-center py-8 text-slate-500">
              <Users className="w-12 h-12 mx-auto mb-2 opacity-30" />
              <p>{isRTL ? 'لا توجد بيانات متاحة' : 'No data available'}</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default DashboardWidgets;
