import type { VerificationStatus } from '@/types'

const STATUS_CONFIG: Record<VerificationStatus, { icon: string; label_ar: string; className: string }> = {
  supported: {
    icon: '✓',
    label_ar: 'مدعوم بالدليل',
    className: 'status-supported',
  },
  partially_supported: {
    icon: '◐',
    label_ar: 'مدعوم جزئياً',
    className: 'status-partially_supported',
  },
  needs_review: {
    icon: '⚠',
    label_ar: 'يحتاج إلى مراجعة',
    className: 'status-needs_review',
  },
  insufficient_evidence: {
    icon: '∅',
    label_ar: 'دليل غير كافٍ (امتناع)',
    className: 'status-insufficient_evidence',
  },
  source_conflict: {
    icon: '⚡',
    label_ar: 'تعارض في المصادر',
    className: 'status-source_conflict',
  },
  specialist_referral: {
    icon: '⚖',
    label_ar: 'إحالة إلى مختص',
    className: 'status-specialist_referral',
  },
  pending: {
    icon: '⏳',
    label_ar: 'قيد المعالجة',
    className: 'status-insufficient_evidence',
  },
  error: {
    icon: '✕',
    label_ar: 'خطأ في التحقق',
    className: 'status-specialist_referral',
  },
}

interface StatusBadgeProps {
  status: VerificationStatus
  size?: 'sm' | 'md' | 'lg'
}

export default function StatusBadge({ status, size = 'md' }: StatusBadgeProps) {
  const config = STATUS_CONFIG[status] || STATUS_CONFIG.insufficient_evidence

  const sizeStyles = {
    sm: { fontSize: '0.78rem', padding: '3px 10px' },
    md: { fontSize: '0.85rem', padding: '5px 14px' },
    lg: { fontSize: '0.95rem', padding: '8px 18px' },
  }

  return (
    <span
      className={`status-badge ${config.className}`}
      style={sizeStyles[size]}
      role="status"
      aria-label={config.label_ar}
    >
      <span style={{ fontWeight: 800, fontSize: '1.05em' }} aria-hidden="true">{config.icon}</span>
      <span>{config.label_ar}</span>
    </span>
  )
}
