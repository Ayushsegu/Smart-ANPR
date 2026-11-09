/**
 * components/Toast.jsx - Notification Alert Component
 * ====================================================
 * Smart ANPR Vehicle Verification System
 * Design: White and Blue Professional Enterprise SaaS UI
 */

import React from 'react';
import { CheckCircle2, AlertCircle, Info, X } from 'lucide-react';

export default function Toast({ toasts = [], onDismiss }) {
  if (!toasts || toasts.length === 0) return null;

  return (
    <div className="fixed bottom-5 right-5 z-50 flex flex-col gap-2 max-w-md w-full pointer-events-none">
      {toasts.map((toast) => {
        const isSuccess = toast.type === 'success';
        const isError = toast.type === 'error';
        const isInfo = toast.type === 'info';

        const borderClass = isSuccess
          ? 'border-emerald-200 border-l-4 border-l-emerald-500'
          : isError
          ? 'border-rose-200 border-l-4 border-l-rose-500'
          : 'border-[#DCE8F8] border-l-4 border-l-[#1769D2]';

        const Icon = isSuccess ? CheckCircle2 : isError ? AlertCircle : Info;
        const iconColor = isSuccess ? 'text-emerald-600' : isError ? 'text-rose-600' : 'text-[#1769D2]';

        return (
          <div
            key={toast.id}
            className={`pointer-events-auto flex items-start gap-3 p-4 rounded-xl bg-white border shadow-lg backdrop-blur-md transition-all animate-in slide-in-from-bottom-3 duration-200 ${borderClass}`}
          >
            <Icon className={`h-5 w-5 shrink-0 mt-0.5 ${iconColor}`} />
            <div className="flex-1 min-w-0">
              {toast.title && (
                <h4 className="text-sm font-bold text-[#172B4D]">{toast.title}</h4>
              )}
              <p className="text-xs text-[#42526E] mt-0.5 leading-relaxed break-words">
                {toast.message}
              </p>
            </div>
            {onDismiss && (
              <button
                onClick={() => onDismiss(toast.id)}
                className="text-[#6B778C] hover:text-[#172B4D] p-1 rounded-md transition-colors"
              >
                <X className="h-4 w-4" />
              </button>
            )}
          </div>
        );
      })}
    </div>
  );
}
