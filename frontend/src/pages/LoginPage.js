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
import { Globe, ArrowRight, Shield } from 'lucide-react';

const LoginPage = () => {
  const { t, i18n } = useTranslation();
  const isRTL = i18n.language?.startsWith('ar');
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
    <div className="flex flex-col min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-slate-100" data-testid="login-page">
      {/* Top Bar */}
      <div className="absolute top-0 left-0 right-0 h-1.5 bg-gradient-to-r from-bayan-navy via-bayan-gold to-bayan-navy"></div>
      
      {/* Header with Language Switcher */}
      <div className="absolute top-4 right-4 z-10 flex items-center gap-3">
        <LanguageSwitcher />
      </div>

      {/* Main Content */}
      <div className="flex-1 flex items-center justify-center p-4 py-12">
        <div className="w-full max-w-md">
          {/* Customer Portal Link - Above Login */}
          <div className="mb-6">
            <Link to="/portal">
              <Card className="border-2 border-bayan-gold/30 bg-gradient-to-r from-bayan-gold/5 to-bayan-gold/10 hover:shadow-lg transition-all cursor-pointer group">
                <CardContent className="p-4">
                  <div className={`flex items-center justify-between ${isRTL ? 'flex-row-reverse' : ''}`}>
                    <div className={`flex items-center gap-3 ${isRTL ? 'flex-row-reverse' : ''}`}>
                      <div className="w-10 h-10 rounded-full bg-bayan-gold/20 flex items-center justify-center">
                        <Globe className="w-5 h-5 text-bayan-gold" />
                      </div>
                      <div className={isRTL ? 'text-right' : 'text-left'}>
                        <p className="font-semibold text-bayan-navy">
                          {isRTL ? 'بوابة العملاء' : 'Customer Portal'}
                        </p>
                        <p className="text-xs text-slate-500">
                          {isRTL ? 'تتبع طلبك أو احصل على عرض سعر' : 'Track your order or request a quote'}
                        </p>
                      </div>
                    </div>
                    <ArrowRight className={`w-5 h-5 text-bayan-gold group-hover:translate-x-1 transition-transform ${isRTL ? 'rotate-180 group-hover:-translate-x-1' : ''}`} />
                  </div>
                </CardContent>
              </Card>
            </Link>
          </div>

          {/* Login Form Card */}
          <Card className="w-full border-2 border-slate-200 shadow-xl overflow-hidden">
            <CardHeader className="bg-gradient-to-r from-bayan-navy to-bayan-navy-light text-white text-center pb-8">
              <div className="flex items-center justify-center gap-2 mb-2">
                <Shield className="w-6 h-6" />
              </div>
              <CardTitle className="text-2xl font-bold" data-testid="login-title">
                {isRTL ? 'تسجيل الدخول للمسؤولين' : 'Admin Login'}
              </CardTitle>
              <CardDescription className="text-blue-100">
                {isRTL ? 'قم بتسجيل الدخول للوصول إلى لوحة التحكم' : 'Sign in to access the dashboard'}
              </CardDescription>
            </CardHeader>
            <CardContent className="pt-6">
              {/* Logo at top of white area */}
              <div className="mb-6 text-center">
                <img 
                  src="/bayan-logo.png" 
                  alt="Bayan for Verification and Conformity" 
                  className="h-24 w-auto object-contain mx-auto"
                />
              </div>
              
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
                    className="h-11"
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
                    className="h-11"
                  />
                </div>

                <div className="flex items-center space-x-2 rtl:space-x-reverse">
                  <input
                    type="checkbox"
                    id="rememberMe"
                    checked={rememberMe}
                    onChange={(e) => setRememberMe(e.target.checked)}
                    className="w-4 h-4 text-bayan-navy bg-gray-100 border-gray-300 rounded focus:ring-bayan-navy focus:ring-2"
                    data-testid="remember-me-checkbox"
                  />
                  <Label htmlFor="rememberMe" className="text-sm font-medium text-gray-700 cursor-pointer">
                    {t('rememberMe')}
                  </Label>
                </div>

                <Button 
                  type="submit" 
                  className="w-full bg-bayan-navy hover:bg-bayan-navy-light text-white font-semibold py-6 text-lg shadow-lg" 
                  disabled={loading} 
                  data-testid="login-submit-button"
                >
                  {loading ? (isRTL ? 'جاري تسجيل الدخول...' : 'Signing in...') : (isRTL ? 'تسجيل الدخول' : 'Sign In')}
                </Button>

                {/* Admin Credentials Display */}
                <div className="mt-6 p-4 bg-slate-50 border border-slate-200 rounded-lg">
                  <div className="text-center mb-3">
                    <h3 className="font-semibold text-slate-700 text-sm">
                      {isRTL ? 'بيانات اختبارية' : 'Demo Credentials'}
                    </h3>
                  </div>
                  <div className="space-y-2 text-xs">
                    <div className="flex items-center justify-between bg-white p-2 rounded border border-slate-100">
                      <span className="font-medium text-slate-500">{t('email')}:</span>
                      <code className="text-bayan-navy font-mono bg-slate-50 px-2 py-0.5 rounded">admin@test.com</code>
                    </div>
                    <div className="flex items-center justify-between bg-white p-2 rounded border border-slate-100">
                      <span className="font-medium text-slate-500">{t('password')}:</span>
                      <code className="text-bayan-navy font-mono bg-slate-50 px-2 py-0.5 rounded">admin123</code>
                    </div>
                  </div>
                </div>
              </form>
            </CardContent>
          </Card>

          {/* Footer */}
          <p className="text-center text-sm text-slate-500 mt-6">
            © {new Date().getFullYear()} {isRTL ? 'بيان للتحقق والمطابقة' : 'Bayan for Verification and Conformity'}
          </p>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
