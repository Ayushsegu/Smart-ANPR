/**
 * App.jsx - Main Application Shell, Router & Authentication Coordinator
 * ======================================================================
 * Smart ANPR Vehicle Verification System
 * Design: STYLE 4 – PREMIUM ENTERPRISE (WHITE + BLUE + GREY)
 * Supports Multi-Language i18n & Theme Context (Light / Dark / System)
 */

import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import Navbar from './components/Navbar';
import DashboardOverview from './components/DashboardOverview';
import ANPRScanner from './components/ANPRScanner';
import DemoFleetTesting from './components/DemoFleetTesting';
import VehicleVerification from './components/VehicleVerification';
import DocumentVerification from './components/DocumentVerification';
import DetectionHistory from './components/DetectionHistory';
import GPSTracking from './components/GPSTracking';
import HelmetDetection from './components/HelmetDetection';
import ChallanManagement from './components/ChallanManagement';
import ReportsAnalytics from './components/ReportsAnalytics';
import OfficerManagement from './components/OfficerManagement';
import Settings from './components/Settings';
import ChallanModal from './components/ChallanModal';
import Toast from './components/Toast';
import LandingPage from './components/LandingPage';
import OfficerLogin from './components/OfficerLogin';
import { logoutOfficer, getAuthMe } from './services/api';
import { ThemeProvider } from './context/ThemeContext';
import { I18nProvider } from './context/I18nContext';

