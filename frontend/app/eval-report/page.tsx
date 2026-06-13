"use client";

import { useEffect, useState } from "react";
import { CheckCircle, XCircle, Activity } from "lucide-react";

export default function EvalReport() {
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch('http://localhost:8000/api/eval-results')
      .then(res => {
        if (!res.ok) throw new Error("Could not fetch results. Did you run the evaluate.py script first?");
        return res.json();
      })
      .then(data => {
        setResults(data);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  return (
    <div className="min-h-screen bg-slate-50 p-8 font-sans text-slate-900">
      <header className="mb-8 border-b pb-4 max-w-5xl mx-auto">
        <h1 className="text-3xl font-bold flex items-center gap-2">
          <Activity className="text-blue-600" /> Evaluation Report
        </h1>
        <p className="text-slate-500 mt-2">Automated trace validation against test_cases.json</p>
      </header>

      <div className="max-w-5xl mx-auto space-y-4">
        {loading && <div className="text-slate-500 font-medium">Loading evaluation results...</div>}

        {error && (
          <div className="bg-red-50 text-red-700 p-4 rounded-lg border border-red-200">
            {error}
          </div>
        )}

        {!loading && !error && results.map((res) => (
          <div key={res.case_id} className={`p-5 rounded-xl border shadow-sm ${res.passed ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'}`}>
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-3">
                {res.passed ? <CheckCircle className="text-green-600 w-6 h-6" /> : <XCircle className="text-red-600 w-6 h-6" />}
                <h3 className="text-lg font-bold">Case #{res.case_id}: {res.description}</h3>
              </div>
              <div className="flex gap-4 text-sm font-medium">
                <span className="text-slate-500">Expected: <span className="text-slate-900">{res.expected}</span></span>
                <span className="text-slate-500">Actual: <span className={res.passed ? 'text-green-700' : 'text-red-700'}>{res.actual}</span></span>
              </div>
            </div>

            <div className="bg-white p-4 rounded-lg border border-slate-100 mt-2">
              <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">System Reasoning Trace</h4>
              <p className="text-sm text-slate-700 leading-relaxed">{res.trace}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}