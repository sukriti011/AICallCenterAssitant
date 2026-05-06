import { NavLink } from 'react-router-dom';
import { BarChart2, PhoneIncoming, Phone } from 'lucide-react';

const NAV_ITEMS = [
  { label: 'Dashboard',    to: '/dashboard', icon: BarChart2 },
  { label: 'Call Analyze', to: '/calls',     icon: PhoneIncoming },
];

export default function Sidebar() {
  return (
    <aside className="fixed top-0 left-0 h-screen w-60 bg-white border-r border-slate-200 flex flex-col z-20 select-none">
      {/* Logo */}
      <div className="flex items-center gap-3 px-5 py-5 border-b border-slate-100">
        <img src="/icon.png" alt="logo" className="w-16 h-16 rounded-xl object-cover flex-shrink-0" />
        <div className="leading-tight">
          <p className="text-[13px] font-700 text-slate-800 font-semibold leading-[1.2]">AI Call Center</p>
          <p className="text-[12px] font-semibold text-blue-600">Assistant</p>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        <NavLink
          to="/dashboard"
          className={({ isActive }) =>
            `flex items-center gap-3 px-3 py-2.5 rounded-lg text-[14px] font-medium transition-colors ${
              isActive
                ? 'bg-blue-50 text-blue-600 border-l-[3px] border-blue-600 pl-[9px]'
                : 'text-slate-500 hover:bg-slate-50 hover:text-slate-700'
            }`
          }
        >
          {({ isActive }) => (
            <>
              <BarChart2 size={22} className={isActive ? 'text-blue-600' : 'text-slate-400'} />
              Dashboard
            </>
          )}
        </NavLink>

        <NavLink
          to="/calls"
          end={false}
          className={({ isActive }) =>
            `flex items-center gap-3 px-3 py-2.5 rounded-lg text-[14px] font-medium transition-colors ${
              isActive
                ? 'bg-blue-50 text-blue-600 border-l-[3px] border-blue-600 pl-[9px]'
                : 'text-slate-500 hover:bg-slate-50 hover:text-slate-700'
            }`
          }
        >
          {({ isActive }) => (
            <>
              <Phone size={22} className={isActive ? 'text-blue-600' : 'text-slate-400'} />
              Call Analyze
            </>
          )}
        </NavLink>

      </nav>

      {/* Footer */}
      <div className="px-5 py-4 border-t border-slate-100">
        <p className="text-[11px] text-slate-400 leading-relaxed">
          © 2026 AI Call Center Assistant
          <br />
          All rights reserved.
        </p>
      </div>
    </aside>
  );
}
