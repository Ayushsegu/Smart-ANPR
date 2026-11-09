/**
 * components/ChallanManagement.jsx - Electronic Traffic Citation Management
 * =========================================================================
 * Smart ANPR Vehicle Verification System
 * Design: White and Blue Professional Enterprise SaaS UI
 *
 * Implements:
 * - Tabular listing of all traffic challans with real-time API sync
 * - Search by citation number or vehicle registration plate
 * - Filter by payment status (ALL, PENDING, PAID, FAILED)
 * - Direct PDF receipt download action
 * - Quick QR code viewer
 * - Inline demonstration payment settlement simulation
 */

import React, { useState, useEffect } from 'react';
import {
  Receipt,
  Search,
  Filter,
  FileDown,
  QrCode,
  CreditCard,
  CheckCircle2,
  XCircle,
  Clock,
  Eye,
  Plus,
  RefreshCw,
  ExternalLink,
} from 'lucide-react';
import LicensePlateBadge from './LicensePlateBadge';
import { getChallans, payChallan, getPdfUrl, getQrUrl } from '../services/api';

export default function ChallanManagement({ onSelectChallan, onNewChallan, showToast }) {
  const [challans, setChallans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL'); // 'ALL' | 'PENDING' | 'PAID' | 'FAILED'
  const [actionInProgress, setActionInProgress] = useState(null);

  const fetchChallansList = async () => {
    setLoading(true);
    try {
      const data = await getChallans();
      setChallans(data.challans || []);
    } catch (err) {
      showToast?.({
        type: 'error',
        title: 'Failed to load challans',
        message: err.message,
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchChallansList();
  }, []);

  // Quick inline payment simulation
  const handleInlinePay = async (e, challanNumber, action = 'PAY') => {
    e.stopPropagation();
    setActionInProgress(challanNumber);
    try {
      const updated = await payChallan(challanNumber, action);
      setChallans((prev) =>
        prev.map((c) => (c.challan_number === challanNumber ? { ...c, ...updated } : c))
      );
      showToast?.({
        type: action === 'PAY' ? 'success' : 'error',
        title: action === 'PAY' ? 'Citation Marked as Paid' : 'Payment Marked as Failed',
        message: updated.demonstration_notice || `Updated status of ${challanNumber}.`,
      });
    } catch (err) {
      showToast?.({
        type: 'error',
        title: 'Payment Simulation Error',
        message: err.message,
      });
    } finally {
      setActionInProgress(null);
    }
  };

  // Filter challans
  const filteredChallans = challans.filter((c) => {
    const matchesSearch =
      !searchQuery ||
      c.challan_number?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.registration_number?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.owner_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.violation_type?.toLowerCase().includes(searchQuery.toLowerCase());

    const matchesStatus =
      statusFilter === 'ALL' || c.payment_status?.toUpperCase() === statusFilter;

    return matchesSearch && matchesStatus;
  });

  const totalCount = challans.length;
  const pendingCount = challans.filter((c) => c.payment_status === 'PENDING').length;
  const paidCount = challans.filter((c) => c.payment_status === 'PAID').length;
  const failedCount = challans.filter((c) => c.payment_status === 'FAILED').length;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#DCE3EC] pb-4">
        <div>
          <h2 className="text-xl md:text-2xl font-bold text-[#172B4D] flex items-center gap-2.5">
            <Receipt className="h-6 w-6 text-[#1769D2]" />
            <span>Digital Challan Citation Records</span>
          </h2>
          <p className="text-xs text-[#64748B] mt-1">
            Central repository of issued electronic citations, official ReportLab PDFs & verification barcodes
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={fetchChallansList}
            className="px-4 py-2 rounded-xl bg-white hover:bg-[#F8FAFC] text-[#172B4D] text-xs font-bold border border-[#DCE3EC] shadow-sm flex items-center gap-2 transition-colors"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${loading ? 'animate-spin text-[#1769D2]' : ''}`} />
            <span>Refresh</span>
          </button>

          {onNewChallan && (
            <button
              onClick={onNewChallan}
              className="px-4 py-2 rounded-xl bg-[#1769D2] hover:bg-[#1258B3] text-white text-xs font-bold transition-all shadow-sm flex items-center gap-2"
            >
              <Plus className="h-4 w-4" />
              <span>Issue New Citation</span>
            </button>
          )}
        </div>
      </div>

      {/* KPI Counters Bar */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <button
          onClick={() => setStatusFilter('ALL')}
          className={`p-4 rounded-xl border text-left transition-all ${
            statusFilter === 'ALL'
              ? 'bg-[#EFF5FF] border-[#1769D2] shadow-sm'
              : 'bg-white border-[#DCE3EC] hover:border-[#1769D2]/40 shadow-sm'
          }`}
        >
          <span className="text-xs text-[#64748B] font-semibold uppercase">Total Citations</span>
          <p className="text-2xl font-mono font-bold text-[#172B4D] mt-1">{totalCount}</p>
        </button>

        <button
          onClick={() => setStatusFilter('PENDING')}
          className={`p-4 rounded-xl border text-left transition-all ${
            statusFilter === 'PENDING'
              ? 'bg-amber-50 border-amber-500 shadow-sm'
              : 'bg-white border-[#DCE3EC] hover:border-amber-300 shadow-sm'
          }`}
        >
          <span className="text-xs text-[#64748B] font-semibold uppercase">Pending Fines</span>
          <p className="text-2xl font-mono font-bold text-amber-600 mt-1">{pendingCount}</p>
        </button>

        <button
          onClick={() => setStatusFilter('PAID')}
          className={`p-4 rounded-xl border text-left transition-all ${
            statusFilter === 'PAID'
              ? 'bg-emerald-50 border-emerald-500 shadow-sm'
              : 'bg-white border-[#DCE3EC] hover:border-emerald-300 shadow-sm'
          }`}
        >
          <span className="text-xs text-[#64748B] font-semibold uppercase">Settled / Paid</span>
          <p className="text-2xl font-mono font-bold text-emerald-600 mt-1">{paidCount}</p>
        </button>

        <button
          onClick={() => setStatusFilter('FAILED')}
          className={`p-4 rounded-xl border text-left transition-all ${
            statusFilter === 'FAILED'
              ? 'bg-rose-50 border-rose-500 shadow-sm'
              : 'bg-white border-[#DCE3EC] hover:border-rose-300 shadow-sm'
          }`}
        >
          <span className="text-xs text-[#64748B] font-semibold uppercase">Payment Failed</span>
          <p className="text-2xl font-mono font-bold text-rose-600 mt-1">{failedCount}</p>
        </button>
      </div>

      {/* Search Bar */}
      <div className="p-4 rounded-2xl border border-[#DCE3EC] bg-white shadow-sm flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="relative w-full md:w-96">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-[#64748B]" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search by citation ID, plate, or violation..."
            className="w-full pl-10 pr-4 py-2 rounded-xl bg-white border border-[#DCE3EC] text-xs font-medium text-[#172B4D] placeholder-slate-400 focus:outline-none focus:border-[#1769D2] focus:ring-2 focus:ring-[#1769D2]/15 transition-colors"
          />
        </div>

        <div className="flex items-center gap-2 w-full md:w-auto">
          <Filter className="h-4 w-4 text-[#64748B] shrink-0" />
          <span className="text-xs text-[#64748B] font-medium shrink-0">Filter Status:</span>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-2 rounded-xl bg-white border border-[#DCE3EC] text-xs font-semibold text-[#172B4D] focus:outline-none focus:border-[#1769D2] transition-colors"
          >
            <option value="ALL">All Statuses</option>
            <option value="PENDING">Pending Payment</option>
            <option value="PAID">Paid / Settled</option>
            <option value="FAILED">Payment Failed</option>
          </select>
        </div>
      </div>

      {/* Main Challan Table */}
      <div className="rounded-2xl border border-[#DCE3EC] bg-white shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#EFF5FF] text-[#172B4D] font-bold uppercase text-[11px] border-b border-[#DCE3EC]">
              <tr>
                <th className="py-3.5 px-4">Citation ID</th>
                <th className="py-3.5 px-4">Target Vehicle</th>
                <th className="py-3.5 px-4">Owner Name</th>
                <th className="py-3.5 px-4">Violation Particulars</th>
                <th className="py-3.5 px-4 text-right">Fine Amount</th>
                <th className="py-3.5 px-4">Issue Date</th>
                <th className="py-3.5 px-4">Payment Status</th>
                <th className="py-3.5 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#DCE3EC]">
              {loading ? (
                <tr>
                  <td colSpan="8" className="py-12 text-center text-[#64748B]">
                    <RefreshCw className="h-5 w-5 animate-spin mx-auto text-[#1769D2] mb-2" />
                    Loading citation records...
                  </td>
                </tr>
              ) : filteredChallans.length === 0 ? (
                <tr>
                  <td colSpan="8" className="py-12 text-center text-[#64748B]">
                    No electronic citations found matching current criteria.
                  </td>
                </tr>
              ) : (
                filteredChallans.map((c) => {
                  const isPaid = c.payment_status === 'PAID';
                  const isFailed = c.payment_status === 'FAILED';
                  const isPending = c.payment_status === 'PENDING';

                  const badgeColor = isPaid
                    ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                    : isFailed
                    ? 'bg-rose-50 text-rose-700 border-rose-200'
                    : 'bg-amber-50 text-amber-700 border-amber-200';

                  const pdfUrl = getPdfUrl(c.challan_number);

                  return (
                    <tr
                      key={c.id || c.challan_number}
                      className="hover:bg-[#F8FAFC] transition-colors cursor-pointer"
                      onClick={() => onSelectChallan(c)}
                    >
                      <td className="py-3 px-4 font-mono font-bold text-[#1769D2]">
                        {c.challan_number}
                      </td>
                      <td className="py-3 px-4">
                        <LicensePlateBadge plate={c.registration_number} size="sm" />
                      </td>
                      <td className="py-3 px-4 font-semibold text-[#172B4D]">
                        {c.owner_name}
                      </td>
                      <td className="py-3 px-4 text-[#64748B] max-w-xs truncate" title={c.violation_type}>
                        {c.violation_type}
                      </td>
                      <td className="py-3 px-4 text-right font-mono font-bold text-rose-600 text-sm">
                        ₹{Number(c.fine_amount).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                      </td>
                      <td className="py-3 px-4 font-mono text-[#64748B] text-[11px]">
                        {c.challan_date}
                      </td>
                      <td className="py-3 px-4">
                        <span className={`px-2.5 py-0.5 rounded-full font-bold uppercase text-[10px] border ${badgeColor}`}>
                          {c.payment_status}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-right" onClick={(e) => e.stopPropagation()}>
                        <div className="flex items-center justify-end gap-2">
                          <button
                            onClick={() => onSelectChallan(c)}
                            className="p-1.5 rounded-lg bg-[#EFF5FF] hover:bg-[#DDEBFF] text-[#1769D2] border border-[#DCE3EC] transition-colors"
                            title="View Details & QR"
                          >
                            <Eye className="h-4 w-4" />
                          </button>

                          <a
                            href={pdfUrl}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="p-1.5 rounded-lg bg-[#EFF5FF] hover:bg-[#DDEBFF] text-[#1769D2] border border-[#DCE3EC] transition-colors"
                            title="Download PDF Citation"
                          >
                            <FileDown className="h-4 w-4" />
                          </a>

                          {/* Quick Simulated Payment Button */}
                          {isPending && (
                            <button
                              onClick={(e) => handleInlinePay(e, c.challan_number, 'PAY')}
                              disabled={actionInProgress === c.challan_number}
                              className="px-2.5 py-1 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white text-[10px] font-bold transition-colors flex items-center gap-1 shadow-sm"
                              title="Simulate Payment (Set to PAID)"
                            >
                              {actionInProgress === c.challan_number ? (
                                <RefreshCw className="h-3 w-3 animate-spin" />
                              ) : (
                                <CheckCircle2 className="h-3 w-3" />
                              )}
                              <span>Pay</span>
                            </button>
                          )}
                        </div>
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
