"use client";

import { FormEvent, useState } from "react";
import { scoreLead, ScoreResponse } from "@/lib/api";
import { Send, AlertCircle, CheckCircle2, Target } from "lucide-react";

export default function SingleScorePage() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ScoreResponse | null>(null);

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    const formData = new FormData(e.currentTarget);
    const data = Object.fromEntries(formData.entries());

    // Basic type conversion
    const payload = {
      ...data,
      total_visits: Number(data.total_visits) || 0,
      total_time_spent_on_website: Number(data.total_time_spent_on_website) || 0,
      page_views_per_visit: Number(data.page_views_per_visit) || 0,
    };

    try {
      const res = await scoreLead(payload);
      setResult(res);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message || "Failed to score lead");
      } else {
        setError("Failed to score lead");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8 animate-fade-in">
      <header className="space-y-4">
        <div className="inline-flex items-center gap-2 rounded-full bg-slate-800/70 px-4 py-2 text-xs uppercase tracking-[0.24em] text-slate-300 shadow-sm shadow-slate-950/20">
          Lead Intelligence
        </div>
        <div>
          <h1 className="text-4xl md:text-5xl font-semibold tracking-tight text-white">Score a single lead</h1>
          <p className="text-slate-400 mt-3 max-w-3xl text-lg leading-8">Enter lead details to receive a refined score, tier classification, and recommended next action.</p>
        </div>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 glass-panel p-8 rounded-2xl">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Contact Info */}
              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-300">Name</label>
                <input type="text" name="name" className="w-full bg-slate-900/50 border border-white/10 rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-primary/50 text-white" placeholder="John Doe" />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-300">Email (Optional)</label>
                <input type="email" name="email" className="w-full bg-slate-900/50 border border-white/10 rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-primary/50 text-white" placeholder="john@example.com" />
              </div>
              
              {/* Behavioral Data */}
              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-300">Total Visits</label>
                <input type="number" name="total_visits" defaultValue={0} className="w-full bg-slate-900/50 border border-white/10 rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-primary/50 text-white" />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-300">Total Time on Website (s)</label>
                <input type="number" name="total_time_spent_on_website" defaultValue={0} className="w-full bg-slate-900/50 border border-white/10 rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-primary/50 text-white" />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-300">Page Views per Visit</label>
                <input type="number" step="0.1" name="page_views_per_visit" defaultValue={0} className="w-full bg-slate-900/50 border border-white/10 rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-primary/50 text-white" />
              </div>

              {/* Categorical Data */}
              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-300">Lead Origin</label>
                <select name="lead_origin" className="w-full bg-slate-900/50 border border-white/10 rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-primary/50 text-white appearance-none">
                  <option value="Landing Page Submission">Landing Page Submission</option>
                  <option value="API">API</option>
                  <option value="Lead Add Form">Lead Add Form</option>
                </select>
              </div>
              
              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-300">Lead Source</label>
                <select name="lead_source" className="w-full bg-slate-900/50 border border-white/10 rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-primary/50 text-white appearance-none">
                  <option value="Direct Traffic">Direct Traffic</option>
                  <option value="Google">Google</option>
                  <option value="Organic Search">Organic Search</option>
                  <option value="Reference">Reference</option>
                </select>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-300">Last Activity</label>
                <select name="last_activity" className="w-full bg-slate-900/50 border border-white/10 rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-primary/50 text-white appearance-none">
                  <option value="Email Opened">Email Opened</option>
                  <option value="SMS Sent">SMS Sent</option>
                  <option value="Page Visited on Website">Page Visited on Website</option>
                  <option value="Converted to Lead">Converted to Lead</option>
                </select>
              </div>
              
              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-300">Lead Quality</label>
                <select name="lead_quality" className="w-full bg-slate-900/50 border border-white/10 rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-primary/50 text-white appearance-none">
                  <option value="Not Sure">Not Sure</option>
                  <option value="Might be">Might be</option>
                  <option value="High in Relevance">High in Relevance</option>
                  <option value="Worst">Worst</option>
                </select>
              </div>

              {/* Checkboxes */}
              <div className="col-span-1 md:col-span-2 flex gap-8">
                <label className="flex items-center gap-2 cursor-pointer text-slate-300">
                  <input type="checkbox" name="do_not_email" value="Yes" className="rounded border-white/10 bg-slate-900/50 text-primary focus:ring-primary/50" />
                  <span>Do Not Email</span>
                </label>
                <label className="flex items-center gap-2 cursor-pointer text-slate-300">
                  <input type="checkbox" name="do_not_call" value="Yes" className="rounded border-white/10 bg-slate-900/50 text-primary focus:ring-primary/50" />
                  <span>Do Not Call</span>
                </label>
              </div>
            </div>

            {error && (
              <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-xl text-red-400 flex items-start gap-3">
                <AlertCircle size={20} className="shrink-0 mt-0.5" />
                <p className="text-sm">{error}</p>
              </div>
            )}

            <button 
              type="submit" 
              disabled={loading}
              className="w-full bg-gradient-to-r from-primary to-primary-hover hover:from-primary-hover hover:to-primary text-white font-medium py-3 px-6 rounded-xl transition-all shadow-lg shadow-primary/25 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                <>
                  <Send size={18} />
                  <span>Calculate Score</span>
                </>
              )}
            </button>
          </form>
        </div>

        <div className="lg:col-span-1">
          {result ? (
            <div className="glass-card p-6 rounded-2xl sticky top-8 animate-fade-in">
              <div className="text-center mb-6">
                <h3 className="text-lg font-medium text-slate-300 mb-1">Lead Score</h3>
                <div className="text-5xl font-bold bg-gradient-to-r from-white to-slate-300 bg-clip-text text-transparent">
                  {result.score.toFixed(1)}
                </div>
              </div>
              
              <div className="space-y-4">
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-slate-400">Classification Tier</span>
                    <span className={`font-semibold ${
                      result.tier === 'Hot' ? 'text-red-400' :
                      result.tier === 'Warm' ? 'text-amber-400' :
                      result.tier === 'Cold' ? 'text-blue-400' :
                      'text-slate-400'
                    }`}>{result.tier}</span>
                  </div>
                  <div className="w-full bg-slate-800 rounded-full h-2">
                    <div 
                      className={`h-2 rounded-full ${
                        result.tier === 'Hot' ? 'bg-red-500' :
                        result.tier === 'Warm' ? 'bg-amber-500' :
                        result.tier === 'Cold' ? 'bg-blue-500' :
                        'bg-slate-500'
                      }`}
                      style={{ width: `${result.score}%` }}
                    />
                  </div>
                </div>

                <div className="pt-4 border-t border-white/5">
                  <h4 className="text-sm font-medium text-slate-300 mb-2">Recommended Action</h4>
                  <div className="flex items-start gap-3 p-3 bg-white/5 rounded-xl border border-white/5">
                    <CheckCircle2 className="shrink-0 text-emerald-400 mt-0.5" size={18} />
                    <p className="text-sm text-slate-300">{result.recommended_action}</p>
                  </div>
                </div>

                <div className="pt-4 text-xs text-center text-slate-500">
                  Scored using {result.model_mode.toUpperCase()} model
                </div>
              </div>
            </div>
          ) : (
            <div className="glass-panel p-8 rounded-2xl h-full flex flex-col items-center justify-center text-center text-slate-500 border-dashed">
              <div className="w-16 h-16 rounded-full bg-white/5 flex items-center justify-center mb-4">
                <Target size={24} className="text-slate-400" />
              </div>
              <p>Submit the form to see the lead score and recommended action.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
