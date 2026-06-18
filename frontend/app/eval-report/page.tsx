"use client";

import { useEffect, useState } from "react";
import { CheckCircle, XCircle, Activity, Play, Clock, RefreshCw } from "lucide-react";

export default function EvalReport() {
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [isEvaluating, setIsEvaluating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Function to pull the latest results from the JSON file
  const fetchResults = () => {
    setLoading(true);
    fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/eval-results`)
      .then(res => {
        if (!res.ok) throw new Error("Could not fetch results. Click 'Run All Test Cases' to generate them.");
        return res.json();
      })
      .then(data => {
        setResults(data);
        setError(null);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  };

  // Load results when the page opens
  useEffect(() => {
    fetchResults();
  }, []);

  // Function to trigger the actual LangGraph agents
  const handleRunEvals = async () => {
    setIsEvaluating(true);
    setError(null);
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/run-evaluations`, {
        method: 'POST'
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || "Failed to run evaluations.");
      }

      // Poll the backend every 5 seconds until it returns a 200 OK (meaning the file is written)
      const pollInterval = setInterval(async () => {
        try {
          const checkRes = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/eval-results`);
          if (checkRes.ok) {
            clearInterval(pollInterval); // Stop asking
            fetchResults(); // Render the data
            setIsEvaluating(false); // Turn off the loading spinner
          }
        } catch (e) {
          // Still loading or 404, keep waiting quietly
        }
      }, 5000);

    } catch (err: any) {
      setError(err.message);
      setIsEvaluating(false);
    }
  };

  // Calculate quick stats
  const passCount = results.filter(r => r.passed).length;
  const totalCount = results.length;

  return (
    <div className="min-h-screen bg-slate-50 p-8 font-sans text-slate-900">
      <header className="mb-8 border-b pb-6 max-w-5xl mx-auto flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <Activity className="text-blue-600" /> Evaluation & Compliance Report
          </h1>
          <p className="text-slate-500 mt-2">Automated trace validation against policy ground-truth</p>
        </div>

        {/* The New Trigger Button */}
        <button
          onClick={handleRunEvals}
          disabled={isEvaluating}
          className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-lg flex items-center gap-2 transition-all disabled:opacity-50 shadow-md"
        >
          {isEvaluating ? <Clock className="animate-spin" size={20} /> : <Play size={20} fill="currentColor" />}
          {isEvaluating ? "Agents Processing (Est. 1-2 mins)..." : "Run All 12 Test Cases"}
        </button>
      </header>

      <div className="max-w-5xl mx-auto space-y-4">

        {/* Stats Bar */}
        {!loading && !error && totalCount > 0 && (
          <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex items-center gap-6 mb-6">
            <div className="text-sm font-bold text-slate-500 uppercase tracking-wider">System Score</div>
            <div className="text-2xl font-black text-slate-800">{passCount} / {totalCount} Passed</div>
            <div className="flex-1 bg-slate-100 rounded-full h-3 overflow-hidden">
              <div
                className="bg-green-500 h-full rounded-full transition-all duration-1000"
                style={{ width: `${(passCount / totalCount) * 100}%` }}
              />
            </div>
          </div>
        )}

        {loading && !isEvaluating && (
          <div className="text-slate-500 font-medium flex items-center gap-2">
            <RefreshCw className="animate-spin" size={16} /> Fetching evaluation records...
          </div>
        )}

        {error && !isEvaluating && (
          <div className="bg-red-50 text-red-700 p-6 rounded-xl border border-red-200 text-center">
            <p className="font-bold text-lg mb-2">{error}</p>
            <p className="text-sm text-red-600">Click the blue button above to initialize the testing sequence.</p>
          </div>
        )}

        {/* The Results List */}
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