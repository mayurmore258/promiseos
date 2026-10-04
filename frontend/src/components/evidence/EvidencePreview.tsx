import React from 'react';
import { EvidenceItem } from '../../types/evidence';
import { Modal } from '../ui/Modal';
import { Button } from '../ui/Button';
import { Badge } from '../ui/Badge';
import { FileText, CheckCircle2, Clock, AlertCircle } from 'lucide-react';

interface EvidencePreviewProps {
  evidence: EvidenceItem | null;
  isOpen: boolean;
  onClose: () => void;
}

export const EvidencePreview: React.FC<EvidencePreviewProps> = ({
  evidence,
  isOpen,
  onClose,
}) => {
  if (!evidence) return null;

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={evidence.fileName}
      description={`Added ${evidence.sourceDate} • ${evidence.fileSize} • ${evidence.fileType}`}
      maxWidth="md"
    >
      <div className="flex flex-col gap-4">
        {/* Status header */}
        <div className="flex items-center justify-between p-3.5 bg-surface-container rounded-xl">
          <div className="flex items-center gap-2">
            <span className="text-xs text-on-surface-variant font-medium">Verification Status:</span>
            {evidence.status === 'Supporting' && (
              <Badge variant="success" size="sm">
                <CheckCircle2 className="w-3 h-3" />
                <span>Supports commitment</span>
              </Badge>
            )}
            {evidence.status === 'Partial Match' && (
              <Badge variant="warning" size="sm">
                <Clock className="w-3 h-3" />
                <span>Partial match</span>
              </Badge>
            )}
            {(evidence.status === 'Missing Items' || evidence.status === 'Contradictory') && (
              <Badge variant="error" size="sm">
                <AlertCircle className="w-3 h-3" />
                <span>Missing requirements</span>
              </Badge>
            )}
          </div>
          {evidence.relevanceScore && (
            <span className="text-xs font-semibold text-secondary">
              {(evidence.relevanceScore * 100).toFixed(0)}% match
            </span>
          )}
        </div>

        {/* Related Promise */}
        <div className="p-3.5 bg-surface-container-low rounded-xl border border-outline-variant/60">
          <span className="text-[11px] font-semibold text-on-surface-variant uppercase tracking-wider block">
            Associated Promise:
          </span>
          <p className="text-sm font-medium text-on-surface mt-1">
            {evidence.relatedCommitment}
          </p>
        </div>

        {/* Content Excerpt */}
        <div>
          <span className="text-xs font-medium text-on-surface-variant block mb-1.5">
            Deliverable Excerpt:
          </span>
          <div className="p-4 bg-surface-container-low/70 border border-outline-variant/60 rounded-xl font-mono text-xs text-on-surface leading-relaxed">
            {evidence.contentExcerpt || 'No excerpt available for this deliverable preview.'}
          </div>
        </div>

        {/* Summary note */}
        {evidence.details && (
          <div className="text-xs text-on-surface-variant bg-surface-container/40 p-3 rounded-xl">
            <span className="font-semibold text-on-surface">Analysis note: </span>
            {evidence.details}
          </div>
        )}

        {/* Footer actions */}
        <div className="flex items-center justify-end gap-2 pt-2 border-t border-outline-variant/40">
          <Button variant="outline" size="sm" onClick={onClose}>
            Close
          </Button>
          <Button variant="primary" size="sm" onClick={onClose} icon={<FileText className="w-3.5 h-3.5" />}>
            Download file
          </Button>
        </div>
      </div>
    </Modal>
  );
};
