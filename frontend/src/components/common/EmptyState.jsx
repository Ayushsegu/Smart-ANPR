/**
 * components/common/EmptyState.jsx
 * ================================
 * Clean Enterprise Empty State Display
 */

import React from 'react';
import { Search } from 'lucide-react';

export default function EmptyState({
  icon: Icon = Search,
  title = 'No records found',
  description = 'No matching information was discovered for your current criteria.',
  actionLabel,
  onAction,
}) {
  return (
    <div className="rounded-xl border border-dashed border-[#DCE3EC] bg-[#F5F7FA]/50 p-10 text-center flex flex-col items-center justify-center space-y-3">
      <div className="h-12 w-12 rounded-xl bg-[#EFF5FF] border border-[#DCE3EC] flex items-center justify-center text-[#1769D2] shadow-sm">
        <Icon className="h-6 w-6" />
      </div>
      <div className="space-y-1 max-w-sm">
        <h4 className="text-sm font-bold text-[#172B4D]">{title}</h4>
        <p className="text-xs text-[#64748B] leading-relaxed">{description}</p>
      </div>
      {actionLabel && onAction && (
        <button
          onClick={onAction}
          className="mt-2 px-4 py-2 rounded-lg bg-[#1769D2] hover:bg-[#1258B3] text-white text-xs font-bold transition-all shadow-sm"
        >
          {actionLabel}
        </button>
      )}
    </div>
  );
}
