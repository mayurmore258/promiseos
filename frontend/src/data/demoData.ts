import { Commitment } from '../types/commitment';
import { EvidenceItem } from '../types/evidence';
import { VerificationResultData, FollowupDraftData } from '../types/verification';

export const INITIAL_DEMO_COMMITMENTS: Commitment[] = [
  {
    id: 'COM-101',
    person: 'Rahul',
    role: 'Design Lead',
    action: 'Send quotation & finalized SOW',
    deadline: 'Due today',
    source: 'Slack #acme-partnership',
    sourceExcerpt: "Rahul: Reviewed the feedback from ACME Corp. I'll send the updated SOW and the revised quotation tonight before 8 PM.",
    expectedEvidence: ['quotation.pdf', 'finalized_sow.docx'],
    status: 'FULFILLED',
    category: 'fulfilled',
    deliverablesTotal: 1,
    deliverablesCompleted: 1,
    confidence: 'High confidence',
    aiExplanation: 'The quotation matching the commitment was found in workspace attachments. Total scope & pricing match the promised deliverable.',
    avatarColor: 'bg-emerald-500/15 text-emerald-700 dark:text-emerald-400',
    createdAt: 'Today at 08:14 AM'
  },
  {
    id: 'COM-102',
    person: 'Priya',
    role: 'Product Manager',
    action: 'Update pricing sheet with EMEA discount',
    deadline: 'Due tomorrow',
    source: 'Slack #pricing-strategy',
    sourceExcerpt: "Priya: Perfect. Also, I will update the pricing sheet with tier discounts by tomorrow morning so you have the fresh figures.",
    expectedEvidence: ['pricing.xlsx', 'emea_tier_discount.csv'],
    status: 'PARTIALLY_FULFILLED',
    category: 'pending',
    deliverablesTotal: 5,
    deliverablesCompleted: 3,
    confidence: 'High confidence',
    aiExplanation: 'Most of the pricing sheet was updated, but two promised items (Product 4 price & delivery cost) are still missing.',
    avatarColor: 'bg-blue-500/15 text-blue-700 dark:text-blue-400',
    createdAt: 'Yesterday at 4:30 PM'
  },
  {
    id: 'COM-103',
    person: 'Aarav',
    role: 'Frontend Eng',
    action: 'Share project files & Figma handover',
    deadline: 'Due Oct 5',
    source: 'Zoom Meeting Notes',
    sourceExcerpt: 'Aarav: I will clean up the design components and send the Figma handover link by Oct 5.',
    expectedEvidence: ['figma_link', 'repository_branch'],
    status: 'UNVERIFIED',
    category: 'pending',
    deliverablesTotal: 2,
    deliverablesCompleted: 0,
    confidence: 'Medium confidence',
    aiExplanation: 'No evidence has been provided or discovered for the Figma handover yet.',
    avatarColor: 'bg-purple-500/15 text-purple-700 dark:text-purple-400',
    createdAt: 'Oct 2 at 11:00 AM'
  },
  {
    id: 'COM-104',
    person: 'Marcus',
    role: 'VP Engineering',
    action: 'Deliver security audit remediation checklist',
    deadline: 'Due Oct 8',
    source: 'Sprint Standup',
    sourceExcerpt: 'Marcus: Will provide the security audit remediation checklist before end of sprint.',
    expectedEvidence: ['security_audit_remediation.pdf'],
    status: 'UNFULFILLED',
    category: 'review',
    deliverablesTotal: 1,
    deliverablesCompleted: 0,
    confidence: 'High confidence',
    aiExplanation: 'Agreed checkpoint has passed without deliverable submission or progress log.',
    avatarColor: 'bg-rose-500/15 text-rose-700 dark:text-rose-400',
    createdAt: 'Oct 1 at 3:15 PM'
  },
  {
    id: 'COM-105',
    person: 'Elena',
    role: 'Legal Counsel',
    action: 'Provide signed MSA amendment',
    deadline: 'Due Oct 10',
    source: 'Email Thread',
    sourceExcerpt: 'Elena: Signed agreement will be sent over as soon as legal completes the clause review.',
    expectedEvidence: ['msa_amendment_signed.pdf'],
    status: 'CONTRADICTORY',
    category: 'review',
    deliverablesTotal: 2,
    deliverablesCompleted: 1,
    confidence: 'High confidence',
    aiExplanation: 'Conflicting evidence: email claims agreement was executed, but internal repository notes show signature pending board approval.',
    avatarColor: 'bg-amber-500/15 text-amber-700 dark:text-amber-400',
    createdAt: 'Sep 30 at 1:45 PM'
  }
];

