import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getCommitments } from '../services/api';
import { Commitment } from '../types/commitment';
import { CommitmentCard } from '../components/commitments/CommitmentCard';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Plus, Search, CheckCircle2, Clock, AlertTriangle, Layers } from 'lucide-react';

export const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [commitments, setCommitments] = useState<Commitment[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeFilter, setActiveFilter] = useState<'all' | 'fulfilled' | 'pending' | 'review'>('all');
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      try {
        const data = await getCommitments();
        setCommitments(data);
      } catch (err) {
        console.error('Failed to load commitments:', err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  // Compute stats
  const totalCount = commitments.length;
  const fulfilledCount = commitments.filter((c) => c.status === 'FULFILLED').length;
  const pendingCount = commitments.filter(
    (c) => c.status === 'PARTIALLY_FULFILLED' || c.status === 'UNVERIFIED'
  ).length;
  const needReviewCount = commitments.filter(
    (c) => c.status === 'UNFULFILLED' || c.status === 'CONTRADICTORY'
  ).length;

  // Filtered commitments
  const filteredCommitments = commitments.filter((item) => {
    const matchesSearch =
      item.person.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.action.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.deadline.toLowerCase().includes(searchQuery.toLowerCase());

    if (!matchesSearch) return false;

    if (activeFilter === 'all') return true;
    if (activeFilter === 'fulfilled') return item.status === 'FULFILLED';
    if (activeFilter === 'pending') {
      return item.status === 'PARTIALLY_FULFILLED' || item.status === 'UNVERIFIED';
    }
    if (activeFilter === 'review') {
      return item.status === 'UNFULFILLED' || item.status === 'CONTRADICTORY';
    }
    return true;
  });

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex flex-col gap-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="font-headline text-2xl sm:text-3xl font-bold tracking-tight text-on-surface">
            Your commitments
          </h1>
          <p className="text-sm text-on-surface-variant mt-1">
            Track what was promised and what actually happened.
          </p>
        </div>

        <Button
          variant="primary"
          onClick={() => navigate('/analyze')}
          icon={<Plus className="w-4 h-4" />}
          className="self-start sm:self-auto"
        >
          New analysis
        </Button>
      </div>

      {/* Summary Stat Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {/* Total */}
        <Card className="flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-on-surface-variant">Total commitments</span>
            <Layers className="w-4 h-4 text-on-surface-variant/70" />
          </div>
          <div className="flex items-baseline justify-between mt-4">
            <span className="font-headline text-2xl md:text-3xl font-bold text-on-surface leading-none">
              {totalCount}
            </span>
            <span className="text-[11px] font-semibold text-on-surface-variant bg-surface-container px-2 py-0.5 rounded-full">
              All active
            </span>
          </div>
        </Card>

        {/* Fulfilled */}
        <Card className="flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-on-surface-variant">Fulfilled</span>
            <CheckCircle2 className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
          </div>
          <div className="flex items-baseline justify-between mt-4">
            <span className="font-headline text-2xl md:text-3xl font-bold text-on-surface leading-none">
              {fulfilledCount}
            </span>
            <span className="text-[11px] font-semibold text-emerald-700 dark:text-emerald-300 bg-emerald-500/10 px-2 py-0.5 rounded-full">
              {totalCount > 0 ? `${Math.round((fulfilledCount / totalCount) * 100)}% done` : '0%'}
            </span>
          </div>
        </Card>

        {/* Pending */}
        <Card className="flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-on-surface-variant">Pending</span>
            <Clock className="w-4 h-4 text-blue-600 dark:text-blue-400" />
          </div>
          <div className="flex items-baseline justify-between mt-4">
            <span className="font-headline text-2xl md:text-3xl font-bold text-on-surface leading-none">
              {pendingCount}
            </span>
            <span className="text-[11px] font-semibold text-blue-700 dark:text-blue-300 bg-blue-500/10 px-2 py-0.5 rounded-full">
              In flight
            </span>
          </div>
        </Card>

        {/* Need Review */}
        <Card className="flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-on-surface-variant">Need Review</span>
            <AlertTriangle className="w-4 h-4 text-rose-600 dark:text-rose-400" />
          </div>
          <div className="flex items-baseline justify-between mt-4">
            <span className="font-headline text-2xl md:text-3xl font-bold text-rose-600 dark:text-rose-400 leading-none">
              {needReviewCount}
            </span>
            <span className="text-[11px] font-semibold text-rose-700 dark:text-rose-300 bg-rose-500/10 px-2 py-0.5 rounded-full">
              Attention
            </span>
          </div>
        </Card>
      </div>

      {/* Filter Tabs & Search Bar */}
      <Card className="p-3 sm:p-3.5 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="flex flex-wrap items-center gap-1.5">
          <button
            onClick={() => setActiveFilter('all')}
            className={`px-3 py-1.5 rounded-xl text-xs font-medium transition-all ${
              activeFilter === 'all'
                ? 'bg-primary text-on-primary'
                : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container'
            }`}
          >
            All ({totalCount})
          </button>
          <button
            onClick={() => setActiveFilter('fulfilled')}
            className={`px-3 py-1.5 rounded-xl text-xs font-medium transition-all ${
              activeFilter === 'fulfilled'
                ? 'bg-primary text-on-primary'
                : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container'
            }`}
          >
            Fulfilled ({fulfilledCount})
          </button>
          <button
            onClick={() => setActiveFilter('pending')}
            className={`px-3 py-1.5 rounded-xl text-xs font-medium transition-all ${
              activeFilter === 'pending'
                ? 'bg-primary text-on-primary'
                : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container'
            }`}
          >
            Pending ({pendingCount})
          </button>
          <button
            onClick={() => setActiveFilter('review')}
            className={`px-3 py-1.5 rounded-xl text-xs font-medium transition-all ${
              activeFilter === 'review'
                ? 'bg-primary text-on-primary'
                : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container'
            }`}
          >
            Need Review ({needReviewCount})
          </button>
        </div>

        <div className="w-full sm:w-64">
          <Input
            placeholder="Filter commitments..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            icon={<Search className="w-4 h-4 text-on-surface-variant" />}
          />
        </div>
      </Card>

      {/* Commitment List */}
      <div className="flex flex-col gap-3">
        {loading ? (
          <div className="flex flex-col items-center justify-center p-12 bg-surface-container-lowest rounded-2xl border border-outline-variant/60">
            <span className="w-6 h-6 border-2 border-secondary border-t-transparent rounded-full animate-spin mb-3" />
            <p className="text-xs text-on-surface-variant">Loading commitments...</p>
          </div>
        ) : filteredCommitments.length === 0 ? (
          <div className="flex flex-col items-center justify-center p-12 bg-surface-container-lowest rounded-2xl border border-outline-variant/60 text-center">
            <Layers className="w-8 h-8 text-on-surface-variant/60 mb-2" />
            <h3 className="font-headline text-sm font-semibold text-on-surface">
              No commitments found
            </h3>
            <p className="text-xs text-on-surface-variant mt-1 max-w-sm">
              {searchQuery
                ? 'No commitments match your search criteria. Try a different search term.'
                : 'You have no commitments in this filter category.'}
            </p>
          </div>
        ) : (
          filteredCommitments.map((commitment) => (
            <CommitmentCard key={commitment.id} commitment={commitment} />
          ))
        )}
      </div>
    </div>
  );
};
