import React, { useState, useEffect, useContext } from 'react';
import axios from 'axios';
import { useTranslation } from 'react-i18next';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { 
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter 
} from '@/components/ui/dialog';
import {
  AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent,
  AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle
} from '@/components/ui/alert-dialog';
import { 
  Users, UserPlus, Search, Edit, Shield, Mail, Phone, 
  Building, CheckCircle, Trash2, Eye, EyeOff, UserCog, Crown
} from 'lucide-react';
import { AuthContext } from '@/App';
import { toast } from 'sonner';

const API = process.env.REACT_APP_BACKEND_URL + '/api';

const UserManagementTab = () => {
  const { t, i18n } = useTranslation();
  const { user } = useContext(AuthContext);
  const isRTL = i18n.language?.startsWith('ar');
  
  // Check if current user is system admin
  const isSystemAdmin = user?.role === 'system_admin' || user?.role === 'admin';
  
  const [loading, setLoading] = useState(true);
  const [users, setUsers] = useState([]);
  const [roles, setRoles] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [roleFilter, setRoleFilter] = useState('all');
  
  // Modals
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditRoleModal, setShowEditRoleModal] = useState(false);
  const [showEditUserModal, setShowEditUserModal] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);
  const [showPassword, setShowPassword] = useState(false);
  
  // Form state
  const [formData, setFormData] = useState({
    name: '',
    name_ar: '',
    email: '',
    password: '',
    phone: '',
    department: '',
    role: 'auditor'
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const token = localStorage.getItem('token');
      const headers = { Authorization: `Bearer ${token}` };
      
      const [usersRes, rolesRes] = await Promise.all([
        axios.get(`${API}/users`, { headers }),
        axios.get(`${API}/roles/staff`, { headers })
      ]);
      
      setUsers(usersRes.data.users || []);
      setRoles(rolesRes.data.roles || []);
    } catch (error) {
      console.error('Error loading data:', error);
      toast.error(isRTL ? 'خطأ في تحميل البيانات' : 'Error loading data');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateUser = async () => {
    try {
      const token = localStorage.getItem('token');
      await axios.post(`${API}/users/create-staff`, formData, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      toast.success(isRTL ? 'تم إنشاء المستخدم بنجاح' : 'User created successfully');
      setShowCreateModal(false);
      setFormData({
        name: '',
        name_ar: '',
        email: '',
        password: '',
        phone: '',
        department: '',
        role: 'auditor'
      });
      loadData();
    } catch (error) {
      console.error('Error creating user:', error);
      toast.error(error.response?.data?.detail || (isRTL ? 'خطأ في إنشاء المستخدم' : 'Error creating user'));
    }
  };

  const handleUpdateRole = async () => {
    if (!selectedUser) return;
    
    try {
      const token = localStorage.getItem('token');
      await axios.put(`${API}/users/${selectedUser.id}/role`, 
        { role: selectedUser.newRole },
        { headers: { Authorization: `Bearer ${token}` }}
      );
      
      toast.success(isRTL ? 'تم تحديث الدور بنجاح' : 'Role updated successfully');
      setShowEditRoleModal(false);
      setSelectedUser(null);
      loadData();
    } catch (error) {
      console.error('Error updating role:', error);
      toast.error(error.response?.data?.detail || (isRTL ? 'خطأ في تحديث الدور' : 'Error updating role'));
    }
  };

  const handleEditUser = async () => {
    if (!selectedUser) return;
    
    try {
      const token = localStorage.getItem('token');
      const updateData = {
        name: selectedUser.name,
        name_ar: selectedUser.name_ar,
        email: selectedUser.email,
        phone: selectedUser.phone,
        department: selectedUser.department,
        role: selectedUser.role
      };
      
      // Only include password if it was changed
      if (selectedUser.newPassword) {
        updateData.password = selectedUser.newPassword;
      }
      
      await axios.put(`${API}/users/${selectedUser.id}`, updateData, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      toast.success(isRTL ? 'تم تحديث المستخدم بنجاح' : 'User updated successfully');
      setShowEditUserModal(false);
      setSelectedUser(null);
      loadData();
    } catch (error) {
      console.error('Error updating user:', error);
      toast.error(error.response?.data?.detail || (isRTL ? 'خطأ في تحديث المستخدم' : 'Error updating user'));
    }
  };

  const handleDeleteUser = async () => {
    if (!selectedUser) return;
    
    try {
      const token = localStorage.getItem('token');
      await axios.delete(`${API}/users/${selectedUser.id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      toast.success(isRTL ? 'تم حذف المستخدم بنجاح' : 'User deleted successfully');
      setShowDeleteConfirm(false);
      setSelectedUser(null);
      loadData();
    } catch (error) {
      console.error('Error deleting user:', error);
      toast.error(error.response?.data?.detail || (isRTL ? 'خطأ في حذف المستخدم' : 'Error deleting user'));
    }
  };

  const filteredUsers = users.filter(u => {
    const matchesSearch = 
      u.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      u.name_ar?.includes(searchTerm) ||
      u.email?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesRole = roleFilter === 'all' || u.role === roleFilter;
    return matchesSearch && matchesRole;
  });

  const getRoleColor = (role) => {
    const colors = {
      system_admin: 'bg-red-100 text-red-800 ring-2 ring-red-300',
      ceo: 'bg-purple-100 text-purple-800',
      general_manager: 'bg-indigo-100 text-indigo-800',
      admin: 'bg-red-100 text-red-800',
      quality_manager: 'bg-blue-100 text-blue-800',
      certification_manager: 'bg-cyan-100 text-cyan-800',
      operation_coordinator: 'bg-green-100 text-green-800',
      marketing_manager: 'bg-pink-100 text-pink-800',
      financial_manager: 'bg-yellow-100 text-yellow-800',
      hr_manager: 'bg-orange-100 text-orange-800',
      lead_auditor: 'bg-teal-100 text-teal-800',
      auditor: 'bg-emerald-100 text-emerald-800',
      technical_expert: 'bg-slate-100 text-slate-800',
      client: 'bg-gray-100 text-gray-800'
    };
    return colors[role] || 'bg-gray-100 text-gray-800';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#1e3a5f]"></div>
      </div>
    );
  }

  return (
    <div className={isRTL ? 'rtl' : 'ltr'}>
      {/* Header */}
      <div className={`flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6 ${isRTL ? 'sm:flex-row-reverse' : ''}`}>
        <div>
          <h2 className={`text-xl font-bold text-[#1e3a5f] flex items-center gap-2 ${isRTL ? 'flex-row-reverse' : ''}`}>
            <Users className="w-6 h-6" />
            {isRTL ? 'إدارة المستخدمين' : 'User Management'}
          </h2>
          <p className="text-slate-600 text-sm mt-1">
            {isRTL ? 'إدارة حسابات المستخدمين والأدوار' : 'Manage user accounts and roles'}
          </p>
        </div>
        <Button 
          onClick={() => setShowCreateModal(true)}
          className="bg-[#1e3a5f] hover:bg-[#152a45] gap-2"
        >
          <UserPlus className="w-4 h-4" />
          {isRTL ? 'إضافة مستخدم' : 'Add User'}
        </Button>
      </div>

      {/* Filters */}
      <Card className="mb-6">
        <CardContent className="p-4">
          <div className={`flex flex-col sm:flex-row gap-4 ${isRTL ? 'sm:flex-row-reverse' : ''}`}>
            <div className="flex-1 relative">
              <Search className={`absolute top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 ${isRTL ? 'right-3' : 'left-3'}`} />
              <Input
                placeholder={isRTL ? 'بحث بالاسم أو البريد...' : 'Search by name or email...'}
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className={isRTL ? 'pr-10 text-right' : 'pl-10'}
              />
            </div>
            <Select value={roleFilter} onValueChange={setRoleFilter}>
              <SelectTrigger className="w-full sm:w-[200px]">
                <SelectValue placeholder={isRTL ? 'جميع الأدوار' : 'All Roles'} />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">{isRTL ? 'جميع الأدوار' : 'All Roles'}</SelectItem>
                {roles.map(role => (
                  <SelectItem key={role.id} value={role.id}>
                    {isRTL ? role.name_ar : role.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <Card>
          <CardContent className="p-4">
            <div className={`flex items-center gap-3 ${isRTL ? 'flex-row-reverse' : ''}`}>
              <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                <Users className="w-5 h-5 text-blue-600" />
              </div>
              <div className={isRTL ? 'text-right' : ''}>
                <p className="text-2xl font-bold text-[#1e3a5f]">{users.length}</p>
                <p className="text-xs text-slate-500">{isRTL ? 'إجمالي المستخدمين' : 'Total Users'}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className={`flex items-center gap-3 ${isRTL ? 'flex-row-reverse' : ''}`}>
              <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                <Shield className="w-5 h-5 text-green-600" />
              </div>
              <div className={isRTL ? 'text-right' : ''}>
                <p className="text-2xl font-bold text-[#1e3a5f]">
                  {users.filter(u => ['ceo', 'general_manager', 'admin'].includes(u.role)).length}
                </p>
                <p className="text-xs text-slate-500">{isRTL ? 'الإدارة' : 'Management'}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className={`flex items-center gap-3 ${isRTL ? 'flex-row-reverse' : ''}`}>
              <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                <CheckCircle className="w-5 h-5 text-purple-600" />
              </div>
              <div className={isRTL ? 'text-right' : ''}>
                <p className="text-2xl font-bold text-[#1e3a5f]">
                  {users.filter(u => ['lead_auditor', 'auditor', 'technical_expert'].includes(u.role)).length}
                </p>
                <p className="text-xs text-slate-500">{isRTL ? 'المدققين' : 'Auditors'}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className={`flex items-center gap-3 ${isRTL ? 'flex-row-reverse' : ''}`}>
              <div className="w-10 h-10 bg-amber-100 rounded-lg flex items-center justify-center">
                <Building className="w-5 h-5 text-amber-600" />
              </div>
              <div className={isRTL ? 'text-right' : ''}>
                <p className="text-2xl font-bold text-[#1e3a5f]">
                  {users.filter(u => u.role === 'client').length}
                </p>
                <p className="text-xs text-slate-500">{isRTL ? 'العملاء' : 'Clients'}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Users Table */}
      <Card>
        <CardHeader>
          <CardTitle className={isRTL ? 'text-right' : ''}>
            {isRTL ? 'قائمة المستخدمين' : 'Users List'}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto" dir={isRTL ? 'rtl' : 'ltr'}>
            <table className="w-full">
              <thead>
                <tr className={`border-b ${isRTL ? 'text-right' : 'text-left'}`}>
                  {isRTL ? (
                    <>
                      <th className="pb-3 font-medium text-slate-600">المستخدم</th>
                      <th className="pb-3 font-medium text-slate-600">البريد الإلكتروني</th>
                      <th className="pb-3 font-medium text-slate-600">الدور</th>
                      <th className="pb-3 font-medium text-slate-600">القسم</th>
                      <th className="pb-3 font-medium text-slate-600">الإجراءات</th>
                    </>
                  ) : (
                    <>
                      <th className="pb-3 font-medium text-slate-600">User</th>
                      <th className="pb-3 font-medium text-slate-600">Email</th>
                      <th className="pb-3 font-medium text-slate-600">Role</th>
                      <th className="pb-3 font-medium text-slate-600">Department</th>
                      <th className="pb-3 font-medium text-slate-600">Actions</th>
                    </>
                  )}
                </tr>
              </thead>
              <tbody>
                {filteredUsers.map((u) => (
                  <tr key={u.id} className="border-b hover:bg-slate-50">
                    {/* User Column */}
                    <td className="py-4">
                      <div className={`flex items-center gap-3 ${isRTL ? 'flex-row-reverse justify-end' : ''}`}>
                        <div className="w-10 h-10 bg-[#1e3a5f] rounded-full flex items-center justify-center text-white font-semibold">
                          {(u.name || u.email || '?').charAt(0).toUpperCase()}
                        </div>
                        <div className={isRTL ? 'text-right' : ''}>
                          <p className="font-medium text-slate-800">{isRTL ? (u.name_ar || u.name) : u.name}</p>
                          {u.phone && (
                            <p className={`text-xs text-slate-500 flex items-center gap-1 ${isRTL ? 'flex-row-reverse justify-end' : ''}`}>
                              <Phone className="w-3 h-3" /> {u.phone}
                            </p>
                          )}
                        </div>
                      </div>
                    </td>
                    {/* Email Column */}
                    <td className="py-4">
                      <div className={`flex items-center gap-1 text-slate-600 ${isRTL ? 'flex-row-reverse justify-end' : ''}`}>
                        <Mail className="w-4 h-4" />
                        <span dir="ltr">{u.email}</span>
                      </div>
                    </td>
                    {/* Role Column */}
                    <td className="py-4">
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${getRoleColor(u.role)}`}>
                        {isRTL ? u.role_name_ar : u.role_name}
                      </span>
                    </td>
                    {/* Department Column */}
                    <td className={`py-4 text-slate-600 ${isRTL ? 'text-right' : ''}`}>
                      {u.department || '-'}
                    </td>
                    {/* Actions Column */}
                    <td className="py-4">
                      <div className={`flex items-center gap-2 ${isRTL ? 'flex-row-reverse justify-end' : ''}`}>
                        {/* Edit Role - available to all managers */}
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => {
                            setSelectedUser({ ...u, newRole: u.role });
                            setShowEditRoleModal(true);
                          }}
                          className={`gap-1 ${isRTL ? 'flex-row-reverse' : ''}`}
                        >
                          <Shield className="w-4 h-4" />
                          {isRTL ? 'الدور' : 'Role'}
                        </Button>
                        
                        {/* Edit User - System Admin only */}
                        {isSystemAdmin && (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => {
                              setSelectedUser({ ...u, newPassword: '' });
                              setShowEditUserModal(true);
                            }}
                            className={`gap-1 text-blue-600 hover:text-blue-800 ${isRTL ? 'flex-row-reverse' : ''}`}
                          >
                            <Edit className="w-4 h-4" />
                            {isRTL ? 'تعديل' : 'Edit'}
                          </Button>
                        )}
                        
                        {/* Delete User - System Admin only, can't delete yourself */}
                        {isSystemAdmin && u.id !== user?.user_id && (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => {
                              setSelectedUser(u);
                              setShowDeleteConfirm(true);
                            }}
                            className={`gap-1 text-red-600 hover:text-red-800 hover:bg-red-50 ${isRTL ? 'flex-row-reverse' : ''}`}
                          >
                            <Trash2 className="w-4 h-4" />
                            {isRTL ? 'حذف' : 'Delete'}
                          </Button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            
            {filteredUsers.length === 0 && (
              <div className="text-center py-12 text-slate-500">
                <Users className="w-12 h-12 mx-auto mb-3 opacity-50" />
                <p>{isRTL ? 'لا يوجد مستخدمين' : 'No users found'}</p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Create User Modal */}
      <Dialog open={showCreateModal} onOpenChange={setShowCreateModal}>
        <DialogContent className={`max-w-md ${isRTL ? 'rtl' : 'ltr'}`}>
          <DialogHeader>
            <DialogTitle className={`flex items-center gap-2 ${isRTL ? 'flex-row-reverse' : ''}`}>
              <UserPlus className="w-5 h-5" />
              {isRTL ? 'إضافة مستخدم جديد' : 'Add New User'}
            </DialogTitle>
          </DialogHeader>
          
          <div className="space-y-4 py-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label className={isRTL ? 'text-right block' : ''}>{isRTL ? 'الاسم (إنجليزي)' : 'Name (English)'}</Label>
                <Input
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                  placeholder="John Doe"
                />
              </div>
              <div>
                <Label className={isRTL ? 'text-right block' : ''}>{isRTL ? 'الاسم (عربي)' : 'Name (Arabic)'}</Label>
                <Input
                  value={formData.name_ar}
                  onChange={(e) => setFormData({...formData, name_ar: e.target.value})}
                  placeholder="جون دو"
                  className="text-right"
                  dir="rtl"
                />
              </div>
            </div>
            
            <div>
              <Label className={isRTL ? 'text-right block' : ''}>{isRTL ? 'البريد الإلكتروني' : 'Email'}</Label>
              <Input
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({...formData, email: e.target.value})}
                placeholder="user@example.com"
              />
            </div>
            
            <div>
              <Label className={isRTL ? 'text-right block' : ''}>{isRTL ? 'كلمة المرور' : 'Password'}</Label>
              <div className="relative">
                <Input
                  type={showPassword ? 'text' : 'password'}
                  value={formData.password}
                  onChange={(e) => setFormData({...formData, password: e.target.value})}
                  placeholder="••••••••"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className={`absolute top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 ${isRTL ? 'left-3' : 'right-3'}`}
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>
            
            <div>
              <Label className={isRTL ? 'text-right block' : ''}>{isRTL ? 'رقم الهاتف' : 'Phone'}</Label>
              <Input
                value={formData.phone}
                onChange={(e) => setFormData({...formData, phone: e.target.value})}
                placeholder="+966 5xxxxxxxx"
              />
            </div>
            
            <div>
              <Label className={isRTL ? 'text-right block' : ''}>{isRTL ? 'القسم' : 'Department'}</Label>
              <Input
                value={formData.department}
                onChange={(e) => setFormData({...formData, department: e.target.value})}
                placeholder={isRTL ? 'مثال: قسم الجودة' : 'e.g., Quality Department'}
              />
            </div>
            
            <div>
              <Label className={isRTL ? 'text-right block' : ''}>{isRTL ? 'الدور' : 'Role'}</Label>
              <Select 
                value={formData.role} 
                onValueChange={(value) => setFormData({...formData, role: value})}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {roles.map(role => (
                    <SelectItem key={role.id} value={role.id}>
                      <span className={`flex items-center gap-2 ${isRTL ? 'flex-row-reverse' : ''}`}>
                        {isRTL ? role.name_ar : role.name}
                        <span className="text-xs text-slate-400">({role.description?.slice(0, 30)}...)</span>
                      </span>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
          
          <DialogFooter className={isRTL ? 'flex-row-reverse' : ''}>
            <Button variant="outline" onClick={() => setShowCreateModal(false)}>
              {isRTL ? 'إلغاء' : 'Cancel'}
            </Button>
            <Button 
              onClick={handleCreateUser}
              className="bg-[#1e3a5f] hover:bg-[#152a45]"
              disabled={!formData.name || !formData.email || !formData.password}
            >
              {isRTL ? 'إنشاء المستخدم' : 'Create User'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Edit Role Modal */}
      <Dialog open={showEditRoleModal} onOpenChange={setShowEditRoleModal}>
        <DialogContent className={`max-w-md ${isRTL ? 'rtl' : 'ltr'}`}>
          <DialogHeader>
            <DialogTitle className={`flex items-center gap-2 ${isRTL ? 'flex-row-reverse' : ''}`}>
              <Shield className="w-5 h-5" />
              {isRTL ? 'تعديل دور المستخدم' : 'Edit User Role'}
            </DialogTitle>
          </DialogHeader>
          
          {selectedUser && (
            <div className="space-y-4 py-4">
              <div className={`p-4 bg-slate-50 rounded-lg ${isRTL ? 'text-right' : ''}`}>
                <p className="font-medium text-slate-800">
                  {isRTL ? (selectedUser.name_ar || selectedUser.name) : selectedUser.name}
                </p>
                <p className="text-sm text-slate-500">{selectedUser.email}</p>
                <p className="text-sm mt-2">
                  <span className="text-slate-500">{isRTL ? 'الدور الحالي:' : 'Current role:'}</span>{' '}
                  <span className={`px-2 py-0.5 rounded-full text-xs ${getRoleColor(selectedUser.role)}`}>
                    {isRTL ? selectedUser.role_name_ar : selectedUser.role_name}
                  </span>
                </p>
              </div>
              
              <div>
                <Label className={isRTL ? 'text-right block' : ''}>{isRTL ? 'الدور الجديد' : 'New Role'}</Label>
                <Select 
                  value={selectedUser.newRole} 
                  onValueChange={(value) => setSelectedUser({...selectedUser, newRole: value})}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {roles.map(role => (
                      <SelectItem key={role.id} value={role.id}>
                        <span className={isRTL ? 'flex flex-row-reverse items-center gap-2' : ''}>
                          {isRTL ? role.name_ar : role.name}
                        </span>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
          )}
          
          <DialogFooter className={isRTL ? 'flex-row-reverse' : ''}>
            <Button variant="outline" onClick={() => setShowEditRoleModal(false)}>
              {isRTL ? 'إلغاء' : 'Cancel'}
            </Button>
            <Button 
              onClick={handleUpdateRole}
              className="bg-[#1e3a5f] hover:bg-[#152a45]"
              disabled={!selectedUser || selectedUser.role === selectedUser.newRole}
            >
              {isRTL ? 'تحديث الدور' : 'Update Role'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Edit User Modal (System Admin only) */}
      <Dialog open={showEditUserModal} onOpenChange={setShowEditUserModal}>
        <DialogContent className={`max-w-md ${isRTL ? 'rtl' : 'ltr'}`}>
          <DialogHeader>
            <DialogTitle className={`flex items-center gap-2 ${isRTL ? 'flex-row-reverse' : ''}`}>
              <UserCog className="w-5 h-5" />
              {isRTL ? 'تعديل بيانات المستخدم' : 'Edit User Details'}
            </DialogTitle>
          </DialogHeader>
          
          {selectedUser && (
            <div className="space-y-4 py-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label className={isRTL ? 'text-right block' : ''}>{isRTL ? 'الاسم (إنجليزي)' : 'Name (English)'}</Label>
                  <Input
                    value={selectedUser.name || ''}
                    onChange={(e) => setSelectedUser({...selectedUser, name: e.target.value})}
                  />
                </div>
                <div>
                  <Label className={isRTL ? 'text-right block' : ''}>{isRTL ? 'الاسم (عربي)' : 'Name (Arabic)'}</Label>
                  <Input
                    value={selectedUser.name_ar || ''}
                    onChange={(e) => setSelectedUser({...selectedUser, name_ar: e.target.value})}
                    className="text-right"
                    dir="rtl"
                  />
                </div>
              </div>
              
              <div>
                <Label className={isRTL ? 'text-right block' : ''}>{isRTL ? 'البريد الإلكتروني' : 'Email'}</Label>
                <Input
                  type="email"
                  value={selectedUser.email || ''}
                  onChange={(e) => setSelectedUser({...selectedUser, email: e.target.value})}
                />
              </div>
              
              <div>
                <Label className={isRTL ? 'text-right block' : ''}>{isRTL ? 'كلمة المرور الجديدة (اتركها فارغة للإبقاء)' : 'New Password (leave empty to keep)'}</Label>
                <div className="relative">
                  <Input
                    type={showPassword ? 'text' : 'password'}
                    value={selectedUser.newPassword || ''}
                    onChange={(e) => setSelectedUser({...selectedUser, newPassword: e.target.value})}
                    placeholder="••••••••"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className={`absolute top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 ${isRTL ? 'left-3' : 'right-3'}`}
                  >
                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>
              
              <div>
                <Label className={isRTL ? 'text-right block' : ''}>{isRTL ? 'رقم الهاتف' : 'Phone'}</Label>
                <Input
                  value={selectedUser.phone || ''}
                  onChange={(e) => setSelectedUser({...selectedUser, phone: e.target.value})}
                />
              </div>
              
              <div>
                <Label className={isRTL ? 'text-right block' : ''}>{isRTL ? 'القسم' : 'Department'}</Label>
                <Input
                  value={selectedUser.department || ''}
                  onChange={(e) => setSelectedUser({...selectedUser, department: e.target.value})}
                />
              </div>
              
              <div>
                <Label className={isRTL ? 'text-right block' : ''}>{isRTL ? 'الدور' : 'Role'}</Label>
                <Select 
                  value={selectedUser.role} 
                  onValueChange={(value) => setSelectedUser({...selectedUser, role: value})}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {roles.map(role => (
                      <SelectItem key={role.id} value={role.id}>
                        {isRTL ? role.name_ar : role.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
          )}
          
          <DialogFooter className={isRTL ? 'flex-row-reverse' : ''}>
            <Button variant="outline" onClick={() => setShowEditUserModal(false)}>
              {isRTL ? 'إلغاء' : 'Cancel'}
            </Button>
            <Button 
              onClick={handleEditUser}
              className="bg-[#1e3a5f] hover:bg-[#152a45]"
            >
              {isRTL ? 'حفظ التغييرات' : 'Save Changes'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={showDeleteConfirm} onOpenChange={setShowDeleteConfirm}>
        <AlertDialogContent className={isRTL ? 'rtl' : 'ltr'}>
          <AlertDialogHeader>
            <AlertDialogTitle className={`flex items-center gap-2 text-red-600 ${isRTL ? 'flex-row-reverse' : ''}`}>
              <Trash2 className="w-5 h-5" />
              {isRTL ? 'تأكيد حذف المستخدم' : 'Confirm Delete User'}
            </AlertDialogTitle>
            <AlertDialogDescription className={isRTL ? 'text-right' : ''}>
              {isRTL 
                ? `هل أنت متأكد من حذف المستخدم "${selectedUser?.name || selectedUser?.email}"؟ لا يمكن التراجع عن هذا الإجراء.`
                : `Are you sure you want to delete the user "${selectedUser?.name || selectedUser?.email}"? This action cannot be undone.`
              }
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter className={isRTL ? 'flex-row-reverse' : ''}>
            <AlertDialogCancel>
              {isRTL ? 'إلغاء' : 'Cancel'}
            </AlertDialogCancel>
            <AlertDialogAction 
              onClick={handleDeleteUser}
              className="bg-red-600 hover:bg-red-700"
            >
              {isRTL ? 'حذف المستخدم' : 'Delete User'}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
};

export default UserManagementTab;
