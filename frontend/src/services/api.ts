import { Commitment } from '../types/commitment';
import { EvidenceItem } from '../types/evidence';
import { VerificationResultData, FollowupDraftData } from '../types/verification';
import { 
  INITIAL_DEMO_COMMITMENTS, 
  INITIAL_DEMO_EVIDENCE, 
  INITIAL_DEMO_VERIFICATIONS, 
  INITIAL_DEMO_FOLLOWUPS 
} from '../data/demoData';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// In-memory frontend state for demo mode
let localCommitments: Commitment[] = [...INITIAL_DEMO_COMMITMENTS];
let localEvidence: EvidenceItem[] = [...INITIAL_DEMO_EVIDENCE];
let localVerifications: Record<string, VerificationResultData> = { ...INITIAL_DEMO_VERIFICATIONS };
let localFollowups: Record<string, FollowupDraftData> = { ...INITIAL_DEMO_FOLLOWUPS };

/**
 * Analyzes conversation text to extract commitments.
 * Communicates with Member 3's POST /api/analyze endpoint.
 */
export async function analyzeConversation(text: string): Promise<{ commitments: Commitment[]; count: number }> {
  try {
    const res = await fetch(`${API_BASE_URL}/api/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text }),
    });
    if (res.ok) {
      const data = await res.json();
      return data;
    }
  } catch {
    // Backend not connected yet - simulated fallback for Member 4 frontend demo
  }

  // Simulated AI analysis delay
  await new Promise((resolve) => setTimeout(resolve, 1200));

  // Extract demo commitments from the sample conversation or generate dynamic ones
  const newCommitments: Commitment[] = [
    {
      id: `COM-${Math.floor(1000 + Math.random() * 9000)}`,
      person: 'Rahul',
      role: 'Design Lead',
      action: 'Send quotation & updated SOW',
      deadline: 'Tonight before 8 PM',
      source: 'Direct Conversation',
      sourceExcerpt: "Rahul: I'll send the updated SOW and the revised quotation tonight before 8 PM.",
      expectedEvidence: ['quotation.pdf', 'updated_sow.docx'],
      status: 'UNVERIFIED',
      category: 'pending',
      deliverablesTotal: 2,
      deliverablesCompleted: 0,
      confidence: 'High confidence',
      aiExplanation: 'Detected deliverable commitment with explicit deadline tonight.',
      avatarColor: 'bg-emerald-500/15 text-emerald-700 dark:text-emerald-400',
      createdAt: 'Just now'
    },
    {
      id: `COM-${Math.floor(1000 + Math.random() * 9000)}`,
      person: 'Priya',
      role: 'Product Manager',
      action: 'Share revised presentation deck with legal counsel',
      deadline: 'Friday noon',
      source: 'Direct Conversation',
      sourceExcerpt: "Priya: I'll make sure to share the revised presentation deck with their legal counsel by Friday noon.",
      expectedEvidence: ['presentation_deck.pdf'],
      status: 'UNVERIFIED',
      category: 'pending',
      deliverablesTotal: 1,
      deliverablesCompleted: 0,
      confidence: 'High confidence',
      aiExplanation: 'Stipulated handoff to legal counsel identified with Friday milestone.',
      avatarColor: 'bg-blue-500/15 text-blue-700 dark:text-blue-400',
      createdAt: 'Just now'
    },
    {
      id: `COM-${Math.floor(1000 + Math.random() * 9000)}`,
      person: 'Rahul',
      role: 'Design Lead',
      action: 'Update pricing sheet with tier discounts',
      deadline: 'Tomorrow morning',
      source: 'Direct Conversation',
      sourceExcerpt: 'Rahul: I will update the pricing sheet with tier discounts by tomorrow morning.',
      expectedEvidence: ['pricing_sheet.xlsx'],
      status: 'UNVERIFIED',
      category: 'pending',
      deliverablesTotal: 1,
      deliverablesCompleted: 0,
      confidence: 'High confidence',
      aiExplanation: 'Financial pricing model revision promised by tomorrow morning.',
      avatarColor: 'bg-emerald-500/15 text-emerald-700 dark:text-emerald-400',
      createdAt: 'Just now'
    }
  ];

  // Prepend to local commitments so they show up across the app
  localCommitments = [...newCommitments, ...localCommitments];

  return {
    commitments: newCommitments,
    count: newCommitments.length
  };
}

/**
 * Fetches all commitments.
 * Communicates with Member 3's GET /api/commitments endpoint.
 */
export async function getCommitments(): Promise<Commitment[]> {
  try {
    const res = await fetch(`${API_BASE_URL}/api/commitments`);
    if (res.ok) {
      return await res.json();
    }
  } catch {
    // Backend offline fallback
  }

  await new Promise((resolve) => setTimeout(resolve, 150));
  return localCommitments;
}

/**
 * Fetches a single commitment by ID.
 * Communicates with Member 3's GET /api/commitments/:id endpoint.
 */
export async function getCommitment(id: string): Promise<Commitment | null> {
  try {
    const res = await fetch(`${API_BASE_URL}/api/commitments/${id}`);
    if (res.ok) {
      return await res.json();
    }
  } catch {
    // Backend offline fallback
  }

  await new Promise((resolve) => setTimeout(resolve, 150));
  const found = localCommitments.find((c) => c.id === id);
  return found || null;
}

/**
 * Fetches all evidence items.
 * Communicates with Member 3's GET /api/evidence endpoint.
 */
export async function getEvidence(): Promise<EvidenceItem[]> {
  try {
    const res = await fetch(`${API_BASE_URL}/api/evidence`);
    if (res.ok) {
      return await res.json();
    }
  } catch {
    // Backend offline fallback
  }

  await new Promise((resolve) => setTimeout(resolve, 150));
  return localEvidence;
}

/**
 * Uploads evidence file.
 * Communicates with Member 3's POST /api/evidence/upload endpoint.
 */
export async function uploadEvidence(file: File, commitmentId?: string): Promise<EvidenceItem> {
  try {
    const formData = new FormData();
    formData.append('file', file);
    if (commitmentId) formData.append('commitment_id', commitmentId);

    const res = await fetch(`${API_BASE_URL}/api/evidence/upload`, {
      method: 'POST',
      body: formData,
    });
    if (res.ok) {
      return await res.json();
    }
  } catch {
    // Backend offline fallback
  }

  await new Promise((resolve) => setTimeout(resolve, 500));
  const newEvidence: EvidenceItem = {
    id: `EVD-${Math.floor(100 + Math.random() * 900)}`,
    fileName: file.name,
    fileType: file.name.endsWith('.pdf') ? 'PDF' : file.name.endsWith('.xlsx') ? 'XLSX' : 'DOCX',
    fileSize: `${(file.size / 1024).toFixed(1)} KB`,
    relatedCommitment: commitmentId ? `Commitment #${commitmentId}` : 'General Workspace Evidence',
    commitmentId: commitmentId || 'COM-101',
    status: 'Supporting',
    relevanceScore: 0.95,
    sourceDate: 'Just now',
    contentExcerpt: `Parsed content snippet from uploaded deliverable ${file.name}. Verified valid formatting.`,
    details: 'Uploaded directly via Member 4 Frontend UI.'
  };

  localEvidence = [newEvidence, ...localEvidence];
  return newEvidence;
}

/**
 * Verifies a commitment against available evidence.
 * Communicates with Member 3's POST /api/verify/:id endpoint.
 */
export async function verifyCommitment(id: string): Promise<VerificationResultData> {
  try {
    const res = await fetch(`${API_BASE_URL}/api/verify/${id}`, { method: 'POST' });
    if (res.ok) {
      return await res.json();
    }
  } catch {
    // Backend offline fallback
  }

  await new Promise((resolve) => setTimeout(resolve, 800));

  if (localVerifications[id]) {
    return localVerifications[id];
  }

  // Default dynamic verification result
  const commitment = localCommitments.find((c) => c.id === id);
  const result: VerificationResultData = {
    commitmentId: id,
    status: commitment?.status || 'PARTIALLY_FULFILLED',
    evidence: commitment?.expectedEvidence || ['deliverable.pdf'],
    evidenceFileName: commitment?.expectedEvidence[0] || 'deliverable.pdf',
    explanation: commitment?.aiExplanation || 'PromiseOS analyzed workspace files and matched deliverable content.',
    missingItems: commitment?.status === 'PARTIALLY_FULFILLED' ? ['Product 4 price', 'Delivery cost'] : [],
    confidence: 'High',
    completedItemsCount: commitment?.deliverablesCompleted || 1,
    totalItemsCount: commitment?.deliverablesTotal || 2,
    contradictions: commitment?.status === 'CONTRADICTORY' ? ['Conflicting timestamp in email records'] : [],
    verifiedAt: 'Just now',
    verifiedBy: 'Automated Verification Agent'
  };

  localVerifications[id] = result;
  return result;
}

/**
 * Generates or fetches follow-up draft for a commitment.
 * Communicates with Member 3's POST /api/followup/:id endpoint.
 */
export async function generateFollowUp(id: string): Promise<FollowupDraftData> {
  try {
    const res = await fetch(`${API_BASE_URL}/api/followup/${id}`, { method: 'POST' });
    if (res.ok) {
      return await res.json();
    }
  } catch {
    // Backend offline fallback
  }

  await new Promise((resolve) => setTimeout(resolve, 600));

  if (localFollowups[id]) {
    return localFollowups[id];
  }

  const commitment = localCommitments.find((c) => c.id === id);
  const person = commitment?.person || 'Counterparty';
  const action = commitment?.action || 'the deliverable';

  const draft: FollowupDraftData = {
    commitmentId: id,
    recipient: person,
    deliverable: action,
    status: commitment?.status || 'Partially Fulfilled',
    draft: `Hi ${person}, just following up on ${action}. Two items still appear to be missing. Could you update them when you get a chance?`,
    approved: false,
    sentBaseline: 'Today 10:00 AM',
    lastUpdated: 'Just now'
  };

  localFollowups[id] = draft;
  return draft;
}

/**
 * Approves a follow-up draft (Human-in-the-loop review).
 * NOTE: PromiseOS does not autonomously send messages; user approval is required.
 */
export async function approveFollowUp(id: string, message: string): Promise<{ success: boolean; message: string }> {
  try {
    const res = await fetch(`${API_BASE_URL}/api/followup/${id}/approve`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message }),
    });
    if (res.ok) {
      return await res.json();
    }
  } catch {
    // Backend offline fallback
  }

  await new Promise((resolve) => setTimeout(resolve, 400));
  if (localFollowups[id]) {
    localFollowups[id].approved = true;
    localFollowups[id].draft = message;
    localFollowups[id].lastUpdated = 'Approved by user';
  }

  return {
    success: true,
    message: 'Follow-up message approved and marked ready for dispatch.'
  };
}
