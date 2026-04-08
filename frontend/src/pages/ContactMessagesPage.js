import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import axios from 'axios';
import { API } from '@/lib/apiConfig';
import {
  MessageSquare, 
  Mail, 
  User, 
  Calendar,
  Check,
  X,
  Trash2,
  Eye,
  Clock,
  Filter,
  Search,
  RefreshCw,
  Download,
  Reply,
  MailOpen,
  Inbox
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { Badge } from '@/components/ui/badge';
import { toast } from 'sonner';



const ContactMessagesPage = () => {
  const { t, i18n } = useTranslation();
  const isRTL = i18n.language?.startsWith('ar');
  
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedMessage, setSelectedMessage] = useState(null);
  const [viewDialogOpen, setViewDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);

  useEffect(() => {
    loadMessages();
  }, [statusFilter]);

  const loadMessages = async () => {
    setLoading(true);
    try {
      const params = statusFilter !== 'all' ? `?status=${statusFilter}` : '';
      const response = await axios.get(`${API}/contact-messages${params}`);
      setMessages(response.data);
    } catch (error) {
      console.error('Error loading messages:', error);
      toast.error(isRTL ? 'خطأ في تحميل الرسائل' : 'Error loading messages');
    } finally {
      setLoading(false);
    }
  };

  const updateStatus = async (messageId, newStatus) => {
    try {
      await axios.put(`${API}/contact-messages/${messageId}?status=${newStatus}`);
      toast.success(isRTL ? 'تم تحديث الحالة' : 'Status updated');
      loadMessages();
      if (newStatus === 'read' && selectedMessage) {
        setSelectedMessage({ ...selectedMessage, status: newStatus });
      }
    } catch (error) {
      console.error('Error updating status:', error);
      toast.error(isRTL ? 'خطأ في تحديث الحالة' : 'Error updating status');
    }
  };

  const deleteMessage = async () => {
    if (!selectedMessage) return;
    try {
      await axios.delete(`${API}/contact-messages/${selectedMessage.id}`);
      toast.success(isRTL ? 'تم حذف الرسالة' : 'Message deleted');
      loadMessages();
      setDeleteDialogOpen(false);
      setViewDialogOpen(false);
      setSelectedMessage(null);
    } catch (error) {
      console.error('Error deleting message:', error);
      toast.error(isRTL ? 'خطأ في حذف الرسالة' : 'Error deleting message');
    }
  };

  const openMessage = (message) => {
    setSelectedMessage(message);
    setViewDialogOpen(true);
    // Mark as read when opened
    if (message.status === 'unread') {
      updateStatus(message.id, 'read');
    }
  };

  const getStatusBadge = (status) => {
    const statusConfig = {
      'unread': { color: 'bg-blue-100 text-blue-800', label: isRTL ? 'غير مقروء' : 'Unread' },
      'read': { color: 'bg-gray-100 text-gray-800', label: isRTL ? 'مقروء' : 'Read' },
      'replied': { color: 'bg-green-100 text-green-800', label: isRTL ? 'تم الرد' : 'Replied' },
      'archived': { color: 'bg-yellow-100 text-yellow-800', label: isRTL ? 'مؤرشف' : 'Archived' },
    };
    const config = statusConfig[status] || statusConfig['unread'];
    return <Badge className={config.color}>{config.label}</Badge>;
  };

  const formatDate = (dateString) => {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString(isRTL ? 'ar-SA' : 'en-GB', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const filteredMessages = messages.filter(msg => {
    if (!searchQuery) return true;
    const query = searchQuery.toLowerCase();
    return (
      msg.name?.toLowerCase().includes(query) ||
      msg.email?.toLowerCase().includes(query) ||
      msg.subject?.toLowerCase().includes(query)
    );
  });

  const exportToCSV = () => {
    const headers = ['Name', 'Email', 'Subject', 'Message', 'Status', 'Date'];
    const rows = filteredMessages.map(msg => [
      msg.name,
      msg.email,
      msg.subject,
      msg.message?.replace(/,/g, ';'),
      msg.status,
      formatDate(msg.created_at)
    ]);
    
    const csvContent = [headers, ...rows].map(row => row.join(',')).join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `contact_messages_${new Date().toISOString().split('T')[0]}.csv`;
    link.click();
  };

  const handleReply = (email, subject) => {
    window.location.href = `mailto:${email}?subject=Re: ${subject}`;
    if (selectedMessage && selectedMessage.status !== 'replied') {
      updateStatus(selectedMessage.id, 'replied');
    }
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className={`flex items-center justify-between ${isRTL ? 'flex-row-reverse' : ''}`}>
        <div>
          <h1 className={`text-2xl font-bold text-gray-900 ${isRTL ? 'text-right' : ''}`}>
            {isRTL ? 'رسائل التواصل' : 'Contact Messages'}
          </h1>
          <p className={`text-gray-500 mt-1 ${isRTL ? 'text-right' : ''}`}>
            {isRTL ? 'إدارة رسائل التواصل من بوابة العملاء' : 'Manage contact messages from the customer portal'}
          </p>
        </div>
        <div className={`flex items-center gap-2 ${isRTL ? 'flex-row-reverse' : ''}`}>
          <Button variant="outline" onClick={loadMessages} disabled={loading}>
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''} ${isRTL ? 'ml-2' : 'mr-2'}`} />
            {isRTL ? 'تحديث' : 'Refresh'}
          </Button>
          <Button variant="outline" onClick={exportToCSV}>
            <Download className={`w-4 h-4 ${isRTL ? 'ml-2' : 'mr-2'}`} />
            {isRTL ? 'تصدير' : 'Export'}
          </Button>
        </div>
      </div>

      {/* Filters */}
      <div className={`flex items-center gap-4 ${isRTL ? 'flex-row-reverse' : ''}`}>
        <div className="relative flex-1 max-w-md">
          <Search className={`absolute top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4 ${isRTL ? 'right-3' : 'left-3'}`} />
          <Input
            placeholder={isRTL ? 'البحث عن اسم أو موضوع...' : 'Search name or subject...'}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className={isRTL ? 'pr-10 text-right' : 'pl-10'}
          />
        </div>
        <Select value={statusFilter} onValueChange={setStatusFilter}>
          <SelectTrigger className="w-48">
            <Filter className={`w-4 h-4 ${isRTL ? 'ml-2' : 'mr-2'}`} />
            <SelectValue placeholder={isRTL ? 'تصفية حسب الحالة' : 'Filter by status'} />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">{isRTL ? 'الكل' : 'All'}</SelectItem>
            <SelectItem value="unread">{isRTL ? 'غير مقروء' : 'Unread'}</SelectItem>
            <SelectItem value="read">{isRTL ? 'مقروء' : 'Read'}</SelectItem>
            <SelectItem value="replied">{isRTL ? 'تم الرد' : 'Replied'}</SelectItem>
            <SelectItem value="archived">{isRTL ? 'مؤرشف' : 'Archived'}</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-blue-50 rounded-lg p-4 border border-blue-100">
          <div className={`flex items-center gap-3 ${isRTL ? 'flex-row-reverse' : ''}`}>
            <div className="p-2 bg-blue-100 rounded-lg">
              <Inbox className="w-5 h-5 text-blue-600" />
            </div>
            <div className={isRTL ? 'text-right' : ''}>
              <p className="text-sm text-blue-600">{isRTL ? 'غير مقروء' : 'Unread'}</p>
              <p className="text-2xl font-bold text-blue-800">
                {messages.filter(m => m.status === 'unread').length}
              </p>
            </div>
          </div>
        </div>
        <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
          <div className={`flex items-center gap-3 ${isRTL ? 'flex-row-reverse' : ''}`}>
            <div className="p-2 bg-gray-100 rounded-lg">
              <MailOpen className="w-5 h-5 text-gray-600" />
            </div>
            <div className={isRTL ? 'text-right' : ''}>
              <p className="text-sm text-gray-600">{isRTL ? 'مقروء' : 'Read'}</p>
              <p className="text-2xl font-bold text-gray-800">
                {messages.filter(m => m.status === 'read').length}
              </p>
            </div>
          </div>
        </div>
        <div className="bg-green-50 rounded-lg p-4 border border-green-100">
          <div className={`flex items-center gap-3 ${isRTL ? 'flex-row-reverse' : ''}`}>
            <div className="p-2 bg-green-100 rounded-lg">
              <Reply className="w-5 h-5 text-green-600" />
            </div>
            <div className={isRTL ? 'text-right' : ''}>
              <p className="text-sm text-green-600">{isRTL ? 'تم الرد' : 'Replied'}</p>
              <p className="text-2xl font-bold text-green-800">
                {messages.filter(m => m.status === 'replied').length}
              </p>
            </div>
          </div>
        </div>
        <div className="bg-yellow-50 rounded-lg p-4 border border-yellow-100">
          <div className={`flex items-center gap-3 ${isRTL ? 'flex-row-reverse' : ''}`}>
            <div className="p-2 bg-yellow-100 rounded-lg">
              <MessageSquare className="w-5 h-5 text-yellow-600" />
            </div>
            <div className={isRTL ? 'text-right' : ''}>
              <p className="text-sm text-yellow-600">{isRTL ? 'الإجمالي' : 'Total'}</p>
              <p className="text-2xl font-bold text-yellow-800">{messages.length}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Messages List */}
      <div className="bg-white rounded-lg border shadow-sm overflow-hidden">
        <div className="divide-y divide-gray-200">
          {loading ? (
            <div className="px-4 py-8 text-center text-gray-500">
              {isRTL ? 'جاري التحميل...' : 'Loading...'}
            </div>
          ) : filteredMessages.length === 0 ? (
            <div className="px-4 py-8 text-center text-gray-500">
              <MessageSquare className="w-12 h-12 mx-auto mb-3 text-gray-300" />
              <p>{isRTL ? 'لا توجد رسائل' : 'No messages found'}</p>
            </div>
          ) : (
            filteredMessages.map((msg) => (
              <div 
                key={msg.id} 
                className={`px-4 py-4 hover:bg-gray-50 cursor-pointer transition-colors ${
                  msg.status === 'unread' ? 'bg-blue-50/50' : ''
                }`}
                onClick={() => openMessage(msg)}
              >
                <div className={`flex items-start gap-4 ${isRTL ? 'flex-row-reverse' : ''}`}>
                  <div className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${
                    msg.status === 'unread' ? 'bg-blue-100' : 'bg-gray-100'
                  }`}>
                    <User className={`w-5 h-5 ${msg.status === 'unread' ? 'text-blue-600' : 'text-gray-500'}`} />
                  </div>
                  <div className={`flex-1 min-w-0 ${isRTL ? 'text-right' : ''}`}>
                    <div className={`flex items-center gap-2 ${isRTL ? 'flex-row-reverse' : ''}`}>
                      <p className={`font-medium ${msg.status === 'unread' ? 'text-gray-900' : 'text-gray-700'}`}>
                        {msg.name}
                      </p>
                      {getStatusBadge(msg.status)}
                    </div>
                    <p className={`text-sm ${msg.status === 'unread' ? 'font-medium text-gray-800' : 'text-gray-600'} mt-1`}>
                      {msg.subject}
                    </p>
                    <p className="text-sm text-gray-500 mt-1 truncate">
                      {msg.message}
                    </p>
                    <div className={`flex items-center gap-4 mt-2 text-xs text-gray-400 ${isRTL ? 'flex-row-reverse' : ''}`}>
                      <span className={`flex items-center gap-1 ${isRTL ? 'flex-row-reverse' : ''}`}>
                        <Mail className="w-3 h-3" />
                        {msg.email}
                      </span>
                      <span className={`flex items-center gap-1 ${isRTL ? 'flex-row-reverse' : ''}`}>
                        <Calendar className="w-3 h-3" />
                        {formatDate(msg.created_at)}
                      </span>
                    </div>
                  </div>
                  <div className={`flex items-center gap-2 ${isRTL ? 'flex-row-reverse' : ''}`}>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="text-red-600 hover:text-red-700"
                      onClick={(e) => { 
                        e.stopPropagation();
                        setSelectedMessage(msg); 
                        setDeleteDialogOpen(true); 
                      }}
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* View Dialog */}
      <Dialog open={viewDialogOpen} onOpenChange={setViewDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle className={isRTL ? 'text-right' : ''}>
              {isRTL ? 'تفاصيل الرسالة' : 'Message Details'}
            </DialogTitle>
          </DialogHeader>
          {selectedMessage && (
            <div className="space-y-4">
              <div className={`flex items-center gap-4 pb-4 border-b ${isRTL ? 'flex-row-reverse' : ''}`}>
                <div className="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center">
                  <User className="w-6 h-6 text-blue-600" />
                </div>
                <div className={`flex-1 ${isRTL ? 'text-right' : ''}`}>
                  <p className="font-semibold text-gray-900">{selectedMessage.name}</p>
                  <p className="text-sm text-gray-500">{selectedMessage.email}</p>
                </div>
                <div className={`text-sm text-gray-400 ${isRTL ? 'text-left' : 'text-right'}`}>
                  {formatDate(selectedMessage.created_at)}
                </div>
              </div>
              
              <div className={`space-y-1 ${isRTL ? 'text-right' : ''}`}>
                <label className="text-sm font-medium text-gray-500">
                  {isRTL ? 'الموضوع' : 'Subject'}
                </label>
                <p className="text-lg font-medium text-gray-900">{selectedMessage.subject}</p>
              </div>
              
              <div className={`space-y-1 ${isRTL ? 'text-right' : ''}`}>
                <label className="text-sm font-medium text-gray-500">
                  {isRTL ? 'الرسالة' : 'Message'}
                </label>
                <div className="bg-gray-50 p-4 rounded-lg whitespace-pre-wrap text-gray-700">
                  {selectedMessage.message}
                </div>
              </div>

              <div className={`flex items-center gap-2 pt-4 border-t ${isRTL ? 'flex-row-reverse' : ''}`}>
                <Button 
                  className="flex-1"
                  onClick={() => handleReply(selectedMessage.email, selectedMessage.subject)}
                >
                  <Reply className={`w-4 h-4 ${isRTL ? 'ml-2' : 'mr-2'}`} />
                  {isRTL ? 'رد بالبريد الإلكتروني' : 'Reply via Email'}
                </Button>
                {selectedMessage.status !== 'archived' && (
                  <Button 
                    variant="outline"
                    onClick={() => updateStatus(selectedMessage.id, 'archived')}
                  >
                    {isRTL ? 'أرشفة' : 'Archive'}
                  </Button>
                )}
                <Button 
                  variant="outline"
                  className="text-red-600 hover:text-red-700"
                  onClick={() => setDeleteDialogOpen(true)}
                >
                  <Trash2 className="w-4 h-4" />
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle className={isRTL ? 'text-right' : ''}>
              {isRTL ? 'تأكيد الحذف' : 'Confirm Delete'}
            </DialogTitle>
          </DialogHeader>
          <p className={`text-gray-600 ${isRTL ? 'text-right' : ''}`}>
            {isRTL 
              ? `هل أنت متأكد من حذف رسالة ${selectedMessage?.name}؟`
              : `Are you sure you want to delete the message from ${selectedMessage?.name}?`
            }
          </p>
          <DialogFooter className={isRTL ? 'flex-row-reverse' : ''}>
            <Button variant="outline" onClick={() => setDeleteDialogOpen(false)}>
              {isRTL ? 'إلغاء' : 'Cancel'}
            </Button>
            <Button variant="destructive" onClick={deleteMessage}>
              {isRTL ? 'حذف' : 'Delete'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default ContactMessagesPage;
