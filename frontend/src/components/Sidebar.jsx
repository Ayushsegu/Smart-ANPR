/**
 * components/Sidebar.jsx - Enterprise Navigation Sidebar Component
 * ================================================================
 * Smart ANPR Vehicle Verification System
 * Design: STYLE 4 – PREMIUM ENTERPRISE (WHITE + BLUE + GREY)
 * Supports Multi-Language i18n & Dark Mode (#1E293B)
 */

import React from 'react';
import {
  ShieldCheck,
  LayoutDashboard,
  Camera,
  Car,
  FileCheck2,
  Receipt,
  BarChart3,
  Settings as SettingsIcon,
  UserCheck,
  User,
  History,
  Navigation,
  HardHat,
  ChevronRight,
  LogOut,
  DatabaseZap,
} from 'lucide-react';
import { useTranslation } from '../context/I18nContext';

export default function Sidebar({ activeTab, onSelectTab, currentUser, onLogout }) {
  const { t } = useTranslation();
  const isAdmin = currentUser?.role === 'ADMIN';

  const menuItems = [
    {
      id: 'dashboard',
      label: t('nav.dashboard', {}, 'Dashboard'),
      icon: LayoutDashboard,
      description: 'Operations Overview',
    },
    {
      id: 'anpr',
      label: t('nav.anpr_scanner', {}, 'Live ANPR Scanner'),
      icon: Camera,
      description: 'AI License Plate Reader',
      badge: 'YOLOv8',
    },
    {
      id: 'fleet',
      label: t('nav.fleet', {}, 'Demo Fleet (50)'),
      icon: DatabaseZap,
      description: '50 Pre-Registered Vehicles',
      badge: '50 Demo',
    },
    {
      id: 'vehicles',
      label: t('nav.vehicle_verification', {}, 'Vehicle Verification'),
      icon: Car,
      description: 'Compliance & Owner Records',
    },
    {
      id: 'documents',
      label: t('nav.document_verification', {}, 'Document Verification'),
      icon: FileCheck2,
      description: 'RC, PUC, Insurance, Tax',
    },
    {
      id: 'history',
      label: t('nav.detection_history', {}, 'Detection History'),
      icon: History,
      description: 'Inspections & Audits Log',
    },
    {
      id: 'gps',
      label: t('nav.gps_tracking', {}, 'GPS Tracking'),
      icon: Navigation,
      description: 'Corridor & Node Mapping',
      badge: 'Live',
    },
    {
      id: 'helmet',
      label: t('nav.helmet_detection', {}, 'Helmet Detection'),
      icon: HardHat,
      description: 'Rider Safety Compliance',
      badge: 'AI',
    },
    {
      id: 'challans',
      label: t('nav.digital_challans', {}, 'Digital Challans'),
      icon: Receipt,
      description: 'Digital Fines & QR Codes',
    },
    {
      id: 'reports',
      label: t('nav.reports_analytics', {}, 'Analytics & Reports'),
      icon: BarChart3,
      description: 'Traffic Intelligence Data',
    },
    ...(isAdmin
      ? [
          {
            id: 'officers',
            label: t('nav.officer_management', {}, 'Officer Management'),
            icon: UserCheck,
            description: 'Personnel & Roles Roster',
            badge: 'Admin',
          },
        ]
      : []),
    {
      id: 'settings',
      label: t('nav.settings', {}, 'Settings'),
      icon: SettingsIcon,
      description: 'Station & System Config',
    },
  ];

  const displayName = currentUser?.full_name || 'Insp. Vikram Sharma';
  const displayBadge = currentUser?.badge_number || 'TP-DEL-8842';
  const displayRole = currentUser?.role || 'OFFICER';

  return (
    <aside className="w-64 md:w-72 bg-white dark:bg-[#1E293B] border-r border-[#DCE3EC] dark:border-slate-800 flex flex-col justify-between select-none shrink-0 transition-colors duration-200 shadow-[1px_0_4px_rgba(23,43,77,0.02)] z-20">
      <div className="flex-1 overflow-y-auto">
        {/* Brand Header */}
        <div className="p-5 border-b border-[#DCE3EC] dark:border-slate-800 flex items-center gap-3 bg-white dark:bg-[#1E293B]">
          <div className="h-11 w-11 rounded-xl bg-[#1769D2] flex items-center justify-center text-white shadow-md shadow-[#1769D2]/20 shrink-0">
            <ShieldCheck className="h-6 w-6 text-white" />
          </div>
          <div className="min-w-0">
            <h1 className="font-extrabold text-xs tracking-wider text-[#172B4D] dark:text-slate-100 uppercase truncate">
              {t('nav.brand_title', {}, 'Smart ANPR System')}
            </h1>
            <p className="text-xs text-[#1769D2] dark:text-blue-400 font-semibold tracking-wide truncate">
              {t('nav.brand_subtitle', {}, 'Intelligent Vehicle Surveillance')}
            </p>
          </div>
        </div>

        {/* Menu Navigation */}
        <div className="p-3.5 space-y-1">
          <div className="px-3 py-2 text-[10px] font-bold tracking-wider text-[#64748B] dark:text-slate-400 uppercase flex items-center justify-between">
            <span>{t('nav.live_patrol', {}, 'Enforcement Console')}</span>
            <span className="text-[10px] px-2 py-0.5 rounded font-bold bg-[#EFF5FF] dark:bg-blue-950 text-[#1769D2] dark:text-blue-400 border border-[#DCE3EC] dark:border-slate-700">
              {displayRole}
            </span>
          </div>

          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => onSelectTab(item.id)}
                className={`w-full flex items-center justify-between px-3 py-2 rounded-xl text-left transition-all cursor-pointer ${
                  isActive
                    ? 'bg-[#EFF5FF] dark:bg-blue-950/60 text-[#1769D2] dark:text-blue-400 font-bold border-l-4 border-[#1769D2] shadow-sm'
                    : 'text-[#64748B] dark:text-slate-400 hover:text-[#172B4D] dark:hover:text-slate-100 hover:bg-[#F5F7FA] dark:hover:bg-slate-800'
                }`}
              >
                <div className="flex items-center gap-2.5 min-w-0">
                  <div
                    className={`h-7 w-7 rounded-lg flex items-center justify-center transition-colors shrink-0 ${
                      isActive
                        ? 'bg-[#1769D2] text-white'
                        : 'bg-[#EFF5FF] dark:bg-slate-800 text-[#1769D2] dark:text-blue-400'
                    }`}
                  >
                    <Icon className="h-3.5 w-3.5 shrink-0" />
                  </div>
                  <div className="min-w-0">
                    <p className={`text-xs truncate ${isActive ? 'text-[#172B4D] dark:text-slate-100 font-bold' : 'text-[#64748B] dark:text-slate-300 font-semibold'}`}>
                      {item.label}
                    </p>
                  </div>
                </div>

                {item.badge && (
                  <span
                    className={`text-[9px] font-mono px-1.5 py-0.5 rounded font-bold shrink-0 ${
                      item.badge === 'Admin'
                        ? 'bg-rose-50 dark:bg-rose-950/50 text-rose-700 dark:text-rose-400 border border-rose-200 dark:border-rose-900'
                        : item.badge === 'Live'
                        ? 'bg-emerald-50 dark:bg-emerald-950/50 text-emerald-700 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-900'
                        : 'bg-[#EFF5FF] dark:bg-blue-950/50 text-[#1769D2] dark:text-blue-400 border border-[#DCE3EC] dark:border-slate-700'
                    }`}
                  >
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </div>
      </div>

      {/* Duty Officer Profile Footer & Logout */}
      <div className="p-3.5 border-t border-[#DCE3EC] dark:border-slate-800 bg-[#F5F7FA] dark:bg-slate-900/60 space-y-2 shrink-0">
        <div className="flex items-center gap-2.5 p-2.5 rounded-xl bg-white dark:bg-[#1E293B] border border-[#DCE3EC] dark:border-slate-700 shadow-sm">
          <div className="h-9 w-9 rounded-full bg-[#1769D2] flex items-center justify-center text-white font-bold shadow-sm shrink-0">
            <User className="h-4 w-4" />
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-xs font-bold text-[#172B4D] dark:text-slate-100 truncate">{displayName}</p>
            <p className="text-[10px] text-[#64748B] dark:text-slate-400 font-mono truncate">Badge: #{displayBadge}</p>
          </div>
          <span
            className="h-2 w-2 rounded-full bg-[#16A36A] ring-4 ring-[#ECFDF3] dark:ring-emerald-950/40 shrink-0"
            title="Patrol Active & Online"
          ></span>
        </div>

        {onLogout && (
          <button
            onClick={onLogout}
            className="w-full py-2 px-3 rounded-xl bg-white dark:bg-[#1E293B] hover:bg-rose-50 dark:hover:bg-rose-950/30 hover:text-[#DC4545] dark:hover:text-rose-400 text-[#64748B] dark:text-slate-300 text-xs font-semibold border border-[#DCE3EC] dark:border-slate-700 hover:border-rose-200 dark:hover:border-rose-900 flex items-center justify-center gap-2 transition-colors shadow-sm cursor-pointer"
          >
            <LogOut className="h-3.5 w-3.5" />
            <span>{t('nav.logout', {}, 'Sign Out')}</span>
          </button>
        )}
      </div>
    </aside>
  );
}
