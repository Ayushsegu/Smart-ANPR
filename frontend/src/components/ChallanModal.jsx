/**
 * components/ChallanModal.jsx - Citation Detail, QR & PDF Viewer Modal
 * ====================================================================
 * Smart ANPR Vehicle Verification System
 * Design: White and Blue Professional Enterprise SaaS UI
 * Supports Multi-Language i18n & Dark Mode
 */

import React, { useState } from 'react';
import {
  X,
  FileDown,
  QrCode,
  CreditCard,
  CheckCircle2,
  AlertTriangle,
  Clock,
  Shield,
  ExternalLink,
  Car,
  User,
  Calendar,
  AlertCircle,
  RefreshCw,
} from 'lucide-react';
import LicensePlateBadge from './LicensePlateBadge';
import { payChallan, getPdfUrl, getQrUrl } from '../services/api';
import { useTranslation } from '../context/I18nContext';

export default function ChallanModal({ challan, onClose, onChallanUpdated, showToast }) {
  const { t } = useTranslation();
  const [activeTab, setActiveTab] = useState('details'); // 'details' | 'qr'
  const [isProcessingPayment, setIsProcessingPayment] = useState(false);
  const [currentChallan, setCurrentChallan] = useState(challan);

  if (!challan) return null;

  const chNum = currentChallan.challan_number;
  const isPaid = currentChallan.payment_status === 'PAID';
  const isFailed = currentChallan.payment_status === 'FAILED';

  const handleSimulatePayment = async (action = 'PAY') => {
    setIsProcessingPayment(true);
    try {
      const updated = await payChallan(chNum, action);
      setCurrentChallan(updated);
      if (onChallanUpdated) onChallanUpdated(updated);
      showToast?.({
        type: action === 'PAY' ? 'success' : 'error',
        title: action === 'PAY' ? 'Demonstration Payment Successful' : 'Demonstration Payment Failed',
        message: updated.demonstration_notice || `Payment status updated to ${action}.`,
      });
    } catch (err) {
      showToast?.({
        type: 'error',
        title: 'Payment Simulation Error',
        message: err.message,
      });
    } finally {
      setIsProcessingPayment(false);
    }
  };

  const pdfUrl = getPdfUrl(chNum);
  const qrUrl = getQrUrl(chNum);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="relative w-full max-w-3xl max-h-[90vh] overflow-hidden rounded-2xl border border-[#DCE3EC] dark:border-slate-800 bg-white dark:bg-[#1E293B] shadow-2xl flex flex-col text-[#172B4D] dark:text-slate-100 transition-colors">
        {/* Modal Header */}
        <div className="p-5 border-b border-[#DCE3EC] dark:border-slate-800 flex items-center justify-between bg-white dark:bg-[#1E293B]">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-xl bg-[#EFF5FF] dark:bg-blue-950/60 border border-[#DCE3EC] dark:border-slate-700 flex items-center justify-center text-[#1769D2]">
              <Shield className="h-5 w-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="font-bold text-base text-[#172B4D] dark:text-slate-100">
                  Traffic Citation Particulars
                </h3>
                <span
                  className={`text-[10px] px-2.5 py-0.5 rounded-full font-bold uppercase tracking-wider ${
                    isPaid
                      ? 'bg-emerald-50 dark:bg-emerald-950/50 text-emerald-700 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-900'
                      : isFailed
                      ? 'bg-rose-50 dark:bg-rose-950/50 text-rose-700 dark:text-rose-400 border border-rose-200 dark:border-rose-900'
                      : 'bg-amber-50 dark:bg-amber-950/50 text-amber-700 dark:text-amber-400 border border-amber-200 dark:border-amber-900'
                  }`}
                >
                  {currentChallan.payment_status}
                </span>
              </div>
              <p className="text-xs font-mono text-[#64748B] dark:text-slate-400 mt-0.5">
                Citation ID: <span className="text-[#1769D2] dark:text-blue-400 font-bold">{chNum}</span>
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <a
              href={pdfUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="px-3.5 py-1.5 rounded-lg bg-[#1769D2] hover:bg-[#1258B3] text-white text-xs font-semibold flex items-center gap-1.5 transition-colors shadow-sm"
            >
              <FileDown className="h-3.5 w-3.5" />
              <span>{t('common.download_pdf', {}, 'Download PDF')}</span>
            </a>
            <button
              onClick={onClose}
              className="h-8 w-8 rounded-lg bg-[#EFF5FF] dark:bg-slate-800 hover:bg-[#DDEBFF] dark:hover:bg-slate-700 text-[#64748B] dark:text-slate-300 hover:text-[#172B4D] dark:hover:text-white flex items-center justify-center transition-colors cursor-pointer"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        </div>

        {/* Modal Navigation Tabs */}
        <div className="flex border-b border-[#DCE3EC] dark:border-slate-800 bg-[#F8FAFC] dark:bg-slate-900/60 px-5 text-xs font-medium">
          <button
            onClick={() => setActiveTab('details')}
            className={`py-2.5 px-3 border-b-2 font-semibold transition-colors cursor-pointer ${
              activeTab === 'details'
                ? 'border-[#1769D2] text-[#1769D2] dark:text-blue-400'
                : 'border-transparent text-[#64748B] dark:text-slate-400 hover:text-[#172B4D] dark:hover:text-slate-200'
            }`}
          >
            Citation Summary
          </button>
          <button
            onClick={() => setActiveTab('qr')}
            className={`py-2.5 px-3 border-b-2 font-semibold flex items-center gap-1.5 transition-colors cursor-pointer ${
              activeTab === 'qr'
                ? 'border-[#1769D2] text-[#1769D2] dark:text-blue-400'
                : 'border-transparent text-[#64748B] dark:text-slate-400 hover:text-[#172B4D] dark:hover:text-slate-200'
            }`}
          >
            <QrCode className="h-3.5 w-3.5" />
            <span>Verification QR Barcode</span>
          </button>
        </div>

        {/* Modal Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {activeTab === 'details' ? (
            <>
              {/* Vehicle & Owner Info Card */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 p-4 rounded-xl bg-[#F8FAFC] dark:bg-slate-900/60 border border-[#DCE3EC] dark:border-slate-800">
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-[#64748B] dark:text-slate-400">Target Vehicle:</span>
                    <LicensePlateBadge
                      plate={currentChallan.vehicle?.registration_number || currentChallan.registration_number}
                      vehicleType={currentChallan.vehicle?.vehicle_type}
                      size="sm"
                    />
                  </div>
                  <div className="flex items-center gap-2 text-xs text-[#172B4D] dark:text-slate-200">
                    <Car className="h-4 w-4 text-[#1769D2]" />
                    <span>
                      {currentChallan.vehicle?.vehicle_type || 'Vehicle'} &bull;{' '}
                      {currentChallan.vehicle?.vehicle_model || 'Standard Model'}
                    </span>
                  </div>
                </div>

                <div className="space-y-2 border-t md:border-t-0 md:border-l border-[#DCE3EC] dark:border-slate-800 md:pl-4">
                  <div className="flex items-center gap-2 text-xs text-[#172B4D] dark:text-slate-200">
                    <User className="h-4 w-4 text-[#1769D2]" />
                    <span className="font-semibold">
                      {currentChallan.vehicle?.owner_name || currentChallan.owner_name || 'Registered Owner'}
                    </span>
                  </div>
                  <div className="flex items-center gap-2 text-xs text-[#64748B] dark:text-slate-400 font-mono">
                    <Calendar className="h-4 w-4 text-[#64748B]" />
                    <span>Issued: {currentChallan.challan_date}</span>
                  </div>
                </div>
              </div>

              {/* Itemized Fine Breakdown */}
              <div className="space-y-3">
                <h4 className="text-xs font-bold uppercase tracking-wider text-[#64748B] dark:text-slate-400">
                  Violation Schedule & Penalties
                </h4>

                <div className="rounded-xl border border-[#DCE3EC] dark:border-slate-800 overflow-hidden bg-white dark:bg-[#1E293B]">
                  <table className="w-full text-left text-xs">
                    <thead className="bg-[#EFF5FF] dark:bg-blue-950/60 text-[#172B4D] dark:text-slate-200 uppercase font-bold text-[11px] border-b border-[#DCE3EC] dark:border-slate-800">
                      <tr>
                        <th className="py-2.5 px-4">Violation Particulars</th>
                        <th className="py-2.5 px-4">Statutory Clause</th>
                        <th className="py-2.5 px-4">Severity</th>
                        <th className="py-2.5 px-4 text-right">Fine Amount</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-[#DCE3EC] dark:divide-slate-800">
                      {currentChallan.fine_breakdown?.items ? (
                        currentChallan.fine_breakdown.items.map((item, idx) => (
                          <tr key={idx} className="hover:bg-[#F8FAFC] dark:hover:bg-slate-800/50 transition-colors">
                            <td className="py-2.5 px-4 font-semibold text-[#172B4D] dark:text-slate-200">
                              {item.title}
                            </td>
                            <td className="py-2.5 px-4 text-[#64748B] dark:text-slate-400 font-mono text-[11px]">
                              {item.statute}
                            </td>
                            <td className="py-2.5 px-4">
                              <span className="px-2 py-0.5 rounded font-bold text-[10px] bg-rose-50 dark:bg-rose-950/50 text-rose-700 dark:text-rose-400 border border-rose-200 dark:border-rose-900">
                                {item.severity}
                              </span>
                            </td>
                            <td className="py-2.5 px-4 text-right font-mono font-bold text-[#172B4D] dark:text-slate-200">
                              ₹{Number(item.fine_amount).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                            </td>
                          </tr>
                        ))
                      ) : (
                        <tr>
                          <td className="py-3 px-4 font-semibold text-[#172B4D] dark:text-slate-200">
                            {currentChallan.violation_type}
                          </td>
                          <td className="py-3 px-4 text-[#64748B] dark:text-slate-400 font-mono text-[11px]">
                            Motor Vehicles Act 1988
                          </td>
                          <td className="py-3 px-4">
                            <span className="px-2 py-0.5 rounded font-bold text-[10px] bg-rose-50 dark:bg-rose-950/50 text-rose-700 dark:text-rose-400 border border-rose-200 dark:border-rose-900">
                              HIGH
                            </span>
                          </td>
                          <td className="py-3 px-4 text-right font-mono font-bold text-rose-600">
                            ₹{Number(currentChallan.fine_amount).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                          </td>
                        </tr>
                      )}
                    </tbody>
                    <tfoot className="bg-[#EFF5FF] dark:bg-blue-950/40 font-bold border-t border-[#DCE3EC] dark:border-slate-800">
                      <tr>
                        <td colSpan="3" className="py-3 px-4 text-right uppercase text-[#172B4D] dark:text-slate-200 text-[11px]">
                          Total Payable Fine:
                        </td>
                        <td className="py-3 px-4 text-right text-base text-rose-600 dark:text-rose-400 font-mono">
                          ₹{Number(currentChallan.fine_amount).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                        </td>
                      </tr>
                    </tfoot>
                  </table>
                </div>
              </div>

              {/* Payment Status Action Card */}
              <div className="p-4 rounded-xl border border-[#DCE3EC] dark:border-slate-800 bg-[#EFF5FF] dark:bg-blue-950/30 space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <CreditCard className="h-4 w-4 text-[#1769D2]" />
                    <span className="text-xs font-bold text-[#172B4D] dark:text-slate-200">
                      Demonstration Fine Settlement Gateway
                    </span>
                  </div>
                  <span className="text-[10px] font-mono font-bold text-[#1769D2] dark:text-blue-400">
                    UPI / BharatQR Protocol
                  </span>
                </div>

                <div className="flex flex-wrap items-center gap-3 pt-1">
                  {!isPaid && (
                    <button
                      onClick={() => handleSimulatePayment('PAY')}
                      disabled={isProcessingPayment}
                      className="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold flex items-center gap-1.5 shadow-sm transition-all cursor-pointer disabled:opacity-50"
                    >
                      <CheckCircle2 className="h-4 w-4" />
                      <span>Simulate Successful UPI Payment</span>
                    </button>
                  )}

                  {!isPaid && !isFailed && (
                    <button
                      onClick={() => handleSimulatePayment('FAIL')}
                      disabled={isProcessingPayment}
                      className="px-3.5 py-2 rounded-lg bg-white dark:bg-[#1E293B] hover:bg-rose-50 dark:hover:bg-rose-950/40 text-rose-600 border border-rose-200 dark:border-rose-900 text-xs font-bold flex items-center gap-1.5 transition-all cursor-pointer disabled:opacity-50"
                    >
                      <AlertTriangle className="h-4 w-4" />
                      <span>Simulate Transaction Failure</span>
                    </button>
                  )}

                  {isPaid && (
                    <span className="text-xs font-bold text-emerald-700 dark:text-emerald-400 flex items-center gap-1.5">
                      <CheckCircle2 className="h-4 w-4" />
                      Paid & Settled via UPI Gateway
                    </span>
                  )}
                </div>
              </div>
            </>
          ) : (
            /* QR Code Tab */
            <div className="flex flex-col items-center justify-center p-6 space-y-4 text-center">
              <div className="p-4 rounded-2xl bg-white border border-[#DCE3EC] shadow-md">
                <img
                  src={qrUrl}
                  alt={`QR Code for Citation ${chNum}`}
                  className="w-48 h-48 sm:w-56 sm:h-56 object-contain"
                />
              </div>
              <div className="space-y-1">
                <p className="text-xs font-bold text-[#172B4D] dark:text-slate-100">
                  Scan to Verify or Pay Citation
                </p>
                <p className="text-[11px] font-mono text-[#64748B] dark:text-slate-400">
                  UPI URI / Traffic Police Parivahan Node
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
