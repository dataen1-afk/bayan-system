import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { API } from '@/App';
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

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const response = await axios.get(`${API}/dashboard/stats`);
      setStats(response.data);
    } catch (error) {
      console.error('Error loading dashboard stats:', error);
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

  if (!stats) return null;

  const totalExpiring = (stats.certificates?.expiring_count?.['30_days'] || 0) +
                        (stats.certificates?.expiring_count?.['60_days'] || 0) +
                        (stats.certificates?.expiring_count?.['90_days'] || 0);

  const revenueProgress = stats.revenue?.monthly_target > 0 
    ? Math.min((stats.revenue?.monthly / stats.revenue?.monthly_target) * 100, 100) 
    : 0;

  return (
    <div className="space-y-6">
      {/* Top Row - Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        
        {/* Certificate Expiration Widget */}
        <Card className="border-amber-200 bg-gradient-to-br from-amber-50 to-white hover:shadow-lg transition-all" data-testid="cert-expiration-widget">
          <CardHeader className="pb-2">
            <div className={`flex items-center justify-between ${isRTL ? 'flex-row-reverse' : ''}`}>
              <CardTitle className="text-sm font-medium text-amber-800">
                {isRTL ? 'الشهادات المنتهية قريباً' : 'Expiring Certificates'}
              </CardTitle>
              <div className="p-2 bg-amber-100 rounded-lg">
                <AlertTriangle className="w-4 h-4 text-amber-600" />
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className={`flex items-baseline gap-2 ${isRTL ? 'flex-row-reverse' : ''}`}>
                <span className="text-3xl font-bold text-amber-700">{totalExpiring}</span>
                <span className="text-sm text-amber-600">{isRTL ? 'شهادة' : 'certificates'}</span>
              </div>
              <div className="space-y-1.5 text-sm">
                <div className={`flex justify-between items-center ${isRTL ? 'flex-row-reverse' : ''}`}>
                  <span className="text-red-600 font-medium">30 {isRTL ? 'يوم' : 'days'}</span>
                  <span className="font-bold text-red-700 bg-red-100 px-2 py-0.5 rounded">
                    {stats.certificates?.expiring_count?.['30_days'] || 0}
                  </span>
                </div>
                <div className={`flex justify-between items-center ${isRTL ? 'flex-row-reverse' : ''}`}>
                  <span className="text-amber-600">60 {isRTL ? 'يوم' : 'days'}</span>
                  <span className="font-semibold text-amber-700">
                    {stats.certificates?.expiring_count?.['60_days'] || 0}
                  </span>
                </div>
                <div className={`flex justify-between items-center ${isRTL ? 'flex-row-reverse' : ''}`}>
                  <span className="text-yellow-600">90 {isRTL ? 'يوم' : 'days'}</span>
                  <span className="font-semibold text-yellow-700">
                    {stats.certificates?.expiring_count?.['90_days'] || 0}
                  </span>
                </div>
              </div>
              <Button 
                variant="outline" 
                size="sm" 
                className="w-full mt-2 border-amber-300 text-amber-700 hover:bg-amber-50"
                onClick={() => navigate('/expiration-alerts')}
              >
                {isRTL ? 'عرض التفاصيل' : 'View Details'}
                <ArrowRight className={`w-4 h-4 ${isRTL ? 'mr-2 rotate-180' : 'ml-2'}`} />
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Quick Actions Card */}
        <Card className="border-blue-200 bg-gradient-to-br from-blue-50 to-white hover:shadow-lg transition-all" data-testid="quick-actions-widget">
          <CardHeader className="pb-2">
            <div className={`flex items-center justify-between ${isRTL ? 'flex-row-reverse' : ''}`}>
              <CardTitle className="text-sm font-medium text-blue-800">
                {isRTL ? 'إجراءات سريعة' : 'Quick Actions'}
              </CardTitle>
              <div className="p-2 bg-blue-100 rounded-lg">
                <Activity className="w-4 h-4 text-blue-600" />
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <Button 
                variant="outline" 
                size="sm" 
                className={`w-full justify-between border-blue-200 hover:bg-blue-50 ${isRTL ? 'flex-row-reverse' : ''}`}
                onClick={() => navigate('/dashboard?tab=forms')}
              >
                <span className={`flex items-center gap-2 ${isRTL ? 'flex-row-reverse' : ''}`}>
                  <Plus className="w-4 h-4" />
                  {isRTL ? 'إنشاء طلب' : 'Create Form'}
                </span>
                {stats.forms?.submitted > 0 && (
                  <span className="bg-blue-100 text-blue-700 text-xs px-2 py-0.5 rounded-full">
                    {stats.forms.submitted}
                  </span>
                )}
              </Button>
              <Button 
                variant="outline" 
                size="sm" 
                className={`w-full justify-between border-blue-200 hover:bg-blue-50 ${isRTL ? 'flex-row-reverse' : ''}`}
                onClick={() => navigate('/approvals')}
              >
                <span className={`flex items-center gap-2 ${isRTL ? 'flex-row-reverse' : ''}`}>
                  <CheckCircle className="w-4 h-4" />
                  {isRTL ? 'الموافقات المعلقة' : 'Pending Approvals'}
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
                className={`w-full justify-between border-blue-200 hover:bg-blue-50 ${isRTL ? 'flex-row-reverse' : ''}`}
                onClick={() => navigate('/audit-programs')}
              >
                <span className={`flex items-center gap-2 ${isRTL ? 'flex-row-reverse' : ''}`}>
                  <Calendar className="w-4 h-4" />
                  {isRTL ? 'برامج التدقيق' : 'Audit Programs'}
                </span>
              </Button>
              <Button 
                variant="outline" 
                size="sm" 
                className={`w-full justify-between border-blue-200 hover:bg-blue-50 ${isRTL ? 'flex-row-reverse' : ''}`}
                onClick={() => navigate('/certificates')}
              >
                <span className={`flex items-center gap-2 ${isRTL ? 'flex-row-reverse' : ''}`}>
                  <Award className="w-4 h-4" />
                  {isRTL ? 'الشهادات' : 'Certificates'}
                </span>
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Revenue Target Progress */}
        <Card className="border-emerald-200 bg-gradient-to-br from-emerald-50 to-white hover:shadow-lg transition-all" data-testid="revenue-widget">
          <CardHeader className="pb-2">
            <div className={`flex items-center justify-between ${isRTL ? 'flex-row-reverse' : ''}`}>
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
                <div className={`flex items-baseline gap-2 ${isRTL ? 'flex-row-reverse' : ''}`}>
                  <span className="text-2xl font-bold text-emerald-700">
                    {formatCurrency(stats.revenue?.monthly)}
                  </span>
                </div>
                <p className="text-xs text-slate-500 mt-1">
                  {isRTL ? 'الهدف: ' : 'Target: '}{formatCurrency(stats.revenue?.monthly_target)}
                </p>
              </div>
              <div>
                <div className={`flex justify-between text-xs mb-1 ${isRTL ? 'flex-row-reverse' : ''}`}>
                  <span className="text-slate-600">{isRTL ? 'التقدم' : 'Progress'}</span>
                  <span className="font-semibold text-emerald-700">{Math.round(revenueProgress)}%</span>
                </div>
                <Progress value={revenueProgress} className="h-2 bg-emerald-100" />
              </div>
              <div className={`flex justify-between text-sm pt-2 border-t border-emerald-100 ${isRTL ? 'flex-row-reverse' : ''}`}>
                <span className="text-slate-600">{isRTL ? 'الإجمالي' : 'Total Revenue'}</span>
                <span className="font-bold text-emerald-700">{formatCurrency(stats.revenue?.total)}</span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Today's Activity */}
        <Card className="border-purple-200 bg-gradient-to-br from-purple-50 to-white hover:shadow-lg transition-all" data-testid="activity-widget">
          <CardHeader className="pb-2">
            <div className={`flex items-center justify-between ${isRTL ? 'flex-row-reverse' : ''}`}>
              <CardTitle className="text-sm font-medium text-purple-800">
                {isRTL ? 'نشاط اليوم' : "Today's Activity"}
              </CardTitle>
              <div className="p-2 bg-purple-100 rounded-lg">
                <Clock className="w-4 h-4 text-purple-600" />
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className={`flex items-center justify-between p-2 bg-purple-50 rounded-lg ${isRTL ? 'flex-row-reverse' : ''}`}>
                <span className={`flex items-center gap-2 text-sm text-purple-700 ${isRTL ? 'flex-row-reverse' : ''}`}>
                  <FileText className="w-4 h-4" />
                  {isRTL ? 'طلبات جديدة' : 'New Forms'}
                </span>
                <span className="font-bold text-purple-800">{stats.today_activity?.new_forms || 0}</span>
              </div>
              <div className={`flex items-center justify-between p-2 bg-purple-50 rounded-lg ${isRTL ? 'flex-row-reverse' : ''}`}>
                <span className={`flex items-center gap-2 text-sm text-purple-700 ${isRTL ? 'flex-row-reverse' : ''}`}>
                  <DollarSign className="w-4 h-4" />
                  {isRTL ? 'عروض أسعار' : 'Proposals'}
                </span>
                <span className="font-bold text-purple-800">{stats.today_activity?.new_proposals || 0}</span>
              </div>
              {stats.today_activity?.notifications?.length > 0 && (
                <div className="pt-2 border-t border-purple-100">
                  <p className={`text-xs text-purple-600 mb-2 ${isRTL ? 'text-right' : ''}`}>
                    {isRTL ? 'آخر الإشعارات' : 'Recent Notifications'}
                  </p>
                  <div className="space-y-1 max-h-20 overflow-y-auto">
                    {stats.today_activity.notifications.slice(0, 2).map((notif, idx) => (
                      <p key={idx} className={`text-xs text-slate-600 truncate ${isRTL ? 'text-right' : ''}`}>
                        • {isRTL ? notif.title_ar || notif.title : notif.title}
                      </p>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Auditor Workload Chart */}
      <Card className="border-slate-200 hover:shadow-lg transition-all" data-testid="auditor-workload-widget">
        <CardHeader>
          <div className={`flex items-center justify-between ${isRTL ? 'flex-row-reverse' : ''}`}>
            <div>
              <CardTitle className={`text-lg font-semibold text-slate-800 ${isRTL ? 'text-right' : ''}`}>
                {isRTL ? 'توزيع عبء العمل على المدققين' : 'Auditor Workload Distribution'}
              </CardTitle>
              <CardDescription className={isRTL ? 'text-right' : ''}>
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
                    <div className={`flex justify-between text-sm ${isRTL ? 'flex-row-reverse' : ''}`}>
                      <span className="font-medium text-slate-700">
                        {isRTL ? auditor.name_ar || auditor.name : auditor.name}
                      </span>
                      <span className="text-slate-500">
                        {auditor.total_tasks} {isRTL ? 'مهمة' : 'tasks'}
                      </span>
                    </div>
                    <div className="h-3 bg-slate-100 rounded-full overflow-hidden">
                      <div 
                        className={`h-full ${colors[idx % colors.length]} rounded-full transition-all`}
                        style={{ width: `${percentage}%` }}
                      />
                    </div>
                  </div>
                );
              })}
              {stats.auditor_workload.length === 0 && (
                <div className="text-center py-8 text-slate-500">
                  <Users className="w-12 h-12 mx-auto mb-2 opacity-30" />
                  <p>{isRTL ? 'لا يوجد مدققين مسجلين' : 'No auditors registered yet'}</p>
                </div>
              )}
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
