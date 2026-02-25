import React, { useState, useContext } from 'react';
import { useTranslation } from 'react-i18next';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Settings, Users, Bell, Shield, Globe, Palette } from 'lucide-react';
import { AuthContext } from '@/App';
import UserManagementTab from '@/components/settings/UserManagementTab';

const SettingsPage = () => {
  const { t, i18n } = useTranslation();
  const { user } = useContext(AuthContext);
  const isRTL = i18n.language?.startsWith('ar');
  
  // Check if current user is system admin
  const isSystemAdmin = user?.role === 'system_admin' || user?.role === 'admin';
  
  const [activeTab, setActiveTab] = useState('users');

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
      </Tabs>
    </div>
  );
};

export default SettingsPage;
