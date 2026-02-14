import React, { useRef, useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Pen, Eraser, Upload, RotateCcw, Check, X } from 'lucide-react';

const SignaturePad = ({ 
  onSignatureChange, 
  onStampChange,
  initialSignature = null,
  initialStamp = null,
  showStamp = true 
}) => {
  const { t, i18n } = useTranslation();
  const isRTL = i18n.language?.startsWith('ar');
  
  const canvasRef = useRef(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const [hasSignature, setHasSignature] = useState(false);
  const [signatureDataUrl, setSignatureDataUrl] = useState(initialSignature);
  const [stampDataUrl, setStampDataUrl] = useState(initialStamp);
  const [useUpload, setUseUpload] = useState(false);
  
  // Initialize canvas
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.strokeStyle = '#000000';
    ctx.lineWidth = 2;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    
    // If we have an initial signature, draw it
    if (initialSignature) {
      const img = new Image();
      img.onload = () => {
        ctx.drawImage(img, 0, 0);
        setHasSignature(true);
      };
      img.src = initialSignature;
    }
  }, [initialSignature]);

  const getCoordinates = (e) => {
    const canvas = canvasRef.current;
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    
    if (e.touches) {
      return {
        x: (e.touches[0].clientX - rect.left) * scaleX,
        y: (e.touches[0].clientY - rect.top) * scaleY
      };
    }
    return {
      x: (e.clientX - rect.left) * scaleX,
      y: (e.clientY - rect.top) * scaleY
    };
  };

  const startDrawing = (e) => {
    e.preventDefault();
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    const { x, y } = getCoordinates(e);
    
    ctx.beginPath();
    ctx.moveTo(x, y);
    setIsDrawing(true);
    setHasSignature(true);
  };

  const draw = (e) => {
    if (!isDrawing) return;
    e.preventDefault();
    
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    const { x, y } = getCoordinates(e);
    
    ctx.lineTo(x, y);
    ctx.stroke();
  };

  const stopDrawing = () => {
    if (!isDrawing) return;
    setIsDrawing(false);
    saveSignature();
  };

  const saveSignature = () => {
    const canvas = canvasRef.current;
    const dataUrl = canvas.toDataURL('image/png');
    setSignatureDataUrl(dataUrl);
    onSignatureChange && onSignatureChange(dataUrl);
  };

  const clearSignature = () => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    setHasSignature(false);
    setSignatureDataUrl(null);
    onSignatureChange && onSignatureChange(null);
  };

  const handleSignatureUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    const reader = new FileReader();
    reader.onload = (event) => {
      const dataUrl = event.target.result;
      setSignatureDataUrl(dataUrl);
      setHasSignature(true);
      onSignatureChange && onSignatureChange(dataUrl);
      
      // Also draw on canvas for preview
      const canvas = canvasRef.current;
      const ctx = canvas.getContext('2d');
      const img = new Image();
      img.onload = () => {
        ctx.fillStyle = '#ffffff';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        // Scale to fit
        const scale = Math.min(canvas.width / img.width, canvas.height / img.height) * 0.9;
        const x = (canvas.width - img.width * scale) / 2;
        const y = (canvas.height - img.height * scale) / 2;
        ctx.drawImage(img, x, y, img.width * scale, img.height * scale);
      };
      img.src = dataUrl;
    };
    reader.readAsDataURL(file);
  };

  const handleStampUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    const reader = new FileReader();
    reader.onload = (event) => {
      const dataUrl = event.target.result;
      setStampDataUrl(dataUrl);
      onStampChange && onStampChange(dataUrl);
    };
    reader.readAsDataURL(file);
  };

  const removeStamp = () => {
    setStampDataUrl(null);
    onStampChange && onStampChange(null);
  };

  return (
    <div className="space-y-6">
      {/* Signature Section */}
      <div className="space-y-3">
        <div className={`flex items-center justify-between ${isRTL ? 'flex-row-reverse' : ''}`}>
          <Label className="text-base font-semibold flex items-center gap-2">
            <Pen className="w-4 h-4" />
            {t('digitalSignature') || 'Digital Signature'} *
          </Label>
          <div className="flex gap-2">
            <Button
              type="button"
              variant={useUpload ? "outline" : "default"}
              size="sm"
              onClick={() => setUseUpload(false)}
              className={!useUpload ? "bg-bayan-navy" : ""}
            >
              <Pen className="w-4 h-4 mr-1" />
              {t('draw') || 'Draw'}
            </Button>
            <Button
              type="button"
              variant={useUpload ? "default" : "outline"}
              size="sm"
              onClick={() => setUseUpload(true)}
              className={useUpload ? "bg-bayan-navy" : ""}
            >
              <Upload className="w-4 h-4 mr-1" />
              {t('upload') || 'Upload'}
            </Button>
          </div>
        </div>

        {!useUpload ? (
          /* Drawing Canvas */
          <div className="space-y-2">
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-2 bg-white">
              <canvas
                ref={canvasRef}
                width={500}
                height={150}
                className="w-full h-36 cursor-crosshair touch-none"
                onMouseDown={startDrawing}
                onMouseMove={draw}
                onMouseUp={stopDrawing}
                onMouseLeave={stopDrawing}
                onTouchStart={startDrawing}
                onTouchMove={draw}
                onTouchEnd={stopDrawing}
                data-testid="signature-canvas"
              />
            </div>
            <div className={`flex gap-2 ${isRTL ? 'flex-row-reverse' : ''}`}>
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={clearSignature}
                className="text-red-600 hover:text-red-700"
              >
                <Eraser className="w-4 h-4 mr-1" />
                {t('clear') || 'Clear'}
              </Button>
              {hasSignature && (
                <span className="text-sm text-green-600 flex items-center gap-1">
                  <Check className="w-4 h-4" />
                  {t('signatureCaptured') || 'Signature captured'}
                </span>
              )}
            </div>
            <p className="text-xs text-gray-500">
              {t('signatureInstructions') || 'Use your mouse or finger to draw your signature above'}
            </p>
          </div>
        ) : (
          /* Upload Option */
          <div className="space-y-2">
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 bg-gray-50 text-center">
              {signatureDataUrl && useUpload ? (
                <div className="space-y-2">
                  <img 
                    src={signatureDataUrl} 
                    alt="Signature" 
                    className="max-h-24 mx-auto"
                  />
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      setSignatureDataUrl(null);
                      onSignatureChange && onSignatureChange(null);
                    }}
                    className="text-red-600"
                  >
                    <X className="w-4 h-4 mr-1" />
                    {t('remove') || 'Remove'}
                  </Button>
                </div>
              ) : (
                <label className="cursor-pointer block">
                  <Upload className="w-8 h-8 mx-auto mb-2 text-gray-400" />
                  <p className="text-sm text-gray-600 mb-1">
                    {t('clickToUploadSignature') || 'Click to upload signature image'}
                  </p>
                  <p className="text-xs text-gray-400">PNG, JPG (max 2MB)</p>
                  <input
                    type="file"
                    accept="image/png,image/jpeg,image/jpg"
                    onChange={handleSignatureUpload}
                    className="hidden"
                    data-testid="signature-upload-input"
                  />
                </label>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Stamp/Seal Section */}
      {showStamp && (
        <div className="space-y-3">
          <Label className="text-base font-semibold flex items-center gap-2">
            <Upload className="w-4 h-4" />
            {t('companySealStamp') || 'Company Seal / Stamp'} ({t('optional') || 'Optional'})
          </Label>
          
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 bg-gray-50 text-center">
            {stampDataUrl ? (
              <div className="space-y-2">
                <img 
                  src={stampDataUrl} 
                  alt="Stamp" 
                  className="max-h-24 mx-auto"
                />
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={removeStamp}
                  className="text-red-600"
                >
                  <X className="w-4 h-4 mr-1" />
                  {t('remove') || 'Remove'}
                </Button>
              </div>
            ) : (
              <label className="cursor-pointer block">
                <Upload className="w-8 h-8 mx-auto mb-2 text-gray-400" />
                <p className="text-sm text-gray-600 mb-1">
                  {t('clickToUploadStamp') || 'Click to upload company seal/stamp'}
                </p>
                <p className="text-xs text-gray-400">PNG, JPG (max 2MB)</p>
                <input
                  type="file"
                  accept="image/png,image/jpeg,image/jpg"
                  onChange={handleStampUpload}
                  className="hidden"
                  data-testid="stamp-upload-input"
                />
              </label>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default SignaturePad;
