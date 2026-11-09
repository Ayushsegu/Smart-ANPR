/**
 * components/DocumentVerification.jsx - Multi-Vehicle Document Registry Browser
 * ==============================================================================
 * Smart ANPR Vehicle Verification System
 * Design: White and Blue Professional Enterprise SaaS UI
 *
 * Implements:
 * - Tabular view of all vehicle document records
 * - Filtering by document status (ALL, EXPIRED, EXPIRING_SOON, VALID)
 * - Filtering by document type (ALL, RC, INSURANCE, PUC, ROAD_TAX)
 * - Search by registration plate or owner name
 * - Quick jump to vehicle verification
 */

import React, { useState, useEffect } from 'react';
import {
  FileCheck2,
  Search,
  Filter,
  AlertTriangle,
  CheckCircle2,
  Clock,
  Car,
  User,
  ExternalLink,
  RefreshCw,
} from 'lucide-react';
import LicensePlateBadge from './LicensePlateBadge';
import { getVehicles } from '../services/api';

export default function DocumentVerification({ onVerifyPlate, showToast }) {
  const [vehicles, setVehicles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL'); // 'ALL' | 'EXPIRED' | 'EXPIRING_SOON' | 'VALID'
  const [typeFilter, setTypeFilter] = useState('ALL'); // 'ALL' | 'RC' | 'INSURANCE' | 'PUC' | 'ROAD_TAX'

  const fetchVehicleDocs = async () => {
    setLoading(true);
    try {
      const data = await getVehicles();
      setVehicles(data.vehicles || []);
    } catch (err) {
      showToast?.({
        type: 'error',
        title: 'Failed to load document records',
        message: err.message,
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchVehicleDocs();
  }, []);

  // Flatten documents for tabular filtering
  const allDocuments = [];
  vehicles.forEach((v) => {
    (v.documents || []).forEach((d) => {
      allDocuments.push({
        ...d,
        registration_number: v.registration_number,
        owner_name: v.owner_name,
        vehicle_type: v.vehicle_type,
        vehicle_model: v.vehicle_model,
      });
    });
  });

  // Calculate counters
  const totalCount = allDocuments.length;
  const expiredCount = allDocuments.filter((d) => d.status === 'EXPIRED').length;
  const expiringCount = allDocuments.filter((d) => d.status === 'EXPIRING_SOON').length;
  const validCount = allDocuments.filter((d) => d.status === 'VALID').length;

  // Apply filters
  const filteredDocs = allDocuments.filter((doc) => {
    const matchesSearch =
      !searchQuery ||
      doc.registration_number.toLowerCase().includes(searchQuery.toLowerCase()) ||
      doc.owner_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      doc.document_number.toLowerCase().includes(searchQuery.toLowerCase());

    const matchesStatus =
      statusFilter === 'ALL' || doc.status?.toUpperCase() === statusFilter;

    const matchesType =
      typeFilter === 'ALL' || doc.document_type?.toUpperCase() === typeFilter;

    return matchesSearch && matchesStatus && matchesType;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#DCE3EC] pb-4">
        <div>
          <h2 className="text-xl md:text-2xl font-bold text-[#172B4D] flex items-center gap-2.5">
            <FileCheck2 className="h-6 w-6 text-[#1769D2]" />
            <span>Document Compliance Registry Browser</span>
          </h2>
          <p className="text-xs text-[#64748B] mt-1">
            Audit RC, Insurance, PUC, and Road Tax records across the registered vehicular database
          </p>
        </div>

        <button
          onClick={fetchVehicleDocs}
          className="px-4 py-2 rounded-xl bg-white hover:bg-[#F8FAFC] text-[#172B4D] text-xs font-bold border border-[#DCE3EC] shadow-sm flex items-center gap-2 transition-colors self-start sm:self-auto"
        >
          <RefreshCw className={`h-3.5 w-3.5 ${loading ? 'animate-spin text-[#1769D2]' : ''}`} />
          <span>Refresh Records</span>
        </button>
      </div>

      {/* Summary KPI Badges */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <button
          onClick={() => setStatusFilter('ALL')}
          className={`p-4 rounded-xl border text-left transition-all ${
            statusFilter === 'ALL'
              ? 'bg-[#EFF5FF] border-[#1769D2] shadow-sm'
              : 'bg-white border-[#DCE3EC] hover:border-[#1769D2]/40 shadow-sm'
          }`}
        >
          <span className="text-xs text-[#64748B] font-semibold uppercase">Total Documents</span>
          <p className="text-2xl font-mono font-bold text-[#172B4D] mt-1">{totalCount}</p>
        </button>

        <button
          onClick={() => setStatusFilter('VALID')}
          className={`p-4 rounded-xl border text-left transition-all ${
            statusFilter === 'VALID'
              ? 'bg-emerald-50 border-emerald-500 shadow-sm'
              : 'bg-white border-[#DCE3EC] hover:border-emerald-300 shadow-sm'
          }`}
        >
          <span className="text-xs text-[#64748B] font-semibold uppercase">Valid</span>
          <p className="text-2xl font-mono font-bold text-emerald-600 mt-1">{validCount}</p>
        </button>

        <button
          onClick={() => setStatusFilter('EXPIRING_SOON')}
          className={`p-4 rounded-xl border text-left transition-all ${
            statusFilter === 'EXPIRING_SOON'
              ? 'bg-amber-50 border-amber-500 shadow-sm'
              : 'bg-white border-[#DCE3EC] hover:border-amber-300 shadow-sm'
          }`}
        >
          <span className="text-xs text-[#64748B] font-semibold uppercase">Expiring Soon (30d)</span>
          <p className="text-2xl font-mono font-bold text-amber-600 mt-1">{expiringCount}</p>
        </button>

        <button
          onClick={() => setStatusFilter('EXPIRED')}
          className={`p-4 rounded-xl border text-left transition-all ${
            statusFilter === 'EXPIRED'
              ? 'bg-rose-50 border-rose-500 shadow-sm'
              : 'bg-white border-[#DCE3EC] hover:border-rose-300 shadow-sm'
          }`}
        >
          <span className="text-xs text-[#64748B] font-semibold uppercase">Expired (Violation)</span>
          <p className="text-2xl font-mono font-bold text-rose-600 mt-1">{expiredCount}</p>
        </button>
      </div>

      {/* Filter & Search Toolbar */}
      <div className="p-4 rounded-2xl border border-[#DCE3EC] bg-white shadow-sm flex flex-col md:flex-row items-center justify-between gap-4">
        {/* Search Input */}
        <div className="relative w-full md:w-96">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-[#64748B]" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search by plate, owner or document #..."
            className="w-full pl-10 pr-4 py-2 rounded-xl bg-white border border-[#DCE3EC] text-xs font-medium text-[#172B4D] placeholder-slate-400 focus:outline-none focus:border-[#1769D2] focus:ring-2 focus:ring-[#1769D2]/15 transition-colors"
          />
        </div>

        {/* Type Filter Select */}
        <div className="flex items-center gap-2 w-full md:w-auto">
          <Filter className="h-4 w-4 text-[#64748B] shrink-0" />
          <span className="text-xs text-[#64748B] font-medium shrink-0">Type:</span>
          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            className="px-3 py-2 rounded-xl bg-white border border-[#DCE3EC] text-xs font-semibold text-[#172B4D] focus:outline-none focus:border-[#1769D2] transition-colors"
          >
            <option value="ALL">All Document Types</option>
            <option value="RC">RC (Registration Certificate)</option>
            <option value="INSURANCE">Insurance Policy</option>
            <option value="PUC">PUC (Emissions)</option>
            <option value="ROAD_TAX">Road Tax</option>
          </select>
        </div>
      </div>

      {/* Main Table */}
      <div className="rounded-2xl border border-[#DCE3EC] bg-white shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#EFF5FF] text-[#172B4D] font-bold uppercase text-[11px] border-b border-[#DCE3EC]">
              <tr>
                <th className="py-3.5 px-4">Vehicle Plate</th>
                <th className="py-3.5 px-4">Owner Particulars</th>
                <th className="py-3.5 px-4">Document Type</th>
                <th className="py-3.5 px-4">Document Number</th>
                <th className="py-3.5 px-4">Expiry Date</th>
                <th className="py-3.5 px-4">Status</th>
                <th className="py-3.5 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#DCE3EC]">
              {loading ? (
                <tr>
                  <td colSpan="7" className="py-12 text-center text-[#64748B]">
                    <RefreshCw className="h-5 w-5 animate-spin mx-auto text-[#1769D2] mb-2" />
                    Loading document registry records...
                  </td>
                </tr>
              ) : filteredDocs.length === 0 ? (
                <tr>
                  <td colSpan="7" className="py-12 text-center text-[#64748B]">
                    No documents match the specified criteria.
                  </td>
                </tr>
              ) : (
                filteredDocs.map((doc, idx) => {
                  const isVal = doc.status === 'VALID';
                  const isExp = doc.status === 'EXPIRED';
                  const isSoon = doc.status === 'EXPIRING_SOON';

                  const badgeColor = isVal
                    ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                    : isExp
                    ? 'bg-rose-50 text-rose-700 border-rose-200'
                    : 'bg-amber-50 text-amber-700 border-amber-200';

                  return (
                    <tr key={idx} className="hover:bg-[#F8FAFC] transition-colors">
                      <td className="py-3 px-4">
                        <LicensePlateBadge
                          plate={doc.registration_number}
                          vehicleType={doc.vehicle_type}
                          size="sm"
                        />
                      </td>
                      <td className="py-3 px-4">
                        <p className="font-semibold text-[#172B4D]">{doc.owner_name}</p>
                        <p className="text-[11px] text-[#64748B]">{doc.vehicle_type} &bull; {doc.vehicle_model}</p>
                      </td>
                      <td className="py-3 px-4 font-bold text-[#172B4D]">
                        {doc.document_type}
                      </td>
                      <td className="py-3 px-4 font-mono text-[#64748B] text-[11px]">
                        {doc.document_number}
                      </td>
                      <td className="py-3 px-4 font-mono text-[#172B4D]">
                        {doc.expiry_date}
                      </td>
                      <td className="py-3 px-4">
                        <span className={`px-2.5 py-0.5 rounded-full font-bold uppercase text-[10px] border ${badgeColor}`}>
                          {doc.status}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-right">
                        <button
                          onClick={() => onVerifyPlate?.(doc.registration_number)}
                          className="px-3 py-1.5 rounded-lg bg-[#EFF5FF] hover:bg-[#DDEBFF] text-[#1769D2] text-xs font-semibold transition-colors border border-[#DCE3EC]"
                        >
                          Verify Vehicle
                        </button>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
