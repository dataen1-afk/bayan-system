import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useParams, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { motion, AnimatePresence } from 'framer-motion';
import { Card, CardContent } from '@/components/ui/card';
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
import PWAInstallPrompt from '@/components/PWAInstallPrompt';
import { 
  Search, CheckCircle, Clock, FileText, DollarSign, FileCheck, 
  Loader2, Building2, Mail, Phone, MapPin,
  Shield, Leaf, Users, Utensils, Lock, Award, ArrowRight, 
  Send, ChevronDown, Globe, Star, CheckCircle2, Menu, X
} from 'lucide-react';
import { toast } from 'sonner';

const API = process.env.REACT_APP_BACKEND_URL + '/api';

// Animation variants
const fadeInUp = {
  hidden: { opacity: 0, y: 30 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.6, ease: "easeOut" } }
};

const staggerContainer = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.1 } }
};

const CustomerPortalPage = () => {
  const { trackingId } = useParams();
  const navigate = useNavigate();
  const { t, i18n } = useTranslation();
  const isRTL = i18n.language?.startsWith('ar');
  
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [searchId, setSearchId] = useState(trackingId || '');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [orderData, setOrderData] = useState(null);
  const [searched, setSearched] = useState(false);
  
  const [rfqForm, setRfqForm] = useState({
    company_name: '', contact_name: '', email: '', phone: '',
    employees: '', sites: '1', standards: [], message: ''
  });
  const [rfqSubmitting, setRfqSubmitting] = useState(false);
  const [rfqSubmitted, setRfqSubmitted] = useState(false);

  const [contactForm, setContactForm] = useState({
    name: '', email: '', subject: '', message: ''
  });
  const [contactSubmitting, setContactSubmitting] = useState(false);

  useEffect(() => {
    if (trackingId) handleSearch();
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
      setError(err.response?.status === 404 
        ? (isRTL ? 'لم يتم العثور على الطلب' : 'Order not found')
        : (isRTL ? 'خطأ في تتبع الطلب' : 'Error tracking order'));
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

  const services = [
    { id: 'iso9001', icon: Award, title: 'ISO 9001:2015', subtitle: isRTL ? 'نظام إدارة الجودة' : 'Quality Management', color: 'blue' },
    { id: 'iso14001', icon: Leaf, title: 'ISO 14001:2015', subtitle: isRTL ? 'نظام الإدارة البيئية' : 'Environmental Management', color: 'emerald' },
    { id: 'iso45001', icon: Shield, title: 'ISO 45001:2018', subtitle: isRTL ? 'الصحة والسلامة المهنية' : 'Occupational Health & Safety', color: 'amber' },
    { id: 'iso22000', icon: Utensils, title: 'ISO 22000:2018', subtitle: isRTL ? 'سلامة الغذاء' : 'Food Safety', color: 'rose' },
    { id: 'iso27001', icon: Lock, title: 'ISO 27001:2022', subtitle: isRTL ? 'أمن المعلومات' : 'Information Security', color: 'violet' },
  ];

  const faqs = [
    { q: isRTL ? 'ما هي مدة عملية الشهادة؟' : 'How long does certification take?', a: isRTL ? 'تستغرق العملية من 2-4 أشهر حسب حجم المؤسسة وجاهزيتها.' : 'The process typically takes 2-4 months depending on organization size and readiness.' },
    { q: isRTL ? 'ما هي تكلفة الحصول على الشهادة؟' : 'What is the cost of certification?', a: isRTL ? 'تختلف التكلفة بناءً على حجم المؤسسة ونطاق الشهادة. تواصل معنا للحصول على عرض سعر مخصص.' : 'Costs vary based on organization size and scope. Contact us for a customized quote.' },
    { q: isRTL ? 'ما هي مدة صلاحية الشهادة؟' : 'How long is the certificate valid?', a: isRTL ? 'الشهادة صالحة لمدة 3 سنوات مع تدقيقات مراقبة سنوية.' : 'The certificate is valid for 3 years with annual surveillance audits.' },
    { q: isRTL ? 'هل يمكن الحصول على شهادات متعددة؟' : 'Can we obtain multiple certifications?', a: isRTL ? 'نعم، يمكن دمج التدقيقات للحصول على شهادات متعددة بتكلفة ووقت أقل.' : 'Yes, audits can be combined to obtain multiple certifications at reduced cost and time.' },
  ];

  const stats = [
    { value: '500+', label: isRTL ? 'شركة معتمدة' : 'Certified Companies' },
    { value: '15+', label: isRTL ? 'سنوات خبرة' : 'Years Experience' },
    { value: '50+', label: isRTL ? 'مدقق معتمد' : 'Certified Auditors' },
    { value: '99%', label: isRTL ? 'رضا العملاء' : 'Client Satisfaction' },
  ];

  const timelineSteps = [
    { key: 'pending', label: isRTL ? 'تم الإنشاء' : 'Created', icon: FileText },
    { key: 'submitted', label: isRTL ? 'تم التقديم' : 'Submitted', icon: CheckCircle },
    { key: 'under_review', label: isRTL ? 'قيد المراجعة' : 'Under Review', icon: Clock },
    { key: 'accepted', label: isRTL ? 'تم القبول' : 'Accepted', icon: DollarSign },
    { key: 'agreement_signed', label: isRTL ? 'تم التوقيع' : 'Signed', icon: FileCheck },
  ];

  const getStatusStep = (status) => {
    const steps = ['pending', 'submitted', 'under_review', 'accepted', 'agreement_signed'];
    return steps.indexOf(status);
  };

  const scrollTo = (id) => {
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' });
    setMobileMenuOpen(false);
  };

  return (
    <div className="min-h-screen bg-[#F8F9FA]" dir={isRTL ? 'rtl' : 'ltr'}>
      {/* Navigation */}
      <header className="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-xl border-b border-slate-200/50">
        <div className="max-w-7xl mx-auto px-6 md:px-12">
          <div className="flex items-center justify-between h-20">
            <img src="/bayan-logo.png" alt="Bayan" className="h-14 w-auto" />
            
            <nav className="hidden md:flex items-center gap-8">
              {[
                { id: 'services', label: isRTL ? 'خدماتنا' : 'Services' },
                { id: 'tracking', label: isRTL ? 'تتبع الطلب' : 'Track Order' },
                { id: 'rfq', label: isRTL ? 'طلب عرض سعر' : 'Get Quote' },
                { id: 'faq', label: isRTL ? 'الأسئلة الشائعة' : 'FAQ' },
              ].map(item => (
                <button
                  key={item.id}
                  onClick={() => scrollTo(item.id)}
                  className="text-slate-600 hover:text-[#1e3a5f] font-medium transition-colors text-sm tracking-wide"
                  data-testid={`nav-${item.id}`}
                >
                  {item.label}
                </button>
              ))}
            </nav>
            
            <div className="flex items-center gap-4">
              <LanguageSwitcher />
              <Button 
                variant="outline" 
                size="sm"
                onClick={() => navigate('/login')}
                className="hidden md:flex border-[#1e3a5f] text-[#1e3a5f] hover:bg-[#1e3a5f] hover:text-white"
                data-testid="admin-login-btn"
              >
                {isRTL ? 'تسجيل الدخول' : 'Admin Login'}
              </Button>
              <button 
                className="md:hidden p-2"
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                data-testid="mobile-menu-btn"
              >
                {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
              </button>
            </div>
          </div>
        </div>
        
        {/* Mobile Menu */}
        <AnimatePresence>
          {mobileMenuOpen && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="md:hidden bg-white border-t"
            >
              <div className="px-6 py-4 space-y-3">
                {['services', 'tracking', 'rfq', 'faq'].map(id => (
                  <button
                    key={id}
                    onClick={() => scrollTo(id)}
                    className="block w-full text-start py-2 text-slate-600 hover:text-[#1e3a5f]"
                  >
                    {id === 'services' && (isRTL ? 'خدماتنا' : 'Services')}
                    {id === 'tracking' && (isRTL ? 'تتبع الطلب' : 'Track Order')}
                    {id === 'rfq' && (isRTL ? 'طلب عرض سعر' : 'Get Quote')}
                    {id === 'faq' && (isRTL ? 'الأسئلة الشائعة' : 'FAQ')}
                  </button>
                ))}
                <Button 
                  className="w-full mt-2"
                  onClick={() => navigate('/login')}
                >
                  {isRTL ? 'تسجيل الدخول' : 'Admin Login'}
                </Button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </header>

      {/* Hero Section */}
      <section className="relative min-h-[90vh] flex items-center pt-20 overflow-hidden">
        {/* Background */}
        <div className="absolute inset-0 bg-gradient-to-br from-[#1e3a5f] via-[#1e3a5f] to-[#0f1e31]">
          <div className="absolute inset-0" style={{
            backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23c9a55c' fill-opacity='0.05'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
          }} />
        </div>
        
        <div className="relative z-10 max-w-7xl mx-auto px-6 md:px-12 py-20">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            <motion.div 
              initial="hidden" 
              animate="visible" 
              variants={staggerContainer}
              className={isRTL ? 'text-right' : 'text-left'}
            >
              <motion.div variants={fadeInUp} className="inline-flex items-center gap-2 px-4 py-2 bg-[#c9a55c]/20 rounded-full mb-8">
                <Globe className="w-4 h-4 text-[#c9a55c]" />
                <span className="text-sm font-medium text-[#c9a55c]">
                  {isRTL ? 'معتمدون من الهيئة السعودية للاعتماد' : 'SAC Accredited Certification Body'}
                </span>
              </motion.div>
              
              <motion.h1 variants={fadeInUp} className="text-5xl md:text-7xl font-bold text-white mb-8 tracking-tighter leading-[1.1]">
                {isRTL ? (
                  <>بوابة <span className="text-[#c9a55c]">العملاء</span></>
                ) : (
                  <>Customer <span className="text-[#c9a55c]">Portal</span></>
                )}
              </motion.h1>
              
              <motion.p variants={fadeInUp} className="text-xl text-white/70 mb-10 leading-relaxed max-w-lg">
                {isRTL 
                  ? 'شريكك الموثوق في رحلة الاعتماد والتميز المؤسسي'
                  : 'Your trusted partner in the journey of accreditation and organizational excellence'}
              </motion.p>
              
              <motion.div variants={fadeInUp} className={`flex flex-wrap gap-4 ${isRTL ? 'justify-end' : 'justify-start'}`}>
                <Button 
                  size="lg"
                  onClick={() => scrollTo('rfq')}
                  className="bg-[#c9a55c] hover:bg-[#b08d45] text-white font-semibold px-8 py-6 text-base shadow-lg shadow-yellow-600/20 hover:scale-[1.02] transition-all"
                  data-testid="hero-get-quote-btn"
                >
                  {isRTL ? 'طلب عرض سعر' : 'Request Quote'}
                  <ArrowRight className={`w-5 h-5 ${isRTL ? 'mr-2 rotate-180' : 'ml-2'}`} />
                </Button>
                <Button 
                  size="lg"
                  variant="outline"
                  onClick={() => scrollTo('tracking')}
                  className="border-2 border-white/30 text-white hover:bg-white/10 font-semibold px-8 py-6 text-base"
                  data-testid="hero-track-btn"
                >
                  <Search className={`w-5 h-5 ${isRTL ? 'ml-2' : 'mr-2'}`} />
                  {isRTL ? 'تتبع طلبك' : 'Track Order'}
                </Button>
              </motion.div>
            </motion.div>
            
            {/* Stats */}
            <motion.div 
              initial={{ opacity: 0, x: 50 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.4, duration: 0.6 }}
              className="hidden lg:grid grid-cols-2 gap-6"
            >
              {stats.map((stat, idx) => (
                <div 
                  key={idx}
                  className="bg-white/10 backdrop-blur-sm rounded-2xl p-8 border border-white/10"
                >
                  <div className="text-4xl font-bold text-[#c9a55c] mb-2">{stat.value}</div>
                  <div className="text-white/70 font-medium">{stat.label}</div>
                </div>
              ))}
            </motion.div>
          </div>
        </div>
        
        {/* Scroll indicator */}
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1 }}
          className="absolute bottom-8 left-1/2 -translate-x-1/2"
        >
          <motion.div
            animate={{ y: [0, 10, 0] }}
            transition={{ repeat: Infinity, duration: 2 }}
          >
            <ChevronDown className="w-8 h-8 text-white/50" />
          </motion.div>
        </motion.div>
      </section>

      {/* Services Section */}
      <section id="services" className="py-24 md:py-32">
        <div className="max-w-7xl mx-auto px-6 md:px-12">
          <motion.div 
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={staggerContainer}
            className={`mb-16 ${isRTL ? 'text-right' : 'text-left'}`}
          >
            <motion.span variants={fadeInUp} className="text-sm font-medium tracking-widest uppercase text-[#c9a55c] mb-4 block">
              {isRTL ? 'خدماتنا' : 'Our Services'}
            </motion.span>
            <motion.h2 variants={fadeInUp} className="text-4xl md:text-5xl font-semibold text-[#1e3a5f] tracking-tight mb-6">
              {isRTL ? 'خدمات الاعتماد' : 'Certification Services'}
            </motion.h2>
            <motion.p variants={fadeInUp} className="text-lg text-slate-600 max-w-2xl leading-relaxed">
              {isRTL 
                ? 'نقدم خدمات اعتماد معترف بها دوليًا لمساعدة مؤسستك على تحقيق التميز'
                : 'We provide internationally recognized certification services to help your organization achieve excellence'}
            </motion.p>
          </motion.div>
          
          {/* Bento Grid */}
          <motion.div 
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={staggerContainer}
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
          >
            {services.map((service, idx) => {
              const Icon = service.icon;
              const isLarge = idx === 0;
              return (
                <motion.div
                  key={service.id}
                  variants={fadeInUp}
                  className={`group bg-white rounded-2xl p-8 border border-slate-100 hover:border-[#c9a55c]/50 transition-all duration-300 cursor-pointer shadow-[0_8px_30px_rgb(0,0,0,0.04)] hover:shadow-[0_8px_30px_rgb(0,0,0,0.08)] ${isLarge ? 'md:col-span-2 lg:col-span-1' : ''}`}
                  onClick={() => toggleStandard(service.title)}
                >
                  <div className={`w-14 h-14 rounded-xl flex items-center justify-center mb-6 transition-colors duration-300 ${rfqForm.standards.includes(service.title) ? 'bg-[#1e3a5f] text-white' : 'bg-[#1e3a5f]/5 text-[#1e3a5f] group-hover:bg-[#1e3a5f] group-hover:text-white'}`}>
                    <Icon className="w-7 h-7" />
                  </div>
                  <h3 className="text-xl font-semibold text-[#1e3a5f] mb-2">{service.title}</h3>
                  <p className="text-slate-600">{service.subtitle}</p>
                  {rfqForm.standards.includes(service.title) && (
                    <div className={`mt-4 flex items-center gap-2 text-[#c9a55c] text-sm font-medium ${isRTL ? 'flex-row-reverse' : ''}`}>
                      <CheckCircle2 className="w-4 h-4" />
                      {isRTL ? 'تم الاختيار' : 'Selected'}
                    </div>
                  )}
                </motion.div>
              );
            })}
          </motion.div>
        </div>
      </section>

      {/* RFQ Section */}
      <section id="rfq" className="py-24 md:py-32 bg-gradient-to-b from-[#F8F9FA] to-white">
        <div className="max-w-7xl mx-auto px-6 md:px-12">
          <div className="grid lg:grid-cols-2 gap-16 items-start">
            <motion.div 
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true }}
              variants={staggerContainer}
              className={isRTL ? 'text-right order-2 lg:order-1' : 'text-left order-2 lg:order-1'}
            >
              <motion.span variants={fadeInUp} className="text-sm font-medium tracking-widest uppercase text-[#c9a55c] mb-4 block">
                {isRTL ? 'احصل على عرض سعر' : 'Get a Quote'}
              </motion.span>
              <motion.h2 variants={fadeInUp} className="text-4xl md:text-5xl font-semibold text-[#1e3a5f] tracking-tight mb-6">
                {isRTL ? 'طلب عرض سعر' : 'Request for Quote'}
              </motion.h2>
              <motion.p variants={fadeInUp} className="text-lg text-slate-600 leading-relaxed mb-8">
                {isRTL 
                  ? 'املأ النموذج وسنتواصل معك خلال 24 ساعة بعرض سعر مخصص لاحتياجات مؤسستك'
                  : 'Fill out the form and we will contact you within 24 hours with a customized quote for your organization'}
              </motion.p>
              
              <motion.div variants={fadeInUp} className="space-y-4">
                {[
                  { icon: CheckCircle2, text: isRTL ? 'عروض أسعار مجانية' : 'Free quotes' },
                  { icon: Clock, text: isRTL ? 'رد خلال 24 ساعة' : '24-hour response' },
                  { icon: Shield, text: isRTL ? 'بيانات آمنة ومحمية' : 'Secure & protected data' },
                ].map((item, idx) => (
                  <div key={idx} className={`flex items-center gap-3 ${isRTL ? 'flex-row-reverse' : ''}`}>
                    <item.icon className="w-5 h-5 text-[#c9a55c]" />
                    <span className="text-slate-600">{item.text}</span>
                  </div>
                ))}
              </motion.div>
            </motion.div>
            
            <motion.div 
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              className="order-1 lg:order-2"
            >
              {rfqSubmitted ? (
                <div className="bg-white rounded-2xl p-12 text-center shadow-[0_20px_50px_rgba(8,_112,_184,_0.1)]">
                  <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
                    <CheckCircle2 className="w-10 h-10 text-green-600" />
                  </div>
                  <h3 className="text-2xl font-semibold text-[#1e3a5f] mb-4">
                    {isRTL ? 'تم إرسال طلبك بنجاح!' : 'Request Submitted Successfully!'}
                  </h3>
                  <p className="text-slate-600 mb-6">
                    {isRTL ? 'سنتواصل معك قريبًا' : 'We will contact you soon'}
                  </p>
                  <Button onClick={() => setRfqSubmitted(false)} variant="outline">
                    {isRTL ? 'إرسال طلب آخر' : 'Submit Another Request'}
                  </Button>
                </div>
              ) : (
                <form onSubmit={handleRfqSubmit} className="bg-white/80 backdrop-blur-xl rounded-2xl p-8 shadow-[0_20px_50px_rgba(8,_112,_184,_0.1)] border border-white/20">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-2">
                      <Label className={`text-sm font-medium text-slate-700 ${isRTL ? 'text-right block' : ''}`}>
                        {isRTL ? 'اسم الشركة' : 'Company Name'} *
                      </Label>
                      <Input
                        required
                        value={rfqForm.company_name}
                        onChange={(e) => setRfqForm(prev => ({ ...prev, company_name: e.target.value }))}
                        className={`h-12 bg-slate-50 border-slate-200 focus:border-[#c9a55c] focus:ring-[#c9a55c]/20 ${isRTL ? 'text-right' : ''}`}
                        data-testid="rfq-company-name"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label className={`text-sm font-medium text-slate-700 ${isRTL ? 'text-right block' : ''}`}>
                        {isRTL ? 'اسم جهة الاتصال' : 'Contact Name'} *
                      </Label>
                      <Input
                        required
                        value={rfqForm.contact_name}
                        onChange={(e) => setRfqForm(prev => ({ ...prev, contact_name: e.target.value }))}
                        className={`h-12 bg-slate-50 border-slate-200 focus:border-[#c9a55c] focus:ring-[#c9a55c]/20 ${isRTL ? 'text-right' : ''}`}
                        data-testid="rfq-contact-name"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label className={`text-sm font-medium text-slate-700 ${isRTL ? 'text-right block' : ''}`}>
                        {isRTL ? 'البريد الإلكتروني' : 'Email'} *
                      </Label>
                      <Input
                        type="email"
                        required
                        value={rfqForm.email}
                        onChange={(e) => setRfqForm(prev => ({ ...prev, email: e.target.value }))}
                        className={`h-12 bg-slate-50 border-slate-200 focus:border-[#c9a55c] focus:ring-[#c9a55c]/20 ${isRTL ? 'text-right' : ''}`}
                        data-testid="rfq-email"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label className={`text-sm font-medium text-slate-700 ${isRTL ? 'text-right block' : ''}`}>
                        {isRTL ? 'رقم الهاتف' : 'Phone'} *
                      </Label>
                      <Input
                        required
                        value={rfqForm.phone}
                        onChange={(e) => setRfqForm(prev => ({ ...prev, phone: e.target.value }))}
                        className={`h-12 bg-slate-50 border-slate-200 focus:border-[#c9a55c] focus:ring-[#c9a55c]/20 ${isRTL ? 'text-right' : ''}`}
                        data-testid="rfq-phone"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label className={`text-sm font-medium text-slate-700 ${isRTL ? 'text-right block' : ''}`}>
                        {isRTL ? 'عدد الموظفين' : 'Number of Employees'}
                      </Label>
                      <Input
                        value={rfqForm.employees}
                        onChange={(e) => setRfqForm(prev => ({ ...prev, employees: e.target.value }))}
                        placeholder={isRTL ? 'مثال: 50-100' : 'e.g., 50-100'}
                        className={`h-12 bg-slate-50 border-slate-200 focus:border-[#c9a55c] focus:ring-[#c9a55c]/20 ${isRTL ? 'text-right' : ''}`}
                        data-testid="rfq-employees"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label className={`text-sm font-medium text-slate-700 ${isRTL ? 'text-right block' : ''}`}>
                        {isRTL ? 'عدد المواقع' : 'Number of Sites'}
                      </Label>
                      <Input
                        value={rfqForm.sites}
                        onChange={(e) => setRfqForm(prev => ({ ...prev, sites: e.target.value }))}
                        className={`h-12 bg-slate-50 border-slate-200 focus:border-[#c9a55c] focus:ring-[#c9a55c]/20 ${isRTL ? 'text-right' : ''}`}
                        data-testid="rfq-sites"
                      />
                    </div>
                  </div>
                  
                  <div className="mt-6 space-y-2">
                    <Label className={`text-sm font-medium text-slate-700 ${isRTL ? 'text-right block' : ''}`}>
                      {isRTL ? 'المعايير المطلوبة' : 'Required Standards'} *
                    </Label>
                    <div className="flex flex-wrap gap-3">
                      {services.map(s => (
                        <button
                          key={s.id}
                          type="button"
                          onClick={() => toggleStandard(s.title)}
                          className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                            rfqForm.standards.includes(s.title)
                              ? 'bg-[#1e3a5f] text-white'
                              : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                          }`}
                          data-testid={`rfq-standard-${s.id}`}
                        >
                          {s.title}
                        </button>
                      ))}
                    </div>
                  </div>
                  
                  <div className="mt-6 space-y-2">
                    <Label className={`text-sm font-medium text-slate-700 ${isRTL ? 'text-right block' : ''}`}>
                      {isRTL ? 'رسالة إضافية' : 'Additional Message'}
                    </Label>
                    <Textarea
                      value={rfqForm.message}
                      onChange={(e) => setRfqForm(prev => ({ ...prev, message: e.target.value }))}
                      rows={3}
                      className={`bg-slate-50 border-slate-200 focus:border-[#c9a55c] focus:ring-[#c9a55c]/20 ${isRTL ? 'text-right' : ''}`}
                      data-testid="rfq-message"
                    />
                  </div>
                  
                  <Button 
                    type="submit" 
                    disabled={rfqSubmitting}
                    className="w-full mt-8 h-14 bg-[#1e3a5f] hover:bg-[#152a45] text-white font-semibold text-base shadow-lg shadow-blue-900/20 hover:scale-[1.01] transition-all"
                    data-testid="rfq-submit-btn"
                  >
                    {rfqSubmitting ? (
                      <Loader2 className="w-5 h-5 animate-spin" />
                    ) : (
                      <>
                        <Send className={`w-5 h-5 ${isRTL ? 'ml-2' : 'mr-2'}`} />
                        {isRTL ? 'إرسال الطلب' : 'Submit Request'}
                      </>
                    )}
                  </Button>
                </form>
              )}
            </motion.div>
          </div>
        </div>
      </section>

      {/* Tracking Section */}
      <section id="tracking" className="py-24 md:py-32 bg-[#1e3a5f]">
        <div className="max-w-4xl mx-auto px-6 md:px-12">
          <motion.div 
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={staggerContainer}
            className="text-center mb-12"
          >
            <motion.span variants={fadeInUp} className="text-sm font-medium tracking-widest uppercase text-[#c9a55c] mb-4 block">
              {isRTL ? 'تتبع طلبك' : 'Track Your Order'}
            </motion.span>
            <motion.h2 variants={fadeInUp} className="text-4xl md:text-5xl font-semibold text-white tracking-tight mb-6">
              {isRTL ? 'تتبع حالة الطلب' : 'Track Order Status'}
            </motion.h2>
          </motion.div>
          
          <motion.div 
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="bg-white rounded-2xl p-8 shadow-[0_20px_50px_rgba(0,_0,_0,_0.3)]"
          >
            <div className={`flex gap-4 mb-8 ${isRTL ? 'flex-row-reverse' : ''}`}>
              <Input
                value={searchId}
                onChange={(e) => setSearchId(e.target.value)}
                placeholder={isRTL ? 'أدخل رقم التتبع أو البريد الإلكتروني' : 'Enter tracking ID or email'}
                className={`h-14 flex-1 bg-slate-50 border-slate-200 focus:border-[#c9a55c] text-lg ${isRTL ? 'text-right' : ''}`}
                onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                data-testid="tracking-input"
              />
              <Button 
                onClick={handleSearch}
                disabled={loading}
                className="h-14 px-8 bg-[#c9a55c] hover:bg-[#b08d45] text-white font-semibold"
                data-testid="tracking-search-btn"
              >
                {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Search className="w-5 h-5" />}
              </Button>
            </div>
            
            {error && (
              <div className={`p-4 rounded-lg bg-red-50 text-red-600 mb-6 ${isRTL ? 'text-right' : ''}`}>
                {error}
              </div>
            )}
            
            {orderData && (
              <div className="space-y-6">
                <div className={`p-6 bg-slate-50 rounded-xl ${isRTL ? 'text-right' : ''}`}>
                  <h4 className="font-semibold text-[#1e3a5f] mb-4">
                    {isRTL ? 'معلومات الطلب' : 'Order Information'}
                  </h4>
                  <div className="grid md:grid-cols-2 gap-4 text-sm">
                    <div><span className="text-slate-500">{isRTL ? 'الشركة:' : 'Company:'}</span> <span className="font-medium">{orderData.company_name}</span></div>
                    <div><span className="text-slate-500">{isRTL ? 'البريد:' : 'Email:'}</span> <span className="font-medium">{orderData.email}</span></div>
                  </div>
                </div>
                
                {/* Timeline */}
                <div className="relative">
                  <div className={`flex justify-between ${isRTL ? 'flex-row-reverse' : ''}`}>
                    {timelineSteps.map((step, idx) => {
                      const Icon = step.icon;
                      const currentStep = getStatusStep(orderData.status);
                      const isComplete = idx <= currentStep;
                      const isCurrent = idx === currentStep;
                      return (
                        <div key={step.key} className="flex flex-col items-center relative z-10">
                          <div className={`w-12 h-12 rounded-full flex items-center justify-center transition-all ${
                            isComplete ? 'bg-[#c9a55c] text-white' : 'bg-slate-200 text-slate-400'
                          } ${isCurrent ? 'ring-4 ring-[#c9a55c]/30' : ''}`}>
                            <Icon className="w-5 h-5" />
                          </div>
                          <span className={`mt-3 text-xs font-medium text-center max-w-[80px] ${isComplete ? 'text-[#1e3a5f]' : 'text-slate-400'}`}>
                            {step.label}
                          </span>
                        </div>
                      );
                    })}
                  </div>
                  {/* Progress Line */}
                  <div className="absolute top-6 left-6 right-6 h-0.5 bg-slate-200 -z-0">
                    <div 
                      className="h-full bg-[#c9a55c] transition-all duration-500"
                      style={{ width: `${(getStatusStep(orderData.status) / (timelineSteps.length - 1)) * 100}%` }}
                    />
                  </div>
                </div>
              </div>
            )}
            
            {searched && !orderData && !loading && !error && (
              <div className="text-center py-8 text-slate-500">
                {isRTL ? 'لم يتم العثور على نتائج' : 'No results found'}
              </div>
            )}
          </motion.div>
        </div>
      </section>

      {/* FAQ Section */}
      <section id="faq" className="py-24 md:py-32">
        <div className="max-w-3xl mx-auto px-6 md:px-12">
          <motion.div 
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={staggerContainer}
            className="text-center mb-12"
          >
            <motion.span variants={fadeInUp} className="text-sm font-medium tracking-widest uppercase text-[#c9a55c] mb-4 block">
              {isRTL ? 'الأسئلة الشائعة' : 'FAQ'}
            </motion.span>
            <motion.h2 variants={fadeInUp} className="text-4xl md:text-5xl font-semibold text-[#1e3a5f] tracking-tight">
              {isRTL ? 'الأسئلة المتكررة' : 'Frequently Asked Questions'}
            </motion.h2>
          </motion.div>
          
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <Accordion type="single" collapsible className="space-y-4">
              {faqs.map((faq, idx) => (
                <AccordionItem 
                  key={idx} 
                  value={`item-${idx}`}
                  className="bg-white rounded-xl border border-slate-100 px-6 overflow-hidden shadow-[0_8px_30px_rgb(0,0,0,0.04)]"
                >
                  <AccordionTrigger className={`py-6 text-[#1e3a5f] font-medium hover:no-underline ${isRTL ? 'text-right flex-row-reverse' : ''}`}>
                    {faq.q}
                  </AccordionTrigger>
                  <AccordionContent className={`pb-6 text-slate-600 leading-relaxed ${isRTL ? 'text-right' : ''}`}>
                    {faq.a}
                  </AccordionContent>
                </AccordionItem>
              ))}
            </Accordion>
          </motion.div>
        </div>
      </section>

      {/* Contact Section */}
      <section className="py-24 md:py-32 bg-slate-50">
        <div className="max-w-7xl mx-auto px-6 md:px-12">
          <div className="grid lg:grid-cols-2 gap-16">
            <motion.div 
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true }}
              variants={staggerContainer}
              className={isRTL ? 'text-right' : ''}
            >
              <motion.span variants={fadeInUp} className="text-sm font-medium tracking-widest uppercase text-[#c9a55c] mb-4 block">
                {isRTL ? 'تواصل معنا' : 'Contact Us'}
              </motion.span>
              <motion.h2 variants={fadeInUp} className="text-4xl md:text-5xl font-semibold text-[#1e3a5f] tracking-tight mb-6">
                {isRTL ? 'نحن هنا للمساعدة' : "We're Here to Help"}
              </motion.h2>
              <motion.p variants={fadeInUp} className="text-lg text-slate-600 leading-relaxed mb-8">
                {isRTL 
                  ? 'لديك استفسار؟ فريقنا جاهز للإجابة على جميع أسئلتك'
                  : 'Have a question? Our team is ready to answer all your inquiries'}
              </motion.p>
              
              <motion.div variants={fadeInUp} className="space-y-6">
                {[
                  { icon: Phone, label: isRTL ? 'الهاتف' : 'Phone', value: '+966 11 XXX XXXX' },
                  { icon: Mail, label: isRTL ? 'البريد' : 'Email', value: 'info@bayan.sa' },
                  { icon: MapPin, label: isRTL ? 'العنوان' : 'Address', value: isRTL ? 'الرياض، المملكة العربية السعودية' : 'Riyadh, Saudi Arabia' },
                ].map((item, idx) => (
                  <div key={idx} className={`flex items-start gap-4 ${isRTL ? 'flex-row-reverse' : ''}`}>
                    <div className="w-12 h-12 rounded-xl bg-[#1e3a5f]/5 flex items-center justify-center flex-shrink-0">
                      <item.icon className="w-5 h-5 text-[#1e3a5f]" />
                    </div>
                    <div>
                      <div className="text-sm text-slate-500 mb-1">{item.label}</div>
                      <div className="font-medium text-[#1e3a5f]">{item.value}</div>
                    </div>
                  </div>
                ))}
              </motion.div>
            </motion.div>
            
            <motion.form
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              onSubmit={handleContactSubmit}
              className="bg-white rounded-2xl p-8 shadow-[0_8px_30px_rgb(0,0,0,0.04)]"
            >
              <div className="space-y-6">
                <div className="space-y-2">
                  <Label className={`text-sm font-medium text-slate-700 ${isRTL ? 'text-right block' : ''}`}>
                    {isRTL ? 'الاسم' : 'Name'} *
                  </Label>
                  <Input
                    required
                    value={contactForm.name}
                    onChange={(e) => setContactForm(prev => ({ ...prev, name: e.target.value }))}
                    className={`h-12 bg-slate-50 border-slate-200 focus:border-[#c9a55c] ${isRTL ? 'text-right' : ''}`}
                    data-testid="contact-name"
                  />
                </div>
                <div className="space-y-2">
                  <Label className={`text-sm font-medium text-slate-700 ${isRTL ? 'text-right block' : ''}`}>
                    {isRTL ? 'البريد الإلكتروني' : 'Email'} *
                  </Label>
                  <Input
                    type="email"
                    required
                    value={contactForm.email}
                    onChange={(e) => setContactForm(prev => ({ ...prev, email: e.target.value }))}
                    className={`h-12 bg-slate-50 border-slate-200 focus:border-[#c9a55c] ${isRTL ? 'text-right' : ''}`}
                    data-testid="contact-email"
                  />
                </div>
                <div className="space-y-2">
                  <Label className={`text-sm font-medium text-slate-700 ${isRTL ? 'text-right block' : ''}`}>
                    {isRTL ? 'الموضوع' : 'Subject'} *
                  </Label>
                  <Input
                    required
                    value={contactForm.subject}
                    onChange={(e) => setContactForm(prev => ({ ...prev, subject: e.target.value }))}
                    className={`h-12 bg-slate-50 border-slate-200 focus:border-[#c9a55c] ${isRTL ? 'text-right' : ''}`}
                    data-testid="contact-subject"
                  />
                </div>
                <div className="space-y-2">
                  <Label className={`text-sm font-medium text-slate-700 ${isRTL ? 'text-right block' : ''}`}>
                    {isRTL ? 'الرسالة' : 'Message'} *
                  </Label>
                  <Textarea
                    required
                    rows={4}
                    value={contactForm.message}
                    onChange={(e) => setContactForm(prev => ({ ...prev, message: e.target.value }))}
                    className={`bg-slate-50 border-slate-200 focus:border-[#c9a55c] ${isRTL ? 'text-right' : ''}`}
                    data-testid="contact-message"
                  />
                </div>
                <Button 
                  type="submit"
                  disabled={contactSubmitting}
                  className="w-full h-14 bg-[#1e3a5f] hover:bg-[#152a45] text-white font-semibold"
                  data-testid="contact-submit-btn"
                >
                  {contactSubmitting ? <Loader2 className="w-5 h-5 animate-spin" /> : (
                    <>
                      <Send className={`w-5 h-5 ${isRTL ? 'ml-2' : 'mr-2'}`} />
                      {isRTL ? 'إرسال الرسالة' : 'Send Message'}
                    </>
                  )}
                </Button>
              </div>
            </motion.form>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-[#0f1e31] text-white py-12">
        <div className="max-w-7xl mx-auto px-6 md:px-12">
          <div className={`flex flex-col md:flex-row items-center justify-between gap-6 ${isRTL ? 'md:flex-row-reverse' : ''}`}>
            <img src="/bayan-logo.png" alt="Bayan" className="h-12 brightness-0 invert" />
            <p className="text-white/60 text-sm">
              © {new Date().getFullYear()} Bayan Auditing & Conformity. {isRTL ? 'جميع الحقوق محفوظة' : 'All rights reserved.'}
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default CustomerPortalPage;