export const INITIAL_DEMO_EVIDENCE: EvidenceItem[] = [
  {
    id: 'EVD-01',
    fileName: 'quotation.pdf',
    fileType: 'PDF',
    fileSize: '248 KB',
    relatedCommitment: 'Rahul will send the quotation',
    commitmentId: 'COM-101',
    status: 'Supporting',
    relevanceScore: 0.98,
    sourceDate: 'Today at 08:14 AM',
    contentExcerpt: 'ACME Corp Quotation #4902 - Scope of Work and final tier pricing totaling $45,000 for Phase 1 deliverable.',
    details: 'Validated PDF deliverable sent via workspace email. Contains signature and line-item breakdown.'
  },
  {
    id: 'EVD-02',
    fileName: 'pricing.xlsx',
    fileType: 'XLSX',
    fileSize: '1.2 MB',
    relatedCommitment: 'Priya will update the pricing sheet',
    commitmentId: 'COM-102',
    status: 'Partial Match',
    relevanceScore: 0.88,
    sourceDate: 'Yesterday at 4:30 PM',
    contentExcerpt: 'Global Pricing Matrix 2026. Tier A and B EMEA discounts applied. Columns 12-14 (Product 4 and Freight Surcharge) remain uncalculated.',
    details: 'Spreadsheet contains 3 updated product lines. Product 4 base price and delivery surcharge remain blank.'
  },
  {
    id: 'EVD-03',
    fileName: 'revised_deck.pdf',
    fileType: 'PDF',
    fileSize: '3.8 MB',
    relatedCommitment: 'Priya will share revised presentation deck',
    commitmentId: 'COM-102',
    status: 'Supporting',
    relevanceScore: 0.94,
    sourceDate: 'Today at 11:20 AM',
    contentExcerpt: 'ACME Partners Q4 Strategic Roadmap presentation, 18 slides with executive summary.',
    details: 'Clean deck with client comments addressed and revision history recorded.'
  },
  {
    id: 'EVD-04',
    fileName: 'msa_amendment_signed.pdf',
    fileType: 'PDF',
    fileSize: '410 KB',
    relatedCommitment: 'Elena will provide signed MSA amendment',
    commitmentId: 'COM-105',
    status: 'Missing Items',
    relevanceScore: 0.76,
    sourceDate: 'Oct 2 at 2:15 PM',
    contentExcerpt: 'Master Services Agreement Addendum B. Contains unsigned initials on page 4.',
    details: 'Document uploaded contains signature fields for customer, but internal authorization stamp is missing.'
  }
];

