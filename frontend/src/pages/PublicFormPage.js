import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { CheckCircle, AlertCircle, Loader2 } from 'lucide-react';
import LanguageSwitcher from '@/components/LanguageSwitcher';
import ApplicationForm from '@/components/ApplicationForm';

const API = process.env.REACT_APP_BACKEND_URL + '/api';

const PublicFormPage = () => {
  const { accessToken } = useParams();
  const { t, i18n } = useTranslation();
  const isRTL = i18n.language?.startsWith('ar');
  
  const [form, setForm] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [submitted, setSubmitted] = useState(false);

  useEffect(() => {
    loadForm();
  }, [accessToken]);

  const loadForm = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await axios.get(`${API}/public/form/${accessToken}`);
      setForm(response.data);
      if (response.data.status === 'submitted') {
        setSubmitted(true);
      }
    } catch (error) {
      console.error('Error loading form:', error);
      if (error.response?.status === 404) {
        setError('formNotFound');
      } else {
        setError('errorLoadingForm');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSaveDraft = async (formData) => {
    try {
      await axios.put(`${API}/public/form/${accessToken}`, {
        company_data: formData
      });
      alert(t('draftSaved'));
      loadForm();
    } catch (error) {
      alert(t('errorSavingDraft') + ' ' + (error.response?.data?.detail || error.message));
    }
  };

  const handleSubmit = async (formData) => {
    try {
      await axios.post(`${API}/public/form/${accessToken}/submit`, {
        company_data: formData
      });
      setSubmitted(true);
    } catch (error) {
      alert(t('errorSubmittingApplication') + ' ' + (error.response?.data?.detail || error.message));
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin text-bayan-navy mx-auto mb-4" />
          <p className="text-gray-600">{t('loadingForm')}</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <Card className="w-full max-w-md">
          <CardContent className="pt-6">
            <div className="text-center">
              <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
              <h2 className="text-xl font-bold text-gray-800 mb-2">{t(error)}</h2>
              <p className="text-gray-600">{t('formLinkInvalidOrExpired')}</p>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (submitted) {
    return (
      <div className="min-h-screen bg-gray-50" dir={isRTL ? 'rtl' : 'ltr'}>
        {/* Header */}
        <header className="bg-white shadow-sm border-b fixed top-0 left-0 right-0 z-50">
          <div className="dashboard-header max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
            <div className="dashboard-header-left flex items-center gap-4">
              <img src="/Bayan-removebg-preview.png" alt="Bayan" className="h-16 w-auto object-contain" />
            </div>
            <div className="dashboard-header-right">
              <LanguageSwitcher />
            </div>
          </div>
          <div className="h-1.5 bg-gradient-to-r from-bayan-navy via-bayan-navy-light to-bayan-navy"></div>
        </header>

        <main className="pt-28 pb-12 px-4">
          <div className="max-w-2xl mx-auto">
            <Card>
              <CardContent className="pt-8 pb-8">
                <div className="text-center">
                  <CheckCircle className="w-20 h-20 text-green-500 mx-auto mb-6" />
                  <h2 className="text-2xl font-bold text-gray-800 mb-4">{t('applicationSubmittedSuccess')}</h2>
                  <p className="text-gray-600 mb-6">{t('thankYouForSubmitting')}</p>
                  <div className="bg-green-50 border border-green-200 rounded-lg p-4 max-w-md mx-auto">
                    <p className="text-sm text-green-800">
                      {t('applicationSubmittedMessage')}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50" dir={isRTL ? 'rtl' : 'ltr'}>
      {/* Header */}
      <header className="bg-white shadow-sm border-b fixed top-0 left-0 right-0 z-50">
        <div className="dashboard-header max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="dashboard-header-left flex items-center gap-4">
            <img src="/Bayan-removebg-preview.png" alt="Bayan" className="h-16 w-auto object-contain" />
          </div>
          <div className="dashboard-header-right">
            <LanguageSwitcher />
          </div>
        </div>
        <div className="h-1.5 bg-gradient-to-r from-bayan-navy via-bayan-navy-light to-bayan-navy"></div>
      </header>

      <main className="pt-28 pb-12 px-4">
        <div className="max-w-5xl mx-auto">
          {/* Welcome Card */}
          <Card className="mb-6">
            <CardHeader className={isRTL ? 'text-right' : 'text-left'}>
              <CardTitle className="text-bayan-navy">{t('welcomeToApplicationForm')}</CardTitle>
              <CardDescription>
                {t('formForCompany')}: <span className="font-semibold">{form?.client_info?.company_name}</span>
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className={`grid grid-cols-1 md:grid-cols-2 gap-4 text-sm ${isRTL ? 'text-right' : 'text-left'}`}>
                <div>
                  <span className="font-medium text-gray-700">{t('clientName')}:</span>{' '}
                  <span className="text-gray-600">{form?.client_info?.name}</span>
                </div>
                <div>
                  <span className="font-medium text-gray-700">{t('email')}:</span>{' '}
                  <span className="text-gray-600">{form?.client_info?.email}</span>
                </div>
                <div>
                  <span className="font-medium text-gray-700">{t('phone')}:</span>{' '}
                  <span className="text-gray-600">{form?.client_info?.phone}</span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Application Form */}
          <ApplicationForm 
            initialData={form?.company_data}
            onSubmit={handleSubmit}
            onSaveDraft={handleSaveDraft}
          />
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-bayan-navy text-white py-6 mt-12">
        <div className="max-w-7xl mx-auto px-4 text-center">
          <p className="text-sm opacity-80">
            © {new Date().getFullYear()} {t('bayanAuditingConformity')}. {t('allRightsReserved')}
          </p>
        </div>
      </footer>
    </div>
  );
};

export default PublicFormPage;
