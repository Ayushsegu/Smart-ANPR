/**
 * context/ThemeContext.jsx - Appearance Theme Context Coordinator
 * ===============================================================
 * Smart ANPR Vehicle Verification System
 *
 * Implements:
 * - Light Mode (Default: White, Blue, Light Grey)
 * - Dark Mode (#0F172A background, #1E293B surfaces, White text)
 * - System Default (Auto-detects OS theme via matchMedia)
 * - Immediate application to entire DOM via 'dark' class on <html>
 * - Local storage persistence + optional backend officer sync
 */

import React, { createContext, useContext, useState, useEffect } from 'react';
import { saveUserPreferences } from '../services/api';

const ThemeContext = createContext();

export function ThemeProvider({ children, currentUser }) {
  const [theme, setThemeState] = useState(() => {
    // 1. Check logged-in user profile preference
    if (currentUser?.preferences?.theme) {
      return currentUser.preferences.theme;
    }
    // 2. Fallback to localStorage
    const saved = localStorage.getItem('anpr_theme');
    if (saved && ['light', 'dark', 'system'].includes(saved)) {
      return saved;
    }
    // 3. Default to 'light' (Enterprise White & Blue)
    return 'light';
  });

  const [resolvedTheme, setResolvedTheme] = useState('light');

  // Sync when currentUser changes after login
  useEffect(() => {
    if (currentUser?.preferences?.theme) {
      setThemeState(currentUser.preferences.theme);
      localStorage.setItem('anpr_theme', currentUser.preferences.theme);
    }
  }, [currentUser]);

  useEffect(() => {
    const applyTheme = () => {
      let active = theme;
      if (theme === 'system') {
        const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
        active = prefersDark ? 'dark' : 'light';
      }

      setResolvedTheme(active);

      const root = document.documentElement;
      if (active === 'dark') {
        root.classList.add('dark');
      } else {
        root.classList.remove('dark');
      }
    };

    applyTheme();

    if (theme === 'system' && window.matchMedia) {
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
      const handleChange = () => applyTheme();
      mediaQuery.addEventListener('change', handleChange);
      return () => mediaQuery.removeEventListener('change', handleChange);
    }
  }, [theme]);

  const setTheme = (newTheme) => {
    if (!['light', 'dark', 'system'].includes(newTheme)) return;
    setThemeState(newTheme);
    localStorage.setItem('anpr_theme', newTheme);

    // If officer is logged in, sync with backend preferences
    if (currentUser?.id) {
      saveUserPreferences({ theme: newTheme }).catch(() => {});
    }
  };

  return (
    <ThemeContext.Provider value={{ theme, resolvedTheme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
}
