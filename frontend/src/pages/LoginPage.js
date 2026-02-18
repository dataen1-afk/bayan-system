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
    <div className="min-h-screen relative" data-testid="login-page">
      {/* Full Screen Background Image */}
      <div 
        className="absolute inset-0 bg-cover bg-center bg-no-repeat"
        style={{
          backgroundImage: `url('https://static.prod-images.emergentagent.com/jobs/b2f7052b-c928-43fa-8576-4632fce854a9/images/2981159434af46d8a59e2efde0e4758a357e7cff46c8567933938f350e67d0d0.png')`,
        }}
      />
      
      {/* Dark overlay for depth */}
      <div className="absolute inset-0 bg-[#1e3a5f]/30" />

      {/* Logo - Top Right Corner - ENLARGED & WHITE */}
      <div className="absolute top-6 right-6 z-20">
        <img 
          src="/bayan-logo.png" 
          alt="Bayan for Verification and Conformity" 
          className="h-20 md:h-24 lg:h-28 drop-shadow-2xl brightness-0 invert"
        />
      </div>

      {/* Language Switcher - Top Left */}
      <div className="absolute top-6 left-6 z-20">
        <LanguageSwitcher />
      </div>

      {/* Powerful Text - Far Right (Clear of login card) */}
      <div className="hidden lg:flex absolute right-0 top-0 bottom-0 w-[35%] items-center justify-end pr-16 z-0">
        <div className="max-w-md text-right" dir="rtl">
          <h2 className="text-4xl xl:text-5xl font-bold text-white mb-6 leading-tight drop-shadow-lg">
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
          <p className="text-lg xl:text-xl text-white/90 drop-shadow-md leading-relaxed">
            {isRTL 
              ? 'نقدم خدمات التحقق والمطابقة المعتمدة دولياً لمساعدة مؤسستك على تحقيق أعلى معايير الجودة'
              : 'We provide internationally accredited verification and conformity services to help your organization achieve the highest quality standards'
            }
          </p>
        </div>
      </div>

      {/* Login Card - Centered */}
      <div className="absolute inset-0 flex items-center justify-center p-4 z-10">
        <div className="w-full max-w-md">
          <div className="backdrop-blur-xl bg-[#1e3a5f]/40 rounded-3xl shadow-2xl border border-white/20 overflow-hidden">
            {/* Card Header */}
            <div className="pt-8 pb-4 px-8 text-center" dir={isRTL ? 'rtl' : 'ltr'}>
              <h1 className="text-2xl font-bold text-white">
                {isRTL ? 'تسجيل الدخول' : 'Sign In'}
              </h1>
              <p className="text-sm text-white/70 mt-2">
                {isRTL ? 'قم بتسجيل الدخول للوصول إلى لوحة التحكم' : 'Sign in to access your dashboard'}
              </p>
            </div>

            {/* Form Section */}
            <div className="px-8 pb-6" dir={isRTL ? 'rtl' : 'ltr'}>
              <form onSubmit={handleSubmit} className="space-y-5">
                {error && (
                  <div className="p-3 text-sm text-red-200 bg-red-500/30 border border-red-400/50 rounded-xl" data-testid="login-error">
                    {error}
                  </div>
                )}
                
                {/* Email Field */}
                <div className="space-y-2">
                  <Label htmlFor="email" className={`text-sm font-medium text-white ${isRTL ? 'text-right block' : ''}`}>
                    {t('email')}
                  </Label>
                  <div className="relative">
                    <Mail className={`absolute top-1/2 -translate-y-1/2 w-5 h-5 text-white/50 ${isRTL ? 'right-4' : 'left-4'}`} />
                    <Input
                      id="email"
                      type="email"
                      placeholder={isRTL ? 'أدخل بريدك الإلكتروني' : 'Enter your email'}
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      required
                      data-testid="login-email-input"
                      className={`h-12 bg-white/10 border-white/30 text-white placeholder:text-white/40 focus:border-[#c9a55c] focus:ring-[#c9a55c]/30 rounded-xl ${isRTL ? 'pr-12 text-right' : 'pl-12'}`}
                    />
                  </div>
                </div>

                {/* Password Field */}
                <div className="space-y-2">
                  <Label htmlFor="password" className={`text-sm font-medium text-white ${isRTL ? 'text-right block' : ''}`}>
                    {t('password')}
                  </Label>
                  <div className="relative">
                    <Lock className={`absolute top-1/2 -translate-y-1/2 w-5 h-5 text-white/50 ${isRTL ? 'right-4' : 'left-4'}`} />
                    <Input
                      id="password"
                      type={showPassword ? 'text' : 'password'}
                      placeholder={isRTL ? 'أدخل كلمة المرور' : 'Enter your password'}
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      required
                      data-testid="login-password-input"
                      className={`h-12 bg-white/10 border-white/30 text-white placeholder:text-white/40 focus:border-[#c9a55c] focus:ring-[#c9a55c]/30 rounded-xl ${isRTL ? 'pr-12 pl-12 text-right' : 'pl-12 pr-12'}`}
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className={`absolute top-1/2 -translate-y-1/2 text-white/50 hover:text-white transition-colors ${isRTL ? 'left-4' : 'right-4'}`}
                    >
                      {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                    </button>
                  </div>
                </div>

                {/* Remember Me */}
                <div className={`flex items-center gap-3 ${isRTL ? 'flex-row-reverse' : ''}`}>
                  <input
                    type="checkbox"
                    id="rememberMe"
                    checked={rememberMe}
                    onChange={(e) => setRememberMe(e.target.checked)}
                    className="w-4 h-4 text-[#c9a55c] bg-white/10 border-white/30 rounded focus:ring-[#c9a55c] focus:ring-2"
                    data-testid="remember-me-checkbox"
                  />
                  <Label htmlFor="rememberMe" className="text-sm text-white/80 cursor-pointer">
                    {t('rememberMe')}
                  </Label>
                </div>

                {/* Submit Button - Gold/Amber */}
                <Button 
                  type="submit" 
                  className="w-full h-12 bg-[#c9a55c] hover:bg-[#b8954d] text-[#1e3a5f] font-bold rounded-xl shadow-lg shadow-[#c9a55c]/30 hover:shadow-xl transition-all text-base" 
                  disabled={loading} 
                  data-testid="login-submit-button"
                >
                  {loading ? (
                    <span className="flex items-center justify-center gap-2">
                      <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
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
              <div className="mt-5 p-4 bg-white/5 rounded-xl border border-white/10">
                <p className={`text-xs text-white/50 mb-2 ${isRTL ? 'text-right' : 'text-left'}`}>
                  {isRTL ? 'بيانات اختبارية' : 'Demo Credentials'}
                </p>
                <div className={`flex gap-6 text-sm ${isRTL ? 'flex-row-reverse justify-end' : ''}`}>
                  <div>
                    <span className="text-white/50">{t('password')}: </span>
                    <code className="text-[#c9a55c] font-mono font-medium">admin123</code>
                  </div>
                  <div>
                    <span className="text-white/50">{t('email')}: </span>
                    <code className="text-[#c9a55c] font-mono font-medium">admin@test.com</code>
                  </div>
                </div>
              </div>
            </div>

            {/* Customer Portal Link */}
            <div className="px-8 py-4 bg-white/5 border-t border-white/10" dir={isRTL ? 'rtl' : 'ltr'}>
              <Link 
                to="/portal" 
                className={`flex items-center justify-center gap-2 text-sm text-white/70 hover:text-[#c9a55c] transition-colors group ${isRTL ? 'flex-row-reverse' : ''}`}
                data-testid="customer-portal-link"
              >
                <span>{isRTL ? 'هل أنت عميل؟' : 'Are you a customer?'}</span>
                <span className="font-semibold text-[#c9a55c]">{isRTL ? 'بوابة العملاء' : 'Customer Portal'}</span>
                <ArrowRight className={`w-4 h-4 text-[#c9a55c] group-hover:translate-x-1 transition-transform ${isRTL ? 'rotate-180 group-hover:-translate-x-1' : ''}`} />
              </Link>
            </div>
          </div>

          {/* Footer below card */}
          <p className="text-center text-sm text-white/70 mt-6 drop-shadow-md">
            © {new Date().getFullYear()} {isRTL ? 'بيان للتحقق والمطابقة' : 'Bayan for Verification and Conformity'}
          </p>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
