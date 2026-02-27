import React, { useState, useContext, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Settings, Users, Bell, Shield, Globe, Trash2, AlertTriangle, Database, CheckCircle } from 'lucide-react';
import { AuthContext } from '@/App';
import UserManagementTab from '@/components/settings/UserManagementTab';
import axios from 'axios';

const API = process.env.REACT_APP_BACKEND_URL;

const SettingsPage = () => {
  const { t, i18n } = useTranslation();
  const { user, token } = useContext(AuthContext);
  const isRTL = i18n.language?.startsWith('ar');
  
  // Check if current user is system admin
  const isSystemAdmin = user?.role === 'system_admin' || user?.role === 'admin';
  
  const [activeTab, setActiveTab] = useState('users');
  const [dataSummary, setDataSummary] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [deleteResult, setDeleteResult] = useState(null);
  const [showConfirmDelete, setShowConfirmDelete] = useState(false);

  // Fetch data summary when Data Management tab is selected
  useEffect(() => {
    if (activeTab === 'data' && isSystemAdmin) {
      fetchDataSummary();
    }
  }, [activeTab]);

  const fetchDataSummary = async () => {
    try {
      setIsLoading(true);
      const response = await axios.get(`${API}/api/admin/data-summary`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setDataSummary(response.data);
    } catch (error) {
      console.error('Error fetching data summary:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearAllData = async () => {
    try {
      setIsLoading(true);
      const response = await axios.delete(`${API}/api/admin/clear-all-data`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setDeleteResult(response.data);
      setShowConfirmDelete(false);
      // Refresh the summary
      await fetchDataSummary();
    } catch (error) {
      console.error('Error clearing data:', error);
      setDeleteResult({ 
        message: isRTL ? 'حدث خطأ أثناء حذف البيانات' : 'Error clearing data',
        error: error.response?.data?.detail || error.message 
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={`p-6 ${isRTL ? 'rtl' : 'ltr'}`}>
      {/* Header */}
      <div className="mb-6">
        <h1 className={`text-2xl font-bold text-[#1e3a5f] flex items-center gap-2 ${isRTL ? 'flex-row-reverse' : ''}`}>
          <Settings className="w-7 h-7" />
          {isRTL ? 'الإعدادات' : 'Settings'}
        </h1>
        <p className="text-slate-600 mt-1">
          {isRTL ? 'إدارة إعدادات النظام والمستخدمين' : 'Manage system settings and users'}
        </p>
      </div>

      {/* Settings Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className={`bg-slate-100 p-1 ${isRTL ? 'flex-row-reverse' : ''}`}>
          <TabsTrigger 
            value="users" 
            className={`gap-2 data-[state=active]:bg-white ${isRTL ? 'flex-row-reverse' : ''}`}
          >
            <Users className="w-4 h-4" />
            {isRTL ? 'المستخدمين' : 'Users'}
          </TabsTrigger>
          <TabsTrigger 
            value="notifications" 
            className={`gap-2 data-[state=active]:bg-white ${isRTL ? 'flex-row-reverse' : ''}`}
          >
            <Bell className="w-4 h-4" />
            {isRTL ? 'الإشعارات' : 'Notifications'}
          </TabsTrigger>
          <TabsTrigger 
            value="security" 
            className={`gap-2 data-[state=active]:bg-white ${isRTL ? 'flex-row-reverse' : ''}`}
          >
            <Shield className="w-4 h-4" />
            {isRTL ? 'الأمان' : 'Security'}
          </TabsTrigger>
          <TabsTrigger 
            value="language" 
            className={`gap-2 data-[state=active]:bg-white ${isRTL ? 'flex-row-reverse' : ''}`}
          >
            <Globe className="w-4 h-4" />
            {isRTL ? 'اللغة' : 'Language'}
          </TabsTrigger>
          {isSystemAdmin && (
            <TabsTrigger 
              value="data" 
              className={`gap-2 data-[state=active]:bg-white ${isRTL ? 'flex-row-reverse' : ''}`}
            >
              <Database className="w-4 h-4" />
              {isRTL ? 'إدارة البيانات' : 'Data Management'}
            </TabsTrigger>
          )}
        </TabsList>

        {/* Users Tab */}
        <TabsContent value="users">
          <UserManagementTab />
        </TabsContent>

        {/* Notifications Tab */}
        <TabsContent value="notifications">
          <Card>
            <CardHeader>
              <CardTitle className={`flex items-center gap-2 ${isRTL ? 'flex-row-reverse' : ''}`}>
                <Bell className="w-5 h-5" />
                {isRTL ? 'إعدادات الإشعارات' : 'Notification Settings'}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-slate-500 text-center py-8">
                {isRTL ? 'إعدادات الإشعارات قيد التطوير' : 'Notification settings coming soon'}
              </p>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Security Tab */}
        <TabsContent value="security">
          <Card>
            <CardHeader>
              <CardTitle className={`flex items-center gap-2 ${isRTL ? 'flex-row-reverse' : ''}`}>
                <Shield className="w-5 h-5" />
                {isRTL ? 'إعدادات الأمان' : 'Security Settings'}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-slate-500 text-center py-8">
                {isRTL ? 'إعدادات الأمان قيد التطوير' : 'Security settings coming soon'}
              </p>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Language Tab */}
        <TabsContent value="language">
          <Card>
            <CardHeader>
              <CardTitle className={`flex items-center gap-2 ${isRTL ? 'flex-row-reverse' : ''}`}>
                <Globe className="w-5 h-5" />
                {isRTL ? 'إعدادات اللغة' : 'Language Settings'}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-slate-500 text-center py-8">
                {isRTL ? 'استخدم محول اللغة في أعلى الصفحة' : 'Use the language switcher at the top of the page'}
              </p>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Data Management Tab (System Admin Only) */}
        {isSystemAdmin && (
          <TabsContent value="data">
            <div className="space-y-6" dir={isRTL ? 'rtl' : 'ltr'}>
              {/* Data Summary Card */}
              <Card dir={isRTL ? 'rtl' : 'ltr'}>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Database className="w-5 h-5" />
                    {isRTL ? 'ملخص البيانات' : 'Data Summary'}
                  </CardTitle>
                  <CardDescription>
                    {isRTL ? 'نظرة عامة على جميع البيانات في النظام' : 'Overview of all data in the system'}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {isLoading ? (
                    <div className="text-center py-8">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                      <p className="mt-2 text-slate-500">{isRTL ? 'جاري التحميل...' : 'Loading...'}</p>
                    </div>
                  ) : dataSummary ? (
                    <div>
                      <div className="mb-4 p-4 bg-blue-50 rounded-lg">
                        <p className="text-lg font-bold text-blue-800">
                          {isRTL ? 'إجمالي السجلات:' : 'Total Records:'} {dataSummary.total_records}
                        </p>
                      </div>
                      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
                        {dataSummary.collections?.map((coll) => (
                          <div key={coll.collection} className={`p-3 border rounded-lg ${coll.count > 0 ? 'bg-slate-50' : 'bg-white'}`} dir={isRTL ? 'rtl' : 'ltr'}>
                            <p className="text-sm font-medium text-slate-700">{coll.name_ar}</p>
                            <p className="text-xs text-slate-500">{coll.collection}</p>
                            <p className={`text-lg font-bold ${coll.count > 0 ? 'text-blue-600' : 'text-slate-400'}`}>
                              {coll.count}
                            </p>
                          </div>
                        ))}
                      </div>
                    </div>
                  ) : (
                    <p className="text-slate-500 text-center py-8">
                      {isRTL ? 'لا توجد بيانات متاحة' : 'No data available'}
                    </p>
                  )}
                </CardContent>
              </Card>

              {/* Delete All Data Card */}
              <Card className="border-red-200" dir={isRTL ? 'rtl' : 'ltr'}>
                <CardHeader className="bg-red-50">
                  <CardTitle className="flex items-center gap-2 text-red-700">
                    <AlertTriangle className="w-5 h-5" />
                    {isRTL ? 'حذف جميع البيانات التجريبية' : 'Delete All Test Data'}
                  </CardTitle>
                  <CardDescription className="text-red-600">
                    {isRTL 
                      ? 'تحذير: سيؤدي هذا الإجراء إلى حذف جميع البيانات باستثناء حسابات المستخدمين'
                      : 'Warning: This action will delete all data except user accounts'}
                  </CardDescription>
                </CardHeader>
                <CardContent className="pt-6">
                  {deleteResult && (
                    <div className={`mb-4 p-4 rounded-lg ${deleteResult.error ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'}`}>
                      <div className="flex items-center gap-2">
                        {deleteResult.error ? <AlertTriangle className="w-5 h-5" /> : <CheckCircle className="w-5 h-5" />}
                        <p className="font-medium">{deleteResult.message}</p>
                      </div>
                      {deleteResult.details && (
                        <div className="mt-2 text-sm">
                          {Object.entries(deleteResult.details).map(([key, value]) => (
                            <p key={key}>{key}: {value}</p>
                          ))}
                        </div>
                      )}
                    </div>
                  )}

                  {!showConfirmDelete ? (
                    <Button 
                      variant="destructive" 
                      onClick={() => setShowConfirmDelete(true)}
                      className={`gap-2 ${isRTL ? 'flex-row-reverse' : ''}`}
                      disabled={!dataSummary || dataSummary.total_records === 0}
                    >
                      <Trash2 className="w-4 h-4" />
                      {isRTL ? 'حذف جميع البيانات التجريبية' : 'Delete All Test Data'}
                    </Button>
                  ) : (
                    <div className="space-y-4">
                      <div className="p-4 bg-red-100 border border-red-300 rounded-lg">
                        <p className="font-bold text-red-800">
                          {isRTL ? 'هل أنت متأكد؟' : 'Are you sure?'}
                        </p>
                        <p className="text-red-700 text-sm mt-1">
                          {isRTL 
                            ? `سيتم حذف ${dataSummary?.total_records || 0} سجل. هذا الإجراء لا يمكن التراجع عنه.`
                            : `${dataSummary?.total_records || 0} records will be deleted. This action cannot be undone.`}
                        </p>
                      </div>
                      <div className={`flex gap-3 ${isRTL ? 'flex-row-reverse' : ''}`}>
                        <Button 
                          variant="destructive" 
                          onClick={handleClearAllData}
                          disabled={isLoading}
                          className={`gap-2 ${isRTL ? 'flex-row-reverse' : ''}`}
                        >
                          {isLoading ? (
                            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                          ) : (
                            <Trash2 className="w-4 h-4" />
                          )}
                          {isRTL ? 'نعم، احذف الكل' : 'Yes, Delete All'}
                        </Button>
                        <Button 
                          variant="outline" 
                          onClick={() => setShowConfirmDelete(false)}
                          disabled={isLoading}
                        >
                          {isRTL ? 'إلغاء' : 'Cancel'}
                        </Button>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        )}
      </Tabs>
    </div>
  );
};

export default SettingsPage;
