import React from 'react';

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: 'default' | 'success' | 'warning' | 'error' | 'neutral' | 'purple' | 'blue';
  size?: 'sm' | 'md';
  dot?: boolean;
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = 'default',
  size = 'md',
  dot = false,
  className = '',
  ...props
}) => {
  const sizes = {
    sm: 'text-[11px] px-2.5 py-0.5 font-medium gap-1',
    md: 'text-xs px-3 py-1 font-semibold gap-1.5',
  };

  const variants = {
    default: 'bg-surface-container text-on-surface-variant border border-outline-variant/60',
    success: 'bg-emerald-500/10 text-emerald-700 dark:text-emerald-400 border border-emerald-500/20',
    warning: 'bg-amber-500/10 text-amber-700 dark:text-amber-400 border border-amber-500/20',
    error: 'bg-rose-500/10 text-rose-700 dark:text-rose-400 border border-rose-500/20',
    neutral: 'bg-slate-500/10 text-slate-700 dark:text-slate-300 border border-slate-500/20',
    purple: 'bg-violet-500/10 text-violet-700 dark:text-violet-400 border border-violet-500/20',
    blue: 'bg-blue-500/10 text-blue-700 dark:text-blue-400 border border-blue-500/20',
  };

  const dotColors = {
    default: 'bg-on-surface-variant',
    success: 'bg-emerald-500',
    warning: 'bg-amber-500',
    error: 'bg-rose-500',
    neutral: 'bg-slate-500',
    purple: 'bg-violet-500',
    blue: 'bg-blue-500',
  };

  return (
    <span
      className={`inline-flex items-center rounded-full shrink-0 select-none ${sizes[size]} ${variants[variant]} ${className}`}
      {...props}
    >
      {dot && <span className={`w-1.5 h-1.5 rounded-full ${dotColors[variant]}`} />}
      {children}
    </span>
  );
};
