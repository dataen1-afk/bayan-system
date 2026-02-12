import React, { useState, useContext } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { useTranslation } from 'react-i18next';
import { API, AuthContext } from '@/App';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import LanguageSwitcher from '@/components/LanguageSwitcher';

const LoginPage = () => {
  const { t } = useTranslation();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useContext(AuthContext);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await axios.post(`${API}/auth/login`, { email, password });
      login(response.data.token, response.data.user);
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.detail || t('errorLogin'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-100 p-4" data-testid="login-page">
      <div className="absolute top-4 right-4 z-10">
        <LanguageSwitcher />
      </div>
      
      {/* Logo Section */}
      <div className="mb-8 text-center">
        <div className="bg-white p-6 rounded-2xl shadow-lg mb-4 inline-block">
          <img 
            src="/bayan-logo.jpeg" 
            alt="Bayan Auditing & Conformity" 
            className="h-24 w-auto object-contain"
          />
        </div>
        <p className="text-bayan-gray text-base font-medium">
          {t('serviceContractManagement')}
        </p>
      </div>
      
      <div className="w-full max-w-5xl flex flex-col lg:flex-row gap-6">
        {/* Login Form Card */}
        <Card className="w-full lg:w-1/2 border-2 border-blue-100 shadow-xl">
          <CardHeader className="bg-gradient-to-r from-bayan-blue to-blue-600 text-white rounded-t-lg">
            <CardTitle className="text-2xl font-bold" data-testid="login-title">{t('login')}</CardTitle>
            <CardDescription className="text-blue-100">{t('signInToAccount')}</CardDescription>
          </CardHeader>
          <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <div className="p-3 text-sm text-red-600 bg-red-50 border border-red-200 rounded" data-testid="login-error">
                {error}
              </div>
            )}
            
            <div className="space-y-2">
              <Label htmlFor="email">{t('email')}</Label>
              <Input
                id="email"
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                data-testid="login-email-input"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="password">{t('password')}</Label>
              <Input
                id="password"
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                data-testid="login-password-input"
              />
            </div>

            <Button type="submit" className="w-full" disabled={loading} data-testid="login-submit-button">
              {loading ? t('signingIn') : t('signIn')}
            </Button>

            <p className="text-sm text-center text-gray-600">
              {t('dontHaveAccount')}{' '}
              <Link to="/register" className="text-blue-600 hover:underline" data-testid="register-link">
                {t('registerHere')}
              </Link>
            </p>
          </form>
        </CardContent>
      </Card>

      {/* Demo Credentials Card */}
      <Card className="w-full lg:w-1/2 bg-gradient-to-br from-blue-50 to-white border-blue-200">
        <CardHeader>
          <CardTitle className="text-xl font-bold text-blue-900">
            🔐 {t('demoCredentials')}
          </CardTitle>
          <CardDescription>{t('useTheseCredentials')}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Admin Credentials */}
          <div className="p-4 bg-white rounded-lg border-2 border-purple-200 hover:border-purple-400 transition-colors cursor-pointer"
               onClick={() => { setEmail('admin@test.com'); setPassword('admin123'); }}
               data-testid="admin-credentials-card">
            <div className="flex items-center justify-between mb-2">
              <h3 className="font-bold text-purple-900">👨‍💼 {t('admin')}</h3>
              <span className="text-xs px-2 py-1 bg-purple-100 text-purple-800 rounded-full">
                {t('clickToFill')}
              </span>
            </div>
            <div className="space-y-1 text-sm">
              <div className="flex items-center gap-2">
                <span className="font-medium text-gray-600">{t('email')}:</span>
                <code className="text-purple-700 bg-purple-50 px-2 py-1 rounded">admin@test.com</code>
              </div>
              <div className="flex items-center gap-2">
                <span className="font-medium text-gray-600">{t('password')}:</span>
                <code className="text-purple-700 bg-purple-50 px-2 py-1 rounded">admin123</code>
              </div>
            </div>
            <p className="text-xs text-gray-500 mt-2">
              {t('adminAccess')}
            </p>
          </div>

          {/* Client Credentials */}
          <div className="p-4 bg-white rounded-lg border-2 border-green-200 hover:border-green-400 transition-colors cursor-pointer"
               onClick={() => { setEmail('client@test.com'); setPassword('client123'); }}
               data-testid="client-credentials-card">
            <div className="flex items-center justify-between mb-2">
              <h3 className="font-bold text-green-900">👤 {t('client')}</h3>
              <span className="text-xs px-2 py-1 bg-green-100 text-green-800 rounded-full">
                {t('clickToFill')}
              </span>
            </div>
            <div className="space-y-1 text-sm">
              <div className="flex items-center gap-2">
                <span className="font-medium text-gray-600">{t('email')}:</span>
                <code className="text-green-700 bg-green-50 px-2 py-1 rounded">client@test.com</code>
              </div>
              <div className="flex items-center gap-2">
                <span className="font-medium text-gray-600">{t('password')}:</span>
                <code className="text-green-700 bg-green-50 px-2 py-1 rounded">client123</code>
              </div>
            </div>
            <p className="text-xs text-gray-500 mt-2">
              {t('clientAccess')}
            </p>
          </div>

          <div className="pt-2 border-t border-blue-200">
            <p className="text-xs text-center text-gray-600">
              💡 {t('clickCredentialsTip')}
            </p>
          </div>
        </CardContent>
      </Card>
      </div>
    </div>
  );
};

export default LoginPage;
