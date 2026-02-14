import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { useTranslation } from 'react-i18next';
import { useNavigate, useParams } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { 
  FileText, ArrowLeft, Plus, X, Download, Trash2, 
  Upload, File, Image, FileArchive, Loader2, AlertCircle,
  Eye, Paperclip
} from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL + '/api';

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

const formatDate = (dateString) => {
  if (!dateString) return '-';
  return new Date(dateString).toLocaleDateString('en-GB', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  });
};

const DocumentManagementPage = ({ relatedId, relatedType }) => {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const isRTL = i18n.language?.startsWith('ar');
  const fileInputRef = useRef(null);
  
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [documents, setDocuments] = useState([]);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [documentName, setDocumentName] = useState('');

  useEffect(() => {
    loadDocuments();
  }, [relatedId]);

  const loadDocuments = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const headers = { Authorization: `Bearer ${token}` };
      
      let url = `${API}/documents`;
      if (relatedId) {
        url += `?related_id=${relatedId}`;
      }
      
      const response = await axios.get(url, { headers });
      setDocuments(response.data);
    } catch (error) {
      console.error('Error loading documents:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedFile(file);
      setDocumentName(file.name);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile || !documentName) return;
    
    setUploading(true);
    try {
      const token = localStorage.getItem('token');
      const headers = { Authorization: `Bearer ${token}` };
      
      // Convert file to base64
      const reader = new FileReader();
      reader.onload = async (e) => {
        const base64Data = e.target.result;
        
        const docData = {
          related_id: relatedId || 'general',
          related_type: relatedType || 'general',
          name: documentName,
          file_type: selectedFile.type || 'application/octet-stream',
          file_data: base64Data
        };
        
        try {
          await axios.post(`${API}/documents`, docData, { headers });
          setShowUploadModal(false);
          setSelectedFile(null);
          setDocumentName('');
          loadDocuments();
        } catch (error) {
          console.error('Error uploading document:', error);
          alert(t('errorUploadingDocument'));
        } finally {
          setUploading(false);
        }
      };
      
      reader.readAsDataURL(selectedFile);
    } catch (error) {
      console.error('Error reading file:', error);
      setUploading(false);
    }
  };

  const handleDownload = async (documentId, documentName) => {
    try {
      const token = localStorage.getItem('token');
      const headers = { Authorization: `Bearer ${token}` };
      
      const response = await axios.get(`${API}/documents/${documentId}`, { headers });
      const { file_data, file_type } = response.data;
      
      // Create download link
      const link = document.createElement('a');
      link.href = file_data;
      link.download = documentName;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (error) {
      console.error('Error downloading document:', error);
    }
  };

  const handleDelete = async (documentId) => {
    if (!window.confirm(t('confirmDeleteDocument') || 'Are you sure you want to delete this document?')) return;
    
    try {
      const token = localStorage.getItem('token');
      const headers = { Authorization: `Bearer ${token}` };
      
      await axios.delete(`${API}/documents/${documentId}`, { headers });
      loadDocuments();
    } catch (error) {
      console.error('Error deleting document:', error);
    }
  };

  const getFileIcon = (fileType) => {
    if (fileType?.startsWith('image/')) return <Image className="w-8 h-8 text-blue-500" />;
    if (fileType?.includes('pdf')) return <FileText className="w-8 h-8 text-red-500" />;
    if (fileType?.includes('zip') || fileType?.includes('rar')) return <FileArchive className="w-8 h-8 text-amber-500" />;
    return <File className="w-8 h-8 text-slate-500" />;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="w-8 h-8 animate-spin text-bayan-navy" />
      </div>
    );
  }

  return (
    <div dir={isRTL ? 'rtl' : 'ltr'}>
      {/* Header */}
      <div className={`flex items-center justify-between mb-6 ${isRTL ? 'flex-row-reverse' : ''}`}>
        <h2 className={`text-xl font-bold text-slate-800 flex items-center gap-2 ${isRTL ? 'flex-row-reverse' : ''}`}>
          <Paperclip className="w-5 h-5 text-bayan-navy" />
          {t('documents')}
        </h2>
        <Button 
          onClick={() => setShowUploadModal(true)}
          className="bg-bayan-navy hover:bg-bayan-navy-light"
          data-testid="upload-document-btn"
        >
          <Upload className="w-4 h-4 me-2" />
          {t('uploadDocument')}
        </Button>
      </div>

      {/* Document List */}
      {documents.length === 0 ? (
        <Card className="text-center py-12">
          <CardContent>
            <FileText className="w-16 h-16 mx-auto text-slate-300 mb-4" />
            <h3 className="text-lg font-semibold text-slate-700 mb-2">{t('noDocumentsYet')}</h3>
            <p className="text-slate-500">{t('uploadFirstDocument')}</p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {documents.map((doc) => (
            <Card 
              key={doc.id} 
              className="hover:shadow-md transition-shadow"
              data-testid={`document-card-${doc.id}`}
            >
              <CardContent className="p-4">
                <div className={`flex items-start gap-3 ${isRTL ? 'flex-row-reverse text-right' : ''}`}>
                  {getFileIcon(doc.file_type)}
                  <div className="flex-1 min-w-0">
                    <h4 className="font-medium text-slate-800 truncate" title={doc.name}>
                      {doc.name}
                    </h4>
                    <p className="text-sm text-slate-500">
                      {formatFileSize(doc.file_size)}
                    </p>
                    <p className="text-xs text-slate-400 mt-1">
                      {formatDate(doc.created_at)}
                    </p>
                  </div>
                </div>
                
                <div className={`flex gap-2 mt-4 ${isRTL ? 'flex-row-reverse' : ''}`}>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleDownload(doc.id, doc.name)}
                    className="flex-1"
                    data-testid={`download-doc-${doc.id}`}
                  >
                    <Download className="w-4 h-4 me-1" />
                    {t('downloadDocument')}
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleDelete(doc.id)}
                    className="text-red-500 hover:text-red-700 hover:bg-red-50"
                    data-testid={`delete-doc-${doc.id}`}
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Upload Modal */}
      {showUploadModal && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <Card className="w-full max-w-md">
            <CardHeader className={isRTL ? 'text-right' : 'text-left'}>
              <div className={`flex justify-between items-center ${isRTL ? 'flex-row-reverse' : ''}`}>
                <CardTitle>{t('uploadDocument')}</CardTitle>
                <Button variant="ghost" size="sm" onClick={() => setShowUploadModal(false)}>
                  <X className="w-4 h-4" />
                </Button>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* File Input */}
              <div className="space-y-2">
                <Label className={isRTL ? 'text-right block' : ''}>{t('selectFile') || 'Select File'} *</Label>
                <div 
                  onClick={() => fileInputRef.current?.click()}
                  className={`
                    border-2 border-dashed border-slate-300 rounded-lg p-8 text-center cursor-pointer
                    hover:border-bayan-navy hover:bg-slate-50 transition-colors
                  `}
                >
                  <input
                    ref={fileInputRef}
                    type="file"
                    onChange={handleFileSelect}
                    className="hidden"
                    data-testid="file-input"
                  />
                  {selectedFile ? (
                    <div className="space-y-2">
                      {getFileIcon(selectedFile.type)}
                      <p className="font-medium text-slate-700">{selectedFile.name}</p>
                      <p className="text-sm text-slate-500">{formatFileSize(selectedFile.size)}</p>
                    </div>
                  ) : (
                    <>
                      <Upload className="w-12 h-12 mx-auto text-slate-400 mb-2" />
                      <p className="text-slate-600">{t('clickToSelectFile') || 'Click to select file'}</p>
                      <p className="text-sm text-slate-400 mt-1">{t('supportedFormats') || 'PDF, Images, Documents'}</p>
                    </>
                  )}
                </div>
              </div>

              {/* Document Name */}
              <div className="space-y-2">
                <Label className={isRTL ? 'text-right block' : ''}>{t('documentName')} *</Label>
                <Input
                  value={documentName}
                  onChange={(e) => setDocumentName(e.target.value)}
                  placeholder={t('enterDocumentName') || 'Enter document name'}
                  data-testid="document-name-input"
                />
              </div>

              <div className={`flex gap-2 pt-4 ${isRTL ? 'flex-row-reverse' : ''}`}>
                <Button variant="outline" onClick={() => setShowUploadModal(false)}>
                  {t('cancel')}
                </Button>
                <Button 
                  onClick={handleUpload}
                  className="bg-bayan-navy hover:bg-bayan-navy-light"
                  disabled={!selectedFile || !documentName || uploading}
                  data-testid="confirm-upload-btn"
                >
                  {uploading ? (
                    <Loader2 className="w-4 h-4 me-2 animate-spin" />
                  ) : (
                    <Upload className="w-4 h-4 me-2" />
                  )}
                  {t('uploadDocument')}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
};

export default DocumentManagementPage;
