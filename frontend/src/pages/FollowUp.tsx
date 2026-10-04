import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { getCommitment, generateFollowUp, approveFollowUp } from '../services/api';
import { Commitment } from '../types/commitment';
import { FollowupDraftData } from '../types/verification';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Textarea } from '../components/ui/Textarea';
import { CommitmentStatusBadge } from '../components/commitments/CommitmentStatus';
import { 
  ArrowLeft, 
  ShieldCheck, 
  Send, 
  Copy, 
  Check, 
  RefreshCw, 
  Edit3, 
  CheckCircle2 
} from 'lucide-react';

export const FollowUp: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [commitment, setCommitment] = useState<Commitment | null>(null);
  const [draftData, setDraftData] = useState<FollowupDraftData | null>(null);
  const [message, setMessage] = useState('');
  const [copied, setCopied] = useState(false);
  const [approved, setApproved] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      if (!id) return;
      setLoading(true);
      try {
        const c = await getCommitment(id);
        setCommitment(c);
        if (c) {
          const draft = await generateFollowUp(c.id);
          setDraftData(draft);
          setMessage(draft.draft);
          setApproved(draft.approved);
        }
      } catch (err) {
        console.error('Failed to load followup draft:', err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [id]);

  const handleCopy = () => {
    navigator.clipboard.writeText(message);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleApprove = async () => {
    if (!id) return;
    setSubmitting(true);
    try {
      await approveFollowUp(id, message);
      setApproved(true);
    } finally {
      setSubmitting(false);
    }
  };

  const handleRegenerate = async () => {
    if (!commitment) return;
    setLoading(true);
    try {
      const regenerated = `Hi ${commitment.person}, following up on the ${commitment.action.toLowerCase()}. The initial deliverables have been processed, but a few items remain outstanding. Could you share an update when you have a moment?`;
      setMessage(regenerated);
      setApproved(false);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-16 flex flex-col items-center justify-center">
        <span className="w-6 h-6 border-2 border-secondary border-t-transparent rounded-full animate-spin mb-3" />
        <p className="text-xs text-on-surface-variant">Generating follow-up draft...</p>
      </div>
    );
  }

  if (!commitment || !draftData) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-16 text-center">
        <h2 className="text-lg font-semibold text-on-surface">Commitment not found</h2>
        <Button variant="outline" size="sm" onClick={() => navigate('/commitments')} className="mt-4">
          Back to commitments
        </Button>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex flex-col gap-6">
      {/* Back button */}
      <div>
        <Link
          to={`/commitments/${commitment.id}`}
          className="inline-flex items-center gap-1.5 text-xs font-medium text-on-surface-variant hover:text-on-surface transition-colors"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Back to commitment details</span>
        </Link>
      </div>

      {/* Header */}
      <div>
        <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-blue-500/10 text-secondary text-xs font-semibold mb-2">
          <ShieldCheck className="w-3.5 h-3.5" />
          <span>Human-in-the-Loop Review</span>
        </div>
        <h1 className="font-headline text-2xl sm:text-3xl font-bold tracking-tight text-on-surface">
          Review follow-up
        </h1>
        <p className="text-sm text-on-surface-variant mt-1">
          Review the generated reconciliation prompt before dispatching to the counterparty.
        </p>
      </div>

      {/* Main Review Card */}
      <Card className="flex flex-col gap-5">
        {/* Commitment Summary Bar */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between p-4 bg-surface-container rounded-xl gap-3">
          <div className="flex flex-col gap-1">
            <div className="flex items-center gap-2">
              <span className="text-xs text-on-surface-variant font-medium">Recipient:</span>
              <span className="text-xs font-semibold text-on-surface">{commitment.person}</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-xs text-on-surface-variant font-medium">Deliverable:</span>
              <span className="text-xs font-semibold text-on-surface truncate max-w-xs">{commitment.action}</span>
            </div>
          </div>

          <div className="flex items-center gap-2 self-start sm:self-auto">
            <span className="text-xs text-on-surface-variant">Status:</span>
            <CommitmentStatusBadge status={commitment.status} size="sm" />
          </div>
        </div>

        {/* Safety Guardrail Callout */}
        <div className="p-3.5 bg-secondary/5 border border-secondary/20 rounded-xl flex items-start gap-3">
          <ShieldCheck className="w-4 h-4 text-secondary shrink-0 mt-0.5" />
          <div className="text-xs text-on-surface-variant leading-relaxed">
            <span className="font-semibold text-on-surface">Safety Guardrail Active: </span>
            PromiseOS never sends messages automatically. Please review, edit if necessary, and explicitly approve before dispatching.
          </div>
        </div>

        {/* Editable Message Box */}
        <div className="flex flex-col gap-2">
          <div className="flex items-center justify-between">
            <label className="text-xs font-semibold text-on-surface-variant uppercase tracking-wider flex items-center gap-1.5">
              <Edit3 className="w-3.5 h-3.5" />
              <span>Follow-up Message (Editable)</span>
            </label>
            <button
              onClick={handleCopy}
              className="text-xs text-secondary hover:underline flex items-center gap-1"
            >
              {copied ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
              <span>{copied ? 'Copied!' : 'Copy text'}</span>
            </button>
          </div>

          <Textarea
            rows={5}
            value={message}
            onChange={(e) => {
              setMessage(e.target.value);
              setApproved(false);
            }}
            className="font-sans text-sm leading-relaxed"
          />
        </div>

        {/* Approved State Banner */}
        {approved && (
          <div className="p-3.5 bg-emerald-500/10 border border-emerald-500/20 rounded-xl flex items-center gap-2.5 text-xs text-emerald-800 dark:text-emerald-300 font-medium">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
            <span>This follow-up draft has been approved and staged for dispatch.</span>
          </div>
        )}

        {/* Footer actions */}
        <div className="flex items-center justify-between pt-3 border-t border-outline-variant/60">
          <Button
            variant="outline"
            size="sm"
            onClick={handleRegenerate}
            icon={<RefreshCw className="w-3.5 h-3.5" />}
          >
            Regenerate draft
          </Button>

          <Button
            variant="primary"
            onClick={handleApprove}
            loading={submitting}
            disabled={approved}
            icon={<Send className="w-3.5 h-3.5" />}
          >
            {approved ? 'Approved & Ready' : 'Approve & Stage'}
          </Button>
        </div>
      </Card>
    </div>
  );
};
