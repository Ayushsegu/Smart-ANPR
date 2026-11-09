/**
 * services/api.js - Centralized Axios API Service
 * ===============================================
 * Smart ANPR Vehicle Verification System
 *
 * Configures the Axios client and connects to the Flask backend endpoints.
 * Handles environment-based baseURL resolution and error unwrapping.
 */

import axios from 'axios';

const BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

const apiClient = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,
  headers: {
    'Accept': 'application/json',
  },
});

// Request interceptor to attach bearer token if available
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('anpr_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor to unwrap error messages cleanly
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    let message = 'An unexpected error occurred while communicating with the server.';
    if (error.response?.data?.error) {
      message = error.response.data.error;
    } else if (error.message) {
      message = error.message;
    }
    return Promise.reject(new Error(message));
  }
);

// ─────────────────────────────────────────────────────────────────────────────
// API Methods
// ─────────────────────────────────────────────────────────────────────────────

/** Backend Health Check */
export const getHealth = async () => {
  const res = await apiClient.get('/api/health');
  return res.data;
};

/** Retrieve all registered vehicles with optional search & filters */
export const getVehicles = async (params = {}) => {
  const res = await apiClient.get('/api/vehicles', { params });
  return res.data;
};

/** Retrieve dynamic fleet compliance metrics from local SQLite records */
export const getFleetMetrics = async () => {
  const res = await apiClient.get('/api/vehicles/metrics');
  return res.data;
};

/** Register a new demo vehicle (Admin/Officer capability) */
export const registerDemoVehicle = async (vehicleData) => {
  const res = await apiClient.post('/api/vehicles', vehicleData);
  return res.data;
};

/** Retrieve single vehicle particulars by plate */
export const getVehicleByPlate = async (plate) => {
  const cleanPlate = encodeURIComponent(plate.trim().toUpperCase());
  const res = await apiClient.get(`/api/vehicles/${cleanPlate}`);
  return res.data;
};

/** Retrieve vehicle documents by plate */
export const getVehicleDocuments = async (plate) => {
  const cleanPlate = encodeURIComponent(plate.trim().toUpperCase());
  const res = await apiClient.get(`/api/vehicles/${cleanPlate}/documents`);
  return res.data;
};

/** Comprehensive Vehicle Compliance & Fine Verification */
export const verifyVehicle = async (plate) => {
  const cleanPlate = encodeURIComponent(plate.trim().toUpperCase());
  const res = await apiClient.get(`/api/vehicles/${cleanPlate}/verify`);
  return res.data;
};

/** ANPR Vehicle Image Detection & OCR Upload */
export const uploadANPRImage = async (formData, onProgress) => {
  const res = await apiClient.post('/api/anpr/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    onUploadProgress: (progressEvent) => {
      if (onProgress && progressEvent.total) {
        const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        onProgress(percent);
      }
    },
  });
  return res.data;
};

/** Retrieve all challans with optional plate filter */
export const getChallans = async (registrationNumber = null) => {
  const params = {};
  if (registrationNumber) {
    params.registration_number = registrationNumber.trim().toUpperCase();
  }
  const res = await apiClient.get('/api/challans', { params });
  return res.data;
};

/** Retrieve single challan citation by number (QR Target) */
export const getChallanByNumber = async (challanNumber) => {
  const cleanNum = encodeURIComponent(challanNumber.trim().toUpperCase());
  const res = await apiClient.get(`/api/challans/${cleanNum}`);
  return res.data;
};

/** Generate new digital challan */
export const generateChallan = async (payload) => {
  const res = await apiClient.post('/api/challans/generate', payload);
  return res.data;
};

/** Simulate demonstration payment (PAY, FAIL, RESET) */
export const payChallan = async (challanNumber, action = 'PAY') => {
  const cleanNum = encodeURIComponent(challanNumber.trim().toUpperCase());
  const res = await apiClient.post(`/api/challans/${cleanNum}/pay`, { action });
  return res.data;
};

/** Build download URL for challan PDF */
export const getPdfUrl = (challanNumber) => {
  const cleanNum = encodeURIComponent(challanNumber.trim().toUpperCase());
  return `${BASE_URL}/api/challans/${cleanNum}/pdf`;
};

/** Build image URL for challan QR code */
export const getQrUrl = (challanNumber) => {
  const cleanNum = encodeURIComponent(challanNumber.trim().toUpperCase());
  return `${BASE_URL}/api/challans/${cleanNum}/qr`;
};

// ─────────────────────────────────────────────────────────────────────────────
// Authentication & Officer Management APIs
// ─────────────────────────────────────────────────────────────────────────────

/** Officer Login with username/ID and password */
export const loginOfficer = async (credentials) => {
  const res = await apiClient.post('/api/auth/login', credentials);
  if (res.data?.token) {
    localStorage.setItem('anpr_token', res.data.token);
    localStorage.setItem('anpr_officer', JSON.stringify(res.data.officer));
  }
  return res.data;
};

/** Get authenticated officer profile */
export const getAuthMe = async () => {
  const res = await apiClient.get('/api/auth/me');
  return res.data;
};

/** Get officer customization preferences */
export const getUserPreferences = async () => {
  const res = await apiClient.get('/api/auth/preferences');
  return res.data;
};

/** Save officer customization preferences */
export const saveUserPreferences = async (preferences) => {
  const res = await apiClient.put('/api/auth/preferences', preferences);
  return res.data;
};

/** Get all officers (Admin only) */
export const getOfficers = async () => {
  const res = await apiClient.get('/api/auth/officers');
  return res.data;
};

/** Register new officer (Admin only) */
export const createOfficer = async (officerData) => {
  const res = await apiClient.post('/api/auth/officers', officerData);
  return res.data;
};

/** Clear authentication state */
export const logoutOfficer = () => {
  localStorage.removeItem('anpr_token');
  localStorage.removeItem('anpr_officer');
};

/** Update officer details or active status (Admin only) */
export const updateOfficer = async (officerId, data) => {
  const res = await apiClient.put(`/api/auth/officers/${officerId}`, data);
  return res.data;
};

// ─────────────────────────────────────────────────────────────────────────────
// Detection History & GPS Inspection APIs
// ─────────────────────────────────────────────────────────────────────────────

/** Retrieve inspection history with search and filters */
export const getInspections = async (params = {}) => {
  const res = await apiClient.get('/api/inspections', { params });
  return res.data;
};

/** Retrieve single inspection details by ID */
export const getInspectionById = async (id) => {
  const res = await apiClient.get(`/api/inspections/${id}`);
  return res.data;
};

/** Create manual inspection log */
export const createInspection = async (payload) => {
  const res = await apiClient.post('/api/inspections', payload);
  return res.data;
};

// ─────────────────────────────────────────────────────────────────────────────
// Helmet Detection APIs
// ─────────────────────────────────────────────────────────────────────────────

/** Analyze vehicle/rider image for helmet compliance */
export const detectHelmet = async (formData) => {
  const res = await apiClient.post('/api/helmet/detect', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return res.data;
};

/** Get helmet detection model status */
export const getHelmetStatus = async () => {
  const res = await apiClient.get('/api/helmet/status');
  return res.data;
};

export default apiClient;
