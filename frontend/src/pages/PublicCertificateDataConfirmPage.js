import React, { useState, useEffect, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import axios from 'axios';
import {
  Building2,
  CheckCircle,
  AlertCircle,
  FileCheck,
  Loader2,
  Calendar,
  User,
  Tag,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { toast } from 'sonner';
import SignaturePad from '@/components/SignaturePad';
import LanguageSwitcher from '@/components/LanguageSwitcher';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function PublicCertificateDataConfirmPage() {
  const { accessToken } = useParams();
  const { t, i18n } = useTranslation();
  const isRTL = i18n.language === 'ar';

  const [record, setRecord] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [signatureDate, setSignatureDate] = useState(() => {
    const d = new Date();
    return d.toISOString().slice(0, 10);
  });
  const [signatureData, setSignatureData] = useState(null);
  const [stampData, setStampData] = useState(null);

  const fetchRecord = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get(
        `${API_URL}/api/public/certificate-data/${accessToken}`
      );
      setRecord(response.data);
    } catch (err) {
      const status = err.response?.status;
      const detail = err.response?.data?.detail;
      if (status === 404) {
        setError(t('certDataConfirm.notFound'));
      } else if (status === 400) {
        setError(detail || t('certDataConfirm.notAvailable'));
      } else {
        setError(detail || t('certDataConfirm.loadError'));
      }
      setRecord(null);
    } finally {
      setLoading(false);
    }
  }, [accessToken, t]);

  useEffect(() => {
    fetchRecord();
  }, [fetchRecord]);

  const alreadyConfirmed = record?.status === 'client_confirmed';
  const canSubmit = record?.status === 'sent_to_client' && !success;

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!canSubmit) return;

    if (!signatureData) {
      toast.error(t('certDataConfirm.signatureRequired'));
      return;
    }
    if (!stampData) {
      toast.error(t('certDataConfirm.stampRequired'));
      return;
    }
    if (!signatureDate?.trim()) {
      toast.error(t('certDataConfirm.dateRequired'));
      return;
    }

    setSubmitting(true);
    try {
      await axios.post(
        `${API_URL}/api/public/certificate-data/${accessToken}/confirm`,
        {
          client_signature: signatureData,
          client_stamp: stampData,
          signature_date: signatureDate,
        }
      );
      setSuccess(true);
      toast.success(t('certDataConfirm.submitSuccess'));
      setRecord((prev) =>
        prev
          ? {
              ...prev,
              status: 'client_confirmed',
              client_confirmed: true,
              client_signature_date: signatureDate,
            }
          : prev
      );
    } catch (err) {
      const detail = err.response?.data?.detail;
      toast.error(detail || t('certDataConfirm.submitError'));
    } finally {
      setSubmitting(false);
    }
  };

  const renderField = (label, value, options = {}) => (
    <div className={options.fullWidth ? 'md:col-span-2' : ''}>
      <div className="text-xs font-medium text-gray-500 mb-1">{label}</div>
      <div
        className={`text-sm text-gray-900 whitespace-pre-wrap ${isRTL ? 'text-right' : 'text-left'}`}
        dir={options.rtl ? 'rtl' : undefined}
      >
        {value != null && value !== '' ? value : '—'}
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 flex flex-col">
        <PublicHeader isRTL={isRTL} />
        <div className="flex-1 flex items-center justify-center p-8">
          <div className="flex flex-col items-center gap-3 text-gray-600">
            <Loader2 className="w-10 h-10 animate-spin text-teal-600" />
            <p>{t('certDataConfirm.loading')}</p>
          </div>
        </div>
      </div>
    );
  }

  if (error && !record) {
    return (
      <div className="min-h-screen bg-slate-50 flex flex-col">
        <PublicHeader isRTL={isRTL} />
        <div className="flex-1 flex items-center justify-center p-8">
          <Card className="max-w-md w-full border-red-200">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-red-700">
                <AlertCircle className="w-5 h-5 shrink-0" />
                {t('certDataConfirm.errorTitle')}
              </CardTitle>
              <CardDescription className="text-red-600/90">{error}</CardDescription>
            </CardHeader>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className={`min-h-screen bg-slate-50 ${isRTL ? 'rtl' : 'ltr'}`} dir={isRTL ? 'rtl' : 'ltr'}>
      <PublicHeader isRTL={isRTL} />

      <main className="max-w-3xl mx-auto px-4 py-8 pb-16">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <FileCheck className="w-8 h-8 text-teal-600" />
            {t('certDataConfirm.pageTitle')}
          </h1>
          <p className="text-gray-600 mt-1">{t('certDataConfirm.pageSubtitle')}</p>
        </div>

        {(success || alreadyConfirmed) && (
          <Card className="mb-6 border-green-200 bg-green-50/80">
            <CardContent className="pt-6 flex items-start gap-3">
              <CheckCircle className="w-6 h-6 text-green-600 shrink-0 mt-0.5" />
              <div>
                <p className="font-semibold text-green-900">
                  {alreadyConfirmed && !success
                    ? t('certDataConfirm.alreadyConfirmedTitle')
                    : t('certDataConfirm.successTitle')}
                </p>
                <p className="text-sm text-green-800 mt-1">
                  {alreadyConfirmed && !success
                    ? t('certDataConfirm.alreadyConfirmedBody')
                    : t('certDataConfirm.successBody')}
                </p>
              </div>
            </CardContent>
          </Card>
        )}

        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-lg">
              <Building2 className="w-5 h-5 text-teal-600" />
              {t('certDataConfirm.detailsTitle')}
            </CardTitle>
            <CardDescription>{t('certDataConfirm.detailsHint')}</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {renderField(t('certData.clientName'), record?.client_name)}
              {renderField(t('certData.standards'), record?.standards?.join(', '))}
              {renderField(t('certData.leadAuditor'), record?.lead_auditor)}
              {renderField(t('certData.auditType'), record?.audit_type)}
              {renderField(t('certData.date'), record?.audit_date)}
              {renderField(t('certData.eaCode'), record?.ea_code)}
              {renderField(t('certData.agreedScope'), record?.agreed_certification_scope, {
                fullWidth: true,
              })}
              {renderField(t('certData.companyDataLocal'), record?.company_data_local, {
                fullWidth: true,
                rtl: true,
              })}
              {renderField(t('certData.scopeField'), record?.certification_scope_local, {
                fullWidth: true,
                rtl: true,
              })}
              {renderField(t('certData.companyDataField'), record?.company_data_english, {
                fullWidth: true,
              })}
              {renderField(t('certData.scopeField'), record?.certification_scope_english, {
                fullWidth: true,
              })}
            </div>
          </CardContent>
        </Card>

        {canSubmit && (
          <form onSubmit={handleSubmit} className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-lg">
                  <Calendar className="w-5 h-5 text-teal-600" />
                  {t('certDataConfirm.dateSection')}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 max-w-xs">
                  <Label htmlFor="signature_date">{t('certDataConfirm.signatureDateLabel')}</Label>
                  <Input
                    id="signature_date"
                    type="date"
                    value={signatureDate}
                    onChange={(e) => setSignatureDate(e.target.value)}
                    required
                    data-testid="cert-data-signature-date"
                  />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-lg">
                  <Tag className="w-5 h-5 text-teal-600" />
                  {t('certDataConfirm.signatureSection')}
                </CardTitle>
                <CardDescription>{t('certDataConfirm.signatureHint')}</CardDescription>
              </CardHeader>
              <CardContent>
                <SignaturePad
                  onSignatureChange={setSignatureData}
                  onStampChange={setStampData}
                  showStamp
                />
              </CardContent>
            </Card>

            <div className="flex justify-center">
              <Button
                type="submit"
                size="lg"
                disabled={submitting}
                className="min-w-[200px] bg-teal-600 hover:bg-teal-700"
                data-testid="cert-data-confirm-submit"
              >
                {submitting ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    {t('certDataConfirm.submitting')}
                  </>
                ) : (
                  <>
                    <User className="w-4 h-4 mr-2" />
                    {t('certDataConfirm.submit')}
                  </>
                )}
              </Button>
            </div>
          </form>
        )}
      </main>
    </div>
  );
}

function PublicHeader({ isRTL }) {
  return (
    <header className="bg-white border-b border-gray-200 shadow-sm">
      <div className="max-w-3xl mx-auto px-4 py-3 flex items-center justify-between gap-4">
        <img
          src="/Bayan-removebg-preview.png"
          alt="Bayan"
          className="h-12 w-auto object-contain"
        />
        <div className={isRTL ? 'flex-row-reverse' : ''}>
          <LanguageSwitcher />
        </div>
      </div>
      <div className="h-1 bg-gradient-to-r from-teal-700 via-teal-500 to-teal-700" />
    </header>
  );
}
