import React from 'react';
import { EvidenceItem } from '../../types/evidence';
import { Badge } from '../ui/Badge';
import { Button } from '../ui/Button';
import { FileText, FileSpreadsheet, Eye, Link as LinkIcon, CheckCircle2, Clock, AlertCircle } from 'lucide-react';

interface EvidenceCardProps {
  evidence: EvidenceItem;
  onView: (item: EvidenceItem) => void;
}

export const EvidenceCard: React.FC<EvidenceCardProps> = ({ evidence, onView }) => {
  const getFileIcon = (type: string) => {
    switch (type) {
      case 'XLSX':
      case 'CSV':
        return <FileSpreadsheet className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />;
      case 'LINK':
        return <LinkIcon className="w-5 h-5 text-blue-600 dark:text-blue-400" />;
      case 'PDF':
      default:
        return <FileText className="w-5 h-5 text-secondary" />;
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'Supporting':
        return (
          <Badge variant="success" size="sm">
            <CheckCircle2 className="w-3 h-3" />
            <span>Supports commitment</span>
          </Badge>
        );
      case 'Partial Match':
        return (
          <Badge variant="warning" size="sm">
            <Clock className="w-3 h-3" />
            <span>Partial match</span>
          </Badge>
        );
      case 'Missing Items':
      case 'Contradictory':
        return (
          <Badge variant="error" size="sm">
            <AlertCircle className="w-3 h-3" />
            <span>Missing items</span>
          </Badge>
        );
      default:
        return (
          <Badge variant="neutral" size="sm">
            <span>{status}</span>
          </Badge>
        );
    }
  };

  return (
    <div className="flex flex-col sm:flex-row sm:items-center justify-between p-4 sm:p-5 bg-surface-container-lowest rounded-2xl border border-outline-variant/60 shadow-subtle hover:shadow-card hover:border-outline-variant transition-all duration-200 gap-4">
      {/* File Info */}
      <div className="flex items-start sm:items-center gap-3.5 min-w-[220px]">
        <div className="w-10 h-10 rounded-xl bg-surface-container flex items-center justify-center shrink-0 border border-outline-variant/40">
          {getFileIcon(evidence.fileType)}
        </div>
        <div className="flex flex-col">
          <div className="flex items-center gap-2">
            <span className="text-sm font-semibold text-on-surface">
              {evidence.fileName}
            </span>
            <span className="text-[10px] px-1.5 py-0.5 rounded bg-surface-container text-on-surface-variant font-mono font-medium">
              {evidence.fileType}
            </span>
          </div>
          <span className="text-xs text-on-surface-variant mt-0.5">
            {evidence.fileSize} • Added {evidence.sourceDate}
          </span>
        </div>
      </div>

      {/* Used For / Related Commitment */}
      <div className="flex-1 min-w-0">
        <span className="text-[11px] font-medium text-on-surface-variant block uppercase tracking-wider">
          Used for:
        </span>
        <p className="text-sm font-medium text-on-surface truncate mt-0.5">
          {evidence.relatedCommitment}
        </p>
      </div>

      {/* Status & View Action */}
      <div className="flex items-center justify-between sm:justify-end gap-3 shrink-0 pt-2 sm:pt-0 border-t border-outline-variant/40 sm:border-0">
        {getStatusBadge(evidence.status)}

        <Button
          variant="secondary"
          size="sm"
          onClick={() => onView(evidence)}
          icon={<Eye className="w-3.5 h-3.5" />}
        >
          <span>View</span>
        </Button>
      </div>
    </div>
  );
};
