import React, { useState, useContext, useEffect } from 'react';
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
  const [rememberMe, setRememberMe] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useContext(AuthContext);
  const navigate = useNavigate();

  // Load saved credentials on mount
  useEffect(() => {
    const savedEmail = localStorage.getItem('savedEmail');
    const savedPassword = localStorage.getItem('savedPassword');
    if (savedEmail && savedPassword) {
      setEmail(savedEmail);
      setPassword(savedPassword);
      setRememberMe(true);
    }
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await axios.post(`${API}/auth/login`, { email, password });
      
      // Save credentials if "Remember me" is checked
      if (rememberMe) {
        localStorage.setItem('savedEmail', email);
        localStorage.setItem('savedPassword', password);
      } else {
        localStorage.removeItem('savedEmail');
        localStorage.removeItem('savedPassword');
      }
      
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
        <img 
          src="/bayan-logo.png" 
          alt="Bayan Auditing & Conformity" 
          className="h-32 w-auto object-contain mx-auto mb-4"
        />
        <p className="text-bayan-gray text-base font-medium">
          {t('serviceContractManagement')}
        </p>
      </div>
      
      <div className="w-full max-w-md">
        {/* Login Form Card */}
        <Card className="w-full border-2 border-blue-100 shadow-xl">
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

            <div className="flex items-center space-x-2 rtl:space-x-reverse">
              <input
                type="checkbox"
                id="rememberMe"
                checked={rememberMe}
                onChange={(e) => setRememberMe(e.target.checked)}
                className="w-4 h-4 text-bayan-blue bg-gray-100 border-gray-300 rounded focus:ring-bayan-blue focus:ring-2"
                data-testid="remember-me-checkbox"
              />
              <Label htmlFor="rememberMe" className="text-sm font-medium text-gray-700 cursor-pointer">
                {t('rememberMe')}
              </Label>
            </div>

            <Button type="submit" className="w-full bg-bayan-blue hover:bg-bayan-blue-dark text-white font-semibold py-6 text-lg shadow-lg" disabled={loading} data-testid="login-submit-button">
              {loading ? t('signingIn') : t('signIn')}
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* Demo Credentials Card */}
      <Card className="w-full lg:w-1/2 border-2 border-blue-100 shadow-xl">
        <CardHeader className="bg-gradient-to-r from-blue-50 to-blue-100 border-b-2 border-blue-200">
          <CardTitle className="text-xl font-bold text-bayan-blue flex items-center gap-2">
            🔐 {t('demoCredentials')}
          </CardTitle>
          <CardDescription className="text-bayan-gray">{t('useTheseCredentials')}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4 pt-6">
          {/* Admin Credentials */}
          <div className="p-5 bg-gradient-to-br from-purple-50 to-white rounded-xl border-2 border-purple-300 hover:border-purple-500 hover:shadow-lg transition-all cursor-pointer transform hover:scale-[1.02]"
               onClick={() => { setEmail('admin@test.com'); setPassword('admin123'); }}
               data-testid="admin-credentials-card">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-bold text-purple-900 text-lg flex items-center gap-2">
                <span className="text-2xl">👨‍💼</span> {t('admin')}
              </h3>
              <span className="text-xs px-3 py-1.5 bg-purple-500 text-white rounded-full font-semibold shadow-md">
                {t('clickToFill')}
              </span>
            </div>
            <div className="space-y-2 text-sm">
              <div className="flex items-center gap-2">
                <span className="font-semibold text-gray-700 min-w-[80px]">{t('email')}:</span>
                <code className="text-purple-700 bg-purple-100 px-3 py-1.5 rounded-lg font-mono text-xs">admin@test.com</code>
              </div>
              <div className="flex items-center gap-2">
                <span className="font-semibold text-gray-700 min-w-[80px]">{t('password')}:</span>
                <code className="text-purple-700 bg-purple-100 px-3 py-1.5 rounded-lg font-mono text-xs">admin123</code>
              </div>
            </div>
            <p className="text-xs text-gray-600 mt-3 leading-relaxed">
              {t('adminAccess')}
            </p>
          </div>

          {/* Client Credentials */}
          <div className="p-5 bg-gradient-to-br from-green-50 to-white rounded-xl border-2 border-green-300 hover:border-green-500 hover:shadow-lg transition-all cursor-pointer transform hover:scale-[1.02]"
               onClick={() => { setEmail('client@test.com'); setPassword('client123'); }}
               data-testid="client-credentials-card">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-bold text-green-900 text-lg flex items-center gap-2">
                <span className="text-2xl">👤</span> {t('client')}
              </h3>
              <span className="text-xs px-3 py-1.5 bg-green-500 text-white rounded-full font-semibold shadow-md">
                {t('clickToFill')}
              </span>
            </div>
            <div className="space-y-2 text-sm">
              <div className="flex items-center gap-2">
                <span className="font-semibold text-gray-700 min-w-[80px]">{t('email')}:</span>
                <code className="text-green-700 bg-green-100 px-3 py-1.5 rounded-lg font-mono text-xs">client@test.com</code>
              </div>
              <div className="flex items-center gap-2">
                <span className="font-semibold text-gray-700 min-w-[80px]">{t('password')}:</span>
                <code className="text-green-700 bg-green-100 px-3 py-1.5 rounded-lg font-mono text-xs">client123</code>
              </div>
            </div>
            <p className="text-xs text-gray-600 mt-3 leading-relaxed">
              {t('clientAccess')}
            </p>
          </div>

          <div className="pt-3 border-t border-blue-200 bg-blue-50 -mx-6 px-6 -mb-6 pb-6 rounded-b-lg">
            <p className="text-xs text-center text-bayan-gray flex items-center justify-center gap-2">
              <span className="text-lg">💡</span>
              <span>{t('clickCredentialsTip')}</span>
            </p>
          </div>
        </CardContent>
      </Card>
      </div>
    </div>
  );
};

export default LoginPage;
