import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { Bell, Check, CheckCheck, FileText, DollarSign, FileSignature, X } from 'lucide-react';
import { Button } from '@/components/ui/button';

const API = process.env.REACT_APP_BACKEND_URL + '/api';

const NotificationBell = () => {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const isRTL = i18n.language?.startsWith('ar');
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const dropdownRef = useRef(null);

  useEffect(() => {
    loadNotifications();
    // Poll for new notifications every 30 seconds
    const interval = setInterval(loadNotifications, 30000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    // Close dropdown when clicking outside
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const loadNotifications = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) return;
      
      const response = await axios.get(`${API}/notifications?limit=10`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setNotifications(response.data.notifications);
      setUnreadCount(response.data.unread_count);
    } catch (error) {
      console.error('Error loading notifications:', error);
    }
  };

  const markAsRead = async (notificationId) => {
    try {
      const token = localStorage.getItem('token');
      await axios.put(`${API}/notifications/${notificationId}/read`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      loadNotifications();
    } catch (error) {
      console.error('Error marking notification as read:', error);
    }
  };

  // Get the navigation URL based on notification type and related item
  const getNavigationUrl = (notification) => {
    const { related_type, related_id } = notification;
    if (!related_type || !related_id) return null;

    switch (related_type) {
      case 'form':
        // Navigate to dashboard with Forms tab, including the form ID as query param
        return `/dashboard?tab=forms&highlight=${related_id}`;
      case 'proposal':
        // Navigate to dashboard with Quotations tab
        return `/dashboard?tab=quotations&highlight=${related_id}`;
      case 'agreement':
        // Navigate to dashboard with Contracts tab
        return `/dashboard?tab=contracts&highlight=${related_id}`;
      default:
        return '/dashboard';
    }
  };

  // Handle notification click - mark as read, navigate, and close dropdown
  const handleNotificationClick = async (notification) => {
    console.log('Notification clicked:', notification);
    
    // Mark as read if not already read
    if (!notification.is_read) {
      await markAsRead(notification.id);
    }

    // Get navigation URL and navigate
    const url = getNavigationUrl(notification);
    console.log('Navigating to:', url);
    
    if (url) {
      setIsOpen(false); // Close dropdown
      
      // Parse the URL to get path and search params
      const [path, queryString] = url.split('?');
      
      console.log('Path:', path, 'Query:', queryString);
      
      // Navigate with search params - use navigate with options
      navigate({
        pathname: path,
        search: queryString ? `?${queryString}` : ''
      });
    }
  };

  const markAllAsRead = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      await axios.put(`${API}/notifications/read-all`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      // Clear all notifications from the dropdown
      setNotifications([]);
      setUnreadCount(0);
      // Keep dropdown open briefly to show empty state, then auto-close
      setTimeout(() => setIsOpen(false), 1000);
    } catch (error) {
      console.error('Error clearing notifications:', error);
    } finally {
      setLoading(false);
    }
  };

  const getNotificationIcon = (type) => {
    switch (type) {
      case 'form_submitted':
        return <FileText className="w-4 h-4 text-blue-500" />;
      case 'proposal_accepted':
        return <Check className="w-4 h-4 text-green-500" />;
      case 'proposal_rejected':
        return <X className="w-4 h-4 text-red-500" />;
      case 'agreement_signed':
        return <FileSignature className="w-4 h-4 text-purple-500" />;
      default:
        return <Bell className="w-4 h-4 text-gray-500" />;
    }
  };

  const formatTime = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return t('justNow');
    if (diffMins < 60) return `${diffMins} ${t('minutesAgo')}`;
    if (diffHours < 24) return `${diffHours} ${t('hoursAgo')}`;
    if (diffDays < 7) return `${diffDays} ${t('daysAgo')}`;
    return date.toLocaleDateString('en-GB');
  };

  return (
    <div className="relative" ref={dropdownRef}>
      {/* Bell Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-full transition-colors"
        data-testid="notification-bell"
      >
        <Bell className="w-5 h-5" />
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs font-bold rounded-full w-5 h-5 flex items-center justify-center">
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}
      </button>

      {/* Dropdown */}
      {isOpen && (
        <div 
          className="absolute top-full mt-2 bg-white rounded-lg shadow-xl border z-50"
          style={{ 
            width: '400px',
            left: '0'
          }}
          data-testid="notification-dropdown"
        >
          {/* Header */}
          <div className={`px-4 py-3 border-b flex items-center justify-between gap-3 ${isRTL ? 'flex-row-reverse' : ''}`}>
            <h3 className="font-semibold text-gray-800">{t('notifications')}</h3>
            {notifications.length > 0 && (
              <button
                onClick={markAllAsRead}
                disabled={loading}
                className="text-sm text-blue-600 hover:text-blue-800 flex items-center gap-1 whitespace-nowrap"
                data-testid="mark-all-read-btn"
              >
                <CheckCheck className="w-4 h-4" />
                <span>{t('markAllRead')}</span>
              </button>
            )}
          </div>

          {/* Notification List */}
          <div className="max-h-96 overflow-y-auto">
            {notifications.length === 0 ? (
              <div className="px-4 py-8 text-center text-gray-500">
                <Bell className="w-8 h-8 mx-auto mb-2 opacity-50" />
                <p>{t('noNotifications')}</p>
              </div>
            ) : (
              notifications.map((notification) => (
                <div
                  key={notification.id}
                  className={`px-4 py-3 border-b last:border-b-0 hover:bg-gray-50 cursor-pointer transition-colors ${
                    !notification.is_read ? 'bg-blue-50' : ''
                  }`}
                  onClick={() => handleNotificationClick(notification)}
                  data-testid={`notification-${notification.id}`}
                >
                  <div className={`flex gap-3 ${isRTL ? 'flex-row-reverse' : ''}`}>
                    <div className="flex-shrink-0 mt-1">
                      {getNotificationIcon(notification.type)}
                    </div>
                    <div className={`flex-1 min-w-0 ${isRTL ? 'text-right' : 'text-left'}`}>
                      <p className={`text-sm font-medium text-gray-800 ${!notification.is_read ? 'font-semibold' : ''}`}>
                        {notification.title}
                      </p>
                      <p className="text-sm text-gray-600 mt-1 break-words leading-relaxed">
                        {notification.message}
                      </p>
                      <p className="text-xs text-gray-400 mt-1">
                        {formatTime(notification.created_at)}
                      </p>
                    </div>
                    {!notification.is_read && (
                      <div className="flex-shrink-0">
                        <span className="w-2 h-2 bg-blue-500 rounded-full block"></span>
                      </div>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>

          {/* Footer */}
          {notifications.length > 0 && (
            <div className="px-4 py-2 border-t bg-gray-50 text-center">
              <button 
                className="text-sm text-blue-600 hover:text-blue-800"
                onClick={() => setIsOpen(false)}
              >
                {t('close')}
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default NotificationBell;
