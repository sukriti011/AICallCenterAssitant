export default function StatsCard({ icon: Icon, label, value, color = 'blue' }) {
  const colorMap = {
    blue:   { bg: 'bg-blue-100',   icon: 'text-blue-600',   value: 'text-blue-600'   },
    green:  { bg: 'bg-green-100',  icon: 'text-green-600',  value: 'text-green-600'  },
    orange: { bg: 'bg-orange-100', icon: 'text-orange-500', value: 'text-orange-500' },
    red:    { bg: 'bg-red-100',    icon: 'text-red-500',    value: 'text-red-500'    },
    purple: { bg: 'bg-purple-100', icon: 'text-purple-600', value: 'text-purple-600' },
  };

  const c = colorMap[color] || colorMap.blue;

  return (
    <div className="bg-white rounded-xl shadow-card border border-slate-100 px-5 py-3.5 flex items-center gap-4 flex-1 min-w-0">
      <div className={`flex items-center justify-center w-9 h-9 rounded-full flex-shrink-0 ${c.bg}`}>
        <Icon size={18} className={c.icon} />
      </div>
      <div className="min-w-0">
        <p className="text-[13px] text-slate-500 font-medium truncate">{label}</p>
        <p className={`text-2xl font-bold leading-none mt-1 ${c.value}`}>{value}</p>
      </div>
    </div>
  );
}
