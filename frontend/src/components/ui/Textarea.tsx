import React from 'react';

export interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  error?: string;
}

export const Textarea: React.FC<TextareaProps> = ({
  label,
  error,
  className = '',
  ...props
}) => {
  return (
    <div className="flex flex-col gap-1.5 w-full">
      {label && (
        <label className="text-xs font-medium text-on-surface-variant">
          {label}
        </label>
      )}
      <textarea
        className={`w-full bg-surface-container-low text-on-surface placeholder:text-on-surface-variant/70 border border-outline-variant/60 rounded-xl p-3.5 text-sm transition-all focus:outline-none focus:border-secondary focus:bg-surface-container-lowest focus:ring-2 focus:ring-secondary/15 resize-y ${
          error ? 'border-rose-500' : ''
        } ${className}`}
        {...props}
      />
      {error && <span className="text-xs text-rose-500">{error}</span>}
    </div>
  );
};
