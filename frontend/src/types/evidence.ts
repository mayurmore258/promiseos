export type EvidenceStatus = 
  | 'Supporting'
  | 'Partial Match'
  | 'Missing Items'
  | 'Contradictory'
  | 'Unrelated';

export interface EvidenceItem {
  id: string;
  fileName: string;
  fileType: 'PDF' | 'XLSX' | 'DOCX' | 'CSV' | 'TXT' | 'LINK';
  fileSize: string;
  relatedCommitment: string;
  commitmentId: string;
  status: EvidenceStatus;
  relevanceScore?: number;
  sourceDate: string;
  contentExcerpt?: string;
  details?: string;
}
