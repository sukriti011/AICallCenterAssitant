import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import {
  ChevronRight, Download, ChevronDown, User, Calendar, Clock, Phone, Headphones,
  CheckCircle2, Circle, Tag, AlertCircle, RotateCcw, Loader2, ChevronLeft,
  Search, SlidersHorizontal, FileText, Check, X, Plus,
} from 'lucide-react';
import Sidebar from '../components/Sidebar.jsx';
import AudioPlayer from '../components/AudioPlayer.jsx';
import NewCallModal from '../components/NewCallModal.jsx';
import { getCallById, updateUploadedCall } from '../data/callStore.js';
import { getCallAnalysis } from '../data/mockData.js';
import { analyzeCall } from '../api/callCenter.js';
import useApi from '../hooks/useApi.js';

// ── Score helpers ─────────────────────────────────────────────────────────────
function scoreColor(v) {
  if (v >= 0.80) return 'bg-green-500';
  if (v >= 0.65) return 'bg-yellow-400';
  return 'bg-red-500';
}
function scoreLabelColor(v) {
  if (v >= 0.80) return 'text-green-600';
  if (v >= 0.65) return 'text-yellow-600';
  return 'text-red-500';
}
function overallLabel(v) {
  if (v >= 0.90) return 'Excellent';
  if (v >= 0.80) return 'Good';
  if (v >= 0.65) return 'Fair';
  return 'Poor';
}

function StatusBadge({ value }) {
  if (value === 'Success')      return <span className="px-2 py-0.5 rounded-full bg-green-100 text-green-700 text-[11px] font-medium">Success</span>;
  if (value === 'Not Required') return <span className="px-2 py-0.5 rounded-full bg-slate-100 text-slate-500 text-[11px] font-medium">Not Required</span>;
  return <span className="px-2 py-0.5 rounded-full bg-blue-100 text-blue-700 text-[11px] font-medium">{value}</span>;
}

function BoolBadge({ value }) {
  return value
    ? <span className="px-2 py-0.5 rounded-full bg-red-100 text-red-600 text-[11px] font-medium">Yes</span>
    : <span className="px-2 py-0.5 rounded-full bg-green-100 text-green-700 text-[11px] font-medium">No</span>;
}

function RiskPill({ value }) {
  const map = {
    Low:    'bg-green-100 text-green-700',
    Medium: 'bg-yellow-100 text-yellow-700',
    High:   'bg-red-100 text-red-600',
  };
  return <span className={`px-2 py-0.5 rounded-full text-[11px] font-medium ${map[value] || map.Low}`}>{value}</span>;
}

