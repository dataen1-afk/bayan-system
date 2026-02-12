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
      </div>
    </div>
  );
};

export default LoginPage;
