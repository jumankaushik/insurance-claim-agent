"use client";

import { Activity, Beaker, User } from "lucide-react";
import Link from "next/link"; // Added Next.js router link
import { usePipeline } from "../hooks/usePipeline";
import ClaimForm from "../components/ClaimForm";
import TraceViewer from "../components/TraceViewer";

export default function ClaimsDashboard() {
  const { loading, result, error, runPipeline } = usePipeline();

  return (
    <div className="min-h-screen bg-slate-50 p-8 font-sans text-slate-900">

      {/* Updated Header with Eval Button */}
      <header className="mb-8 border-b border-slate-200 pb-4 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3">
            <Activity className="text-blue-600" /> Plum AI Adjudicator Pod
          </h1>
          <p className="text-slate-500 mt-2 font-medium">Multi-Agent Claims Processing Architecture</p>
        </div>

        {/* Header Actions */}
        <div className="flex items-center gap-4">
          {/* Goal #3: Admin Portal Link */}
          <Link
            href="/admin"
            target="_blank"
            rel="noopener noreferrer"
            className="text-slate-500 hover:text-slate-900 font-semibold text-sm flex items-center gap-2 transition-colors px-3 py-2 rounded hover:bg-slate-200"
          >
            <User size={18} /> Admin Portal
          </Link>

          {/* Goal #2: The Eval Result Button */}
          <Link
            href="/eval-report"
            target="_blank"
            rel="noopener noreferrer"
            className="bg-white border border-slate-300 hover:border-blue-500 hover:bg-blue-50 text-slate-700 hover:text-blue-700 font-bold py-2 px-4 rounded-lg flex items-center gap-2 transition-all shadow-sm"
          >
            <Beaker size={18} /> Run Automated Evals
          </Link>
        </div>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <ClaimForm onRun={runPipeline} isLoading={loading} />

        <div className="lg:col-span-2">
          <TraceViewer result={result} error={error} isLoading={loading} />
        </div>
      </div>
    </div>
  );
}