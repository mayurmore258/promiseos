import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Commitment } from '../../types/commitment';
import { CommitmentStatusBadge } from './CommitmentStatus';
import { Button } from '../ui/Button';
import { ChevronRight, Calendar } from 'lucide-react';

interface CommitmentCardProps {
  commitment: Commitment;
}

export const CommitmentCard: React.FC<CommitmentCardProps> = ({ commitment }) => {
  const navigate = useNavigate();

  // Generate initials for avatar
  const initials = commitment.person
    ? commitment.person
        .split(' ')
        .map((n) => n[0])
        .join('')
        .slice(0, 2)
        .toUpperCase()
    : '??';

  const handleClick = () => {
    navigate(`/commitments/${commitment.id}`);
  };

  return (
    <div
      onClick={handleClick}
      className="group flex flex-col md:flex-row md:items-center justify-between p-4 sm:p-5 bg-surface-container-lowest rounded-2xl border border-outline-variant/60 shadow-subtle hover:shadow-card hover:border-outline-variant transition-all duration-200 gap-4 cursor-pointer"
    >
      {/* Person & Avatar */}
      <div className="flex items-center gap-3.5 min-w-[200px]">
        <div
          className={`w-10 h-10 rounded-full flex items-center justify-center text-xs font-semibold shrink-0 shadow-xs ${
            commitment.avatarColor || 'bg-surface-container text-on-surface'
          }`}
        >
          {initials}
        </div>
        <div className="flex flex-col">
          <span className="text-sm font-semibold text-on-surface leading-tight group-hover:text-secondary transition-colors">
            {commitment.person}
          </span>
          <span className="text-xs text-on-surface-variant mt-0.5">
            {commitment.role || commitment.source || 'Team Member'}
          </span>
        </div>
      </div>

      {/* Commitment Action & Deadline */}
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-on-surface truncate">
          {commitment.action}
        </p>
        <div className="flex items-center gap-1.5 text-xs text-on-surface-variant mt-0.5">
          <Calendar className="w-3.5 h-3.5 text-on-surface-variant/80" />
          <span>{commitment.deadline}</span>
        </div>
      </div>

      {/* Status & Action */}
      <div className="flex items-center justify-between md:justify-end gap-3 shrink-0 pt-2 md:pt-0 border-t border-outline-variant/40 md:border-0">
        <CommitmentStatusBadge status={commitment.status} />
        
        <Button
          variant="secondary"
          size="sm"
          onClick={(e) => {
            e.stopPropagation();
            navigate(`/commitments/${commitment.id}`);
          }}
          className="text-xs group-hover:bg-surface-container-high transition-colors"
        >
          <span>View details</span>
          <ChevronRight className="w-3 h-3 text-on-surface-variant" />
        </Button>
      </div>
    </div>
  );
};
