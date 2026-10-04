import { Commitment, CommitmentStatusType } from '../types/commitment';
import { EvidenceItem, EvidenceStatus } from '../types/evidence';
import { VerificationResultData, FollowupDraftData } from '../types/verification';
import { 
  INITIAL_DEMO_COMMITMENTS, 
  INITIAL_DEMO_EVIDENCE, 
  INITIAL_DEMO_VERIFICATIONS, 
  INITIAL_DEMO_FOLLOWUPS 
} from '../data/demoData';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const USE_DEMO_FALLBACK = import.meta.env.VITE_USE_DEMO_FALLBACK === 'true';

// In-memory frontend state for demo mode
let localCommitments: Commitment[] = [...INITIAL_DEMO_COMMITMENTS];
let localEvidence: EvidenceItem[] = [...INITIAL_DEMO_EVIDENCE];
const localVerifications: Record<string, VerificationResultData> = { ...INITIAL_DEMO_VERIFICATIONS };
const localFollowups: Record<string, FollowupDraftData> = { ...INITIAL_DEMO_FOLLOWUPS };

// Session cache for newly uploaded evidence items during active session
const sessionEvidenceItems: EvidenceItem[] = [];

// Mapping from commitmentId -> followupId to support human approval routes
const commitmentToFollowupIdMap = new Map<string, string>();

// ============================================================================
// DATA TYPES FOR BACKEND RESPONSES
// ============================================================================

interface BackendCommitment {
  id: string;
  person: string;
  action?: string;
  object?: string;
  description?: string;
  deadline?: string | null;
  deadline_raw?: string | null;
  source?: string;
  source_excerpt?: string;
  expected_evidence?: string[];
  status?: string;
  confidence?: number;
  created_at?: string;
  updated_at?: string;
  role?: string;
  missing_items?: string[];
  evidence?: BackendEvidence[];
  verification?: BackendVerification | null;
  followup?: BackendFollowup | null;
}

interface BackendEvidence {
  id: string;
  file_name: string;
  commitment_id?: string | null;
  mime_type?: string;
  file_size?: number;
  relevance_score?: number;
  created_at?: string;
  details?: string;
  content_excerpt?: string;
}

interface BackendVerificationItem {
  file_name?: string;
  excerpt?: string;
  relevance_score?: number;
  source_type?: string;
}

interface BackendVerification {
  id?: string;
  commitment_id: string;
  status: string;
  evidence?: Array<string | BackendVerificationItem>;
  explanation?: string;
  evidence_summary?: string;
  missing_items?: string[];
  contradictions?: string[];
  confidence?: number | string;
  verified_at?: string;
}

interface BackendFollowup {
  id: string;
  commitment_id: string;
  draft: string;
  approved?: boolean;
  approved_at?: string | null;
  created_at?: string;
}

// ============================================================================
// ADAPTER HELPERS
// ============================================================================

const AVATAR_COLORS = [
  'bg-emerald-500/15 text-emerald-700 dark:text-emerald-400',
  'bg-blue-500/15 text-blue-700 dark:text-blue-400',
  'bg-purple-500/15 text-purple-700 dark:text-purple-400',
  'bg-amber-500/15 text-amber-700 dark:text-amber-400',
  'bg-rose-500/15 text-rose-700 dark:text-rose-400',
  'bg-indigo-500/15 text-indigo-700 dark:text-indigo-400',
];

function getAvatarColor(name: string): string {
  if (!name) return AVATAR_COLORS[0];
  let hash = 0;
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash);
  }
  return AVATAR_COLORS[Math.abs(hash) % AVATAR_COLORS.length];
}

function formatDeadline(deadlineRaw?: string | null, deadlineIso?: string | null): string {
  if (deadlineRaw && deadlineRaw.trim()) {
    return deadlineRaw.trim();
  }
  if (deadlineIso) {
    try {
      const d = new Date(deadlineIso);
      if (!isNaN(d.getTime())) {
        return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });
      }
    } catch {
      // ignore parsing error
    }
  }
  return 'No explicit deadline';
}

