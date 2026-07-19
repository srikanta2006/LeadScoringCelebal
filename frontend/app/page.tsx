import { getAnalytics } from "@/lib/api";
import { Users, TrendingUp, Target, BarChart2 } from "lucide-react";

export const revalidate = 0; // Disable caching for dashboard

export default async function Home() {
  let analytics;
  try {
    analytics = await getAnalytics();
  } catch (err) {
    console.error(err);
  }

  if (!analytics) {
    return (
      <div className="flex flex-col items-center justify-center h-full animate-fade-in">
        <div className="glass-panel p-8 rounded-2xl text-center max-w-md">
          <div className="w-16 h-16 bg-red-500/10 text-red-500 rounded-full flex items-center justify-center mx-auto mb-4">
            <TrendingUp size={32} />
          </div>
          <h2 className="text-xl font-bold mb-2">Backend Not Connected</h2>
          <p className="text-slate-400">
            Make sure your FastAPI server is running on port 8000.
          </p>
        </div>
      </div>
    );
  }

  const { total_leads_scored, average_score, hot_count, warm_count, top_sources } = analytics;

  return (
    <div className="space-y-8 animate-fade-in">
      <header>
        <h1 className="text-3xl font-bold bg-gradient-to-r from-white to-slate-400 bg-clip-text text-transparent">
          Dashboard Overview
        </h1>
        <p className="text-slate-400 mt-1">Real-time metrics from your Lead Scoring ML Pipeline.</p>
      </header>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="glass-card p-6 rounded-2xl">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-slate-400 text-sm font-medium">Total Leads Scored</p>
              <h3 className="text-3xl font-bold mt-2">{total_leads_scored?.toLocaleString() || 0}</h3>
            </div>
            <div className="p-3 bg-blue-500/20 text-blue-400 rounded-xl">
              <Users size={24} />
            </div>
          </div>
        </div>

        <div className="glass-card p-6 rounded-2xl delay-100">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-slate-400 text-sm font-medium">Average Score</p>
              <h3 className="text-3xl font-bold mt-2">{average_score.toFixed(1)}</h3>
            </div>
            <div className="p-3 bg-emerald-500/20 text-emerald-400 rounded-xl">
              <Target size={24} />
            </div>
          </div>
        </div>

        <div className="glass-card p-6 rounded-2xl delay-200">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-slate-400 text-sm font-medium">Hot Leads</p>
              <h3 className="text-3xl font-bold mt-2">{hot_count || 0}</h3>
            </div>
            <div className="p-3 bg-red-500/20 text-red-400 rounded-xl">
              <TrendingUp size={24} />
            </div>
          </div>
        </div>

        <div className="glass-card p-6 rounded-2xl delay-300">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-slate-400 text-sm font-medium">Warm Leads</p>
              <h3 className="text-3xl font-bold mt-2">{warm_count || 0}</h3>
            </div>
            <div className="p-3 bg-amber-500/20 text-amber-400 rounded-xl">
              <BarChart2 size={24} />
            </div>
          </div>
        </div>
      </div>

      {/* Top Sources Table */}
      <div className="glass-panel rounded-2xl overflow-hidden mt-8 delay-300">
        <div className="p-6 border-b border-white/5 flex justify-between items-center">
          <h3 className="text-xl font-bold">Top Lead Sources</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead className="bg-white/5 text-slate-400 text-sm">
              <tr>
                <th className="px-6 py-4 font-medium">Source</th>
                <th className="px-6 py-4 font-medium">Count</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {(!top_sources || top_sources.length === 0) ? (
                <tr>
                  <td colSpan={2} className="px-6 py-8 text-center text-slate-400">
                    No lead sources tracked yet.
                  </td>
                </tr>
              ) : (
                top_sources.map((src: any, i: number) => (
                  <tr key={i} className="hover:bg-white/5 transition-colors">
                    <td className="px-6 py-4 font-medium">{src.source || 'Unknown'}</td>
                    <td className="px-6 py-4 text-slate-300">{src.count}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
