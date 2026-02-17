import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import axios from 'axios';
import { 
  Star, Building, Calendar, User, CheckCircle, Send, AlertCircle
} from 'lucide-react';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function PublicFeedbackPage() {
  const { accessToken } = useParams();
  const { t, i18n } = useTranslation();
  const isRTL = i18n.language === 'ar';
  
  const [feedback, setFeedback] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  
  const [ratings, setRatings] = useState({});
  const [wantSameTeam, setWantSameTeam] = useState(null);
  const [suggestions, setSuggestions] = useState('');
  const [respondentName, setRespondentName] = useState('');
  const [respondentDesignation, setRespondentDesignation] = useState('');

  useEffect(() => {
    fetchFeedback();
  }, [accessToken]);

  const fetchFeedback = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/public/feedback/${accessToken}`);
      setFeedback(response.data);
      
      // Initialize ratings
      const initialRatings = {};
      response.data.questions?.forEach((q, idx) => {
        initialRatings[idx] = q.rating || null;
      });
      setRatings(initialRatings);
    } catch (error) {
      console.error('Error fetching feedback:', error);
      if (error.response?.status === 400) {
        setError(isRTL ? 'تم تقديم هذا الاستبيان مسبقاً' : 'This feedback has already been submitted');
      } else {
        setError(isRTL ? 'نموذج الملاحظات غير موجود' : 'Feedback form not found');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleRatingChange = (questionIndex, rating) => {
    setRatings(prev => ({
      ...prev,
      [questionIndex]: rating
    }));
  };

  const handleSubmit = async () => {
    // Validate required fields
    if (!respondentName.trim()) {
      toast.error(isRTL ? 'الرجاء إدخال اسمك' : 'Please enter your name');
      return;
    }

    setSubmitting(true);
    
    try {
      // Prepare questions with ratings
      const questionsData = Object.entries(ratings).map(([index, rating]) => ({
        index: parseInt(index),
        rating: rating
      }));

      const response = await axios.post(`${API_URL}/api/public/feedback/${accessToken}/submit`, {
        questions: questionsData,
        want_same_team: wantSameTeam,
        suggestions: suggestions,
        respondent_name: respondentName,
        respondent_designation: respondentDesignation
      });

      setResult(response.data);
      setSubmitted(true);
      toast.success(isRTL ? 'شكراً لك! تم تقديم ملاحظاتك بنجاح' : 'Thank you! Your feedback has been submitted successfully');
    } catch (error) {
      console.error('Error submitting feedback:', error);
      toast.error(isRTL ? 'حدث خطأ أثناء الإرسال' : 'Error submitting feedback');
    } finally {
      setSubmitting(false);
    }
  };

  const renderStarRating = (questionIndex, currentRating) => {
    return (
      <div className="flex items-center gap-1">
        {[1, 2, 3, 4, 5].map((star) => (
          <button
            key={star}
            type="button"
            onClick={() => handleRatingChange(questionIndex, star)}
            className="p-1 hover:scale-110 transition-transform"
          >
            <Star
              className={`w-8 h-8 ${
                currentRating >= star 
                  ? 'fill-yellow-400 text-yellow-400' 
                  : 'text-gray-300 hover:text-yellow-300'
              }`}
            />
          </button>
        ))}
        <button
          type="button"
          onClick={() => handleRatingChange(questionIndex, 'na')}
          className={`ml-2 px-2 py-1 text-xs rounded ${
            currentRating === 'na' 
              ? 'bg-gray-600 text-white' 
              : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
          }`}
        >
          N/A
        </button>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
        <Card className="max-w-md w-full">
          <CardContent className="p-8 text-center">
            <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
            <h2 className="text-xl font-bold text-gray-800 mb-2">
              {isRTL ? 'عذراً' : 'Sorry'}
            </h2>
            <p className="text-gray-600">{error}</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (submitted) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-emerald-100 flex items-center justify-center p-4">
        <Card className="max-w-md w-full">
          <CardContent className="p-8 text-center">
            <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-gray-800 mb-2">
              {isRTL ? 'شكراً لك!' : 'Thank You!'}
            </h2>
            <p className="text-gray-600 mb-4">
              {isRTL ? 'تم استلام ملاحظاتك بنجاح' : 'Your feedback has been received successfully'}
            </p>
            {result && (
              <div className="p-4 bg-white rounded-lg shadow-inner">
                <p className="text-sm text-gray-500 mb-1">
                  {isRTL ? 'تقييمك العام' : 'Your Overall Score'}
                </p>
                <p className="text-3xl font-bold text-primary">{result.overall_score}%</p>
                <p className={`mt-2 px-3 py-1 rounded-full text-sm font-medium inline-block ${
                  result.evaluation_result === 'excellent' ? 'bg-green-100 text-green-700' :
                  result.evaluation_result === 'good' ? 'bg-blue-100 text-blue-700' :
                  result.evaluation_result === 'average' ? 'bg-yellow-100 text-yellow-700' :
                  'bg-red-100 text-red-700'
                }`}>
                  {result.evaluation_result === 'excellent' ? (isRTL ? 'ممتاز' : 'Excellent') :
                   result.evaluation_result === 'good' ? (isRTL ? 'جيد' : 'Good') :
                   result.evaluation_result === 'average' ? (isRTL ? 'متوسط' : 'Average') :
                   (isRTL ? 'غير مرضٍ' : 'Unsatisfactory')}
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    );
  }

  // Group questions by category
  const questionsByCategory = {};
  feedback?.questions?.forEach((q, idx) => {
    const category = q.category || 'Other';
    if (!questionsByCategory[category]) {
      questionsByCategory[category] = [];
    }
    questionsByCategory[category].push({ ...q, index: idx });
  });

  return (
    <div className={`min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-8 px-4 ${isRTL ? 'rtl' : 'ltr'}`} dir={isRTL ? 'rtl' : 'ltr'}>
      <div className="max-w-3xl mx-auto">
        {/* Header */}
        <Card className="mb-6 overflow-hidden">
          <div className="bg-gradient-to-r from-blue-600 to-indigo-600 p-6 text-white">
            <div className="flex items-center gap-3 mb-2">
              <img 
                src="/bayan-logo.png" 
                alt="BAYAN" 
                className="h-12 w-auto bg-white rounded-lg p-1"
                onError={(e) => e.target.style.display = 'none'}
              />
              <div>
                <h1 className="text-2xl font-bold">
                  {isRTL ? 'استبيان رضا العملاء' : 'Customer Feedback Survey'}
                </h1>
                <p className="text-blue-100 text-sm">BAC-F6-16</p>
              </div>
            </div>
          </div>
          
          <CardContent className="p-6">
            <p className="text-gray-600 mb-4">
              {isRTL 
                ? 'نقدر ملاحظاتك حول خدمات الاعتماد لدينا. ستساعدنا إجاباتك في تحسين جودة خدماتنا.'
                : 'We value your feedback on our certification services. Your responses will help us improve the quality of our services.'}
            </p>
            
            {/* Audit Info */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center gap-2">
                <Building className="w-5 h-5 text-gray-400" />
                <div>
                  <p className="text-xs text-gray-500">{isRTL ? 'المنظمة' : 'Organization'}</p>
                  <p className="text-sm font-medium">{feedback?.organization_name || '-'}</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Calendar className="w-5 h-5 text-gray-400" />
                <div>
                  <p className="text-xs text-gray-500">{isRTL ? 'تاريخ التدقيق' : 'Audit Date'}</p>
                  <p className="text-sm font-medium">{feedback?.audit_date || '-'}</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <User className="w-5 h-5 text-gray-400" />
                <div>
                  <p className="text-xs text-gray-500">{isRTL ? 'المدقق الرئيسي' : 'Lead Auditor'}</p>
                  <p className="text-sm font-medium">{feedback?.lead_auditor || '-'}</p>
                </div>
              </div>
              <div>
                <p className="text-xs text-gray-500">{isRTL ? 'نوع التدقيق' : 'Audit Type'}</p>
                <p className="text-sm font-medium">{feedback?.audit_type || '-'}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Rating Scale Legend */}
        <Card className="mb-6">
          <CardContent className="p-4">
            <p className="text-sm text-gray-600 text-center">
              <span className="font-medium">{isRTL ? 'مقياس التقييم:' : 'Rating Scale:'}</span>
              {' '}
              <Star className="w-4 h-4 inline fill-yellow-400 text-yellow-400" /> 5 = {isRTL ? 'ممتاز' : 'Excellent'},
              4 = {isRTL ? 'جيد جداً' : 'Very Good'},
              3 = {isRTL ? 'جيد' : 'Good'},
              2 = {isRTL ? 'متوسط' : 'Average'},
              1 = {isRTL ? 'ضعيف' : 'Poor'},
              N/A = {isRTL ? 'لا ينطبق' : 'Not Applicable'}
            </p>
          </CardContent>
        </Card>

        {/* Questions by Category */}
        {Object.entries(questionsByCategory).map(([category, questions]) => (
          <Card key={category} className="mb-6">
            <CardHeader className="bg-gradient-to-r from-gray-100 to-gray-50">
              <CardTitle className="text-lg flex items-center justify-between">
                <span>{category}</span>
                <span className="text-sm font-normal text-gray-500">
                  {questions[0]?.category_ar}
                </span>
              </CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              {questions.map((q, qIdx) => (
                <div 
                  key={q.index} 
                  className={`p-4 ${qIdx !== questions.length - 1 ? 'border-b' : ''}`}
                >
                  <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                    <div className="flex-1">
                      <p className="font-medium text-gray-800">{q.question}</p>
                      <p className="text-sm text-gray-500" dir="rtl">{q.question_ar}</p>
                    </div>
                    <div className="flex-shrink-0">
                      {renderStarRating(q.index, ratings[q.index])}
                    </div>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        ))}

        {/* Additional Questions */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="text-lg">
              {isRTL ? 'أسئلة إضافية' : 'Additional Questions'}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Want Same Team */}
            <div>
              <Label className="text-base font-medium">
                {isRTL 
                  ? 'هل تريد أن يقوم نفس فريق التدقيق بتقييم نظامكم في المرة القادمة؟'
                  : 'Do you want this audit team to assess your management system next time?'}
              </Label>
              <div className="flex gap-4 mt-2">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="radio"
                    name="wantSameTeam"
                    checked={wantSameTeam === true}
                    onChange={() => setWantSameTeam(true)}
                    className="w-4 h-4"
                  />
                  <span>{isRTL ? 'نعم' : 'Yes'}</span>
                </label>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="radio"
                    name="wantSameTeam"
                    checked={wantSameTeam === false}
                    onChange={() => setWantSameTeam(false)}
                    className="w-4 h-4"
                  />
                  <span>{isRTL ? 'لا' : 'No'}</span>
                </label>
              </div>
            </div>

            {/* Suggestions */}
            <div>
              <Label className="text-base font-medium">
                {isRTL ? 'اقتراحاتكم' : 'Your Suggestions'}
              </Label>
              <Textarea
                value={suggestions}
                onChange={(e) => setSuggestions(e.target.value)}
                placeholder={isRTL ? 'شاركنا اقتراحاتكم لتحسين خدماتنا...' : 'Share your suggestions to improve our services...'}
                className="mt-2"
                rows={4}
              />
            </div>
          </CardContent>
        </Card>

        {/* Respondent Information */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="text-lg">
              {isRTL ? 'معلومات المستجيب' : 'Respondent Information'}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label>{isRTL ? 'الاسم' : 'Name'} *</Label>
                <Input
                  value={respondentName}
                  onChange={(e) => setRespondentName(e.target.value)}
                  placeholder={isRTL ? 'أدخل اسمك' : 'Enter your name'}
                  className="mt-1"
                />
              </div>
              <div>
                <Label>{isRTL ? 'المنصب' : 'Designation'}</Label>
                <Input
                  value={respondentDesignation}
                  onChange={(e) => setRespondentDesignation(e.target.value)}
                  placeholder={isRTL ? 'أدخل منصبك' : 'Enter your designation'}
                  className="mt-1"
                />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Submit Button */}
        <div className="text-center">
          <Button 
            size="lg" 
            onClick={handleSubmit} 
            disabled={submitting}
            className="px-8 py-6 text-lg"
          >
            {submitting ? (
              <div className="flex items-center gap-2">
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                {isRTL ? 'جارٍ الإرسال...' : 'Submitting...'}
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <Send className="w-5 h-5" />
                {isRTL ? 'إرسال الملاحظات' : 'Submit Feedback'}
              </div>
            )}
          </Button>
          <p className="text-sm text-gray-500 mt-4">
            {isRTL 
              ? 'شكراً لك على الوقت الذي خصصته لمشاركة ملاحظاتك'
              : 'Thank you for taking the time to share your feedback'}
          </p>
        </div>
      </div>
    </div>
  );
}
