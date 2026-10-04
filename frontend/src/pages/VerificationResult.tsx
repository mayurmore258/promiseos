import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { getCommitment, verifyCommitment } from '../services/api';
import { Commitment } from '../types/commitment';
import { VerificationResultData } from '../types/verification';
import { VerificationResult as VerificationResultView } from '../components/verification/VerificationResult';
import { Button } from '../components/ui/Button';
import { ArrowLeft } from 'lucide-react';

export const VerificationResultPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [commitment, setCommitment] = useState<Commitment | null>(null);
  const [result, setResult] = useState<VerificationResultData | null>(null);
  const [loading, setLoading] = useState(true);
  const [reverifying, setReverifying] = useState(false);

  useEffect(() => {
    async function load() {
      if (!id) return;
      setLoading(true);
      try {
        const c = await getCommitment(id);
        setCommitment(c);
        if (c) {
          const v = await verifyCommitment(c.id);
          setResult(v);
          setCommitment((prev) => (prev ? { ...prev, status: v.status } : null));
        }
      } catch (err) {
        console.error('Failed to load verification:', err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [id]);

  const handleVerifyAgain = async () => {
    if (!id) return;
    setReverifying(true);
    try {
      const v = await verifyCommitment(id);
      setResult(v);
      setCommitment((prev) => (prev ? { ...prev, status: v.status } : null));
    } finally {
      setReverifying(false);
    }
  };

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-16 flex flex-col items-center justify-center">
        <span className="w-6 h-6 border-2 border-secondary border-t-transparent rounded-full animate-spin mb-3" />
        <p className="text-xs text-on-surface-variant">Loading verification results...</p>
      </div>
    );
  }

  if (!commitment || !result) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-16 text-center">
        <h2 className="text-lg font-semibold text-on-surface">Verification not found</h2>
        <p className="text-xs text-on-surface-variant mt-1">
          No verification record found for this commitment ID.
        </p>
        <Button variant="outline" size="sm" onClick={() => navigate('/commitments')} className="mt-4">
          Back to commitments
        </Button>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex flex-col gap-6">
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

      {/* Page Title */}
      <div>
        <h1 className="font-headline text-2xl sm:text-3xl font-bold tracking-tight text-on-surface">
          Verification result
        </h1>
        <p className="text-sm text-on-surface-variant mt-1">
          Full audit and deliverable comparison for this commitment.
        </p>
      </div>

      {/* Main Verification View Component */}
      <VerificationResultView
        commitment={commitment}
        result={result}
        onVerifyAgain={handleVerifyAgain}
        loading={reverifying}
      />
    </div>
  );
};
