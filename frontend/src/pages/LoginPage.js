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
    <div className="min-h-screen relative flex" dir={isRTL ? 'rtl' : 'ltr'} data-testid="login-page">
      {/* Full Screen Background Image */}
      <div 
        className="absolute inset-0 bg-cover bg-center bg-no-repeat"
        style={{
          backgroundImage: `url('https://static.prod-images.emergentagent.com/jobs/b2f7052b-c928-43fa-8576-4632fce854a9/images/2981159434af46d8a59e2efde0e4758a357e7cff46c8567933938f350e67d0d0.png')`,
        }}
      />
      
      {/* Gradient Overlay - Stronger on the form side */}
      <div className={`absolute inset-0 ${isRTL ? 'bg-gradient-to-l' : 'bg-gradient-to-r'} from-[#1e3a5f]/80 via-[#1e3a5f]/40 to-transparent`} />

      {/* Logo - Always Top Right Corner */}
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

      {/* Left Side - Login Form (Always on left for powerful asymmetric layout) */}
      <div className="relative z-10 w-full md:w-1/2 lg:w-[45%] min-h-screen flex flex-col justify-center ml-0">
        <div className={`px-8 md:px-12 lg:px-16 py-12 ${isRTL ? 'text-right' : 'text-left'}`}
          
          {/* Powerful Headline */}
          <div className="mb-10">
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold text-white mb-4 leading-tight">
              {isRTL ? (
                <>
                  <span className="block">مرحباً بك</span>
                  <span className="block text-[#c9a55c]">في بيان</span>
                </>
              ) : (
                <>
                  <span className="block">Welcome to</span>
                  <span className="block text-[#c9a55c]">Bayan</span>
                </>
              )}
            </h1>
            <p className="text-lg text-white/80 max-w-md">
              {isRTL 
                ? 'منصتك الموثوقة للتحقق والمطابقة في المملكة العربية السعودية'
                : 'Your trusted platform for verification and conformity in Saudi Arabia'
              }
            </p>
          </div>

          {/* Login Form */}
          <div className="backdrop-blur-md bg-white/10 rounded-2xl p-8 border border-white/20 shadow-2xl max-w-md">
            <h2 className="text-xl font-semibold text-white mb-6">
              {isRTL ? 'تسجيل الدخول' : 'Sign In'}
            </h2>
            
            <form onSubmit={handleSubmit} className="space-y-5">
              {error && (
                <div className="p-3 text-sm text-red-200 bg-red-500/30 border border-red-400/50 rounded-xl" data-testid="login-error">
                  {error}
                </div>
              )}
              
              {/* Email Field */}
              <div className="space-y-2">
                <Label htmlFor="email" className={`text-sm font-medium text-white/90 ${isRTL ? 'text-right block' : ''}`}>
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
                    className={`h-12 bg-white/10 border-white/20 text-white placeholder:text-white/40 focus:border-[#c9a55c] focus:ring-[#c9a55c]/30 rounded-xl ${isRTL ? 'pr-12 text-right' : 'pl-12'}`}
                  />
                </div>
              </div>

              {/* Password Field */}
              <div className="space-y-2">
                <Label htmlFor="password" className={`text-sm font-medium text-white/90 ${isRTL ? 'text-right block' : ''}`}>
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
                    className={`h-12 bg-white/10 border-white/20 text-white placeholder:text-white/40 focus:border-[#c9a55c] focus:ring-[#c9a55c]/30 rounded-xl ${isRTL ? 'pr-12 pl-12 text-right' : 'pl-12 pr-12'}`}
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

              {/* Submit Button */}
              <Button 
                type="submit" 
                className="w-full h-12 bg-[#c9a55c] hover:bg-[#b8954d] text-[#1e3a5f] font-bold rounded-xl shadow-lg shadow-[#c9a55c]/30 hover:shadow-xl transition-all text-base" 
                disabled={loading} 
                data-testid="login-submit-button"
              >
                {loading ? (
                  <span className="flex items-center gap-2">
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
            <div className="mt-5 p-3 bg-white/5 rounded-xl border border-white/10">
              <p className={`text-xs text-white/50 mb-2 ${isRTL ? 'text-right' : 'text-left'}`}>
                {isRTL ? 'بيانات اختبارية' : 'Demo Credentials'}
              </p>
              <div className={`flex gap-4 text-xs ${isRTL ? 'flex-row-reverse' : ''}`}>
                <div>
                  <span className="text-white/50">{t('email')}: </span>
                  <code className="text-[#c9a55c] font-mono font-medium">admin@test.com</code>
                </div>
                <div>
                  <span className="text-white/50">{t('password')}: </span>
                  <code className="text-[#c9a55c] font-mono font-medium">admin123</code>
                </div>
              </div>
            </div>
          </div>

          {/* Customer Portal Link */}
          <div className="mt-8">
            <Link 
              to="/portal" 
              className={`inline-flex items-center gap-2 text-white/80 hover:text-[#c9a55c] transition-colors group ${isRTL ? 'flex-row-reverse' : ''}`}
              data-testid="customer-portal-link"
            >
              <span>{isRTL ? 'هل أنت عميل؟' : 'Are you a customer?'}</span>
              <span className="font-semibold text-[#c9a55c]">{isRTL ? 'بوابة العملاء' : 'Customer Portal'}</span>
              <ArrowRight className={`w-4 h-4 text-[#c9a55c] group-hover:translate-x-1 transition-transform ${isRTL ? 'rotate-180 group-hover:-translate-x-1' : ''}`} />
            </Link>
          </div>

          {/* Footer */}
          <p className="text-sm text-white/50 mt-12">
            © {new Date().getFullYear()} {isRTL ? 'بيان للتحقق والمطابقة' : 'Bayan for Verification and Conformity'}
          </p>
        </div>
      </div>

      {/* Right Side - Empty to show the beautiful desert image */}
      <div className="hidden md:block md:w-1/2 lg:w-[55%]" />
    </div>
  );
};

export default LoginPage;
