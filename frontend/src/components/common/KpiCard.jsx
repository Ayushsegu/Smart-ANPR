/**
 * components/common/KpiCard.jsx
 * =============================
 * Premium Enterprise Metric KPI Card
 * Style 4: Minimalist, clean border, subtle shadow, clear typography.
 * Supports Dark Mode (#1E293B surfaces)
 */

import React from 'react';

export default function KpiCard({
  title,
  value,
  subtitle,
  icon: Icon,
  trend,
  trendPositive = true,
  badge,
  onClick,
  accentColor = '#1769D2',
}) {
  return (
    <div
      onClick={onClick}
      className={`rounded-2xl border border-[#DCE3EC] dark:border-slate-800 bg-white dark:bg-[#1E293B] p-5 shadow-sm hover:shadow-md transition-all duration-150 ${
        onClick ? 'cursor-pointer hover:border-[#1769D2]/50' : ''
      }`}
    >
      <div className="flex items-center justify-between">
        <p className="text-xs font-bold uppercase tracking-wider text-[#64748B] dark:text-slate-400">
          {title}
        </p>
        {Icon && (
          <div
            className="h-9 w-9 rounded-xl flex items-center justify-center shrink-0 border border-[#DCE3EC] dark:border-slate-700 bg-[#EFF5FF] dark:bg-blue-950/60"
            style={{ color: accentColor }}
          >
            <Icon className="h-4 w-4" />
          </div>
        )}
      </div>

      <div className="mt-3 flex items-baseline justify-between gap-2">
        <p className="text-2xl sm:text-3xl font-black text-[#172B4D] dark:text-slate-100 tracking-tight font-mono">
          {value}
        </p>
        {badge && (
          <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-[#EFF5FF] dark:bg-blue-950 text-[#1769D2] dark:text-blue-400 border border-[#DCE3EC] dark:border-slate-700">
            {badge}
          </span>
        )}
      </div>

      {(subtitle || trend) && (
        <div className="mt-2.5 flex items-center justify-between text-xs pt-2 border-t border-[#F5F7FA] dark:border-slate-800">
          {subtitle && (
            <span className="text-[#64748B] dark:text-slate-400 text-[11px] font-medium truncate">
              {subtitle}
            </span>
          )}
          {trend && (
            <span
              className={`text-[11px] font-bold font-mono ${
                trendPositive ? 'text-[#16A36A]' : 'text-[#DC4545]'
              }`}
            >
              {trend}
            </span>
          )}
        </div>
      )}
    </div>
  );
}
