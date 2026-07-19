import Link from 'next/link';
import { LayoutDashboard, UserPlus, FileSpreadsheet, Settings } from 'lucide-react';

export default function Sidebar() {
  return (
    <aside className="w-64 glass-panel border-r border-white/10 flex flex-col h-full sticky top-0">
      <div className="p-6 border-b border-white/10">
        <h2 className="text-xl font-bold bg-gradient-to-r from-primary to-emerald-400 bg-clip-text text-transparent">
          X Education
        </h2>
        <p className="text-xs text-slate-400 mt-1">Lead Scoring Dashboard</p>
      </div>

      <nav className="flex-1 p-4 space-y-2">
        <Link href="/" className="flex items-center gap-3 px-4 py-3 rounded-lg text-slate-300 hover:text-white hover:bg-white/5 transition-all">
          <LayoutDashboard size={20} />
          <span>Analytics</span>
        </Link>
        <Link href="/single" className="flex items-center gap-3 px-4 py-3 rounded-lg text-slate-300 hover:text-white hover:bg-white/5 transition-all">
          <UserPlus size={20} />
          <span>Score Lead</span>
        </Link>
        <Link href="/batch" className="flex items-center gap-3 px-4 py-3 rounded-lg text-slate-300 hover:text-white hover:bg-white/5 transition-all">
          <FileSpreadsheet size={20} />
          <span>Batch Upload</span>
        </Link>
      </nav>

      <div className="p-4 border-t border-white/10">
        <button className="flex items-center gap-3 px-4 py-3 w-full rounded-lg text-slate-400 hover:text-white hover:bg-white/5 transition-all">
          <Settings size={20} />
          <span>Settings</span>
        </button>
      </div>
    </aside>
  );
}