function mapBackendStatus(status?: string): CommitmentStatusType {
  const s = (status || '').toLowerCase().trim();
  switch (s) {
    case 'fulfilled':
      return 'FULFILLED';
    case 'partial':
    case 'partially_fulfilled':
      return 'PARTIALLY_FULFILLED';
    case 'unfulfilled':
      return 'UNFULFILLED';
    case 'unverified':
      return 'UNVERIFIED';
    case 'contradictory':
      return 'CONTRADICTORY';
    case 'pending':
    default:
      return 'UNVERIFIED';
  }
}

function mapConfidenceLabel(conf?: number | string | null): string {
  if (typeof conf === 'number') {
    if (conf >= 0.8) return 'High confidence';
    if (conf >= 0.5) return 'Medium confidence';
    return 'Low confidence';
  }
  if (typeof conf === 'string' && conf.trim()) {
    return conf.includes('confidence') ? conf : `${conf} confidence`;
  }
  return 'High confidence';
}

function mapConfidenceShort(conf?: number | string | null): string {
  if (typeof conf === 'number') {
    if (conf >= 0.8) return 'High';
    if (conf >= 0.5) return 'Medium';
    return 'Low';
  }
  if (typeof conf === 'string' && conf.trim()) {
    return conf.replace(/\s*confidence/i, '').trim() || 'High';
  }
  return 'High';
}

function detectFileType(fileName: string, mimeType?: string): 'PDF' | 'XLSX' | 'DOCX' | 'CSV' | 'TXT' | 'LINK' {
  const lower = (fileName || '').toLowerCase();
  if (lower.endsWith('.pdf')) return 'PDF';
  if (lower.endsWith('.xlsx') || lower.endsWith('.xls')) return 'XLSX';
  if (lower.endsWith('.docx') || lower.endsWith('.doc')) return 'DOCX';
  if (lower.endsWith('.csv')) return 'CSV';
  if (lower.endsWith('.txt')) return 'TXT';
  if (mimeType?.includes('pdf')) return 'PDF';
  if (mimeType?.includes('sheet') || mimeType?.includes('excel')) return 'XLSX';
  if (mimeType?.includes('word')) return 'DOCX';
  if (mimeType?.includes('csv')) return 'CSV';
  if (mimeType?.includes('text')) return 'TXT';
  return 'PDF';
}

