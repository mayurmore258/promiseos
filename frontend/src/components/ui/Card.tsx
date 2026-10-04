import React from 'react';

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  hover?: boolean;
  border?: boolean;
}

export const Card: React.FC<CardProps> = ({
  children,
  className = '',
  hover = false,
  border = true,
  ...props
}) => {
  return (
    <div
      className={`bg-surface-container-lowest rounded-2xl p-5 md:p-6 shadow-subtle ${
        border ? 'border border-outline-variant/60 dark:border-outline-variant/40' : ''
      } ${
        hover ? 'hover:shadow-card hover:border-outline-variant transition-all duration-200' : ''
      } ${className}`}
      {...props}
    >
      {children}
    </div>
  );
};
