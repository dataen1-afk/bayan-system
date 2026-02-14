import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { 
  BarChart3, TrendingUp, FileText, DollarSign, CheckCircle, 
  XCircle, Clock, ArrowLeft, RefreshCw, Loader2, Filter,
  Calendar, AlertCircle, Download, FileSpreadsheet
} from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL + '/api';

const ReportsPage = () => {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const isRTL = i18n.language?.startsWith('ar');
  
  const [loading, setLoading] = useState(true);
  const [submissionStats, setSubmissionStats] = useState(null);
  const [revenueStats, setRevenueStats] = useState(null);
  const [filteredData, setFilteredData] = useState(null);
  
  // Filter states
  const [showFilters, setShowFilters] = useState(false);
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [standardFilter, setStandardFilter] = useState('all');
  const [filtersApplied, setFiltersApplied] = useState(false);
  const [exporting, setExporting] = useState(false);

  const certificationStandards = [
    'ISO9001', 'ISO14001', 'ISO45001', 'ISO22000', 
    'ISO13485', 'ISO22301', 'ISO27001', 'ISO50001'
  ];

  const statusOptions = [
    { value: 'all', label: t('all') || 'All' },
    { value: 'pending', label: t('pending') },
    { value: 'submitted', label: t('submitted') },
    { value: 'under_review', label: t('under_review') },
    { value: 'accepted', label: t('accepted') },
    { value: 'rejected', label: t('rejected') },
    { value: 'agreement_signed', label: t('agreement_signed') },
    { value: 'modification_requested', label: t('modificationRequested') || 'Modification Requested' }
  ];

  useEffect(() => {
    loadAllStats();
  }, []);

  const handleExport = async (format) => {
    setExporting(true);
    try {
      const token = localStorage.getItem('token');
      const headers = { Authorization: `Bearer ${token}` };
      
      const params = new URLSearchParams();
      params.append('format', format);
      if (startDate) params.append('start_date', startDate);
      if (endDate) params.append('end_date', endDate);
      if (statusFilter !== 'all') params.append('status', statusFilter);
      if (standardFilter !== 'all') params.append('standard', standardFilter);
      
      const response = await axios.get(`${API}/reports/export?${params.toString()}`, {
        headers,
        responseType: 'blob'
      });
      
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      const filename = format === 'excel' 
        ? `report_${new Date().toISOString().split('T')[0]}.xlsx`
        : `report_${new Date().toISOString().split('T')[0]}.pdf`;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error exporting report:', error);
      alert(t('errorExportingReport'));
    } finally {
      setExporting(false);
    }
  };

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
      setFilteredData(null);
      setFiltersApplied(false);
    } catch (error) {
      console.error('Error loading stats:', error);
    } finally {
      setLoading(false);
    }
  };

  const applyFilters = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const headers = { Authorization: `Bearer ${token}` };
      
      const params = new URLSearchParams();
      if (startDate) params.append('start_date', startDate);
      if (endDate) params.append('end_date', endDate);
      if (statusFilter !== 'all') params.append('status', statusFilter);
      if (standardFilter !== 'all') params.append('standard', standardFilter);
      
      const response = await axios.get(`${API}/reports/filtered?${params.toString()}`, { headers });
      setFilteredData(response.data);
      setFiltersApplied(true);
    } catch (error) {
      console.error('Error applying filters:', error);
    } finally {
      setLoading(false);
    }
  };

  const clearFilters = () => {
    setStartDate('');
    setEndDate('');
    setStatusFilter('all');
    setStandardFilter('all');
    setFilteredData(null);
    setFiltersApplied(false);
    loadAllStats();
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount || 0) + ' SAR';
  };

  if (loading && !submissionStats) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-bayan-navy" />
      </div>
    );
  }

  // Use filtered data if filters are applied, otherwise use original stats
  const displayStats = filtersApplied && filteredData ? {
    total_forms: filteredData.forms.total,
    submitted_forms: filteredData.forms.submitted,
    pending_forms: filteredData.forms.pending,
    total_proposals: filteredData.proposals.total,
    accepted_proposals: filteredData.proposals.accepted,
    conversion_rate: filteredData.conversion_rate,
    monthly_stats: submissionStats?.monthly_stats || []
  } : submissionStats;

  const displayRevenue = filtersApplied && filteredData ? {
    total_quoted: filteredData.revenue.total_quoted,
    accepted_revenue: filteredData.revenue.accepted,
    pending_revenue: filteredData.revenue.pending,
    rejected_revenue: filteredData.revenue.rejected,
    total_contracts: revenueStats?.total_contracts || 0,
    monthly_revenue: revenueStats?.monthly_revenue || []
  } : revenueStats;

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
              data-testid="back-to-dashboard-btn"
            >
              <ArrowLeft className={`w-4 h-4 ${isRTL ? 'ml-2 rotate-180' : 'mr-2'}`} />
              {t('backToDashboard')}
            </Button>
            <h1 className="text-2xl font-bold text-bayan-navy flex items-center gap-2">
              <BarChart3 className="w-6 h-6" />
              {t('reportsAnalytics')}
            </h1>
          </div>
          <div className="flex items-center gap-2">
            <Button 
              variant={showFilters ? "default" : "outline"} 
              onClick={() => setShowFilters(!showFilters)}
              className={showFilters ? "bg-bayan-navy" : ""}
              data-testid="toggle-filters-btn"
            >
              <Filter className="w-4 h-4 mr-2" />
              {t('filters') || 'Filters'}
            </Button>
            <Button variant="outline" onClick={loadAllStats} data-testid="refresh-btn">
              <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
              {t('refresh')}
            </Button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Filters Panel */}
        {showFilters && (
          <Card className="mb-6 border-bayan-navy/20" data-testid="filters-panel">
            <CardHeader className={isRTL ? 'text-right' : ''}>
              <CardTitle className="flex items-center gap-2 text-lg">
                <Filter className="w-5 h-5 text-bayan-navy" />
                {t('filterReports') || 'Filter Reports'}
              </CardTitle>
              <CardDescription>{t('filterDescription') || 'Apply filters to narrow down your report data'}</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {/* Date Range - Start */}
                <div className="space-y-2">
                  <Label className="flex items-center gap-1">
                    <Calendar className="w-4 h-4" />
                    {t('startDate') || 'Start Date'}
                  </Label>
                  <Input
                    type="date"
                    value={startDate}
                    onChange={(e) => setStartDate(e.target.value)}
                    data-testid="start-date-input"
                  />
                </div>
                
                {/* Date Range - End */}
                <div className="space-y-2">
                  <Label className="flex items-center gap-1">
                    <Calendar className="w-4 h-4" />
                    {t('endDate') || 'End Date'}
                  </Label>
                  <Input
                    type="date"
                    value={endDate}
                    onChange={(e) => setEndDate(e.target.value)}
                    data-testid="end-date-input"
                  />
                </div>
                
                {/* Status Filter */}
                <div className="space-y-2">
                  <Label>{t('status')}</Label>
                  <select
                    value={statusFilter}
                    onChange={(e) => setStatusFilter(e.target.value)}
                    className="w-full h-10 px-3 rounded-md border border-input bg-background text-sm"
                    data-testid="status-filter-select"
                  >
                    {statusOptions.map(option => (
                      <option key={option.value} value={option.value}>{option.label}</option>
                    ))}
                  </select>
                </div>
                
                {/* Standard Filter */}
                <div className="space-y-2">
                  <Label>{t('certificationStandards') || 'Certification Standard'}</Label>
                  <select
                    value={standardFilter}
                    onChange={(e) => setStandardFilter(e.target.value)}
                    className="w-full h-10 px-3 rounded-md border border-input bg-background text-sm"
                    data-testid="standard-filter-select"
                  >
                    <option value="all">{t('all') || 'All Standards'}</option>
                    {certificationStandards.map(std => (
                      <option key={std} value={std}>{std}</option>
                    ))}
                  </select>
                </div>
              </div>
              
              {/* Filter Actions */}
              <div className={`flex gap-2 mt-4 ${isRTL ? 'flex-row-reverse' : ''}`}>
                <Button 
                  onClick={applyFilters} 
                  className="bg-bayan-navy hover:bg-bayan-navy-light"
                  disabled={loading}
                  data-testid="apply-filters-btn"
                >
                  {loading ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : null}
                  {t('applyFilters') || 'Apply Filters'}
                </Button>
                <Button 
                  variant="outline" 
                  onClick={clearFilters}
                  data-testid="clear-filters-btn"
                >
                  {t('clearFilters') || 'Clear Filters'}
                </Button>
              </div>
              
              {/* Active Filters Indicator */}
              {filtersApplied && (
                <div className="mt-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
                  <p className="text-sm text-blue-800 flex items-center gap-2">
                    <AlertCircle className="w-4 h-4" />
                    {t('filtersActive') || 'Filters are active. Showing filtered results.'}
                    {filteredData?.filters_applied && (
                      <span className="ml-2 text-blue-600">
                        ({startDate && `${t('from') || 'From'}: ${startDate}`}
                        {endDate && ` ${t('to') || 'To'}: ${endDate}`}
                        {statusFilter !== 'all' && ` | ${t('status')}: ${statusFilter}`}
                        {standardFilter !== 'all' && ` | ${t('standard') || 'Standard'}: ${standardFilter}`})
                      </span>
                    )}
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {/* Total Forms */}
          <Card className="bg-white" data-testid="total-forms-card">
            <CardContent className="pt-6">
              <div className={`flex items-center justify-between ${isRTL ? 'flex-row-reverse' : ''}`}>
                <div className={isRTL ? 'text-right' : ''}>
                  <p className="text-sm text-gray-500">{t('totalForms')}</p>
                  <p className="text-3xl font-bold text-gray-800">{displayStats?.total_forms || 0}</p>
                </div>
                <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                  <FileText className="w-6 h-6 text-blue-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Submitted Forms */}
          <Card className="bg-white" data-testid="submitted-forms-card">
            <CardContent className="pt-6">
              <div className={`flex items-center justify-between ${isRTL ? 'flex-row-reverse' : ''}`}>
                <div className={isRTL ? 'text-right' : ''}>
                  <p className="text-sm text-gray-500">{t('submittedForms')}</p>
                  <p className="text-3xl font-bold text-green-600">{displayStats?.submitted_forms || 0}</p>
                </div>
                <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
                  <CheckCircle className="w-6 h-6 text-green-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Conversion Rate */}
          <Card className="bg-white" data-testid="conversion-rate-card">
            <CardContent className="pt-6">
              <div className={`flex items-center justify-between ${isRTL ? 'flex-row-reverse' : ''}`}>
                <div className={isRTL ? 'text-right' : ''}>
                  <p className="text-sm text-gray-500">{t('conversionRate')}</p>
                  <p className="text-3xl font-bold text-purple-600">{displayStats?.conversion_rate || 0}%</p>
                </div>
                <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center">
                  <TrendingUp className="w-6 h-6 text-purple-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Total Contracts */}
          <Card className="bg-white" data-testid="total-contracts-card">
            <CardContent className="pt-6">
              <div className={`flex items-center justify-between ${isRTL ? 'flex-row-reverse' : ''}`}>
                <div className={isRTL ? 'text-right' : ''}>
                  <p className="text-sm text-gray-500">{t('totalContracts')}</p>
                  <p className="text-3xl font-bold text-bayan-navy">{displayRevenue?.total_contracts || 0}</p>
                </div>
                <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                  <DollarSign className="w-6 h-6 text-bayan-navy" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Standards Breakdown (only shown when filtered) */}
        {filtersApplied && filteredData?.standards_breakdown && Object.keys(filteredData.standards_breakdown).length > 0 && (
          <Card className="mb-8" data-testid="standards-breakdown-card">
            <CardHeader className={isRTL ? 'text-right' : ''}>
              <CardTitle className="flex items-center gap-2">
                <FileText className="w-5 h-5 text-bayan-navy" />
                {t('standardsBreakdown') || 'Standards Breakdown'}
              </CardTitle>
              <CardDescription>{t('proposalsByStandard') || 'Proposals grouped by certification standard'}</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-3">
                {Object.entries(filteredData.standards_breakdown).map(([std, count]) => (
                  <div key={std} className="px-4 py-2 bg-bayan-navy/10 rounded-lg">
                    <span className="font-medium text-bayan-navy">{std}</span>
                    <span className="ml-2 bg-bayan-navy text-white px-2 py-0.5 rounded-full text-sm">{count}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Revenue Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Revenue Overview */}
          <Card data-testid="revenue-overview-card">
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
                  <span className="font-semibold text-gray-800">{formatCurrency(displayRevenue?.total_quoted)}</span>
                </div>
                
                {/* Accepted Revenue */}
                <div className={`flex justify-between items-center p-3 bg-green-50 rounded-lg ${isRTL ? 'flex-row-reverse' : ''}`}>
                  <span className="text-green-700 flex items-center gap-2">
                    <CheckCircle className="w-4 h-4" />
                    {t('acceptedRevenue')}
                  </span>
                  <span className="font-semibold text-green-700">{formatCurrency(displayRevenue?.accepted_revenue)}</span>
                </div>
                
                {/* Pending Revenue */}
                <div className={`flex justify-between items-center p-3 bg-yellow-50 rounded-lg ${isRTL ? 'flex-row-reverse' : ''}`}>
                  <span className="text-yellow-700 flex items-center gap-2">
                    <Clock className="w-4 h-4" />
                    {t('pendingRevenue')}
                  </span>
                  <span className="font-semibold text-yellow-700">{formatCurrency(displayRevenue?.pending_revenue)}</span>
                </div>
                
                {/* Rejected Revenue */}
                <div className={`flex justify-between items-center p-3 bg-red-50 rounded-lg ${isRTL ? 'flex-row-reverse' : ''}`}>
                  <span className="text-red-700 flex items-center gap-2">
                    <XCircle className="w-4 h-4" />
                    {t('rejectedRevenue')}
                  </span>
                  <span className="font-semibold text-red-700">{formatCurrency(displayRevenue?.rejected_revenue)}</span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Proposal Stats */}
          <Card data-testid="proposal-statistics-card">
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
                  <span className="font-semibold text-gray-800">{displayStats?.total_proposals || 0}</span>
                </div>
                
                {/* Accepted */}
                <div className={`flex justify-between items-center ${isRTL ? 'flex-row-reverse' : ''}`}>
                  <span className="text-green-600">{t('accepted')}</span>
                  <span className="font-semibold text-green-600">{displayStats?.accepted_proposals || 0}</span>
                </div>
                
                {/* Pending Forms */}
                <div className={`flex justify-between items-center ${isRTL ? 'flex-row-reverse' : ''}`}>
                  <span className="text-yellow-600">{t('pendingForms')}</span>
                  <span className="font-semibold text-yellow-600">{displayStats?.pending_forms || 0}</span>
                </div>

                {/* Modification Requested (only when filtered) */}
                {filtersApplied && filteredData?.proposals?.modification_requested > 0 && (
                  <div className={`flex justify-between items-center ${isRTL ? 'flex-row-reverse' : ''}`}>
                    <span className="text-orange-600">{t('modificationRequested') || 'Modification Requested'}</span>
                    <span className="font-semibold text-orange-600">{filteredData.proposals.modification_requested}</span>
                  </div>
                )}

                {/* Conversion Progress */}
                <div className="mt-4 pt-4 border-t">
                  <div className={`flex justify-between items-center mb-2 ${isRTL ? 'flex-row-reverse' : ''}`}>
                    <span className="text-sm text-gray-500">{t('conversionProgress')}</span>
                    <span className="text-sm font-medium">{displayStats?.conversion_rate || 0}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-green-500 h-2 rounded-full transition-all"
                      style={{ width: `${displayStats?.conversion_rate || 0}%` }}
                    />
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Monthly Stats */}
        <Card data-testid="monthly-stats-card">
          <CardHeader className={isRTL ? 'text-right' : ''}>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-blue-600" />
              {t('monthlySubmissions')}
            </CardTitle>
            <CardDescription>{t('lastSixMonths')}</CardDescription>
          </CardHeader>
          <CardContent>
            <div className={`flex items-end gap-4 h-48 ${isRTL ? 'flex-row-reverse' : ''}`}>
              {displayStats?.monthly_stats?.map((stat, index) => {
                const maxCount = Math.max(...(displayStats.monthly_stats?.map(s => s.count) || [1]), 1);
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
