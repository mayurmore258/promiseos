import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Settings as SettingsIcon, Menu, X, User } from 'lucide-react';
import { Navigation } from './Navigation';
import { ThemeToggle } from '../ui/ThemeToggle';

export const Header: React.FC = () => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [profileDropdownOpen, setProfileDropdownOpen] = useState(false);
  const navigate = useNavigate();

  return (
    <header className="sticky top-0 z-40 bg-surface-container-lowest/90 backdrop-blur-md border-b border-outline-variant/60 shadow-xs">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-14 flex items-center justify-between gap-4">
        {/* Brand & Desktop Navigation */}
        <div className="flex items-center gap-6 md:gap-8">
          <Link to="/dashboard" className="flex items-center gap-2.5 group">
            <div className="w-8 h-8 rounded-xl bg-slate-900 dark:bg-white flex items-center justify-center shrink-0 shadow-xs">
              <svg width="20" height="20" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="20" cy="20" r="12" stroke="#3B82F6" strokeWidth="3" strokeDasharray="75" strokeDashoffset="18"/>
                <path d="M15 20.5L18.5 24L25.5 16.5" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" className="text-white dark:text-slate-950"/>
              </svg>
            </div>
            <span className="font-headline text-base font-semibold tracking-tight text-on-surface group-hover:text-secondary transition-colors">
              PromiseOS
            </span>
          </Link>

          <div className="hidden md:flex items-center">
            <Navigation />
          </div>
        </div>

        {/* Right Actions: Theme Toggle & Profile */}
        <div className="flex items-center gap-2">
          <ThemeToggle />

          {/* Profile / Settings Button */}
          <div className="relative">
            <button
              onClick={() => setProfileDropdownOpen(!profileDropdownOpen)}
              className="flex items-center gap-2 p-1 pl-1.5 pr-2.5 rounded-full hover:bg-surface-container transition-colors text-left"
              aria-label="User menu"
            >
              <div className="w-7 h-7 rounded-full bg-slate-900 text-white dark:bg-slate-100 dark:text-slate-900 flex items-center justify-center text-xs font-semibold shrink-0">
                <User className="w-3.5 h-3.5" />
              </div>
              <span className="text-xs font-medium text-on-surface hidden sm:inline-block">
                Alex M.
              </span>
            </button>

            {/* Profile Dropdown */}
            {profileDropdownOpen && (
              <>
                <div
                  className="fixed inset-0 z-40"
                  onClick={() => setProfileDropdownOpen(false)}
                />
                <div className="absolute right-0 mt-2 w-48 bg-surface-container-lowest border border-outline-variant rounded-xl shadow-dropdown py-1.5 z-50 animate-in fade-in zoom-in-95 duration-100">
                  <div className="px-3 py-2 border-b border-outline-variant/60">
                    <p className="text-xs font-medium text-on-surface">Alex Mercer</p>
                    <p className="text-[11px] text-on-surface-variant truncate">alex@promiseos.io</p>
                  </div>
                  <button
                    onClick={() => {
                      setProfileDropdownOpen(false);
                      navigate('/settings');
                    }}
                    className="w-full text-left px-3 py-2 text-xs text-on-surface hover:bg-surface-container flex items-center gap-2 transition-colors"
                  >
                    <SettingsIcon className="w-3.5 h-3.5 text-on-surface-variant" />
                    <span>Settings</span>
                  </button>
                  <button
                    onClick={() => {
                      setProfileDropdownOpen(false);
                      navigate('/dashboard');
                    }}
                    className="w-full text-left px-3 py-2 text-xs text-rose-600 dark:text-rose-400 hover:bg-rose-500/10 transition-colors"
                  >
                    Sign out
                  </button>
                </div>
              </>
            )}
          </div>

          {/* Mobile hamburger toggle */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="md:hidden w-9 h-9 rounded-xl flex items-center justify-center text-on-surface-variant hover:text-on-surface hover:bg-surface-container transition-colors ml-1"
            aria-label="Open menu"
          >
            {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>
      </div>

      {/* Mobile Drawer */}
      {mobileMenuOpen && (
        <div className="md:hidden border-t border-outline-variant/60 bg-surface-container-lowest px-4 py-3 shadow-card animate-in slide-in-from-top-2 duration-150">
          <Navigation mobile onItemClick={() => setMobileMenuOpen(false)} />
          <div className="mt-3 pt-3 border-t border-outline-variant/60">
            <Link
              to="/settings"
              onClick={() => setMobileMenuOpen(false)}
              className="flex items-center gap-2.5 px-4 py-2 text-xs font-medium text-on-surface-variant hover:text-on-surface rounded-xl hover:bg-surface-container transition-colors"
            >
              <SettingsIcon className="w-4 h-4" />
              <span>Settings</span>
            </Link>
          </div>
        </div>
      )}
    </header>
  );
};
