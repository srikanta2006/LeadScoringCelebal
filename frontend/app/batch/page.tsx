"use client";

import { useMemo, useState, useRef } from "react";
import { uploadBatchCsv, BatchUploadResponse } from "@/lib/api";
import { UploadCloud, File, AlertCircle, CheckCircle2, Sparkles } from "lucide-react";

export default function BatchUploadPage() {
  const [dragActive, setDragActive] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<BatchUploadResponse | null>(null);
  const [query, setQuery] = useState("");
  const [tierFilter, setTierFilter] = useState("All");
  const inputRef = useRef<HTMLInputElement>(null);

  const filteredResults = useMemo(() => {
    if (!result) return [];

    return result.results
      .slice()
      .sort((a, b) => b.score - a.score)
      .filter((row) => {
        if (tierFilter !== "All" && row.tier !== tierFilter) return false;
        if (!query) return true;

        const search = query.toLowerCase();
        return [row.prospect_id, row.lead_source, row.country, row.city, row.recommended_action]
          .filter(Boolean)
          .some((value) => String(value).toLowerCase().includes(search));
      });
  }, [result, query, tierFilter]);

  const displayedResults = useMemo(() => filteredResults.slice(0, 20), [filteredResults]);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFile = e.dataTransfer.files[0];
      if (droppedFile.name.endsWith('.csv')) {
        setFile(droppedFile);
        setError(null);
        setResult(null);
      } else {
        setError("Please upload a CSV file");
      }
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError(null);
      setResult(null);
    }
  };

  const onButtonClick = () => {
    inputRef.current?.click();
  };

  const clearFile = () => {
    setFile(null);
    setResult(null);
    setError(null);
    if (inputRef.current) inputRef.current.value = "";
  };

  const handleUpload = async () => {
    if (!file) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const res = await uploadBatchCsv(file);
      setResult(res);
    } catch (err: any) {
      setError(err.message || "Failed to process CSV file");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto space-y-10 animate-fade-in py-6">
      <header className="space-y-4">
        <div className="inline-flex items-center gap-2 rounded-full bg-slate-800/70 px-4 py-2 text-xs uppercase tracking-[0.24em] text-slate-300 shadow-sm shadow-slate-950/20">
          Premium Suite
        </div>
        <div className="space-y-3">
          <h1 className="text-4xl md:text-5xl font-semibold tracking-tight text-white">Batch lead scoring with clarity and precision</h1>
          <p className="max-w-3xl text-slate-400 text-lg leading-8">
            Upload your CSV once and receive a complete scoring overview for every prospect, including tier classification and recommended next steps.
          </p>
        </div>
      </header>

      <div className="grid gap-6 lg:grid-cols-[1.35fr_0.9fr]">
        <div className="glass-card p-8 rounded-[2rem] border border-white/10 shadow-[0_30px_80px_-40px_rgba(15,23,42,0.9)]">
          {!result ? (
            <div className="space-y-6">
              <div 
                className={`relative flex flex-col items-center justify-center p-16 rounded-[1.75rem] border-2 transition-all text-center
                  ${dragActive ? 'border-blue-400/30 bg-blue-500/10' : 'border-white/10 bg-slate-950/35'}
                  ${file ? 'border-emerald-400/30 bg-emerald-500/10' : ''}
                `}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
              >
                <input
                  ref={inputRef}
                  type="file"
                  accept=".csv"
                  className="hidden"
                  onChange={handleChange}
                />

                {!file ? (
                  <>
                    <div className="w-18 h-18 rounded-full bg-slate-800 flex items-center justify-center mb-5 text-blue-300 shadow-lg shadow-blue-900/20">
                      <UploadCloud size={36} />
                    </div>
                    <h3 className="text-2xl font-semibold text-white mb-3">Drag & drop your CSV</h3>
                    <p className="text-slate-400 text-sm max-w-md">Upload a standard lead list and let the platform score every row with a refined tier and action recommendation.</p>
                    <button 
                      onClick={onButtonClick}
                      className="mt-8 inline-flex items-center justify-center rounded-full bg-white/10 px-7 py-3 text-sm font-semibold text-white transition hover:bg-white/20"
                    >
                      Select File
                    </button>
                  </>
                ) : (
                  <div className="flex flex-col items-center gap-4">
                    <div className="w-18 h-18 rounded-full bg-emerald-500/10 flex items-center justify-center text-emerald-300">
                      <File size={36} />
                    </div>
                    <div>
                      <p className="text-sm text-slate-400">Ready to score</p>
                      <p className="text-xl font-semibold text-white">{file.name}</p>
                      <p className="text-slate-500 text-sm mt-1">{(file.size / 1024).toFixed(1)} KB</p>
                    </div>
                    <div className="flex flex-wrap gap-3">
                      <button 
                        onClick={clearFile}
                        className="rounded-full border border-white/10 bg-white/5 px-5 py-2 text-sm text-white transition hover:bg-white/10"
                      >
                        Remove
                      </button>
                      <button 
                        onClick={handleUpload}
                        disabled={loading}
                        className="rounded-full bg-gradient-to-r from-blue-500 to-sky-500 px-6 py-2.5 text-sm font-semibold text-white shadow-lg shadow-blue-500/20 transition disabled:opacity-50"
                      >
                        {loading ? 'Processing...' : 'Score Leads'}
                      </button>
                    </div>
                  </div>
                )}
              </div>

              {error && (
                <div className="rounded-[1.5rem] border border-red-500/20 bg-red-500/10 p-5 text-slate-100">
                  <div className="flex items-start gap-3">
                    <AlertCircle size={20} className="text-red-300" />
                    <div>
                      <p className="font-semibold text-white">Upload error</p>
                      <p className="text-sm text-slate-300">{error}</p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="space-y-6">
              <div className="grid gap-4 sm:grid-cols-3">
                <div className="rounded-[1.75rem] border border-white/10 bg-slate-950/80 p-6">
                  <p className="text-sm text-slate-400">Total records</p>
                  <p className="mt-3 text-3xl font-semibold text-white">{result.total_leads}</p>
                </div>
                <div className="rounded-[1.75rem] border border-white/10 bg-slate-950/80 p-6">
                  <p className="text-sm text-slate-400">Scored rows</p>
                  <p className="mt-3 text-3xl font-semibold text-white">{result.scored_successfully}</p>
                </div>
                <div className="rounded-[1.75rem] border border-white/10 bg-slate-950/80 p-6">
                  <p className="text-sm text-slate-400">Issues found</p>
                  <p className="mt-3 text-3xl font-semibold text-white">{result.errors.length}</p>
                </div>
              </div>

              <div className="rounded-[2rem] border border-white/10 bg-slate-950/85 overflow-hidden">
      <div className="flex flex-col gap-4 border-b border-white/10 bg-slate-950/95 p-6">
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="text-sm uppercase tracking-[0.24em] text-slate-500">Batch results</p>
            <h2 className="text-2xl font-semibold text-white">Top-scoring leads</h2>
          </div>
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
            <input
              type="search"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="Search by lead, source, region, action"
              className="w-full min-w-[220px] rounded-full border border-white/10 bg-slate-900/80 px-4 py-3 text-sm text-white outline-none focus:border-blue-400/60 focus:ring-2 focus:ring-blue-400/20"
            />
            <select
              value={tierFilter}
              onChange={(event) => setTierFilter(event.target.value)}
              className="w-full min-w-[160px] rounded-full border border-white/10 bg-slate-900/80 px-4 py-3 text-sm text-white outline-none focus:border-blue-400/60 focus:ring-2 focus:ring-blue-400/20"
            >
              <option value="All">All tiers</option>
              <option value="Hot">Hot</option>
              <option value="Warm">Warm</option>
              <option value="Cold">Cold</option>
              <option value="Frozen">Frozen</option>
            </select>
          </div>
        </div>

        <p className="text-sm text-slate-400">Showing {displayedResults.length} of {filteredResults.length} filtered rows (top 20 by score).</p>
      </div>

      <div className="overflow-x-auto p-6">
        <table className="w-full border-separate border-spacing-y-3 text-left">
                    <thead className="text-slate-400 text-xs uppercase tracking-[0.2em]">
                      <tr>
                        <th className="pb-3 pr-6">Lead</th>
                        <th className="pb-3 pr-6">Source</th>
                        <th className="pb-3 pr-6">Region</th>
                        <th className="pb-3 pr-6">Score</th>
                        <th className="pb-3 pr-6">Tier</th>
                        <th className="pb-3">Action</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-white/10">
                      {displayedResults.map((row, index) => (
                        <tr key={index} className="bg-slate-950/75 hover:bg-slate-900/90 transition-colors">
                          <td className="px-4 py-4 text-sm font-medium text-white">{row.prospect_id || row.lead_source || `Row ${index + 1}`}</td>
                          <td className="px-4 py-4 text-sm text-slate-300">{row.lead_source || "—"}</td>
                          <td className="px-4 py-4 text-sm text-slate-300">{row.country || row.city || "—"}</td>
                          <td className="px-4 py-4 text-sm font-semibold text-white">{row.score.toFixed(1)}</td>
                          <td className="px-4 py-4 text-sm text-slate-300">{row.tier}</td>
                          <td className="px-4 py-4 text-sm text-slate-300">{row.recommended_action}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {result.errors.length > 0 && (
                <div className="rounded-[1.75rem] border border-amber-400/10 bg-amber-500/10 p-6 text-amber-100">
                  <h3 className="text-lg font-semibold text-white">Review the first issues</h3>
                  <p className="mt-2 text-sm text-slate-300">Make sure the CSV columns match the expected format and retry if necessary.</p>
                  <ul className="mt-4 space-y-2 text-sm text-slate-200">
                    {result.errors.slice(0, 4).map((error, index) => (
                      <li key={index}>• {error}</li>
                    ))}
                  </ul>
                </div>
              )}

              <div className="flex flex-wrap gap-4">
                <button 
                  onClick={clearFile}
                  className="rounded-full border border-white/10 bg-white/5 px-6 py-3 text-sm font-semibold text-white transition hover:bg-white/10"
                >
                  Score another file
                </button>
                <button 
                  onClick={() => setResult(null)}
                  className="rounded-full border border-slate-600 bg-slate-900/75 px-6 py-3 text-sm font-semibold text-slate-100 transition hover:bg-slate-900"
                >
                  Reset results
                </button>
              </div>
            </div>
          )}
        </div>

        <aside className="space-y-6">
          <div className="glass-card rounded-[2rem] border border-white/10 p-6 shadow-[0_30px_80px_-40px_rgba(15,23,42,0.9)]">
            <div className="flex items-center gap-3 text-slate-300 mb-4">
              <Sparkles size={20} />
              <span className="text-sm uppercase tracking-[0.24em]">Professional workflow</span>
            </div>
            <h2 className="text-xl font-semibold text-white">Premium scoring made simple</h2>
            <p className="mt-3 text-sm leading-6 text-slate-400">Instantly prioritize leads with a refined scoring system, clear classification, and recommended actions for every row.</p>
            <div className="mt-6 space-y-4">
              <div className="rounded-3xl border border-white/10 bg-slate-950/70 p-4">
                <p className="text-sm font-medium text-slate-300">Fast results</p>
                <p className="mt-2 text-sm text-slate-400">Upload once and receive immediate results directly in the interface.</p>
              </div>
              <div className="rounded-3xl border border-white/10 bg-slate-950/70 p-4">
                <p className="text-sm font-medium text-slate-300">Trusted structure</p>
                <p className="mt-2 text-sm text-slate-400">Supported by a consistent input schema and robust scoring logic.</p>
              </div>
            </div>
          </div>

          <div className="glass-card rounded-[2rem] border border-white/10 p-6">
            <h3 className="text-lg font-semibold text-white mb-4">What to include</h3>
            <div className="grid gap-3 text-sm text-slate-400">
              <div className="rounded-3xl bg-slate-950/70 p-4">Prospect identifier, source, and country.</div>
              <div className="rounded-3xl bg-slate-950/70 p-4">Total visits, time spent, and page views per visit.</div>
              <div className="rounded-3xl bg-slate-950/70 p-4">Recent activity, opt-out flags, and profile signals.</div>
            </div>
          </div>
        </aside>
      </div>
    </div>
  );
}
