import { CommitmentStatusType } from './commitment';

export interface VerificationResultData {
  commitmentId: string;
  status: CommitmentStatusType;
  evidence: string[];
  evidenceFileName?: string;
  explanation: string;
  missingItems: string[];
  confidence: string; // "High", "Medium", "Low"
  completedItemsCount: number;
  totalItemsCount: number;
  contradictions?: string[];
  verifiedAt?: string;
  verifiedBy?: string;
}

export interface FollowupDraftData {
  commitmentId: string;
  recipient: string;
  deliverable: string;
  status: string;
  draft: string;
  approved: boolean;
  sentBaseline?: string;
  lastUpdated?: string;
}
