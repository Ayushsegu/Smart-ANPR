/**
 * components/Settings.jsx - Station & System Customization Settings
 * ================================================================
 * Smart ANPR Vehicle Verification System
 * Design: STYLE 4 – PREMIUM ENTERPRISE (WHITE + BLUE + GREY)
 *
 * Implements 8 Structured Sections:
 * 1. Appearance Settings (Light Mode, Dark Mode, System Default) with visual previews
 * 2. Language & Regional Settings (English, हिन्दी, ಕನ್ನಡ) with native scripts
 * 3. General & Station Settings (Node ID, Patrol Corridor, Date & Time format)
 * 4. Officer Profile (Duty officer name, Badge ID, Rank & Role)
 * 5. Camera Hardware (Lens preference, resolution, reticle overlay, feedback)
 * 6. ANPR & AI Models (Plate detector confidence, OCR cutoff, helmet sensitivity)
 * 7. Demo Fine Configuration (Customizable MVA 2019 tariff amounts)
 * 8. System Telemetry & Diagnostics (Flask, SQLite 3, YOLOv8, EasyOCR, ReportLab)
 */

import React, { useState, useEffect } from 'react';
import {
  Settings as SettingsIcon,
  Sun,
  Moon,
  Laptop,
  Globe2,
  Shield,
  Camera,
  Sliders,
  Database,
  Cpu,
  CheckCircle2,
  Save,
  RotateCcw,
  Info,
  Server,
  FileText,
  BadgeAlert,
  MapPin,
  Sparkles,
  User,
  Clock,
  Calendar,
  Bell,
  Eye,
  SlidersHorizontal,
  Layers,
  IndianRupee,
  Check,
  Languages,
} from 'lucide-react';
import Breadcrumbs from './common/Breadcrumbs';
import { useTheme } from '../context/ThemeContext';
import { useTranslation, SUPPORTED_LANGUAGES } from '../context/I18nContext';
import { saveUserPreferences, getUserPreferences } from '../services/api';

