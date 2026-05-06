import { getAllCallRecords, getCallAnalysis } from './mockData.js';

const STORAGE_KEY = 'call_center_uploaded_calls';

// ── Helpers ───────────────────────────────────────────────────────────────────

function loadUploaded() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
  } catch {
    return [];
  }
}

function saveUploaded(calls) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(calls));
}

// ── Public API ────────────────────────────────────────────────────────────────

/** Returns next available call ID (e.g. "CALL-011") */
export function generateNextCallId() {
  const mockIds     = getAllCallRecords().map((r) => r.call_id);
  const uploadedIds = loadUploaded().map((r) => r.call_id);
  const allIds      = [...mockIds, ...uploadedIds];

  const nums = allIds
    .map((id) => {
      const m = id.match(/^CALL-(\d+)$/);
      return m ? parseInt(m[1], 10) : 0;
    })
    .filter(Boolean);

  const max = nums.length > 0 ? Math.max(...nums) : 0;
  return `CALL-${String(max + 1).padStart(3, '0')}`;
}

/** Merged call records: mock + uploaded (for dashboard table) */
export function getAllCalls() {
  return [...getAllCallRecords(), ...loadUploaded()];
}

/** Full call analysis object for a given ID.
 *  Checks uploaded calls first, then falls back to mockData. */
export function getCallById(callId) {
  const uploaded = loadUploaded().find((c) => c.call_id === callId);
  if (uploaded) return uploaded;
  return getCallAnalysis(callId);
}

// ── Transcript parser ────────────────────────────────────────────────────────

/**
 * Convert raw TXT content into a structured transcript array.
 * Handles speaker labels:
 *   Agent: ...   Agent - ...   [Agent] ...   Agent(...): ...
 *   Customer: ...  Customer - ...  [Customer] ...  Customer(...): ...
 * Falls back to role 'Unknown' when no speaker label is detected.
 */
export function parseTranscriptText(rawText) {
  const normalised = rawText.replace(/\r\n/g, '\n').replace(/\r/g, '\n');
  const lines = normalised.split('\n').filter((l) => l.trim());

  // Regex: matches Agent / Customer speaker prefixes in common formats
  const AGENT_RE    = /^(?:\[Agent\]|Agent\s*[-\u2013:(]|Agent\b[^:]*:)\s*/i;
  const CUSTOMER_RE = /^(?:\[Customer\]|Customer\s*[-\u2013:(]|Customer\b[^:]*:)\s*/i;

  const hasSpeakerLabels = lines.some(
    (l) => AGENT_RE.test(l) || CUSTOMER_RE.test(l)
  );

  function toTime(index) {
    const totalSecs = index * 15;
    return `${String(Math.floor(totalSecs / 60)).padStart(2, '0')}:${String(totalSecs % 60).padStart(2, '0')}`;
  }

  if (hasSpeakerLabels) {
    const entries = [];
    let current = null;

    for (const line of lines) {
      const isAgent    = AGENT_RE.test(line);
      const isCustomer = CUSTOMER_RE.test(line);

      if (isAgent || isCustomer) {
        if (current) entries.push(current);
        const role = isAgent ? 'Agent' : 'Customer';
        const text = line.replace(isAgent ? AGENT_RE : CUSTOMER_RE, '').trim();
        current = { time: toTime(entries.length), role, text };
      } else if (current) {
        // Continuation line — append to the previous speaker's turn
        current.text += ' ' + line.trim();
      } else {
        // Line before any speaker label
        entries.push({ time: toTime(entries.length), role: 'Unknown', text: line.trim() });
      }
    }
    if (current) entries.push(current);
    return entries;
  }

  // Plain text without speaker labels — one row per non-empty line
  return lines.map((line, i) => ({
    time: toTime(i),
    role: 'Unknown',
    text: line.trim(),
  }));
}

// ─────────────────────────────────────────────────────────────────────────────

/** Creates a new call entry from a user-uploaded file, persists to localStorage,
 *  and returns the newly generated call ID.
 *
 * @param {File}   file     - The File object selected by the user
 * @param {'audio'|'transcript'} type - Upload category
 * @param {string} [rawText]          - Pre-read text content (TXT transcripts)
 * @param {string} [audioSrc]         - Blob URL for audio playback (audio uploads only)
 * @returns {string} The new call ID
 */
export function addUploadedCall(file, type, rawText, audioSrc) {
  const callId     = generateNextCallId();
  const uploadNum  = callId.replace('CALL-', '');
  const now        = new Date();
  const dateStr    = now.toLocaleDateString('en-US', {
    month: 'short', day: 'numeric', year: 'numeric',
  });
  const timeStr = now.toLocaleTimeString('en-US', {
    hour: '2-digit', minute: '2-digit',
  });

  const transcriptEntries = rawText
    ? parseTranscriptText(rawText)
    : [
        {
          time: '00:00',
          role: 'System',
          text: `Uploaded file: ${file.name}. Analysis pending.`,
        },
      ];

  const newCall = {
    // ── Record fields (dashboard table) ──────────────────────────────────────
    call_id:        callId,
    agent_name:     'Uploaded Call',
    customer_id:    `CUST-UPLOAD-${uploadNum}`,
    datetime:       `${dateStr} ${timeStr}`,
    duration:       'Pending',
    qa_score:       0,
    sentiment:      'Pending',
    escalation_flag: false,
    guardrail_risk: 'Pending',
    source:         type === 'audio' ? 'Audio Upload' : 'Transcript Upload',

    // ── Analysis fields (call details page) ──────────────────────────────────
    audio_src:   audioSrc || null,
    transcript:  transcriptEntries,
    summary:     'This call was uploaded and is ready for analysis. Click Re-Analyze to process.',
    key_points:  [],
    action_items:[],
    tags:        ['Uploaded'],
    quality_score: {
      overall:    0,
      label:      'Pending',
      dimensions: [],
    },
    guardrail: {
      pii_detected:        false,
      hallucination_risk:  'N/A',
      compliance_risk:     false,
      confidence_score:    0,
      requires_human_review: false,
    },
    mcp_actions:    [],
    pipeline_trace: [],
    total_time:     'N/A',
    routing: {
      route:        'Uploaded',
      used_fallback: false,
      reason:       'Manual upload',
    },

    // ── Upload metadata ───────────────────────────────────────────────────────
    _uploaded: true,
    _filename: file.name,
    _fileType: type,
    _rawText:  rawText || null,
  };

  const existing = loadUploaded();
  saveUploaded([...existing, newCall]);

  return callId;
}

/** Merge updates into an existing uploaded call in localStorage.
 *  Used to persist Re-Analyze results so the dashboard reflects live data. */
export function updateUploadedCall(callId, updates) {
  const existing = loadUploaded();
  const updated  = existing.map((c) =>
    c.call_id === callId ? { ...c, ...updates } : c
  );
  saveUploaded(updated);
}
