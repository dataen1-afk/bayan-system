import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

const resources = {
  en: {
    translation: {
      // Auth
      "login": "Login",
      "register": "Register",
      "logout": "Logout",
      "signIn": "Sign In",
      "signInToAccount": "Sign in to your account",
      "createAccount": "Create Account",
      "createNewAccount": "Create a new account",
      "email": "Email",
      "password": "Password",
      "fullName": "Full Name",
      "role": "Role",
      "signingIn": "Signing in...",
      "creatingAccount": "Creating account...",
      "dontHaveAccount": "Don't have an account?",
      "alreadyHaveAccount": "Already have an account?",
      "registerHere": "Register here",
      "loginHere": "Login here",
      
      // Roles
      "admin": "Admin",
      "client": "Client",
      
      // Dashboard
      "adminDashboard": "Admin Dashboard",
      "clientDashboard": "Client Dashboard",
      "welcome": "Welcome",
      
      // Tabs
      "forms": "Forms",
      "myForms": "My Forms",
      "quotations": "Quotations",
      "contracts": "Contracts",
      
      // Forms
      "createNewForm": "Create New Form",
      "createCustomForm": "Create a custom form for a client",
      "clientId": "Client ID",
      "enterClientId": "Enter client user ID",
      "formFields": "Form Fields",
      "fieldLabel": "Field label",
      "addField": "Add Field",
      "remove": "Remove",
      "createForm": "Create Form",
      "allForms": "All Forms",
      "noFormsCreated": "No forms created yet",
      "noFormsAssigned": "No forms assigned to you yet",
      "formId": "Form ID",
      "client": "Client",
      "status": "Status",
      "fields": "Fields",
      "pending": "pending",
      "submitted": "submitted",
      "fillForm": "Fill Form",
      "submitForm": "Submit Form",
      "cancel": "Cancel",
      "fillOutForm": "Fill out the form below",
      
      // Field Types
      "text": "Text",
      "textarea": "Textarea",
      "number": "Number",
      
      // Quotations
      "createQuotation": "Create Quotation",
      "createQuotationFor": "Create a quotation for a submitted form",
      "formId": "Form ID",
      "enterFormId": "Enter form ID",
      "enterClientId": "Enter client ID",
      "clientEmail": "Client Email",
      "price": "Price",
      "details": "Details",
      "serviceDetails": "Service details...",
      "allQuotations": "All Quotations",
      "myQuotations": "My Quotations",
      "noQuotationsCreated": "No quotations created yet",
      "noQuotationsReceived": "No quotations received yet",
      "quotationId": "Quotation ID",
      "form": "Form",
      "approved": "approved",
      "rejected": "rejected",
      "approve": "Approve",
      "reject": "Reject",
      
      // Contracts
      "allContracts": "All Contracts",
      "myContracts": "My Contracts",
      "noContractsGenerated": "No contracts generated yet",
      "noContractsAvailable": "No contracts available yet",
      "contractId": "Contract ID",
      "quotation": "Quotation",
      "created": "Created",
      "downloadPdf": "Download PDF",
      
      // Messages
      "formCreatedSuccess": "Form created successfully!",
      "formSubmittedSuccess": "Form submitted successfully!",
      "quotationCreatedSuccess": "Quotation created and email sent!",
      "quotationApproved": "Quotation approved!",
      "quotationRejected": "Quotation rejected!",
      "errorCreatingForm": "Error creating form:",
      "errorSubmittingForm": "Error submitting form:",
      "errorCreatingQuotation": "Error creating quotation:",
      "errorRespondingQuotation": "Error responding to quotation:",
      "errorDownloadingContract": "Error downloading contract:",
      
      // Language
      "language": "Language",
      "english": "English",
      "arabic": "العربية",
      
      // Company
      "serviceContractManagement": "Service Contract Management System",
      
      // Demo Credentials
      "demoCredentials": "Demo Credentials",
      "useTheseCredentials": "Use these credentials to test the system",
      "clickToFill": "Click to fill",
      "adminAccess": "Full access to create forms, quotations, and contracts",
      "clientAccess": "Access to submit forms, review quotations, and download contracts",
      "clickCredentialsTip": "Click on any credential card to auto-fill the login form"
    }
  },
  ar: {
    translation: {
      // Auth
      "login": "تسجيل الدخول",
      "register": "التسجيل",
      "logout": "تسجيل الخروج",
      "signIn": "تسجيل الدخول",
      "signInToAccount": "سجل الدخول إلى حسابك",
      "createAccount": "إنشاء حساب",
      "createNewAccount": "إنشاء حساب جديد",
      "email": "البريد الإلكتروني",
      "password": "كلمة المرور",
      "fullName": "الاسم الكامل",
      "role": "الدور",
      "signingIn": "جاري تسجيل الدخول...",
      "creatingAccount": "جاري إنشاء الحساب...",
      "dontHaveAccount": "ليس لديك حساب؟",
      "alreadyHaveAccount": "لديك حساب بالفعل؟",
      "registerHere": "سجل هنا",
      "loginHere": "سجل الدخول هنا",
      
      // Roles
      "admin": "مدير",
      "client": "عميل",
      
      // Dashboard
      "adminDashboard": "لوحة تحكم المدير",
      "clientDashboard": "لوحة تحكم العميل",
      "welcome": "مرحباً",
      
      // Tabs
      "forms": "النماذج",
      "myForms": "نماذجي",
      "quotations": "عروض الأسعار",
      "contracts": "العقود",
      
      // Forms
      "createNewForm": "إنشاء نموذج جديد",
      "createCustomForm": "إنشاء نموذج مخصص للعميل",
      "clientId": "معرف العميل",
      "enterClientId": "أدخل معرف المستخدم العميل",
      "formFields": "حقول النموذج",
      "fieldLabel": "تسمية الحقل",
      "addField": "إضافة حقل",
      "remove": "إزالة",
      "createForm": "إنشاء نموذج",
      "allForms": "جميع النماذج",
      "noFormsCreated": "لم يتم إنشاء نماذج بعد",
      "noFormsAssigned": "لم يتم تعيين نماذج لك بعد",
      "formId": "معرف النموذج",
      "client": "العميل",
      "status": "الحالة",
      "fields": "الحقول",
      "pending": "قيد الانتظار",
      "submitted": "تم الإرسال",
      "fillForm": "ملء النموذج",
      "submitForm": "إرسال النموذج",
      "cancel": "إلغاء",
      "fillOutForm": "املأ النموذج أدناه",
      
      // Field Types
      "text": "نص",
      "textarea": "نص طويل",
      "number": "رقم",
      
      // Quotations
      "createQuotation": "إنشاء عرض سعر",
      "createQuotationFor": "إنشاء عرض سعر لنموذج مرسل",
      "formId": "معرف النموذج",
      "enterFormId": "أدخل معرف النموذج",
      "enterClientId": "أدخل معرف العميل",
      "clientEmail": "بريد العميل الإلكتروني",
      "price": "السعر",
      "details": "التفاصيل",
      "serviceDetails": "تفاصيل الخدمة...",
      "allQuotations": "جميع عروض الأسعار",
      "myQuotations": "عروض الأسعار الخاصة بي",
      "noQuotationsCreated": "لم يتم إنشاء عروض أسعار بعد",
      "noQuotationsReceived": "لم تستلم عروض أسعار بعد",
      "quotationId": "معرف عرض السعر",
      "form": "النموذج",
      "approved": "موافق عليه",
      "rejected": "مرفوض",
      "approve": "موافقة",
      "reject": "رفض",
      
      // Contracts
      "allContracts": "جميع العقود",
      "myContracts": "عقودي",
      "noContractsGenerated": "لم يتم إنشاء عقود بعد",
      "noContractsAvailable": "لا توجد عقود متاحة بعد",
      "contractId": "معرف العقد",
      "quotation": "عرض السعر",
      "created": "تم الإنشاء",
      "downloadPdf": "تنزيل PDF",
      
      // Messages
      "formCreatedSuccess": "تم إنشاء النموذج بنجاح!",
      "formSubmittedSuccess": "تم إرسال النموذج بنجاح!",
      "quotationCreatedSuccess": "تم إنشاء عرض السعر وإرسال البريد الإلكتروني!",
      "quotationApproved": "تمت الموافقة على عرض السعر!",
      "quotationRejected": "تم رفض عرض السعر!",
      "errorCreatingForm": "خطأ في إنشاء النموذج:",
      "errorSubmittingForm": "خطأ في إرسال النموذج:",
      "errorCreatingQuotation": "خطأ في إنشاء عرض السعر:",
      "errorRespondingQuotation": "خطأ في الرد على عرض السعر:",
      "errorDownloadingContract": "خطأ في تنزيل العقد:",
      
      // Language
      "language": "اللغة",
      "english": "English",
      "arabic": "العربية",
      
      // Company
      "serviceContractManagement": "نظام إدارة عقود الخدمات",
      
      // Demo Credentials
      "demoCredentials": "بيانات تجريبية",
      "useTheseCredentials": "استخدم هذه البيانات لتجربة النظام",
      "clickToFill": "انقر للملء",
      "adminAccess": "صلاحية كاملة لإنشاء النماذج وعروض الأسعار والعقود",
      "clientAccess": "صلاحية لإرسال النماذج ومراجعة عروض الأسعار وتنزيل العقود",
      "clickCredentialsTip": "انقر على أي بطاقة بيانات لملء نموذج تسجيل الدخول تلقائياً"
    }
  }
};

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: 'ar',
    lng: 'ar', // Arabic as default
    interpolation: {
      escapeValue: false
    }
  });

export default i18n;
