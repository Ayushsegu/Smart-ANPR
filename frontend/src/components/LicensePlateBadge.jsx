/**
 * components/LicensePlateBadge.jsx - Realistic Indian HSRP License Plate Badge
 * ===========================================================================
 * Smart ANPR Vehicle Verification System
 */

import React from 'react';

export default function LicensePlateBadge({
  plate = 'DL01AB1234',
  vehicleType = 'Car',
  size = 'md',
  className = '',
}) {
  const clean = (plate || '').toUpperCase().replace(/\s+/g, '');

  // Format with space grouping: e.g. DL 01 AB 1234
  const formatted = clean.length >= 8
    ? `${clean.slice(0, 2)} ${clean.slice(2, 4)} ${clean.slice(4, clean.length - 4)} ${clean.slice(-4)}`
    : clean;

  const isCommercial =
    vehicleType?.toLowerCase().includes('commercial') ||
    vehicleType?.toLowerCase().includes('truck') ||
    vehicleType?.toLowerCase().includes('taxi') ||
    vehicleType?.toLowerCase().includes('cab') ||
    clean.startsWith('DL1L');

  // Styles based on size
  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5 border',
    md: 'text-sm px-3 py-1 border-2',
    lg: 'text-xl px-4 py-1.5 border-2',
    xl: 'text-2xl md:text-3xl px-6 py-2.5 border-[3px]',
  }[size] || 'text-sm px-3 py-1 border-2';

  const bgClasses = isCommercial
    ? 'bg-amber-400 text-slate-950 border-amber-600'
    : 'bg-slate-100 text-slate-950 border-slate-300';

  return (
    <div
      className={`inline-flex items-center rounded-md font-mono font-black tracking-wider shadow-md select-all ${bgClasses} ${sizeClasses} ${className}`}
      style={{
        boxShadow: '0 2px 8px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.6)',
      }}
    >
      {/* Blue IND left strip */}
      <div className="flex flex-col items-center justify-center mr-2 px-1 py-0.5 bg-blue-700 text-white rounded text-[8px] leading-none font-sans font-bold">
        <span className="text-[7px] text-amber-300">●</span>
        <span>IND</span>
      </div>

      {/* License plate characters */}
      <span className="tracking-widest uppercase">{formatted}</span>
    </div>
  );
}
