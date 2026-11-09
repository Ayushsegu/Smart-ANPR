/**
 * components/OfficerLogin.jsx - Officer & Administrator Authentication Portal
 * ============================================================================
 * Smart ANPR Vehicle Verification System
 * Design: White and Blue Professional Enterprise SaaS UI
 * Supports Multi-Language i18n & Theme Context (Light / Dark / System)
 */

import React, { useState } from 'react';
import {
  Shield,
  Lock,
  User,
  Eye,
  EyeOff,
  ArrowLeft,
  LogIn,
  AlertCircle,
  Camera,
  FileCheck2,
  Receipt,
  CheckCircle2,
  KeyRound,
  ShieldCheck,
  Building2,
  Globe2,
  Sun,
  Moon,
  Laptop,
} from 'lucide-react';
import { loginOfficer } from '../services/api';
import anprVisual from '../assets/anpr-login-visual.png';
import { useTheme } from '../context/ThemeContext';
import { useTranslation, SUPPORTED_LANGUAGES } from '../context/I18nContext';

export default function OfficerLogin({ onLoginSuccess, onBackToLanding }) {
  const { theme, setTheme } = useTheme();
  const { language, changeLanguage, t } = useTranslation();

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [showLangMenu, setShowLangMenu] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMessage('');

    if (!username.trim()) {
      setErrorMessage('Please enter your Officer ID or registered email.');
      return;
    }
    if (!password) {
      setErrorMessage('Please enter your password.');
      return;
    }

    setLoading(true);
    try {
      const response = await loginOfficer({
        username: username.trim(),
        password: password,
      });

      if (response.success && response.token) {
        onLoginSuccess(response.officer, response.token);
      } else {
        setErrorMessage(response.error || 'Authentication failed. Please verify credentials.');
      }
    } catch (err) {
      setErrorMessage(err.message || 'Authentication error. Please check credentials or API server.');
    } finally {
      setLoading(false);
    }
  };

  // Quick fill helper for evaluator testing
  const handleQuickFill = (u, p) => {
    setUsername(u);
    setPassword(p);
    setErrorMessage('');
  };

  const toggleTheme = () => {
    if (theme === 'light') setTheme('dark');
    else if (theme === 'dark') setTheme('system');
    else setTheme('light');
  };

  return (
    <div className="min-h-screen bg-white dark:bg-[#0F172A] text-[#172B4D] dark:text-slate-100 font-sans flex flex-col justify-between selection:bg-[#EFF5FF] selection:text-[#1769D2] transition-colors duration-200">
      {/* ──────────────── Top Navigation Bar ──────────────── */}
      <header className="h-16 border-b border-[#DCE3EC] dark:border-slate-800 bg-white dark:bg-[#1E293B] px-6 md:px-10 flex items-center justify-between sticky top-0 z-30 shadow-[0_1px_3px_rgba(23,43,77,0.03)] transition-colors">
        <button
          onClick={onBackToLanding}
          className="text-xs font-bold text-[#1769D2] dark:text-blue-400 hover:text-[#1258B3] flex items-center gap-2 transition-colors py-1.5 px-3 rounded-lg hover:bg-[#EFF5FF] dark:hover:bg-slate-800 cursor-pointer"
        >
          <ArrowLeft className="h-4 w-4" />
          <span>{t('login.return_home', {}, '← Return to Public Portal')}</span>
        </button>

        <div className="flex items-center gap-2 sm:gap-3">
          {/* Quick Language Dropdown */}
          <div className="relative">
            <button
              onClick={() => setShowLangMenu(!showLangMenu)}
              className="h-8 px-2.5 rounded-lg border border-[#DCE3EC] dark:border-slate-700 bg-white dark:bg-[#1E293B] hover:bg-[#F5F7FA] dark:hover:bg-slate-800 text-[#172B4D] dark:text-slate-200 text-xs font-bold flex items-center gap-1.5 shadow-sm transition-colors cursor-pointer"
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
                    <span>{lang.nativeName}</span>
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
          >
            {theme === 'dark' ? (
              <Moon className="h-3.5 w-3.5 text-blue-400" />
            ) : theme === 'light' ? (
              <Sun className="h-3.5 w-3.5 text-amber-500" />
            ) : (
              <Laptop className="h-3.5 w-3.5 text-emerald-500" />
            )}
          </button>

          <span className="hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-[#EFF5FF] dark:bg-blue-950/60 border border-[#DCE3EC] dark:border-slate-700 text-[11px] font-semibold text-[#1769D2] dark:text-blue-400">
            <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse"></span>
            Enforcement Server Active
          </span>
        </div>
      </header>

      {/* ──────────────── Main Two-Column Container ──────────────── */}
      <main className="flex-1 flex items-center justify-center p-4 sm:p-6 lg:p-10 my-4 md:my-8">
        <div className="w-full max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-12 items-center">
          
          {/* ══════════════════════════════════════════════════════════════════════
              LEFT SIDE – ANPR Information & Prominent Visual Illustration
             ══════════════════════════════════════════════════════════════════════ */}
          <div className="lg:col-span-7 space-y-6">
            {/* System Title & Subtitle */}
            <div className="space-y-2">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-bold bg-[#EFF5FF] dark:bg-blue-950/60 text-[#1769D2] dark:text-blue-400 border border-[#DCE3EC] dark:border-slate-700">
                <ShieldCheck className="h-3.5 w-3.5 text-[#1769D2]" />
                <span>Traffic Police Surveillance Network</span>
              </div>
              <h1 className="text-3xl sm:text-4xl font-black text-[#172B4D] dark:text-slate-100 tracking-tight leading-tight">
                {t('login.left_heading', {}, 'Smart ANPR System')}
              </h1>
              <p className="text-base sm:text-lg font-semibold text-[#1769D2] dark:text-blue-400">
                {t('login.left_subtitle', {}, 'Intelligent Vehicle Recognition and Verification')}
              </p>
            </div>

            {/* Prominent ANPR Traffic-Camera Illustration Container */}
            <div className="rounded-2xl border border-[#DCE3EC] dark:border-slate-800 bg-[#F8FAFC] dark:bg-slate-900/60 p-3 sm:p-4 shadow-md overflow-hidden transition-all">
              <div className="relative rounded-xl overflow-hidden bg-white dark:bg-slate-950 border border-[#DCE3EC]/60 dark:border-slate-800 flex items-center justify-center">
                <img
                  src={anprVisual}
                  alt="Smart ANPR Traffic Camera and Number Plate Recognition"
                  className="w-full h-auto object-contain max-h-[380px] rounded-lg select-none"
                  loading="eager"
                />
              </div>
            </div>

            {/* Project Short Description */}
            <p className="text-sm text-[#42526E] dark:text-slate-400 leading-relaxed">
              {t('login.left_desc', {}, 'An intelligent traffic monitoring solution that uses Artificial Intelligence, Computer Vision and OCR to recognize vehicle number plates, verify vehicle documents and identify possible traffic violations.')}
            </p>

            {/* Three Highlights Below Image */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-2">
              <div className="p-3.5 rounded-xl bg-white dark:bg-[#1E293B] border border-[#DCE3EC] dark:border-slate-800 shadow-sm flex items-start gap-2.5">
                <div className="h-7 w-7 rounded-lg bg-[#EFF5FF] dark:bg-blue-950 text-[#1769D2] dark:text-blue-400 flex items-center justify-center shrink-0">
                  <Camera className="h-4 w-4" />
                </div>
                <div>
                  <h4 className="text-xs font-bold text-[#172B4D] dark:text-slate-200">
                    {t('login.highlight_1', {}, 'AI Number Plate Recognition')}
                  </h4>
                  <p className="text-[11px] text-[#64748B] dark:text-slate-400 mt-0.5">YOLOv8 + EasyOCR</p>
                </div>
              </div>

              <div className="p-3.5 rounded-xl bg-white dark:bg-[#1E293B] border border-[#DCE3EC] dark:border-slate-800 shadow-sm flex items-start gap-2.5">
                <div className="h-7 w-7 rounded-lg bg-[#EFF5FF] dark:bg-blue-950 text-[#1769D2] dark:text-blue-400 flex items-center justify-center shrink-0">
                  <FileCheck2 className="h-4 w-4" />
                </div>
                <div>
                  <h4 className="text-xs font-bold text-[#172B4D] dark:text-slate-200">
                    {t('login.highlight_2', {}, 'Automated Vehicle Verification')}
                  </h4>
                  <p className="text-[11px] text-[#64748B] dark:text-slate-400 mt-0.5">RC, Insurance, PUC, Tax</p>
                </div>
              </div>

              <div className="p-3.5 rounded-xl bg-white dark:bg-[#1E293B] border border-[#DCE3EC] dark:border-slate-800 shadow-sm flex items-start gap-2.5">
                <div className="h-7 w-7 rounded-lg bg-[#EFF5FF] dark:bg-blue-950 text-[#1769D2] dark:text-blue-400 flex items-center justify-center shrink-0">
                  <Receipt className="h-4 w-4" />
                </div>
                <div>
                  <h4 className="text-xs font-bold text-[#172B4D] dark:text-slate-200">
                    {t('login.highlight_3', {}, 'Digital Challan Management')}
                  </h4>
                  <p className="text-[11px] text-[#64748B] dark:text-slate-400 mt-0.5">UPI QR & ReportLab PDF</p>
                </div>
              </div>
            </div>
          </div>

          {/* ══════════════════════════════════════════════════════════════════════
              RIGHT SIDE – Officer Login Form Card
             ══════════════════════════════════════════════════════════════════════ */}
          <div className="lg:col-span-5">
            <div className="bg-white dark:bg-[#1E293B] rounded-2xl border border-[#DCE3EC] dark:border-slate-800 shadow-xl p-6 sm:p-8 space-y-6">
              
              {/* Card Header */}
              <div className="space-y-1.5 border-b border-[#DCE3EC] dark:border-slate-800 pb-5">
                <div className="flex items-center gap-2 text-[#1769D2] dark:text-blue-400 font-bold text-xs uppercase tracking-wider">
                  <Shield className="h-4 w-4" />
                  <span>Official Personnel Portal</span>
                </div>
                <h2 className="text-2xl font-bold text-[#172B4D] dark:text-slate-100">
                  {t('login.title', {}, 'Officer Login')}
                </h2>
                <p className="text-xs text-[#64748B] dark:text-slate-400">
                  {t('login.subtitle', {}, 'Sign in to access the traffic management portal.')}
                </p>
              </div>

              {/* Error Notification */}
              {errorMessage && (
                <div className="p-3.5 rounded-xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900 text-rose-700 dark:text-rose-400 text-xs flex items-start gap-2.5">
                  <AlertCircle className="h-4 w-4 shrink-0 mt-0.5" />
                  <span className="leading-relaxed font-medium">{errorMessage}</span>
                </div>
              )}

              {/* Login Form */}
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-xs font-bold text-[#172B4D] dark:text-slate-200 mb-1.5">
                    {t('login.username_label', {}, 'Officer ID / Username')}
                  </label>
                  <div className="relative">
                    <User className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-[#64748B] dark:text-slate-400" />
                    <input
                      type="text"
                      value={username}
                      onChange={(e) => setUsername(e.target.value)}
                      placeholder={t('login.username_placeholder', {}, 'e.g. officer or admin')}
                      className="w-full pl-10 pr-3.5 py-2.5 rounded-xl bg-white dark:bg-[#0F172A] border border-[#DCE3EC] dark:border-slate-700 text-[#172B4D] dark:text-slate-100 placeholder-[#64748B] dark:placeholder-slate-500 text-xs font-medium focus:outline-none focus:border-[#1769D2] focus:ring-2 focus:ring-[#1769D2]/15 transition-all"
                      autoComplete="username"
                      required
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-bold text-[#172B4D] dark:text-slate-200 mb-1.5">
                    {t('login.password_label', {}, 'Password')}
                  </label>
                  <div className="relative">
                    <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-[#64748B] dark:text-slate-400" />
                    <input
                      type={showPassword ? 'text' : 'password'}
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder={t('login.password_placeholder', {}, 'Enter your secure password')}
                      className="w-full pl-10 pr-10 py-2.5 rounded-xl bg-white dark:bg-[#0F172A] border border-[#DCE3EC] dark:border-slate-700 text-[#172B4D] dark:text-slate-100 placeholder-[#64748B] dark:placeholder-slate-500 text-xs font-medium focus:outline-none focus:border-[#1769D2] focus:ring-2 focus:ring-[#1769D2]/15 transition-all"
                      autoComplete="current-password"
                      required
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3.5 top-1/2 -translate-y-1/2 text-[#64748B] dark:text-slate-400 hover:text-[#172B4D] dark:hover:text-slate-200"
                    >
                      {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </button>
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full py-3 rounded-xl bg-[#1769D2] hover:bg-[#1258B3] text-white font-bold text-xs flex items-center justify-center gap-2 transition-all shadow-md shadow-[#1769D2]/25 cursor-pointer disabled:opacity-50"
                >
                  <LogIn className="h-4 w-4" />
                  <span>
                    {loading
                      ? t('login.signing_in', {}, 'Authenticating Credentials...')
                      : t('login.sign_in_btn', {}, 'Sign In to Duty Portal')}
                  </span>
                </button>
              </form>

              {/* Demo Credentials Fast-Fill */}
              <div className="p-3.5 rounded-xl bg-[#EFF5FF] dark:bg-blue-950/40 border border-[#DCE3EC] dark:border-slate-800 space-y-2">
                <div className="flex items-center gap-1.5 text-[11px] font-bold text-[#1769D2] dark:text-blue-300">
                  <KeyRound className="h-3.5 w-3.5" />
                  <span>{t('login.demo_credentials_title', {}, 'Demonstration Credentials:')}</span>
                </div>
                <div className="grid grid-cols-2 gap-2 text-[11px]">
                  <button
                    type="button"
                    onClick={() => handleQuickFill('admin', 'Admin@123')}
                    className="p-2 rounded-lg bg-white dark:bg-[#1E293B] border border-[#DCE3EC] dark:border-slate-700 text-left hover:border-[#1769D2] transition-colors cursor-pointer"
                  >
                    <span className="block font-bold text-[#172B4D] dark:text-slate-100">Administrator</span>
                    <span className="block font-mono text-[10px] text-[#64748B] dark:text-slate-400">admin / Admin@123</span>
                  </button>
                  <button
                    type="button"
                    onClick={() => handleQuickFill('officer', 'Officer@123')}
                    className="p-2 rounded-lg bg-white dark:bg-[#1E293B] border border-[#DCE3EC] dark:border-slate-700 text-left hover:border-[#1769D2] transition-colors cursor-pointer"
                  >
                    <span className="block font-bold text-[#172B4D] dark:text-slate-100">Patrol Officer</span>
                    <span className="block font-mono text-[10px] text-[#64748B] dark:text-slate-400">officer / Officer@123</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="h-12 border-t border-[#DCE3EC] dark:border-slate-800 bg-[#F8FAFC] dark:bg-slate-900 px-6 flex items-center justify-between text-[11px] text-[#64748B] dark:text-slate-400">
        <span>Smart ANPR System • Intelligent Traffic Surveillance Platform</span>
        <span>MVA 2019 Enforcement Standard</span>
      </footer>
    </div>
  );
}