// ── Transcript tab ─────────────────────────────────────────────────────────────
function TranscriptTab({ transcript, activeTab, setActiveTab }) {
  const [search, setSearch] = useState('');

  const rawText = transcript.map((m) => `${m.role}: ${m.text}`).join('\n');

  const filteredMessages =
    search.trim()
      ? transcript.filter((m) => m.text.toLowerCase().includes(search.toLowerCase()))
      : transcript;

  return (
    <div>
      {/* Tab bar */}
      <div className="flex items-center justify-between border-b border-slate-100 mb-3">
        <div className="flex gap-0">
          {['Transcript', 'Timestamps', 'Raw Transcript'].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-2 text-[13px] font-medium border-b-2 -mb-px transition-colors ${
                activeTab === tab
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-slate-500 hover:text-slate-700'
              }`}
            >
              {tab}
            </button>
          ))}
        </div>
        <div className="flex items-center gap-2 pb-2">
          <div className="relative">
            <Search size={14} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search in transcript..."
              className="pl-7 pr-3 py-1.5 border border-slate-200 rounded-lg text-[12px] text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500 w-44"
            />
          </div>
          <button className="p-1.5 border border-slate-200 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-50">
            <SlidersHorizontal size={14} />
          </button>
        </div>
      </div>

      {/* Tab content */}
      {activeTab === 'Raw Transcript' ? (
        <pre className="text-[12px] text-slate-600 bg-slate-50 rounded-lg p-4 overflow-auto min-h-[180px] max-h-[20rem] font-mono whitespace-pre-wrap leading-relaxed">
          {rawText}
        </pre>
      ) : (
        <div className="space-y-2 overflow-y-auto min-h-[180px] max-h-[20rem] pr-1">
          {filteredMessages.map((msg, i) => (
            <div key={i} className="flex items-start gap-3">
              {activeTab === 'Timestamps' && (
                <span className="text-[11px] text-slate-400 font-mono mt-0.5 w-10 flex-shrink-0">{msg.time}</span>
              )}
              <span
                className={`flex-shrink-0 px-2 py-0.5 rounded-full text-[11px] font-semibold mt-0.5 ${
                  msg.role === 'Agent'
                    ? 'bg-blue-100 text-blue-700'
                    : msg.role === 'Customer'
                      ? 'bg-green-100 text-green-700'
                      : 'bg-slate-100 text-slate-500'
                }`}
              >
                {msg.role}
              </span>
              <p className="text-[13px] text-slate-700 leading-relaxed flex-1">{msg.text}</p>
            </div>
          ))}
          {filteredMessages.length === 0 && (
            <p className="text-center text-slate-400 text-[13px] py-8">No messages match your search.</p>
          )}
        </div>
      )}
    </div>
  );
}

// ── Progress bar ───────────────────────────────────────────────────────────────
function ScoreBar({ name, score }) {
  const pct = Math.round(score * 100);
  return (
    <div className="space-y-0.5">
      <div className="flex justify-between items-center">
        <span className="text-[13px] text-slate-600">{name}</span>
        <span className={`text-[13px] font-semibold ${scoreLabelColor(score)}`}>{pct}%</span>
      </div>
      <div className="h-1.5 bg-slate-100 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all ${scoreColor(score)}`}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}

// ── Workflow step ──────────────────────────────────────────────────────────────
function WorkflowStep({ step, duration, status, isLast, isClock }) {
  const ok = status === 'ok';
  const escalated = status === 'escalated';
  return (
    <div className="flex items-center gap-2 flex-shrink-0">
      <div className="border border-slate-200 rounded-lg px-2 py-1.5 w-[70px] min-w-[70px] h-[76px] flex flex-col items-center justify-center gap-1 bg-white">
        <div
          className={`w-7 h-7 rounded-full flex items-center justify-center ${
            isClock ? 'bg-blue-50' : ok ? 'bg-green-50' : escalated ? 'bg-orange-50' : 'bg-red-50'
          }`}
        >
          {isClock ? (
            <Clock size={13} className="text-blue-500" />
          ) : ok ? (
            <Check size={12} className="text-green-600" strokeWidth={2.5} />
          ) : (
            <AlertCircle size={12} className="text-orange-500" />
          )}
        </div>
        <p className="text-[10px] font-semibold text-slate-700 text-center leading-tight">{step}</p>
        <p className="text-[10px] text-slate-400">{duration}</p>
      </div>
      {!isLast && (
        <ChevronRight size={12} className="text-slate-300 flex-shrink-0" />
      )}
    </div>
  );
}

// ── Main component ─────────────────────────────────────────────────────────────
export default function CallDetails() {
  const { callId }  = useParams();
  const navigate    = useNavigate();
  const [activeTab, setActiveTab]              = useState('Transcript');
  const [jsonOpen, setJsonOpen]                = useState(false);
  const [showNewCallModal, setShowNewCallModal] = useState(false);
  const [actionItems, setActionItems]          = useState([]);
  const { data: liveData, loading, error, execute } = useApi();

  const mockAnalysis = getCallById(callId) || getCallAnalysis(callId);

  if (!mockAnalysis) {
    return (
      <div className="flex min-h-screen bg-[#F0F4F8]">
        <Sidebar />
        <main className="ml-60 flex-1 flex items-center justify-center">
          <div className="text-center">
            <p className="text-xl font-semibold text-slate-700">Call not found</p>
            <p className="text-slate-500 mt-1 mb-4">{callId} does not exist in the records.</p>
            <button onClick={() => navigate('/dashboard')} className="px-4 py-2 bg-blue-600 text-white rounded-lg text-[14px] font-medium hover:bg-blue-700">
              Back to Dashboard
            </button>
          </div>
        </main>
      </div>
    );
  }

  // Merge live analysis data over mock data if re-analyzed
  const analysis = liveData
    ? mergeAnalysis(mockAnalysis, liveData)
    : mockAnalysis;

  // Sync action items into local state (re-runs on new call or after Re-Analyze)
  useEffect(() => {
    setActionItems(analysis.action_items ?? []);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [callId, liveData]);

  function toggleActionItem(i) {
    setActionItems((prev) => {
      const next = prev.map((item, idx) =>
        idx === i ? { ...item, done: !item.done } : item
      );
      if (mockAnalysis?._uploaded) updateUploadedCall(callId, { action_items: next });
      return next;
    });
  }

  const overallPct = Math.round(analysis.quality_score.overall * 100);

  const handleReAnalyze = () => {
    // For uploaded TXT calls, use the stored raw text; otherwise join transcript array
    const rawTranscript = mockAnalysis._rawText
      ? mockAnalysis._rawText
      : Array.isArray(mockAnalysis.transcript)
        ? mockAnalysis.transcript.map((m) => `${m.role}: ${m.text}`).join('\n')
        : '';
    execute(() =>
      analyzeCall({
        session_id:  callId,
        transcript:  rawTranscript,
        customer_id: analysis.customer_id,
      })
    );
  };

  // Persist Re-Analyze results for uploaded calls back to localStorage
  useEffect(() => {
    if (!liveData || !mockAnalysis?._uploaded) return;
    const merged = mergeAnalysis(mockAnalysis, liveData);
    // Extract and normalize sentiment from key_points e.g. "Sentiment: Positive"
    const sentimentKp = liveData.summary?.key_points
      ?.find((kp) => kp.toLowerCase().startsWith('sentiment:'));
    const rawSentiment = sentimentKp
      ? sentimentKp.split(':').slice(1).join(':').trim().toLowerCase()
      : null;
    const normSentiment =
      rawSentiment === 'positive' ? 'Positive'
      : rawSentiment === 'negative' ? 'Negative'
      : rawSentiment === 'neutral' ? 'Neutral'
      : null;
    updateUploadedCall(callId, {
      ...merged,
      qa_score:       liveData.quality_score?.overall_score ?? mockAnalysis.qa_score,
      sentiment:      normSentiment ?? mockAnalysis.sentiment,
      guardrail_risk: liveData.guardrail?.compliance_risk   ? 'High' : 'Low',
      mcp_actions:    liveData.mcp_actions?.length ? liveData.mcp_actions : merged.mcp_actions,
    });
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [liveData]);

  return (
    <div className="flex min-h-screen bg-[#F0F4F8]">
      <Sidebar />

      <main className="ml-60 flex-1 min-w-0 px-8 py-3">
        {/* Breadcrumb */}
        <nav className="flex items-center gap-1.5 text-[12px] text-slate-400 mb-2">
          <Link to="/dashboard" className="hover:text-slate-600">Dashboard</Link>
          <ChevronRight size={13} />
          <Link to="/dashboard" className="hover:text-slate-600">Call Analyze</Link>
          <ChevronRight size={13} />
          <span className="text-slate-600 font-medium">Call Details</span>
        </nav>

        {/* Page header */}
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-3">
            <button
              onClick={() => navigate('/dashboard')}
              className="flex items-center justify-center w-8 h-8 rounded-lg border border-slate-200 bg-white hover:bg-slate-50 text-slate-500"
            >
              <ChevronLeft size={16} />
            </button>
            <h1 className="text-[26px] font-bold text-slate-800">Call Details – {callId}</h1>
          </div>
          <div className="flex items-center gap-2">
            {/* New Call button */}
            <button
              onClick={() => setShowNewCallModal(true)}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 rounded-lg text-[13px] text-white font-medium hover:bg-blue-700 transition-colors shadow-sm"
            >
              <Plus size={14} />
              New Call
            </button>
            {/* Re-Analyze button */}
            <button
              onClick={handleReAnalyze}
              disabled={loading}
              className="flex items-center gap-2 px-4 py-2 border border-slate-200 bg-white rounded-lg text-[13px] text-slate-700 font-medium hover:bg-slate-50 transition-colors disabled:opacity-60"
            >
              {loading ? (
                <Loader2 size={14} className="animate-spin text-blue-600" />
              ) : (
                <RotateCcw size={14} className="text-slate-500" />
              )}
              {loading ? 'Analyzing...' : 'Re-Analyze'}
            </button>
            {/* Download */}
            <button className="flex items-center gap-2 px-4 py-2 bg-blue-600 rounded-lg text-[13px] text-white font-medium hover:bg-blue-700 shadow-sm">
              <Download size={14} />
              Download
              <ChevronDown size={13} />
            </button>
          </div>
        </div>

        {/* Error banner */}
        {error && (
          <div className="flex items-center gap-2 mb-4 px-4 py-3 bg-red-50 border border-red-200 rounded-lg text-[13px] text-red-700">
            <AlertCircle size={15} />
            <span>{error}</span>
            <button onClick={() => {}} className="ml-auto text-red-400 hover:text-red-600">
              <X size={14} />
            </button>
          </div>
        )}

        {/* Success banner */}
        {liveData && !error && (
          <div className="flex items-center gap-2 mb-4 px-4 py-3 bg-green-50 border border-green-200 rounded-lg text-[13px] text-green-700">
            <CheckCircle2 size={15} />
            Re-analysis complete. Displaying updated results.
          </div>
        )}

        {/* Metadata row */}
        <div className="flex items-center gap-3 flex-wrap mb-3">
          <MetaPill icon={<User size={13} />}       label="Agent"       value={analysis.agent_name} />
          <MetaPill icon={<User size={13} />}       label="Customer ID" value={analysis.customer_id} />
          <MetaPill icon={<Calendar size={13} />}   label="Date"        value={analysis.datetime} />
          <MetaPill icon={<Clock size={13} />}      label="Duration"    value={analysis.duration} />
          <MetaPill icon={<Phone size={13} />}      label="Source"      value={analysis.source} />
        </div>

        {/* Main grid */}
        <div className="flex gap-5 mb-4 items-start">
          {/* LEFT panel — 50% */}
          <div className="flex-[5] min-w-0 space-y-3">
            {/* Audio player */}
            <AudioPlayer src={analysis.audio_src} />

            {/* Transcript */}
            <div className="bg-white rounded-xl shadow-card border border-slate-100 p-5">
              <TranscriptTab
                transcript={analysis.transcript}
                activeTab={activeTab}
                setActiveTab={setActiveTab}
              />
            </div>
          </div>

          {/* RIGHT panel — 50% */}
          <div className="flex-[5] min-w-0 space-y-3">
            {/* Summary — full width */}
            <Card title="Summary" icon={<FileText size={15} className="text-slate-400" />}>
              <p className="text-[13px] text-slate-600 leading-relaxed">{analysis.summary}</p>
            </Card>

            {/* Row 2: Key Points + QA Score side by side */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Card title="Key Points">
                <ul className="space-y-2">
                  {analysis.key_points.map((kp, i) => (
                    <li key={i} className="flex items-start gap-2">
                      <span className="w-1.5 h-1.5 rounded-full bg-blue-500 mt-1.5 flex-shrink-0" />
                      <span className="text-[13px] text-slate-600">
                        <span className="font-semibold text-slate-700">{kp.label}:</span>{' '}
                        {kp.value}
                      </span>
                    </li>
                  ))}
                </ul>
              </Card>

              <Card
                title="QA Score"
                aside={
                  <div className="flex items-baseline gap-1.5">
                    <span className={`text-2xl font-bold ${scoreLabelColor(analysis.quality_score.overall)}`}>
                      {overallPct}%
                    </span>
                    <span className={`text-[13px] font-medium ${scoreLabelColor(analysis.quality_score.overall)}`}>
                      {overallLabel(analysis.quality_score.overall)}
                    </span>
                  </div>
                }
              >
                <div className="space-y-2">
                  {analysis.quality_score.dimensions.map((d) => (
                    <ScoreBar key={d.name} name={d.name} score={d.score} />
                  ))}
                </div>
              </Card>
            </div>

            {/* Row 3: Action Items + Tags side by side */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Card title="Action Items">
                <ul className="space-y-2">
                  {actionItems.map((item, i) => (
                    <li
                      key={i}
                      onClick={() => toggleActionItem(i)}
                      className="flex items-start gap-2 cursor-pointer select-none rounded px-1 -mx-1 hover:bg-slate-50 transition-colors"
                    >
                      {item.done ? (
                        <CheckCircle2 size={16} className="text-green-500 mt-0.5 flex-shrink-0" />
                      ) : (
                        <Circle size={16} className="text-slate-300 mt-0.5 flex-shrink-0" />
                      )}
                      <span className={`text-[13px] leading-relaxed ${item.done ? 'text-slate-400 line-through' : 'text-slate-600'}`}>
                        {item.text}
                      </span>
                    </li>
                  ))}
                </ul>
              </Card>

              <Card title="Tags">
                <div className="flex flex-wrap gap-2">
                  {analysis.tags.map((tag) => (
                    <span
                      key={tag}
                      className="inline-flex items-center gap-1 px-2.5 py-1 bg-blue-50 text-blue-700 rounded-full text-[12px] font-medium"
                    >
                      <Tag size={11} />
                      {tag}
                    </span>
                  ))}
                </div>
              </Card>
            </div>
          </div>
        </div>

        {/* Bottom row: all 3 panels side by side */}
        <div className="grid grid-cols-4 gap-4 mb-4">
          {/* Agent Workflow Trace — wider column */}
          <div className="col-span-2 bg-white rounded-xl shadow-card border border-slate-100 p-3">
            <div className="flex items-center gap-2 mb-2">
              <Headphones size={15} className="text-slate-400" />
              <h3 className="text-[14px] font-semibold text-slate-700">Agent Workflow Trace</h3>
            </div>
            <div className="flex items-center flex-nowrap gap-1">
              {analysis.pipeline_trace.map((step) => (
                <WorkflowStep
                  key={step.step}
                  step={step.step}
                  duration={step.duration}
                  status={step.status}
                  isLast={false}
                />
              ))}
              <ChevronRight size={14} className="text-slate-300 flex-shrink-0" />
              <WorkflowStep
                step="Total Time"
                duration={analysis.total_time}
                status="ok"
                isClock
                isLast
              />
            </div>
          </div>

          {/* Guardrail Checks */}
          <div className="bg-white rounded-xl shadow-card border border-slate-100 p-4">
            <div className="flex items-center gap-2 mb-3">
              <span className="text-[15px]">🛡️</span>
              <h3 className="text-[14px] font-semibold text-slate-700">Guardrail Checks</h3>
            </div>
            <div className="space-y-2">
              <GuardrailRow label="PII Detected">
                <BoolBadge value={analysis.guardrail.pii_detected} />
              </GuardrailRow>
              <GuardrailRow label="Hallucination Risk">
                <RiskPill value={analysis.guardrail.hallucination_risk} />
              </GuardrailRow>
              <GuardrailRow label="Compliance Risk">
                <BoolBadge value={analysis.guardrail.compliance_risk} />
              </GuardrailRow>
              <GuardrailRow label="Confidence Score">
                <span className="text-[12px] font-semibold text-slate-700">{analysis.guardrail.confidence_score.toFixed(2)}</span>
              </GuardrailRow>
              <GuardrailRow label="Requires Human Review">
                <BoolBadge value={analysis.guardrail.requires_human_review} />
              </GuardrailRow>
            </div>
          </div>

          {/* MCP Tool Actions */}
          <div className="bg-white rounded-xl shadow-card border border-slate-100 p-4">
            <div className="flex items-center gap-2 mb-3">
              <span className="text-[15px]">🔧</span>
              <h3 className="text-[14px] font-semibold text-slate-700">MCP Tool Actions</h3>
              {!liveData?.mcp_actions?.length && (
                <span className="ml-auto text-[10px] font-medium px-2 py-0.5 rounded-full bg-slate-100 text-slate-400">
                  Mock Data
                </span>
              )}
            </div>
            <div className="space-y-2.5">
              {analysis.mcp_actions.map((action) => {
                const isSuccess = action.status === 'Success';
                const isFailed  = action.status === 'Failed';
                return (
                  <div key={action.name} className="group flex items-start justify-between gap-2">
                    <div className="flex items-start gap-2 min-w-0">
                      {isFailed ? (
                        <AlertCircle size={14} className="text-red-400 flex-shrink-0 mt-0.5" />
                      ) : isSuccess ? (
                        <CheckCircle2 size={14} className="text-green-500 flex-shrink-0 mt-0.5" />
                      ) : (
                        <Circle size={14} className="text-slate-300 flex-shrink-0 mt-0.5" />
                      )}
                      <div className="min-w-0">
                        <span className="text-[12px] text-slate-600 font-medium">{action.name}</span>
                        {action.details && (
                          <p className="text-[11px] text-slate-400 mt-0.5 leading-snug max-w-[220px] hidden group-hover:block">
                            {action.details}
                          </p>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center gap-1.5 flex-shrink-0">
                      {action.duration_ms != null && action.duration_ms > 0 && (
                        <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-50 text-slate-400 font-mono">
                          {action.duration_ms} ms
                        </span>
                      )}
                      <StatusBadge value={action.status} />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Raw JSON Output */}
        <div className="bg-white rounded-xl shadow-card border border-slate-100 overflow-hidden mb-2">
          <button
            onClick={() => setJsonOpen((o) => !o)}
            className="w-full flex items-center justify-between px-5 py-4 hover:bg-slate-50 transition-colors"
          >
            <div className="flex items-center gap-2">
              <span className="text-[13px] text-slate-500 font-mono">&lt;/&gt;</span>
              <span className="text-[14px] font-semibold text-slate-700">Raw JSON Output</span>
            </div>
            <ChevronDown size={16} className={`text-slate-400 transition-transform ${jsonOpen ? 'rotate-180' : ''}`} />
          </button>
          {jsonOpen && (
            <div className="border-t border-slate-100 px-5 py-4">
              <pre className="text-[11px] text-slate-600 bg-slate-50 rounded-lg p-4 overflow-auto max-h-80 font-mono">
                {JSON.stringify(liveData || mockAnalysis, null, 2)}
              </pre>
            </div>
          )}
        </div>
        {/* New Call Modal */}
        <NewCallModal
          isOpen={showNewCallModal}
          onClose={() => setShowNewCallModal(false)}
          onCallCreated={(newCallId) => {
            setShowNewCallModal(false);
            navigate(`/calls/${newCallId}`);
          }}
        />
      </main>
    </div>
  );
}

// ── Small reusable pieces ──────────────────────────────────────────────────────

function MetaPill({ icon, label, value }) {
  return (
    <div className="flex items-center gap-2 px-3.5 py-1.5 bg-white border border-slate-200 rounded-lg shadow-sm">
      <span className="text-slate-400">{icon}</span>
      <span className="text-[12px] text-slate-500">{label}:</span>
      <span className="text-[13px] font-semibold text-slate-700">{value}</span>
    </div>
  );
}

function Card({ title, icon, aside, children }) {
  return (
    <div className="bg-white rounded-xl shadow-card border border-slate-100 p-4">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          {icon}
          <h3 className="text-[14px] font-semibold text-slate-700">{title}</h3>
        </div>
        {aside}
      </div>
      {children}
    </div>
  );
}

function GuardrailRow({ label, children }) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-[12px] text-slate-500">{label}</span>
      {children}
    </div>
  );
}

// Merge live API response shape into mock analysis display shape
function mergeAnalysis(mock, live) {
  if (!live) return mock;
  return {
    ...mock,
    summary: live.summary?.summary ?? mock.summary,
    key_points: live.summary?.key_points?.map((kp) => {
      const [labelPart, ...rest] = kp.split(':');
      return { label: labelPart.trim(), value: rest.join(':').trim() };
    }) ?? mock.key_points,
    action_items: live.summary?.action_items?.map((t) => ({ text: t, done: false })) ?? mock.action_items,
    tags: live.summary?.tags ?? mock.tags,
    quality_score: live.quality_score
      ? {
          overall: live.quality_score.overall_score,
          label:   overallLabel(live.quality_score.overall_score),
          dimensions: [
            { name: 'Tone',               score: live.quality_score.tone_score },
            { name: 'Empathy',            score: live.quality_score.empathy_score },
            { name: 'Professionalism',    score: live.quality_score.professionalism_score },
            { name: 'Resolution Clarity', score: live.quality_score.resolution_score },
          ],
        }
      : mock.quality_score,
    pipeline_trace: live.pipeline_trace
      ? live.pipeline_trace.map((s) => ({ step: s.step, status: s.status, duration: s.duration }))
      : mock.pipeline_trace,
    total_time: live.pipeline_trace
      ? (() => {
          const total = live.pipeline_trace.reduce((sum, s) => {
            const n = parseFloat(s.duration);
            return sum + (isNaN(n) ? 0 : n);
          }, 0);
          return total > 0 ? `${total.toFixed(1)}s` : mock.total_time;
        })()
      : mock.total_time,
    mcp_actions: live.mcp_actions?.length
      ? live.mcp_actions
      : mock.mcp_actions,
  };
}
