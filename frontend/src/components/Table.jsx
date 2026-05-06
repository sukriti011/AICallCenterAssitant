import { useNavigate } from 'react-router-dom';
import { ExternalLink, ChevronUp, ChevronDown } from 'lucide-react';
import { useState } from 'react';

// ── Badge helpers ─────────────────────────────────────────────────────────────
export function QaBadge({ score }) {
  const pct = Math.round(score * 100);
  const cls =
    pct >= 80
      ? 'bg-green-100 text-green-700'
      : pct >= 65
      ? 'bg-yellow-100 text-yellow-700'
      : 'bg-red-100 text-red-600';
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-[12px] font-semibold ${cls}`}>
      {pct}%
    </span>
  );
}

export function SentimentBadge({ sentiment }) {
  const map = {
    Positive: { cls: 'bg-green-100 text-green-700',  emoji: '😊' },
    Neutral:  { cls: 'bg-yellow-50 text-yellow-700', emoji: '😐' },
    Negative: { cls: 'bg-red-100 text-red-600',      emoji: '😞' },
  };
  const { cls, emoji } = map[sentiment] || map.Neutral;
  return (
    <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[12px] font-medium ${cls}`}>
      <span>{emoji}</span>
      {sentiment}
    </span>
  );
}

export function RiskBadge({ risk }) {
  const map = {
    Low:    'bg-green-100 text-green-700',
    Medium: 'bg-orange-100 text-orange-600',
    High:   'bg-red-100 text-red-600',
  };
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-[12px] font-medium ${map[risk] || map.Low}`}>
      {risk}
    </span>
  );
}

// ── Table ─────────────────────────────────────────────────────────────────────
export default function Table({ records }) {
  const navigate = useNavigate();
  const [page, setPage]     = useState(1);
  const [sortDir, setSortDir] = useState('desc');
  const ROWS_PER_PAGE = 10;

  const sorted = [...records].sort((a, b) => {
    return sortDir === 'desc'
      ? new Date(b.datetime) - new Date(a.datetime)
      : new Date(a.datetime) - new Date(b.datetime);
  });

  const totalPages = Math.max(1, Math.ceil(sorted.length / ROWS_PER_PAGE));
  const pageRecords = sorted.slice((page - 1) * ROWS_PER_PAGE, page * ROWS_PER_PAGE);

  return (
    <div className="bg-white rounded-xl shadow-card border border-slate-100 overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full text-[13px]">
          <thead>
            <tr className="bg-slate-50 border-b border-slate-100">
              <Th>Call ID</Th>
              <Th>Agent</Th>
              <Th>Customer ID</Th>
              <Th>
                <button
                  className="flex items-center gap-1 uppercase tracking-wide text-[11px] font-semibold text-slate-500 hover:text-slate-700"
                  onClick={() => setSortDir((d) => (d === 'desc' ? 'asc' : 'desc'))}
                >
                  Date
                  {sortDir === 'desc' ? <ChevronDown size={13} /> : <ChevronUp size={13} />}
                </button>
              </Th>
              <Th>Duration</Th>
              <Th>QA Score</Th>
              <Th>Sentiment</Th>
              <Th>Escalation</Th>
              <Th>Risk Level</Th>
              <Th>Actions</Th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-50">
            {pageRecords.length === 0 ? (
              <tr>
                <td colSpan={10} className="py-12 text-center text-slate-400 text-[14px]">
                  No calls match the current filters.
                </td>
              </tr>
            ) : (
              pageRecords.map((row) => (
                <tr key={row.call_id} className="hover:bg-slate-50/50 transition-colors">
                  <td className="px-5 py-2">
                    <button
                      className="text-blue-600 font-semibold hover:underline"
                      onClick={() => navigate(`/calls/${row.call_id}`)}
                    >
                      {row.call_id}
                    </button>
                  </td>
                  <td className="px-5 py-2 text-slate-700 font-medium">{row.agent_name}</td>
                  <td className="px-5 py-2 text-slate-500">{row.customer_id}</td>
                  <td className="px-5 py-2 text-slate-500 whitespace-nowrap">{row.datetime}</td>
                  <td className="px-5 py-2 text-slate-500 font-mono">{row.duration}</td>
                  <td className="px-5 py-2">
                    <QaBadge score={row.qa_score} />
                  </td>
                  <td className="px-5 py-2">
                    <SentimentBadge sentiment={row.sentiment} />
                  </td>
                  <td className="px-5 py-2 text-slate-600">
                    {row.escalation_flag ? (
                      <span className="text-red-500 font-medium">Yes</span>
                    ) : (
                      <span className="text-slate-400">No</span>
                    )}
                  </td>
                  <td className="px-5 py-2">
                    <RiskBadge risk={row.guardrail_risk} />
                  </td>
                  <td className="px-5 py-2">
                    <button
                      onClick={() => navigate(`/calls/${row.call_id}`)}
                      className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-200 text-blue-600 text-[12px] font-medium hover:bg-blue-50 hover:border-blue-200 transition-colors"
                    >
                      View Details
                      <ExternalLink size={12} />
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      <div className="flex items-center justify-between px-5 py-2 border-t border-slate-100 bg-white">
        <span className="text-[12px] text-slate-500">
          Showing {pageRecords.length === 0 ? 0 : (page - 1) * ROWS_PER_PAGE + 1} to{' '}
          {Math.min(page * ROWS_PER_PAGE, records.length)} of {records.length} calls
        </span>
        <div className="flex items-center gap-1.5">
          <PageBtn
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page === 1}
          >
            ‹
          </PageBtn>
          {Array.from({ length: totalPages }, (_, i) => i + 1).map((n) => (
            <PageBtn
              key={n}
              active={n === page}
              onClick={() => setPage(n)}
            >
              {n}
            </PageBtn>
          ))}
          <PageBtn
            onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
            disabled={page === totalPages}
          >
            ›
          </PageBtn>
        </div>
        <span className="text-[12px] text-slate-500">Rows per page: {ROWS_PER_PAGE}</span>
      </div>
    </div>
  );
}

function Th({ children }) {
  return (
    <th className="px-5 py-2 text-left text-[11px] font-semibold text-slate-500 uppercase tracking-wide whitespace-nowrap">
      {children}
    </th>
  );
}

function PageBtn({ children, active, disabled, onClick }) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`w-7 h-7 rounded text-[13px] font-medium flex items-center justify-center transition-colors ${
        active
          ? 'bg-blue-600 text-white'
          : disabled
          ? 'text-slate-300 cursor-not-allowed'
          : 'text-slate-600 hover:bg-slate-100'
      }`}
    >
      {children}
    </button>
  );
}
