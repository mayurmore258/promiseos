export type CommitmentStatusType = 
  | 'FULFILLED'
  | 'PARTIALLY_FULFILLED'
  | 'UNFULFILLED'
  | 'UNVERIFIED'
  | 'CONTRADICTORY';

export interface Commitment {
  id: string;
  person: string;
  role?: string;
  action: string;
  deadline: string;
  source: string;
  sourceExcerpt?: string;
  expectedEvidence: string[];
  status: CommitmentStatusType;
  category?: 'fulfilled' | 'pending' | 'review';
  deliverablesTotal?: number;
  deliverablesCompleted?: number;
  confidence?: string;
  aiExplanation?: string;
  avatarColor?: string;
  createdAt?: string;
}

export interface CommitmentFilterCounts {
  all: number;
  fulfilled: number;
  pending: number;
  needReview: number;
}
