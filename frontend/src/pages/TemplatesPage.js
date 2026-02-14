import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { 
  Package, FileText, Plus, Trash2, ArrowLeft, Loader2, 
  Check, DollarSign, Edit, Save, X
} from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL + '/api';

const TemplatesPage = () => {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const isRTL = i18n.language?.startsWith('ar');
  
  const [loading, setLoading] = useState(true);
  const [packages, setPackages] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [activeTab, setActiveTab] = useState('packages');
  const [showAddForm, setShowAddForm] = useState(false);
  const [saving, setSaving] = useState(false);
  const [editingItem, setEditingItem] = useState(null);

  // Form states
  const [newPackage, setNewPackage] = useState({
    name: '', name_ar: '', description: '', description_ar: '', standards: []
  });
  const [newTemplate, setNewTemplate] = useState({
    name: '', name_ar: '', description: '',
    default_fees: { initial_certification: 0, surveillance_1: 0, surveillance_2: 0, recertification: 0 },
    default_notes: '', default_validity_days: 30
  });

  const availableStandards = [
    { id: 'ISO9001', label: 'ISO 9001' },
    { id: 'ISO14001', label: 'ISO 14001' },
    { id: 'ISO45001', label: 'ISO 45001' },
    { id: 'ISO22000', label: 'ISO 22000' },
    { id: 'ISO27001', label: 'ISO 27001' },
    { id: 'ISO13485', label: 'ISO 13485' },
    { id: 'ISO50001', label: 'ISO 50001' },
    { id: 'ISO22301', label: 'ISO 22301' }
  ];

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const headers = { Authorization: `Bearer ${token}` };
      
      const [packagesRes, templatesRes] = await Promise.all([
        axios.get(`${API}/templates/packages`, { headers }),
        axios.get(`${API}/templates/proposals`, { headers })
      ]);
      
      setPackages(packagesRes.data);
      setTemplates(templatesRes.data);
    } catch (error) {
      console.error('Error loading templates:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAddPackage = async () => {
    if (!newPackage.name || !newPackage.name_ar || newPackage.standards.length === 0) {
      alert(t('fillRequiredFields'));
      return;
    }
    
    setSaving(true);
    try {
      const token = localStorage.getItem('token');
      await axios.post(`${API}/templates/packages`, newPackage, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setNewPackage({ name: '', name_ar: '', description: '', description_ar: '', standards: [] });
      setShowAddForm(false);
      loadData();
    } catch (error) {
      console.error('Error adding package:', error);
      alert(t('errorAddingPackage'));
    } finally {
      setSaving(false);
    }
  };

  const handleAddTemplate = async () => {
    if (!newTemplate.name || !newTemplate.name_ar) {
      alert(t('fillRequiredFields'));
      return;
    }
    
    setSaving(true);
    try {
      const token = localStorage.getItem('token');
      await axios.post(`${API}/templates/proposals`, newTemplate, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setNewTemplate({
        name: '', name_ar: '', description: '',
        default_fees: { initial_certification: 0, surveillance_1: 0, surveillance_2: 0, recertification: 0 },
        default_notes: '', default_validity_days: 30
      });
      setShowAddForm(false);
      loadData();
    } catch (error) {
      console.error('Error adding template:', error);
      alert(t('errorAddingTemplate'));
    } finally {
      setSaving(false);
    }
  };

  const handleDeletePackage = async (id) => {
    if (!window.confirm(t('confirmDelete'))) return;
    
    try {
      const token = localStorage.getItem('token');
      await axios.delete(`${API}/templates/packages/${id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      loadData();
    } catch (error) {
      console.error('Error deleting package:', error);
    }
  };

  const handleDeleteTemplate = async (id) => {
    if (!window.confirm(t('confirmDelete'))) return;
    
    try {
      const token = localStorage.getItem('token');
      await axios.delete(`${API}/templates/proposals/${id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      loadData();
    } catch (error) {
      console.error('Error deleting template:', error);
    }
  };

  // Edit handlers
  const handleEditPackage = (pkg) => {
    setEditingItem({ type: 'package', id: pkg.id });
    setNewPackage({
      name: pkg.name || '',
      name_ar: pkg.name_ar || '',
      description: pkg.description || '',
      description_ar: pkg.description_ar || '',
      standards: pkg.standards || []
    });
    setShowAddForm(true);
  };

  const handleEditTemplate = (tmpl) => {
    setEditingItem({ type: 'template', id: tmpl.id });
    setNewTemplate({
      name: tmpl.name || '',
      name_ar: tmpl.name_ar || '',
      description: tmpl.description || '',
      default_fees: tmpl.default_fees || { initial_certification: 0, surveillance_1: 0, surveillance_2: 0, recertification: 0 },
      default_notes: tmpl.default_notes || '',
      default_validity_days: tmpl.default_validity_days || 30
    });
    setShowAddForm(true);
  };

  const handleUpdatePackage = async () => {
    if (!newPackage.name || !newPackage.name_ar || newPackage.standards.length === 0) {
      alert(t('fillRequiredFields'));
      return;
    }
    
    setSaving(true);
    try {
      const token = localStorage.getItem('token');
      await axios.put(`${API}/templates/packages/${editingItem.id}`, newPackage, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setNewPackage({ name: '', name_ar: '', description: '', description_ar: '', standards: [] });
      setShowAddForm(false);
      setEditingItem(null);
      loadData();
    } catch (error) {
      console.error('Error updating package:', error);
      alert(t('errorUpdatingPackage'));
    } finally {
      setSaving(false);
    }
  };

  const handleUpdateTemplate = async () => {
    if (!newTemplate.name || !newTemplate.name_ar) {
      alert(t('fillRequiredFields'));
      return;
    }
    
    setSaving(true);
    try {
      const token = localStorage.getItem('token');
      await axios.put(`${API}/templates/proposals/${editingItem.id}`, newTemplate, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setNewTemplate({
        name: '', name_ar: '', description: '',
        default_fees: { initial_certification: 0, surveillance_1: 0, surveillance_2: 0, recertification: 0 },
        default_notes: '', default_validity_days: 30
      });
      setShowAddForm(false);
      setEditingItem(null);
      loadData();
    } catch (error) {
      console.error('Error updating template:', error);
      alert(t('errorUpdatingTemplate'));
    } finally {
      setSaving(false);
    }
  };

  const cancelEdit = () => {
    setShowAddForm(false);
    setEditingItem(null);
    setNewPackage({ name: '', name_ar: '', description: '', description_ar: '', standards: [] });
    setNewTemplate({
      name: '', name_ar: '', description: '',
      default_fees: { initial_certification: 0, surveillance_1: 0, surveillance_2: 0, recertification: 0 },
      default_notes: '', default_validity_days: 30
    });
  };

  const toggleStandard = (standardId) => {
    setNewPackage(prev => ({
      ...prev,
      standards: prev.standards.includes(standardId)
        ? prev.standards.filter(s => s !== standardId)
        : [...prev.standards, standardId]
    }));
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-bayan-navy" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50" dir={isRTL ? 'rtl' : 'ltr'}>
      {/* Header */}
      <div className="bg-white border-b px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className={`flex items-center gap-4 ${isRTL ? 'flex-row-reverse' : ''}`}>
            <Button 
              variant="ghost" 
              onClick={() => navigate('/dashboard')}
              className={`${isRTL ? 'flex-row-reverse' : ''}`}
            >
              <ArrowLeft className={`w-4 h-4 ${isRTL ? 'ml-2 rotate-180' : 'mr-2'}`} />
              {t('backToDashboard')}
            </Button>
            <h1 className="text-2xl font-bold text-bayan-navy flex items-center gap-2">
              <Package className="w-6 h-6" />
              {t('templatesManagement')}
            </h1>
          </div>
          <Button onClick={() => setShowAddForm(true)}>
            <Plus className="w-4 h-4 mr-2" />
            {activeTab === 'packages' ? t('addPackage') : t('addTemplate')}
          </Button>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Tabs */}
        <div className={`flex gap-4 mb-6 ${isRTL ? 'flex-row-reverse' : ''}`}>
          <Button 
            variant={activeTab === 'packages' ? 'default' : 'outline'}
            onClick={() => { setActiveTab('packages'); setShowAddForm(false); }}
          >
            <Package className="w-4 h-4 mr-2" />
            {t('certificationPackages')}
          </Button>
          <Button 
            variant={activeTab === 'templates' ? 'default' : 'outline'}
            onClick={() => { setActiveTab('templates'); setShowAddForm(false); }}
          >
            <FileText className="w-4 h-4 mr-2" />
            {t('proposalTemplates')}
          </Button>
        </div>

        {/* Add Form */}
        {showAddForm && (
          <Card className="mb-6 border-2 border-blue-200">
            <CardHeader className={isRTL ? 'text-right' : ''}>
              <CardTitle>
                {activeTab === 'packages' ? t('addNewPackage') : t('addNewTemplate')}
              </CardTitle>
            </CardHeader>
            <CardContent>
              {activeTab === 'packages' ? (
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label>{t('nameEnglish')} *</Label>
                      <Input
                        value={newPackage.name}
                        onChange={(e) => setNewPackage({ ...newPackage, name: e.target.value })}
                        placeholder="QMS Basic"
                      />
                    </div>
                    <div>
                      <Label>{t('nameArabic')} *</Label>
                      <Input
                        value={newPackage.name_ar}
                        onChange={(e) => setNewPackage({ ...newPackage, name_ar: e.target.value })}
                        placeholder="نظام إدارة الجودة الأساسي"
                        className="text-right"
                      />
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label>{t('descriptionEnglish')}</Label>
                      <Textarea
                        value={newPackage.description}
                        onChange={(e) => setNewPackage({ ...newPackage, description: e.target.value })}
                        rows={2}
                      />
                    </div>
                    <div>
                      <Label>{t('descriptionArabic')}</Label>
                      <Textarea
                        value={newPackage.description_ar}
                        onChange={(e) => setNewPackage({ ...newPackage, description_ar: e.target.value })}
                        rows={2}
                        className="text-right"
                      />
                    </div>
                  </div>
                  <div>
                    <Label>{t('standards')} *</Label>
                    <div className="flex flex-wrap gap-2 mt-2">
                      {availableStandards.map((std) => (
                        <button
                          key={std.id}
                          type="button"
                          onClick={() => toggleStandard(std.id)}
                          className={`px-3 py-1 rounded-full text-sm border transition-colors ${
                            newPackage.standards.includes(std.id)
                              ? 'bg-blue-500 text-white border-blue-500'
                              : 'bg-white text-gray-600 border-gray-300 hover:border-blue-300'
                          }`}
                        >
                          {std.label}
                        </button>
                      ))}
                    </div>
                  </div>
                  <div className={`flex gap-2 ${isRTL ? 'flex-row-reverse' : ''}`}>
                    <Button onClick={handleAddPackage} disabled={saving}>
                      {saving ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Save className="w-4 h-4 mr-2" />}
                      {t('save')}
                    </Button>
                    <Button variant="outline" onClick={() => setShowAddForm(false)}>
                      <X className="w-4 h-4 mr-2" />
                      {t('cancel')}
                    </Button>
                  </div>
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label>{t('nameEnglish')} *</Label>
                      <Input
                        value={newTemplate.name}
                        onChange={(e) => setNewTemplate({ ...newTemplate, name: e.target.value })}
                        placeholder="Standard Pricing"
                      />
                    </div>
                    <div>
                      <Label>{t('nameArabic')} *</Label>
                      <Input
                        value={newTemplate.name_ar}
                        onChange={(e) => setNewTemplate({ ...newTemplate, name_ar: e.target.value })}
                        placeholder="الأسعار القياسية"
                        className="text-right"
                      />
                    </div>
                  </div>
                  <div>
                    <Label>{t('defaultFees')} (SAR)</Label>
                    <div className="grid grid-cols-4 gap-4 mt-2">
                      <div>
                        <Label className="text-xs">{t('initialCertification')}</Label>
                        <Input
                          type="number"
                          value={newTemplate.default_fees.initial_certification}
                          onChange={(e) => setNewTemplate({
                            ...newTemplate,
                            default_fees: { ...newTemplate.default_fees, initial_certification: Number(e.target.value) }
                          })}
                        />
                      </div>
                      <div>
                        <Label className="text-xs">Surveillance 1</Label>
                        <Input
                          type="number"
                          value={newTemplate.default_fees.surveillance_1}
                          onChange={(e) => setNewTemplate({
                            ...newTemplate,
                            default_fees: { ...newTemplate.default_fees, surveillance_1: Number(e.target.value) }
                          })}
                        />
                      </div>
                      <div>
                        <Label className="text-xs">Surveillance 2</Label>
                        <Input
                          type="number"
                          value={newTemplate.default_fees.surveillance_2}
                          onChange={(e) => setNewTemplate({
                            ...newTemplate,
                            default_fees: { ...newTemplate.default_fees, surveillance_2: Number(e.target.value) }
                          })}
                        />
                      </div>
                      <div>
                        <Label className="text-xs">{t('recertification')}</Label>
                        <Input
                          type="number"
                          value={newTemplate.default_fees.recertification}
                          onChange={(e) => setNewTemplate({
                            ...newTemplate,
                            default_fees: { ...newTemplate.default_fees, recertification: Number(e.target.value) }
                          })}
                        />
                      </div>
                    </div>
                  </div>
                  <div>
                    <Label>{t('defaultNotes')}</Label>
                    <Textarea
                      value={newTemplate.default_notes}
                      onChange={(e) => setNewTemplate({ ...newTemplate, default_notes: e.target.value })}
                      rows={2}
                    />
                  </div>
                  <div className={`flex gap-2 ${isRTL ? 'flex-row-reverse' : ''}`}>
                    <Button onClick={handleAddTemplate} disabled={saving}>
                      {saving ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Save className="w-4 h-4 mr-2" />}
                      {t('save')}
                    </Button>
                    <Button variant="outline" onClick={() => setShowAddForm(false)}>
                      <X className="w-4 h-4 mr-2" />
                      {t('cancel')}
                    </Button>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* Packages Grid */}
        {activeTab === 'packages' && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {packages.map((pkg) => (
              <Card key={pkg.id} className="hover:shadow-lg transition-shadow">
                <CardHeader className={isRTL ? 'text-right' : ''}>
                  <CardTitle className="flex items-center justify-between">
                    <span>{isRTL ? pkg.name_ar : pkg.name}</span>
                    <Button 
                      variant="ghost" 
                      size="icon"
                      onClick={() => handleDeletePackage(pkg.id)}
                      className="text-red-500 hover:text-red-700 hover:bg-red-50"
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </CardTitle>
                  <CardDescription>{isRTL ? pkg.description_ar : pkg.description}</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="flex flex-wrap gap-2">
                    {pkg.standards.map((std) => (
                      <span key={std} className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded-full">
                        {std}
                      </span>
                    ))}
                  </div>
                </CardContent>
              </Card>
            ))}
            {packages.length === 0 && (
              <div className="col-span-full text-center py-12 text-gray-500">
                <Package className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p>{t('noPackagesYet')}</p>
              </div>
            )}
          </div>
        )}

        {/* Templates Grid */}
        {activeTab === 'templates' && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {templates.map((tmpl) => (
              <Card key={tmpl.id} className="hover:shadow-lg transition-shadow">
                <CardHeader className={isRTL ? 'text-right' : ''}>
                  <CardTitle className="flex items-center justify-between">
                    <span>{isRTL ? tmpl.name_ar : tmpl.name}</span>
                    <Button 
                      variant="ghost" 
                      size="icon"
                      onClick={() => handleDeleteTemplate(tmpl.id)}
                      className="text-red-500 hover:text-red-700 hover:bg-red-50"
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </CardTitle>
                  <CardDescription>{tmpl.description}</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2 text-sm">
                    <div className={`flex justify-between ${isRTL ? 'flex-row-reverse' : ''}`}>
                      <span className="text-gray-500">{t('initialCertification')}:</span>
                      <span className="font-medium">SAR {tmpl.default_fees?.initial_certification?.toLocaleString()}</span>
                    </div>
                    <div className={`flex justify-between ${isRTL ? 'flex-row-reverse' : ''}`}>
                      <span className="text-gray-500">{t('recertification')}:</span>
                      <span className="font-medium">SAR {tmpl.default_fees?.recertification?.toLocaleString()}</span>
                    </div>
                    <div className={`flex justify-between ${isRTL ? 'flex-row-reverse' : ''}`}>
                      <span className="text-gray-500">{t('validity')}:</span>
                      <span className="font-medium">{tmpl.default_validity_days} {t('days')}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
            {templates.length === 0 && (
              <div className="col-span-full text-center py-12 text-gray-500">
                <FileText className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p>{t('noTemplatesYet')}</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default TemplatesPage;
