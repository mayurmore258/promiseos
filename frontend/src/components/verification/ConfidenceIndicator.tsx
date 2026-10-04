import React from 'react';
import { Badge } from '../ui/Badge';
import { ShieldCheck, ShieldAlert } from 'lucide-react';

interface ConfidenceIndicatorProps {
  confidence?: string;
  size?: 'sm' | 'md';
}

export const ConfidenceIndicator: React.FC<ConfidenceIndicatorProps> = ({
  confidence = 'High confidence',
  size = 'md',
}) => {
  const isHigh = confidence.toLowerCase().includes('high');
  const isMedium = confidence.toLowerCase().includes('medium');

  return (
    <Badge
      variant={isHigh ? 'success' : isMedium ? 'warning' : 'neutral'}
      size={size}
    >
      {isHigh ? (
        <ShieldCheck className="w-3.5 h-3.5" />
      ) : (
        <ShieldAlert className="w-3.5 h-3.5" />
      )}
      <span>{confidence}</span>
    </Badge>
  );
};
