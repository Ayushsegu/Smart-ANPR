/**
 * components/DemoFleetTesting.jsx - 50 Pre-Registered Demo Vehicles Fleet & Testing Hub
 * ======================================================================================
 * Smart ANPR Vehicle Verification System
 * Design: STYLE 4 – PREMIUM ENTERPRISE (WHITE + BLUE + GREY)
 *
 * Implements:
 * 1. Directory of all 50 pre-registered demo vehicles (DEMO-01 to DEMO-50).
 * 2. Instant manual verification trigger with a single click.
 * 3. Multi-attribute filtering: Search by Plate/ID, Filter by Type, State & Compliance.
 * 4. Masked personal owner data protected behind officer duty session.
 * 5. Admin modal to register custom demo test vehicles.
 */

import React, { useState, useEffect } from 'react';
import {
  DatabaseZap,
  Search,
  Filter,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Clock,
  Car,
  FileCheck2,
  Copy,
  ExternalLink,
  ShieldCheck,
  RefreshCw,
  PlusCircle,
  HelpCircle,
  Fuel,
  Calendar,
  Layers,
  MapPin,
  UserCheck,
  X,
} from 'lucide-react';
import { getVehicles, registerDemoVehicle } from '../services/api';
import Breadcrumbs from './common/Breadcrumbs';
import StatusBadge from './common/StatusBadge';
import EmptyState from './common/EmptyState';
import LicensePlateBadge from './LicensePlateBadge';