export default function Settings({ showToast, currentUser }) {
  const { theme, resolvedTheme, setTheme } = useTheme();
  const { language, changeLanguage, t } = useTranslation();

  const [activeSection, setActiveSection] = useState('appearance');

  // General & Station
  const [stationName, setStationName] = useState('Enforcement Node 01 - Sector 04 Expressway');
  const [patrolZone, setPatrolZone] = useState('NH-48 Delhi-Gurugram Expressway Toll Plaza');
  const [dateFormat, setDateFormat] = useState('DD/MM/YYYY');
  const [timeFormat, setTimeFormat] = useState('12');
  const [notificationChime, setNotificationChime] = useState(true);

  // Officer Profile
  const [officerName, setOfficerName] = useState(currentUser?.full_name || 'Insp. Vikram Sharma');
  const [badgeId, setBadgeId] = useState(currentUser?.badge_number || 'TP-DEL-8842');
  const [officerRole, setOfficerRole] = useState(currentUser?.role || 'OFFICER');

  // Camera Hardware
  const [defaultCamera, setDefaultCamera] = useState('environment');
  const [resolution, setResolution] = useState('1080p');
  const [autoVerifyOnScan, setAutoVerifyOnScan] = useState(true);
  const [shutterFeedback, setShutterFeedback] = useState(true);

  // ANPR & AI Models
  const [plateConfidence, setPlateConfidence] = useState(75);
  const [ocrConfidence, setOcrConfidence] = useState(60);
  const [helmetSensitivity, setHelmetSensitivity] = useState(80);
  const [enableCraftDetector, setEnableCraftDetector] = useState(true);

  // Fine schedule (MVA 2019 tariff)
  const [pucFine, setPucFine] = useState(10000);
  const [insuranceFine, setInsuranceFine] = useState(2000);
  const [rcFine, setRcFine] = useState(5000);
  const [roadTaxFine, setRoadTaxFine] = useState(4000);
  const [missingDocFine, setMissingDocFine] = useState(5000);
  const [helmetFine, setHelmetFine] = useState(1000);

  const [isSaving, setIsSaving] = useState(false);

  // Load backend preferences on mount if available
  useEffect(() => {
    getUserPreferences()
      .then((data) => {
        if (data?.preferences) {
          const p = data.preferences;
          if (p.dateFormat) setDateFormat(p.dateFormat);
          if (p.timeFormat) setTimeFormat(p.timeFormat);
          if (p.notificationChime !== undefined) setNotificationChime(p.notificationChime);
        }
      })
      .catch(() => {});
  }, []);

  const handleSaveSettings = async (e) => {
    if (e) e.preventDefault();
    setIsSaving(true);
    try {
      await saveUserPreferences({
        theme,
        language,
        dateFormat,
        timeFormat,
        notificationChime,
        stationName,
        patrolZone,
        defaultCamera,
        resolution,
        autoVerifyOnScan,
        shutterFeedback,
        plateConfidence,
        ocrConfidence,
        helmetSensitivity,
        fines: {
          pucFine,
          insuranceFine,
          rcFine,
          roadTaxFine,
          missingDocFine,
          helmetFine,
        },
      });

      showToast?.({
        type: 'success',
        title: t('common.success', {}, 'Configuration Saved'),
        message: 'System preferences, appearance theme, and language localization updated in persistent storage.',
      });
    } catch {
      showToast?.({
        type: 'success',
        title: t('common.success', {}, 'Configuration Saved'),
        message: 'Preferences updated locally in active runtime memory.',
      });
    } finally {
      setIsSaving(false);
    }
  };

  const handleResetDefaults = () => {
    setTheme('light');
    changeLanguage('en');
    setDateFormat('DD/MM/YYYY');
    setTimeFormat('12');
    setNotificationChime(true);
    setStationName('Enforcement Node 01 - Sector 04 Expressway');
    setPatrolZone('NH-48 Delhi-Gurugram Expressway Toll Plaza');
    setDefaultCamera('environment');
    setResolution('1080p');
    setAutoVerifyOnScan(true);
    setShutterFeedback(true);
    setPlateConfidence(75);
    setOcrConfidence(60);
    setHelmetSensitivity(80);
    setEnableCraftDetector(true);
    setPucFine(10000);
    setInsuranceFine(2000);
    setRcFine(5000);
    setRoadTaxFine(4000);
    setMissingDocFine(5000);
    setHelmetFine(1000);

    showToast?.({
      type: 'info',
      title: 'Defaults Restored',
      message: 'All station parameters, White & Blue light theme, and English language restored.',
    });
  };

  const sectionsList = [
    { id: 'appearance', label: t('settings.tabs.appearance', {}, 'Appearance & Theme'), icon: Sun },
    { id: 'language', label: t('settings.tabs.language', {}, 'Language & Region'), icon: Globe2 },
    { id: 'general', label: t('settings.tabs.general', {}, 'General & Station'), icon: Shield },
    { id: 'profile', label: t('settings.tabs.profile', {}, 'Officer Profile'), icon: User },
    { id: 'camera', label: t('settings.tabs.camera', {}, 'Camera Hardware'), icon: Camera },
    { id: 'anpr_ai', label: t('settings.tabs.anpr_ai', {}, 'ANPR & AI Models'), icon: Cpu },
    { id: 'fines', label: t('settings.tabs.fines', {}, 'Fine Schedules'), icon: IndianRupee },
    { id: 'system', label: t('settings.tabs.system', {}, 'System Telemetry'), icon: Server },
  ];

  return (
    <div className="space-y-6">
      {/* Breadcrumbs */}
      <Breadcrumbs items={[{ label: 'System' }, { label: t('settings.page_title', {}, 'Station Settings & Hardware Parameters') }]} />

      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#DCE3EC] dark:border-slate-800 pb-4">
        <div>
          <h2 className="text-xl md:text-2xl font-bold text-[#172B4D] dark:text-slate-100 flex items-center gap-2.5">
            <div className="h-9 w-9 rounded-xl bg-[#EFF5FF] dark:bg-blue-950/50 flex items-center justify-center text-[#1769D2] border border-[#DCE3EC] dark:border-slate-700">
              <SettingsIcon className="h-5 w-5" />
            </div>
            <span>{t('settings.page_title', {}, 'Station & System Customization Settings')}</span>
          </h2>
          <p className="text-xs text-[#64748B] dark:text-slate-400 mt-1">
            {t('settings.page_subtitle', {}, 'Configure roadside surveillance parameters, appearance themes, and multi-language localization')}
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={handleResetDefaults}
            className="px-4 py-2 rounded-xl bg-white dark:bg-[#1E293B] hover:bg-[#F5F7FA] dark:hover:bg-slate-800 text-[#64748B] dark:text-slate-300 hover:text-[#172B4D] dark:hover:text-white text-xs font-semibold border border-[#DCE3EC] dark:border-slate-700 shadow-sm flex items-center gap-2 transition-colors cursor-pointer"
          >
            <RotateCcw className="h-3.5 w-3.5" />
            <span>{t('settings.reset_defaults', {}, 'Reset Defaults')}</span>
          </button>
          <button
            type="button"
            onClick={handleSaveSettings}
            disabled={isSaving}
            className="px-5 py-2 rounded-xl bg-[#1769D2] hover:bg-[#1258B3] text-white text-xs font-bold transition-all shadow-sm flex items-center gap-2 cursor-pointer disabled:opacity-50"
          >
            <Save className="h-4 w-4" />
            <span>{isSaving ? t('common.saving', {}, 'Saving...') : t('settings.save_config', {}, 'Save Configuration')}</span>
          </button>
        </div>
      </div>

      {/* Horizontal Section Navigation Tabs */}
      <div className="flex items-center gap-1.5 overflow-x-auto pb-1 border-b border-[#DCE3EC] dark:border-slate-800">
        <button
          onClick={() => setActiveSection('all')}
          className={`px-3.5 py-2 rounded-xl text-xs font-semibold whitespace-nowrap transition-all cursor-pointer flex items-center gap-2 ${
            activeSection === 'all'
              ? 'bg-[#1769D2] text-white shadow-sm'
              : 'text-[#64748B] dark:text-slate-400 hover:bg-[#EFF5FF] dark:hover:bg-slate-800 hover:text-[#1769D2]'
          }`}
        >
          <Layers className="h-3.5 w-3.5" />
          <span>All 8 Sections</span>
        </button>
        {sectionsList.map((sec) => {
          const Icon = sec.icon;
          const isActive = activeSection === sec.id;
          return (
            <button
              key={sec.id}
              onClick={() => setActiveSection(sec.id)}
              className={`px-3.5 py-2 rounded-xl text-xs font-semibold whitespace-nowrap transition-all cursor-pointer flex items-center gap-2 ${
                isActive
                  ? 'bg-[#1769D2] text-white shadow-sm'
                  : 'text-[#64748B] dark:text-slate-400 hover:bg-[#EFF5FF] dark:hover:bg-slate-800 hover:text-[#1769D2]'
              }`}
            >
              <Icon className="h-3.5 w-3.5" />
              <span>{sec.label}</span>
            </button>
          );
        })}
      </div>

      {/* ─────────────────────────────────────────────────────────────────────────────
          SECTION 1: APPEARANCE SETTINGS (Light, Dark, System)
         ───────────────────────────────────────────────────────────────────────────── */}
      {(activeSection === 'all' || activeSection === 'appearance') && (
        <section className="p-6 rounded-2xl border border-[#DCE3EC] dark:border-slate-800 bg-white dark:bg-[#1E293B] shadow-sm space-y-5 transition-colors">
          <div className="flex items-center justify-between border-b border-[#DCE3EC] dark:border-slate-800 pb-3">
            <div className="flex items-center gap-2.5">
              <div className="h-9 w-9 rounded-xl bg-[#EFF5FF] dark:bg-blue-950/60 flex items-center justify-center text-[#1769D2] border border-[#DCE3EC] dark:border-slate-700">
                <Sun className="h-5 w-5 text-amber-500 dark:text-amber-400" />
              </div>
              <div>
                <h3 className="font-bold text-base text-[#172B4D] dark:text-slate-100">
                  {t('settings.appearance.title', {}, 'Appearance & Theme')}
                </h3>
                <p className="text-xs text-[#64748B] dark:text-slate-400">
                  {t('settings.appearance.subtitle', {}, 'Select visual display mode for the enforcement interface')}
                </p>
              </div>
            </div>
            <span className="text-[11px] font-mono px-2.5 py-1 rounded-full bg-[#EFF5FF] dark:bg-blue-950 text-[#1769D2] dark:text-blue-400 font-bold border border-[#DCE3EC] dark:border-slate-700">
              Active: {theme === 'system' ? `System (${resolvedTheme})` : theme.toUpperCase()}
            </span>
          </div>

          {/* 3 Theme Selection Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* 1. Light Mode Card */}
            <div
              onClick={() => setTheme('light')}
              className={`relative rounded-2xl border-2 p-4 cursor-pointer transition-all duration-200 flex flex-col justify-between ${
                theme === 'light'
                  ? 'border-[#1769D2] bg-[#EFF5FF]/40 dark:bg-blue-950/30 shadow-md ring-2 ring-[#1769D2]/20'
                  : 'border-[#DCE3EC] dark:border-slate-700 bg-white dark:bg-slate-900/60 hover:border-slate-300 dark:hover:border-slate-600'
              }`}
            >
              {theme === 'light' && (
                <div className="absolute top-3 right-3 h-5 w-5 rounded-full bg-[#1769D2] text-white flex items-center justify-center shadow-sm">
                  <Check className="h-3 w-3 stroke-[3]" />
                </div>
              )}

              {/* Visual Mini Preview */}
              <div className="rounded-xl border border-[#DCE3EC] bg-[#F5F7FA] p-3 mb-3.5 space-y-2">
                <div className="h-4 rounded-md bg-white border border-[#DCE3EC] flex items-center justify-between px-2">
                  <div className="flex items-center gap-1.5">
                    <span className="h-1.5 w-1.5 rounded-full bg-[#1769D2]" />
                    <span className="h-1 w-8 bg-[#172B4D] rounded" />
                  </div>
                  <span className="h-1 w-4 bg-[#64748B] rounded" />
                </div>
                <div className="rounded-md bg-white border border-[#DCE3EC] p-2 space-y-1.5 shadow-sm">
                  <div className="h-1.5 w-16 bg-[#172B4D] rounded" />
                  <div className="h-1 w-24 bg-[#64748B]/50 rounded" />
                  <div className="h-2.5 w-12 rounded bg-[#1769D2]" />
                </div>
              </div>

              <div>
                <div className="flex items-center gap-2 mb-1">
                  <Sun className="h-4 w-4 text-amber-500" />
                  <h4 className="text-sm font-bold text-[#172B4D] dark:text-slate-100">
                    {t('settings.appearance.light_mode', {}, 'Light Mode')}
                  </h4>
                </div>
                <p className="text-[11px] text-[#64748B] dark:text-slate-400 leading-relaxed">
                  {t('settings.appearance.light_desc', {}, 'Enterprise white background with dark navy headings and crisp blue accents. Optimal for daytime field patrol.')}
                </p>
              </div>

              <div className="mt-3 pt-2.5 border-t border-[#DCE3EC] dark:border-slate-700 flex items-center justify-between text-[11px] font-semibold text-[#172B4D] dark:text-slate-300">
                <span>Enterprise White (#FFFFFF)</span>
                <span className="h-3 w-3 rounded-full bg-white border border-[#DCE3EC]" />
              </div>
            </div>

            {/* 2. Dark Mode Card */}
            <div
              onClick={() => setTheme('dark')}
              className={`relative rounded-2xl border-2 p-4 cursor-pointer transition-all duration-200 flex flex-col justify-between ${
                theme === 'dark'
                  ? 'border-[#1769D2] bg-[#EFF5FF]/40 dark:bg-blue-950/30 shadow-md ring-2 ring-[#1769D2]/20'
                  : 'border-[#DCE3EC] dark:border-slate-700 bg-white dark:bg-slate-900/60 hover:border-slate-300 dark:hover:border-slate-600'
              }`}
            >
              {theme === 'dark' && (
                <div className="absolute top-3 right-3 h-5 w-5 rounded-full bg-[#1769D2] text-white flex items-center justify-center shadow-sm">
                  <Check className="h-3 w-3 stroke-[3]" />
                </div>
              )}

              {/* Visual Mini Preview */}
              <div className="rounded-xl border border-slate-700 bg-[#0F172A] p-3 mb-3.5 space-y-2">
                <div className="h-4 rounded-md bg-[#1E293B] border border-slate-700 flex items-center justify-between px-2">
                  <div className="flex items-center gap-1.5">
                    <span className="h-1.5 w-1.5 rounded-full bg-[#1769D2]" />
                    <span className="h-1 w-8 bg-white rounded" />
                  </div>
                  <span className="h-1 w-4 bg-slate-400 rounded" />
                </div>
                <div className="rounded-md bg-[#1E293B] border border-slate-700 p-2 space-y-1.5 shadow-sm">
                  <div className="h-1.5 w-16 bg-white rounded" />
                  <div className="h-1 w-24 bg-slate-400/50 rounded" />
                  <div className="h-2.5 w-12 rounded bg-[#1769D2]" />
                </div>
              </div>

              <div>
                <div className="flex items-center gap-2 mb-1">
                  <Moon className="h-4 w-4 text-blue-400" />
                  <h4 className="text-sm font-bold text-[#172B4D] dark:text-slate-100">
                    {t('settings.appearance.dark_mode', {}, 'Dark Mode')}
                  </h4>
                </div>
                <p className="text-[11px] text-[#64748B] dark:text-slate-400 leading-relaxed">
                  {t('settings.appearance.dark_desc', {}, 'High-contrast dark navy surfaces (#0F172A) with white typography. Reduces eye strain during nighttime roadside patrol.')}
                </p>
              </div>

              <div className="mt-3 pt-2.5 border-t border-[#DCE3EC] dark:border-slate-700 flex items-center justify-between text-[11px] font-semibold text-[#172B4D] dark:text-slate-300">
                <span>Dark Navy (#0F172A)</span>
                <span className="h-3 w-3 rounded-full bg-[#0F172A] border border-slate-600" />
              </div>
            </div>

            {/* 3. System Default Card */}
            <div
              onClick={() => setTheme('system')}
              className={`relative rounded-2xl border-2 p-4 cursor-pointer transition-all duration-200 flex flex-col justify-between ${
                theme === 'system'
                  ? 'border-[#1769D2] bg-[#EFF5FF]/40 dark:bg-blue-950/30 shadow-md ring-2 ring-[#1769D2]/20'
                  : 'border-[#DCE3EC] dark:border-slate-700 bg-white dark:bg-slate-900/60 hover:border-slate-300 dark:hover:border-slate-600'
              }`}
            >
              {theme === 'system' && (
                <div className="absolute top-3 right-3 h-5 w-5 rounded-full bg-[#1769D2] text-white flex items-center justify-center shadow-sm">
                  <Check className="h-3 w-3 stroke-[3]" />
                </div>
              )}

              {/* Visual Mini Preview (Split Half Light, Half Dark) */}
              <div className="rounded-xl border border-[#DCE3EC] dark:border-slate-700 overflow-hidden mb-3.5 flex h-[78px]">
                {/* Left: Light Half */}
                <div className="flex-1 bg-[#F5F7FA] p-2.5 space-y-1.5 border-r border-[#DCE3EC]">
                  <div className="h-3 rounded bg-white border border-[#DCE3EC] px-1 flex items-center">
                    <span className="h-1 w-6 bg-[#172B4D] rounded" />
                  </div>
                  <div className="h-7 rounded bg-white border border-[#DCE3EC] p-1 space-y-1">
                    <div className="h-1 w-8 bg-[#1769D2] rounded" />
                    <div className="h-1 w-10 bg-[#64748B] rounded" />
                  </div>
                </div>
                {/* Right: Dark Half */}
                <div className="flex-1 bg-[#0F172A] p-2.5 space-y-1.5">
                  <div className="h-3 rounded bg-[#1E293B] border border-slate-700 px-1 flex items-center">
                    <span className="h-1 w-6 bg-white rounded" />
                  </div>
                  <div className="h-7 rounded bg-[#1E293B] border border-slate-700 p-1 space-y-1">
                    <div className="h-1 w-8 bg-[#1769D2] rounded" />
                    <div className="h-1 w-10 bg-slate-400 rounded" />
                  </div>
                </div>
              </div>

              <div>
                <div className="flex items-center gap-2 mb-1">
                  <Laptop className="h-4 w-4 text-emerald-500" />
                  <h4 className="text-sm font-bold text-[#172B4D] dark:text-slate-100">
                    {t('settings.appearance.system_mode', {}, 'System Default')}
                  </h4>
                </div>
                <p className="text-[11px] text-[#64748B] dark:text-slate-400 leading-relaxed">
                  {t('settings.appearance.system_desc', {}, 'Automatically synchronizes with your device operating system theme preference.')}
                </p>
              </div>

              <div className="mt-3 pt-2.5 border-t border-[#DCE3EC] dark:border-slate-700 flex items-center justify-between text-[11px] font-semibold text-[#172B4D] dark:text-slate-300">
                <span>Auto OS Sync (matchMedia)</span>
                <Sparkles className="h-3.5 w-3.5 text-[#1769D2]" />
              </div>
            </div>
          </div>
        </section>
      )}

      {/* ─────────────────────────────────────────────────────────────────────────────
          SECTION 2: LANGUAGE & REGIONAL SETTINGS (English, हिन्दी, ಕನ್ನಡ)
         ───────────────────────────────────────────────────────────────────────────── */}
      {(activeSection === 'all' || activeSection === 'language') && (
        <section className="p-6 rounded-2xl border border-[#DCE3EC] dark:border-slate-800 bg-white dark:bg-[#1E293B] shadow-sm space-y-5 transition-colors">
          <div className="flex items-center justify-between border-b border-[#DCE3EC] dark:border-slate-800 pb-3">
            <div className="flex items-center gap-2.5">
              <div className="h-9 w-9 rounded-xl bg-[#EFF5FF] dark:bg-blue-950/60 flex items-center justify-center text-[#1769D2] border border-[#DCE3EC] dark:border-slate-700">
                <Languages className="h-5 w-5" />
              </div>
              <div>
                <h3 className="font-bold text-base text-[#172B4D] dark:text-slate-100">
                  {t('settings.language.title', {}, 'Language & Regional Localization')}
                </h3>
                <p className="text-xs text-[#64748B] dark:text-slate-400">
                  {t('settings.language.subtitle', {}, 'Choose interface language across all modules, navigation bars, forms, and dialogs')}
                </p>
              </div>
            </div>
            <span className="text-[11px] font-mono px-2.5 py-1 rounded-full bg-[#EFF5FF] dark:bg-blue-950 text-[#1769D2] dark:text-blue-400 font-bold border border-[#DCE3EC] dark:border-slate-700">
              Current: {language.toUpperCase()}
            </span>
          </div>

          {/* 3 Language Selection Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {SUPPORTED_LANGUAGES.map((lang) => {
              const isSelected = language === lang.code;
              return (
                <div
                  key={lang.code}
                  onClick={() => changeLanguage(lang.code)}
                  className={`relative rounded-2xl border-2 p-4 cursor-pointer transition-all duration-200 flex flex-col justify-between ${
                    isSelected
                      ? 'border-[#1769D2] bg-[#EFF5FF]/40 dark:bg-blue-950/30 shadow-md ring-2 ring-[#1769D2]/20'
                      : 'border-[#DCE3EC] dark:border-slate-700 bg-white dark:bg-slate-900/60 hover:border-slate-300 dark:hover:border-slate-600'
                  }`}
                >
                  {isSelected && (
                    <div className="absolute top-3 right-3 h-5 w-5 rounded-full bg-[#1769D2] text-white flex items-center justify-center shadow-sm">
                      <Check className="h-3 w-3 stroke-[3]" />
                    </div>
                  )}

                  <div>
                    <div className="flex items-center gap-2 mb-2">
                      <span className="h-7 w-7 rounded-lg bg-[#EFF5FF] dark:bg-blue-950/80 text-[#1769D2] dark:text-blue-400 font-bold text-xs flex items-center justify-center border border-[#DCE3EC] dark:border-slate-700">
                        {lang.badge}
                      </span>
                      <div>
                        <h4 className="text-sm font-bold text-[#172B4D] dark:text-slate-100 flex items-center gap-1.5">
                          <span>{lang.nativeName}</span>
                          {lang.code !== 'en' && (
                            <span className="text-xs text-[#64748B] dark:text-slate-400 font-normal">
                              ({lang.label})
                            </span>
                          )}
                        </h4>
                      </div>
                    </div>

                    <p className="text-[11px] text-[#64748B] dark:text-slate-400 leading-relaxed mt-1">
                      {lang.subtitle}
                    </p>
                  </div>

                  <div className="mt-4 pt-2.5 border-t border-[#DCE3EC] dark:border-slate-700 flex items-center justify-between text-[11px]">
                    <span className="font-semibold text-[#172B4D] dark:text-slate-300">
                      {lang.code === 'en' ? 'Default Standard' : lang.code === 'hi' ? 'राजभाषा हिन्दी' : 'ಕನ್ನಡ ಆವೃತ್ತಿ'}
                    </span>
                    <span className="text-[#1769D2] dark:text-blue-400 font-mono font-bold text-[10px]">
                      UTF-8 Unicode
                    </span>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Regional Formats & Notification Toggles */}
          <div className="p-4 rounded-xl bg-[#F5F7FA] dark:bg-slate-900/50 border border-[#DCE3EC] dark:border-slate-700 space-y-4">
            <h4 className="text-xs font-bold text-[#172B4D] dark:text-slate-200 flex items-center gap-2">
              <Clock className="h-4 w-4 text-[#1769D2]" />
              <span>{t('settings.preferences.title', {}, 'Regional Date & Time Preferences')}</span>
            </h4>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
              <div>
                <label className="block text-xs font-bold text-[#172B4D] dark:text-slate-300 mb-1">
                  {t('settings.preferences.date_format', {}, 'Date Display Format')}
                </label>
                <select
                  value={dateFormat}
                  onChange={(e) => setDateFormat(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-white dark:bg-[#1E293B] border border-[#DCE3EC] dark:border-slate-700 text-[#172B4D] dark:text-slate-200 focus:outline-none focus:border-[#1769D2] font-mono text-xs"
                >
                  <option value="DD/MM/YYYY">DD/MM/YYYY (Indian Standard - e.g. 08/11/2026)</option>
                  <option value="YYYY-MM-DD">YYYY-MM-DD (ISO 8601 - e.g. 2026-11-08)</option>
                  <option value="MM/DD/YYYY">MM/DD/YYYY (US Format - e.g. 11/08/2026)</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-bold text-[#172B4D] dark:text-slate-300 mb-1">
                  {t('settings.preferences.time_format', {}, 'Time Display Format')}
                </label>
                <select
                  value={timeFormat}
                  onChange={(e) => setTimeFormat(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-white dark:bg-[#1E293B] border border-[#DCE3EC] dark:border-slate-700 text-[#172B4D] dark:text-slate-200 focus:outline-none focus:border-[#1769D2] font-mono text-xs"
                >
                  <option value="12">{t('settings.preferences.time_12', {}, '12-Hour (e.g. 09:30 PM)')}</option>
                  <option value="24">{t('settings.preferences.time_24', {}, '24-Hour (e.g. 21:30)')}</option>
                </select>
              </div>
            </div>

            <div className="pt-1">
              <label className="flex items-center gap-2.5 cursor-pointer text-[#172B4D] dark:text-slate-300">
                <input
                  type="checkbox"
                  checked={notificationChime}
                  onChange={(e) => setNotificationChime(e.target.checked)}
                  className="rounded border-[#DCE3EC] dark:border-slate-700 text-[#1769D2] focus:ring-[#1769D2] h-4 w-4"
                />
                <span className="font-semibold text-xs">
                  {t('settings.preferences.notifications', {}, 'Enable audio chime and high-priority banners for expired document scans')}
                </span>
              </label>
            </div>
          </div>

          {/* Technical Identifiers Notice */}
          <div className="p-3.5 rounded-xl bg-[#EFF5FF] dark:bg-blue-950/40 border border-[#DCE3EC] dark:border-slate-700 text-xs text-[#1769D2] dark:text-blue-300 flex items-start gap-2.5">
            <Info className="h-4 w-4 shrink-0 mt-0.5" />
            <p className="leading-relaxed">
              {t('settings.language.fallback_notice', {}, 'Technical identifiers such as vehicle registration numbers (DL01DM0001), Officer IDs, and Challan codes remain preserved.')}
            </p>
          </div>
        </section>
      )}

      {/* ─────────────────────────────────────────────────────────────────────────────
          SECTION 3: GENERAL & ENFORCEMENT STATION PARTICULARS
         ───────────────────────────────────────────────────────────────────────────── */}
      {(activeSection === 'all' || activeSection === 'general') && (
        <section className="p-6 rounded-2xl border border-[#DCE3EC] dark:border-slate-800 bg-white dark:bg-[#1E293B] shadow-sm space-y-4 transition-colors">
          <div className="flex items-center gap-2.5 border-b border-[#DCE3EC] dark:border-slate-800 pb-3">
            <div className="h-9 w-9 rounded-xl bg-[#EFF5FF] dark:bg-blue-950/60 flex items-center justify-center text-[#1769D2] border border-[#DCE3EC] dark:border-slate-700">
              <Shield className="h-5 w-5" />
            </div>
            <div>
              <h3 className="font-bold text-base text-[#172B4D] dark:text-slate-100">
                Enforcement Station Particulars
              </h3>
              <p className="text-xs text-[#64748B] dark:text-slate-400">
                Operational node identifier & patrol zone mapping for citation headers
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
            <div>
              <label className="block text-xs font-bold text-[#172B4D] dark:text-slate-300 mb-1">
                Surveillance Node Identifier
              </label>
              <input
                type="text"
                value={stationName}
                onChange={(e) => setStationName(e.target.value)}
                className="w-full px-3.5 py-2.5 rounded-xl bg-white dark:bg-[#0F172A] border border-[#DCE3EC] dark:border-slate-700 text-[#172B4D] dark:text-slate-200 focus:outline-none focus:border-[#1769D2] text-xs font-medium"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-[#172B4D] dark:text-slate-300 mb-1">
                Checkpost Patrol Zone / Highway Corridor
              </label>
              <input
                type="text"
                value={patrolZone}
                onChange={(e) => setPatrolZone(e.target.value)}
                className="w-full px-3.5 py-2.5 rounded-xl bg-white dark:bg-[#0F172A] border border-[#DCE3EC] dark:border-slate-700 text-[#172B4D] dark:text-slate-200 focus:outline-none focus:border-[#1769D2] text-xs font-medium"
              />
            </div>
          </div>
        </section>
      )}

      {/* ─────────────────────────────────────────────────────────────────────────────
          SECTION 4: OFFICER PROFILE
         ───────────────────────────────────────────────────────────────────────────── */}
      {(activeSection === 'all' || activeSection === 'profile') && (
        <section className="p-6 rounded-2xl border border-[#DCE3EC] dark:border-slate-800 bg-white dark:bg-[#1E293B] shadow-sm space-y-4 transition-colors">
          <div className="flex items-center gap-2.5 border-b border-[#DCE3EC] dark:border-slate-800 pb-3">
            <div className="h-9 w-9 rounded-xl bg-[#EFF5FF] dark:bg-blue-950/60 flex items-center justify-center text-[#1769D2] border border-[#DCE3EC] dark:border-slate-700">
              <User className="h-5 w-5" />
            </div>
            <div>
              <h3 className="font-bold text-base text-[#172B4D] dark:text-slate-100">
                Duty Officer Profile & Credentials
              </h3>
              <p className="text-xs text-[#64748B] dark:text-slate-400">
                Active enforcement personnel metadata attached to generated digital citations
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
            <div>
              <label className="block text-xs font-bold text-[#172B4D] dark:text-slate-300 mb-1">
                Duty Officer Full Name
              </label>
              <input
                type="text"
                value={officerName}
                onChange={(e) => setOfficerName(e.target.value)}
                className="w-full px-3.5 py-2.5 rounded-xl bg-white dark:bg-[#0F172A] border border-[#DCE3EC] dark:border-slate-700 text-[#172B4D] dark:text-slate-200 focus:outline-none focus:border-[#1769D2] text-xs font-medium"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-[#172B4D] dark:text-slate-300 mb-1">
                Badge / Service ID
              </label>
              <input
                type="text"
                value={badgeId}
                onChange={(e) => setBadgeId(e.target.value)}
                className="w-full px-3.5 py-2.5 rounded-xl bg-white dark:bg-[#0F172A] border border-[#DCE3EC] dark:border-slate-700 text-[#1769D2] dark:text-blue-400 font-mono font-bold text-xs focus:outline-none focus:border-[#1769D2]"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-[#172B4D] dark:text-slate-300 mb-1">
                Assigned Role / Authorization
              </label>
              <input
                type="text"
                value={officerRole}
                disabled
                className="w-full px-3.5 py-2.5 rounded-xl bg-[#F5F7FA] dark:bg-slate-900 border border-[#DCE3EC] dark:border-slate-700 text-[#64748B] dark:text-slate-400 font-mono text-xs font-bold cursor-not-allowed"
              />
            </div>
          </div>
        </section>
      )}

      {/* ─────────────────────────────────────────────────────────────────────────────
          SECTION 5: CAMERA HARDWARE
         ───────────────────────────────────────────────────────────────────────────── */}
      {(activeSection === 'all' || activeSection === 'camera') && (
        <section className="p-6 rounded-2xl border border-[#DCE3EC] dark:border-slate-800 bg-white dark:bg-[#1E293B] shadow-sm space-y-4 transition-colors">
          <div className="flex items-center gap-2.5 border-b border-[#DCE3EC] dark:border-slate-800 pb-3">
            <div className="h-9 w-9 rounded-xl bg-[#EFF5FF] dark:bg-blue-950/60 flex items-center justify-center text-[#1769D2] border border-[#DCE3EC] dark:border-slate-700">
              <Camera className="h-5 w-5" />
            </div>
            <div>
              <h3 className="font-bold text-base text-[#172B4D] dark:text-slate-100">
                Live Camera Hardware Preferences
              </h3>
              <p className="text-xs text-[#64748B] dark:text-slate-400">
                Optical resolution, lens selection & roadside trigger
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
            <div>
              <label className="block text-xs font-bold text-[#172B4D] dark:text-slate-300 mb-1">
                Default Lens Selection for Roadside Patrol
              </label>
              <select
                value={defaultCamera}
                onChange={(e) => setDefaultCamera(e.target.value)}
                className="w-full px-3.5 py-2.5 rounded-xl bg-white dark:bg-[#0F172A] border border-[#DCE3EC] dark:border-slate-700 text-[#172B4D] dark:text-slate-200 focus:outline-none focus:border-[#1769D2] text-xs font-medium"
              >
                <option value="environment">Rear Camera (facingMode: environment - Recommended for roadside)</option>
                <option value="user">Front Camera (facingMode: user - Desktop webcam)</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-bold text-[#172B4D] dark:text-slate-300 mb-1">
                Capture Target Resolution
              </label>
              <select
                value={resolution}
                onChange={(e) => setResolution(e.target.value)}
                className="w-full px-3.5 py-2.5 rounded-xl bg-white dark:bg-[#0F172A] border border-[#DCE3EC] dark:border-slate-700 text-[#172B4D] dark:text-slate-200 focus:outline-none focus:border-[#1769D2] text-xs font-medium"
              >
                <option value="1080p">1080p Full HD (1920 x 1080) - Optimal OCR accuracy</option>
                <option value="720p">720p HD (1280 x 720) - Fast mobile bandwidth</option>
                <option value="4k">4K Ultra HD (3840 x 2160) - High fidelity</option>
              </select>
            </div>
          </div>

          <div className="space-y-2.5 pt-1">
            <label className="flex items-center gap-2.5 cursor-pointer text-[#172B4D] dark:text-slate-300">
              <input
                type="checkbox"
                checked={autoVerifyOnScan}
                onChange={(e) => setAutoVerifyOnScan(e.target.checked)}
                className="rounded border-[#DCE3EC] dark:border-slate-700 text-[#1769D2] focus:ring-[#1769D2] h-4 w-4"
              />
              <span className="font-semibold text-xs">
                Automatically verify vehicle registry upon successful plate extraction
              </span>
            </label>

            <label className="flex items-center gap-2.5 cursor-pointer text-[#172B4D] dark:text-slate-300">
              <input
                type="checkbox"
                checked={shutterFeedback}
                onChange={(e) => setShutterFeedback(e.target.checked)}
                className="rounded border-[#DCE3EC] dark:border-slate-700 text-[#1769D2] focus:ring-[#1769D2] h-4 w-4"
              />
              <span className="font-semibold text-xs">
                Show targeting reticle alignment guides over camera viewport
              </span>
            </label>
          </div>
        </section>
      )}

      {/* ─────────────────────────────────────────────────────────────────────────────
          SECTION 6: ANPR & AI MODELS
         ───────────────────────────────────────────────────────────────────────────── */}
      {(activeSection === 'all' || activeSection === 'anpr_ai') && (
        <section className="p-6 rounded-2xl border border-[#DCE3EC] dark:border-slate-800 bg-white dark:bg-[#1E293B] shadow-sm space-y-4 transition-colors">
          <div className="flex items-center gap-2.5 border-b border-[#DCE3EC] dark:border-slate-800 pb-3">
            <div className="h-9 w-9 rounded-xl bg-[#EFF5FF] dark:bg-blue-950/60 flex items-center justify-center text-[#1769D2] border border-[#DCE3EC] dark:border-slate-700">
              <SlidersHorizontal className="h-5 w-5" />
            </div>
            <div>
              <h3 className="font-bold text-base text-[#172B4D] dark:text-slate-100">
                ANPR & AI Neural Inference Thresholds
              </h3>
              <p className="text-xs text-[#64748B] dark:text-slate-400">
                Confidence cutoffs for YOLOv8 number plate detector & EasyOCR character recognizer
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-5 text-xs">
            <div className="p-4 rounded-xl bg-[#F5F7FA] dark:bg-slate-900/60 border border-[#DCE3EC] dark:border-slate-700 space-y-2">
              <div className="flex items-center justify-between font-bold text-[#172B4D] dark:text-slate-200">
                <span>Plate Detection Bounding-Box</span>
                <span className="font-mono text-[#1769D2] dark:text-blue-400">{plateConfidence}%</span>
              </div>
              <input
                type="range"
                min="40"
                max="95"
                value={plateConfidence}
                onChange={(e) => setPlateConfidence(Number(e.target.value))}
                className="w-full accent-[#1769D2]"
              />
              <p className="text-[10px] text-[#64748B] dark:text-slate-400">
                YOLOv8 confidence threshold for High Security Registration Plates
              </p>
            </div>

            <div className="p-4 rounded-xl bg-[#F5F7FA] dark:bg-slate-900/60 border border-[#DCE3EC] dark:border-slate-700 space-y-2">
              <div className="flex items-center justify-between font-bold text-[#172B4D] dark:text-slate-200">
                <span>EasyOCR Character Recognition</span>
                <span className="font-mono text-[#1769D2] dark:text-blue-400">{ocrConfidence}%</span>
              </div>
              <input
                type="range"
                min="30"
                max="90"
                value={ocrConfidence}
                onChange={(e) => setOcrConfidence(Number(e.target.value))}
                className="w-full accent-[#1769D2]"
              />
              <p className="text-[10px] text-[#64748B] dark:text-slate-400">
                Minimum character confidence cutoff for automatic verification
              </p>
            </div>

            <div className="p-4 rounded-xl bg-[#F5F7FA] dark:bg-slate-900/60 border border-[#DCE3EC] dark:border-slate-700 space-y-2">
              <div className="flex items-center justify-between font-bold text-[#172B4D] dark:text-slate-200">
                <span>Helmet Safety AI Sensitivity</span>
                <span className="font-mono text-[#1769D2] dark:text-blue-400">{helmetSensitivity}%</span>
              </div>
              <input
                type="range"
                min="50"
                max="95"
                value={helmetSensitivity}
                onChange={(e) => setHelmetSensitivity(Number(e.target.value))}
                className="w-full accent-[#1769D2]"
              />
              <p className="text-[10px] text-[#64748B] dark:text-slate-400">
                Head curvature contour and rider bounding box sensitivity
              </p>
            </div>
          </div>
        </section>
      )}

      {/* ─────────────────────────────────────────────────────────────────────────────
          SECTION 7: DEMO FINE SCHEDULE CONFIGURATION (MVA 2019)
         ───────────────────────────────────────────────────────────────────────────── */}
      {(activeSection === 'all' || activeSection === 'fines') && (
        <section className="p-6 rounded-2xl border border-[#DCE3EC] dark:border-slate-800 bg-white dark:bg-[#1E293B] shadow-sm space-y-4 transition-colors">
          <div className="flex items-center justify-between border-b border-[#DCE3EC] dark:border-slate-800 pb-3">
            <div className="flex items-center gap-2.5">
              <div className="h-9 w-9 rounded-xl bg-[#EFF5FF] dark:bg-blue-950/60 flex items-center justify-center text-[#1769D2] border border-[#DCE3EC] dark:border-slate-700">
                <Sliders className="h-5 w-5" />
              </div>
              <div>
                <h3 className="font-bold text-base text-[#172B4D] dark:text-slate-100">
                  Demo Fine Schedule Rates (INR)
                </h3>
                <p className="text-xs text-[#64748B] dark:text-slate-400">
                  Customizable statutory violation tariff benchmarks for demo testing
                </p>
              </div>
            </div>
            <span className="text-[10px] px-2.5 py-1 rounded-full bg-[#EFF5FF] dark:bg-blue-950 text-[#1769D2] dark:text-blue-400 font-bold border border-[#DCE3EC] dark:border-slate-700">
              MVA 2019 Tariff
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
            <div className="flex items-center justify-between p-3 rounded-xl bg-[#F5F7FA] dark:bg-slate-900/60 border border-[#DCE3EC] dark:border-slate-700">
              <div>
                <p className="font-bold text-[#172B4D] dark:text-slate-200">Pollution Under Control (PUC) Expired</p>
                <p className="text-[11px] text-[#64748B] dark:text-slate-400">Section 190(2) Mandatory emission lapse</p>
              </div>
              <div className="flex items-center gap-1 font-mono font-bold text-[#172B4D] dark:text-slate-200">
                <span>₹</span>
                <input
                  type="number"
                  value={pucFine}
                  onChange={(e) => setPucFine(Number(e.target.value))}
                  className="w-24 px-2 py-1 rounded-lg bg-white dark:bg-[#0F172A] border border-[#DCE3EC] dark:border-slate-700 text-right font-mono text-xs font-bold text-[#172B4D] dark:text-slate-200 focus:outline-none focus:border-[#1769D2]"
                />
              </div>
            </div>

            <div className="flex items-center justify-between p-3 rounded-xl bg-[#F5F7FA] dark:bg-slate-900/60 border border-[#DCE3EC] dark:border-slate-700">
              <div>
                <p className="font-bold text-[#172B4D] dark:text-slate-200">Motor Insurance Expired</p>
                <p className="text-[11px] text-[#64748B] dark:text-slate-400">Section 196 Third-party policy lapse</p>
              </div>
              <div className="flex items-center gap-1 font-mono font-bold text-[#172B4D] dark:text-slate-200">
                <span>₹</span>
                <input
                  type="number"
                  value={insuranceFine}
                  onChange={(e) => setInsuranceFine(Number(e.target.value))}
                  className="w-24 px-2 py-1 rounded-lg bg-white dark:bg-[#0F172A] border border-[#DCE3EC] dark:border-slate-700 text-right font-mono text-xs font-bold text-[#172B4D] dark:text-slate-200 focus:outline-none focus:border-[#1769D2]"
                />
              </div>
            </div>

            <div className="flex items-center justify-between p-3 rounded-xl bg-[#F5F7FA] dark:bg-slate-900/60 border border-[#DCE3EC] dark:border-slate-700">
              <div>
                <p className="font-bold text-[#172B4D] dark:text-slate-200">Registration Certificate (RC) Expired</p>
                <p className="text-[11px] text-[#64748B] dark:text-slate-400">Section 192 Vehicle fitness expiry</p>
              </div>
              <div className="flex items-center gap-1 font-mono font-bold text-[#172B4D] dark:text-slate-200">
                <span>₹</span>
                <input
                  type="number"
                  value={rcFine}
                  onChange={(e) => setRcFine(Number(e.target.value))}
                  className="w-24 px-2 py-1 rounded-lg bg-white dark:bg-[#0F172A] border border-[#DCE3EC] dark:border-slate-700 text-right font-mono text-xs font-bold text-[#172B4D] dark:text-slate-200 focus:outline-none focus:border-[#1769D2]"
                />
              </div>
            </div>

            <div className="flex items-center justify-between p-3 rounded-xl bg-[#F5F7FA] dark:bg-slate-900/60 border border-[#DCE3EC] dark:border-slate-700">
              <div>
                <p className="font-bold text-[#172B4D] dark:text-slate-200">Commercial Road Tax Expired</p>
                <p className="text-[11px] text-[#64748B] dark:text-slate-400">State motor vehicle tax delinquency</p>
              </div>
              <div className="flex items-center gap-1 font-mono font-bold text-[#172B4D] dark:text-slate-200">
                <span>₹</span>
                <input
                  type="number"
                  value={roadTaxFine}
                  onChange={(e) => setRoadTaxFine(Number(e.target.value))}
                  className="w-24 px-2 py-1 rounded-lg bg-white dark:bg-[#0F172A] border border-[#DCE3EC] dark:border-slate-700 text-right font-mono text-xs font-bold text-[#172B4D] dark:text-slate-200 focus:outline-none focus:border-[#1769D2]"
                />
              </div>
            </div>

            <div className="flex items-center justify-between p-3 rounded-xl bg-[#F5F7FA] dark:bg-slate-900/60 border border-[#DCE3EC] dark:border-slate-700">
              <div>
                <p className="font-bold text-[#172B4D] dark:text-slate-200">Riding Without Helmet</p>
                <p className="text-[11px] text-[#64748B] dark:text-slate-400">Section 129 / 194D Mandatory safety</p>
              </div>
              <div className="flex items-center gap-1 font-mono font-bold text-[#172B4D] dark:text-slate-200">
                <span>₹</span>
                <input
                  type="number"
                  value={helmetFine}
                  onChange={(e) => setHelmetFine(Number(e.target.value))}
                  className="w-24 px-2 py-1 rounded-lg bg-white dark:bg-[#0F172A] border border-[#DCE3EC] dark:border-slate-700 text-right font-mono text-xs font-bold text-[#172B4D] dark:text-slate-200 focus:outline-none focus:border-[#1769D2]"
                />
              </div>
            </div>

            <div className="flex items-center justify-between p-3 rounded-xl bg-[#F5F7FA] dark:bg-slate-900/60 border border-[#DCE3EC] dark:border-slate-700">
              <div>
                <p className="font-bold text-[#172B4D] dark:text-slate-200">Missing Mandatory Document</p>
                <p className="text-[11px] text-[#64748B] dark:text-slate-400">Unregistered statutory certificate</p>
              </div>
              <div className="flex items-center gap-1 font-mono font-bold text-[#172B4D] dark:text-slate-200">
                <span>₹</span>
                <input
                  type="number"
                  value={missingDocFine}
                  onChange={(e) => setMissingDocFine(Number(e.target.value))}
                  className="w-24 px-2 py-1 rounded-lg bg-white dark:bg-[#0F172A] border border-[#DCE3EC] dark:border-slate-700 text-right font-mono text-xs font-bold text-[#172B4D] dark:text-slate-200 focus:outline-none focus:border-[#1769D2]"
                />
              </div>
            </div>
          </div>
        </section>
      )}

      {/* ─────────────────────────────────────────────────────────────────────────────
          SECTION 8: SYSTEM TELEMETRY & DIAGNOSTICS
         ───────────────────────────────────────────────────────────────────────────── */}
      {(activeSection === 'all' || activeSection === 'system') && (
        <section className="p-6 rounded-2xl border border-[#DCE3EC] dark:border-slate-800 bg-white dark:bg-[#1E293B] shadow-sm space-y-4 transition-colors">
          <div className="flex items-center gap-2.5 border-b border-[#DCE3EC] dark:border-slate-800 pb-3">
            <div className="h-9 w-9 rounded-xl bg-[#EFF5FF] dark:bg-blue-950/60 flex items-center justify-center text-[#16A36A] border border-[#DCE3EC] dark:border-slate-700">
              <Cpu className="h-5 w-5" />
            </div>
            <div>
              <h3 className="font-bold text-base text-[#172B4D] dark:text-slate-100">
                System Telemetry & AI Engines
              </h3>
              <p className="text-xs text-[#64748B] dark:text-slate-400">
                Hardware & computer vision pipeline audit for demonstration
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
            <div className="flex items-center justify-between p-3 rounded-xl bg-[#F5F7FA] dark:bg-slate-900/60 border border-[#DCE3EC] dark:border-slate-700">
              <span className="text-[#64748B] dark:text-slate-400">Backend REST API:</span>
              <span className="font-mono font-semibold text-[#172B4D] dark:text-slate-200">Flask 3.x (Port 5001)</span>
            </div>

            <div className="flex items-center justify-between p-3 rounded-xl bg-[#F5F7FA] dark:bg-slate-900/60 border border-[#DCE3EC] dark:border-slate-700">
              <span className="text-[#64748B] dark:text-slate-400">Database Engine:</span>
              <span className="font-mono font-semibold text-[#172B4D] dark:text-slate-200">SQLite 3 (50 Demo Fleet)</span>
            </div>

            <div className="flex items-center justify-between p-3 rounded-xl bg-[#F5F7FA] dark:bg-slate-900/60 border border-[#DCE3EC] dark:border-slate-700">
              <span className="text-[#64748B] dark:text-slate-400">ANPR Localization Model:</span>
              <span className="font-semibold text-[#16A36A] flex items-center gap-1">
                <CheckCircle2 className="h-3.5 w-3.5" />
                YOLOv8 Plate Detector (`license_plate_detector.pt`)
              </span>
            </div>

            <div className="flex items-center justify-between p-3 rounded-xl bg-[#F5F7FA] dark:bg-slate-900/60 border border-[#DCE3EC] dark:border-slate-700">
              <span className="text-[#64748B] dark:text-slate-400">OCR Character Extractor:</span>
              <span className="font-semibold text-[#1769D2] dark:text-blue-400">EasyOCR PyTorch (CRAFT + english_g2)</span>
            </div>

            <div className="flex items-center justify-between p-3 rounded-xl bg-[#F5F7FA] dark:bg-slate-900/60 border border-[#DCE3EC] dark:border-slate-700">
              <span className="text-[#64748B] dark:text-slate-400">Helmet Violation Pipeline:</span>
              <span className="font-semibold text-[#172B4D] dark:text-slate-200">YOLOv8 Rider + CV Head Curvature Analysis</span>
            </div>

            <div className="flex items-center justify-between p-3 rounded-xl bg-[#F5F7FA] dark:bg-slate-900/60 border border-[#DCE3EC] dark:border-slate-700">
              <span className="text-[#64748B] dark:text-slate-400">PDF & QR Citation Engine:</span>
              <span className="font-semibold text-[#172B4D] dark:text-slate-200">ReportLab 4.x + QRCode 8.x</span>
            </div>
          </div>
        </section>
      )}
    </div>
  );
}
