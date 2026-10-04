import React from 'react';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  icon?: React.ReactNode;
  loading?: boolean;
}

export const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'primary',
  size = 'md',
  icon,
  loading = false,
  className = '',
  disabled,
  ...props
}) => {
  const baseStyles = 'inline-flex items-center justify-center font-medium transition-all duration-150 active:scale-[0.98] disabled:opacity-50 disabled:pointer-events-none disabled:active:scale-100 select-none';
  
  // Strict requirement: 10px - 12px border radius, not sharp, not pill
  const radius = 'rounded-xl';

  const sizes = {
    sm: 'text-xs px-3 py-1.5 gap-1.5 h-8',
    md: 'text-sm px-4 py-2 gap-2 h-9 md:h-10',
    lg: 'text-base px-5 py-2.5 gap-2.5 h-11',
  };

  const variants = {
    primary: 'bg-primary text-on-primary hover:opacity-90 shadow-sm border border-transparent dark:hover:bg-slate-200',
    secondary: 'bg-surface-container text-on-surface hover:bg-surface-container-high border border-outline-variant/60',
    outline: 'bg-transparent text-on-surface border border-outline-variant hover:bg-surface-container hover:border-outline/40',
    ghost: 'bg-transparent text-on-surface-variant hover:text-on-surface hover:bg-surface-container',
    danger: 'bg-rose-500/10 text-rose-600 dark:text-rose-400 border border-rose-500/20 hover:bg-rose-500/20',
  };

  return (
    <button
      className={`${baseStyles} ${radius} ${sizes[size]} ${variants[variant]} ${className}`}
      disabled={disabled || loading}
      {...props}
    >
      {loading ? (
        <span className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin shrink-0" />
      ) : (
        icon && <span className="shrink-0 flex items-center">{icon}</span>
      )}
      <span>{children}</span>
    </button>
  );
};