export default function App() {
  // Current active view: 'landing' | 'login' | 'dashboard'
  const [view, setView] = useState(() => {
    const token = localStorage.getItem('anpr_token');
    const officer = localStorage.getItem('anpr_officer');
    return token && officer ? 'dashboard' : 'landing';
  });

  // Current authenticated officer record
  const [currentUser, setCurrentUser] = useState(() => {
    try {
      const stored = localStorage.getItem('anpr_officer');
      const token = localStorage.getItem('anpr_token');
      if (stored && token) {
        return JSON.parse(stored);
      }
    } catch {
      // Fallback
    }
    return null;
  });

  // Dashboard active tab
  const [activeTab, setActiveTab] = useState('dashboard');
  const [selectedChallan, setSelectedChallan] = useState(null);
  const [targetVehiclePlate, setTargetVehiclePlate] = useState('');
  const [toasts, setToasts] = useState([]);
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  // Validate active session token with backend on mount
  useEffect(() => {
    if (view === 'dashboard' && currentUser) {
      getAuthMe()
        .then((data) => {
          if (data?.officer) {
            setCurrentUser(data.officer);
            localStorage.setItem('anpr_officer', JSON.stringify(data.officer));
          }
        })
        .catch(() => {
          // Token expired or invalid -> sign out back to landing
          logoutOfficer();
          setCurrentUser(null);
          setView('landing');
        });
    }
  }, [view]);

  // Helper to append toast notification
  const showToast = ({ type = 'info', title = '', message = '' }) => {
    const id = Date.now() + Math.random().toString(36).substring(2, 6);
    setToasts((prev) => [...prev, { id, type, title, message }]);

    // Auto-dismiss after 5 seconds
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 5000);
  };

  const dismissToast = (id) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  };

  // Login handler
  const handleLoginSuccess = (officer, token) => {
    setCurrentUser(officer);
    setView('dashboard');
    setActiveTab('dashboard');
    showToast({
      type: 'success',
      title: 'Authentication Successful',
      message: `Welcome back, ${officer.full_name || officer.username}. Duty patrol station online.`,
    });
  };

  // Logout handler
  const handleLogout = () => {
    logoutOfficer();
    setCurrentUser(null);
    setView('landing');
    setActiveTab('dashboard');
    showToast({
      type: 'info',
      title: 'Session Ended',
      message: 'You have been securely signed out. Returned to public portal.',
    });
  };

  // Switch to vehicle verification with a pre-filled license plate
  const handleVerifyPlate = (plate) => {
    setTargetVehiclePlate(plate);
    setActiveTab('vehicles');
  };

  // Open challan detail modal
  const handleSelectChallan = (challan) => {
    setSelectedChallan(challan);
  };

  // Refresh trigger for components
  const handleRefreshAll = () => {
    setRefreshTrigger((prev) => prev + 1);
    showToast({
      type: 'info',
      title: 'Refreshing Telemetry Feeds',
      message: 'All surveillance feeds and database records re-synchronized.',
    });
  };

  return (
    <ThemeProvider currentUser={currentUser}>
      <I18nProvider currentUser={currentUser}>
        {view === 'landing' && (
          <LandingPage onOpenLogin={() => setView('login')} />
        )}

        {view === 'login' && (
          <OfficerLogin
            onLoginSuccess={handleLoginSuccess}
            onBackToLanding={() => setView('landing')}
          />
        )}

        {view === 'dashboard' && (
          <div className="flex h-screen bg-[#F5F7FA] dark:bg-[#0F172A] text-[#172B4D] dark:text-slate-100 overflow-hidden font-sans transition-colors duration-200">
            {/* Left Sidebar Navigation */}
            <Sidebar
              activeTab={activeTab}
              onSelectTab={(tab) => {
                setActiveTab(tab);
              }}
              currentUser={currentUser}
              onLogout={handleLogout}
            />

            {/* Right Content Area */}
            <div className="flex-1 flex flex-col overflow-hidden bg-white dark:bg-[#0F172A] transition-colors duration-200">
              {/* Top Header */}
              <Navbar
                onRefreshAll={handleRefreshAll}
                currentUser={currentUser}
                onLogout={handleLogout}
                onQuickSearch={handleVerifyPlate}
              />

              {/* Scrollable View Container */}
              <main className="flex-1 overflow-y-auto p-6 md:p-8 bg-[#F5F7FA] dark:bg-[#0F172A] transition-colors duration-200">
                <div className="max-w-7xl mx-auto">
                  {activeTab === 'dashboard' && (
                    <DashboardOverview
                      key={refreshTrigger}
                      onNavigate={setActiveTab}
                      onSelectChallan={handleSelectChallan}
                    />
                  )}

                  {activeTab === 'anpr' && (
                    <ANPRScanner
                      key={refreshTrigger}
                      onSelectChallan={handleSelectChallan}
                      showToast={showToast}
                    />
                  )}

                  {activeTab === 'fleet' && (
                    <DemoFleetTesting
                      key={refreshTrigger}
                      onVerifyPlate={handleVerifyPlate}
                      currentUser={currentUser}
                      showToast={showToast}
                    />
                  )}

                  {activeTab === 'vehicles' && (
                    <VehicleVerification
                      key={`${targetVehiclePlate}-${refreshTrigger}`}
                      initialPlate={targetVehiclePlate}
                      onSelectChallan={handleSelectChallan}
                      showToast={showToast}
                    />
                  )}

                  {activeTab === 'documents' && (
                    <DocumentVerification
                      key={refreshTrigger}
                      onVerifyPlate={handleVerifyPlate}
                      showToast={showToast}
                    />
                  )}

                  {activeTab === 'history' && (
                    <DetectionHistory
                      key={refreshTrigger}
                      onVerifyPlate={handleVerifyPlate}
                      onNewChallan={() => setActiveTab('vehicles')}
                      showToast={showToast}
                    />
                  )}

                  {activeTab === 'gps' && (
                    <GPSTracking
                      key={refreshTrigger}
                      onVerifyPlate={handleVerifyPlate}
                      showToast={showToast}
                    />
                  )}

                  {activeTab === 'helmet' && (
                    <HelmetDetection
                      key={refreshTrigger}
                      onSelectChallan={handleSelectChallan}
                      showToast={showToast}
                    />
                  )}

                  {activeTab === 'challans' && (
                    <ChallanManagement
                      key={refreshTrigger}
                      onSelectChallan={handleSelectChallan}
                      onNewChallan={() => setActiveTab('vehicles')}
                      showToast={showToast}
                    />
                  )}

                  {activeTab === 'reports' && (
                    <ReportsAnalytics
                      key={refreshTrigger}
                      showToast={showToast}
                    />
                  )}

                  {activeTab === 'officers' && currentUser?.role === 'ADMIN' && (
                    <OfficerManagement
                      key={refreshTrigger}
                      currentUser={currentUser}
                      showToast={showToast}
                    />
                  )}

                  {activeTab === 'settings' && (
                    <Settings
                      key={refreshTrigger}
                      showToast={showToast}
                      currentUser={currentUser}
                    />
                  )}
                </div>
              </main>
            </div>

            {/* Global Challan Modal */}
            {selectedChallan && (
              <ChallanModal
                challan={selectedChallan}
                onClose={() => setSelectedChallan(null)}
                onChallanUpdated={(updated) => setSelectedChallan(updated)}
                showToast={showToast}
              />
            )}
          </div>
        )}

        {/* Global Toast Alerts */}
        <Toast toasts={toasts} onDismiss={dismissToast} />
      </I18nProvider>
    </ThemeProvider>
  );
}
