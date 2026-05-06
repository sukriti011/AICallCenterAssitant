import { useState, useMemo } from 'react';
import { CalendarDays, ChevronDown, Phone, Star, TrendingUp, Frown, Shield, User, Filter, X } from 'lucide-react';
import Sidebar from '../components/Sidebar.jsx';
import StatsCard from '../components/StatsCard.jsx';
import Table from '../components/Table.jsx';
import { getAllCalls } from '../data/callStore.js';
import { getAllCallRecords, getDashboardStats } from '../data/mockData.js';

const ALL_AGENTS = ['All Agents', ...Array.from(new Set(getAllCallRecords().map((r) => r.agent_name))).sort()];
const ALL_SENTIMENTS = ['All', 'Positive', 'Neutral', 'Negative'];

export default function ManagerDashboard() {
  const allRecords = getAllCalls();
  const stats      = getDashboardStats(allRecords);

  const [agentFilter,     setAgentFilter]     = useState('All Agents');
  const [sentimentFilter, setSentimentFilter] = useState('All');
  const [applied,         setApplied]         = useState({ agent: 'All Agents', sentiment: 'All' });

  const filtered = useMemo(() => {
    return allRecords.filter((r) => {
      const agentOk     = applied.agent     === 'All Agents' || r.agent_name === applied.agent;
      const sentimentOk = applied.sentiment === 'All'        || r.sentiment  === applied.sentiment;
      return agentOk && sentimentOk;
    });
  }, [applied, allRecords]);

  const handleApply = () => setApplied({ agent: agentFilter, sentiment: sentimentFilter });

  const handleClear = () => {
    setAgentFilter('All Agents');
    setSentimentFilter('All');
    setApplied({ agent: 'All Agents', sentiment: 'All' });
  };

  const hasActiveFilter = applied.agent !== 'All Agents' || applied.sentiment !== 'All';

  return (
    <div className="flex min-h-screen bg-[#F0F4F8]">
      <Sidebar />

      {/* Main content */}
      <main className="ml-60 flex-1 min-w-0 px-8 py-4">
        {/* Page header */}
        <div className="flex items-start justify-between mb-4">
          <div>
            <h1 className="text-[28px] font-bold text-slate-800 leading-tight">Manager Dashboard</h1>
            <p className="text-[14px] text-slate-500 mt-1">Monitor call center performance and review conversations</p>
          </div>
          <div className="flex items-center gap-3 mt-1 flex-shrink-0">
            {/* Date range pill */}
            <button className="flex items-center gap-2 px-3.5 py-2 bg-white border border-slate-200 rounded-full text-[13px] text-slate-600 font-medium shadow-sm hover:shadow-md transition-shadow">
              <CalendarDays size={15} className="text-slate-400" />
              Apr 20 – Apr 29, 2026
              <ChevronDown size={14} className="text-slate-400" />
            </button>
            {/* User profile pill */}
            <button className="flex items-center gap-2 px-3.5 py-2 bg-white border border-slate-200 rounded-full text-[13px] shadow-sm hover:shadow-md transition-shadow">
              <div className="w-6 h-6 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0">
                <User size={13} className="text-blue-600" />
              </div>
              <div className="text-left leading-tight">
                <p className="font-semibold text-slate-700 text-[12px]">Manager</p>
                <p className="text-slate-400 text-[11px]">Team Lead</p>
              </div>
              <ChevronDown size={14} className="text-slate-400" />
            </button>
          </div>
        </div>

        {/* Stats cards */}
        <div className="flex gap-4 mb-4">
          <StatsCard icon={Phone}     label="Total Calls"        value={stats.total}           color="blue"   />
          <StatsCard icon={Star}      label="Avg QA Score"       value={`${stats.avgQa}%`}     color="green"  />
          <StatsCard icon={TrendingUp} label="Escalations"       value={stats.escalations}     color="orange" />
          <StatsCard icon={Frown}     label="Negative Sentiment" value={stats.negativeSentiment} color="red"  />
          <StatsCard icon={Shield}    label="Guardrail Risk Calls" value={stats.guardrailRisk}  color="purple" />
        </div>

        {/* Filters */}
        <div className="bg-white rounded-xl shadow-card border border-slate-100 px-5 py-3 mb-4">
          <div className="flex items-end gap-4 flex-wrap">
            {/* Agent */}
            <div className="flex flex-col gap-1.5">
              <label className="text-[12px] font-medium text-slate-500">Agent</label>
              <div className="relative">
                <select
                  value={agentFilter}
                  onChange={(e) => setAgentFilter(e.target.value)}
                  className="appearance-none w-44 pl-3 pr-8 py-2 border border-slate-200 rounded-lg text-[13px] text-slate-700 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  {ALL_AGENTS.map((a) => (
                    <option key={a} value={a}>{a}</option>
                  ))}
                </select>
                <ChevronDown size={14} className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" />
              </div>
            </div>

            {/* Sentiment */}
            <div className="flex flex-col gap-1.5">
              <label className="text-[12px] font-medium text-slate-500">Sentiment</label>
              <div className="relative">
                <select
                  value={sentimentFilter}
                  onChange={(e) => setSentimentFilter(e.target.value)}
                  className="appearance-none w-36 pl-3 pr-8 py-2 border border-slate-200 rounded-lg text-[13px] text-slate-700 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  {ALL_SENTIMENTS.map((s) => (
                    <option key={s} value={s}>{s}</option>
                  ))}
                </select>
                <ChevronDown size={14} className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" />
              </div>
            </div>

            {/* Spacer */}
            <div className="flex-1" />

            {/* Clear */}
            <button
              onClick={handleClear}
              className="flex items-center gap-1.5 px-4 py-2 border border-slate-200 rounded-lg text-[13px] text-slate-600 font-medium hover:bg-slate-50 transition-colors"
            >
              {hasActiveFilter && <X size={13} />}
              Clear
            </button>

            {/* Apply Filters */}
            <button
              onClick={handleApply}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 rounded-lg text-[13px] text-white font-medium hover:bg-blue-700 transition-colors shadow-sm"
            >
              <Filter size={14} />
              Apply Filters
            </button>
          </div>
        </div>

        {/* Active filter chips */}
        {hasActiveFilter && (
          <div className="flex items-center gap-2 mb-3 flex-wrap">
            <span className="text-[12px] text-slate-500">Active filters:</span>
            {applied.agent !== 'All Agents' && (
              <Chip label={`Agent: ${applied.agent}`} onRemove={() => { setApplied((p) => ({ ...p, agent: 'All Agents' })); setAgentFilter('All Agents'); }} />
            )}
            {applied.sentiment !== 'All' && (
              <Chip label={`Sentiment: ${applied.sentiment}`} onRemove={() => { setApplied((p) => ({ ...p, sentiment: 'All' })); setSentimentFilter('All'); }} />
            )}
          </div>
        )}

        {/* Table */}
        <Table records={filtered} />
      </main>
    </div>
  );
}

function Chip({ label, onRemove }) {
  return (
    <span className="inline-flex items-center gap-1.5 px-2.5 py-1 bg-blue-50 text-blue-700 rounded-full text-[12px] font-medium">
      {label}
      <button onClick={onRemove} className="hover:text-blue-900">
        <X size={11} />
      </button>
    </span>
  );
}