function formatFileSize(bytes?: number): string {
  if (!bytes || bytes <= 0) return '12.4 KB';
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

// ============================================================================
// PUBLIC ADAPTER FUNCTIONS
// ============================================================================

export function adaptCommitment(raw: BackendCommitment): Commitment {
  const status = mapBackendStatus(raw.status);
  const actionText =
    raw.description ||
    (raw.action && raw.object ? `${raw.action} ${raw.object}` : raw.action) ||
    'Commitment deliverable';

  const expectedEv = Array.isArray(raw.expected_evidence) ? raw.expected_evidence : [];
  const deliverablesTotal = expectedEv.length > 0 ? expectedEv.length : 1;
  let deliverablesCompleted = 0;
  if (status === 'FULFILLED') {
    deliverablesCompleted = deliverablesTotal;
  } else if (status === 'PARTIALLY_FULFILLED') {
    const missingCount = Array.isArray(raw.missing_items) ? raw.missing_items.length : 1;
    deliverablesCompleted = Math.max(1, deliverablesTotal - missingCount);
  }

  let category: 'fulfilled' | 'pending' | 'review' = 'pending';
  if (status === 'FULFILLED') {
    category = 'fulfilled';
  } else if (status === 'UNFULFILLED' || status === 'CONTRADICTORY') {
    category = 'review';
  }

  return {
    id: raw.id,
    person: raw.person || 'Team Member',
    role: raw.role || 'Team Member',
    action: actionText,
    deadline: formatDeadline(raw.deadline_raw, raw.deadline),
    source: raw.source || 'Direct Conversation',
    sourceExcerpt: raw.source_excerpt || undefined,
    expectedEvidence: expectedEv,
    status,
    category,
    deliverablesTotal,
    deliverablesCompleted,
    confidence: mapConfidenceLabel(raw.confidence),
    aiExplanation: raw.description
      ? `Commitment extracted: ${raw.description}`
      : 'Commitment identified from communication.',
    avatarColor: getAvatarColor(raw.person || ''),
    createdAt: raw.created_at ? new Date(raw.created_at).toLocaleDateString() : 'Just now',
  };
}

export function adaptVerification(raw: BackendVerification): VerificationResultData {
  const status = mapBackendStatus(raw.status);
  const rawEvidence = Array.isArray(raw.evidence) ? raw.evidence : [];
  const evidenceFileNames: string[] = rawEvidence.map((e) => {
    if (typeof e === 'string') return e;
    return e.file_name || e.excerpt || 'Evidence document';
  });

  const missingItems = Array.isArray(raw.missing_items) ? raw.missing_items : [];
  const contradictions = Array.isArray(raw.contradictions) ? raw.contradictions : [];
  const primaryFileName =
    rawEvidence.length > 0
      ? typeof rawEvidence[0] === 'string'
        ? rawEvidence[0]
        : rawEvidence[0].file_name
      : undefined;

  const totalItemsCount = Math.max(1, evidenceFileNames.length + missingItems.length);
  let completedItemsCount = 0;
  if (status === 'FULFILLED') {
    completedItemsCount = totalItemsCount;
  } else if (status === 'PARTIALLY_FULFILLED') {
    completedItemsCount = Math.max(1, totalItemsCount - (missingItems.length || 1));
  }

  return {
    commitmentId: raw.commitment_id,
    status,
    evidence: evidenceFileNames,
    evidenceFileName: primaryFileName,
    explanation: raw.explanation || 'Verification completed against workspace evidence.',
    missingItems,
    confidence: mapConfidenceShort(raw.confidence),
    completedItemsCount,
    totalItemsCount,
    contradictions,
    verifiedAt: raw.verified_at ? new Date(raw.verified_at).toLocaleString() : 'Just now',
    verifiedBy: 'Automated Verification Agent',
  };
}

export function adaptEvidence(
  raw: BackendEvidence,
  commitmentContext?: { id: string; action: string }
): EvidenceItem {
  const score = raw.relevance_score ?? 0.9;
  let status: EvidenceStatus = 'Supporting';
  if (score < 0.4) {
    status = 'Partial Match';
  }

  const relatedText = commitmentContext?.action
    ? `Commitment: ${commitmentContext.action}`
    : raw.commitment_id
    ? `Commitment #${raw.commitment_id.slice(0, 8)}`
    : 'General Workspace Evidence';

  return {
    id: raw.id,
    fileName: raw.file_name,
    fileType: detectFileType(raw.file_name, raw.mime_type),
    fileSize: formatFileSize(raw.file_size),
    relatedCommitment: relatedText,
    commitmentId: raw.commitment_id || commitmentContext?.id || '',
    status,
    relevanceScore: score,
    sourceDate: raw.created_at ? new Date(raw.created_at).toLocaleDateString() : 'Recent',
    contentExcerpt:
      raw.content_excerpt ||
      `Indexed evidence from deliverable ${raw.file_name}. Processed and verified in PromiseOS workspace.`,
    details: raw.details || `File: ${raw.file_name} • Type: ${raw.mime_type || 'document'}`,
  };
}

export function adaptFollowUp(
  raw: BackendFollowup,
  commitment?: Commitment | null
): FollowupDraftData {
  return {
    commitmentId: raw.commitment_id,
    recipient: commitment?.person || 'Counterparty',
    deliverable: commitment?.action || 'the deliverable',
    status: commitment?.status ? mapBackendStatus(commitment.status) : 'UNVERIFIED',
    draft: raw.draft,
    approved: Boolean(raw.approved),
    sentBaseline: raw.created_at ? new Date(raw.created_at).toLocaleString() : 'Today 10:00 AM',
    lastUpdated: raw.approved
      ? 'Approved by user'
      : raw.approved_at
      ? 'Approved'
      : 'Draft generated',
  };
}

// ============================================================================
// RESPONSE / ERROR HANDLING HELPERS
// ============================================================================

async function handleResponse<T>(res: Response, fallbackGetter?: () => T | Promise<T>): Promise<T> {
  if (res.ok) {
    return (await res.json()) as T;
  }
  const errorText = await res.text().catch(() => '');
  let message = `API request failed with status ${res.status}: ${res.statusText}`;
  try {
    const errorJson = JSON.parse(errorText);
    if (errorJson.detail) {
      message = typeof errorJson.detail === 'string' ? errorJson.detail : JSON.stringify(errorJson.detail);
    }
  } catch {
    if (errorText) message += ` - ${errorText}`;
  }

  if (USE_DEMO_FALLBACK && fallbackGetter) {
    console.warn(`[PromiseOS] Backend error (${res.status}), using demo fallback:`, message);
    return await fallbackGetter();
  }

  throw new Error(message);
}

async function handleNetworkError<T>(err: unknown, fallbackGetter?: () => T | Promise<T>): Promise<T> {
  if (USE_DEMO_FALLBACK && fallbackGetter) {
    console.warn('[PromiseOS] Network failed, using demo fallback:', err);
    return await fallbackGetter();
  }
  const msg = err instanceof Error ? err.message : String(err);
  throw new Error(`PromiseOS backend connection error: ${msg}. Make sure backend is running at ${API_BASE_URL}`);
}

// ============================================================================
// DEMO FALLBACK ROUTINES (Preserved for VITE_USE_DEMO_FALLBACK=true)
// ============================================================================

async function fallbackAnalyze(_text: string): Promise<{ commitments: Commitment[]; count: number }> {
  await new Promise((resolve) => setTimeout(resolve, 800));
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
    }
  ];
  localCommitments = [...newCommitments, ...localCommitments];
  return { commitments: newCommitments, count: newCommitments.length };
}

