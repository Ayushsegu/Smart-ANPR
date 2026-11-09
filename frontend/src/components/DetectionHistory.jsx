/**
 * components/DetectionHistory.jsx - Vehicle Detection History & Inspection Audits
 * ==============================================================================
 * Smart ANPR Vehicle Verification System
 * Design: STYLE 4 – PREMIUM ENTERPRISE (WHITE + BLUE + GREY)
 *
 * Requirements:
 * - Inspection ID (e.g. INSP-2026-9001)
 * - Registration number
 * - Date and time
 * - Detection confidence (YOLOv8)
 * - Verification result & violation information
 * - Officer details
 * - Search and status filters
 * - Inspection detail modal view
 */

import React, { useState, useEffect } from 'react';
import {
  History,
  Search,
  Filter,
  RefreshCw,
  ExternalLink,
  Eye,
  Camera,
  MapPin,
  Calendar,
  Clock,
  User,
  ShieldCheck,
  AlertTriangle,
  Receipt,
  X,
} from 'lucide-react';
import LicensePlateBadge from './LicensePlateBadge';
import StatusBadge from './common/StatusBadge';
import Breadcrumbs from './common/Breadcrumbs';
import EmptyState from './common/EmptyState';
import { getInspections } from '../services/api';

export default function DetectionHistory({ onVerifyPlate, onNewChallan, showToast }) {
  const [inspections, setInspections] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [selectedInspection, setSelectedInspection] = useState(null);

  const fetchHistory = async () => {
    setLoading(true);
    try {
      const res = await getInspections({
        search: searchQuery || undefined,
        status: statusFilter !== 'ALL' ? statusFilter : undefined,
      });
      setInspections(res.inspections || []);
    } catch (err) {
      showToast?.({
        type: 'error',
        title: 'Failed to load inspection history',
        message: err.message,
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, [statusFilter]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    fetchHistory();
  };

  return (
    <div className="space-y-6">
      {/* ──────────────── Top Breadcrumbs Bar ──────────────── */}
      <Breadcrumbs
        pageTitle="Detection History"
        category="Audit Log"
        badge={
          <span className="text-xs font-mono font-bold px-3 py-1 rounded-full bg-[#EFF5FF] text-[#1769D2] border border-[#DCE3EC]">
            {inspections.length} Recorded Inspections
          </span>
        }
      />

      {/* ──────────────── Controls: Search & Filter ──────────────── */}
      <div className="rounded-xl border border-[#DCE3EC] bg-white p-4 shadow-sm flex flex-col sm:flex-row items-center justify-between gap-4">
        {/* Search */}
        <form onSubmit={handleSearchSubmit} className="relative w-full sm:w-96">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-[#64748B]" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search by Plate (e.g. DL01AB1234) or Node..."
            className="w-full pl-10 pr-4 py-2 rounded-lg bg-[#F5F7FA] border border-[#DCE3EC] text-xs font-medium text-[#172B4D] placeholder-[#64748B] focus:outline-none focus:border-[#1769D2] focus:bg-white uppercase transition-all"
          />
        </form>

        {/* Status Filter Buttons */}
        <div className="flex items-center gap-2 w-full sm:w-auto overflow-x-auto pb-1 sm:pb-0">
          <span className="text-xs font-bold text-[#64748B] flex items-center gap-1 shrink-0">
            <Filter className="h-3.5 w-3.5" />
            <span>Status:</span>
          </span>
          {['ALL', 'COMPLIANT', 'VIOLATION'].map((st) => (
            <button
              key={st}
              onClick={() => setStatusFilter(st)}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-colors shrink-0 cursor-pointer ${
                statusFilter === st
                  ? 'bg-[#1769D2] text-white shadow-sm'
                  : 'bg-[#F5F7FA] text-[#64748B] hover:text-[#172B4D] border border-[#DCE3EC]'
              }`}
            >
              {st}
            </button>
          ))}

          <button
            onClick={fetchHistory}
            className="p-1.5 rounded-lg bg-[#F5F7FA] border border-[#DCE3EC] text-[#64748B] hover:text-[#1769D2] transition-colors shrink-0 cursor-pointer ml-1"
            title="Refresh Inspection Data"
          >
            <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin text-[#1769D2]' : ''}`} />
          </button>
        </div>
      </div>

      {/* ──────────────── Inspections Table ──────────────── */}
      <div className="rounded-xl border border-[#DCE3EC] bg-white shadow-sm overflow-hidden">
        {loading ? (
          <div className="py-16 text-center space-y-3">
            <div className="h-8 w-8 mx-auto rounded-full border-2 border-[#1769D2] border-t-transparent animate-spin"></div>
            <p className="text-xs font-bold text-[#64748B]">Querying surveillance database...</p>
          </div>
        ) : inspections.length === 0 ? (
          <EmptyState
            title="No inspection records found"
            description="No matching vehicle detections found for the current search query or filter."
            actionLabel="Reset Search Filter"
            onAction={() => {
              setSearchQuery('');
              setStatusFilter('ALL');
            }}
          />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-[#F5F7FA] border-b border-[#DCE3EC] text-[#64748B] uppercase tracking-wider text-[10px]">
                <tr>
                  <th className="py-3 px-4 font-bold">Inspection ID</th>
                  <th className="py-3 px-4 font-bold">Registration Plate</th>
                  <th className="py-3 px-4 font-bold">Date & Time</th>
                  <th className="py-3 px-4 font-bold">Checkpoint Location</th>
                  <th className="py-3 px-4 font-bold">Verification Status</th>
                  <th className="py-3 px-4 font-bold">Infractions Summary</th>
                  <th className="py-3 px-4 font-bold">Officer</th>
                  <th className="py-3 px-4 font-bold text-center">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#DCE3EC]">
                {inspections.map((insp) => (
                  <tr key={insp.id} className="hover:bg-[#F5F7FA]/70 transition-colors">
                    <td className="py-3 px-4 font-mono font-bold text-[#1769D2]">
                      {insp.inspection_code}
                    </td>
                    <td className="py-3 px-4">
                      <LicensePlateBadge plate={insp.registration_number} size="sm" />
                    </td>
                    <td className="py-3 px-4 font-mono text-[#64748B] whitespace-nowrap">
                      {insp.inspection_time ? insp.inspection_time.substring(0, 16) : '—'}
                    </td>
                    <td className="py-3 px-4 text-[#172B4D] font-medium max-w-[180px] truncate">
                      {insp.location_name}
                    </td>
                    <td className="py-3 px-4">
                      <StatusBadge status={insp.verification_status} size="sm" />
                    </td>
                    <td className="py-3 px-4 text-[#64748B] max-w-[200px] truncate">
                      {insp.violations_summary || '—'}
                    </td>
                    <td className="py-3 px-4 text-[#64748B] whitespace-nowrap">
                      {insp.officer_name || 'Duty Patrol'}
                    </td>
                    <td className="py-3 px-4 text-center">
                      <button
                        onClick={() => setSelectedInspection(insp)}
                        className="p-1.5 rounded-lg bg-[#EFF5FF] hover:bg-[#DDEBFF] text-[#1769D2] border border-[#DCE3EC] transition-colors cursor-pointer"
                        title="View Full Inspection Audit"
                      >
                        <Eye className="h-3.5 w-3.5" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* ──────────────── Inspection Detail Modal ──────────────── */}
      {selectedInspection && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#172B4D]/40 backdrop-blur-xs animate-in fade-in duration-100">
          <div className="w-full max-w-xl rounded-2xl border border-[#DCE3EC] bg-white p-6 shadow-2xl space-y-5 animate-in zoom-in-95 duration-150">
            {/* Modal Header */}
            <div className="flex items-center justify-between pb-3 border-b border-[#DCE3EC]">
              <div className="space-y-0.5">
                <span className="font-mono text-xs font-bold text-[#1769D2]">
                  {selectedInspection.inspection_code}
                </span>
                <h3 className="text-base font-black text-[#172B4D]">
                  Roadside Inspection Audit Log
                </h3>
              </div>
              <button
                onClick={() => setSelectedInspection(null)}
                className="p-1.5 rounded-lg text-[#64748B] hover:text-[#172B4D] hover:bg-[#F5F7FA] cursor-pointer"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            {/* Vehicle Plate & Status */}
            <div className="flex items-center justify-between p-3.5 rounded-xl bg-[#F5F7FA] border border-[#DCE3EC]">
              <div className="flex items-center gap-3">
                <LicensePlateBadge plate={selectedInspection.registration_number} size="md" />
                <div>
                  <p className="text-xs font-bold text-[#172B4D]">Optical Detection Active</p>
                  <p className="text-[10px] text-[#64748B] font-mono">
                    YOLO Conf: {Math.round((selectedInspection.detection_confidence || 0.95) * 100)}% &bull; OCR Conf: {Math.round((selectedInspection.ocr_confidence || 0.92) * 100)}%
                  </p>
                </div>
              </div>
              <StatusBadge status={selectedInspection.verification_status} size="lg" />
            </div>

            {/* Evidence Visual Crop if present */}
            {selectedInspection.plate_image_url && (
              <div className="space-y-1.5">
                <p className="text-xs font-bold text-[#172B4D]">Cropped Number Plate Evidence:</p>
                <div className="h-20 w-full rounded-xl border border-[#DCE3EC] bg-slate-900 flex items-center justify-center overflow-hidden">
                  <img
                    src={selectedInspection.plate_image_url}
                    alt="Cropped License Plate"
                    className="max-h-full max-w-full object-contain"
                  />
                </div>
              </div>
            )}

            {/* Location & Officer Metadata Grid */}
            <div className="grid grid-cols-2 gap-3 text-xs">
              <div className="p-3 rounded-lg border border-[#DCE3EC] bg-[#F5F7FA] space-y-1">
                <span className="text-[#64748B] text-[10px] uppercase font-bold flex items-center gap-1">
                  <MapPin className="h-3 w-3 text-[#1769D2]" /> Checkpoint
                </span>
                <p className="font-semibold text-[#172B4D]">{selectedInspection.location_name}</p>
                <p className="text-[10px] text-[#64748B] font-mono">
                  GPS: {selectedInspection.latitude}, {selectedInspection.longitude}
                </p>
              </div>

              <div className="p-3 rounded-lg border border-[#DCE3EC] bg-[#F5F7FA] space-y-1">
                <span className="text-[#64748B] text-[10px] uppercase font-bold flex items-center gap-1">
                  <User className="h-3 w-3 text-[#1769D2]" /> Officer on Duty
                </span>
                <p className="font-semibold text-[#172B4D]">{selectedInspection.officer_name || 'Insp. Vikram Sharma'}</p>
                <p className="text-[10px] text-[#64748B] font-mono">
                  Logged at: {selectedInspection.inspection_time}
                </p>
              </div>
            </div>

            {/* Violation Details */}
            <div className="space-y-1.5">
              <span className="text-xs font-bold text-[#172B4D]">Violation Summary:</span>
              <p className="text-xs text-[#64748B] p-3 rounded-lg border border-[#DCE3EC] bg-white">
                {selectedInspection.violations_summary || 'No violations identified. Vehicle meets compliance requirements.'}
              </p>
            </div>

            {/* Actions */}
            <div className="flex items-center justify-end gap-3 pt-3 border-t border-[#DCE3EC]">
              {onVerifyPlate && (
                <button
                  onClick={() => {
                    onVerifyPlate(selectedInspection.registration_number);
                    setSelectedInspection(null);
                  }}
                  className="px-4 py-2 rounded-lg bg-[#EFF5FF] hover:bg-[#DDEBFF] text-[#1769D2] font-bold text-xs border border-[#DCE3EC] flex items-center gap-1.5 transition-colors cursor-pointer"
                >
                  <ExternalLink className="h-3.5 w-3.5" />
                  <span>Verify Documents</span>
                </button>
              )}

              <button
                onClick={() => setSelectedInspection(null)}
                className="px-4 py-2 rounded-lg bg-[#1769D2] hover:bg-[#1258B3] text-white font-bold text-xs transition-colors cursor-pointer"
              >
                Close Audit
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
