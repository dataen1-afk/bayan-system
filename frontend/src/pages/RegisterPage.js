import React, { useState, useContext } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { useTranslation } from 'react-i18next';
import { API, AuthContext } from '@/App';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import LanguageSwitcher from '@/components/LanguageSwitcher';

const RegisterPage = () => {
  const { t } = useTranslation();
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    role: 'client'
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useContext(AuthContext);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      // Register user
      await axios.post(`${API}/auth/register`, formData);
      
      // Auto login after registration
      const loginResponse = await axios.post(`${API}/auth/login`, {
        email: formData.email,
        password: formData.password
      });
      
      login(loginResponse.data.token, loginResponse.data.user);
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.detail || t('errorRegister'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100" data-testid="register-page">
      <div className="absolute top-4 right-4">
        <LanguageSwitcher />
      </div>
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle className="text-2xl font-bold" data-testid="register-title">{t('register')}</CardTitle>
          <CardDescription>{t('createNewAccount')}</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <div className="p-3 text-sm text-red-600 bg-red-50 border border-red-200 rounded" data-testid="register-error">
                {error}
              </div>
            )}
            
            <div className="space-y-2">
              <Label htmlFor="name">{t('fullName')}</Label>
              <Input
                id="name"
                type="text"
                placeholder="John Doe"
                value={formData.name}
                onChange={(e) => setFormData({...formData, name: e.target.value})}
                required
                data-testid="register-name-input"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="email">{t('email')}</Label>
              <Input
                id="email"
                type="email"
                placeholder="you@example.com"
                value={formData.email}
                onChange={(e) => setFormData({...formData, email: e.target.value})}
                required
                data-testid="register-email-input"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="password">{t('password')}</Label>
              <Input
                id="password"
                type="password"
                placeholder="••••••••"
                value={formData.password}
                onChange={(e) => setFormData({...formData, password: e.target.value})}
                required
                minLength={6}
                data-testid="register-password-input"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="role">{t('role')}</Label>
              <Select value={formData.role} onValueChange={(value) => setFormData({...formData, role: value})}>
                <SelectTrigger data-testid="register-role-select">
                  <SelectValue placeholder={t('role')} />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="client">{t('client')}</SelectItem>
                  <SelectItem value="admin">{t('admin')}</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <Button type="submit" className="w-full" disabled={loading} data-testid="register-submit-button">
              {loading ? t('creatingAccount') : t('createAccount')}
            </Button>

            <p className="text-sm text-center text-gray-600">
              {t('alreadyHaveAccount')}{' '}
              <Link to="/login" className="text-blue-600 hover:underline" data-testid="login-link">
                {t('loginHere')}
              </Link>
            </p>
          </form>
        </CardContent>
      </Card>
    </div>
  );
};

export default RegisterPage;