async function fallbackVerify(id: string): Promise<VerificationResultData> {
  await new Promise((resolve) => setTimeout(resolve, 400));
  if (localVerifications[id]) {
    return localVerifications[id];
  }
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

async function fallbackFollowup(id: string): Promise<FollowupDraftData> {
  await new Promise((resolve) => setTimeout(resolve, 400));
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
    draft: `Hi ${person}, just following up on ${action}. Could you update when you get a chance?`,
    approved: false,
    sentBaseline: 'Today 10:00 AM',
    lastUpdated: 'Just now'
  };
  localFollowups[id] = draft;
  return draft;
}

// ============================================================================
// SERVICE API CLIENT IMPLEMENTATION
// ============================================================================

/**
 * Analyzes conversation text to extract commitments.
 * Communicates with POST /api/analyze.
 */
export async function analyzeConversation(text: string): Promise<{ commitments: Commitment[]; count: number }> {
  try {
    const res = await fetch(`${API_BASE_URL}/api/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, source: 'conversation' }),
    });

    if (!res.ok) {
      return await handleResponse<{ commitments: Commitment[]; count: number }>(res, () => fallbackAnalyze(text));
    }

    const data = (await res.json()) as {
      analysis_id?: string;
      total_commitments: number;
      commitments: BackendCommitment[];
    };

    const adaptedCommitments = (data.commitments || []).map(adaptCommitment);
    return {
      commitments: adaptedCommitments,
      count: data.total_commitments ?? adaptedCommitments.length,
    };
  } catch (err) {
    return await handleNetworkError<{ commitments: Commitment[]; count: number }>(err, () => fallbackAnalyze(text));
  }
}

/**
 * Fetches all commitments.
 * Communicates with GET /api/commitments.
 */
export async function getCommitments(): Promise<Commitment[]> {
  try {
    const res = await fetch(`${API_BASE_URL}/api/commitments`);
    if (!res.ok) {
      return await handleResponse<Commitment[]>(res, () => localCommitments);
    }
    const data = (await res.json()) as BackendCommitment[];
    return (data || []).map(adaptCommitment);
  } catch (err) {
    return await handleNetworkError<Commitment[]>(err, () => localCommitments);
  }
}

/**
 * Fetches a single commitment by ID.
 * Communicates with GET /api/commitments/:id.
 */
export async function getCommitment(id: string): Promise<Commitment | null> {
  try {
    const res = await fetch(`${API_BASE_URL}/api/commitments/${id}`);
    if (res.status === 404) {
      if (USE_DEMO_FALLBACK) {
        return localCommitments.find((c) => c.id === id) || null;
      }
      return null;
    }
    if (!res.ok) {
      return await handleResponse<Commitment | null>(res, () => localCommitments.find((c) => c.id === id) || null);
    }

    const data = (await res.json()) as BackendCommitment & {
      followup?: { id?: string };
    };

    if (data.followup?.id) {
      commitmentToFollowupIdMap.set(data.id, data.followup.id);
    }

    return adaptCommitment(data);
  } catch (err) {
    return await handleNetworkError<Commitment | null>(err, () => localCommitments.find((c) => c.id === id) || null);
  }
}

/**
 * Fetches all evidence items.
 * Backend does not provide GET /api/evidence; we aggregate evidence through commitments.
 */
export async function getEvidence(): Promise<EvidenceItem[]> {
  try {
    const commitmentsRes = await fetch(`${API_BASE_URL}/api/commitments`);
    if (!commitmentsRes.ok) {
      return await handleResponse<EvidenceItem[]>(commitmentsRes, () => localEvidence);
    }
    const commitmentsList = (await commitmentsRes.json()) as BackendCommitment[];

    // Fetch details for commitments in parallel to gather linked evidence items
    const detailPromises = commitmentsList.map(async (c) => {
      try {
        const detRes = await fetch(`${API_BASE_URL}/api/commitments/${c.id}`);
        if (detRes.ok) {
          const detail = (await detRes.json()) as BackendCommitment & { evidence?: BackendEvidence[] };
          if (Array.isArray(detail.evidence)) {
            return detail.evidence.map((ev) =>
              adaptEvidence(ev, {
                id: c.id,
                action: c.description || (c.action && c.object ? `${c.action} ${c.object}` : c.action) || 'Deliverable',
              })
            );
          }
        }
      } catch {
        // Individual commitment detail fetch failure handled gracefully
      }
      return [];
    });

    const nested = await Promise.all(detailPromises);
    const aggregated = nested.flat();

    // Deduplicate by evidence ID
    const seenIds = new Set<string>();
    const allEvidence: EvidenceItem[] = [];

    for (const item of [...sessionEvidenceItems, ...aggregated]) {
      if (!seenIds.has(item.id)) {
        seenIds.add(item.id);
        allEvidence.push(item);
      }
    }

    return allEvidence;
  } catch (err) {
    return await handleNetworkError<EvidenceItem[]>(err, () => localEvidence);
  }
}

/**
 * Uploads evidence file.
 * Communicates with POST /api/evidence/upload.
 */
export async function uploadEvidence(file: File, commitmentId?: string): Promise<EvidenceItem> {
  try {
    const formData = new FormData();
    formData.append('file', file);
    if (commitmentId) {
      formData.append('commitment_id', commitmentId);
    }

    const res = await fetch(`${API_BASE_URL}/api/evidence/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!res.ok) {
      return await handleResponse<EvidenceItem>(res, () => {
        const mock: EvidenceItem = {
          id: `EVD-${Math.floor(100 + Math.random() * 900)}`,
          fileName: file.name,
          fileType: detectFileType(file.name),
          fileSize: formatFileSize(file.size),
          relatedCommitment: commitmentId ? `Commitment #${commitmentId.slice(0, 8)}` : 'General Workspace Evidence',
          commitmentId: commitmentId || 'COM-101',
          status: 'Supporting',
          relevanceScore: 0.95,
          sourceDate: 'Just now',
          contentExcerpt: `Parsed content snippet from uploaded deliverable ${file.name}.`,
          details: 'Uploaded directly via UI.',
        };
        localEvidence = [mock, ...localEvidence];
        return mock;
      });
    }

    const data = (await res.json()) as BackendEvidence;
    const adapted = adaptEvidence(data, commitmentId ? { id: commitmentId, action: 'Linked Deliverable' } : undefined);
    sessionEvidenceItems.unshift(adapted);
    return adapted;
  } catch (err) {
    return await handleNetworkError<EvidenceItem>(err, () => {
      const mock: EvidenceItem = {
        id: `EVD-${Math.floor(100 + Math.random() * 900)}`,
        fileName: file.name,
        fileType: detectFileType(file.name),
        fileSize: formatFileSize(file.size),
        relatedCommitment: commitmentId ? `Commitment #${commitmentId.slice(0, 8)}` : 'General Workspace Evidence',
        commitmentId: commitmentId || 'COM-101',
        status: 'Supporting',
        relevanceScore: 0.95,
        sourceDate: 'Just now',
        contentExcerpt: `Parsed content snippet from uploaded deliverable ${file.name}.`,
        details: 'Uploaded directly via UI.',
      };
      localEvidence = [mock, ...localEvidence];
      return mock;
    });
  }
}