export const INITIAL_DEMO_VERIFICATIONS: Record<string, VerificationResultData> = {
  'COM-101': {
    commitmentId: 'COM-101',
    status: 'FULFILLED',
    evidence: ['quotation.pdf'],
    evidenceFileName: 'quotation.pdf',
    explanation: 'The quotation matching the commitment was found. All scope requirements and pricing figures correspond with the promised terms.',
    missingItems: [],
    confidence: 'High',
    completedItemsCount: 1,
    totalItemsCount: 1,
    contradictions: [],
    verifiedAt: 'Today at 08:30 AM',
    verifiedBy: 'Automated Evidence Verification'
  },
  'COM-102': {
    commitmentId: 'COM-102',
    status: 'PARTIALLY_FULFILLED',
    evidence: ['pricing.xlsx'],
    evidenceFileName: 'pricing.xlsx',
    explanation: 'Most of the pricing sheet was updated, but two promised items are still missing.',
    missingItems: ['Product 4 price', 'Delivery cost'],
    confidence: 'High',
    completedItemsCount: 3,
    totalItemsCount: 5,
    contradictions: [],
    verifiedAt: 'Yesterday at 5:00 PM',
    verifiedBy: 'Automated Evidence Verification'
  },
  'COM-103': {
    commitmentId: 'COM-103',
    status: 'UNVERIFIED',
    evidence: [],
    explanation: 'No evidence has been uploaded or discovered for this deliverable yet.',
    missingItems: ['Figma file URL', 'Asset export bundle'],
    confidence: 'Medium',
    completedItemsCount: 0,
    totalItemsCount: 2,
    contradictions: [],
    verifiedAt: 'Pending',
    verifiedBy: 'Verification Queue'
  },
  'COM-104': {
    commitmentId: 'COM-104',
    status: 'UNFULFILLED',
    evidence: [],
    explanation: 'The promised audit remediation deliverable was not provided before the agreed deadline.',
    missingItems: ['Security audit report PDF', 'Remediation log'],
    confidence: 'High',
    completedItemsCount: 0,
    totalItemsCount: 1,
    contradictions: [],
    verifiedAt: 'Oct 3 at 9:00 AM',
    verifiedBy: 'Automated Evidence Verification'
  },
  'COM-105': {
    commitmentId: 'COM-105',
    status: 'CONTRADICTORY',
    evidence: ['msa_amendment_signed.pdf'],
    evidenceFileName: 'msa_amendment_signed.pdf',
    explanation: 'Evidence directly conflicts: Email thread indicated document was signed, but the uploaded file lacks counterparty execution.',
    missingItems: ['Final executed signature on page 4'],
    confidence: 'High',
    completedItemsCount: 1,
    totalItemsCount: 2,
    contradictions: ['Email timestamp confirms execution', 'Uploaded PDF signature block is blank'],
    verifiedAt: 'Oct 2 at 3:00 PM',
    verifiedBy: 'Automated Evidence Verification'
  }
};

export const INITIAL_DEMO_FOLLOWUPS: Record<string, FollowupDraftData> = {
  'COM-102': {
    commitmentId: 'COM-102',
    recipient: 'Priya Sharma',
    deliverable: 'Pricing sheet with EMEA discount',
    status: 'Partially Fulfilled',
    draft: 'Hi Priya, just following up on the pricing sheet. Two items still appear to be missing (Product 4 price and delivery cost). Could you update them when you get a chance?',
    approved: false,
    sentBaseline: 'Today 09:42 AM',
    lastUpdated: '10 minutes ago'
  },
  'COM-101': {
    commitmentId: 'COM-101',
    recipient: 'Rahul Verma',
    deliverable: 'Quotation and SOW',
    status: 'Fulfilled',
    draft: 'Hi Rahul, confirming receipt of the quotation and SOW. Everything has been verified and meets the agreed requirements. Thanks for sending it over so quickly!',
    approved: false,
    sentBaseline: 'Today 08:30 AM',
    lastUpdated: 'Today at 08:45 AM'
  },
  'COM-104': {
    commitmentId: 'COM-104',
    recipient: 'Marcus Chen',
    deliverable: 'Security audit remediation checklist',
    status: 'Unfulfilled',
    draft: 'Hi Marcus, checking in on the security audit remediation checklist. The milestone date has passed—do you have an updated timeframe for when this will be ready?',
    approved: false,
    sentBaseline: 'Yesterday 04:15 PM',
    lastUpdated: 'Yesterday at 04:30 PM'
  }
};
