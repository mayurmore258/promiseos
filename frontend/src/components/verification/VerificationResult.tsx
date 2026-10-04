import React from 'react';
import { useNavigate } from 'react-router-dom';
import { VerificationResultData } from '../../types/verification';
import { Commitment } from '../../types/commitment';
import { CommitmentStatusBadge } from '../commitments/CommitmentStatus';
import { ConfidenceIndicator } from './ConfidenceIndicator';
import { Card } from '../ui/Card';
import { Button } from '../ui/Button';
import { FileText, RefreshCw, Send, AlertCircle, CheckCircle2 } from 'lucide-react';

interface VerificationResultProps {
  commitment: Commitment;
  result: VerificationResultData;
  onVerifyAgain?: () => void;
  loading?: boolean;
}

export const VerificationResult: React.FC<VerificationResultProps> = ({
  commitment,
  result,
  onVerifyAgain,
  loading = false,
}) => {
  const navigate = useNavigate();

  const progressPercent = result.totalItemsCount > 0
    ? Math.round((result.completedItemsCount / result.totalItemsCount) * 100)
    : 100;

  return (
    <div className="flex flex-col gap-6 max-w-4xl mx-auto">
      {/* Commitment Header */}
      <Card>
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-outline-variant/60">
          <div>
            <div className="flex items-center gap-2 mb-1.5">
              <span className="text-xs font-mono text-on-surface-variant">
                {commitment.id}
              </span>
              <span className="text-xs text-on-surface-variant">•</span>
              <span className="text-xs text-on-surface-variant font-medium">
                {commitment.deadline}
              </span>
            </div>
            <h1 className="font-headline text-xl md:text-2xl font-semibold text-on-surface">
              "{commitment.action}"
            </h1>
            <p className="text-xs text-on-surface-variant mt-1">
              Promised by <span className="font-medium text-on-surface">{commitment.person}</span> ({commitment.role || 'Assigned Member'})
            </p>
          </div>

          <div className="flex flex-col sm:flex-row items-start sm:items-center gap-2.5">
            <CommitmentStatusBadge status={result.status} size="md" />
            <ConfidenceIndicator confidence={`${result.confidence} confidence`} />
          </div>
        </div>

        {/* Verification Summary / Explanation */}
        <div className="py-5 flex flex-col gap-5">
          {/* AI Explanation Box */}
          <div className="p-4 bg-surface-container rounded-xl border border-outline-variant/60">
            <span className="text-xs font-semibold text-on-surface-variant uppercase tracking-wider block mb-1">
              AI Verification Explanation:
            </span>
            <p className="text-sm text-on-surface leading-relaxed">
              {result.explanation}
            </p>
          </div>

          {/* Progress Indicator */}
          {result.totalItemsCount > 1 && (
            <div className="flex flex-col gap-2">
              <div className="flex items-center justify-between text-xs">
                <span className="font-medium text-on-surface">
                  {result.completedItemsCount} of {result.totalItemsCount} promised items completed
                </span>
                <span className="font-semibold text-secondary">{progressPercent}%</span>
              </div>
              <div className="w-full h-2 rounded-full bg-surface-container overflow-hidden">
                <div
                  className="h-full bg-secondary rounded-full transition-all duration-500"
                  style={{ width: `${progressPercent}%` }}
                />
              </div>
            </div>
          )}

          {/* Evidence Found */}
          {result.evidence && result.evidence.length > 0 && (
            <div className="flex flex-col gap-2">
              <span className="text-xs font-semibold text-on-surface-variant uppercase tracking-wider">
                Evidence Found:
              </span>
              <div className="flex flex-wrap gap-2">
                {result.evidence.map((ev, index) => (
                  <div
                    key={index}
                    className="inline-flex items-center gap-2 px-3 py-1.5 rounded-xl bg-surface-container-low border border-outline-variant/60 text-xs font-medium text-on-surface"
                  >
                    <FileText className="w-3.5 h-3.5 text-secondary" />
                    <span>{ev}</span>
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Missing Items */}
          {result.missingItems && result.missingItems.length > 0 && (
            <div className="flex flex-col gap-2 p-4 bg-amber-500/10 border border-amber-500/20 rounded-xl">
              <div className="flex items-center gap-1.5 text-amber-800 dark:text-amber-300 font-semibold text-xs">
                <AlertCircle className="w-4 h-4" />
                <span>Missing Deliverables:</span>
              </div>
              <ul className="list-disc list-inside text-xs text-on-surface space-y-1 pl-1">
                {result.missingItems.map((item, index) => (
                  <li key={index} className="text-amber-900 dark:text-amber-200">
                    {item}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Contradictions */}
          {result.contradictions && result.contradictions.length > 0 && (
            <div className="flex flex-col gap-2 p-4 bg-rose-500/10 border border-rose-500/20 rounded-xl">
              <div className="flex items-center gap-1.5 text-rose-800 dark:text-rose-300 font-semibold text-xs">
                <AlertCircle className="w-4 h-4" />
                <span>Contradictions Identified:</span>
              </div>
              <ul className="list-disc list-inside text-xs text-on-surface space-y-1 pl-1">
                {result.contradictions.map((c, index) => (
                  <li key={index} className="text-rose-900 dark:text-rose-200">
                    {c}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {/* Primary Action Buttons */}
        <div className="flex flex-wrap items-center justify-between gap-3 pt-4 border-t border-outline-variant/60">
          <Button
            variant="outline"
            onClick={onVerifyAgain}
            loading={loading}
            icon={<RefreshCw className="w-4 h-4" />}
          >
            Verify again
          </Button>

          <Button
            variant="primary"
            onClick={() => navigate(`/commitments/${commitment.id}/follow-up`)}
            icon={<Send className="w-4 h-4" />}
          >
            Generate follow-up
          </Button>
        </div>
      </Card>
    </div>
  );
};