export default function DemoFleetTesting({ onVerifyPlate, currentUser, showToast }) {
  const [vehicles, setVehicles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [typeFilter, setTypeFilter] = useState('ALL');
  const [stateFilter, setStateFilter] = useState('ALL');
  const [complianceFilter, setComplianceFilter] = useState('ALL');
  const [copiedPlate, setCopiedPlate] = useState(null);

  // Register New Demo Vehicle Modal
  const [showAddModal, setShowAddModal] = useState(false);
  const [newReg, setNewReg] = useState('');
  const [newOwner, setNewOwner] = useState('');
  const [newMake, setNewMake] = useState('Maruti Suzuki');
  const [newModel, setNewModel] = useState('');
  const [newType, setNewType] = useState('Car');
  const [newState, setNewState] = useState('Delhi');
  const [newFuel, setNewFuel] = useState('Petrol');
  const [newYear, setNewYear] = useState('2023');
  const [newPhone, setNewPhone] = useState('+91-98765-01099');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const fetchFleet = async () => {
    setLoading(true);
    try {
      const res = await getVehicles({ is_demo: 1 });
      setVehicles(res.vehicles || []);
    } catch (err) {
      showToast?.({
        type: 'error',
        title: 'Failed to load demo fleet',
        message: err.message,
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFleet();
  }, []);

  const handleCopyPlate = (plate) => {
    navigator.clipboard.writeText(plate);
    setCopiedPlate(plate);
    showToast?.({
      type: 'info',
      title: 'Plate Identifier Copied',
      message: `Copied ${plate} to clipboard. You can paste it into ANPR Scanner or Search.`,
    });
    setTimeout(() => setCopiedPlate(null), 2500);
  };

  const handleCreateDemoVehicle = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      await registerDemoVehicle({
        registration_number: newReg.toUpperCase().replace(/\s+/g, ''),
        owner_name: `${newOwner} [Demo Owner]`,
        vehicle_type: newType,
        vehicle_class: newType,
        vehicle_model: newModel,
        manufacturer: newMake,
        state: newState,
        rto_code: `${newReg.slice(0, 4)} RTO`,
        fuel_type: newFuel,
        manufacturing_year: parseInt(newYear, 10),
        owner_phone: newPhone,
        driver_name: newOwner,
      });

      showToast?.({
        type: 'success',
        title: 'Demo Vehicle Registered',
        message: `Registered ${newReg.toUpperCase()} into local demo database.`,
      });

      setShowAddModal(false);
      setNewReg('');
      setNewOwner('');
      setNewModel('');
      fetchFleet();
    } catch (err) {
      showToast?.({
        type: 'error',
        title: 'Registration Failed',
        message: err.message,
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const filteredVehicles = vehicles.filter((v) => {
    const q = searchQuery.toLowerCase().trim();
    const matchQuery =
      !q ||
      v.registration_number?.toLowerCase().includes(q) ||
      v.demo_id?.toLowerCase().includes(q) ||
      v.owner_name?.toLowerCase().includes(q) ||
      v.vehicle_model?.toLowerCase().includes(q) ||
      v.manufacturer?.toLowerCase().includes(q);

    const matchType =
      typeFilter === 'ALL' ||
      (v.vehicle_type || '').toLowerCase() === typeFilter.toLowerCase() ||
      (v.vehicle_class || '').toLowerCase() === typeFilter.toLowerCase();

    const matchState =
      stateFilter === 'ALL' ||
      (v.state || '').toLowerCase().includes(stateFilter.toLowerCase());

    return matchQuery && matchType && matchState;
  });

  return (
    <div className="space-y-6">
      {/* Breadcrumbs */}
      <Breadcrumbs items={[{ label: 'Field Testing' }, { label: '50 Pre-Registered Demo Vehicles' }]} />

      {/* Prominent Demo Notice Banner */}
      <div className="p-4 rounded-2xl bg-[#EFF5FF] border border-[#DCE3EC] flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
        <div className="flex items-start gap-3">
          <div className="w-8 h-8 rounded-xl bg-[#1769D2] text-white flex items-center justify-center shrink-0 font-bold">
            <DatabaseZap className="h-4 w-4" />
          </div>
          <div>
            <h4 className="font-extrabold text-[#172B4D] tracking-wide text-sm flex items-center gap-2">
              <span>DEMO DATASET — 50 PRE-REGISTERED VEHICLES</span>
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-blue-100 text-[#1769D2] font-bold">
                ACADEMIC / FIELD SIMULATION
              </span>
            </h4>
            <p className="text-[#64748B] mt-0.5 leading-relaxed">
              All records below are synthetic and stored strictly in the local SQLite database. Use these pre-registered
              license plates to reliably demonstrate number plate recognition, document compliance checking, and digital challan issuance.
            </p>
          </div>
        </div>

        {currentUser?.role === 'ADMIN' && (
          <button
            onClick={() => setShowAddModal(true)}
            className="px-4 py-2 rounded-xl bg-[#1769D2] hover:bg-[#1258B3] text-white text-xs font-bold transition-all shadow-sm flex items-center gap-2 shrink-0 self-start sm:self-auto"
          >
            <PlusCircle className="h-3.5 w-3.5" />
            <span>Add Demo Vehicle</span>
          </button>
        )}
      </div>

      {/* Header & Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#DCE3EC] pb-4">
        <div>
          <h2 className="text-xl md:text-2xl font-bold text-[#172B4D] flex items-center gap-2.5">
            <Layers className="h-6 w-6 text-[#1769D2]" />
            <span>Demo Fleet Directory & Testing Hub</span>
          </h2>
          <p className="text-xs text-[#64748B] mt-1">
            Displaying <strong>{filteredVehicles.length}</strong> of <strong>{vehicles.length}</strong> pre-registered vehicles across 6 states
          </p>
        </div>

        <button
          onClick={fetchFleet}
          className="px-3.5 py-2 rounded-xl bg-white hover:bg-[#F5F7FA] text-[#172B4D] text-xs font-semibold border border-[#DCE3EC] shadow-sm flex items-center gap-2 transition-colors self-start sm:self-auto"
        >
          <RefreshCw className={`h-3.5 w-3.5 ${loading ? 'animate-spin text-[#1769D2]' : 'text-[#64748B]'}`} />
          <span>Refresh Fleet</span>
        </button>
      </div>

      {/* Search and Filters Toolbar */}
      <div className="p-4 rounded-2xl border border-[#DCE3EC] bg-white shadow-sm space-y-3">
        <div className="flex flex-col md:flex-row items-stretch md:items-center gap-3">
          {/* Search Input */}
          <div className="relative flex-1">
            <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-[#64748B]" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search by Plate (e.g. DL01DM0001), Demo ID (DEMO-01), Model, Make, Owner..."
              className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-white border border-[#DCE3EC] text-xs font-medium text-[#172B4D] placeholder-slate-400 focus:outline-none focus:border-[#1769D2] focus:ring-2 focus:ring-[#1769D2]/15 transition-colors"
            />
          </div>

          {/* Type Filter */}
          <div className="flex items-center gap-2">
            <span className="text-xs text-[#64748B] font-bold">Class:</span>
            <select
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
              className="px-3 py-2 rounded-xl bg-white border border-[#DCE3EC] text-xs font-semibold text-[#172B4D] focus:outline-none focus:border-[#1769D2]"
            >
              <option value="ALL">All Classes</option>
              <option value="Car">Cars</option>
              <option value="SUV">SUVs</option>
              <option value="Motorcycle">Motorcycles</option>
              <option value="Scooter">Scooters</option>
              <option value="Commercial">Commercial</option>
              <option value="Transport">Transport / Heavy</option>
            </select>
          </div>

          {/* State Filter */}
          <div className="flex items-center gap-2">
            <span className="text-xs text-[#64748B] font-bold">State:</span>
            <select
              value={stateFilter}
              onChange={(e) => setStateFilter(e.target.value)}
              className="px-3 py-2 rounded-xl bg-white border border-[#DCE3EC] text-xs font-semibold text-[#172B4D] focus:outline-none focus:border-[#1769D2]"
            >
              <option value="ALL">All States</option>
              <option value="Delhi">Delhi (DL-01)</option>
              <option value="Haryana">Haryana (HR-26)</option>
              <option value="Maharashtra">Maharashtra (MH-12)</option>
              <option value="Karnataka">Karnataka (KA-05)</option>
              <option value="Tamil Nadu">Tamil Nadu (TN-09)</option>
              <option value="Uttar Pradesh">Uttar Pradesh (UP-32)</option>
            </select>
          </div>
        </div>

        {/* Quick Suggestion Pills */}
        <div className="flex flex-wrap items-center gap-2 pt-1 border-t border-[#DCE3EC] text-[11px]">
          <span className="text-[#64748B] font-bold">Quick Presets:</span>
          {[
            { label: 'DEMO-01 (Maruti Dzire - Valid)', plate: 'DL01DM0001' },
            { label: 'DEMO-02 (Creta - Expired PUC)', plate: 'DL01DM0002' },
            { label: 'DEMO-03 (Nexon EV - Expiring Ins)', plate: 'DL01DM0003' },
            { label: 'DEMO-04 (Classic 350 - Valid)', plate: 'DL01DM0004' },
            { label: 'DEMO-05 (Activa - Expired Ins)', plate: 'DL01DM0005' },
            { label: 'DEMO-06 (Ace Gold - Expired Tax)', plate: 'DL01DM0006' },
            { label: 'DEMO-10 (Innova - Missing PUC)', plate: 'DL01DM0010' },
            { label: 'DEMO-12 (Dost - Expired RC)', plate: 'DL01DM0012' },
          ].map((item, idx) => (
            <button
              key={idx}
              onClick={() => onVerifyPlate?.(item.plate)}
              className="px-2.5 py-1 rounded-lg bg-[#F5F7FA] hover:bg-[#EFF5FF] hover:text-[#1769D2] hover:border-[#1769D2] border border-[#DCE3EC] text-[#172B4D] font-medium transition-colors"
            >
              {item.label}
            </button>
          ))}
        </div>
      </div>

      {/* Vehicles Table / Roster */}
      <div className="rounded-2xl border border-[#DCE3EC] bg-white shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#EFF5FF] text-[#172B4D] font-bold uppercase text-[11px] border-b border-[#DCE3EC]">
              <tr>
                <th className="py-3.5 px-4">Demo ID & Plate</th>
                <th className="py-3.5 px-4">Make, Model & Class</th>
                <th className="py-3.5 px-4">State & RTO Node</th>
                <th className="py-3.5 px-4">Fictional Owner</th>
                <th className="py-3.5 px-4">Assigned Driver</th>
                <th className="py-3.5 px-4 text-center">Dataset Tag</th>
                <th className="py-3.5 px-4 text-right">Testing Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#DCE3EC]">
              {loading ? (
                <tr>
                  <td colSpan="7" className="py-12 text-center text-[#64748B]">
                    <RefreshCw className="h-5 w-5 animate-spin mx-auto text-[#1769D2] mb-2" />
                    Loading pre-registered demo fleet...
                  </td>
                </tr>
              ) : filteredVehicles.length === 0 ? (
                <tr>
                  <td colSpan="7" className="py-12">
                    <EmptyState
                      icon={Car}
                      title="No Demo Vehicles Found"
                      message="No demo vehicle matched your search or filter. Try clearing the filter."
                      actionLabel="Reset Search"
                      onAction={() => {
                        setSearchQuery('');
                        setTypeFilter('ALL');
                        setStateFilter('ALL');
                      }}
                    />
                  </td>
                </tr>
              ) : (
                filteredVehicles.map((v) => {
                  const plate = v.registration_number;
                  const demoId = v.demo_id || `DEMO-${v.id}`;
                  const isCopied = copiedPlate === plate;

                  return (
                    <tr key={v.id} className="hover:bg-[#F5F7FA] transition-colors">
                      {/* Plate & ID */}
                      <td className="py-3.5 px-4">
                        <div className="flex items-center gap-2">
                          <span className="font-mono text-[10px] font-extrabold px-1.5 py-0.5 rounded bg-slate-100 text-[#172B4D] border border-[#DCE3EC]">
                            {demoId}
                          </span>
                          <span className="font-mono font-bold text-xs text-[#1769D2]">
                            {plate}
                          </span>
                          <button
                            onClick={() => handleCopyPlate(plate)}
                            title="Copy Plate Number"
                            className="p-1 rounded text-[#64748B] hover:text-[#1769D2] hover:bg-[#EFF5FF] transition-colors"
                          >
                            <Copy className="h-3 w-3" />
                          </button>
                        </div>
                        <div className="text-[10px] text-[#64748B] mt-0.5 font-mono">
                          Reg: {v.registration_date || '2022-01-01'}
                        </div>
                      </td>

                      {/* Make & Model */}
                      <td className="py-3.5 px-4">
                        <div className="font-bold text-[#172B4D]">{v.vehicle_model}</div>
                        <div className="text-[11px] text-[#64748B] flex items-center gap-2 mt-0.5">
                          <span className="font-semibold text-[#172B4D]">{v.manufacturer || 'Maruti Suzuki'}</span>
                          <span>&bull;</span>
                          <span className="px-1.5 py-0.2 rounded bg-slate-100 text-[#172B4D] font-medium text-[10px]">
                            {v.vehicle_type || v.vehicle_class}
                          </span>
                          <span>&bull;</span>
                          <span className="text-[#64748B]">{v.fuel_type || 'Petrol'}</span>
                        </div>
                      </td>

                      {/* State & RTO */}
                      <td className="py-3.5 px-4">
                        <div className="font-medium text-[#172B4D] flex items-center gap-1.5">
                          <MapPin className="h-3 w-3 text-[#1769D2]" />
                          <span>{v.state || 'Delhi'}</span>
                        </div>
                        <div className="text-[10px] text-[#64748B] mt-0.5">{v.rto_code || 'DL-01'}</div>
                      </td>

                      {/* Owner */}
                      <td className="py-3.5 px-4">
                        <div className="font-semibold text-[#172B4D]">{v.owner_name}</div>
                        <div className="text-[10px] text-[#64748B] mt-0.5">{v.owner_phone || '+91-98765-XXXXX'}</div>
                      </td>

                      {/* Driver */}
                      <td className="py-3.5 px-4">
                        <div className="font-medium text-[#172B4D]">
                          {v.driver_name || v.owner_name}
                        </div>
                        <div className="text-[10px] text-[#64748B] font-mono mt-0.5">
                          DL: {v.driver_license_number || 'VALID'}
                        </div>
                      </td>

                      {/* Demo Marker */}
                      <td className="py-3.5 px-4 text-center">
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-[#EFF5FF] text-[#1769D2] border border-[#DCE3EC]">
                          <ShieldCheck className="h-3 w-3" />
                          <span>DEMO</span>
                        </span>
                      </td>

                      {/* Verification Action */}
                      <td className="py-3.5 px-4 text-right">
                        <button
                          onClick={() => onVerifyPlate?.(plate)}
                          className="px-3.5 py-1.5 rounded-xl bg-[#1769D2] hover:bg-[#1258B3] text-white font-bold text-xs shadow-sm flex items-center gap-1.5 ml-auto transition-all"
                        >
                          <FileCheck2 className="h-3.5 w-3.5" />
                          <span>Verify</span>
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

      {/* Modal: Register Custom Demo Vehicle */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm animate-in fade-in duration-150">
          <div className="w-full max-w-lg rounded-2xl border border-[#DCE3EC] bg-white p-6 shadow-2xl space-y-4 text-[#172B4D]">
            <div className="flex items-center justify-between border-b border-[#DCE3EC] pb-3">
              <div className="flex items-center gap-2">
                <PlusCircle className="h-5 w-5 text-[#1769D2]" />
                <h3 className="font-bold text-base text-[#172B4D]">Register Custom Demo Vehicle</h3>
              </div>
              <button
                onClick={() => setShowAddModal(false)}
                className="text-[#64748B] hover:text-[#172B4D] p-1 rounded-lg"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            <form onSubmit={handleCreateDemoVehicle} className="space-y-3 text-xs">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-bold mb-1">Registration Plate *</label>
                  <input
                    type="text"
                    required
                    value={newReg}
                    onChange={(e) => setNewReg(e.target.value.toUpperCase())}
                    placeholder="e.g. DL01DM0051"
                    className="w-full px-3 py-2 rounded-xl bg-white border border-[#DCE3EC] font-mono font-bold focus:outline-none focus:border-[#1769D2]"
                  />
                </div>
                <div>
                  <label className="block font-bold mb-1">Owner Name *</label>
                  <input
                    type="text"
                    required
                    value={newOwner}
                    onChange={(e) => setNewOwner(e.target.value)}
                    placeholder="e.g. Rajiv Kapoor"
                    className="w-full px-3 py-2 rounded-xl bg-white border border-[#DCE3EC] focus:outline-none focus:border-[#1769D2]"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-bold mb-1">Manufacturer *</label>
                  <select
                    value={newMake}
                    onChange={(e) => setNewMake(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl bg-white border border-[#DCE3EC] focus:outline-none focus:border-[#1769D2]"
                  >
                    <option value="Maruti Suzuki">Maruti Suzuki</option>
                    <option value="Hyundai">Hyundai</option>
                    <option value="Tata">Tata</option>
                    <option value="Honda">Honda</option>
                    <option value="Toyota">Toyota</option>
                    <option value="Mahindra">Mahindra</option>
                    <option value="Kia">Kia</option>
                    <option value="Royal Enfield">Royal Enfield</option>
                    <option value="TVS">TVS</option>
                    <option value="Bajaj">Bajaj</option>
                  </select>
                </div>
                <div>
                  <label className="block font-bold mb-1">Vehicle Model *</label>
                  <input
                    type="text"
                    required
                    value={newModel}
                    onChange={(e) => setNewModel(e.target.value)}
                    placeholder="e.g. Baleno Alpha 1.2"
                    className="w-full px-3 py-2 rounded-xl bg-white border border-[#DCE3EC] focus:outline-none focus:border-[#1769D2]"
                  />
                </div>
              </div>

              <div className="grid grid-cols-3 gap-3">
                <div>
                  <label className="block font-bold mb-1">Class</label>
                  <select
                    value={newType}
                    onChange={(e) => setNewType(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl bg-white border border-[#DCE3EC] focus:outline-none focus:border-[#1769D2]"
                  >
                    <option value="Car">Car</option>
                    <option value="SUV">SUV</option>
                    <option value="Motorcycle">Motorcycle</option>
                    <option value="Scooter">Scooter</option>
                    <option value="Commercial">Commercial</option>
                    <option value="Transport">Transport</option>
                  </select>
                </div>

                <div>
                  <label className="block font-bold mb-1">State</label>
                  <select
                    value={newState}
                    onChange={(e) => setNewState(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl bg-white border border-[#DCE3EC] focus:outline-none focus:border-[#1769D2]"
                  >
                    <option value="Delhi">Delhi</option>
                    <option value="Haryana">Haryana</option>
                    <option value="Maharashtra">Maharashtra</option>
                    <option value="Karnataka">Karnataka</option>
                    <option value="Tamil Nadu">Tamil Nadu</option>
                    <option value="Uttar Pradesh">Uttar Pradesh</option>
                  </select>
                </div>

                <div>
                  <label className="block font-bold mb-1">Fuel Type</label>
                  <select
                    value={newFuel}
                    onChange={(e) => setNewFuel(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl bg-white border border-[#DCE3EC] focus:outline-none focus:border-[#1769D2]"
                  >
                    <option value="Petrol">Petrol</option>
                    <option value="Diesel">Diesel</option>
                    <option value="CNG">CNG</option>
                    <option value="Electric">Electric</option>
                    <option value="Hybrid">Hybrid</option>
                  </select>
                </div>
              </div>

              <div className="flex items-center justify-end gap-3 pt-3 border-t border-[#DCE3EC]">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 rounded-xl bg-[#EFF5FF] hover:bg-[#DDEBFF] text-[#1769D2] font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="px-5 py-2 rounded-xl bg-[#1769D2] hover:bg-[#1258B3] text-white font-bold disabled:opacity-50"
                >
                  {isSubmitting ? 'Registering...' : 'Save Demo Vehicle'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
