/**
 * components/OfficerManagement.jsx - Admin Officer Roster & Personnel Management
 * ===============================================================================
 * Smart ANPR Vehicle Verification System
 * Design: STYLE 4 – PREMIUM ENTERPRISE (WHITE + BLUE + GREY)
 *
 * Implements:
 * - List all registered officers with badge numbers, stations, roles, and status
 * - Register new officer account with role assignment (ADMIN or OFFICER)
 * - Edit officer profile & assigned station
 * - Toggle officer account status (Active / Suspended)
 * - Accessible only to authenticated users with ADMIN role
 */

import React, { useState, useEffect } from 'react';
import {
  Shield,
  UserCheck,
  UserPlus,
  RefreshCw,
  Search,
  CheckCircle2,
  XCircle,
  AlertCircle,
  BadgeCheck,
  Lock,
  Edit2,
  Power,
  X,
  UserCog,
  MapPin,
  Building,
} from 'lucide-react';
import { getOfficers, createOfficer, updateOfficer } from '../services/api';
import Breadcrumbs from './common/Breadcrumbs';
import StatusBadge from './common/StatusBadge';
import EmptyState from './common/EmptyState';

export default function OfficerManagement({ currentUser, showToast }) {
  const [officers, setOfficers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [roleFilter, setRoleFilter] = useState('ALL');
  const [showAddModal, setShowAddModal] = useState(false);
  const [editingOfficer, setEditingOfficer] = useState(null);

  // New Officer Form
  const [newUsername, setNewUsername] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [newFullName, setNewFullName] = useState('');
  const [newBadge, setNewBadge] = useState('');
  const [newRole, setNewRole] = useState('OFFICER');
  const [newStation, setNewStation] = useState('SEC-04-EXPRESSWAY');
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Edit Officer Form
  const [editFullName, setEditFullName] = useState('');
  const [editBadge, setEditBadge] = useState('');
  const [editStation, setEditStation] = useState('');
  const [editRole, setEditRole] = useState('OFFICER');
  const [editActive, setEditActive] = useState(true);
  const [isUpdating, setIsUpdating] = useState(false);

  const fetchOfficersList = async () => {
    setLoading(true);
    try {
      const res = await getOfficers();
      setOfficers(res.officers || []);
    } catch (err) {
      showToast?.({
        type: 'error',
        title: 'Failed to load officers',
        message: err.message,
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOfficersList();
  }, []);

  const handleCreateOfficer = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      const res = await createOfficer({
        username: newUsername,
        password: newPassword,
        full_name: newFullName,
        badge_number: newBadge,
        role: newRole,
        station_id: newStation,
      });

      showToast?.({
        type: 'success',
        title: 'Officer Registered',
        message: res.message || `Officer ${newFullName} registered successfully.`,
      });

      setShowAddModal(false);
      setNewUsername('');
      setNewPassword('');
      setNewFullName('');
      setNewBadge('');
      fetchOfficersList();
    } catch (err) {
      showToast?.({
        type: 'error',
        title: 'Registration Error',
        message: err.message,
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const openEditModal = (officer) => {
    setEditingOfficer(officer);
    setEditFullName(officer.full_name || '');
    setEditBadge(officer.badge_number || '');
    setEditStation(officer.station_id || 'SEC-04-EXPRESSWAY');
    setEditRole(officer.role || 'OFFICER');
    setEditActive(officer.is_active !== 0 && officer.is_active !== false);
  };

  const handleUpdateOfficer = async (e) => {
    e.preventDefault();
    if (!editingOfficer) return;
    setIsUpdating(true);
    try {
      await updateOfficer(editingOfficer.id, {
        full_name: editFullName,
        badge_number: editBadge,
        station_id: editStation,
        role: editRole,
        is_active: editActive ? 1 : 0,
      });

      showToast?.({
        type: 'success',
        title: 'Officer Updated',
        message: `Credentials and station updated for ${editFullName}.`,
      });

      setEditingOfficer(null);
      fetchOfficersList();
    } catch (err) {
      showToast?.({
        type: 'error',
        title: 'Update Failed',
        message: err.message,
      });
    } finally {
      setIsUpdating(false);
    }
  };

  const handleToggleActive = async (officer) => {
    const nextState = officer.is_active === 0 || officer.is_active === false ? 1 : 0;
    try {
      await updateOfficer(officer.id, { is_active: nextState });
      showToast?.({
        type: nextState === 1 ? 'success' : 'warning',
        title: nextState === 1 ? 'Account Activated' : 'Account Suspended',
        message: `${officer.full_name} is now ${nextState === 1 ? 'ACTIVE' : 'SUSPENDED'}.`,
      });
      fetchOfficersList();
    } catch (err) {
      showToast?.({
        type: 'error',
        title: 'Status Update Failed',
        message: err.message,
      });
    }
  };

  const filteredOfficers = officers.filter((o) => {
    const q = searchQuery.toLowerCase();
    const matchQuery =
      !searchQuery ||
      o.username?.toLowerCase().includes(q) ||
      o.full_name?.toLowerCase().includes(q) ||
      o.badge_number?.toLowerCase().includes(q) ||
      o.station_id?.toLowerCase().includes(q);

    const matchRole = roleFilter === 'ALL' || o.role === roleFilter;
    return matchQuery && matchRole;
  });

  const totalActive = officers.filter((o) => o.is_active !== 0 && o.is_active !== false).length;
  const totalAdmins = officers.filter((o) => o.role === 'ADMIN').length;

  return (
    <div className="space-y-6">
      {/* Breadcrumbs */}
      <Breadcrumbs items={[{ label: 'Administration' }, { label: 'Personnel & Officer Roster' }]} />

      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#DCE3EC] pb-4">
        <div>
          <h2 className="text-xl md:text-2xl font-bold text-[#172B4D] flex items-center gap-2.5">
            <UserCheck className="h-6 w-6 text-[#1769D2]" />
            <span>Officer Roster & Role Management</span>
          </h2>
          <p className="text-xs text-[#64748B] mt-1">
            Administration console to oversee enforcement personnel, credential issuance, and checkpoint station assignment
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={fetchOfficersList}
            className="px-3.5 py-2 rounded-xl bg-white hover:bg-[#F5F7FA] text-[#172B4D] text-xs font-semibold border border-[#DCE3EC] shadow-sm flex items-center gap-2 transition-colors"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${loading ? 'animate-spin text-[#1769D2]' : 'text-[#64748B]'}`} />
            <span>Refresh Roster</span>
          </button>

          <button
            onClick={() => setShowAddModal(true)}
            className="px-4 py-2 rounded-xl bg-[#1769D2] hover:bg-[#1258B3] text-white text-xs font-bold transition-all shadow-sm flex items-center gap-2"
          >
            <UserPlus className="h-4 w-4" />
            <span>Add New Officer</span>
          </button>
        </div>
      </div>

      {/* Summary KPI Strip */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="p-4 rounded-2xl bg-white border border-[#DCE3EC] shadow-sm flex items-center gap-3.5">
          <div className="w-10 h-10 rounded-xl bg-[#EFF5FF] text-[#1769D2] flex items-center justify-center font-bold">
            <UserCheck className="h-5 w-5" />
          </div>
          <div>
            <p className="text-[11px] font-bold uppercase tracking-wider text-[#64748B]">Total Registered Personnel</p>
            <p className="text-xl font-extrabold text-[#172B4D] mt-0.5">{officers.length}</p>
          </div>
        </div>

        <div className="p-4 rounded-2xl bg-white border border-[#DCE3EC] shadow-sm flex items-center gap-3.5">
          <div className="w-10 h-10 rounded-xl bg-emerald-50 text-[#16A36A] flex items-center justify-center font-bold">
            <CheckCircle2 className="h-5 w-5" />
          </div>
          <div>
            <p className="text-[11px] font-bold uppercase tracking-wider text-[#64748B]">Active On Duty</p>
            <p className="text-xl font-extrabold text-[#16A36A] mt-0.5">{totalActive}</p>
          </div>
        </div>

        <div className="p-4 rounded-2xl bg-white border border-[#DCE3EC] shadow-sm flex items-center gap-3.5">
          <div className="w-10 h-10 rounded-xl bg-slate-100 text-[#172B4D] flex items-center justify-center font-bold">
            <Shield className="h-5 w-5" />
          </div>
          <div>
            <p className="text-[11px] font-bold uppercase tracking-wider text-[#64748B]">System Administrators</p>
            <p className="text-xl font-extrabold text-[#172B4D] mt-0.5">{totalAdmins}</p>
          </div>
        </div>
      </div>

      {/* Search & Filter Toolbar */}
      <div className="p-4 rounded-2xl border border-[#DCE3EC] bg-white shadow-sm flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-[#64748B]" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search by officer name, badge, username, station..."
            className="w-full pl-10 pr-4 py-2 rounded-xl bg-white border border-[#DCE3EC] text-xs font-medium text-[#172B4D] placeholder-slate-400 focus:outline-none focus:border-[#1769D2] focus:ring-2 focus:ring-[#1769D2]/15 transition-colors"
          />
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs text-[#64748B] font-medium mr-1">Role:</span>
          {['ALL', 'OFFICER', 'ADMIN'].map((r) => (
            <button
              key={r}
              onClick={() => setRoleFilter(r)}
              className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all border ${
                roleFilter === r
                  ? 'bg-[#1769D2] text-white border-[#1769D2]'
                  : 'bg-white text-[#64748B] border-[#DCE3EC] hover:bg-[#F5F7FA]'
              }`}
            >
              {r}
            </button>
          ))}
        </div>
      </div>

      {/* Officers Table */}
      <div className="rounded-2xl border border-[#DCE3EC] bg-white shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#EFF5FF] text-[#172B4D] font-bold uppercase text-[11px] border-b border-[#DCE3EC]">
              <tr>
                <th className="py-3.5 px-4">Officer Particulars</th>
                <th className="py-3.5 px-4">Badge Number</th>
                <th className="py-3.5 px-4">Username</th>
                <th className="py-3.5 px-4">Assigned Station</th>
                <th className="py-3.5 px-4">Role & Privileges</th>
                <th className="py-3.5 px-4">Account Status</th>
                <th className="py-3.5 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#DCE3EC]">
              {loading ? (
                <tr>
                  <td colSpan="7" className="py-12 text-center text-[#64748B]">
                    <RefreshCw className="h-5 w-5 animate-spin mx-auto text-[#1769D2] mb-2" />
                    Loading personnel roster...
                  </td>
                </tr>
              ) : filteredOfficers.length === 0 ? (
                <tr>
                  <td colSpan="7" className="py-12">
                    <EmptyState
                      icon={UserCheck}
                      title="No Officers Found"
                      message="No officer profiles match your search criteria. You can register a new officer above."
                      actionLabel="Clear Search"
                      onAction={() => {
                        setSearchQuery('');
                        setRoleFilter('ALL');
                      }}
                    />
                  </td>
                </tr>
              ) : (
                filteredOfficers.map((o) => {
                  const isAdmin = o.role === 'ADMIN';
                  const isActive = o.is_active !== 0 && o.is_active !== false;

                  return (
                    <tr key={o.id} className="hover:bg-[#F5F7FA] transition-colors">
                      <td className="py-3.5 px-4">
                        <div className="font-bold text-[#172B4D]">{o.full_name}</div>
                        <div className="text-[11px] text-[#64748B]">
                          ID #{o.id} &bull; Created {o.created_at ? new Date(o.created_at).toLocaleDateString() : 'Active'}
                        </div>
                      </td>
                      <td className="py-3.5 px-4 font-mono font-bold text-[#1769D2]">
                        {o.badge_number}
                      </td>
                      <td className="py-3.5 px-4 font-mono text-[#64748B]">
                        {o.username}
                      </td>
                      <td className="py-3.5 px-4 text-[#172B4D] font-medium">
                        <span className="inline-flex items-center gap-1.5">
                          <MapPin className="h-3 w-3 text-[#1769D2]" />
                          {o.station_id || 'UNASSIGNED'}
                        </span>
                      </td>
                      <td className="py-3.5 px-4">
                        <span
                          className={`px-2.5 py-0.5 rounded-full font-bold uppercase text-[10px] border ${
                            isAdmin
                              ? 'bg-purple-50 text-purple-700 border-purple-200'
                              : 'bg-blue-50 text-[#1769D2] border-blue-200'
                          }`}
                        >
                          {o.role}
                        </span>
                      </td>
                      <td className="py-3.5 px-4">
                        <StatusBadge status={isActive ? 'ACTIVE' : 'SUSPENDED'} />
                      </td>
                      <td className="py-3.5 px-4 text-right">
                        <div className="inline-flex items-center gap-1.5">
                          <button
                            onClick={() => openEditModal(o)}
                            title="Edit Officer Profile"
                            className="p-1.5 rounded-lg border border-[#DCE3EC] bg-white text-[#64748B] hover:text-[#1769D2] hover:bg-[#EFF5FF] transition-colors"
                          >
                            <Edit2 className="h-3.5 w-3.5" />
                          </button>
                          <button
                            onClick={() => handleToggleActive(o)}
                            title={isActive ? 'Suspend Officer' : 'Activate Officer'}
                            className={`p-1.5 rounded-lg border transition-colors ${
                              isActive
                                ? 'border-[#DCE3EC] bg-white text-[#64748B] hover:text-[#DC4545] hover:bg-rose-50'
                                : 'border-emerald-200 bg-emerald-50 text-[#16A36A] hover:bg-emerald-100'
                            }`}
                          >
                            <Power className="h-3.5 w-3.5" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Add Officer Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm animate-in fade-in duration-150">
          <div className="w-full max-w-md rounded-2xl border border-[#DCE3EC] bg-white p-6 shadow-2xl space-y-5 text-[#172B4D]">
            <div className="flex items-center justify-between border-b border-[#DCE3EC] pb-3">
              <div className="flex items-center gap-2">
                <UserPlus className="h-5 w-5 text-[#1769D2]" />
                <h3 className="font-bold text-base text-[#172B4D]">Register Enforcement Officer</h3>
              </div>
              <button
                onClick={() => setShowAddModal(false)}
                className="text-[#64748B] hover:text-[#172B4D] p-1 rounded-lg"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            <form onSubmit={handleCreateOfficer} className="space-y-3.5 text-xs">
              <div>
                <label className="block font-bold text-[#172B4D] mb-1">Full Name</label>
                <input
                  type="text"
                  required
                  value={newFullName}
                  onChange={(e) => setNewFullName(e.target.value)}
                  placeholder="e.g. Sub-Insp. Rahul Verma"
                  className="w-full px-3.5 py-2.5 rounded-xl bg-white border border-[#DCE3EC] text-[#172B4D] focus:outline-none focus:border-[#1769D2]"
                />
              </div>

              <div>
                <label className="block font-bold text-[#172B4D] mb-1">Badge / Service Number</label>
                <input
                  type="text"
                  required
                  value={newBadge}
                  onChange={(e) => setNewBadge(e.target.value.toUpperCase())}
                  placeholder="e.g. TP-DEL-9520"
                  className="w-full px-3.5 py-2.5 rounded-xl bg-white border border-[#DCE3EC] font-mono text-[#172B4D] focus:outline-none focus:border-[#1769D2]"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-bold text-[#172B4D] mb-1">Username / ID</label>
                  <input
                    type="text"
                    required
                    value={newUsername}
                    onChange={(e) => setNewUsername(e.target.value.toLowerCase())}
                    placeholder="e.g. rahul_verma"
                    className="w-full px-3.5 py-2.5 rounded-xl bg-white border border-[#DCE3EC] font-mono text-[#172B4D] focus:outline-none focus:border-[#1769D2]"
                  />
                </div>
                <div>
                  <label className="block font-bold text-[#172B4D] mb-1">Password</label>
                  <input
                    type="password"
                    required
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    placeholder="Min 6 characters"
                    className="w-full px-3.5 py-2.5 rounded-xl bg-white border border-[#DCE3EC] text-[#172B4D] focus:outline-none focus:border-[#1769D2]"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-bold text-[#172B4D] mb-1">Role</label>
                  <select
                    value={newRole}
                    onChange={(e) => setNewRole(e.target.value)}
                    className="w-full px-3.5 py-2.5 rounded-xl bg-white border border-[#DCE3EC] text-[#172B4D] focus:outline-none focus:border-[#1769D2]"
                  >
                    <option value="OFFICER">OFFICER (Standard)</option>
                    <option value="ADMIN">ADMIN (Full Access)</option>
                  </select>
                </div>
                <div>
                  <label className="block font-bold text-[#172B4D] mb-1">Station ID</label>
                  <input
                    type="text"
                    required
                    value={newStation}
                    onChange={(e) => setNewStation(e.target.value.toUpperCase())}
                    placeholder="e.g. SEC-04-EXPRESSWAY"
                    className="w-full px-3.5 py-2.5 rounded-xl bg-white border border-[#DCE3EC] font-mono text-[#172B4D] focus:outline-none focus:border-[#1769D2]"
                  />
                </div>
              </div>

              <div className="flex items-center justify-end gap-3 pt-3 border-t border-[#DCE3EC]">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 rounded-xl bg-[#EFF5FF] hover:bg-[#DDEBFF] text-[#1769D2] font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="px-5 py-2 rounded-xl bg-[#1769D2] hover:bg-[#1258B3] text-white font-bold disabled:opacity-50"
                >
                  {isSubmitting ? 'Registering...' : 'Register Officer'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Edit Officer Modal */}
      {editingOfficer && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm animate-in fade-in duration-150">
          <div className="w-full max-w-md rounded-2xl border border-[#DCE3EC] bg-white p-6 shadow-2xl space-y-5 text-[#172B4D]">
            <div className="flex items-center justify-between border-b border-[#DCE3EC] pb-3">
              <div className="flex items-center gap-2">
                <UserCog className="h-5 w-5 text-[#1769D2]" />
                <div>
                  <h3 className="font-bold text-base text-[#172B4D]">Modify Officer Credentials</h3>
                  <p className="text-[11px] text-[#64748B]">Username: {editingOfficer.username}</p>
                </div>
              </div>
              <button
                onClick={() => setEditingOfficer(null)}
                className="text-[#64748B] hover:text-[#172B4D] p-1 rounded-lg"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            <form onSubmit={handleUpdateOfficer} className="space-y-3.5 text-xs">
              <div>
                <label className="block font-bold text-[#172B4D] mb-1">Full Name</label>
                <input
                  type="text"
                  required
                  value={editFullName}
                  onChange={(e) => setEditFullName(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-xl bg-white border border-[#DCE3EC] text-[#172B4D] focus:outline-none focus:border-[#1769D2]"
                />
              </div>

              <div>
                <label className="block font-bold text-[#172B4D] mb-1">Badge / Service Number</label>
                <input
                  type="text"
                  required
                  value={editBadge}
                  onChange={(e) => setEditBadge(e.target.value.toUpperCase())}
                  className="w-full px-3.5 py-2.5 rounded-xl bg-white border border-[#DCE3EC] font-mono text-[#172B4D] focus:outline-none focus:border-[#1769D2]"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-bold text-[#172B4D] mb-1">Role</label>
                  <select
                    value={editRole}
                    onChange={(e) => setEditRole(e.target.value)}
                    className="w-full px-3.5 py-2.5 rounded-xl bg-white border border-[#DCE3EC] text-[#172B4D] focus:outline-none focus:border-[#1769D2]"
                  >
                    <option value="OFFICER">OFFICER (Standard)</option>
                    <option value="ADMIN">ADMIN (Full Access)</option>
                  </select>
                </div>
                <div>
                  <label className="block font-bold text-[#172B4D] mb-1">Assigned Station</label>
                  <input
                    type="text"
                    required
                    value={editStation}
                    onChange={(e) => setEditStation(e.target.value.toUpperCase())}
                    className="w-full px-3.5 py-2.5 rounded-xl bg-white border border-[#DCE3EC] font-mono text-[#172B4D] focus:outline-none focus:border-[#1769D2]"
                  />
                </div>
              </div>

              <div className="pt-2">
                <label className="flex items-center gap-2.5 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={editActive}
                    onChange={(e) => setEditActive(e.target.checked)}
                    className="rounded border-[#DCE3EC] text-[#1769D2] focus:ring-[#1769D2] h-4 w-4"
                  />
                  <span className="font-bold text-xs text-[#172B4D]">
                    Account is Active and authorized for roadside checkpoint duty
                  </span>
                </label>
              </div>

              <div className="flex items-center justify-end gap-3 pt-3 border-t border-[#DCE3EC]">
                <button
                  type="button"
                  onClick={() => setEditingOfficer(null)}
                  className="px-4 py-2 rounded-xl bg-[#EFF5FF] hover:bg-[#DDEBFF] text-[#1769D2] font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isUpdating}
                  className="px-5 py-2 rounded-xl bg-[#1769D2] hover:bg-[#1258B3] text-white font-bold disabled:opacity-50"
                >
                  {isUpdating ? 'Saving Changes...' : 'Save Changes'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
