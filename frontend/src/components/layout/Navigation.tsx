import React from 'react';
import { NavLink } from 'react-router-dom';

interface NavigationProps {
  mobile?: boolean;
  onItemClick?: () => void;
}

export const Navigation: React.FC<NavigationProps> = ({ mobile = false, onItemClick }) => {
  const navItems = [
    { label: 'Dashboard', path: '/dashboard' },
    { label: 'Analyze', path: '/analyze' },
    { label: 'Commitments', path: '/commitments' },
    { label: 'Evidence', path: '/evidence' },
  ];

  return (
    <nav className={`flex ${mobile ? 'flex-col space-y-1 w-full' : 'items-center gap-1.5'}`}>
      {navItems.map((item) => (
        <NavLink
          key={item.path}
          to={item.path}
          onClick={onItemClick}
          className={({ isActive }) =>
            `px-3.5 py-1.5 rounded-full text-xs font-medium transition-all ${
              isActive
                ? 'bg-surface-container text-on-surface font-semibold shadow-xs'
                : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container/60'
            } ${mobile ? 'text-sm py-2.5 px-4 w-full rounded-xl' : ''}`
          }
        >
          {item.label}
        </NavLink>
      ))}
    </nav>
  );
};
