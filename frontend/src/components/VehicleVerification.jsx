/**
 * components/VehicleVerification.jsx - Vehicle Compliance & Document Verification Page
 * ====================================================================================
 * Smart ANPR Vehicle Verification System
 * Design: STYLE 4 – PREMIUM ENTERPRISE (WHITE + BLUE + GREY)
 *
 * Implements:
 * 1. Prominent Notice: "DEMO RECORD – NOT VERIFIED AGAINST GOVERNMENT DATABASES"
 * 2. Eight Core Sections:
 *    - Vehicle Overview
 *    - Registration Details
 *    - Owner Information
 *    - Driving Licence & Driver Information
 *    - 4 Mandatory Documents (RC, Insurance, PUC, Road Tax) with Green/Yellow/Red/Grey badges
 *    - Previous Demo Challans
 *    - Verification Summary & Statutory Fine Breakdown
 * 3. Pre-registered 50 demo vehicles support + presets.
 * 4. Dedicated "Vehicle Not Found in Demo Database" view when plate is unregistered.
 */

import React, { useState, useEffect } from 'react';
import {
  Search,
  Car,
  FileCheck2,
  AlertTriangle,
  CheckCircle2,
  Clock,
  User,
  Calendar,
  Receipt,
  RefreshCw,
  ShieldCheck,
  ShieldAlert,
  Info,
  MapPin,
  FileText,
  BadgeAlert,
  CreditCard,
  UserCheck,
  Fuel,
  Hash,
  AlertCircle,
  ExternalLink,
  Layers,
} from 'lucide-react';
import LicensePlateBadge from './LicensePlateBadge';
import StatusBadge from './common/StatusBadge';
import Breadcrumbs from './common/Breadcrumbs';
import { verifyVehicle, generateChallan } from '../services/api';

