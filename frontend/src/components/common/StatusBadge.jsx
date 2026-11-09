/**
 * components/common/StatusBadge.jsx
 * =================================
 * Premium Enterprise Status Badge Component
 * Style 4: Minimalist, clean border, subtle background, professional dot.
 * Supports Multi-Language i18n & Dark Mode
 */

import React from 'react';
import { CheckCircle2, AlertTriangle, XCircle, Clock, ShieldAlert, HelpCircle } from 'lucide-react';
import { useTranslation } from '../../context/I18nContext';

export default function StatusBadge({ status, label, size = 'sm' }) {
  const { t } = useTranslation();
  const normalized = (status || '').toUpperCase().trim();

  let bg = 'bg-[#F5F7FA] dark:bg-slate-800';
  let text = 'text-[#64748B] dark:text-slate-300';
  let border = 'border-[#DCE3EC] dark:border-slate-700';
  let dot = 'bg-[#64748B]';
  let Icon = HelpCircle;
  let textLabel = label || normalized;

  switch (normalized) {
    case 'VALID':
    case 'COMPLIANT':
    case 'PAID':
    case 'ACTIVE':
    case 'HELMET_COMPLIANT':
    case 'SETTLED':
      bg = 'bg-[#ECFDF3] dark:bg-emerald-950/40';
      text = 'text-[#16A36A] dark:text-emerald-400';
      border = 'border-[#A6F4C5] dark:border-emerald-900';
      dot = 'bg-[#16A36A]';
      Icon = CheckCircle2;
      textLabel = label || (normalized === 'VALID' ? t('common.valid', {}, 'VALID') : normalized === 'COMPLIANT' ? t('common.compliant', {}, 'COMPLIANT') : normalized === 'PAID' ? t('common.paid', {}, 'PAID') : normalized === 'HELMET_COMPLIANT' ? 'Helmet Verified' : normalized);
      break;

    case 'EXPIRING_SOON':
    case 'PENDING':
    case 'WARNING':
    case 'MANUAL_REVIEW':
    case 'UNCERTAIN_MANUAL_REVIEW':
      bg = 'bg-[#FEFBE8] dark:bg-amber-950/40';
      text = 'text-[#B45309] dark:text-amber-400';
      border = 'border-[#FDE047] dark:border-amber-900';
      dot = 'bg-[#E5A000]';
      Icon = AlertTriangle;
      textLabel = label || (normalized === 'EXPIRING_SOON' ? t('common.expiring_soon', {}, 'EXPIRING SOON') : normalized === 'PENDING' ? t('common.pending', {}, 'PENDING') : normalized === 'MANUAL_REVIEW' ? 'Review Needed' : normalized);
      break;

    case 'EXPIRED':
    case 'VIOLATION':
    case 'FAILED':
    case 'INACTIVE':
    case 'NO_HELMET_VIOLATION':
    case 'UNREGISTERED':
      bg = 'bg-[#FEF2F2] dark:bg-rose-950/40';
      text = 'text-[#DC4545] dark:text-rose-400';
      border = 'border-[#FCA5A5] dark:border-rose-900';
      dot = 'bg-[#DC4545]';
      Icon = XCircle;
      textLabel = label || (normalized === 'EXPIRED' ? t('common.expired', {}, 'EXPIRED') : normalized === 'NO_HELMET_VIOLATION' ? 'No Helmet' : normalized);
      break;

    case 'MISSING':
    case 'UNPAID':
      bg = 'bg-[#FFF7ED] dark:bg-orange-950/40';
      text = 'text-[#C2410C] dark:text-orange-400';
      border = 'border-[#FFEDD5] dark:border-orange-900';
      dot = 'bg-[#EA580C]';
      Icon = AlertTriangle;
      textLabel = label || (normalized === 'MISSING' ? t('common.missing', {}, 'MISSING') : normalized === 'UNPAID' ? t('common.unpaid', {}, 'UNPAID') : normalized);
      break;

    default:
      break;
  }

  const sizeClasses =
    size === 'xs'
      ? 'px-2 py-0.5 text-[10px] gap-1'
      : size === 'md'
      ? 'px-3 py-1.5 text-xs gap-1.5'
      : 'px-2.5 py-1 text-[11px] gap-1.5';

  return (
    <span
      className={`inline-flex items-center font-bold rounded-full border ${bg} ${text} ${border} ${sizeClasses} tracking-wide select-none`}
    >
      <span className={`h-1.5 w-1.5 rounded-full ${dot} shrink-0`}></span>
      <span className="font-mono uppercase">{textLabel}</span>
    </span>
  );
}
