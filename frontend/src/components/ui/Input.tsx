import React from 'react';

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  icon?: React.ReactNode;
}

export const Input: React.FC<InputProps> = ({
  icon,
  className = '',
  ...props
}) => {
  return (
    <div className="relative flex items-center w-full">
      {icon && (
        <span className="absolute left-3.5 text-on-surface-variant pointer-events-none flex items-center">
          {icon}
        </span>
      )}
      <input
        className={`w-full bg-surface-container-low text-on-surface placeholder:text-on-surface-variant/70 border border-outline-variant/60 rounded-xl px-3.5 py-2 text-sm transition-all focus:outline-none focus:border-secondary focus:bg-surface-container-lowest focus:ring-2 focus:ring-secondary/15 ${
          icon ? 'pl-10' : ''
        } ${className}`}
        {...props}
      />
    </div>
  );
};
