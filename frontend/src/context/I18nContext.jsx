/**
 * context/I18nContext.jsx - Multi-Language Localization Engine
 * ============================================================
 * Smart ANPR Vehicle Verification System
 *
 * Implements:
 * - English (Default: Standard Indian Traffic Enforcement terminology)
 * - हिन्दी (Hindi: Complete Unicode system translation)
 * - ಕನ್ನಡ (Kannada: Complete native Karnataka state transport translation)
 * - Zero external library dependencies (lightweight native React Context)
 * - Nested dot-notation key lookup with automatic English fallback
 * - Variable interpolation e.g. {{count}}, {{plate}}
 * - Preserves technical identifiers (DL01DM0001, Officer IDs, Challan IDs)
 * - LocalStorage persistence + optional officer preference cloud sync
 */

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { saveUserPreferences } from '../services/api';

import en from '../locales/en.json';
import hi from '../locales/hi.json';
import kn from '../locales/kn.json';

const dictionaries = {
  en,
  hi,
  kn
};

export const SUPPORTED_LANGUAGES = [
  {
    code: 'en',
    label: 'English',
    nativeName: 'English',
    subtitle: 'Standard Indian Enforcement Terminology',
    badge: 'EN'
  },
  {
    code: 'hi',
    label: 'Hindi',
    nativeName: 'हिन्दी',
    subtitle: 'राष्ट्रभाषा हिन्दी - संपूर्ण प्रणाली अनुवाद',
    badge: 'HI'
  },
  {
    code: 'kn',
    label: 'Kannada',
    nativeName: 'ಕನ್ನಡ',
    subtitle: 'ಕರ್ನಾಟಕ ರಾಜ್ಯ ಸಾರಿಗೆ - ಸಂಪೂರ್ಣ ಕನ್ನಡ ಆವೃತ್ತಿ',
    badge: 'KN'
  }
];

const I18nContext = createContext();

export function I18nProvider({ children, currentUser }) {
  const [language, setLanguageState] = useState(() => {
    // 1. Check logged-in user preferences
    if (currentUser?.preferences?.language) {
      const pref = currentUser.preferences.language;
      if (['en', 'hi', 'kn'].includes(pref)) return pref;
    }
    // 2. Fallback to localStorage
    const saved = localStorage.getItem('anpr_language');
    if (saved && ['en', 'hi', 'kn'].includes(saved)) {
      return saved;
    }
    // 3. Fallback to browser language if Hindi or Kannada
    if (typeof navigator !== 'undefined' && navigator.language) {
      const navLang = navigator.language.toLowerCase();
      if (navLang.startsWith('hi')) return 'hi';
      if (navLang.startsWith('kn')) return 'kn';
    }
    return 'en';
  });

  // Sync if currentUser preferences change
  useEffect(() => {
    if (currentUser?.preferences?.language) {
      const pref = currentUser.preferences.language;
      if (['en', 'hi', 'kn'].includes(pref)) {
        setLanguageState(pref);
        localStorage.setItem('anpr_language', pref);
      }
    }
  }, [currentUser]);

  const changeLanguage = useCallback((code) => {
    if (!['en', 'hi', 'kn'].includes(code)) return;
    setLanguageState(code);
    localStorage.setItem('anpr_language', code);

    // Sync to backend officer preferences if logged in
    if (currentUser?.id) {
      saveUserPreferences({ language: code }).catch(() => {});
    }
  }, [currentUser]);

  // Nested property resolver
  const getNestedValue = (obj, path) => {
    if (!obj || !path) return undefined;
    return path.split('.').reduce((acc, part) => (acc && acc[part] !== undefined ? acc[part] : undefined), obj);
  };

  /**
   * t(key, params, fallback)
   * Resolves translation string with dot notation and parameter interpolation
   */
  const t = useCallback((key, params = {}, defaultText = '') => {
    if (!key) return '';

    const currentDict = dictionaries[language] || dictionaries.en;
    let translation = getNestedValue(currentDict, key);

    // Fallback to English if key missing in current language
    if (translation === undefined && language !== 'en') {
      translation = getNestedValue(dictionaries.en, key);
    }

    // Fallback to provided default text or key itself
    if (translation === undefined) {
      translation = defaultText || key;
    }

    if (typeof translation !== 'string') {
      return translation;
    }

    // Interpolate {{param}} or {param}
    if (params && typeof params === 'object') {
      return Object.entries(params).reduce((str, [paramKey, val]) => {
        const regexDouble = new RegExp(`{{\\s*${paramKey}\\s*}}`, 'g');
        const regexSingle = new RegExp(`{\\s*${paramKey}\\s*}`, 'g');
        return str.replace(regexDouble, String(val)).replace(regexSingle, String(val));
      }, translation);
    }

    return translation;
  }, [language]);

  return (
    <I18nContext.Provider
      value={{
        language,
        changeLanguage,
        t,
        supportedLanguages: SUPPORTED_LANGUAGES,
        currentLanguageMeta: SUPPORTED_LANGUAGES.find((l) => l.code === language) || SUPPORTED_LANGUAGES[0]
      }}
    >
      {children}
    </I18nContext.Provider>
  );
}

export function useTranslation() {
  const context = useContext(I18nContext);
  if (!context) {
    throw new Error('useTranslation must be used within an I18nProvider');
  }
  return context;
}
