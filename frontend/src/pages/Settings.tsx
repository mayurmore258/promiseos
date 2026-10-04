import React, { useState } from 'react';
import { useTheme } from '../hooks/useTheme';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { 
  Sun, 
  Moon, 
  Sparkles, 
  Search, 
  Bell, 
  User, 
  LogOut, 
  Check,
  ShieldCheck
} from 'lucide-react';

export const Settings: React.FC = () => {
  const { theme, setTheme } = useTheme();

  // Settings states
  const [aiProvider, setAiProvider] = useState('auto');
  const [evidenceSearch, setEvidenceSearch] = useState(true);
  const [followupReminders, setFollowupReminders] = useState(true);
  const [verificationUpdates, setVerificationUpdates] = useState(true);
  const [savedNotice, setSavedNotice] = useState(false);

  const handleSave = () => {
    setSavedNotice(true);
    setTimeout(() => setSavedNotice(false), 2000);
  };

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex flex-col gap-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-headline text-2xl sm:text-3xl font-bold tracking-tight text-on-surface">
            Settings
          </h1>
          <p className="text-sm text-on-surface-variant mt-1">
            Manage your interface theme, AI verification preferences, and account parameters.
          </p>
        </div>

        {savedNotice && (
          <Badge variant="success" size="sm" className="animate-in fade-in">
            <Check className="w-3 h-3" />
            <span>Preferences saved</span>
          </Badge>
        )}
      </div>

      {/* 1. Appearance */}
      <Card className="flex flex-col gap-4">
        <div>
          <h2 className="font-headline text-base font-semibold text-on-surface">
            Appearance
          </h2>
          <p className="text-xs text-on-surface-variant mt-0.5">
            Select your preferred chromatic appearance across the app interface.
          </p>
        </div>

        <div className="grid grid-cols-2 gap-3 pt-1">
          <button
            onClick={() => setTheme('light')}
            className={`flex items-center gap-3 p-3.5 rounded-xl border text-left transition-all ${
              theme === 'light'
                ? 'border-secondary bg-secondary/5 ring-2 ring-secondary/20'
                : 'border-outline-variant hover:bg-surface-container'
            }`}
          >
            <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${
              theme === 'light' ? 'bg-secondary text-white' : 'bg-surface-container text-on-surface'
            }`}>
              <Sun className="w-4 h-4" />
            </div>
            <div>
              <p className="text-sm font-semibold text-on-surface">Light</p>
              <p className="text-[11px] text-on-surface-variant">Clean high-contrast</p>
            </div>
          </button>

          <button
            onClick={() => setTheme('dark')}
            className={`flex items-center gap-3 p-3.5 rounded-xl border text-left transition-all ${
              theme === 'dark'
                ? 'border-secondary bg-secondary/10 ring-2 ring-secondary/20'
                : 'border-outline-variant hover:bg-surface-container'
            }`}
          >
            <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${
              theme === 'dark' ? 'bg-secondary text-white' : 'bg-surface-container text-on-surface'
            }`}>
              <Moon className="w-4 h-4" />
            </div>
            <div>
              <p className="text-sm font-semibold text-on-surface">Dark</p>
              <p className="text-[11px] text-on-surface-variant">Deep OLED contrast</p>
            </div>
          </button>
        </div>
      </Card>

      {/* 2. AI Provider Routing */}
      <Card className="flex flex-col gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="font-headline text-base font-semibold text-on-surface">
              AI Verification
            </h2>
            <Badge variant="blue" size="sm">
              <Sparkles className="w-3 h-3" />
              <span>Multi-provider</span>
            </Badge>
          </div>
          <p className="text-xs text-on-surface-variant mt-0.5">
            Configure commitment detection engine and autonomous deliverable verification.
          </p>
        </div>

        <div className="flex flex-col gap-3 pt-1">
          <div className="flex items-center justify-between p-3.5 bg-surface-container rounded-xl">
            <div>
              <p className="text-sm font-semibold text-on-surface">Provider routing</p>
              <p className="text-xs text-on-surface-variant">
                Automatic fallback: Groq → NVIDIA → SambaNova → Gemini → OpenRouter
              </p>
            </div>
            <select
              value={aiProvider}
              onChange={(e) => {
                setAiProvider(e.target.value);
                handleSave();
              }}
              className="bg-surface-container-lowest text-on-surface border border-outline-variant/60 rounded-xl px-3 py-1.5 text-xs font-medium focus:outline-none focus:border-secondary"
            >
              <option value="auto">Automatic (Recommended)</option>
              <option value="groq">Groq (Llama 3.3 70B)</option>
              <option value="gemini">Google Gemini 1.5 Flash</option>
              <option value="nvidia">NVIDIA NIM</option>
              <option value="sambanova">SambaNova</option>
            </select>
          </div>
        </div>
      </Card>

      {/* 3. Evidence Search */}
      <Card className="flex flex-col gap-4">
        <div>
          <h2 className="font-headline text-base font-semibold text-on-surface">
            Evidence Pipeline
          </h2>
          <p className="text-xs text-on-surface-variant mt-0.5">
            Configure automated file discovery and semantic matching rules.
          </p>
        </div>

        <div className="flex items-center justify-between p-3.5 bg-surface-container rounded-xl">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-surface-container-lowest flex items-center justify-center text-secondary shrink-0">
              <Search className="w-4 h-4" />
            </div>
            <div>
              <p className="text-sm font-semibold text-on-surface">Semantic evidence search</p>
              <p className="text-xs text-on-surface-variant">
                Index uploaded deliverables and search across workspace attachments
              </p>
            </div>
          </div>

          <label className="relative inline-flex items-center cursor-pointer">
            <input
              type="checkbox"
              checked={evidenceSearch}
              onChange={(e) => {
                setEvidenceSearch(e.target.checked);
                handleSave();
              }}
              className="sr-only peer"
            />
            <div className="w-10 h-6 bg-outline-variant peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-secondary"></div>
          </label>
        </div>
      </Card>

      {/* 4. Notifications */}
      <Card className="flex flex-col gap-4">
        <div>
          <h2 className="font-headline text-base font-semibold text-on-surface">
            Notifications & Guardrails
          </h2>
          <p className="text-xs text-on-surface-variant mt-0.5">
            Follow-up reminders and human-in-the-loop review alerts.
          </p>
        </div>

        <div className="flex flex-col gap-2.5">
          <div className="flex items-center justify-between p-3.5 bg-surface-container rounded-xl">
            <div className="flex items-center gap-3">
              <Bell className="w-4 h-4 text-on-surface-variant" />
              <div>
                <p className="text-sm font-semibold text-on-surface">Follow-up reminders</p>
                <p className="text-xs text-on-surface-variant">
                  Prompt user when a commitment deadline approaches or passes
                </p>
              </div>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={followupReminders}
                onChange={(e) => {
                  setFollowupReminders(e.target.checked);
                  handleSave();
                }}
                className="sr-only peer"
              />
              <div className="w-10 h-6 bg-outline-variant peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-secondary"></div>
            </label>
          </div>

          <div className="flex items-center justify-between p-3.5 bg-surface-container rounded-xl">
            <div className="flex items-center gap-3">
              <ShieldCheck className="w-4 h-4 text-on-surface-variant" />
              <div>
                <p className="text-sm font-semibold text-on-surface">Verification updates</p>
                <p className="text-xs text-on-surface-variant">
                  Alert when an uploaded deliverable changes status to Fulfilled
                </p>
              </div>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={verificationUpdates}
                onChange={(e) => {
                  setVerificationUpdates(e.target.checked);
                  handleSave();
                }}
                className="sr-only peer"
              />
              <div className="w-10 h-6 bg-outline-variant peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-secondary"></div>
            </label>
          </div>
        </div>
      </Card>

      {/* 5. Account */}
      <Card className="flex flex-col gap-4">
        <div>
          <h2 className="font-headline text-base font-semibold text-on-surface">
            Account
          </h2>
          <p className="text-xs text-on-surface-variant mt-0.5">
            Active workspace member credentials and session.
          </p>
        </div>

        <div className="flex flex-col sm:flex-row sm:items-center justify-between p-4 bg-surface-container rounded-xl gap-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-slate-900 text-white dark:bg-slate-100 dark:text-slate-900 flex items-center justify-center font-semibold text-sm">
              <User className="w-5 h-5" />
            </div>
            <div>
              <p className="text-sm font-semibold text-on-surface">Alex Mercer</p>
              <p className="text-xs text-on-surface-variant">alex@promiseos.io • Admin</p>
            </div>
          </div>

          <Button
            variant="outline"
            size="sm"
            onClick={() => alert('Signed out for demo session.')}
            icon={<LogOut className="w-3.5 h-3.5" />}
          >
            Sign out
          </Button>
        </div>
      </Card>
    </div>
  );
};
