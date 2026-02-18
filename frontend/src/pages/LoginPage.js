import React, { useState, useContext, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { useTranslation } from 'react-i18next';
import { API, AuthContext } from '@/App';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import LanguageSwitcher from '@/components/LanguageSwitcher';
import { Mail, Lock, Eye, EyeOff, ArrowRight } from 'lucide-react';

const LoginPage = () => {
  const { t, i18n } = useTranslation();
  const isRTL = i18n.language?.startsWith('ar');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useContext(AuthContext);
  const navigate = useNavigate();

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
    <div className="min-h-screen relative flex items-center justify-center" data-testid="login-page">
      {/* Full Screen Background Image */}
      <div 
        className="absolute inset-0 bg-cover bg-center bg-no-repeat"
        style={{
          backgroundImage: `url('https://static.prod-images.emergentagent.com/jobs/b2f7052b-c928-43fa-8576-4632fce854a9/images/2981159434af46d8a59e2efde0e4758a357e7cff46c8567933938f350e67d0d0.png')`,
        }}
      />
      
      {/* Subtle overlay for better readability */}
      <div className="absolute inset-0 bg-[#1e3a5f]/20" />

      {/* Logo - Top Right Corner */}
      <div className="absolute top-6 right-6 z-20">
        <img 
          src="/bayan-logo.png" 
          alt="Bayan for Verification and Conformity" 
          className="h-16 md:h-20 drop-shadow-2xl"
        />
      </div>

      {/* Language Switcher - Top Left */}
      <div className="absolute top-6 left-6 z-20">
        <LanguageSwitcher />
      </div>

      {/* Powerful Text - Bottom Right */}
      <div className="absolute bottom-12 right-8 md:right-16 z-10 max-w-lg text-right" dir="rtl">
        <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold text-white mb-4 leading-tight drop-shadow-lg">
          {isRTL ? (
            <>
              <span className="block">شريكك الموثوق في رحلة</span>
              <span className="block text-[#c9a55c]">التميز المؤسسي</span>
            </>
          ) : (
            <>
              <span className="block">Your Trusted Partner in</span>
              <span className="block text-[#c9a55c]">Institutional Excellence</span>
            </>
          )}
        </h2>
        <p className="text-base md:text-lg text-white/90 drop-shadow-md">
          {isRTL 
            ? 'نقدم خدمات التحقق والمطابقة المعتمدة دولياً لمساعدة مؤسستك على تحقيق أعلى معايير الجودة'
            : 'We provide internationally accredited verification and conformity services to help your organization achieve the highest quality standards'
          }
        </p>
      </div>

      {/* Centered Glass Login Card */}
      <div className="relative z-10 w-full max-w-md mx-4">
        <div className="backdrop-blur-xl bg-white/90 rounded-3xl shadow-2xl border border-white/30 overflow-hidden">
          {/* Card Header */}
          <div className="pt-8 pb-4 px-8 text-center" dir={isRTL ? 'rtl' : 'ltr'}>
            <h1 className="text-2xl font-bold text-[#1e3a5f]">
              {isRTL ? 'تسجيل الدخول' : 'Sign In'}
            </h1>
            <p className="text-sm text-slate-500 mt-2">
              {isRTL ? 'قم بتسجيل الدخول للوصول إلى لوحة التحكم' : 'Sign in to access your dashboard'}
            </p>
          </div>

          {/* Form Section */}
          <div className="px-8 pb-6" dir={isRTL ? 'rtl' : 'ltr'}>
            <form onSubmit={handleSubmit} className="space-y-4">
              {error && (
                <div className="p-3 text-sm text-red-600 bg-red-50 border border-red-200 rounded-xl" data-testid="login-error">
                  {error}
                </div>
              )}
              
              {/* Email Field */}
              <div className="space-y-1.5">
                <Label htmlFor="email" className={`text-sm font-medium text-slate-700 ${isRTL ? 'text-right block' : ''}`}>
                  {t('email')}
                </Label>
                <div className="relative">
                  <Mail className={`absolute top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 ${isRTL ? 'right-3' : 'left-3'}`} />
                  <Input
                    id="email"
                    type="email"
                    placeholder={isRTL ? 'أدخل بريدك الإلكتروني' : 'Enter your email'}
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    data-testid="login-email-input"
                    className={`h-11 bg-white/70 border-slate-200 focus:border-[#1e3a5f] focus:ring-[#1e3a5f]/20 rounded-xl ${isRTL ? 'pr-10 text-right' : 'pl-10'}`}
                  />
                </div>
              </div>

              {/* Password Field */}
              <div className="space-y-1.5">
                <Label htmlFor="password" className={`text-sm font-medium text-slate-700 ${isRTL ? 'text-right block' : ''}`}>
                  {t('password')}
                </Label>
                <div className="relative">
                  <Lock className={`absolute top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 ${isRTL ? 'right-3' : 'left-3'}`} />
                  <Input
                    id="password"
                    type={showPassword ? 'text' : 'password'}
                    placeholder={isRTL ? 'أدخل كلمة المرور' : 'Enter your password'}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    data-testid="login-password-input"
                    className={`h-11 bg-white/70 border-slate-200 focus:border-[#1e3a5f] focus:ring-[#1e3a5f]/20 rounded-xl ${isRTL ? 'pr-10 pl-10 text-right' : 'pl-10 pr-10'}`}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className={`absolute top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 transition-colors ${isRTL ? 'left-3' : 'right-3'}`}
                  >
                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>

              {/* Remember Me */}
              <div className={`flex items-center gap-2 ${isRTL ? 'flex-row-reverse' : ''}`}>
                <input
                  type="checkbox"
                  id="rememberMe"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                  className="w-4 h-4 text-[#1e3a5f] bg-white border-slate-300 rounded focus:ring-[#1e3a5f] focus:ring-2"
                  data-testid="remember-me-checkbox"
                />
                <Label htmlFor="rememberMe" className="text-sm text-slate-600 cursor-pointer">
                  {t('rememberMe')}
                </Label>
              </div>

              {/* Submit Button */}
              <Button 
                type="submit" 
                className="w-full h-11 bg-[#1e3a5f] hover:bg-[#152a45] text-white font-semibold rounded-xl shadow-lg shadow-[#1e3a5f]/30 hover:shadow-xl transition-all" 
                disabled={loading} 
                data-testid="login-submit-button"
              >
                {loading ? (
                  <span className="flex items-center justify-center gap-2">
                    <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                    {isRTL ? 'جاري تسجيل الدخول...' : 'Signing in...'}
                  </span>
                ) : (
                  isRTL ? 'تسجيل الدخول' : 'Sign In'
                )}
              </Button>
            </form>

            {/* Demo Credentials */}
            <div className="mt-4 p-3 bg-slate-50/80 rounded-xl border border-slate-100">
              <p className={`text-xs text-slate-400 mb-2 ${isRTL ? 'text-right' : 'text-left'}`}>
                {isRTL ? 'بيانات اختبارية' : 'Demo Credentials'}
              </p>
              <div className={`flex gap-4 text-xs ${isRTL ? 'flex-row-reverse justify-end' : ''}`}>
                <div>
                  <span className="text-slate-400">{t('email')}: </span>
                  <code className="text-[#1e3a5f] font-mono font-medium">admin@test.com</code>
                </div>
                <div>
                  <span className="text-slate-400">{t('password')}: </span>
                  <code className="text-[#1e3a5f] font-mono font-medium">admin123</code>
                </div>
              </div>
            </div>
          </div>

          {/* Customer Portal Link */}
          <div className="px-8 py-4 bg-slate-50/50 border-t border-slate-100" dir={isRTL ? 'rtl' : 'ltr'}>
            <Link 
              to="/portal" 
              className={`flex items-center justify-center gap-2 text-sm text-slate-600 hover:text-[#c9a55c] transition-colors group ${isRTL ? 'flex-row-reverse' : ''}`}
              data-testid="customer-portal-link"
            >
              <span>{isRTL ? 'هل أنت عميل؟' : 'Are you a customer?'}</span>
              <span className="font-semibold text-[#c9a55c]">{isRTL ? 'بوابة العملاء' : 'Customer Portal'}</span>
              <ArrowRight className={`w-4 h-4 text-[#c9a55c] group-hover:translate-x-1 transition-transform ${isRTL ? 'rotate-180 group-hover:-translate-x-1' : ''}`} />
            </Link>
          </div>
        </div>

        {/* Footer */}
        <p className="text-center text-sm text-white/80 mt-6 drop-shadow-md">
          © {new Date().getFullYear()} {isRTL ? 'بيان للتحقق والمطابقة' : 'Bayan for Verification and Conformity'}
        </p>
      </div>
    </div>
  );
};

export default LoginPage;
