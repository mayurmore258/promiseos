import React, { useState, useEffect } from 'react';
import { getCommitments } from '../services/api';
import { Commitment } from '../types/commitment';
import { CommitmentCard } from '../components/commitments/CommitmentCard';
import { Card } from '../components/ui/Card';
import { Input } from '../components/ui/Input';
import { Search, Layers } from 'lucide-react';

export const Commitments: React.FC = () => {
  const [commitments, setCommitments] = useState<Commitment[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedFilter, setSelectedFilter] = useState<string>('all');
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

  const filterOptions = [
    { id: 'all', label: 'All', count: commitments.length },
    { id: 'pending', label: 'Pending', count: commitments.filter((c) => c.status === 'PARTIALLY_FULFILLED' || c.status === 'UNVERIFIED').length },
    { id: 'fulfilled', label: 'Fulfilled', count: commitments.filter((c) => c.status === 'FULFILLED').length },
    { id: 'partially_fulfilled', label: 'Partially fulfilled', count: commitments.filter((c) => c.status === 'PARTIALLY_FULFILLED').length },
    { id: 'unverified', label: 'Unverified', count: commitments.filter((c) => c.status === 'UNVERIFIED').length },
    { id: 'contradictory', label: 'Contradictory', count: commitments.filter((c) => c.status === 'CONTRADICTORY').length },
  ];

  const filteredList = commitments.filter((item) => {
    const matchesSearch =
      item.person.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.action.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.deadline.toLowerCase().includes(searchQuery.toLowerCase());

    if (!matchesSearch) return false;

    if (selectedFilter === 'all') return true;
    if (selectedFilter === 'pending') {
      return item.status === 'PARTIALLY_FULFILLED' || item.status === 'UNVERIFIED';
    }
    if (selectedFilter === 'fulfilled') return item.status === 'FULFILLED';
    if (selectedFilter === 'partially_fulfilled') return item.status === 'PARTIALLY_FULFILLED';
    if (selectedFilter === 'unverified') return item.status === 'UNVERIFIED';
    if (selectedFilter === 'contradictory') return item.status === 'CONTRADICTORY';
    return true;
  });

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex flex-col gap-6">
      {/* Header */}
      <div>
        <h1 className="font-headline text-2xl sm:text-3xl font-bold tracking-tight text-on-surface">
          Commitments
        </h1>
        <p className="text-sm text-on-surface-variant mt-1">
          Everything you've promised, in one place.
        </p>
      </div>

      {/* Filter and Search Bar */}
      <Card className="p-3 sm:p-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
        {/* Filter Pills */}
        <div className="flex flex-wrap items-center gap-1.5 overflow-x-auto pb-1 md:pb-0">
          {filterOptions.map((filter) => (
            <button
              key={filter.id}
              onClick={() => setSelectedFilter(filter.id)}
              className={`px-3 py-1.5 rounded-xl text-xs font-medium transition-all flex items-center gap-1.5 shrink-0 ${
                selectedFilter === filter.id
                  ? 'bg-primary text-on-primary'
                  : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container'
              }`}
            >
              <span>{filter.label}</span>
              <span className={`text-[10px] px-1.5 py-0.2 rounded-full ${
                selectedFilter === filter.id
                  ? 'bg-white/20 text-white'
                  : 'bg-surface-container text-on-surface-variant'
              }`}>
                {filter.count}
              </span>
            </button>
          ))}
        </div>

        {/* Search */}
        <div className="w-full md:w-72 shrink-0">
          <Input
            placeholder="Search commitments..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            icon={<Search className="w-4 h-4 text-on-surface-variant" />}
          />
        </div>
      </Card>

      {/* Commitments List */}
      <div className="flex flex-col gap-3">
        {loading ? (
          <div className="flex flex-col items-center justify-center p-12 bg-surface-container-lowest rounded-2xl border border-outline-variant/60">
            <span className="w-6 h-6 border-2 border-secondary border-t-transparent rounded-full animate-spin mb-3" />
            <p className="text-xs text-on-surface-variant">Loading commitments...</p>
          </div>
        ) : filteredList.length === 0 ? (
          <div className="flex flex-col items-center justify-center p-12 bg-surface-container-lowest rounded-2xl border border-outline-variant/60 text-center">
            <Layers className="w-8 h-8 text-on-surface-variant/60 mb-2" />
            <h3 className="font-headline text-sm font-semibold text-on-surface">
              No commitments found
            </h3>
            <p className="text-xs text-on-surface-variant mt-1 max-w-sm">
              No commitments match the selected filter or search term.
            </p>
          </div>
        ) : (
          filteredList.map((c) => (
            <CommitmentCard key={c.id} commitment={c} />
          ))
        )}
      </div>
    </div>
  );
};
