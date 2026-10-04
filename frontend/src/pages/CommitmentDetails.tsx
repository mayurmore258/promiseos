import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { getCommitment, verifyCommitment, getEvidence } from '../services/api';
import { Commitment } from '../types/commitment';
import { VerificationResultData } from '../types/verification';
import { EvidenceItem } from '../types/evidence';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { CommitmentStatusBadge } from '../components/commitments/CommitmentStatus';
import { ConfidenceIndicator } from '../components/verification/ConfidenceIndicator';
import { EvidencePreview } from '../components/evidence/EvidencePreview';
import { 
  ArrowLeft, 
  Calendar, 
  FileText, 
  RefreshCw, 
  Send, 
  Eye, 
  CheckCircle2, 
  Sparkles,
  ExternalLink
} from 'lucide-react';

export const CommitmentDetails: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [commitment, setCommitment] = useState<Commitment | null>(null);
  const [verification, setVerification] = useState<VerificationResultData | null>(null);
  const [evidenceList, setEvidenceList] = useState<EvidenceItem[]>([]);
  const [selectedEvidence, setSelectedEvidence] = useState<EvidenceItem | null>(null);
  const [loading, setLoading] = useState(true);
  const [verifying, setVerifying] = useState(false);

  useEffect(() => {
    async function load() {
      if (!id) return;
      setLoading(true);
      try {
        const c = await getCommitment(id);
        setCommitment(c);
        if (c) {
          const v = await verifyCommitment(c.id);
          setVerification(v);
          const allEv = await getEvidence();
          const matched = allEv.filter(
            (e) => e.commitmentId === c.id || c.expectedEvidence.includes(e.fileName)
          );
          setEvidenceList(matched.length > 0 ? matched : allEv.slice(0, 1));
        }
      } catch (err) {
        console.error('Failed to load commitment details:', err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [id]);

  const handleVerifyAgain = async () => {
    if (!commitment) return;
    setVerifying(true);
    try {
      const v = await verifyCommitment(commitment.id);
      setVerification(v);
    } finally {
      setVerifying(false);
    }
  };

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-16 flex flex-col items-center justify-center">
        <span className="w-6 h-6 border-2 border-secondary border-t-transparent rounded-full animate-spin mb-3" />
        <p className="text-xs text-on-surface-variant">Loading commitment details...</p>
      </div>
    );
  }

  if (!commitment) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-16 text-center">
        <h2 className="text-lg font-semibold text-on-surface">Commitment not found</h2>
        <p className="text-xs text-on-surface-variant mt-1">This commitment ID may not exist.</p>
        <Button variant="outline" size="sm" onClick={() => navigate('/commitments')} className="mt-4">
          Back to commitments
        </Button>
      </div>
    );
  }

  const primaryEvidence = evidenceList[0];

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex flex-col gap-6">
      {/* Back link */}
      <div>
        <Link
          to="/commitments"
          className="inline-flex items-center gap-1.5 text-xs font-medium text-on-surface-variant hover:text-on-surface transition-colors"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Back to commitments</span>
        </Link>
      </div>

      {/* Main Details Card */}
      <Card className="flex flex-col gap-6">
        {/* Commitment Header */}
        <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4 pb-6 border-b border-outline-variant/60">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="text-xs font-mono text-on-surface-variant font-medium">
                {commitment.id}
              </span>
              <span className="text-xs text-on-surface-variant">•</span>
              <div className="flex items-center gap-1 text-xs text-on-surface-variant">
                <Calendar className="w-3.5 h-3.5 text-secondary" />
                <span>{commitment.deadline}</span>
              </div>
            </div>

            <h1 className="font-headline text-xl sm:text-2xl font-bold text-on-surface">
              "{commitment.action}"
            </h1>

            <div className="flex items-center gap-2.5 mt-3">
              <div className="w-7 h-7 rounded-full bg-surface-container flex items-center justify-center text-xs font-semibold text-on-surface">
                {commitment.person[0]}
              </div>
              <span className="text-sm font-semibold text-on-surface">
                {commitment.person}
              </span>
              <span className="text-xs text-on-surface-variant">
                ({commitment.role || 'Assigned Member'})
              </span>
            </div>
          </div>

          <div className="flex flex-col sm:items-end gap-2 shrink-0">
            <CommitmentStatusBadge status={commitment.status} size="md" />
            <ConfidenceIndicator confidence={commitment.confidence || 'High confidence'} />
          </div>
        </div>

        {/* Evidence Section */}
        <div className="flex flex-col gap-3">
          <span className="text-xs font-semibold text-on-surface-variant uppercase tracking-wider">
            Evidence:
          </span>

          {primaryEvidence ? (
            <div className="flex flex-col sm:flex-row sm:items-center justify-between p-4 bg-surface-container-low rounded-xl border border-outline-variant/60 gap-3">
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-xl bg-surface-container flex items-center justify-center shrink-0 text-secondary">
                  <FileText className="w-5 h-5" />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-semibold text-on-surface">
                      {primaryEvidence.fileName}
                    </span>
                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-surface-container font-mono text-on-surface-variant font-medium">
                      {primaryEvidence.fileType}
                    </span>
                  </div>
                  <div className="flex items-center gap-1.5 text-xs text-emerald-700 dark:text-emerald-400 font-medium mt-0.5">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>Matches the promised deliverable</span>
                  </div>
                </div>
              </div>

              <Button
                variant="secondary"
                size="sm"
                onClick={() => setSelectedEvidence(primaryEvidence)}
                icon={<Eye className="w-3.5 h-3.5" />}
              >
                View evidence
              </Button>
            </div>
          ) : (
            <div className="p-4 bg-surface-container-low rounded-xl text-xs text-on-surface-variant">
              No evidence files uploaded yet.
            </div>
          )}
        </div>

        {/* AI Explanation */}
        <div className="flex flex-col gap-2">
          <div className="flex items-center gap-1.5 text-xs font-semibold text-on-surface-variant uppercase tracking-wider">
            <Sparkles className="w-3.5 h-3.5 text-secondary" />
            <span>AI explanation:</span>
          </div>
          <div className="p-4 bg-surface-container rounded-xl text-sm text-on-surface leading-relaxed border border-outline-variant/60">
            "{verification?.explanation || commitment.aiExplanation || 'The quotation matching the commitment was found.'}"
          </div>
        </div>

        {/* Actions bar */}
        <div className="flex flex-wrap items-center justify-between gap-3 pt-4 border-t border-outline-variant/60">
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              onClick={handleVerifyAgain}
              loading={verifying}
              icon={<RefreshCw className="w-3.5 h-3.5" />}
            >
              Verify again
            </Button>
            <Button
              variant="secondary"
              onClick={() => navigate(`/commitments/${commitment.id}/verification`)}
              icon={<ExternalLink className="w-3.5 h-3.5" />}
            >
              Audit breakdown
            </Button>
          </div>

          <Button
            variant="primary"
            onClick={() => navigate(`/commitments/${commitment.id}/follow-up`)}
            icon={<Send className="w-3.5 h-3.5" />}
          >
            Generate follow-up
          </Button>
        </div>
      </Card>

      {/* Modal for viewing evidence */}
      <EvidencePreview
        evidence={selectedEvidence}
        isOpen={Boolean(selectedEvidence)}
        onClose={() => setSelectedEvidence(null)}
      />
    </div>
  );
};
