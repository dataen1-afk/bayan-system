import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useParams, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Checkbox } from '@/components/ui/checkbox';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion';
import LanguageSwitcher from '@/components/LanguageSwitcher';
import { 
  Search, CheckCircle, Clock, FileText, DollarSign, FileCheck, 
  Loader2, AlertCircle, Building2, Mail, Phone, MapPin,
  Calendar, Download, Eye, Shield, Leaf, Users, Utensils,
  Lock, Award, ArrowRight, Send, HelpCircle, ChevronDown,
  Globe, Target, Briefcase, Star, CheckCircle2
} from 'lucide-react';
import { toast } from 'sonner';

const API = process.env.REACT_APP_BACKEND_URL + '/api';

// Format date
const formatDate = (dateString) => {
  if (!dateString) return '-';
  return new Date(dateString).toLocaleDateString('en-GB', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  });
};

// Format currency
const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-US', { 
    minimumFractionDigits: 0,
    maximumFractionDigits: 0 
  }).format(amount || 0) + ' SAR';
};

const CustomerPortalPage = () => {
  const { trackingId } = useParams();
  const navigate = useNavigate();
  const { t, i18n } = useTranslation();
  const isRTL = i18n.language?.startsWith('ar');
  
  // Tracking state
  const [searchId, setSearchId] = useState(trackingId || '');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [orderData, setOrderData] = useState(null);
  const [searched, setSearched] = useState(false);
  
  // RFQ Form state
  const [rfqForm, setRfqForm] = useState({
    company_name: '',
    contact_name: '',
    email: '',
    phone: '',
    employees: '',
    sites: '1',
    standards: [],
    message: ''
  });
  const [rfqSubmitting, setRfqSubmitting] = useState(false);
  const [rfqSubmitted, setRfqSubmitted] = useState(false);

  // Contact form state
  const [contactForm, setContactForm] = useState({
    name: '',
    email: '',
    subject: '',
    message: ''
  });
  const [contactSubmitting, setContactSubmitting] = useState(false);

  useEffect(() => {
    if (trackingId) {
      handleSearch();
    }
  }, [trackingId]);

  const handleSearch = async () => {
    if (!searchId.trim()) {
      setError(isRTL ? 'الرجاء إدخال رقم التتبع' : 'Please enter a tracking ID');
      return;
    }
    
    setLoading(true);
    setError('');
    setSearched(true);
    
    try {
      const response = await axios.get(`${API}/public/track/${searchId.trim()}`);
      setOrderData(response.data);
    } catch (err) {
      if (err.response?.status === 404) {
        setError(isRTL ? 'لم يتم العثور على الطلب' : 'Order not found');
      } else {
        setError(isRTL ? 'خطأ في تتبع الطلب' : 'Error tracking order');
      }
      setOrderData(null);
    } finally {
      setLoading(false);
    }
  };

  const handleRfqSubmit = async (e) => {
    e.preventDefault();
    if (rfqForm.standards.length === 0) {
      toast.error(isRTL ? 'الرجاء اختيار معيار واحد على الأقل' : 'Please select at least one standard');
      return;
    }
    
    setRfqSubmitting(true);
    try {
      await axios.post(`${API}/public/rfq`, rfqForm);
      setRfqSubmitted(true);
      toast.success(isRTL ? 'تم إرسال طلبك بنجاح' : 'Your request has been submitted successfully');
    } catch (err) {
      toast.error(isRTL ? 'خطأ في إرسال الطلب' : 'Error submitting request');
    } finally {
      setRfqSubmitting(false);
    }
  };

  const handleContactSubmit = async (e) => {
    e.preventDefault();
    setContactSubmitting(true);
    try {
      await axios.post(`${API}/public/contact`, contactForm);
      toast.success(isRTL ? 'تم إرسال رسالتك' : 'Your message has been sent');
      setContactForm({ name: '', email: '', subject: '', message: '' });
    } catch (err) {
      toast.error(isRTL ? 'خطأ في إرسال الرسالة' : 'Error sending message');
    } finally {
      setContactSubmitting(false);
    }
  };

  const toggleStandard = (std) => {
    setRfqForm(prev => ({
      ...prev,
      standards: prev.standards.includes(std)
        ? prev.standards.filter(s => s !== std)
        : [...prev.standards, std]
    }));
  };

  // Services data
  const services = [
    {
      id: 'iso9001',
      icon: Award,
      title: isRTL ? 'ISO 9001:2015' : 'ISO 9001:2015',
      subtitle: isRTL ? 'نظام إدارة الجودة' : 'Quality Management System',
      description: isRTL 
        ? 'يساعد على تحسين جودة المنتجات والخدمات وزيادة رضا العملاء'
        : 'Helps improve product and service quality while increasing customer satisfaction',
      color: 'blue'
    },
    {
      id: 'iso14001',
      icon: Leaf,
      title: isRTL ? 'ISO 14001:2015' : 'ISO 14001:2015',
      subtitle: isRTL ? 'نظام الإدارة البيئية' : 'Environmental Management System',
      description: isRTL 
        ? 'يدعم الاستدامة البيئية ويقلل من الأثر البيئي لمؤسستك'
        : 'Supports environmental sustainability and reduces your organization\'s environmental impact',
      color: 'green'
    },
    {
      id: 'iso45001',
      icon: Shield,
      title: isRTL ? 'ISO 45001:2018' : 'ISO 45001:2018',
      subtitle: isRTL ? 'نظام إدارة الصحة والسلامة المهنية' : 'Occupational Health & Safety',
      description: isRTL 
        ? 'يوفر بيئة عمل آمنة وصحية لموظفيك وأصحاب المصلحة'
        : 'Provides a safe and healthy work environment for your employees and stakeholders',
      color: 'orange'
    },
    {
      id: 'iso22000',
      icon: Utensils,
      title: isRTL ? 'ISO 22000:2018' : 'ISO 22000:2018',
      subtitle: isRTL ? 'نظام إدارة سلامة الغذاء' : 'Food Safety Management System',
      description: isRTL 
        ? 'يضمن سلامة الغذاء عبر سلسلة التوريد بأكملها'
        : 'Ensures food safety throughout the entire supply chain',
      color: 'red'
    },
    {
      id: 'iso27001',
      icon: Lock,
      title: isRTL ? 'ISO 27001:2022' : 'ISO 27001:2022',
      subtitle: isRTL ? 'نظام إدارة أمن المعلومات' : 'Information Security Management',
      description: isRTL 
        ? 'يحمي بيانات مؤسستك ومعلومات عملائك الحساسة'
        : 'Protects your organization\'s data and sensitive customer information',
      color: 'purple'
    }
  ];

  // FAQ data
  const faqs = [
    {
      question: isRTL ? 'ما هي مدة عملية الشهادة؟' : 'How long does the certification process take?',
      answer: isRTL 
        ? 'تستغرق عملية الشهادة عادةً من 2 إلى 4 أشهر، اعتمادًا على حجم المؤسسة ومدى جاهزيتها. تشمل العملية مراجعة الوثائق، والتدقيق في الموقع، وإصدار الشهادة.'
        : 'The certification process typically takes 2-4 months, depending on organization size and readiness. The process includes document review, on-site audit, and certificate issuance.'
    },
    {
      question: isRTL ? 'ما هي تكلفة الحصول على الشهادة؟' : 'What is the cost of certification?',
      answer: isRTL 
        ? 'تختلف التكلفة بناءً على حجم المؤسسة، عدد المواقع، ونطاق الشهادة المطلوبة. نقدم عروض أسعار مجانية ومخصصة. تواصل معنا للحصول على تقدير دقيق.'
        : 'Costs vary based on organization size, number of sites, and certification scope. We provide free, customized quotes. Contact us for an accurate estimate.'
    },
    {
      question: isRTL ? 'ما هي مدة صلاحية الشهادة؟' : 'How long is the certificate valid?',
      answer: isRTL 
        ? 'الشهادة صالحة لمدة 3 سنوات، مع تدقيقات مراقبة سنوية للحفاظ على الشهادة. بعد 3 سنوات، يتم إجراء تدقيق إعادة الشهادة.'
        : 'The certificate is valid for 3 years, with annual surveillance audits to maintain certification. After 3 years, a recertification audit is conducted.'
    },
    {
      question: isRTL ? 'هل يمكن الحصول على شهادات متعددة؟' : 'Can we obtain multiple certifications?',
      answer: isRTL 
        ? 'نعم، يمكن الحصول على شهادات متعددة (نظام إدارة متكامل). يمكن دمج التدقيقات لتقليل الوقت والتكلفة.'
        : 'Yes, you can obtain multiple certifications (Integrated Management System). Audits can be combined to reduce time and cost.'
    },
    {
      question: isRTL ? 'ما المطلوب للتحضير للتدقيق؟' : 'What is required to prepare for an audit?',
      answer: isRTL 
        ? 'يجب توثيق العمليات والإجراءات، تدريب الموظفين، إجراء تدقيقات داخلية، ومراجعة الإدارة. سنوفر لك قائمة مرجعية كاملة.'
        : 'You need to document processes and procedures, train employees, conduct internal audits, and perform management review. We will provide you with a complete checklist.'
    },
    {
      question: isRTL ? 'ما هو نطاق اعتماد بيان؟' : 'What is Bayan\'s accreditation scope?',
      answer: isRTL 
        ? 'بيان معتمدة من الهيئة السعودية للاعتماد (ساك) لإصدار شهادات ISO 9001، ISO 14001، ISO 45001، ISO 22000، و ISO 27001.'
        : 'Bayan is accredited by the Saudi Accreditation Center (SAC) to issue ISO 9001, ISO 14001, ISO 45001, ISO 22000, and ISO 27001 certifications.'
    }
  ];

  // Timeline steps
  const timelineSteps = [
    { key: 'pending', label: isRTL ? 'تم إنشاء النموذج' : 'Form Created', icon: FileText },
    { key: 'submitted', label: isRTL ? 'تم تقديم النموذج' : 'Form Submitted', icon: CheckCircle },
    { key: 'under_review', label: isRTL ? 'قيد المراجعة' : 'Under Review', icon: Clock },
    { key: 'accepted', label: isRTL ? 'تم قبول العرض' : 'Proposal Accepted', icon: DollarSign },
    { key: 'agreement_signed', label: isRTL ? 'تم توقيع الاتفاقية' : 'Agreement Signed', icon: FileCheck },
    { key: 'contract_generated', label: isRTL ? 'العقد جاهز' : 'Contract Ready', icon: Download }
  ];

  const getStatusStep = (status) => {
    const steps = ['pending', 'submitted', 'under_review', 'accepted', 'agreement_signed', 'contract_generated'];
    return steps.indexOf(status);
  };

  const colorClasses = {
    blue: 'bg-blue-50 border-blue-200 text-blue-700',
    green: 'bg-green-50 border-green-200 text-green-700',
    orange: 'bg-orange-50 border-orange-200 text-orange-700',
    red: 'bg-red-50 border-red-200 text-red-700',
    purple: 'bg-purple-50 border-purple-200 text-purple-700'
  };

  const iconBgClasses = {
    blue: 'bg-blue-100 text-blue-600',
    green: 'bg-green-100 text-green-600',
    orange: 'bg-orange-100 text-orange-600',
    red: 'bg-red-100 text-red-600',
    purple: 'bg-purple-100 text-purple-600'
  };

  return (
    <div className="min-h-screen bg-slate-50" dir={isRTL ? 'rtl' : 'ltr'}>
      {/* Header */}
      <header className="bg-white shadow-sm border-b sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <img src="/bayan-logo.png" alt="Bayan" className="h-14 w-auto object-contain" />
          </div>
          <nav className="hidden md:flex items-center gap-6">
            <a href="#services" className="text-slate-600 hover:text-bayan-navy font-medium transition-colors">
              {isRTL ? 'خدماتنا' : 'Services'}
            </a>
            <a href="#tracking" className="text-slate-600 hover:text-bayan-navy font-medium transition-colors">
              {isRTL ? 'تتبع الطلب' : 'Track Order'}
            </a>
            <a href="#rfq" className="text-slate-600 hover:text-bayan-navy font-medium transition-colors">
              {isRTL ? 'طلب عرض سعر' : 'Get Quote'}
            </a>
            <a href="#faq" className="text-slate-600 hover:text-bayan-navy font-medium transition-colors">
              {isRTL ? 'الأسئلة الشائعة' : 'FAQ'}
            </a>
          </nav>
          <div className="flex items-center gap-3">
            <LanguageSwitcher />
            <Button 
              variant="outline" 
              size="sm"
              onClick={() => navigate('/login')}
              className="hidden sm:flex"
            >
              {isRTL ? 'تسجيل الدخول' : 'Admin Login'}
            </Button>
          </div>
        </div>
        <div className="h-1 bg-gradient-to-r from-bayan-navy via-bayan-gold to-bayan-navy"></div>
      </header>

      {/* Hero Section */}
      <section className="relative bg-gradient-to-br from-bayan-navy via-bayan-navy-light to-bayan-navy text-white py-20 overflow-hidden">
        {/* Background Pattern */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-0 left-0 w-96 h-96 bg-white rounded-full -translate-x-1/2 -translate-y-1/2"></div>
          <div className="absolute bottom-0 right-0 w-96 h-96 bg-white rounded-full translate-x-1/2 translate-y-1/2"></div>
        </div>
        
        <div className="max-w-7xl mx-auto px-4 relative z-10">
          <div className="max-w-3xl mx-auto text-center">
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-white/10 rounded-full mb-6">
              <Shield className="w-5 h-5 text-bayan-gold" />
              <span className="text-sm font-medium">
                {isRTL ? 'معتمدون من الهيئة السعودية للاعتماد' : 'Accredited by Saudi Accreditation Center (SAC)'}
              </span>
            </div>
            
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold mb-6 leading-tight">
              {isRTL ? 'بوابة العملاء' : 'Customer Portal'}
            </h1>
            <p className="text-xl md:text-2xl text-white/80 mb-8 leading-relaxed">
              {isRTL 
                ? 'شريكك الموثوق في رحلة الاعتماد والتميز المؤسسي'
                : 'Your Trusted Partner in Certification & Organizational Excellence'}
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button 
                size="lg" 
                className="bg-bayan-gold hover:bg-bayan-gold/90 text-bayan-navy font-semibold px-8"
                onClick={() => document.getElementById('rfq').scrollIntoView({ behavior: 'smooth' })}
              >
                {isRTL ? 'طلب عرض سعر' : 'Request Quote'}
                <ArrowRight className="w-5 h-5 ms-2" />
              </Button>
              <Button 
                size="lg" 
                variant="outline" 
                className="border-white text-white hover:bg-white/10 px-8"
                onClick={() => document.getElementById('tracking').scrollIntoView({ behavior: 'smooth' })}
              >
                <Search className="w-5 h-5 me-2" />
                {isRTL ? 'تتبع طلبك' : 'Track Your Order'}
              </Button>
            </div>
          </div>
        </div>
        
        {/* Stats Bar */}
        <div className="max-w-5xl mx-auto mt-16 px-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              { value: '500+', label: isRTL ? 'شركة معتمدة' : 'Certified Companies' },
              { value: '15+', label: isRTL ? 'سنوات خبرة' : 'Years Experience' },
              { value: '50+', label: isRTL ? 'مدقق معتمد' : 'Certified Auditors' },
              { value: '99%', label: isRTL ? 'رضا العملاء' : 'Client Satisfaction' }
            ].map((stat, idx) => (
              <div key={idx} className="text-center p-4 bg-white/10 rounded-xl backdrop-blur-sm">
                <div className="text-3xl md:text-4xl font-bold text-bayan-gold mb-1">{stat.value}</div>
                <div className="text-sm text-white/70">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Services Section */}
      <section id="services" className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold text-bayan-navy mb-4">
              {isRTL ? 'خدمات الاعتماد' : 'Certification Services'}
            </h2>
            <p className="text-lg text-slate-600 max-w-2xl mx-auto">
              {isRTL 
                ? 'نقدم خدمات اعتماد شاملة لمساعدة مؤسستك على تحقيق التميز'
                : 'We provide comprehensive certification services to help your organization achieve excellence'}
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {services.map((service) => {
              const Icon = service.icon;
              return (
                <Card 
                  key={service.id} 
                  className={`border-2 hover:shadow-lg transition-all duration-300 hover:-translate-y-1 ${colorClasses[service.color]}`}
                >
                  <CardContent className="p-6">
                    <div className={`w-14 h-14 rounded-xl ${iconBgClasses[service.color]} flex items-center justify-center mb-4`}>
                      <Icon className="w-7 h-7" />
                    </div>
                    <h3 className="text-xl font-bold mb-1">{service.title}</h3>
                    <p className="text-sm font-medium mb-3 opacity-80">{service.subtitle}</p>
                    <p className="text-sm opacity-70">{service.description}</p>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </div>
      </section>

      {/* Order Tracking Section */}
      <section id="tracking" className="py-20 bg-gradient-to-br from-slate-50 to-blue-50">
        <div className="max-w-5xl mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold text-bayan-navy mb-4">
              {isRTL ? 'تتبع طلبك' : 'Track Your Order'}
            </h2>
            <p className="text-lg text-slate-600">
              {isRTL ? 'أدخل رقم التتبع لمتابعة حالة طلبك' : 'Enter your tracking ID to monitor your application status'}
            </p>
          </div>

          <Card className="shadow-xl border-0" data-testid="tracking-search-card">
            <CardContent className="p-8">
              <div className="flex flex-col md:flex-row gap-4">
                <div className="flex-1">
                  <Input
                    type="text"
                    value={searchId}
                    onChange={(e) => setSearchId(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                    placeholder={isRTL ? 'أدخل رقم التتبع (مثال: TRK-XXXXXXXX)' : 'Enter tracking ID (e.g., TRK-XXXXXXXX)'}
                    className="h-14 text-lg"
                    data-testid="tracking-id-input"
                    dir="ltr"
                  />
                </div>
                <Button 
                  onClick={handleSearch} 
                  disabled={loading}
                  className="h-14 px-8 bg-bayan-navy hover:bg-bayan-navy-light text-lg"
                  data-testid="search-tracking-btn"
                >
                  {loading ? (
                    <Loader2 className="w-5 h-5 animate-spin" />
                  ) : (
                    <>
                      <Search className="w-5 h-5 me-2" />
                      {isRTL ? 'بحث' : 'Search'}
                    </>
                  )}
                </Button>
              </div>
              
              {error && (
                <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center gap-3" data-testid="tracking-error">
                  <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0" />
                  <p className="text-red-700">{error}</p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Order Results */}
          {orderData && (
            <div className="mt-8 space-y-6" data-testid="tracking-results">
              {/* Order Summary */}
              <Card className="shadow-lg overflow-hidden">
                <CardHeader className="bg-gradient-to-r from-bayan-navy to-bayan-navy-light text-white">
                  <div className="flex items-center justify-between">
                    <CardTitle className="flex items-center gap-3">
                      <Building2 className="w-6 h-6" />
                      {orderData.company_name}
                    </CardTitle>
                    <span className="text-sm text-white/70 font-mono" dir="ltr">
                      {orderData.tracking_id}
                    </span>
                  </div>
                </CardHeader>
                <CardContent className="p-6">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div>
                      <p className="text-sm text-slate-500 mb-1">{isRTL ? 'البريد الإلكتروني' : 'Email'}</p>
                      <p className="font-medium">{orderData.contact_email || '-'}</p>
                    </div>
                    <div>
                      <p className="text-sm text-slate-500 mb-1">{isRTL ? 'تاريخ التقديم' : 'Submitted'}</p>
                      <p className="font-medium">{formatDate(orderData.created_at)}</p>
                    </div>
                    <div>
                      <p className="text-sm text-slate-500 mb-1">{isRTL ? 'المعايير' : 'Standards'}</p>
                      <div className="flex flex-wrap gap-1">
                        {orderData.standards?.map((std) => (
                          <span key={std} className="px-2 py-0.5 bg-bayan-navy/10 text-bayan-navy text-xs font-medium rounded">
                            {std}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Timeline */}
              <Card className="shadow-lg">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Clock className="w-5 h-5 text-bayan-navy" />
                    {isRTL ? 'مسار التقدم' : 'Progress Timeline'}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {timelineSteps.map((step, index) => {
                      const currentStep = getStatusStep(orderData.current_status);
                      const isCompleted = index <= currentStep;
                      const isCurrent = index === currentStep;
                      const Icon = step.icon;
                      
                      return (
                        <div key={step.key} className="flex items-center gap-4">
                          <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                            isCompleted ? 'bg-emerald-500' : 'bg-slate-200'
                          } ${isCurrent ? 'ring-4 ring-emerald-200' : ''}`}>
                            <Icon className={`w-5 h-5 ${isCompleted ? 'text-white' : 'text-slate-400'}`} />
                          </div>
                          <div className="flex-1">
                            <p className={`font-medium ${isCompleted ? 'text-slate-900' : 'text-slate-400'}`}>
                              {step.label}
                              {isCurrent && (
                                <span className="ms-2 px-2 py-0.5 bg-emerald-100 text-emerald-700 text-xs rounded-full">
                                  {isRTL ? 'الحالي' : 'Current'}
                                </span>
                              )}
                            </p>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </CardContent>
              </Card>
            </div>
          )}
        </div>
      </section>

      {/* Request for Quotation Section */}
      <section id="rfq" className="py-20 bg-white">
        <div className="max-w-4xl mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold text-bayan-navy mb-4">
              {isRTL ? 'طلب عرض سعر' : 'Request for Quotation'}
            </h2>
            <p className="text-lg text-slate-600">
              {isRTL 
                ? 'املأ النموذج أدناه وسنتواصل معك خلال 24 ساعة'
                : 'Fill out the form below and we\'ll contact you within 24 hours'}
            </p>
          </div>

          {rfqSubmitted ? (
            <Card className="shadow-lg border-green-200 bg-green-50">
              <CardContent className="p-12 text-center">
                <CheckCircle2 className="w-20 h-20 text-green-500 mx-auto mb-6" />
                <h3 className="text-2xl font-bold text-green-800 mb-4">
                  {isRTL ? 'تم إرسال طلبك بنجاح!' : 'Your Request Has Been Submitted!'}
                </h3>
                <p className="text-green-700 mb-6">
                  {isRTL 
                    ? 'سيقوم فريقنا بمراجعة طلبك والتواصل معك في أقرب وقت ممكن.'
                    : 'Our team will review your request and contact you as soon as possible.'}
                </p>
                <Button onClick={() => setRfqSubmitted(false)} variant="outline" className="border-green-500 text-green-700">
                  {isRTL ? 'إرسال طلب آخر' : 'Submit Another Request'}
                </Button>
              </CardContent>
            </Card>
          ) : (
            <Card className="shadow-xl">
              <CardContent className="p-8">
                <form onSubmit={handleRfqSubmit} className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-2">
                      <Label>{isRTL ? 'اسم الشركة' : 'Company Name'} *</Label>
                      <Input
                        value={rfqForm.company_name}
                        onChange={(e) => setRfqForm({ ...rfqForm, company_name: e.target.value })}
                        required
                        placeholder={isRTL ? 'أدخل اسم الشركة' : 'Enter company name'}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label>{isRTL ? 'اسم المسؤول' : 'Contact Name'} *</Label>
                      <Input
                        value={rfqForm.contact_name}
                        onChange={(e) => setRfqForm({ ...rfqForm, contact_name: e.target.value })}
                        required
                        placeholder={isRTL ? 'أدخل اسم المسؤول' : 'Enter contact name'}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label>{isRTL ? 'البريد الإلكتروني' : 'Email'} *</Label>
                      <Input
                        type="email"
                        value={rfqForm.email}
                        onChange={(e) => setRfqForm({ ...rfqForm, email: e.target.value })}
                        required
                        placeholder={isRTL ? 'example@company.com' : 'example@company.com'}
                        dir="ltr"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label>{isRTL ? 'رقم الهاتف' : 'Phone Number'} *</Label>
                      <Input
                        type="tel"
                        value={rfqForm.phone}
                        onChange={(e) => setRfqForm({ ...rfqForm, phone: e.target.value })}
                        required
                        placeholder="+966 5X XXX XXXX"
                        dir="ltr"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label>{isRTL ? 'عدد الموظفين' : 'Number of Employees'}</Label>
                      <Input
                        type="number"
                        value={rfqForm.employees}
                        onChange={(e) => setRfqForm({ ...rfqForm, employees: e.target.value })}
                        placeholder={isRTL ? 'مثال: 50' : 'e.g., 50'}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label>{isRTL ? 'عدد المواقع' : 'Number of Sites'}</Label>
                      <Input
                        type="number"
                        value={rfqForm.sites}
                        onChange={(e) => setRfqForm({ ...rfqForm, sites: e.target.value })}
                        placeholder="1"
                      />
                    </div>
                  </div>

                  <div className="space-y-3">
                    <Label>{isRTL ? 'المعايير المطلوبة' : 'Required Standards'} *</Label>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                      {services.map((service) => (
                        <label
                          key={service.id}
                          className={`flex items-center gap-3 p-3 border-2 rounded-lg cursor-pointer transition-all ${
                            rfqForm.standards.includes(service.title)
                              ? 'border-bayan-navy bg-bayan-navy/5'
                              : 'border-slate-200 hover:border-slate-300'
                          }`}
                        >
                          <Checkbox
                            checked={rfqForm.standards.includes(service.title)}
                            onCheckedChange={() => toggleStandard(service.title)}
                          />
                          <span className="text-sm font-medium">{service.title}</span>
                        </label>
                      ))}
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label>{isRTL ? 'رسالة إضافية' : 'Additional Message'}</Label>
                    <Textarea
                      value={rfqForm.message}
                      onChange={(e) => setRfqForm({ ...rfqForm, message: e.target.value })}
                      placeholder={isRTL ? 'أي معلومات إضافية تود مشاركتها...' : 'Any additional information you\'d like to share...'}
                      rows={4}
                    />
                  </div>

                  <Button 
                    type="submit" 
                    size="lg" 
                    className="w-full bg-bayan-navy hover:bg-bayan-navy-light h-14 text-lg"
                    disabled={rfqSubmitting}
                  >
                    {rfqSubmitting ? (
                      <Loader2 className="w-5 h-5 animate-spin me-2" />
                    ) : (
                      <Send className="w-5 h-5 me-2" />
                    )}
                    {isRTL ? 'إرسال الطلب' : 'Submit Request'}
                  </Button>
                </form>
              </CardContent>
            </Card>
          )}
        </div>
      </section>

      {/* FAQ Section */}
      <section id="faq" className="py-20 bg-gradient-to-br from-slate-50 to-blue-50">
        <div className="max-w-4xl mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold text-bayan-navy mb-4">
              {isRTL ? 'الأسئلة الشائعة' : 'Frequently Asked Questions'}
            </h2>
            <p className="text-lg text-slate-600">
              {isRTL ? 'إجابات على الأسئلة الأكثر شيوعاً' : 'Answers to commonly asked questions'}
            </p>
          </div>

          <Card className="shadow-lg">
            <CardContent className="p-6">
              <Accordion type="single" collapsible className="space-y-2">
                {faqs.map((faq, index) => (
                  <AccordionItem key={index} value={`faq-${index}`} className="border rounded-lg px-4">
                    <AccordionTrigger className="text-start hover:no-underline py-4">
                      <span className="font-semibold text-bayan-navy">{faq.question}</span>
                    </AccordionTrigger>
                    <AccordionContent className="text-slate-600 pb-4">
                      {faq.answer}
                    </AccordionContent>
                  </AccordionItem>
                ))}
              </Accordion>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Contact Section */}
      <section id="contact" className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold text-bayan-navy mb-4">
              {isRTL ? 'تواصل معنا' : 'Contact Us'}
            </h2>
            <p className="text-lg text-slate-600">
              {isRTL ? 'نحن هنا لمساعدتك' : 'We\'re here to help'}
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
            {/* Contact Info */}
            <div className="space-y-8">
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 rounded-xl bg-bayan-navy/10 flex items-center justify-center flex-shrink-0">
                  <MapPin className="w-6 h-6 text-bayan-navy" />
                </div>
                <div>
                  <h3 className="font-semibold text-lg mb-1">{isRTL ? 'العنوان' : 'Address'}</h3>
                  <p className="text-slate-600">
                    {isRTL 
                      ? 'المملكة العربية السعودية، الرياض'
                      : 'Riyadh, Kingdom of Saudi Arabia'}
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-4">
                <div className="w-12 h-12 rounded-xl bg-bayan-navy/10 flex items-center justify-center flex-shrink-0">
                  <Phone className="w-6 h-6 text-bayan-navy" />
                </div>
                <div>
                  <h3 className="font-semibold text-lg mb-1">{isRTL ? 'الهاتف' : 'Phone'}</h3>
                  <p className="text-slate-600" dir="ltr">+966 XX XXX XXXX</p>
                </div>
              </div>

              <div className="flex items-start gap-4">
                <div className="w-12 h-12 rounded-xl bg-bayan-navy/10 flex items-center justify-center flex-shrink-0">
                  <Mail className="w-6 h-6 text-bayan-navy" />
                </div>
                <div>
                  <h3 className="font-semibold text-lg mb-1">{isRTL ? 'البريد الإلكتروني' : 'Email'}</h3>
                  <a href="mailto:info@bayanauditing.com" className="text-bayan-navy hover:underline">
                    info@bayanauditing.com
                  </a>
                </div>
              </div>

              <div className="flex items-start gap-4">
                <div className="w-12 h-12 rounded-xl bg-bayan-navy/10 flex items-center justify-center flex-shrink-0">
                  <Clock className="w-6 h-6 text-bayan-navy" />
                </div>
                <div>
                  <h3 className="font-semibold text-lg mb-1">{isRTL ? 'ساعات العمل' : 'Working Hours'}</h3>
                  <p className="text-slate-600">
                    {isRTL 
                      ? 'الأحد - الخميس: 8 صباحاً - 5 مساءً'
                      : 'Sunday - Thursday: 8 AM - 5 PM'}
                  </p>
                </div>
              </div>
            </div>

            {/* Contact Form */}
            <Card className="shadow-lg">
              <CardContent className="p-6">
                <form onSubmit={handleContactSubmit} className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label>{isRTL ? 'الاسم' : 'Name'} *</Label>
                      <Input
                        value={contactForm.name}
                        onChange={(e) => setContactForm({ ...contactForm, name: e.target.value })}
                        required
                      />
                    </div>
                    <div className="space-y-2">
                      <Label>{isRTL ? 'البريد الإلكتروني' : 'Email'} *</Label>
                      <Input
                        type="email"
                        value={contactForm.email}
                        onChange={(e) => setContactForm({ ...contactForm, email: e.target.value })}
                        required
                        dir="ltr"
                      />
                    </div>
                  </div>
                  <div className="space-y-2">
                    <Label>{isRTL ? 'الموضوع' : 'Subject'} *</Label>
                    <Input
                      value={contactForm.subject}
                      onChange={(e) => setContactForm({ ...contactForm, subject: e.target.value })}
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>{isRTL ? 'الرسالة' : 'Message'} *</Label>
                    <Textarea
                      value={contactForm.message}
                      onChange={(e) => setContactForm({ ...contactForm, message: e.target.value })}
                      required
                      rows={5}
                    />
                  </div>
                  <Button 
                    type="submit" 
                    className="w-full bg-bayan-navy hover:bg-bayan-navy-light"
                    disabled={contactSubmitting}
                  >
                    {contactSubmitting ? (
                      <Loader2 className="w-5 h-5 animate-spin me-2" />
                    ) : (
                      <Send className="w-5 h-5 me-2" />
                    )}
                    {isRTL ? 'إرسال' : 'Send Message'}
                  </Button>
                </form>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-bayan-navy text-white py-12">
        <div className="max-w-7xl mx-auto px-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
            <div className="md:col-span-2">
              <img src="/bayan-logo.png" alt="Bayan" className="h-16 mb-4 brightness-0 invert" />
              <p className="text-white/70 max-w-md">
                {isRTL 
                  ? 'بيان للتدقيق والمطابقة - شريكك الموثوق في رحلة الاعتماد والتميز المؤسسي'
                  : 'Bayan Auditing & Conformity - Your trusted partner in certification and organizational excellence'}
              </p>
            </div>
            <div>
              <h4 className="font-semibold mb-4">{isRTL ? 'روابط سريعة' : 'Quick Links'}</h4>
              <ul className="space-y-2 text-white/70">
                <li><a href="#services" className="hover:text-white">{isRTL ? 'خدماتنا' : 'Services'}</a></li>
                <li><a href="#tracking" className="hover:text-white">{isRTL ? 'تتبع الطلب' : 'Track Order'}</a></li>
                <li><a href="#rfq" className="hover:text-white">{isRTL ? 'طلب عرض سعر' : 'Get Quote'}</a></li>
                <li><a href="#faq" className="hover:text-white">{isRTL ? 'الأسئلة الشائعة' : 'FAQ'}</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">{isRTL ? 'الشهادات' : 'Certifications'}</h4>
              <ul className="space-y-2 text-white/70">
                <li>ISO 9001:2015</li>
                <li>ISO 14001:2015</li>
                <li>ISO 45001:2018</li>
                <li>ISO 22000:2018</li>
                <li>ISO 27001:2022</li>
              </ul>
            </div>
          </div>
          <div className="border-t border-white/20 pt-8 text-center text-white/60">
            <p>© {new Date().getFullYear()} {isRTL ? 'بيان للتدقيق والمطابقة' : 'Bayan Auditing & Conformity'}. {isRTL ? 'جميع الحقوق محفوظة' : 'All rights reserved'}.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default CustomerPortalPage;
