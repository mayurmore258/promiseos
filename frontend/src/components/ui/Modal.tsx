import React, { useEffect } from 'react';
import { X } from 'lucide-react';

export interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  description?: string;
  children: React.ReactNode;
  maxWidth?: 'sm' | 'md' | 'lg' | 'xl';
}

export const Modal: React.FC<ModalProps> = ({
  isOpen,
  onClose,
  title,
  description,
  children,
  maxWidth = 'md',
}) => {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    if (isOpen) {
      document.body.style.overflow = 'hidden';
      window.addEventListener('keydown', handleKeyDown);
    }
    return () => {
      document.body.style.overflow = 'unset';
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const maxWidths = {
    sm: 'max-w-md',
    md: 'max-w-lg',
    lg: 'max-w-2xl',
    xl: 'max-w-4xl',
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/50 backdrop-blur-sm transition-opacity"
        onClick={onClose}
      />

      {/* Modal Surface */}
      <div
        className={`relative w-full ${maxWidths[maxWidth]} bg-surface-container-lowest border border-outline-variant/80 rounded-2xl shadow-dropdown z-10 overflow-hidden flex flex-col max-h-[90vh] animate-in fade-in zoom-in-95 duration-150`}
      >
        <div className="flex items-start justify-between p-5 border-b border-outline-variant/60">
          <div>
            <h3 className="font-headline text-lg font-semibold text-on-surface">
              {title}
            </h3>
            {description && (
              <p className="text-xs text-on-surface-variant mt-0.5">
                {description}
              </p>
            )}
          </div>
          <button
            onClick={onClose}
            className="w-8 h-8 rounded-xl flex items-center justify-center text-on-surface-variant hover:text-on-surface hover:bg-surface-container transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="p-5 overflow-y-auto flex-1">{children}</div>
      </div>
    </div>
  );
};
