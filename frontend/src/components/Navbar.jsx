/**
 * components/Navbar.jsx - Traffic Enforcement Dashboard Header
 * ============================================================
 * Smart ANPR Vehicle Verification System
 * Design: STYLE 4 – PREMIUM ENTERPRISE (WHITE + BLUE + GREY)
 * Supports Multi-Language i18n & Dark Mode (#1E293B)
 * Features quick theme toggle & quick language dropdown in header
 */

import React, { useState, useEffect } from 'react';
import {
  Clock,
  CheckCircle2,
  XCircle,
  RefreshCw,
  MapPin,
  LogOut,
  User,
  Bell,
  Search,
  ShieldCheck,
  AlertTriangle,
  FileCheck2,
  X,
  Sun,
  Moon,
  Laptop,
  Globe2,
  Languages,
} from 'lucide-react';
import { getHealth } from '../services/api';
import { useTheme } from '../context/ThemeContext';
import { useTranslation, SUPPORTED_LANGUAGES } from '../context/I18nContext';

export default function Navbar({ onRefreshAll, currentUser, onLogout, onQuickSearch }) {
  const { theme, resolvedTheme, setTheme } = useTheme();
  const { language, changeLanguage, t } = useTranslation();

  const [health, setHealth] = useState(null);
  const [isChecking, setIsChecking] = useState(false);
  const [currentTime, setCurrentTime] = useState(new Date().toLocaleTimeString());
  const [searchPlate, setSearchPlate] = useState('');
  const [showNotifications, setShowNotifications] = useState(false);
  const [showLangMenu, setShowLangMenu] = useState(false);

  const notifications = [
    {
      id: 1,
      type: 'warning',
      title: 'Expired PUC Detected',
      desc: 'Vehicle DL02CD5678 scanned at CP Outer Circle Node with expired pollution certificate.',
      time: '12m ago',
    },
    {
      id: 2,
      type: 'success',
      title: 'Digital Challan Settled',
      desc: 'Citation #CH-2026-XMG5Y fine payment confirmed via QR gateway.',
      time: '28m ago',
    },
    {
      id: 3,
      type: 'info',
      title: 'YOLOv8 Engine Active',
      desc: 'Neural plate detector running at 98.5% confidence baseline.',
      time: '1h ago',
    },
  ];

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date().toLocaleTimeString());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const checkHealth = async () => {
    setIsChecking(true);
    try {
      const data = await getHealth();
      setHealth({ online: true, ...data });
    } catch (err) {
      setHealth({ online: false, error: err.message });
    } finally {
      setIsChecking(false);
    }
  };

  useEffect(() => {
    checkHealth();
  }, []);

  const handleRefreshClick = () => {
    checkHealth();
    if (onRefreshAll) onRefreshAll();
  };

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    if (searchPlate.trim() && onQuickSearch) {
      onQuickSearch(searchPlate.trim().toUpperCase());
      setSearchPlate('');
    }
  };

  const toggleTheme = () => {
    if (theme === 'light') setTheme('dark');
    else if (theme === 'dark') setTheme('system');
    else setTheme('light');
  };

  const displayName = currentUser?.full_name || 'Insp. Vikram Sharma';
  const displayRole = currentUser?.role || 'OFFICER';
  const displayBadge = currentUser?.badge_number || 'TP-DEL-8842';

  return (
    <header className="h-16 border-b border-[#DCE3EC] dark:border-slate-800 bg-white dark:bg-[#1E293B] px-4 sm:px-6 flex items-center justify-between sticky top-0 z-30 shadow-[0_1px_3px_rgba(23,43,77,0.02)] transition-colors duration-200">
      {/* Left: Station & Surveillance Node */}
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2">
          <span className="h-2 w-2 rounded-full bg-[#16A36A] animate-pulse"></span>
          <span className="text-[11px] font-bold text-[#16A36A] tracking-wider uppercase">
            {t('nav.live_patrol', {}, 'LIVE PATROL')}
          </span>
        </div>
        <span className="text-[#DCE3EC] dark:text-slate-700 hidden sm:inline">|</span>
        <div className="hidden sm:flex items-center gap-1.5 text-xs text-[#64748B] dark:text-slate-400">
          <MapPin className="h-3.5 w-3.5 text-[#1769D2]" />
          <span className="font-medium text-[#172B4D] dark:text-slate-200">
            {t('nav.node_label', {}, 'Node 01 • Sector 04 Expressway Checkpoint')}
          </span>
        </div>
      </div>

      {/* Middle: Quick Search Input */}
      <div className="hidden md:flex flex-1 max-w-md mx-4">
        <form onSubmit={handleSearchSubmit} className="relative w-full">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-[#64748B] dark:text-slate-400" />
          <input
            type="text"
            value={searchPlate}
            onChange={(e) => setSearchPlate(e.target.value)}
            placeholder={t('nav.quick_search_placeholder', {}, 'Quick Plate Search (e.g. DL01DM0001)...')}
            className="w-full pl-9 pr-3 py-1.5 rounded-xl bg-[#F5F7FA] dark:bg-slate-900 border border-[#DCE3EC] dark:border-slate-700 text-[#172B4D] dark:text-slate-100 placeholder-[#64748B] dark:placeholder-slate-500 text-xs focus:outline-none focus:border-[#1769D2] focus:bg-white dark:focus:bg-[#1E293B] font-mono tracking-wider transition-colors"
          />
        </form>
      </div>

      {/* Right Controls: Quick Language, Quick Theme, Notifications, Health, Time */}
      <div className="flex items-center gap-2.5 sm:gap-3">
        {/* Quick Language Selector */}
        <div className="relative">
          <button
            onClick={() => setShowLangMenu(!showLangMenu)}
            className="h-8 px-2.5 rounded-lg border border-[#DCE3EC] dark:border-slate-700 bg-white dark:bg-[#1E293B] hover:bg-[#F5F7FA] dark:hover:bg-slate-800 text-[#172B4D] dark:text-slate-200 text-xs font-bold flex items-center gap-1.5 shadow-sm transition-colors cursor-pointer"
            title="Switch Language (English / हिन्दी / ಕನ್ನಡ)"
          >
            <Globe2 className="h-3.5 w-3.5 text-[#1769D2]" />
            <span className="uppercase text-[11px] font-mono">{language}</span>
          </button>

          {showLangMenu && (
            <div className="absolute right-0 mt-2 w-48 rounded-xl bg-white dark:bg-[#1E293B] border border-[#DCE3EC] dark:border-slate-700 shadow-xl p-1.5 space-y-1 z-50">
              {SUPPORTED_LANGUAGES.map((lang) => (
                <button
                  key={lang.code}
                  onClick={() => {
                    changeLanguage(lang.code);
                    setShowLangMenu(false);
                  }}
                  className={`w-full px-2.5 py-1.5 rounded-lg text-left text-xs font-semibold flex items-center justify-between cursor-pointer ${
                    language === lang.code
                      ? 'bg-[#EFF5FF] dark:bg-blue-950/60 text-[#1769D2] dark:text-blue-400 font-bold'
                      : 'text-[#172B4D] dark:text-slate-200 hover:bg-[#F5F7FA] dark:hover:bg-slate-800'
                  }`}
                >
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] font-mono font-bold px-1 rounded bg-[#F5F7FA] dark:bg-slate-800 border border-[#DCE3EC] dark:border-slate-700">
                      {lang.badge}
                    </span>
                    <span>{lang.nativeName}</span>
                  </div>
                  {language === lang.code && <CheckCircle2 className="h-3 w-3 text-[#1769D2]" />}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Quick Theme Toggle */}
        <button
          onClick={toggleTheme}
          className="h-8 w-8 rounded-lg border border-[#DCE3EC] dark:border-slate-700 bg-white dark:bg-[#1E293B] hover:bg-[#F5F7FA] dark:hover:bg-slate-800 text-[#172B4D] dark:text-slate-200 flex items-center justify-center shadow-sm transition-colors cursor-pointer"
          title={`Appearance: ${theme} (Click to toggle Light / Dark / System)`}
        >
          {theme === 'dark' ? (
            <Moon className="h-3.5 w-3.5 text-blue-400" />
          ) : theme === 'light' ? (
            <Sun className="h-3.5 w-3.5 text-amber-500" />
          ) : (
            <Laptop className="h-3.5 w-3.5 text-emerald-500" />
          )}
        </button>

        {/* Health / AI Model Pulse */}
        <button
          onClick={handleRefreshClick}
          disabled={isChecking}
          className={`h-8 px-2.5 rounded-lg border text-xs font-semibold flex items-center gap-1.5 shadow-sm transition-all cursor-pointer ${
            health?.online
              ? 'border-emerald-200 dark:border-emerald-900 bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-400'
              : 'border-rose-200 dark:border-rose-900 bg-rose-50 dark:bg-rose-950/40 text-rose-700 dark:text-rose-400'
          }`}
          title="Flask REST Service & YOLOv8 Model Status"
        >
          <RefreshCw className={`h-3 w-3 ${isChecking ? 'animate-spin' : ''}`} />
          <span className="hidden sm:inline font-mono text-[11px]">
            {health?.online ? 'YOLOv8 Online' : 'Service Offline'}
          </span>
        </button>

        {/* Time Stamp */}
        <div className="hidden xl:flex items-center gap-1.5 text-xs text-[#64748B] dark:text-slate-400 bg-[#F5F7FA] dark:bg-slate-900 px-2.5 py-1 rounded-lg border border-[#DCE3EC] dark:border-slate-700">
          <Clock className="h-3.5 w-3.5 text-[#1769D2]" />
          <span className="font-mono text-[11px] font-semibold text-[#172B4D] dark:text-slate-200">
            {currentTime}
          </span>
        </div>

        {/* Notifications Dropdown Toggle */}
        <div className="relative">
          <button
            onClick={() => setShowNotifications(!showNotifications)}
            className="h-8 w-8 rounded-lg border border-[#DCE3EC] dark:border-slate-700 bg-white dark:bg-[#1E293B] hover:bg-[#F5F7FA] dark:hover:bg-slate-800 text-[#64748B] dark:text-slate-300 flex items-center justify-center relative shadow-sm cursor-pointer"
            title={t('nav.notifications', {}, 'Notifications')}
          >
            <Bell className="h-3.5 w-3.5 text-[#172B4D] dark:text-slate-200" />
            <span className="absolute top-1 right-1 h-2 w-2 rounded-full bg-[#DC4545] ring-2 ring-white dark:ring-slate-800"></span>
          </button>

          {showNotifications && (
            <div className="absolute right-0 mt-2 w-80 sm:w-96 rounded-2xl bg-white dark:bg-[#1E293B] border border-[#DCE3EC] dark:border-slate-700 shadow-xl p-4 space-y-3 z-50">
              <div className="flex items-center justify-between border-b border-[#DCE3EC] dark:border-slate-800 pb-2">
                <div className="flex items-center gap-2">
                  <Bell className="h-4 w-4 text-[#1769D2]" />
                  <span className="font-bold text-xs text-[#172B4D] dark:text-slate-100">
                    {t('nav.notifications', {}, 'Station Notifications')}
                  </span>
                </div>
                <button
                  onClick={() => setShowNotifications(false)}
                  className="text-[#64748B] dark:text-slate-400 hover:text-[#172B4D] dark:hover:text-white"
                >
                  <X className="h-3.5 w-3.5" />
                </button>
              </div>

              <div className="space-y-2 max-h-72 overflow-y-auto">
                {notifications.map((n) => (
                  <div
                    key={n.id}
                    className="p-2.5 rounded-xl bg-[#F5F7FA] dark:bg-slate-900/60 border border-[#DCE3EC] dark:border-slate-700 text-xs space-y-0.5"
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-[#172B4D] dark:text-slate-200">{n.title}</span>
                      <span className="text-[10px] text-[#64748B] dark:text-slate-400">{n.time}</span>
                    </div>
                    <p className="text-[11px] text-[#64748B] dark:text-slate-400 leading-relaxed">{n.desc}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
