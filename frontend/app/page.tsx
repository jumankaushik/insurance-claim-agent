"use client";

import { Activity } from "lucide-react";
import { usePipeline } from "../hooks/usePipeline";
import ClaimForm from "../components/ClaimForm";
import TraceViewer from "../components/TraceViewer";

export default function ClaimsDashboard() {
  const { loading, result, error, runPipeline } = usePipeline();

  return (
    <div className="min-h-screen bg-slate-50 p-8 font-sans text-slate-900">
      <header className="mb-8 border-b pb-4">
        <h1 className="text-3xl font-bold flex items-center gap-2">
          <Activity className="text-blue-600" /> Plum AI Adjudication Pod
        </h1>
        <p className="text-slate-500 mt-2">Multi-Agent Claims Processing Architecture</p>
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