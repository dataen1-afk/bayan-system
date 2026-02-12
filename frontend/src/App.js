import React, { useState, useEffect } from 'react';
import '@/App.css';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import axios from 'axios';
import '@/i18n'; // Initialize i18n
import { useTranslation } from 'react-i18next';
import LoginPage from '@/pages/LoginPage';
import AdminDashboard from '@/pages/AdminDashboard';
import ClientDashboard from '@/pages/ClientDashboard';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
export const API = `${BACKEND_URL}/api`;

// Set up axios defaults
axios.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const AuthContext = React.createContext();

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const { i18n } = useTranslation();

  useEffect(() => {
    // Set initial direction based on stored or default language
    const storedLang = localStorage.getItem('language') || 'ar';
    i18n.changeLanguage(storedLang);
    document.documentElement.dir = storedLang === 'ar' ? 'rtl' : 'ltr';
    document.documentElement.lang = storedLang;
    
    const token = localStorage.getItem('token');
    if (token) {
      // Verify token and get user info
      axios.get(`${API}/auth/me`)
        .then(response => {
          setUser(response.data);
        })
        .catch(() => {
          localStorage.removeItem('token');
        })
        .finally(() => {
          setLoading(false);
        });
    } else {
      setLoading(false);
    }
  }, [i18n]);

  const login = (token, userData) => {
    localStorage.setItem('token', token);
    setUser(userData);
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-xl">Loading...</div>
      </div>
    );
  }

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      <div className="App">
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={!user ? <LoginPage /> : <Navigate to="/dashboard" />} />
            <Route 
              path="/dashboard" 
              element={
                user ? (
                  user.role === 'admin' ? <AdminDashboard /> : <ClientDashboard />
                ) : (
                  <Navigate to="/login" />
                )
              } 
            />
            <Route path="/" element={<Navigate to={user ? "/dashboard" : "/login"} />} />
          </Routes>
        </BrowserRouter>
      </div>
    </AuthContext.Provider>
  );
}

export default App;
