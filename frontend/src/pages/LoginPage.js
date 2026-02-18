import React, { useState, useContext, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { useTranslation } from 'react-i18next';
import { API, AuthContext } from '@/App';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import LanguageSwitcher from '@/components/LanguageSwitcher';
import { Globe, ArrowRight, Shield, Mail, Lock, Eye, EyeOff } from 'lucide-react';

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
    <div className="min-h-screen flex" dir={isRTL ? 'rtl' : 'ltr'} data-testid="login-page">
      {/* Left Side - Background Image */}
      <div className="hidden lg:flex lg:w-1/2 xl:w-3/5 relative overflow-hidden">
        {/* Saudi Landmark Background */}
        <div 
          className="absolute inset-0 bg-cover bg-center"
          style={{
            backgroundImage: `url('https://images.pexels.com/photos/31849529/pexels-photo-31849529.jpeg?auto=compress&cs=tinysrgb&w=1920')`,
          }}
        />
        {/* Gradient Overlay */}
        <div className="absolute inset-0 bg-gradient-to-r from-[#1e3a5f]/90 via-[#1e3a5f]/70 to-transparent" />
        
        {/* Content on Image */}
        <div className="relative z-10 flex flex-col justify-between p-12 text-white">
          {/* Logo */}
          <div>
            <img 
              src="/bayan-logo.png" 
              alt="Bayan" 
              className="h-16 brightness-0 invert"
            />
          </div>
          
          {/* Middle Content */}
          <div className="max-w-lg">
            <h1 className="text-4xl xl:text-5xl font-bold mb-6 leading-tight">
              {isRTL ? 'شريكك الموثوق في رحلة التميز المؤسسي' : 'Your Trusted Partner in Organizational Excellence'}
            </h1>
            <p className="text-lg text-white/80 leading-relaxed">
              {isRTL 
                ? 'نقدم خدمات التحقق والمطابقة المعتمدة دولياً لمساعدة مؤسستك على تحقيق أعلى معايير الجودة'
                : 'We provide internationally accredited verification and conformity services to help your organization achieve the highest quality standards'}
            </p>
            
            {/* Stats */}
            <div className="flex gap-8 mt-10">
              <div>
                <div className="text-3xl font-bold text-[#c9a55c]">500+</div>
                <div className="text-sm text-white/70">{isRTL ? 'شركة معتمدة' : 'Certified Companies'}</div>
              </div>
              <div>
                <div className="text-3xl font-bold text-[#c9a55c]">15+</div>
                <div className="text-sm text-white/70">{isRTL ? 'سنوات خبرة' : 'Years Experience'}</div>
              </div>
              <div>
                <div className="text-3xl font-bold text-[#c9a55c]">99%</div>
                <div className="text-sm text-white/70">{isRTL ? 'رضا العملاء' : 'Client Satisfaction'}</div>
              </div>
            </div>
          </div>
          
          {/* Bottom - Accreditation Badge */}
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-white/10 flex items-center justify-center">
              <Shield className="w-5 h-5 text-[#c9a55c]" />
            </div>
            <div>
              <p className="text-sm font-medium">{isRTL ? 'معتمدون من الهيئة السعودية للاعتماد' : 'SAC Accredited Certification Body'}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Right Side - Login Form */}
      <div className="w-full lg:w-1/2 xl:w-2/5 flex flex-col">
        {/* Mobile Background */}
        <div 
          className="lg:hidden absolute inset-0 bg-cover bg-center opacity-10"
          style={{
            backgroundImage: `url('https://images.pexels.com/photos/31849529/pexels-photo-31849529.jpeg?auto=compress&cs=tinysrgb&w=1920')`,
          }}
        />
        
        {/* Language Switcher */}
        <div className={`absolute top-4 ${isRTL ? 'left-4' : 'right-4'} z-10`}>
          <LanguageSwitcher />
        </div>

        {/* Form Container */}
        <div className="flex-1 flex flex-col justify-center px-8 sm:px-12 lg:px-16 py-12 relative z-10">
          {/* Mobile Logo */}
          <div className="lg:hidden mb-8 text-center">
            <img 
              src="/bayan-logo.png" 
              alt="Bayan" 
              className="h-20 mx-auto"
            />
          </div>

          {/* Customer Portal Link */}
          <Link to="/portal" className="block mb-8 group">
            <div className="flex items-center justify-between p-4 rounded-xl border-2 border-[#c9a55c]/30 bg-gradient-to-r from-[#c9a55c]/5 to-[#c9a55c]/10 hover:border-[#c9a55c]/50 hover:shadow-lg transition-all">
              <div className={`flex items-center gap-3 ${isRTL ? 'flex-row-reverse' : ''}`}>
                <div className="w-10 h-10 rounded-full bg-[#c9a55c]/20 flex items-center justify-center">
                  <Globe className="w-5 h-5 text-[#c9a55c]" />
                </div>
                <div className={isRTL ? 'text-right' : 'text-left'}>
                  <p className="font-semibold text-[#1e3a5f]">
                    {isRTL ? 'بوابة العملاء' : 'Customer Portal'}
                  </p>
                  <p className="text-xs text-slate-500">
                    {isRTL ? 'تتبع طلبك أو احصل على عرض سعر' : 'Track your order or request a quote'}
                  </p>
                </div>
              </div>
              <ArrowRight className={`w-5 h-5 text-[#c9a55c] group-hover:translate-x-1 transition-transform ${isRTL ? 'rotate-180 group-hover:-translate-x-1' : ''}`} />
            </div>
          </Link>

          {/* Login Header */}
          <div className={`mb-8 ${isRTL ? 'text-right' : 'text-left'}`}>
            <h2 className="text-2xl sm:text-3xl font-bold text-[#1e3a5f] mb-2">
              {isRTL ? 'تسجيل الدخول' : 'Welcome Back'}
            </h2>
            <p className="text-slate-500">
              {isRTL ? 'قم بتسجيل الدخول للوصول إلى لوحة التحكم' : 'Sign in to access your dashboard'}
            </p>
          </div>

          {/* Login Form */}
          <form onSubmit={handleSubmit} className="space-y-5">
            {error && (
              <div className="p-4 text-sm text-red-600 bg-red-50 border border-red-200 rounded-xl" data-testid="login-error">
                {error}
              </div>
            )}
            
            {/* Email Field */}
            <div className="space-y-2">
              <Label htmlFor="email" className={`text-sm font-medium text-slate-700 ${isRTL ? 'text-right block' : ''}`}>
                {t('email')}
              </Label>
              <div className="relative">
                <Mail className={`absolute top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 ${isRTL ? 'right-4' : 'left-4'}`} />
                <Input
                  id="email"
                  type="email"
                  placeholder={isRTL ? 'أدخل بريدك الإلكتروني' : 'Enter your email'}
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  data-testid="login-email-input"
                  className={`h-12 bg-slate-50 border-slate-200 focus:border-[#1e3a5f] focus:ring-[#1e3a5f]/20 ${isRTL ? 'pr-12 text-right' : 'pl-12'}`}
                />
              </div>
            </div>

            {/* Password Field */}
            <div className="space-y-2">
              <Label htmlFor="password" className={`text-sm font-medium text-slate-700 ${isRTL ? 'text-right block' : ''}`}>
                {t('password')}
              </Label>
              <div className="relative">
                <Lock className={`absolute top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 ${isRTL ? 'right-4' : 'left-4'}`} />
                <Input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  placeholder={isRTL ? 'أدخل كلمة المرور' : 'Enter your password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  data-testid="login-password-input"
                  className={`h-12 bg-slate-50 border-slate-200 focus:border-[#1e3a5f] focus:ring-[#1e3a5f]/20 ${isRTL ? 'pr-12 pl-12 text-right' : 'pl-12 pr-12'}`}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className={`absolute top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 ${isRTL ? 'left-4' : 'right-4'}`}
                >
                  {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
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
                className="w-4 h-4 text-[#1e3a5f] bg-gray-100 border-gray-300 rounded focus:ring-[#1e3a5f] focus:ring-2"
                data-testid="remember-me-checkbox"
              />
              <Label htmlFor="rememberMe" className="text-sm text-slate-600 cursor-pointer">
                {t('rememberMe')}
              </Label>
            </div>

            {/* Submit Button */}
            <Button 
              type="submit" 
              className="w-full h-12 bg-[#1e3a5f] hover:bg-[#152a45] text-white font-semibold text-base shadow-lg shadow-[#1e3a5f]/20 hover:shadow-xl transition-all" 
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

            {/* Demo Credentials */}
            <div className="mt-6 p-4 bg-slate-50/80 backdrop-blur border border-slate-200 rounded-xl">
              <p className={`text-xs font-medium text-slate-500 mb-3 ${isRTL ? 'text-right' : 'text-left'}`}>
                {isRTL ? 'بيانات اختبارية' : 'Demo Credentials'}
              </p>
              <div className="grid grid-cols-2 gap-3 text-xs">
                <div className="bg-white p-2.5 rounded-lg border border-slate-100">
                  <span className="text-slate-400 block mb-0.5">{t('email')}</span>
                  <code className="text-[#1e3a5f] font-mono font-medium">admin@test.com</code>
                </div>
                <div className="bg-white p-2.5 rounded-lg border border-slate-100">
                  <span className="text-slate-400 block mb-0.5">{t('password')}</span>
                  <code className="text-[#1e3a5f] font-mono font-medium">admin123</code>
                </div>
              </div>
            </div>
          </form>

          {/* Footer */}
          <p className={`text-center text-sm text-slate-400 mt-8 ${isRTL ? 'text-right' : ''}`}>
            © {new Date().getFullYear()} {isRTL ? 'بيان للتحقق والمطابقة' : 'Bayan for Verification and Conformity'}
          </p>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
