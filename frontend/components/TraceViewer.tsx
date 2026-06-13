import { AlertCircle, CheckCircle, FileText } from "lucide-react";
import { PipelineResult } from "../types/claim";

interface TraceViewerProps {
  result: PipelineResult | null;
  error: string | null;
  isLoading: boolean;
}

export default function TraceViewer({ result, error, isLoading }: TraceViewerProps) {
  if (error) {
    return (
      <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded-md flex items-start gap-3">
        <AlertCircle className="text-red-500 mt-1" />
        <div>
          <h3 className="text-red-800 font-bold">Pipeline Error</h3>
          <p className="text-red-700">{error}</p>
        </div>
      </div>
    );
  }

  if (!result && !isLoading) {
    return (
      <div className="h-full min-h-[400px] flex items-center justify-center border-2 border-dashed border-slate-300 rounded-xl text-slate-400">
        Select a scenario and run the pipeline to view agent traces.
      </div>
    );
  }

  if (!result) return null; // Loading state is handled by the button in the form

  const isApproved = result.final_decision.decision === "APPROVED";

  return (
    <div className="space-y-6">
      {/* Final Decision Card */}
      <div className={`p-6 rounded-xl border ${isApproved ? 'bg-green-50 border-green-200' : 'bg-orange-50 border-orange-200'}`}>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-bold flex items-center gap-2">
            {isApproved ? <CheckCircle className="text-green-600" /> : <AlertCircle className="text-orange-600" />}
            Decision: {result.final_decision.decision}
          </h2>
          <span className="text-lg font-semibold bg-white px-3 py-1 rounded-full shadow-sm">
            Approved: ₹{result.final_decision.approved_amount}
          </span>
        </div>
        <div className="bg-white p-4 rounded-lg shadow-sm border border-slate-100">
          <h3 className="text-sm font-bold text-slate-500 uppercase tracking-wider mb-2">Adjudicator Reasoning Trace</h3>
          <p className="text-slate-800 leading-relaxed">{result.final_decision.notes}</p>
        </div>
      </div>

      {/* Agent Traces */}
      <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
        <h2 className="text-xl font-semibold mb-4 border-b pb-2 flex items-center gap-2">
          <FileText className="text-slate-400" /> Observability Traces
        </h2>

        {/* Triage Trace */}
        <div className="mb-6">
          <h3 className="font-bold text-slate-700 mb-2">1. Intake & Triage Agent</h3>
          {result.agent_trace.triage?.is_valid === false ? (
            <div className="bg-red-50 text-red-700 p-3 rounded text-sm font-mono border border-red-100">
              <strong>BLOCKED:</strong> {result.agent_trace.triage.error_message}
            </div>
          ) : (
            <div className="bg-slate-50 p-3 rounded text-sm font-mono border border-slate-100 text-green-700">
              PASS: Required documents verified.
            </div>
          )}
        </div>

        {/* Extraction Trace */}
        {result.agent_trace.extraction && (
          <div>
            <h3 className="font-bold text-slate-700 mb-2">2. Extraction Agent (Structured JSON)</h3>
            <div className="bg-slate-800 text-green-400 p-4 rounded-lg text-xs font-mono overflow-auto max-h-96">
              <pre>{JSON.stringify(result.agent_trace.extraction, null, 2)}</pre>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}