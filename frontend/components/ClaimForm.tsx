import { useState } from "react";
import { Play, Clock } from "lucide-react";
import { demoScenarios, ScenarioKey } from "../data/scenarios";

interface ClaimFormProps {
  onRun: (payload: any) => void;
  isLoading: boolean;
}

export default function ClaimForm({ onRun, isLoading }: ClaimFormProps) {
  const [activeScenario, setActiveScenario] = useState<ScenarioKey>("diagnostic_success");

  return (
    <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200 h-fit">
      <h2 className="text-xl font-semibold mb-4 border-b pb-2">1. Submit Claim</h2>

      <div className="mb-6">
        <label className="block text-sm font-medium text-slate-700 mb-2">Select Demo Scenario</label>
        <select
          className="w-full p-2 border border-slate-300 rounded-md bg-slate-50"
          value={activeScenario}
          onChange={(e) => setActiveScenario(e.target.value as ScenarioKey)}
        >
          {Object.entries(demoScenarios).map(([key, data]) => (
            <option key={key} value={key}>{data.name}</option>
          ))}
        </select>
      </div>

      <div className="bg-slate-100 p-4 rounded-md mb-6 text-sm font-mono overflow-x-auto">
        <p className="font-bold mb-2 text-slate-500">// Payload Preview</p>
        <pre>{JSON.stringify(demoScenarios[activeScenario].payload, null, 2)}</pre>
      </div>

      <button
        onClick={() => onRun(demoScenarios[activeScenario].payload)}
        disabled={isLoading}
        className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-4 rounded-lg flex items-center justify-center gap-2 transition-all disabled:opacity-50"
      >
        {isLoading ? <Clock className="animate-spin" /> : <Play />}
        {isLoading ? "Agents Processing..." : "Run Multi-Agent Pipeline"}
      </button>
    </div>
  );
}