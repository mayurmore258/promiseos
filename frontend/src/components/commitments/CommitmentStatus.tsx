import React from 'react';
import { CommitmentStatusType } from '../../types/commitment';
import { Badge } from '../ui/Badge';
import { Check, Clock, HelpCircle, XCircle, AlertTriangle } from 'lucide-react';

interface CommitmentStatusProps {
  status: CommitmentStatusType | string;
  size?: 'sm' | 'md';
}

export const CommitmentStatusBadge: React.FC<CommitmentStatusProps> = ({ status, size = 'md' }) => {
  const normalized = status.toUpperCase().replace(/\s+/g, '_');

  switch (normalized) {
    case 'FULFILLED':
      return (
        <Badge variant="success" size={size}>
          <Check className="w-3 h-3" />
          <span>Fulfilled</span>
        </Badge>
      );
    case 'PARTIALLY_FULFILLED':
      return (
        <Badge variant="warning" size={size}>
          <Clock className="w-3 h-3" />
          <span>Partially fulfilled</span>
        </Badge>
      );
    case 'UNFULFILLED':
      return (
        <Badge variant="error" size={size}>
          <XCircle className="w-3 h-3" />
          <span>Unfulfilled</span>
        </Badge>
      );
    case 'CONTRADICTORY':
      return (
        <Badge variant="purple" size={size}>
          <AlertTriangle className="w-3 h-3" />
          <span>Contradictory</span>
        </Badge>
      );
    case 'UNVERIFIED':
    default:
      return (
        <Badge variant="neutral" size={size}>
          <HelpCircle className="w-3 h-3" />
          <span>Unverified</span>
        </Badge>
      );
  }
};
