/**
 * components/GPSTracking.jsx - Roadside Geolocation & Checkpoint Mapping
 * =======================================================================
 * Smart ANPR Vehicle Verification System
 * Design: STYLE 4 – PREMIUM ENTERPRISE (WHITE + BLUE + GREY)
 *
 * Requirements:
 * - Inspection location
 * - Latitude and longitude
 * - Interactive map view & radar sweep
 * - Location-based history
 * - Explicit location permission handling (No unauthorized tracking)
 */

import React, { useState, useEffect } from 'react';
import {
  Navigation,
  MapPin,
  ShieldCheck,
  Compass,
  AlertTriangle,
  CheckCircle2,
  Lock,
  RefreshCw,
  Layers,
  Radio,
  Car,
  Clock,
  ArrowRight,
} from 'lucide-react';
import StatusBadge from './common/StatusBadge';
import Breadcrumbs from './common/Breadcrumbs';
import { getInspections } from '../services/api';

export default function GPSTracking({ onVerifyPlate, showToast }) {
  // Geolocation permission state: 'prompt' | 'granted' | 'denied' | 'unsupported'
  const [permissionStatus, setPermissionStatus] = useState('prompt');
  const [deviceCoords, setDeviceCoords] = useState(null);
  const [isLocating, setIsLocating] = useState(false);
  const [locationError, setLocationError] = useState(null);

  // Selected checkpoint
  const [selectedCheckpoint, setSelectedCheckpoint] = useState(0);
  const [inspections, setInspections] = useState([]);

  const checkpoints = [
    {
      id: 'node-01',
      name: 'Sector 04 Expressway Checkpoint',
      lat: 28.5355,
      lon: 77.3910,
      zone: 'Zone 4 Expressway',
      activeOfficers: 2,
      cameras: 4,
      speedLimit: '80 km/h',
      status: 'ONLINE',
      vehiclesLogged: 48,
    },
    {
      id: 'node-02',
      name: 'Connaught Place Outer Circle Node',
      lat: 28.6139,
      lon: 77.2090,
      zone: 'Central Commercial Ring',
      activeOfficers: 3,
      cameras: 6,
      speedLimit: '50 km/h',
      status: 'ONLINE',
      vehiclesLogged: 62,
    },
    {
      id: 'node-03',
      name: 'NH-48 Kherki Daula Toll Plaza',
      lat: 28.4595,
      lon: 77.0266,
      zone: 'Interstate Freight Corridor',
      activeOfficers: 4,
      cameras: 8,
      speedLimit: '90 km/h',
      status: 'ONLINE',
      vehiclesLogged: 95,
    },
    {
      id: 'node-04',
      name: 'Outer Ring Road G.T. Karnal Node',
      lat: 28.7041,
      lon: 77.1025,
      zone: 'North Transit Axis',
      activeOfficers: 2,
      cameras: 4,
      speedLimit: '70 km/h',
      status: 'ONLINE',
      vehiclesLogged: 34,
    },
    {
      id: 'node-05',
      name: 'Noida-Greater Noida Km 12',
      lat: 28.5700,
      lon: 77.3200,
      zone: 'High-Speed Flyover Corridor',
      activeOfficers: 2,
      cameras: 4,
      speedLimit: '100 km/h',
      status: 'ONLINE',
      vehiclesLogged: 53,
    },
  ];

  // Check initial permission status if supported
  useEffect(() => {
    if ('permissions' in navigator && navigator.permissions?.query) {
      navigator.permissions.query({ name: 'geolocation' }).then((result) => {
        setPermissionStatus(result.state);
        result.onchange = () => setPermissionStatus(result.state);
      }).catch(() => {
        // Fallback
      });
    }

    getInspections({ limit: 20 })
      .then((res) => setInspections(res.inspections || []))
      .catch(() => {});
  }, []);

  // Request explicit geolocation from user device
  const requestLocation = () => {
    if (!('geolocation' in navigator)) {
      setPermissionStatus('unsupported');
      setLocationError('Geolocation is not supported by your current browser.');
      return;
    }

    setIsLocating(true);
    setLocationError(null);

    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setDeviceCoords({
          latitude: pos.coords.latitude,
          longitude: pos.coords.longitude,
          accuracy: Math.round(pos.coords.accuracy),
          altitude: pos.coords.altitude ? Math.round(pos.coords.altitude) : null,
          heading: pos.coords.heading,
          speed: pos.coords.speed,
          timestamp: new Date(pos.timestamp).toLocaleTimeString(),
        });
        setPermissionStatus('granted');
        setIsLocating(false);
        showToast?.({
          type: 'success',
          title: 'GPS Location Verified',
          message: `Coordinates calibrated: ${pos.coords.latitude.toFixed(4)}, ${pos.coords.longitude.toFixed(4)} (±${Math.round(pos.coords.accuracy)}m)`,
        });
      },
      (err) => {
        setIsLocating(false);
        setPermissionStatus('denied');
        setLocationError(err.message || 'Location access permission was denied by user.');
        showToast?.({
          type: 'error',
          title: 'Location Request Denied',
          message: 'Permission is required to geotag roadside vehicle inspections.',
        });
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 30000,
      }
    );
  };

  const activeCheckpoint = checkpoints[selectedCheckpoint] || checkpoints[0];

  return (
    <div className="space-y-6">
      {/* ──────────────── Top Breadcrumbs ──────────────── */}
      <Breadcrumbs
        pageTitle="GPS Tracking & Checkpoints"
        category="Roadway Geolocation"
        badge={
          <span className="text-xs font-mono font-bold px-3 py-1 rounded-full bg-[#ECFDF3] text-[#16A36A] border border-[#A6F4C5] flex items-center gap-1.5">
            <span className="h-2 w-2 rounded-full bg-[#16A36A] animate-pulse"></span>
            5 Active Checkpoints Online
          </span>
        }
      />

      {/* ──────────────── Explicit Permission Request Card ──────────────── */}
      <div className="rounded-xl border border-[#DCE3EC] bg-white p-5 shadow-sm space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-start gap-3">
            <div className="h-10 w-10 rounded-xl bg-[#EFF5FF] border border-[#DCE3EC] flex items-center justify-center text-[#1769D2] shrink-0">
              <Compass className="h-5 w-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-sm font-bold text-[#172B4D]">Patrol Device Geolocation Status</h3>
                <span
                  className={`text-[10px] font-bold px-2 py-0.5 rounded uppercase border ${
                    permissionStatus === 'granted'
                      ? 'bg-[#ECFDF3] text-[#16A36A] border-[#A6F4C5]'
                      : permissionStatus === 'denied'
                      ? 'bg-[#FEF2F2] text-[#DC4545] border-[#FCA5A5]'
                      : 'bg-[#FEFBE8] text-[#E5A000] border-[#FDE047]'
                  }`}
                >
                  {permissionStatus}
                </span>
              </div>
              <p className="text-xs text-[#64748B] mt-0.5">
                Explicit consent is required before tagging live roadside camera scans with GPS coordinates.
              </p>
            </div>
          </div>

          <button
            onClick={requestLocation}
            disabled={isLocating}
            className="px-4 py-2.5 rounded-lg bg-[#1769D2] hover:bg-[#1258B3] disabled:opacity-50 text-white font-bold text-xs flex items-center gap-2 transition-all shadow-sm shrink-0 cursor-pointer"
          >
            <Radio className={`h-3.5 w-3.5 ${isLocating ? 'animate-spin' : ''}`} />
            <span>{permissionStatus === 'granted' ? 'Recalibrate GPS' : 'Request Device Geolocation'}</span>
          </button>
        </div>

        {/* Coords telemetry if granted */}
        {deviceCoords && (
          <div className="p-3.5 rounded-lg bg-[#F5F7FA] border border-[#DCE3EC] grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
            <div>
              <span className="text-[10px] font-bold text-[#64748B] uppercase">Latitude</span>
              <p className="font-mono font-bold text-[#172B4D]">{deviceCoords.latitude.toFixed(6)}° N</p>
            </div>
            <div>
              <span className="text-[10px] font-bold text-[#64748B] uppercase">Longitude</span>
              <p className="font-mono font-bold text-[#172B4D]">{deviceCoords.longitude.toFixed(6)}° E</p>
            </div>
            <div>
              <span className="text-[10px] font-bold text-[#64748B] uppercase">Accuracy</span>
              <p className="font-mono font-bold text-[#16A36A]">±{deviceCoords.accuracy} meters</p>
            </div>
            <div>
              <span className="text-[10px] font-bold text-[#64748B] uppercase">Last Calibrated</span>
              <p className="font-mono font-bold text-[#64748B]">{deviceCoords.timestamp}</p>
            </div>
          </div>
        )}

        {locationError && (
          <div className="p-3 rounded-lg bg-[#FEF2F2] border border-[#FCA5A5] text-[#DC4545] text-xs flex items-center gap-2">
            <AlertTriangle className="h-4 w-4 shrink-0" />
            <span>{locationError}</span>
          </div>
        )}
      </div>

      {/* ──────────────── Map Visualization & Checkpoints Grid ──────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: Interactive Vector Map Visualizer (8 cols) */}
        <div className="lg:col-span-8 rounded-xl border border-[#DCE3EC] bg-white p-5 shadow-sm space-y-4">
          <div className="flex items-center justify-between border-b border-[#DCE3EC] pb-3">
            <div>
              <h3 className="text-sm font-bold text-[#172B4D]">Expressway Surveillance Grid</h3>
              <p className="text-xs text-[#64748B]">Real-time optical checkpoint radar and perimeter map</p>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-[#EFF5FF] text-[#1769D2] border border-[#DCE3EC]">
                GRID: NCR-EXPRESSWAY-SECTOR-04
              </span>
            </div>
          </div>

          {/* Interactive SVG Radar Map Display */}
          <div className="relative h-96 w-full rounded-xl border border-[#DCE3EC] bg-gradient-to-b from-[#F5F7FA] to-white p-4 flex items-center justify-center overflow-hidden">
            {/* Grid Lines */}
            <div className="absolute inset-0 bg-[radial-gradient(#DCE3EC_1px,transparent_1px)] [background-size:24px_24px] opacity-70"></div>

            {/* Simulated Radar Concentric Range Rings */}
            <div className="absolute h-80 w-80 rounded-full border border-[#DCE3EC] pointer-events-none"></div>
            <div className="absolute h-56 w-56 rounded-full border border-[#DCE3EC] pointer-events-none"></div>
            <div className="absolute h-32 w-32 rounded-full border border-[#1769D2]/30 pointer-events-none"></div>

            {/* Radar Crosshairs */}
            <div className="absolute inset-x-0 top-1/2 h-px bg-[#DCE3EC]"></div>
            <div className="absolute inset-y-0 left-1/2 w-px bg-[#DCE3EC]"></div>

            {/* Checkpoint Pins */}
            {checkpoints.map((cp, idx) => {
              const isSelected = selectedCheckpoint === idx;
              // Map coordinates to 2D container offsets
              const xOffsets = [50, 42, 28, 58, 68];
              const yOffsets = [45, 35, 62, 22, 68];
              const left = `${xOffsets[idx]}%`;
              const top = `${yOffsets[idx]}%`;

              return (
                <div
                  key={cp.id}
                  onClick={() => setSelectedCheckpoint(idx)}
                  className="absolute cursor-pointer transform -translate-x-1/2 -translate-y-1/2 z-20 group"
                  style={{ left, top }}
                >
                  <div
                    className={`p-2 rounded-xl border transition-all flex items-center gap-1.5 shadow-md ${
                      isSelected
                        ? 'bg-[#1769D2] text-white border-[#1769D2] ring-4 ring-[#EFF5FF]'
                        : 'bg-white text-[#172B4D] border-[#DCE3EC] hover:border-[#1769D2]'
                    }`}
                  >
                    <MapPin className={`h-3.5 w-3.5 ${isSelected ? 'text-white' : 'text-[#1769D2]'}`} />
                    <span className="text-[10px] font-bold whitespace-nowrap">{cp.name.split(' ')[0]}</span>
                  </div>

                  {/* Ping Animation */}
                  {isSelected && (
                    <span className="absolute -inset-1 rounded-xl bg-[#1769D2]/30 animate-ping -z-10"></span>
                  )}
                </div>
              );
            })}

            {/* Map Legend */}
            <div className="absolute bottom-3 left-3 bg-white/95 backdrop-blur-md px-3 py-1.5 rounded-lg border border-[#DCE3EC] text-[10px] text-[#64748B] flex items-center gap-3 shadow-sm z-30">
              <span className="flex items-center gap-1 font-semibold text-[#172B4D]">
                <span className="h-2 w-2 rounded-full bg-[#1769D2]"></span> Fixed Node
              </span>
              <span className="flex items-center gap-1 font-semibold text-[#172B4D]">
                <span className="h-2 w-2 rounded-full bg-[#16A36A]"></span> Active Stream
              </span>
              <span>Coordinates Datum: WGS 84</span>
            </div>
          </div>
        </div>

        {/* Right: Selected Node Details (4 cols) */}
        <div className="lg:col-span-4 rounded-xl border border-[#DCE3EC] bg-white p-5 shadow-sm space-y-4 flex flex-col justify-between">
          <div className="space-y-3">
            <div className="border-b border-[#DCE3EC] pb-3">
              <span className="text-[10px] font-mono font-bold text-[#1769D2] uppercase">
                {activeCheckpoint.id}
              </span>
              <h3 className="text-base font-bold text-[#172B4D] leading-tight">
                {activeCheckpoint.name}
              </h3>
              <p className="text-xs text-[#64748B] mt-0.5">{activeCheckpoint.zone}</p>
            </div>

            <div className="space-y-2.5 text-xs">
              <div className="flex items-center justify-between p-2 rounded-lg bg-[#F5F7FA] border border-[#DCE3EC]">
                <span className="text-[#64748B]">Coordinates</span>
                <span className="font-mono font-bold text-[#172B4D]">{activeCheckpoint.lat}, {activeCheckpoint.lon}</span>
              </div>

              <div className="flex items-center justify-between p-2 rounded-lg bg-[#F5F7FA] border border-[#DCE3EC]">
                <span className="text-[#64748B]">Operational Status</span>
                <StatusBadge status="COMPLIANT" label="ACTIVE STREAM" size="xs" />
              </div>

              <div className="flex items-center justify-between p-2 rounded-lg bg-[#F5F7FA] border border-[#DCE3EC]">
                <span className="text-[#64748B]">Speed Limit</span>
                <span className="font-bold text-[#172B4D]">{activeCheckpoint.speedLimit}</span>
              </div>

              <div className="flex items-center justify-between p-2 rounded-lg bg-[#F5F7FA] border border-[#DCE3EC]">
                <span className="text-[#64748B]">Optical Feeds</span>
                <span className="font-bold text-[#172B4D]">{activeCheckpoint.cameras} High-Speed Cameras</span>
              </div>

              <div className="flex items-center justify-between p-2 rounded-lg bg-[#F5F7FA] border border-[#DCE3EC]">
                <span className="text-[#64748B]">Vehicles Logged Today</span>
                <span className="font-mono font-bold text-[#1769D2]">{activeCheckpoint.vehiclesLogged}</span>
              </div>
            </div>
          </div>

          <div className="pt-3 border-t border-[#DCE3EC]">
            <p className="text-[11px] text-[#64748B] leading-relaxed">
              Optical sensors at this node are synchronized with the central ANPR database and broadcast real-time telemetry to the dashboard overview.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
