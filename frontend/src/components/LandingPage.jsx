/**
 * components/LandingPage.jsx - Public Portal & ANPR Platform Introduction
 * =======================================================================
 * Smart ANPR Vehicle Verification System
 * Design: STYLE 4 – PREMIUM ENTERPRISE (WHITE + BLUE + GREY)
 * Supports Multi-Language i18n & Theme Context (Light / Dark / System)
 */

import React, { useState } from 'react';
import {
  Shield,
  Camera,
  Car,
  FileCheck2,
  Receipt,
  Scan,
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  LogIn,
  Eye,
  Cpu,
  MapPin,
  Clock,
  Sparkles,
  ChevronRight,
  HelpCircle,
  Phone,
  Mail,
  ExternalLink,
  ShieldCheck,
  HardHat,
  BarChart3,
  Navigation,
  Globe2,
  Sun,
  Moon,
  Laptop,
} from 'lucide-react';
import LicensePlateBadge from './LicensePlateBadge';
import anprVisual from '../assets/anpr-login-visual.png';
import { useTheme } from '../context/ThemeContext';
import { useTranslation, SUPPORTED_LANGUAGES } from '../context/I18nContext';

export default function LandingPage({ onOpenLogin }) {
  const { theme, setTheme } = useTheme();
  const { language, changeLanguage, t } = useTranslation();

  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [showLangMenu, setShowLangMenu] = useState(false);

  const scrollToSection = (id) => {
    const el = document.getElementById(id);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth' });
    }
    setMobileMenuOpen(false);
  };

  const toggleTheme = () => {
    if (theme === 'light') setTheme('dark');
    else if (theme === 'dark') setTheme('system');
    else setTheme('light');
  };

  const capabilities = [
    {
      icon: Camera,
      title: t('landing.cap_1_title', {}, 'AI Number Plate Recognition'),
      desc: t('landing.cap_1_desc', {}, 'Deep neural networks (YOLOv8) detect vehicle high-security registration plates in complex roadway lighting, angles, and velocities with high confidence.'),
      tag: 'YOLOv8 & EasyOCR',
    },
    {
      icon: FileCheck2,
      title: t('landing.cap_2_title', {}, 'Vehicle Document Verification'),
      desc: t('landing.cap_2_desc', {}, 'Instant automated cross-referencing of VAHAN/SARATHI digital registry documents: RC validity, Third-Party Insurance, PUC fitness, and Road Tax.'),
      tag: 'Parivahan Compliance',
    },
    {
      icon: HardHat,
      title: t('landing.cap_5_title', {}, 'Helmet Violation Detection'),
      desc: t('landing.cap_5_desc', {}, 'Computer vision analysis identifies two-wheeler riders, tracks rider head curvature, and detects safety helmet compliance with manual review fallback.'),
      tag: 'Rider Safety Audit',
    },
    {
      icon: Navigation,
      title: t('landing.cap_6_title', {}, 'GPS-Based Inspection'),
      desc: t('landing.cap_6_desc', {}, 'Roadside optical checkpoints tag geographic coordinates, checkpoint nodes, patrol zones, and geofenced corridors with explicit officer consent.'),
      tag: 'Geolocation Mapping',
    },
    {
      icon: Receipt,
      title: t('landing.cap_4_title', {}, 'Digital Challan Generation'),
      desc: t('landing.cap_4_desc', {}, 'Instant synthesis of cryptographic digital e-challans containing violation breakdown, fine totals, secure verification QR codes, and ReportLab PDF receipts.'),
      tag: 'QR-PDF Citations',
    },
    {
      icon: BarChart3,
      title: t('landing.cap_3_title', {}, 'Analytics and Reporting'),
      desc: t('landing.cap_3_desc', {}, 'Real-time telemetry reports detailing daily/monthly vehicle volume, top violation hotspots, payment settlement metrics, and exportable audit registries.'),
      tag: 'Intelligence Reports',
    },
  ];

  const steps = [
    {
      num: '01',
      title: t('landing.stage_1_title', {}, 'Vehicle Image Capture'),
      desc: t('landing.stage_1_desc', {}, 'Roadside optical sensor, patrol smartphone, or static CCTV captures high-resolution photograph of the oncoming vehicle.'),
      icon: Camera,
    },
    {
      num: '02',
      title: t('landing.stage_2_title', {}, 'Number Plate Detection'),
      desc: t('landing.stage_2_desc', {}, 'Trained YOLOv8 neural network localizes the vehicle license plate, predicts bounding coordinates, and extracts high-fidelity cropped plate.'),
      icon: Scan,
    },
    {
      num: '03',
      title: t('landing.stage_3_title', {}, 'OCR Recognition'),
      desc: t('landing.stage_3_desc', {}, 'EasyOCR offline neural text engine extracts alphanumeric characters, normalizes Indian state RTO syntax, and standardizes plate numbers.'),
      icon: Cpu,
    },
    {
      num: '04',
      title: t('landing.stage_4_title', {}, 'Vehicle & Document Verification'),
      desc: t('landing.stage_4_desc', {}, 'Central vehicle database queries ownership, registration validity, insurance policies, pollution fitness certificates, and road tax status.'),
      icon: FileCheck2,
    },
    {
      num: '05',
      title: t('landing.stage_5_title', {}, 'Violation & Digital Challan'),
      desc: t('landing.stage_5_desc', {}, 'If expired documents or violations are flagged, the system computes official fine schedules, generates a signed PDF challan, and issues a payment QR.'),
      icon: Receipt,
    },
  ];

  return (
    <div className="min-h-screen bg-white dark:bg-[#0F172A] text-[#172B4D] dark:text-slate-100 font-sans selection:bg-[#EFF5FF] selection:text-[#1769D2] transition-colors duration-200">
      {/* ──────────────── Top Navigation Bar ──────────────── */}
      <header className="sticky top-0 z-40 bg-white/95 dark:bg-[#1E293B]/95 backdrop-blur-md border-b border-[#DCE3EC] dark:border-slate-800 shadow-[0_1px_3px_rgba(23,43,77,0.03)] transition-colors">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between">
          {/* Logo & Brand */}
          <div className="flex items-center gap-3 cursor-pointer" onClick={() => scrollToSection('hero')}>
            <div className="h-11 w-11 rounded-xl bg-[#1769D2] flex items-center justify-center text-white shadow-md shadow-[#1769D2]/20">
              <ShieldCheck className="h-6 w-6 text-white" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-black text-base text-[#172B4D] dark:text-slate-100 tracking-tight">
                  {t('nav.brand_title', {}, 'Smart ANPR')}
                </span>
                <span className="text-[10px] px-2 py-0.5 rounded font-bold bg-[#EFF5FF] dark:bg-blue-950 text-[#1769D2] dark:text-blue-400 border border-[#DCE3EC] dark:border-slate-700">
                  Enterprise v2.0
                </span>
              </div>
              <p className="text-[11px] text-[#64748B] dark:text-slate-400 font-medium tracking-wide">
                Traffic Enforcement & Document Verification
              </p>
            </div>
          </div>

          {/* Desktop Navigation Links */}
          <nav className="hidden md:flex items-center gap-7 text-xs font-bold text-[#64748B] dark:text-slate-300">
            <button
              onClick={() => scrollToSection('hero')}
              className="hover:text-[#1769D2] dark:hover:text-blue-400 transition-colors py-1 cursor-pointer"
            >
              {t('landing.nav_home', {}, 'Home')}
            </button>
            <button
              onClick={() => scrollToSection('about')}
              className="hover:text-[#1769D2] dark:hover:text-blue-400 transition-colors py-1 cursor-pointer"
            >
              {t('landing.nav_about', {}, 'About ANPR')}
            </button>
            <button
              onClick={() => scrollToSection('how-it-works')}
              className="hover:text-[#1769D2] dark:hover:text-blue-400 transition-colors py-1 cursor-pointer"
            >
              {t('landing.nav_pipeline', {}, 'How It Works')}
            </button>
            <button
              onClick={() => scrollToSection('capabilities')}
              className="hover:text-[#1769D2] dark:hover:text-blue-400 transition-colors py-1 cursor-pointer"
            >
              {t('landing.nav_capabilities', {}, 'Capabilities')}
            </button>
            <button
              onClick={() => scrollToSection('contact')}
              className="hover:text-[#1769D2] dark:hover:text-blue-400 transition-colors py-1 cursor-pointer"
            >
              {t('landing.nav_contact', {}, 'Contact')}
            </button>
          </nav>

          {/* Right Controls: Language, Theme & Officer Login */}
          <div className="flex items-center gap-2.5 sm:gap-3">
            {/* Quick Language Dropdown */}
            <div className="relative">
              <button
                onClick={() => setShowLangMenu(!showLangMenu)}
                className="h-9 px-2.5 rounded-xl border border-[#DCE3EC] dark:border-slate-700 bg-white dark:bg-[#1E293B] hover:bg-[#F5F7FA] dark:hover:bg-slate-800 text-[#172B4D] dark:text-slate-200 text-xs font-bold flex items-center gap-1.5 shadow-sm transition-colors cursor-pointer"
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
              className="h-9 w-9 rounded-xl border border-[#DCE3EC] dark:border-slate-700 bg-white dark:bg-[#1E293B] hover:bg-[#F5F7FA] dark:hover:bg-slate-800 text-[#172B4D] dark:text-slate-200 flex items-center justify-center shadow-sm transition-colors cursor-pointer"
            >
              {theme === 'dark' ? (
                <Moon className="h-4 w-4 text-blue-400" />
              ) : theme === 'light' ? (
                <Sun className="h-4 w-4 text-amber-500" />
              ) : (
                <Laptop className="h-4 w-4 text-emerald-500" />
              )}
            </button>

            {/* Officer Login Button */}
            <button
              onClick={onOpenLogin}
              className="px-5 py-2.5 rounded-xl bg-[#1769D2] hover:bg-[#1258B3] text-white font-bold text-xs flex items-center gap-2 transition-all shadow-sm shadow-[#1769D2]/25 transform active:scale-95 cursor-pointer"
            >
              <LogIn className="h-3.5 w-3.5" />
              <span>{t('landing.officer_login', {}, 'Officer Login')}</span>
            </button>

            {/* Mobile menu toggle */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden p-2 rounded-lg text-[#64748B] dark:text-slate-300 hover:bg-[#F5F7FA] dark:hover:bg-slate-800 border border-[#DCE3EC] dark:border-slate-700"
            >
              <span className="sr-only">Toggle Menu</span>
              <div className="w-5 h-4 flex flex-col justify-between">
                <span className="w-full h-0.5 bg-[#172B4D] dark:bg-slate-200 rounded"></span>
                <span className="w-full h-0.5 bg-[#172B4D] dark:bg-slate-200 rounded"></span>
                <span className="w-full h-0.5 bg-[#172B4D] dark:bg-slate-200 rounded"></span>
              </div>
            </button>
          </div>
        </div>

        {/* Mobile Dropdown Menu */}
        {mobileMenuOpen && (
          <div className="md:hidden border-t border-[#DCE3EC] dark:border-slate-800 bg-white dark:bg-[#1E293B] px-4 py-4 space-y-2 shadow-lg">
            <button
              onClick={() => scrollToSection('hero')}
              className="block w-full text-left py-2 px-3 rounded-lg text-xs font-bold text-[#172B4D] dark:text-slate-200 hover:bg-[#F5F7FA] dark:hover:bg-slate-800"
            >
              {t('landing.nav_home', {}, 'Home')}
            </button>
            <button
              onClick={() => scrollToSection('about')}
              className="block w-full text-left py-2 px-3 rounded-lg text-xs font-bold text-[#172B4D] dark:text-slate-200 hover:bg-[#F5F7FA] dark:hover:bg-slate-800"
            >
              {t('landing.nav_about', {}, 'About ANPR')}
            </button>
            <button
              onClick={() => scrollToSection('how-it-works')}
              className="block w-full text-left py-2 px-3 rounded-lg text-xs font-bold text-[#172B4D] dark:text-slate-200 hover:bg-[#F5F7FA] dark:hover:bg-slate-800"
            >
              {t('landing.nav_pipeline', {}, 'How It Works')}
            </button>
            <button
              onClick={() => scrollToSection('capabilities')}
              className="block w-full text-left py-2 px-3 rounded-lg text-xs font-bold text-[#172B4D] dark:text-slate-200 hover:bg-[#F5F7FA] dark:hover:bg-slate-800"
            >
              {t('landing.nav_capabilities', {}, 'Capabilities')}
            </button>
            <button
              onClick={() => scrollToSection('contact')}
              className="block w-full text-left py-2 px-3 rounded-lg text-xs font-bold text-[#172B4D] dark:text-slate-200 hover:bg-[#F5F7FA] dark:hover:bg-slate-800"
            >
              {t('landing.nav_contact', {}, 'Contact')}
            </button>
          </div>
        )}
      </header>

      {/* ──────────────── Hero Section ──────────────── */}
      <section id="hero" className="relative py-16 md:py-24 border-b border-[#DCE3EC] dark:border-slate-800 overflow-hidden bg-white dark:bg-[#0F172A] transition-colors">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
            {/* Left Column: Heading, Subtitle & Action Buttons */}
            <div className="lg:col-span-6 space-y-6">
              <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full text-xs font-bold bg-[#EFF5FF] dark:bg-blue-950/60 text-[#1769D2] dark:text-blue-400 border border-[#DCE3EC] dark:border-slate-700">
                <span className="h-2 w-2 rounded-full bg-[#16A36A] animate-pulse"></span>
                <span>AI-Powered Traffic Surveillance & Compliance Engine</span>
              </div>

              <h1 className="text-3xl sm:text-4xl lg:text-5xl font-black text-[#172B4D] dark:text-slate-100 tracking-tight leading-tight">
                {t('landing.hero_title', {}, 'Smart ANPR Vehicle Verification System')}
              </h1>

              <p className="text-base md:text-lg text-[#64748B] dark:text-slate-400 leading-relaxed max-w-xl">
                {t('landing.hero_subtitle', {}, 'Intelligent vehicle recognition, automated document verification and smarter traffic monitoring powered by Artificial Intelligence.')}
              </p>

              {/* Action Buttons */}
              <div className="flex flex-wrap items-center gap-4 pt-2">
                <button
                  onClick={onOpenLogin}
                  className="px-7 py-3.5 rounded-xl bg-[#1769D2] hover:bg-[#1258B3] text-white font-bold text-sm flex items-center gap-2.5 transition-all shadow-md shadow-[#1769D2]/25 transform active:scale-95 cursor-pointer"
                >
                  <LogIn className="h-4 w-4" />
                  <span>{t('landing.officer_login', {}, 'Officer Login')}</span>
                </button>

                <button
                  onClick={() => scrollToSection('how-it-works')}
                  className="px-6 py-3.5 rounded-xl bg-[#F5F7FA] dark:bg-[#1E293B] hover:bg-[#EFF5FF] dark:hover:bg-slate-800 text-[#172B4D] dark:text-slate-200 hover:text-[#1769D2] font-bold text-sm border border-[#DCE3EC] dark:border-slate-700 flex items-center gap-2 transition-colors cursor-pointer"
                >
                  <span>{t('landing.explore_system', {}, 'Explore System')}</span>
                  <ArrowRight className="h-4 w-4" />
                </button>
              </div>

              {/* Status Badges */}
              <div className="pt-4 grid grid-cols-3 gap-3 max-w-md border-t border-[#DCE3EC] dark:border-slate-800">
                <div className="space-y-0.5">
                  <p className="text-xl font-mono font-bold text-[#172B4D] dark:text-slate-100">YOLOv8</p>
                  <p className="text-[11px] text-[#64748B] dark:text-slate-400 font-medium">Neural Plate Detector</p>
                </div>
                <div className="space-y-0.5">
                  <p className="text-xl font-mono font-bold text-[#172B4D] dark:text-slate-100">EasyOCR</p>
                  <p className="text-[11px] text-[#64748B] dark:text-slate-400 font-medium">Offline Character Engine</p>
                </div>
                <div className="space-y-0.5">
                  <p className="text-xl font-mono font-bold text-[#172B4D] dark:text-slate-100">100%</p>
                  <p className="text-[11px] text-[#64748B] dark:text-slate-400 font-medium">Automated Citations</p>
                </div>
              </div>
            </div>

            {/* Right Column: High-Impact Visual Graphic */}
            <div className="lg:col-span-6">
              <div className="relative rounded-2xl border border-[#DCE3EC] dark:border-slate-800 bg-[#F5F7FA] dark:bg-slate-900/60 p-3 sm:p-4 shadow-xl space-y-4">
                <div className="relative rounded-xl overflow-hidden bg-white dark:bg-slate-950 border border-[#DCE3EC] dark:border-slate-800 shadow-sm">
                  <img
                    src={anprVisual}
                    alt="Smart ANPR Traffic Camera and Number Plate Recognition"
                    className="w-full h-auto object-contain max-h-[380px] rounded-lg select-none"
                  />
                  {/* Overlay Scanner Telemetry Badge */}
                  <div className="absolute top-3 left-3 flex items-center gap-2 bg-white/95 dark:bg-[#1E293B]/95 backdrop-blur-md px-3 py-1.5 rounded-lg border border-[#DCE3EC] dark:border-slate-700 shadow-sm">
                    <span className="h-2 w-2 rounded-full bg-[#16A36A] animate-ping"></span>
                    <span className="text-[11px] font-bold text-[#172B4D] dark:text-slate-200">Optical Detection: ACTIVE</span>
                  </div>
                </div>

                {/* Live Telemetry Pill Row */}
                <div className="grid grid-cols-4 gap-2 pt-1 text-center">
                  <div className="p-2 rounded-lg bg-white dark:bg-[#1E293B] border border-[#DCE3EC] dark:border-slate-800">
                    <p className="text-[10px] font-bold text-[#64748B] dark:text-slate-400">RC</p>
                    <p className="text-[11px] font-bold text-[#16A36A]">VALID</p>
                  </div>
                  <div className="p-2 rounded-lg bg-white dark:bg-[#1E293B] border border-[#DCE3EC] dark:border-slate-800">
                    <p className="text-[10px] font-bold text-[#64748B] dark:text-slate-400">INSURANCE</p>
                    <p className="text-[11px] font-bold text-[#16A36A]">VALID</p>
                  </div>
                  <div className="p-2 rounded-lg bg-white dark:bg-[#1E293B] border border-[#DCE3EC] dark:border-slate-800">
                    <p className="text-[10px] font-bold text-[#64748B] dark:text-slate-400">PUC</p>
                    <p className="text-[11px] font-bold text-[#16A36A]">VALID</p>
                  </div>
                  <div className="p-2 rounded-lg bg-white dark:bg-[#1E293B] border border-[#DCE3EC] dark:border-slate-800">
                    <p className="text-[10px] font-bold text-[#64748B] dark:text-slate-400">ROAD TAX</p>
                    <p className="text-[11px] font-bold text-[#16A36A]">VALID</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ──────────────── About ANPR Section ──────────────── */}
      <section id="about" className="py-20 bg-[#F5F7FA] dark:bg-slate-900/50 border-b border-[#DCE3EC] dark:border-slate-800 transition-colors">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-12">
          <div className="max-w-3xl space-y-3">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-bold bg-white dark:bg-[#1E293B] text-[#1769D2] dark:text-blue-400 border border-[#DCE3EC] dark:border-slate-700">
              <HelpCircle className="h-3.5 w-3.5" />
              <span>Technology Overview</span>
            </div>
            <h2 className="text-2xl sm:text-3xl font-black text-[#172B4D] dark:text-slate-100 tracking-tight">
              About Automatic Number Plate Recognition (ANPR)
            </h2>
            <p className="text-sm sm:text-base text-[#64748B] dark:text-slate-400 leading-relaxed">
              Automatic Number Plate Recognition (ANPR) is a technology that uses cameras and artificial intelligence to automatically read and identify vehicle license plates. In modern traffic management, ANPR helps traffic authorities monitor vehicles, verify compliance with registration and pollution rules, and detect traffic violations efficiently.
            </p>
          </div>

          {/* 3 Technology Pillars */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="p-6 rounded-2xl bg-white dark:bg-[#1E293B] border border-[#DCE3EC] dark:border-slate-800 shadow-sm space-y-3">
              <div className="h-10 w-10 rounded-xl bg-[#EFF5FF] dark:bg-blue-950/60 border border-[#DCE3EC] dark:border-slate-700 flex items-center justify-center text-[#1769D2]">
                <Camera className="h-5 w-5" />
              </div>
              <h3 className="text-base font-bold text-[#172B4D] dark:text-slate-100">YOLOv8 Plate Detection</h3>
              <p className="text-xs text-[#64748B] dark:text-slate-400 leading-relaxed">
                Trained deep convolutional network predicts vehicle and plate bounding boxes with high precision, isolating the license plate coordinates even in adverse weather or oblique angles.
              </p>
            </div>

            <div className="p-6 rounded-2xl bg-white dark:bg-[#1E293B] border border-[#DCE3EC] dark:border-slate-800 shadow-sm space-y-3">
              <div className="h-10 w-10 rounded-xl bg-[#EFF5FF] dark:bg-blue-950/60 border border-[#DCE3EC] dark:border-slate-700 flex items-center justify-center text-[#1769D2]">
                <Cpu className="h-5 w-5" />
              </div>
              <h3 className="text-base font-bold text-[#172B4D] dark:text-slate-100">EasyOCR Character Engine</h3>
              <p className="text-xs text-[#64748B] dark:text-slate-400 leading-relaxed">
                Recognizes text from cropped license plates using CRAFT text detection and ResNet-based sequence recognition, validated against Indian RTO registration formats.
              </p>
            </div>

            <div className="p-6 rounded-2xl bg-white dark:bg-[#1E293B] border border-[#DCE3EC] dark:border-slate-800 shadow-sm space-y-3">
              <div className="h-10 w-10 rounded-xl bg-[#EFF5FF] dark:bg-blue-950/60 border border-[#DCE3EC] dark:border-slate-700 flex items-center justify-center text-[#1769D2]">
                <ShieldCheck className="h-5 w-5" />
              </div>
              <h3 className="text-base font-bold text-[#172B4D] dark:text-slate-100">Real-Time Compliance Audit</h3>
              <p className="text-xs text-[#64748B] dark:text-slate-400 leading-relaxed">
                Immediately matches recognized plates against the vehicle database to evaluate RC status, Insurance validity, Pollution Under Control fitness, and commercial Road Tax dues.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ──────────────── How It Works Section (5 Sequential Steps) ──────────────── */}
      <section id="how-it-works" className="py-20 bg-white dark:bg-[#0F172A] border-b border-[#DCE3EC] dark:border-slate-800 transition-colors">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-14">
          <div className="text-center max-w-2xl mx-auto space-y-3">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-bold bg-[#EFF5FF] dark:bg-blue-950/60 text-[#1769D2] dark:text-blue-400 border border-[#DCE3EC] dark:border-slate-700">
              <Sparkles className="h-3.5 w-3.5" />
              <span>{t('landing.pipeline_title', {}, '5-Stage Processing Pipeline')}</span>
            </div>
            <h2 className="text-2xl sm:text-3xl font-black text-[#172B4D] dark:text-slate-100 tracking-tight">
              {t('landing.pipeline_subtitle', {}, 'How the System Works')}
            </h2>
            <p className="text-sm text-[#64748B] dark:text-slate-400">
              From roadside capture to verified digital citation in under 300 milliseconds.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            {steps.map((st) => {
              const Icon = st.icon;
              return (
                <div
                  key={st.num}
                  className="p-5 rounded-2xl bg-[#F5F7FA] dark:bg-[#1E293B] border border-[#DCE3EC] dark:border-slate-800 space-y-3 relative flex flex-col justify-between"
                >
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="font-mono text-2xl font-black text-[#1769D2] dark:text-blue-400">
                        {st.num}
                      </span>
                      <div className="h-8 w-8 rounded-lg bg-white dark:bg-slate-900 border border-[#DCE3EC] dark:border-slate-700 flex items-center justify-center text-[#1769D2] shadow-sm">
                        <Icon className="h-4 w-4" />
                      </div>
                    </div>
                    <h3 className="text-sm font-bold text-[#172B4D] dark:text-slate-100">{st.title}</h3>
                    <p className="text-xs text-[#64748B] dark:text-slate-400 leading-relaxed">{st.desc}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* ──────────────── Key Capabilities Section ──────────────── */}
      <section id="capabilities" className="py-20 bg-[#F5F7FA] dark:bg-slate-900/50 border-b border-[#DCE3EC] dark:border-slate-800 transition-colors">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-12">
          <div className="max-w-2xl space-y-3">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-bold bg-white dark:bg-[#1E293B] text-[#1769D2] dark:text-blue-400 border border-[#DCE3EC] dark:border-slate-700">
              <Shield className="h-3.5 w-3.5" />
              <span>{t('landing.capabilities_title', {}, 'Core Modules')}</span>
            </div>
            <h2 className="text-2xl sm:text-3xl font-black text-[#172B4D] dark:text-slate-100 tracking-tight">
              {t('landing.capabilities_subtitle', {}, 'Key Capabilities')}
            </h2>
            <p className="text-sm text-[#64748B] dark:text-slate-400">
              Enterprise-grade modules designed for high-density roadway surveillance and officer ease.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {capabilities.map((cap, idx) => {
              const Icon = cap.icon;
              return (
                <div
                  key={idx}
                  className="p-6 rounded-2xl bg-white dark:bg-[#1E293B] border border-[#DCE3EC] dark:border-slate-800 shadow-sm space-y-4 hover:border-[#1769D2]/50 transition-all flex flex-col justify-between"
                >
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <div className="h-10 w-10 rounded-xl bg-[#EFF5FF] dark:bg-blue-950/60 border border-[#DCE3EC] dark:border-slate-700 flex items-center justify-center text-[#1769D2]">
                        <Icon className="h-5 w-5" />
                      </div>
                      <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-[#F5F7FA] dark:bg-slate-900 text-[#64748B] dark:text-slate-400 border border-[#DCE3EC] dark:border-slate-700">
                        {cap.tag}
                      </span>
                    </div>
                    <h3 className="text-base font-bold text-[#172B4D] dark:text-slate-100">{cap.title}</h3>
                    <p className="text-xs text-[#64748B] dark:text-slate-400 leading-relaxed">{cap.desc}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* ──────────────── Contact & Evaluation Footer ──────────────── */}
      <footer id="contact" className="py-16 bg-white dark:bg-[#0F172A] transition-colors">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-10">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div className="md:col-span-2 space-y-3">
              <div className="flex items-center gap-2">
                <div className="h-8 w-8 rounded-lg bg-[#1769D2] flex items-center justify-center text-white">
                  <ShieldCheck className="h-4 w-4" />
                </div>
                <span className="font-black text-base text-[#172B4D] dark:text-slate-100">
                  {t('landing.footer_title', {}, 'Smart ANPR System')}
                </span>
              </div>
              <p className="text-xs text-[#64748B] dark:text-slate-400 leading-relaxed max-w-sm">
                Advanced Computer Vision & Traffic Law Enforcement Demonstration Prototype. Built with Python Flask, Ultralytics YOLOv8, EasyOCR, and React.
              </p>
            </div>

            <div className="space-y-2">
              <p className="text-xs font-bold text-[#172B4D] dark:text-slate-200 uppercase tracking-wider">Quick Navigation</p>
              <ul className="space-y-1 text-xs text-[#64748B] dark:text-slate-400">
                <li><button onClick={() => scrollToSection('about')} className="hover:text-[#1769D2] cursor-pointer">About ANPR</button></li>
                <li><button onClick={() => scrollToSection('how-it-works')} className="hover:text-[#1769D2] cursor-pointer">5-Step Pipeline</button></li>
                <li><button onClick={() => scrollToSection('capabilities')} className="hover:text-[#1769D2] cursor-pointer">System Capabilities</button></li>
                <li><button onClick={onOpenLogin} className="hover:text-[#1769D2] cursor-pointer">Officer Login</button></li>
              </ul>
            </div>

            <div className="space-y-2">
              <p className="text-xs font-bold text-[#172B4D] dark:text-slate-200 uppercase tracking-wider">Patrol Headquarters</p>
              <p className="text-xs text-[#64748B] dark:text-slate-400 leading-relaxed">
                Traffic Police Directorate<br />
                Highway Surveillance Command Hub<br />
                Node: SEC-04 Expressway
              </p>
            </div>
          </div>

          <div className="pt-8 border-t border-[#DCE3EC] dark:border-slate-800 flex flex-col sm:flex-row items-center justify-between text-xs text-[#64748B] dark:text-slate-400 gap-4">
            <p>&copy; {new Date().getFullYear()} Smart ANPR Vehicle Verification System. All rights reserved.</p>
            <p className="text-[11px] text-[#64748B] dark:text-slate-400">
              College Demonstration Prototype &bull; Not for official government prosecution
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