/**
 * Verifies a commitment against available evidence.
 * Communicates with POST /api/verify/:id.
 */
export async function verifyCommitment(id: string): Promise<VerificationResultData> {
  try {
    const res = await fetch(`${API_BASE_URL}/api/verify/${id}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });

    if (!res.ok) {
      return await handleResponse<VerificationResultData>(res, () => fallbackVerify(id));
    }

    const data = (await res.json()) as BackendVerification;
    return adaptVerification(data);
  } catch (err) {
    return await handleNetworkError<VerificationResultData>(err, () => fallbackVerify(id));
  }
}

/**
 * Generates or fetches follow-up draft for a commitment.
 * Communicates with POST /api/followup/:id.
 */
export async function generateFollowUp(id: string): Promise<FollowupDraftData> {
  try {
    const res = await fetch(`${API_BASE_URL}/api/followup/${id}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ tone: 'polite' }),
    });

    if (!res.ok) {
      return await handleResponse<FollowupDraftData>(res, () => fallbackFollowup(id));
    }

    const data = (await res.json()) as BackendFollowup;
    commitmentToFollowupIdMap.set(data.commitment_id, data.id);

    let c: Commitment | null = null;
    try {
      c = await getCommitment(data.commitment_id);
    } catch {
      // ignore
    }

    return adaptFollowUp(data, c);
  } catch (err) {
    return await handleNetworkError<FollowupDraftData>(err, () => fallbackFollowup(id));
  }
}

