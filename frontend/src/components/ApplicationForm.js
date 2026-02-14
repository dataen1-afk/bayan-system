import React, { useState, useEffect, useCallback, useMemo, createContext, useContext } from 'react';
import { useTranslation } from 'react-i18next';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Checkbox } from '@/components/ui/checkbox';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { 
  ChevronLeft, 
  ChevronRight, 
  Check, 
  Building2, 
  FileCheck, 
  Users, 
  Award, 
  ClipboardList,
  PenTool,
  Save
} from 'lucide-react';
import { cn } from '@/lib/utils';

// Context for RTL state
const RTLContext = createContext(false);

// FormField component defined OUTSIDE the main component to prevent re-creation
const FormField = ({ label, required, children, className }) => {
  const isRTL = useContext(RTLContext);
  return (
    <div className={cn("space-y-2", className)}>
      <Label className={cn("font-medium", isRTL && "text-right block")}>
        {label} {required && <span className="text-red-500">*</span>}
      </Label>
      {children}
    </div>
  );
};

const ApplicationForm = ({ onSubmit, onSaveDraft, initialData = null, readOnly = false }) => {
  const { t, i18n } = useTranslation();
  const isRTL = i18n.language?.startsWith('ar');
  
  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData] = useState(initialData || {
    // Step 1: Company Information
    dateOfApplication: new Date().toISOString().split('T')[0],
    companyName: '',
    address: '',
    phoneNumber: '',
    website: '',
    email: '',
    contactPerson: '',
    designation: '',
    mobileNumber: '',
    contactEmail: '',
    legalStatus: '',
    
    // Step 2: Certification Selection
    certificationSchemes: [],
    certificationProgram: '',
    combinedAudit: '',
    combinedAuditSpecification: '',
    isInternalAuditCombined: '',
    isMRMCombined: '',
    isManualProceduresCombined: '',
    isSystemIntegrated: '',
    
    // Step 3: Sites & Employees
    numberOfSites: 1,
    site1Address: '',
    site2Address: '',
    totalEmployees: '',
    locationShifts: '',
    fullTimeEmployees: '',
    partTimeEmployees: '',
    temporaryEmployees: '',
    unskilledWorkers: '',
    remoteEmployees: '',
    
    // Step 4: Existing Certifications
    isAlreadyCertified: '',
    currentCertifications: [{ system: '', body: '', validUntil: '' }],
    isConsultantInvolved: '',
    consultantName: '',
    transferReason: '',
    currentCertificateExpiry: '',
    keyBusinessProcesses: '',
    
    // Step 5: Management System Requirements
    // EMS
    hasEnvironmentAspectRegister: '',
    hasEnvironmentalManual: '',
    hasEnvironmentalAuditProgram: '',
    
    // FSMS
    numberOfHACCPStudies: '',
    numberOfProcessLines: '',
    processingType: '',
    
    // OHSMS
    hazardsIdentified: '',
    criticalRisks: '',
    
    // EnMS
    annualEnergyConsumption: '',
    numberOfEnergySources: '',
    numberOfSEUs: '',
    
    // Medical Devices
    productsInRange: '',
    medicalDeviceTypes: [],
    sterilizationType: '',
    numberOfDeviceFiles: '',
    applicableLegislations: '',
    exportCountries: '',
    productStandards: '',
    intendedUse: '',
    outsourceProcesses: '',
    
    // ISMS
    businessComplexity: '',
    processStandard: '',
    managementSystemLevel: '',
    itEnvironmentComplexity: '',
    outsourcingDependency: '',
    systemDevelopment: '',
    
    // Step 6: Declaration
    declarationName: '',
    declarationDesignation: '',
    declarationAgreed: false,
  });

  const totalSteps = 6;

  const steps = [
    { number: 1, title: t('companyInformation'), icon: Building2 },
    { number: 2, title: t('certificationSelection'), icon: FileCheck },
    { number: 3, title: t('sitesAndEmployees'), icon: Users },
    { number: 4, title: t('existingCertifications'), icon: Award },
    { number: 5, title: t('managementSystems'), icon: ClipboardList },
    { number: 6, title: t('declaration'), icon: PenTool },
  ];

  const certificationOptions = [
    { value: 'ISO9001', label: 'ISO 9001:2015 - Quality Management' },
    { value: 'ISO14001', label: 'ISO 14001:2015 - Environmental Management' },
    { value: 'ISO45001', label: 'ISO 45001:2018 - Occupational Health & Safety' },
    { value: 'ISO27001', label: 'ISO 27001:2022 - Information Security' },
    { value: 'ISO22000', label: 'ISO 22000:2018 - Food Safety' },
    { value: 'ISO50001', label: 'ISO 50001:2018 - Energy Management' },
    { value: 'ISO13485', label: 'ISO 13485:2016 - Medical Devices' },
    { value: 'ISO22301', label: 'ISO 22301:2019 - Business Continuity' },
    { value: 'ISO41001', label: 'ISO 41001:2018 - Facility Management' },
  ];

  const legalStatusOptions = [
    { value: 'private', label: t('privateCompany') },
    { value: 'public', label: t('publicCompany') },
    { value: 'government', label: t('governmentUndertaking') },
    { value: 'psu', label: t('psu') },
    { value: 'proprietorship', label: t('proprietorship') },
    { value: 'ngo', label: t('ngo') },
    { value: 'partnership', label: t('partnership') },
    { value: 'other', label: t('other') },
  ];

  const updateFormData = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleCertificationChange = (value, checked) => {
    const current = formData.certificationSchemes || [];
    if (checked) {
      updateFormData('certificationSchemes', [...current, value]);
    } else {
      updateFormData('certificationSchemes', current.filter(v => v !== value));
    }
  };

  const handleMedicalDeviceTypeChange = (value, checked) => {
    const current = formData.medicalDeviceTypes || [];
    if (checked) {
      updateFormData('medicalDeviceTypes', [...current, value]);
    } else {
      updateFormData('medicalDeviceTypes', current.filter(v => v !== value));
    }
  };

  const addCertificationRow = () => {
    const current = formData.currentCertifications || [];
    updateFormData('currentCertifications', [...current, { system: '', body: '', validUntil: '' }]);
  };

  const updateCertificationRow = (index, field, value) => {
    const current = [...formData.currentCertifications];
    current[index] = { ...current[index], [field]: value };
    updateFormData('currentCertifications', current);
  };

  const removeCertificationRow = (index) => {
    const current = formData.currentCertifications.filter((_, i) => i !== index);
    updateFormData('currentCertifications', current);
  };

  const nextStep = () => {
    if (currentStep < totalSteps) {
      setCurrentStep(currentStep + 1);
    }
  };

  const prevStep = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleSubmit = () => {
    if (onSubmit) {
      onSubmit(formData);
    }
  };

  const handleSaveDraft = () => {
    if (onSaveDraft) {
      onSaveDraft(formData);
    }
  };

  // Check if specific management system section should be shown
  const showEMS = formData.certificationSchemes?.includes('ISO14001');
  const showFSMS = formData.certificationSchemes?.includes('ISO22000');
  const showOHSMS = formData.certificationSchemes?.includes('ISO45001');
  const showEnMS = formData.certificationSchemes?.includes('ISO50001');
  const showMedicalDevices = formData.certificationSchemes?.includes('ISO13485');
  const showISMS = formData.certificationSchemes?.includes('ISO27001');

  // Progress percentage
  const progressPercentage = (currentStep / totalSteps) * 100;

  // Render Step 1: Company Information
  const renderStep1 = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <FormField label={t('dateOfApplication')} required>
          <Input
            type="date"
            value={formData.dateOfApplication}
            onChange={(e) => updateFormData('dateOfApplication', e.target.value)}
            className={isRTL ? 'text-right' : ''}
          />
        </FormField>
        
        <FormField label={t('companyName')} required>
          <Input
            value={formData.companyName}
            onChange={(e) => updateFormData('companyName', e.target.value)}
            placeholder={t('enterCompanyName')}
            className={isRTL ? 'text-right' : ''}
            dir={isRTL ? 'rtl' : 'ltr'}
          />
        </FormField>
      </div>

      <FormField label={t('companyAddress')} required>
        <Textarea
          value={formData.address}
          onChange={(e) => updateFormData('address', e.target.value)}
          placeholder={t('enterCompanyAddress')}
          rows={3}
          className={isRTL ? 'text-right' : ''}
          dir={isRTL ? 'rtl' : 'ltr'}
        />
      </FormField>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <FormField label={t('phoneNumber')} required>
          <Input
            type="tel"
            value={formData.phoneNumber}
            onChange={(e) => updateFormData('phoneNumber', e.target.value)}
            placeholder="+966 XX XXX XXXX"
            dir="ltr"
          />
        </FormField>
        
        <FormField label={t('website')}>
          <Input
            type="url"
            value={formData.website}
            onChange={(e) => updateFormData('website', e.target.value)}
            placeholder="https://www.example.com"
            dir="ltr"
          />
        </FormField>
      </div>

      <FormField label={t('companyEmail')} required>
        <Input
          type="email"
          value={formData.email}
          onChange={(e) => updateFormData('email', e.target.value)}
          placeholder="info@company.com"
          dir="ltr"
        />
      </FormField>

      <div className="border-t pt-6 mt-6">
        <h3 className={cn("text-lg font-semibold mb-4 text-bayan-navy", isRTL && "text-right")}>
          {t('contactPersonDetails')}
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField label={t('contactPersonName')} required>
            <Input
              value={formData.contactPerson}
              onChange={(e) => updateFormData('contactPerson', e.target.value)}
              placeholder={t('enterContactName')}
              className={isRTL ? 'text-right' : ''}
              dir={isRTL ? 'rtl' : 'ltr'}
            />
          </FormField>
          
          <FormField label={t('designation')} required>
            <Input
              value={formData.designation}
              onChange={(e) => updateFormData('designation', e.target.value)}
              placeholder={t('enterDesignation')}
              className={isRTL ? 'text-right' : ''}
              dir={isRTL ? 'rtl' : 'ltr'}
            />
          </FormField>
          
          <FormField label={t('mobileNumber')} required>
            <Input
              type="tel"
              value={formData.mobileNumber}
              onChange={(e) => updateFormData('mobileNumber', e.target.value)}
              placeholder="+966 5X XXX XXXX"
              dir="ltr"
            />
          </FormField>
          
          <FormField label={t('contactEmail')} required>
            <Input
              type="email"
              value={formData.contactEmail}
              onChange={(e) => updateFormData('contactEmail', e.target.value)}
              placeholder="contact@company.com"
              dir="ltr"
            />
          </FormField>
        </div>
      </div>

      <div className="border-t pt-6 mt-6">
        <FormField label={t('legalStatus')} required>
          <Select value={formData.legalStatus} onValueChange={(value) => updateFormData('legalStatus', value)}>
            <SelectTrigger className={isRTL ? 'text-right' : ''}>
              <SelectValue placeholder={t('selectLegalStatus')} />
            </SelectTrigger>
            <SelectContent>
              {legalStatusOptions.map(option => (
                <SelectItem key={option.value} value={option.value}>
                  {option.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </FormField>
      </div>
    </div>
  );

  // Render Step 2: Certification Selection
  const renderStep2 = () => (
    <div className="space-y-6">
      <FormField label={t('selectCertificationSchemes')} required>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mt-2">
          {certificationOptions.map(option => (
            <div key={option.value} className={cn(
              "flex items-center space-x-3 p-3 border rounded-lg hover:bg-slate-50 transition-colors",
              formData.certificationSchemes?.includes(option.value) && "bg-slate-100 border-bayan-navy",
              isRTL && "flex-row-reverse space-x-reverse"
            )}>
              <Checkbox
                id={option.value}
                checked={formData.certificationSchemes?.includes(option.value)}
                onCheckedChange={(checked) => handleCertificationChange(option.value, checked)}
              />
              <label htmlFor={option.value} className="text-sm cursor-pointer flex-1">
                {option.label}
              </label>
            </div>
          ))}
        </div>
      </FormField>

      <div className="border-t pt-6 mt-6">
        <FormField label={t('certificationProgramRequired')} required>
          <RadioGroup
            value={formData.certificationProgram}
            onValueChange={(value) => updateFormData('certificationProgram', value)}
            className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-2"
          >
            {['initial', 'surveillance', 'recertification', 'transfer'].map(type => (
              <div key={type} className={cn(
                "flex items-center space-x-2 p-3 border rounded-lg",
                formData.certificationProgram === type && "bg-slate-100 border-bayan-navy",
                isRTL && "flex-row-reverse space-x-reverse"
              )}>
                <RadioGroupItem value={type} id={type} />
                <Label htmlFor={type} className="cursor-pointer">{t(type)}</Label>
              </div>
            ))}
          </RadioGroup>
        </FormField>
      </div>

      {formData.certificationSchemes?.length > 1 && (
        <div className="border-t pt-6 mt-6 space-y-4">
          <FormField label={t('combinedAuditQuestion')}>
            <RadioGroup
              value={formData.combinedAudit}
              onValueChange={(value) => updateFormData('combinedAudit', value)}
              className={cn("flex gap-4 mt-2", isRTL && "flex-row-reverse")}
            >
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="yes" id="combined-yes" />
                <Label htmlFor="combined-yes">{t('yes')}</Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="no" id="combined-no" />
                <Label htmlFor="combined-no">{t('no')}</Label>
              </div>
            </RadioGroup>
          </FormField>

          {formData.combinedAudit === 'yes' && (
            <>
              <FormField label={t('specifyStandardsCombination')}>
                <Input
                  value={formData.combinedAuditSpecification}
                  onChange={(e) => updateFormData('combinedAuditSpecification', e.target.value)}
                  placeholder={t('enterStandardsCombination')}
                  className={isRTL ? 'text-right' : ''}
                  dir={isRTL ? 'rtl' : 'ltr'}
                />
              </FormField>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <FormField label={t('isInternalAuditCombined')}>
                  <RadioGroup
                    value={formData.isInternalAuditCombined}
                    onValueChange={(value) => updateFormData('isInternalAuditCombined', value)}
                    className="flex gap-4 mt-2"
                  >
                    <div className="flex items-center space-x-2">
                      <RadioGroupItem value="yes" id="internal-yes" />
                      <Label htmlFor="internal-yes">{t('yes')}</Label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <RadioGroupItem value="no" id="internal-no" />
                      <Label htmlFor="internal-no">{t('no')}</Label>
                    </div>
                  </RadioGroup>
                </FormField>

                <FormField label={t('isMRMCombined')}>
                  <RadioGroup
                    value={formData.isMRMCombined}
                    onValueChange={(value) => updateFormData('isMRMCombined', value)}
                    className="flex gap-4 mt-2"
                  >
                    <div className="flex items-center space-x-2">
                      <RadioGroupItem value="yes" id="mrm-yes" />
                      <Label htmlFor="mrm-yes">{t('yes')}</Label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <RadioGroupItem value="no" id="mrm-no" />
                      <Label htmlFor="mrm-no">{t('no')}</Label>
                    </div>
                  </RadioGroup>
                </FormField>

                <FormField label={t('isManualProceduresCombined')}>
                  <RadioGroup
                    value={formData.isManualProceduresCombined}
                    onValueChange={(value) => updateFormData('isManualProceduresCombined', value)}
                    className="flex gap-4 mt-2"
                  >
                    <div className="flex items-center space-x-2">
                      <RadioGroupItem value="yes" id="manual-yes" />
                      <Label htmlFor="manual-yes">{t('yes')}</Label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <RadioGroupItem value="no" id="manual-no" />
                      <Label htmlFor="manual-no">{t('no')}</Label>
                    </div>
                  </RadioGroup>
                </FormField>

                <FormField label={t('isSystemIntegrated')}>
                  <RadioGroup
                    value={formData.isSystemIntegrated}
                    onValueChange={(value) => updateFormData('isSystemIntegrated', value)}
                    className="flex gap-4 mt-2"
                  >
                    <div className="flex items-center space-x-2">
                      <RadioGroupItem value="yes" id="system-yes" />
                      <Label htmlFor="system-yes">{t('yes')}</Label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <RadioGroupItem value="no" id="system-no" />
                      <Label htmlFor="system-no">{t('no')}</Label>
                    </div>
                  </RadioGroup>
                </FormField>
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );

  // Render Step 3: Sites & Employees
  const renderStep3 = () => (
    <div className="space-y-6">
      <FormField label={t('numberOfSites')} required>
        <Input
          type="number"
          min="1"
          value={formData.numberOfSites}
          onChange={(e) => updateFormData('numberOfSites', parseInt(e.target.value) || 1)}
          className="w-32"
          dir="ltr"
        />
      </FormField>

      <FormField label={t('site1Address')} required>
        <Textarea
          value={formData.site1Address}
          onChange={(e) => updateFormData('site1Address', e.target.value)}
          placeholder={t('enterSiteAddress')}
          rows={2}
          className={isRTL ? 'text-right' : ''}
          dir={isRTL ? 'rtl' : 'ltr'}
        />
      </FormField>

      {formData.numberOfSites > 1 && (
        <FormField label={t('site2Address')}>
          <Textarea
            value={formData.site2Address}
            onChange={(e) => updateFormData('site2Address', e.target.value)}
            placeholder={t('enterSiteAddress')}
            rows={2}
            className={isRTL ? 'text-right' : ''}
            dir={isRTL ? 'rtl' : 'ltr'}
          />
          <p className="text-sm text-gray-500 mt-1">{t('attachSeparateSheetForMoreSites')}</p>
        </FormField>
      )}

      <div className="border-t pt-6 mt-6">
        <h3 className={cn("text-lg font-semibold mb-4 text-bayan-navy", isRTL && "text-right")}>
          {t('employeeInformation')}
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <FormField label={t('totalEmployees')} required>
            <Input
              type="number"
              min="0"
              value={formData.totalEmployees}
              onChange={(e) => updateFormData('totalEmployees', e.target.value)}
              dir="ltr"
            />
          </FormField>

          <FormField label={t('locationShifts')}>
            <Input
              value={formData.locationShifts}
              onChange={(e) => updateFormData('locationShifts', e.target.value)}
              placeholder={t('enterShifts')}
              className={isRTL ? 'text-right' : ''}
              dir={isRTL ? 'rtl' : 'ltr'}
            />
          </FormField>

          <FormField label={t('fullTimeEmployees')}>
            <Input
              type="number"
              min="0"
              value={formData.fullTimeEmployees}
              onChange={(e) => updateFormData('fullTimeEmployees', e.target.value)}
              dir="ltr"
            />
          </FormField>

          <FormField label={t('partTimeEmployees')}>
            <Input
              type="number"
              min="0"
              value={formData.partTimeEmployees}
              onChange={(e) => updateFormData('partTimeEmployees', e.target.value)}
              dir="ltr"
            />
          </FormField>

          <FormField label={t('temporaryEmployees')}>
            <Input
              type="number"
              min="0"
              value={formData.temporaryEmployees}
              onChange={(e) => updateFormData('temporaryEmployees', e.target.value)}
              dir="ltr"
            />
          </FormField>

          <FormField label={t('unskilledWorkers')}>
            <Input
              type="number"
              min="0"
              value={formData.unskilledWorkers}
              onChange={(e) => updateFormData('unskilledWorkers', e.target.value)}
              dir="ltr"
            />
          </FormField>

          <FormField label={t('remoteEmployees')} className="md:col-span-3">
            <Input
              type="number"
              min="0"
              value={formData.remoteEmployees}
              onChange={(e) => updateFormData('remoteEmployees', e.target.value)}
              dir="ltr"
              className="w-48"
            />
          </FormField>
        </div>
      </div>
    </div>
  );

  // Render Step 4: Existing Certifications
  const renderStep4 = () => (
    <div className="space-y-6">
      <FormField label={t('isAlreadyCertified')}>
        <RadioGroup
          value={formData.isAlreadyCertified}
          onValueChange={(value) => updateFormData('isAlreadyCertified', value)}
          className={cn("flex gap-4 mt-2", isRTL && "flex-row-reverse")}
        >
          <div className="flex items-center space-x-2">
            <RadioGroupItem value="yes" id="certified-yes" />
            <Label htmlFor="certified-yes">{t('yes')}</Label>
          </div>
          <div className="flex items-center space-x-2">
            <RadioGroupItem value="no" id="certified-no" />
            <Label htmlFor="certified-no">{t('no')}</Label>
          </div>
        </RadioGroup>
      </FormField>

      {formData.isAlreadyCertified === 'yes' && (
        <div className="space-y-4 p-4 bg-slate-50 rounded-lg">
          <h4 className={cn("font-semibold text-bayan-navy", isRTL && "text-right")}>
            {t('currentCertifications')}
          </h4>
          
          {formData.currentCertifications?.map((cert, index) => (
            <div key={index} className="grid grid-cols-1 md:grid-cols-4 gap-3 p-3 bg-white rounded border">
              <Input
                placeholder={t('certificationSystem')}
                value={cert.system}
                onChange={(e) => updateCertificationRow(index, 'system', e.target.value)}
                className={isRTL ? 'text-right' : ''}
                dir={isRTL ? 'rtl' : 'ltr'}
              />
              <Input
                placeholder={t('certificationBody')}
                value={cert.body}
                onChange={(e) => updateCertificationRow(index, 'body', e.target.value)}
                className={isRTL ? 'text-right' : ''}
                dir={isRTL ? 'rtl' : 'ltr'}
              />
              <Input
                type="date"
                placeholder={t('validUntil')}
                value={cert.validUntil}
                onChange={(e) => updateCertificationRow(index, 'validUntil', e.target.value)}
              />
              {formData.currentCertifications.length > 1 && (
                <Button
                  type="button"
                  variant="destructive"
                  size="sm"
                  onClick={() => removeCertificationRow(index)}
                >
                  {t('remove')}
                </Button>
              )}
            </div>
          ))}
          
          <Button type="button" variant="outline" size="sm" onClick={addCertificationRow}>
            + {t('addCertification')}
          </Button>
          
          <p className="text-sm text-gray-500">{t('attachCertificateDocuments')}</p>
        </div>
      )}

      {formData.certificationProgram === 'transfer' && (
        <div className="space-y-4 border-t pt-6">
          <FormField label={t('transferReason')}>
            <Textarea
              value={formData.transferReason}
              onChange={(e) => updateFormData('transferReason', e.target.value)}
              placeholder={t('enterTransferReason')}
              rows={3}
              className={isRTL ? 'text-right' : ''}
              dir={isRTL ? 'rtl' : 'ltr'}
            />
          </FormField>

          <FormField label={t('currentCertificateExpiry')}>
            <Input
              type="date"
              value={formData.currentCertificateExpiry}
              onChange={(e) => updateFormData('currentCertificateExpiry', e.target.value)}
              className="w-48"
            />
          </FormField>
        </div>
      )}

      <div className="border-t pt-6 mt-6">
        <FormField label={t('isConsultantInvolved')}>
          <RadioGroup
            value={formData.isConsultantInvolved}
            onValueChange={(value) => updateFormData('isConsultantInvolved', value)}
            className={cn("flex gap-4 mt-2", isRTL && "flex-row-reverse")}
          >
            <div className="flex items-center space-x-2">
              <RadioGroupItem value="yes" id="consultant-yes" />
              <Label htmlFor="consultant-yes">{t('yes')}</Label>
            </div>
            <div className="flex items-center space-x-2">
              <RadioGroupItem value="no" id="consultant-no" />
              <Label htmlFor="consultant-no">{t('no')}</Label>
            </div>
          </RadioGroup>
        </FormField>

        {formData.isConsultantInvolved === 'yes' && (
          <FormField label={t('consultantName')} className="mt-4">
            <Input
              value={formData.consultantName}
              onChange={(e) => updateFormData('consultantName', e.target.value)}
              placeholder={t('enterConsultantName')}
              className={isRTL ? 'text-right' : ''}
              dir={isRTL ? 'rtl' : 'ltr'}
            />
          </FormField>
        )}
      </div>

      <div className="border-t pt-6 mt-6">
        <FormField label={t('keyBusinessProcesses')} required>
          <Textarea
            value={formData.keyBusinessProcesses}
            onChange={(e) => updateFormData('keyBusinessProcesses', e.target.value)}
            placeholder={t('describeKeyProcesses')}
            rows={4}
            className={isRTL ? 'text-right' : ''}
            dir={isRTL ? 'rtl' : 'ltr'}
          />
        </FormField>
      </div>
    </div>
  );

  // Render Step 5: Management System Requirements (Dynamic based on selected certifications)
  const renderStep5 = () => (
    <div className="space-y-6">
      {!showEMS && !showFSMS && !showOHSMS && !showEnMS && !showMedicalDevices && !showISMS && (
        <div className="text-center py-8 text-gray-500">
          <ClipboardList className="w-16 h-16 mx-auto mb-4 text-gray-300" />
          <p>{t('noAdditionalRequirements')}</p>
          <p className="text-sm mt-2">{t('proceedToNextStep')}</p>
        </div>
      )}

      {/* EMS Section */}
      {showEMS && (
        <Card>
          <CardHeader>
            <CardTitle className={cn("text-bayan-navy", isRTL && "text-right")}>
              {t('environmentalManagementSystem')} (ISO 14001)
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <FormField label={t('hasEnvironmentAspectRegister')}>
              <RadioGroup
                value={formData.hasEnvironmentAspectRegister}
                onValueChange={(value) => updateFormData('hasEnvironmentAspectRegister', value)}
                className="flex gap-4 mt-2"
              >
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="yes" id="env-aspect-yes" />
                  <Label htmlFor="env-aspect-yes">{t('yes')}</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="no" id="env-aspect-no" />
                  <Label htmlFor="env-aspect-no">{t('no')}</Label>
                </div>
              </RadioGroup>
            </FormField>

            <FormField label={t('hasEnvironmentalManual')}>
              <RadioGroup
                value={formData.hasEnvironmentalManual}
                onValueChange={(value) => updateFormData('hasEnvironmentalManual', value)}
                className="flex gap-4 mt-2"
              >
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="yes" id="env-manual-yes" />
                  <Label htmlFor="env-manual-yes">{t('yes')}</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="no" id="env-manual-no" />
                  <Label htmlFor="env-manual-no">{t('no')}</Label>
                </div>
              </RadioGroup>
            </FormField>

            <FormField label={t('hasEnvironmentalAuditProgram')}>
              <RadioGroup
                value={formData.hasEnvironmentalAuditProgram}
                onValueChange={(value) => updateFormData('hasEnvironmentalAuditProgram', value)}
                className="flex gap-4 mt-2"
              >
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="yes" id="env-audit-yes" />
                  <Label htmlFor="env-audit-yes">{t('yes')}</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="no" id="env-audit-no" />
                  <Label htmlFor="env-audit-no">{t('no')}</Label>
                </div>
              </RadioGroup>
            </FormField>
          </CardContent>
        </Card>
      )}

      {/* FSMS Section */}
      {showFSMS && (
        <Card>
          <CardHeader>
            <CardTitle className={cn("text-bayan-navy", isRTL && "text-right")}>
              {t('foodSafetyManagementSystem')} (ISO 22000)
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <FormField label={t('numberOfHACCPStudies')}>
                <Input
                  type="number"
                  min="0"
                  value={formData.numberOfHACCPStudies}
                  onChange={(e) => updateFormData('numberOfHACCPStudies', e.target.value)}
                  dir="ltr"
                />
              </FormField>

              <FormField label={t('numberOfProcessLines')}>
                <Input
                  type="number"
                  min="0"
                  value={formData.numberOfProcessLines}
                  onChange={(e) => updateFormData('numberOfProcessLines', e.target.value)}
                  dir="ltr"
                />
              </FormField>

              <FormField label={t('processingType')}>
                <Select value={formData.processingType} onValueChange={(value) => updateFormData('processingType', value)}>
                  <SelectTrigger>
                    <SelectValue placeholder={t('selectProcessingType')} />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="seasonal">{t('seasonal')}</SelectItem>
                    <SelectItem value="continuous">{t('continuous')}</SelectItem>
                  </SelectContent>
                </Select>
              </FormField>
            </div>
          </CardContent>
        </Card>
      )}

      {/* OHSMS Section */}
      {showOHSMS && (
        <Card>
          <CardHeader>
            <CardTitle className={cn("text-bayan-navy", isRTL && "text-right")}>
              {t('occupationalHealthSafety')} (ISO 45001)
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <FormField label={t('hazardsIdentified')}>
              <RadioGroup
                value={formData.hazardsIdentified}
                onValueChange={(value) => updateFormData('hazardsIdentified', value)}
                className="flex gap-4 mt-2"
              >
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="yes" id="hazards-yes" />
                  <Label htmlFor="hazards-yes">{t('yes')}</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="no" id="hazards-no" />
                  <Label htmlFor="hazards-no">{t('no')}</Label>
                </div>
              </RadioGroup>
            </FormField>

            <FormField label={t('criticalRisks')}>
              <Textarea
                value={formData.criticalRisks}
                onChange={(e) => updateFormData('criticalRisks', e.target.value)}
                placeholder={t('describeCriticalRisks')}
                rows={3}
                className={isRTL ? 'text-right' : ''}
                dir={isRTL ? 'rtl' : 'ltr'}
              />
            </FormField>
          </CardContent>
        </Card>
      )}

      {/* EnMS Section */}
      {showEnMS && (
        <Card>
          <CardHeader>
            <CardTitle className={cn("text-bayan-navy", isRTL && "text-right")}>
              {t('energyManagementSystem')} (ISO 50001)
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <FormField label={t('annualEnergyConsumption')}>
                <Input
                  type="number"
                  step="0.01"
                  value={formData.annualEnergyConsumption}
                  onChange={(e) => updateFormData('annualEnergyConsumption', e.target.value)}
                  placeholder="TJ"
                  dir="ltr"
                />
                <p className="text-xs text-gray-500 mt-1">{t('energyConversionNote')}</p>
              </FormField>

              <FormField label={t('numberOfEnergySources')}>
                <Input
                  type="number"
                  min="0"
                  value={formData.numberOfEnergySources}
                  onChange={(e) => updateFormData('numberOfEnergySources', e.target.value)}
                  dir="ltr"
                />
                <p className="text-xs text-gray-500 mt-1">{t('energySourcesExample')}</p>
              </FormField>

              <FormField label={t('numberOfSEUs')}>
                <Input
                  type="number"
                  min="0"
                  value={formData.numberOfSEUs}
                  onChange={(e) => updateFormData('numberOfSEUs', e.target.value)}
                  dir="ltr"
                />
                <p className="text-xs text-gray-500 mt-1">{t('seusExample')}</p>
              </FormField>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Medical Devices Section */}
      {showMedicalDevices && (
        <Card>
          <CardHeader>
            <CardTitle className={cn("text-bayan-navy", isRTL && "text-right")}>
              {t('medicalDevicesManagement')} (ISO 13485)
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <FormField label={t('productsInRange')}>
              <Textarea
                value={formData.productsInRange}
                onChange={(e) => updateFormData('productsInRange', e.target.value)}
                placeholder={t('listProductsInRange')}
                rows={3}
                className={isRTL ? 'text-right' : ''}
                dir={isRTL ? 'rtl' : 'ltr'}
              />
            </FormField>

            <FormField label={t('medicalDeviceTypes')}>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-2 mt-2">
                {['implantable', 'nonImplantable', 'active', 'nonActive', 'invasive', 'nonInvasive', 'sterile', 'nonSterile'].map(type => (
                  <div key={type} className={cn(
                    "flex items-center space-x-2 p-2 border rounded",
                    formData.medicalDeviceTypes?.includes(type) && "bg-slate-100",
                    isRTL && "flex-row-reverse space-x-reverse"
                  )}>
                    <Checkbox
                      id={`device-${type}`}
                      checked={formData.medicalDeviceTypes?.includes(type)}
                      onCheckedChange={(checked) => handleMedicalDeviceTypeChange(type, checked)}
                    />
                    <label htmlFor={`device-${type}`} className="text-sm cursor-pointer">
                      {t(type)}
                    </label>
                  </div>
                ))}
              </div>
            </FormField>

            {formData.medicalDeviceTypes?.includes('sterile') && (
              <FormField label={t('sterilizationType')}>
                <Input
                  value={formData.sterilizationType}
                  onChange={(e) => updateFormData('sterilizationType', e.target.value)}
                  placeholder={t('specifySterilizationType')}
                  className={isRTL ? 'text-right' : ''}
                  dir={isRTL ? 'rtl' : 'ltr'}
                />
              </FormField>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <FormField label={t('numberOfDeviceFiles')}>
                <Input
                  type="number"
                  min="0"
                  value={formData.numberOfDeviceFiles}
                  onChange={(e) => updateFormData('numberOfDeviceFiles', e.target.value)}
                  dir="ltr"
                />
              </FormField>

              <FormField label={t('exportCountries')}>
                <Input
                  value={formData.exportCountries}
                  onChange={(e) => updateFormData('exportCountries', e.target.value)}
                  placeholder={t('listExportCountries')}
                  className={isRTL ? 'text-right' : ''}
                  dir={isRTL ? 'rtl' : 'ltr'}
                />
              </FormField>
            </div>

            <FormField label={t('intendedUse')}>
              <Textarea
                value={formData.intendedUse}
                onChange={(e) => updateFormData('intendedUse', e.target.value)}
                placeholder={t('describeIntendedUse')}
                rows={3}
                className={isRTL ? 'text-right' : ''}
                dir={isRTL ? 'rtl' : 'ltr'}
              />
            </FormField>
          </CardContent>
        </Card>
      )}

      {/* ISMS Section */}
      {showISMS && (
        <Card>
          <CardHeader>
            <CardTitle className={cn("text-bayan-navy", isRTL && "text-right")}>
              {t('informationSecurityManagement')} (ISO 27001)
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <FormField label={t('businessComplexity')}>
              <RadioGroup
                value={formData.businessComplexity}
                onValueChange={(value) => updateFormData('businessComplexity', value)}
                className="space-y-2 mt-2"
              >
                {['nonCritical', 'customerCritical', 'worksCritical'].map(option => (
                  <div key={option} className={cn(
                    "flex items-center space-x-3 p-3 border rounded-lg",
                    formData.businessComplexity === option && "bg-slate-100 border-bayan-navy",
                    isRTL && "flex-row-reverse space-x-reverse"
                  )}>
                    <RadioGroupItem value={option} id={`business-${option}`} />
                    <Label htmlFor={`business-${option}`} className="cursor-pointer flex-1 text-sm">
                      {t(`isms_${option}`)}
                    </Label>
                  </div>
                ))}
              </RadioGroup>
            </FormField>

            <FormField label={t('itEnvironmentComplexity')}>
              <RadioGroup
                value={formData.itEnvironmentComplexity}
                onValueChange={(value) => updateFormData('itEnvironmentComplexity', value)}
                className="space-y-2 mt-2"
              >
                {['fewPlatforms', 'severalPlatforms', 'manyPlatforms'].map(option => (
                  <div key={option} className={cn(
                    "flex items-center space-x-3 p-3 border rounded-lg",
                    formData.itEnvironmentComplexity === option && "bg-slate-100 border-bayan-navy",
                    isRTL && "flex-row-reverse space-x-reverse"
                  )}>
                    <RadioGroupItem value={option} id={`it-${option}`} />
                    <Label htmlFor={`it-${option}`} className="cursor-pointer flex-1 text-sm">
                      {t(`isms_${option}`)}
                    </Label>
                  </div>
                ))}
              </RadioGroup>
            </FormField>

            <FormField label={t('outsourcingDependency')}>
              <RadioGroup
                value={formData.outsourcingDependency}
                onValueChange={(value) => updateFormData('outsourcingDependency', value)}
                className="space-y-2 mt-2"
              >
                {['littleDependency', 'someDependency', 'highDependency'].map(option => (
                  <div key={option} className={cn(
                    "flex items-center space-x-3 p-3 border rounded-lg",
                    formData.outsourcingDependency === option && "bg-slate-100 border-bayan-navy",
                    isRTL && "flex-row-reverse space-x-reverse"
                  )}>
                    <RadioGroupItem value={option} id={`outsourcing-${option}`} />
                    <Label htmlFor={`outsourcing-${option}`} className="cursor-pointer flex-1 text-sm">
                      {t(`isms_${option}`)}
                    </Label>
                  </div>
                ))}
              </RadioGroup>
            </FormField>
          </CardContent>
        </Card>
      )}
    </div>
  );

  // Render Step 6: Declaration
  const renderStep6 = () => (
    <div className="space-y-6">
      <Card className="border-bayan-navy">
        <CardHeader>
          <CardTitle className={cn("text-bayan-navy", isRTL && "text-right")}>
            {t('declarationTitle')}
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className={cn("p-4 bg-slate-50 rounded-lg", isRTL && "text-right")}>
            <p className="text-sm text-gray-700 leading-relaxed">
              {t('declarationText')}
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <FormField label={t('declarantName')} required>
              <Input
                value={formData.declarationName}
                onChange={(e) => updateFormData('declarationName', e.target.value)}
                placeholder={t('enterYourName')}
                className={isRTL ? 'text-right' : ''}
                dir={isRTL ? 'rtl' : 'ltr'}
              />
            </FormField>

            <FormField label={t('declarantDesignation')} required>
              <Input
                value={formData.declarationDesignation}
                onChange={(e) => updateFormData('declarationDesignation', e.target.value)}
                placeholder={t('enterYourDesignation')}
                className={isRTL ? 'text-right' : ''}
                dir={isRTL ? 'rtl' : 'ltr'}
              />
            </FormField>
          </div>

          <div className={cn(
            "flex items-start space-x-3 p-4 border-2 rounded-lg",
            formData.declarationAgreed ? "border-green-500 bg-green-50" : "border-gray-200",
            isRTL && "flex-row-reverse space-x-reverse"
          )}>
            <Checkbox
              id="declaration-agree"
              checked={formData.declarationAgreed}
              onCheckedChange={(checked) => updateFormData('declarationAgreed', checked)}
              className="mt-1"
            />
            <label htmlFor="declaration-agree" className="text-sm cursor-pointer">
              {t('declarationAgreement')}
            </label>
          </div>
        </CardContent>
      </Card>

      {/* Summary */}
      <Card>
        <CardHeader>
          <CardTitle className={cn("text-bayan-navy", isRTL && "text-right")}>
            {t('applicationSummary')}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div className={cn("space-y-2", isRTL && "text-right")}>
              <p><strong>{t('companyName')}:</strong> {formData.companyName || '-'}</p>
              <p><strong>{t('contactPerson')}:</strong> {formData.contactPerson || '-'}</p>
              <p><strong>{t('email')}:</strong> {formData.email || '-'}</p>
            </div>
            <div className={cn("space-y-2", isRTL && "text-right")}>
              <p><strong>{t('certificationProgram')}:</strong> {formData.certificationProgram ? t(formData.certificationProgram) : '-'}</p>
              <p><strong>{t('selectedStandards')}:</strong> {formData.certificationSchemes?.length || 0}</p>
              <p><strong>{t('totalEmployees')}:</strong> {formData.totalEmployees || '-'}</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );

  // Render current step content
  const renderStepContent = () => {
    switch (currentStep) {
      case 1: return renderStep1();
      case 2: return renderStep2();
      case 3: return renderStep3();
      case 4: return renderStep4();
      case 5: return renderStep5();
      case 6: return renderStep6();
      default: return null;
    }
  };

  return (
    <RTLContext.Provider value={isRTL}>
    <div className="max-w-4xl mx-auto">
      {/* Progress Bar */}
      <div className="mb-8">
        <div className="flex justify-between items-center mb-2">
          {steps.map((step, index) => {
            const Icon = step.icon;
            const isCompleted = currentStep > step.number;
            const isCurrent = currentStep === step.number;
            
            return (
              <div 
                key={step.number}
                className={cn(
                  "flex flex-col items-center",
                  index < steps.length - 1 && "flex-1"
                )}
              >
                <div className={cn(
                  "w-10 h-10 rounded-full flex items-center justify-center border-2 transition-colors",
                  isCompleted && "bg-green-500 border-green-500 text-white",
                  isCurrent && "bg-bayan-navy border-bayan-navy text-white",
                  !isCompleted && !isCurrent && "bg-white border-gray-300 text-gray-400"
                )}>
                  {isCompleted ? (
                    <Check className="w-5 h-5" />
                  ) : (
                    <Icon className="w-5 h-5" />
                  )}
                </div>
                <span className={cn(
                  "text-xs mt-1 text-center hidden md:block",
                  isCurrent && "text-bayan-navy font-semibold",
                  !isCurrent && "text-gray-500"
                )}>
                  {step.title}
                </span>
              </div>
            );
          })}
        </div>
        
        {/* Progress line */}
        <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
          <div 
            className="h-full bg-bayan-navy transition-all duration-300"
            style={{ width: `${progressPercentage}%` }}
          />
        </div>
        <p className={cn("text-sm text-gray-500 mt-2", isRTL && "text-right")}>
          {t('step')} {currentStep} {t('of')} {totalSteps}
        </p>
      </div>

      {/* Step Content */}
      <Card>
        <CardHeader>
          <CardTitle className={cn("text-xl text-bayan-navy", isRTL && "text-right")}>
            {steps[currentStep - 1]?.title}
          </CardTitle>
          <CardDescription className={isRTL ? "text-right" : ""}>
            {t(`step${currentStep}Description`)}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {renderStepContent()}
        </CardContent>
      </Card>

      {/* Navigation Buttons - Correct positioning for RTL */}
      <div className="flex justify-between mt-6" dir={isRTL ? "rtl" : "ltr"}>
        {/* Previous Button - Left in LTR, Right side visually in RTL due to dir */}
        <div>
          {currentStep > 1 && (
            <Button
              type="button"
              variant="outline"
              onClick={prevStep}
              className="flex items-center gap-2"
            >
              {isRTL ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
              {t('previous')}
            </Button>
          )}
        </div>

        {/* Next/Submit Button - Right in LTR, Left side visually in RTL due to dir */}
        <div className="flex gap-2">
          {!readOnly && (
            <Button
              type="button"
              variant="outline"
              onClick={handleSaveDraft}
              className="flex items-center gap-2"
            >
              <Save className="w-4 h-4" />
              {t('saveDraft')}
            </Button>
          )}

          {currentStep < totalSteps ? (
            <Button
              type="button"
              onClick={nextStep}
              className="flex items-center gap-2 bg-bayan-navy hover:bg-bayan-navy-light"
            >
              {t('next')}
              {isRTL ? <ChevronLeft className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
            </Button>
          ) : !readOnly ? (
            <Button
              type="button"
              onClick={handleSubmit}
              disabled={!formData.declarationAgreed}
              className="flex items-center gap-2 bg-green-600 hover:bg-green-700"
            >
              <Check className="w-4 h-4" />
              {t('submitApplication')}
            </Button>
          ) : null}
        </div>
      </div>
    </div>
    </RTLContext.Provider>
  );
};

export default ApplicationForm;
