/**
 * components/common/Breadcrumbs.jsx
 * =================================
 * Enterprise Page Breadcrumb Navigation & Header Bar
 * Supports Dark Mode & Flexible items/pageTitle props
 */

import React from 'react';
import { ChevronRight, Shield } from 'lucide-react';

export default function Breadcrumbs({ pageTitle, category = 'Operations Console', badge = null, items }) {
  if (items && Array.isArray(items)) {
    return (
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-6 pb-4 border-b border-[#DCE3EC] dark:border-slate-800">
        <nav className="flex items-center gap-1.5 text-xs text-[#64748B] dark:text-slate-400">
          <span className="flex items-center gap-1 hover:text-[#1769D2] cursor-default font-medium">
            <Shield className="h-3 w-3 text-[#1769D2]" />
            Smart ANPR
          </span>
          {items.map((item, idx) => (
            <React.Fragment key={idx}>
              <ChevronRight className="h-3 w-3 text-[#64748B]/60 dark:text-slate-600" />
              <span className={idx === items.length - 1 ? 'font-bold text-[#172B4D] dark:text-slate-100' : 'font-medium'}>
                {item.label}
              </span>
            </React.Fragment>
          ))}
        </nav>
      </div>
    );
  }

  return (
    <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-6 pb-4 border-b border-[#DCE3EC] dark:border-slate-800">
      <div className="space-y-1">
        <nav className="flex items-center gap-1.5 text-xs text-[#64748B] dark:text-slate-400">
          <span className="flex items-center gap-1 hover:text-[#1769D2] cursor-default font-medium">
            <Shield className="h-3 w-3 text-[#1769D2]" />
            Smart ANPR
          </span>
          <ChevronRight className="h-3 w-3 text-[#64748B]/60 dark:text-slate-600" />
          <span className="font-medium text-[#64748B] dark:text-slate-400">{category}</span>
          <ChevronRight className="h-3 w-3 text-[#64748B]/60 dark:text-slate-600" />
          <span className="font-bold text-[#172B4D] dark:text-slate-100">{pageTitle}</span>
        </nav>
        <h1 className="text-xl sm:text-2xl font-black text-[#172B4D] dark:text-slate-100 tracking-tight">
          {pageTitle}
        </h1>
      </div>

      {badge && (
        <div className="self-start sm:self-center">
          {badge}
        </div>
      )}
    </div>
  );
}