/**
 * Approves a follow-up draft (Human-in-the-loop review).
 * Communicates with POST /api/followup/:followupId/approve.
 */
export async function approveFollowUp(id: string, message: string): Promise<{ success: boolean; message: string }> {
  let targetId = commitmentToFollowupIdMap.get(id) || id;

  const payload = {
    approved: true,
    edited_draft: message ? message.trim() : undefined,
  };

  try {
    let res = await fetch(`${API_BASE_URL}/api/followup/${targetId}/approve`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    // If 404, id might be a commitment_id whose followup_id was not yet in our map.
    // Query commitment detail to discover its latest followup ID and retry approval.
    if (res.status === 404 && targetId === id) {
      try {
        const commRes = await fetch(`${API_BASE_URL}/api/commitments/${id}`);
        if (commRes.ok) {
          const detail = await commRes.json();
          if (detail.followup?.id) {
            targetId = detail.followup.id;
            commitmentToFollowupIdMap.set(id, targetId);
            res = await fetch(`${API_BASE_URL}/api/followup/${targetId}/approve`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify(payload),
            });
          }
        }
      } catch {
        // proceed to handleResponse below
      }
    }

    if (!res.ok) {
      return await handleResponse<{ success: boolean; message: string }>(res, () => {
        if (localFollowups[id]) {
          localFollowups[id].approved = true;
          localFollowups[id].draft = message;
          localFollowups[id].lastUpdated = 'Approved by user';
        }
        return {
          success: true,
          message: 'Follow-up message approved and marked ready for dispatch.',
        };
      });
    }

    return {
      success: true,
      message: 'Follow-up message approved and marked ready for dispatch.',
    };
  } catch (err) {
    return await handleNetworkError<{ success: boolean; message: string }>(err, () => {
      if (localFollowups[id]) {
        localFollowups[id].approved = true;
        localFollowups[id].draft = message;
        localFollowups[id].lastUpdated = 'Approved by user';
      }
      return {
        success: true,
        message: 'Follow-up message approved and marked ready for dispatch.',
      };
    });
  }
}
