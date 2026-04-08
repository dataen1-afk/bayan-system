import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import { API } from '@/lib/apiConfig';
import {
  CheckCircle, Building, FileText, Users, AlertCircle, Send
} from 'lucide-react';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';



export default function PublicContractReviewPage() {
  const { accessToken } = useParams();
  const [review, setReview] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState(null);
  
  const [formData, setFormData] = useState({
    consultant_name: '',
    consultant_affects_impartiality: false,
    consultant_impact_explanation: '',
    exclusions_justification: ''
  });
  
  useEffect(() => {
    fetchReview();
  }, [accessToken]);
  
  const fetchReview = async () => {
    try {
      const response = await axios.get(`${API}/public/contract-reviews/${accessToken}`);
      setReview(response.data);
      
      if (response.data.client_submitted) {
        setSubmitted(true);
        setFormData({
          consultant_name: response.data.consultant_name || '',
          consultant_affects_impartiality: response.data.consultant_affects_impartiality || false,
          consultant_impact_explanation: response.data.consultant_impact_explanation || '',
          exclusions_justification: response.data.exclusions_justification || ''
        });
      }
    } catch (err) {
      setError('Contract review not found or link expired');
    } finally {
      setLoading(false);
    }
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    
    try {
      await axios.put(
        `${API}/public/contract-reviews/${accessToken}`,
        formData
      );
      setSubmitted(true);
    } catch (err) {
      setError(err.response?.data?.detail || 'Error submitting data');
    } finally {
      setSubmitting(false);
    }
  };
  
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-600"></div>
      </div>
    );
  }
  
  if (error && !review) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Card className="max-w-md w-full mx-4">
          <CardContent className="p-6 text-center">
            <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
            <h2 className="text-xl font-bold text-gray-900 mb-2">Error</h2>
            <p className="text-gray-600">{error}</p>
          </CardContent>
        </Card>
      </div>
    );
  }
  
  if (submitted) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Card className="max-w-md w-full mx-4">
          <CardContent className="p-6 text-center">
            <CheckCircle className="w-16 h-16 text-emerald-500 mx-auto mb-4" />
            <h2 className="text-xl font-bold text-gray-900 mb-2">Data Submitted Successfully</h2>
            <p className="text-gray-600">
              Thank you for submitting your information for the contract review.
              BAYAN for Verification and Conformity will review your submission and proceed with the audit program.
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-3xl mx-auto px-4">
        {/* Header */}
        <div className="text-center mb-8">
          <img 
            src="/bayan-logo.png" 
            alt="BAYAN" 
            className="h-16 mx-auto mb-4"
            onError={(e) => { e.target.style.display = 'none'; }}
          />
          <h1 className="text-2xl font-bold text-gray-900">Contract Review</h1>
          <p className="text-gray-600">BACF6-04 - Certification Body Application</p>
        </div>
        
        {/* Organization Info Card */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Building className="w-5 h-5 text-emerald-600" />
              Organization Information
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-gray-500">Organization Name:</span>
                <p className="font-semibold text-lg">{review?.organization_name}</p>
              </div>
              <div>
                <span className="text-gray-500">Client ID:</span>
                <p className="font-medium">{review?.client_id}</p>
              </div>
              <div>
                <span className="text-gray-500">Standards:</span>
                <div className="flex flex-wrap gap-1 mt-1">
                  {(review?.standards || []).map((std, idx) => (
                    <span key={idx} className="px-2 py-0.5 bg-blue-100 text-blue-800 text-xs rounded">
                      {std}
                    </span>
                  ))}
                </div>
              </div>
              <div>
                <span className="text-gray-500">Number of Employees:</span>
                <p className="font-medium">{review?.total_employees || 'Not specified'}</p>
              </div>
              <div className="md:col-span-2">
                <span className="text-gray-500">Scope of Services:</span>
                <p className="font-medium">{review?.scope_of_services}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        {/* Client Input Form */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="w-5 h-5 text-emerald-600" />
              Please Complete the Following Information
            </CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Consultant Information */}
              <div className="space-y-4">
                <h3 className="font-semibold flex items-center gap-2">
                  <Users className="w-4 h-4" />
                  Consultant / Business Associates
                </h3>
                
                <div>
                  <Label htmlFor="consultant_name">
                    Name of Consultant/Business Associates (if any)
                  </Label>
                  <Input
                    id="consultant_name"
                    value={formData.consultant_name}
                    onChange={(e) => setFormData({...formData, consultant_name: e.target.value})}
                    placeholder="Enter consultant name or leave blank if none"
                  />
                </div>
                
                <div className="flex items-start gap-3">
                  <input
                    type="checkbox"
                    id="consultant_affects"
                    checked={formData.consultant_affects_impartiality}
                    onChange={(e) => setFormData({...formData, consultant_affects_impartiality: e.target.checked})}
                    className="mt-1"
                  />
                  <Label htmlFor="consultant_affects" className="cursor-pointer">
                    Does the Consultant affect impartial auditing?
                    <p className="text-sm text-gray-500 font-normal">
                      Check this if the consultant was involved in implementing or consulting on your management system
                    </p>
                  </Label>
                </div>
                
                {formData.consultant_affects_impartiality && (
                  <div>
                    <Label htmlFor="consultant_explanation">
                      Please explain how the consultant may affect impartiality
                    </Label>
                    <Textarea
                      id="consultant_explanation"
                      value={formData.consultant_impact_explanation}
                      onChange={(e) => setFormData({...formData, consultant_impact_explanation: e.target.value})}
                      placeholder="Provide details about the consultant's involvement..."
                      rows={3}
                    />
                  </div>
                )}
              </div>
              
              {/* Exclusions */}
              <div className="space-y-4 border-t pt-6">
                <h3 className="font-semibold">Exclusions (Non-Applicable Clauses)</h3>
                
                <div>
                  <Label htmlFor="exclusions">
                    List any standard clauses that are not applicable to your organization with justification
                  </Label>
                  <Textarea
                    id="exclusions"
                    value={formData.exclusions_justification}
                    onChange={(e) => setFormData({...formData, exclusions_justification: e.target.value})}
                    placeholder="e.g., Clause 7.1.5.2 - No monitoring/measuring equipment required for our operations"
                    rows={4}
                  />
                  <p className="text-sm text-gray-500 mt-1">
                    Leave blank if all clauses are applicable to your organization
                  </p>
                </div>
              </div>
              
              {/* Submit */}
              <div className="border-t pt-6">
                <Button 
                  type="submit" 
                  className="w-full bg-emerald-600 hover:bg-emerald-700"
                  disabled={submitting}
                >
                  {submitting ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      Submitting...
                    </>
                  ) : (
                    <>
                      <Send className="w-4 h-4 mr-2" />
                      Submit Information
                    </>
                  )}
                </Button>
                
                {error && (
                  <p className="text-red-500 text-sm text-center mt-2">{error}</p>
                )}
              </div>
            </form>
          </CardContent>
        </Card>
        
        {/* Footer */}
        <div className="text-center mt-8 text-sm text-gray-500">
          <p>BAYAN for Verification and Conformity</p>
          <p>بيان للتحقق والمطابقة</p>
        </div>
      </div>
    </div>
  );
}