export default function VehicleVerification({ initialPlate = '', onSelectChallan, showToast }) {
  const [searchPlate, setSearchPlate] = useState(initialPlate || 'DL01DM0001');
  const [loading, setLoading] = useState(false);
  const [verificationResult, setVerificationResult] = useState(null);
  const [notFoundPlate, setNotFoundPlate] = useState(null);
  const [isGeneratingChallan, setIsGeneratingChallan] = useState(false);

  // Quick preset demo plates for instant presentation
  const demoPresets = [
    { plate: 'DL01DM0001', label: 'DEMO-01 (Dzire - Valid)' },
    { plate: 'DL01DM0002', label: 'DEMO-02 (Creta - Expired PUC)' },
    { plate: 'DL01DM0003', label: 'DEMO-03 (Nexon EV - Expiring Ins)' },
    { plate: 'DL01DM0004', label: 'DEMO-04 (Classic 350 - Valid)' },
    { plate: 'DL01DM0005', label: 'DEMO-05 (Activa - Expired Ins)' },
    { plate: 'DL01DM0006', label: 'DEMO-06 (Ace Gold - Expired Tax)' },
    { plate: 'DL01DM0010', label: 'DEMO-10 (Innova - Missing PUC)' },
    { plate: 'DL01DM0012', label: 'DEMO-12 (Dost - Expired RC)' },
  ];

  const handleSearch = async (plateToSearch) => {
    const target = (plateToSearch || searchPlate).trim().toUpperCase();
    if (!target) return;

    setLoading(true);
    setVerificationResult(null);
    setNotFoundPlate(null);

    try {
      const data = await verifyVehicle(target);
      setVerificationResult(data);
    } catch (err) {
      setNotFoundPlate(target);
      showToast?.({
        type: 'error',
        title: 'Vehicle Lookup Notice',
        message: `Plate ${target} was not found in the local demo database.`,
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (initialPlate) {
      setSearchPlate(initialPlate);
      handleSearch(initialPlate);
    } else {
      handleSearch('DL01DM0001');
    }
  }, [initialPlate]);

  const handleGenerateChallan = async () => {
    if (!verificationResult) return;
    const plate = verificationResult.vehicle?.registration_number;

    setIsGeneratingChallan(true);
    try {
      const result = await generateChallan({
        registration_number: plate,
        description: 'Electronic patrol verification identified non-compliant statutory documents.',
      });

      showToast?.({
        type: 'success',
        title: 'Challan Issued Successfully',
        message: `Citation #${result.challan_number} generated for ${plate}.`,
      });

      if (onSelectChallan) {
        onSelectChallan(result);
      }
    } catch (err) {
      showToast?.({
        type: 'error',
        title: 'Challan Generation Failed',
        message: err.message,
      });
    } finally {
      setIsGeneratingChallan(false);
    }
  };

  const v = verificationResult?.vehicle;
  const summary = verificationResult?.summary;
  const documents = verificationResult?.documents || {};
  const violations = verificationResult?.violations || [];
  const fines = verificationResult?.fines;
  const previousChallans = verificationResult?.challans || [];

  const isCompliant = summary?.overall_status === 'COMPLIANT';
  const isAttention = summary?.overall_status === 'ATTENTION_REQUIRED';
  const isNonCompliant = summary?.overall_status === 'NON_COMPLIANT';

  return (
    <div className="space-y-6">
      {/* Breadcrumbs */}
      <Breadcrumbs items={[{ label: 'Enforcement' }, { label: 'Vehicle Verification & Registry Audit' }]} />

      {/* Prominent Demo Notice Banner */}
      <div className="p-4 rounded-2xl bg-[#EFF5FF] border border-[#DCE3EC] flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
        <div className="flex items-start gap-3">
          <div className="w-8 h-8 rounded-xl bg-[#1769D2] text-white flex items-center justify-center shrink-0 font-bold">
            <ShieldCheck className="h-4 w-4" />
          </div>
          <div>
            <h4 className="font-extrabold text-[#172B4D] tracking-wide text-xs sm:text-sm flex items-center gap-2">
              <span>DEMO RECORD – NOT VERIFIED AGAINST GOVERNMENT DATABASES</span>
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-blue-100 text-[#1769D2] font-bold">
                LOCAL DATABASE RECORD
              </span>
            </h4>
            <p className="text-[#64748B] mt-0.5 leading-relaxed">
              This vehicle verification interface queries the local SQLite pre-registered demo dataset (50 vehicles).
              Document validity is dynamically computed based on today's reference date.
            </p>
          </div>
        </div>
      </div>

      {/* Search Header Bar */}
      <div className="p-4 rounded-2xl border border-[#DCE3EC] bg-white shadow-sm space-y-3">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSearch();
          }}
          className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3"
        >
          <div className="relative flex-1">
            <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-[#64748B]" />
            <input
              type="text"
              value={searchPlate}
              onChange={(e) => setSearchPlate(e.target.value.toUpperCase())}
              placeholder="Enter Registration Identifier (e.g. DL01DM0001, MH12DM0023, HR26DM0013)..."
              className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-white border border-[#DCE3EC] text-xs font-mono font-bold text-[#172B4D] placeholder-slate-400 focus:outline-none focus:border-[#1769D2] focus:ring-2 focus:ring-[#1769D2]/15 transition-colors"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="px-6 py-2.5 rounded-xl bg-[#1769D2] hover:bg-[#1258B3] disabled:opacity-50 text-white font-bold text-xs flex items-center justify-center gap-2 transition-all shadow-sm shrink-0"
          >
            {loading ? (
              <RefreshCw className="h-4 w-4 animate-spin" />
            ) : (
              <Search className="h-4 w-4" />
            )}
            <span>Inspect Vehicle</span>
          </button>
        </form>

        {/* Quick Demo Preset Pills */}
        <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-[#DCE3EC] text-[11px]">
          <span className="text-[#64748B] font-bold flex items-center gap-1">
            <Layers className="h-3.5 w-3.5 text-[#1769D2]" />
            <span>Demo Fleet Presets:</span>
          </span>
          {demoPresets.map((dp, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => {
                setSearchPlate(dp.plate);
                handleSearch(dp.plate);
              }}
              className="px-2.5 py-1 rounded-lg bg-[#F5F7FA] hover:bg-[#EFF5FF] hover:text-[#1769D2] hover:border-[#1769D2] border border-[#DCE3EC] text-[#172B4D] font-mono text-[11px] font-medium transition-colors"
            >
              {dp.label}
            </button>
          ))}
        </div>
      </div>

      {/* Case 1: Vehicle Not Found View */}
      {notFoundPlate && !loading && (
        <div className="p-8 rounded-2xl border border-rose-200 bg-rose-50/50 shadow-sm text-center space-y-4 animate-in fade-in duration-150">
          <div className="w-14 h-14 rounded-2xl bg-rose-100 text-[#DC4545] flex items-center justify-center mx-auto">
            <AlertCircle className="h-8 w-8" />
          </div>
          <div className="max-w-md mx-auto space-y-1">
            <h3 className="text-base font-extrabold text-[#172B4D]">
              Vehicle Not Found in Demo Database
            </h3>
            <p className="text-xs text-[#64748B] leading-relaxed">
              No matching record was found for license plate <strong className="font-mono text-[#DC4545]">{notFoundPlate}</strong> in the local database.
              Only the 50 pre-registered demo vehicles (from <span className="font-mono font-bold">DL01DM0001</span> to <span className="font-mono font-bold">UP32DM0050</span>) are stored.
            </p>
          </div>

          <div className="flex flex-wrap items-center justify-center gap-3 pt-2">
            <button
              onClick={() => {
                setSearchPlate('DL01DM0001');
                handleSearch('DL01DM0001');
              }}
              className="px-4 py-2 rounded-xl bg-[#1769D2] text-white text-xs font-bold shadow-sm hover:bg-[#1258B3] transition-colors"
            >
              Test with DEMO-01 (DL01DM0001)
            </button>
            <button
              onClick={() => {
                setSearchPlate('DL01DM0002');
                handleSearch('DL01DM0002');
              }}
              className="px-4 py-2 rounded-xl bg-white text-[#172B4D] border border-[#DCE3EC] text-xs font-bold shadow-sm hover:bg-[#F5F7FA] transition-colors"
            >
              Test with DEMO-02 (DL01DM0002)
            </button>
          </div>
        </div>
      )}

      {/* Case 2: Vehicle Loaded Successfully */}
      {verificationResult && v && !loading && (
        <div className="space-y-6 animate-in fade-in duration-200">
          {/* SECTION 1: Vehicle Overview Card */}
          <div className="p-6 rounded-2xl border border-[#DCE3EC] bg-white shadow-sm space-y-4">
            <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 border-b border-[#DCE3EC] pb-4">
              <div className="flex items-center gap-3.5">
                <LicensePlateBadge plate={v.registration_number} size="large" />
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="text-lg font-extrabold text-[#172B4D]">
                      {v.vehicle_model}
                    </h3>
                    <span className="text-[10px] px-2 py-0.5 rounded-full font-mono font-bold bg-[#EFF5FF] text-[#1769D2] border border-[#DCE3EC]">
                      {v.demo_id || 'DEMO RECORD'}
                    </span>
                  </div>
                  <p className="text-xs text-[#64748B] mt-0.5 flex items-center gap-2">
                    <span>{v.manufacturer}</span>
                    <span>&bull;</span>
                    <span>{v.vehicle_type || v.vehicle_class}</span>
                    <span>&bull;</span>
                    <span>{v.fuel_type}</span>
                    <span>&bull;</span>
                    <span>Mfg {v.manufacturing_year}</span>
                  </p>
                </div>
              </div>

              {/* Status & Actions */}
              <div className="flex items-center gap-3">
                <StatusBadge status={summary?.overall_status} />

                {summary?.has_violations && (
                  <button
                    type="button"
                    onClick={handleGenerateChallan}
                    disabled={isGeneratingChallan}
                    className="px-4 py-2 rounded-xl bg-[#DC4545] hover:bg-rose-700 disabled:opacity-50 text-white font-bold text-xs flex items-center gap-2 transition-all shadow-sm"
                  >
                    {isGeneratingChallan ? (
                      <RefreshCw className="h-3.5 w-3.5 animate-spin" />
                    ) : (
                      <Receipt className="h-3.5 w-3.5" />
                    )}
                    <span>Issue Digital Challan</span>
                  </button>
                )}
              </div>
            </div>

            {/* Quick Metrics Strip */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
              <div className="p-3 rounded-xl bg-[#F5F7FA] border border-[#DCE3EC]">
                <span className="text-[#64748B] text-[11px] font-bold uppercase">Valid Certificates</span>
                <p className="text-lg font-extrabold text-[#16A36A] mt-0.5">{summary?.valid_count} of 4</p>
              </div>
              <div className="p-3 rounded-xl bg-[#F5F7FA] border border-[#DCE3EC]">
                <span className="text-[#64748B] text-[11px] font-bold uppercase">Expiring Soon</span>
                <p className="text-lg font-extrabold text-[#E5A000] mt-0.5">{summary?.expiring_count}</p>
              </div>
              <div className="p-3 rounded-xl bg-[#F5F7FA] border border-[#DCE3EC]">
                <span className="text-[#64748B] text-[11px] font-bold uppercase">Expired Documents</span>
                <p className="text-lg font-extrabold text-[#DC4545] mt-0.5">{summary?.expired_count}</p>
              </div>
              <div className="p-3 rounded-xl bg-[#F5F7FA] border border-[#DCE3EC]">
                <span className="text-[#64748B] text-[11px] font-bold uppercase">Missing Documents</span>
                <p className="text-lg font-extrabold text-slate-500 mt-0.5">{summary?.missing_count}</p>
              </div>
            </div>
          </div>

          {/* 2-Column Grid: Registration & Owner vs Driver */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* SECTION 2 & 3: Registration & Owner Information */}
            <div className="p-6 rounded-2xl border border-[#DCE3EC] bg-white shadow-sm space-y-4">
              <div className="flex items-center gap-2.5 border-b border-[#DCE3EC] pb-3">
                <FileText className="h-5 w-5 text-[#1769D2]" />
                <div>
                  <h3 className="font-bold text-sm text-[#172B4D]">Registration & Fictional Owner Particulars</h3>
                  <p className="text-[11px] text-[#64748B]">Parivahan SQLite Local Registry</p>
                </div>
              </div>

              <div className="space-y-2.5 text-xs">
                <div className="flex justify-between p-2.5 rounded-xl bg-[#F5F7FA] border border-[#DCE3EC]">
                  <span className="text-[#64748B]">Registration Date:</span>
                  <span className="font-semibold text-[#172B4D]">{v.registration_date}</span>
                </div>
                <div className="flex justify-between p-2.5 rounded-xl bg-[#F5F7FA] border border-[#DCE3EC]">
                  <span className="text-[#64748B]">State & RTO Node:</span>
                  <span className="font-semibold text-[#172B4D] flex items-center gap-1">
                    <MapPin className="h-3 w-3 text-[#1769D2]" />
                    {v.state} &bull; {v.rto_code}
                  </span>
                </div>
                <div className="flex justify-between p-2.5 rounded-xl bg-[#F5F7FA] border border-[#DCE3EC]">
                  <span className="text-[#64748B]">Registration Status:</span>
                  <span className="font-bold text-[#16A36A]">{v.registration_status || 'ACTIVE'}</span>
                </div>
                <div className="flex justify-between p-2.5 rounded-xl bg-[#F5F7FA] border border-[#DCE3EC]">
                  <span className="text-[#64748B]">Fictional Owner Name:</span>
                  <span className="font-bold text-[#172B4D]">{v.owner_name}</span>
                </div>
                <div className="flex justify-between p-2.5 rounded-xl bg-[#F5F7FA] border border-[#DCE3EC]">
                  <span className="text-[#64748B]">Owner Contact:</span>
                  <span className="font-mono text-[#172B4D]">{v.owner_phone || '+91-98765-XXXXX'}</span>
                </div>
                <div className="flex justify-between p-2.5 rounded-xl bg-[#F5F7FA] border border-[#DCE3EC]">
                  <span className="text-[#64748B]">Registered Address:</span>
                  <span className="font-medium text-[#172B4D] max-w-xs text-right truncate">
                    {v.owner_address || 'New Delhi, India'}
                  </span>
                </div>
                <div className="flex justify-between p-2.5 rounded-xl bg-[#F5F7FA] border border-[#DCE3EC]">
                  <span className="text-[#64748B]">Chassis / VIN:</span>
                  <span className="font-mono font-semibold text-[#172B4D]">{v.chassis_number}</span>
                </div>
                <div className="flex justify-between p-2.5 rounded-xl bg-[#F5F7FA] border border-[#DCE3EC]">
                  <span className="text-[#64748B]">Engine Number:</span>
                  <span className="font-mono font-semibold text-[#172B4D]">{v.engine_number}</span>
                </div>
              </div>
            </div>

            {/* SECTION 4: Driver & Driving Licence Information */}
            <div className="p-6 rounded-2xl border border-[#DCE3EC] bg-white shadow-sm space-y-4">
              <div className="flex items-center gap-2.5 border-b border-[#DCE3EC] pb-3">
                <UserCheck className="h-5 w-5 text-[#1769D2]" />
                <div>
                  <h3 className="font-bold text-sm text-[#172B4D]">Driver & Driving Licence Details</h3>
                  <p className="text-[11px] text-[#64748B]">Distinguished from Vehicle Owner</p>
                </div>
              </div>

              <div className="space-y-2.5 text-xs">
                <div className="flex justify-between p-2.5 rounded-xl bg-[#F5F7FA] border border-[#DCE3EC]">
                  <span className="text-[#64748B]">Assigned Driver Name:</span>
                  <span className="font-bold text-[#172B4D]">{v.driver_name || v.owner_name}</span>
                </div>
                <div className="flex justify-between p-2.5 rounded-xl bg-[#F5F7FA] border border-[#DCE3EC]">
                  <span className="text-[#64748B]">Driver Licence Number:</span>
                  <span className="font-mono font-bold text-[#1769D2]">{v.driver_license_number || 'N/A'}</span>
                </div>
                <div className="flex justify-between p-2.5 rounded-xl bg-[#F5F7FA] border border-[#DCE3EC]">
                  <span className="text-[#64748B]">Licence Class:</span>
                  <span className="font-semibold text-[#172B4D]">{v.driver_license_class || 'LMV'}</span>
                </div>
                <div className="flex justify-between p-2.5 rounded-xl bg-[#F5F7FA] border border-[#DCE3EC]">
                  <span className="text-[#64748B]">Licence Expiry:</span>
                  <span className="font-semibold text-[#172B4D]">{v.driver_license_expiry || '2032-12-31'}</span>
                </div>
                <div className="flex justify-between p-2.5 rounded-xl bg-[#F5F7FA] border border-[#DCE3EC]">
                  <span className="text-[#64748B]">Licence Status:</span>
                  <StatusBadge status={v.driver_license_status || 'VALID'} />
                </div>
                <div className="p-3 rounded-xl bg-[#EFF5FF] border border-[#DCE3EC] text-xs text-[#1769D2] flex items-start gap-2 mt-2">
                  <Info className="h-4 w-4 shrink-0 mt-0.5" />
                  <p className="leading-relaxed">
                    Under Indian Motor Vehicle regulations, driver authorization is inspected independently of owner liabilities.
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* SECTION 5: The 4 Mandatory Documents Cards */}
          <div className="space-y-4">
            <div className="flex items-center justify-between border-b border-[#DCE3EC] pb-2">
              <h3 className="font-extrabold text-base text-[#172B4D] flex items-center gap-2">
                <ShieldCheck className="h-5 w-5 text-[#1769D2]" />
                <span>Statutory Compliance Documents (Parivahan Vahan 4.0)</span>
              </h3>
              <span className="text-xs text-[#64748B]">Dynamic Date-Based Evaluation</span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {[
                { key: 'RC', label: 'Registration Certificate (RC)', desc: 'Vehicle Fitness & Title' },
                { key: 'INSURANCE', label: 'Motor Vehicle Insurance', desc: 'Mandatory Third-Party Cover' },
                { key: 'PUC', label: 'Pollution Under Control (PUC)', desc: 'Emission Certificate' },
                { key: 'ROAD_TAX', label: 'Commercial Road Tax', desc: 'State Transport Levy' },
              ].map(({ key, label, desc }) => {
                const doc = documents[key];
                const status = doc?.status || 'MISSING';
                const isDocValid = status === 'VALID';
                const isDocExpiring = status === 'EXPIRING_SOON';
                const isDocExpired = status === 'EXPIRED';
                const isDocMissing = status === 'MISSING';

                let badgeColor = 'bg-slate-100 text-slate-700 border-slate-300';
                let borderColor = 'border-[#DCE3EC]';
                if (isDocValid) {
                  badgeColor = 'bg-emerald-50 text-[#16A36A] border-emerald-200';
                  borderColor = 'border-emerald-200';
                } else if (isDocExpiring) {
                  badgeColor = 'bg-amber-50 text-[#E5A000] border-amber-200';
                  borderColor = 'border-amber-200';
                } else if (isDocExpired) {
                  badgeColor = 'bg-rose-50 text-[#DC4545] border-rose-200';
                  borderColor = 'border-rose-200';
                }

                return (
                  <div
                    key={key}
                    className={`p-4 rounded-2xl bg-white border ${borderColor} shadow-sm space-y-3 flex flex-col justify-between`}
                  >
                    <div>
                      <div className="flex items-center justify-between gap-2 mb-1.5">
                        <span className="text-[11px] font-extrabold text-[#172B4D] uppercase tracking-wider">
                          {key.replace('_', ' ')}
                        </span>
                        <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${badgeColor}`}>
                          {status}
                        </span>
                      </div>
                      <h4 className="font-bold text-xs text-[#172B4D] leading-tight">{label}</h4>
                      <p className="text-[10px] text-[#64748B] mt-0.5">{desc}</p>
                    </div>

                    <div className="pt-2 border-t border-[#DCE3EC] space-y-1.5 text-[11px]">
                      <div className="flex justify-between">
                        <span className="text-[#64748B]">Certificate #:</span>
                        <span className="font-mono font-semibold text-[#172B4D]">
                          {doc?.document_number || 'NOT ON FILE'}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-[#64748B]">Expiry Date:</span>
                        <span className="font-mono font-semibold text-[#172B4D]">
                          {doc?.expiry_date || 'N/A'}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-[#64748B]">Validity:</span>
                        <span className="font-medium text-[#172B4D]">
                          {doc?.days_until_expiry !== null && doc?.days_until_expiry !== undefined
                            ? doc.days_until_expiry < 0
                              ? `Expired ${Math.abs(doc.days_until_expiry)}d ago`
                              : `${doc.days_until_expiry} days left`
                            : 'Missing Record'}
                        </span>
                      </div>
                      <div className="text-[10px] text-[#64748B] pt-1 border-t border-[#DCE3EC]/60 truncate">
                        Provider: {doc?.provider || 'State Authority'}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* SECTION 6: Previous Demo Challans */}
          <div className="p-6 rounded-2xl border border-[#DCE3EC] bg-white shadow-sm space-y-4">
            <div className="flex items-center justify-between border-b border-[#DCE3EC] pb-3">
              <div className="flex items-center gap-2">
                <Receipt className="h-5 w-5 text-[#1769D2]" />
                <h3 className="font-bold text-sm text-[#172B4D]">Previous Demo Traffic Citations</h3>
              </div>
              <span className="text-xs text-[#64748B]">
                Total Historical Challans: <strong>{previousChallans.length}</strong>
              </span>
            </div>

            {previousChallans.length === 0 ? (
              <p className="text-xs text-[#64748B] py-3 text-center">
                Clean historical record. No prior traffic challans issued against this vehicle.
              </p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-[#EFF5FF] text-[#172B4D] font-bold uppercase text-[10px] border-b border-[#DCE3EC]">
                    <tr>
                      <th className="py-2.5 px-3">Citation Number</th>
                      <th className="py-2.5 px-3">Violation Type</th>
                      <th className="py-2.5 px-3">Fine Amount</th>
                      <th className="py-2.5 px-3">Challan Date</th>
                      <th className="py-2.5 px-3">Payment Status</th>
                      <th className="py-2.5 px-3 text-right">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#DCE3EC]">
                    {previousChallans.map((ch) => (
                      <tr key={ch.id} className="hover:bg-[#F5F7FA]">
                        <td className="py-2.5 px-3 font-mono font-bold text-[#1769D2]">
                          {ch.challan_number}
                        </td>
                        <td className="py-2.5 px-3 text-[#172B4D] font-medium">
                          {ch.violation_type.replace(/_/g, ' ')}
                        </td>
                        <td className="py-2.5 px-3 font-mono font-bold text-[#172B4D]">
                          ₹{Number(ch.fine_amount).toLocaleString('en-IN')}
                        </td>
                        <td className="py-2.5 px-3 text-[#64748B] font-mono">
                          {ch.challan_date}
                        </td>
                        <td className="py-2.5 px-3">
                          <StatusBadge status={ch.payment_status} />
                        </td>
                        <td className="py-2.5 px-3 text-right">
                          <button
                            onClick={() => onSelectChallan?.(ch)}
                            className="text-[#1769D2] hover:underline font-bold text-xs"
                          >
                            View
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          {/* SECTION 7: Violations & Statutory Fine Calculation */}
          {summary?.has_violations && (
            <div className="p-6 rounded-2xl border border-rose-200 bg-white shadow-sm space-y-4">
              <div className="flex items-center justify-between border-b border-rose-100 pb-3">
                <div className="flex items-center gap-2">
                  <BadgeAlert className="h-5 w-5 text-[#DC4545]" />
                  <h3 className="font-bold text-sm text-[#172B4D]">
                    Identified Violations & Statutory Fines (Motor Vehicles Act 2019)
                  </h3>
                </div>
                <span className="text-xs font-bold text-[#DC4545]">
                  Total Fine: ₹{fines?.total_fine?.toLocaleString('en-IN')}
                </span>
              </div>

              <div className="space-y-2 text-xs">
                {violations.map((vio, idx) => (
                  <div
                    key={idx}
                    className="flex items-center justify-between p-3 rounded-xl bg-rose-50/50 border border-rose-100 text-[#172B4D]"
                  >
                    <div>
                      <p className="font-bold">{vio.title}</p>
                      <p className="text-[11px] text-[#64748B]">
                        {vio.statute} &bull; {vio.description}
                      </p>
                    </div>
                    <span className="font-mono font-bold text-rose-700 text-sm">
                      ₹{vio.fine_amount?.toLocaleString('en-IN')}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
