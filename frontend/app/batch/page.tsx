"use client";

import { useState, useCallback, useRef } from "react";
import { uploadBatchCsv } from "@/lib/api";
import { UploadCloud, File, AlertCircle, CheckCircle2, Download, X } from "lucide-react";

export default function BatchUploadPage() {
  const [dragActive, setDragActive] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<any>(null);
  const inputRef = useRef<HTMLInputElement>(null);

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
    <div className="max-w-4xl mx-auto space-y-8 animate-fade-in">
      <header>
        <h1 className="text-3xl font-bold bg-gradient-to-r from-white to-slate-400 bg-clip-text text-transparent">
          Batch CSV Upload
        </h1>
        <p className="text-slate-400 mt-1">Upload a list of leads to score them in bulk via the XGBoost model.</p>
      </header>

      <div className="glass-panel p-8 rounded-2xl">
        {!result ? (
          <div className="space-y-6">
            <div 
              className={`relative flex flex-col items-center justify-center p-12 border-2 border-dashed rounded-xl transition-all
                ${dragActive ? 'border-primary bg-primary/5' : 'border-white/20 hover:border-white/40 hover:bg-white/5'}
                ${file ? 'border-emerald-500/50 bg-emerald-500/5' : ''}
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
                  <div className="w-16 h-16 rounded-full bg-slate-800 flex items-center justify-center mb-4 text-primary">
                    <UploadCloud size={32} />
                  </div>
                  <h3 className="text-lg font-medium text-white mb-2">Drag & Drop your CSV</h3>
                  <p className="text-slate-400 text-sm mb-6 text-center max-w-sm">
                    Upload the raw Lead Scoring.csv file. The AI will automatically clean it and score all records.
                  </p>
                  <button 
                    onClick={onButtonClick}
                    className="px-6 py-2.5 bg-white/10 hover:bg-white/20 text-white rounded-lg transition-colors font-medium text-sm"
                  >
                    Browse Files
                  </button>
                </>
              ) : (
                <div className="flex flex-col items-center">
                  <div className="w-16 h-16 rounded-full bg-emerald-500/10 flex items-center justify-center mb-4 text-emerald-400">
                    <File size={32} />
                  </div>
                  <h3 className="text-lg font-medium text-white mb-1">{file.name}</h3>
                  <p className="text-slate-400 text-sm mb-6">{(file.size / 1024).toFixed(1)} KB</p>
                  
                  <div className="flex gap-4">
                    <button 
                      onClick={clearFile}
                      className="px-6 py-2.5 bg-white/5 hover:bg-white/10 text-white rounded-lg transition-colors font-medium text-sm border border-white/10"
                    >
                      Cancel
                    </button>
                    <button 
                      onClick={handleUpload}
                      disabled={loading}
                      className="px-6 py-2.5 bg-gradient-to-r from-primary to-primary-hover text-white rounded-lg transition-colors font-medium text-sm shadow-lg shadow-primary/20 flex items-center gap-2 disabled:opacity-50"
                    >
                      {loading ? (
                        <>
                          <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                          Processing...
                        </>
                      ) : (
                        'Score Leads'
                      )}
                    </button>
                  </div>
                </div>
              )}
            </div>

            {error && (
              <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-xl text-red-400 flex items-start gap-3 animate-fade-in">
                <AlertCircle size={20} className="shrink-0 mt-0.5" />
                <p className="text-sm">{error}</p>
              </div>
            )}
          </div>
        ) : (
          <div className="text-center animate-fade-in py-8">
            <div className="w-20 h-20 bg-emerald-500/20 text-emerald-500 rounded-full flex items-center justify-center mx-auto mb-6">
              <CheckCircle2 size={40} />
            </div>
            <h2 className="text-2xl font-bold mb-2">Processing Complete!</h2>
            <p className="text-slate-400 mb-8 max-w-md mx-auto">
              Successfully scored <strong className="text-white">{result.rows_processed}</strong> leads. The results have been saved to your backend outputs directory.
            </p>
            
            <div className="flex justify-center gap-4">
              <button 
                onClick={clearFile}
                className="px-6 py-2.5 bg-white/10 hover:bg-white/20 text-white rounded-lg transition-colors font-medium"
              >
                Upload Another
              </button>
              {result.output_file && (
                <button 
                  className="px-6 py-2.5 bg-primary/20 text-primary border border-primary/30 rounded-lg cursor-default font-medium flex items-center gap-2"
                >
                  <Download size={18} />
                  Saved: {result.output_file}
                </button>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
