"use client";

import { useEffect, useState } from "react";
import { ShieldAlert, CheckCircle, XCircle, AlertTriangle, FileText, Search, User, BriefcaseMedical } from "lucide-react";

export default function AdminDashboard() {
  const [claims, setClaims] = useState<any[]>([]);
  const [selectedClaim, setSelectedClaim] = useState<any | null>(null);
  const [adminNotes, setAdminNotes] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Fetch the processed claims (Live queue + Eval results)
  useEffect(() => {
    fetch('http://localhost:8000/api/admin/claims') // <-- CHANGED THIS LINE
      .then(res => res.json())
      .then(data => {
        setClaims(data);
        if (data.length > 0) setSelectedClaim(data[0]);
      })
      .catch(err => console.error("Failed to fetch claims:", err));
  }, []);

  const handleOverride = async (decision: string) => {
    if (!selectedClaim) return;
    setIsSubmitting(true);

    try {
      const res = await fetch(`http://localhost:8000/api/admin/claims/${selectedClaim.case_id}/override`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ decision, admin_notes: adminNotes })
      });

      if (res.ok) {
        // Update local state to reflect the override
        const updatedClaims = claims.map(c =>
          c.case_id === selectedClaim.case_id ? { ...c, actual: decision, is_overridden: true } : c
        );
        setClaims(updatedClaims);
        setSelectedClaim({ ...selectedClaim, actual: decision, is_overridden: true });
        setAdminNotes("");
        alert(`Claim successfully marked as ${decision}`);
      }
    } catch (err) {
      alert("Failed to update claim.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const getStatusColor = (status: string) => {
    if (status?.includes("APPROVED")) return "bg-green-100 text-green-800 border-green-200";
    if (status?.includes("REJECTED")) return "bg-red-100 text-red-800 border-red-200";
    if (status?.includes("PARTIAL")) return "bg-yellow-100 text-yellow-800 border-yellow-200";
    return "bg-orange-100 text-orange-800 border-orange-200"; // For MANUAL_REVIEW
  };

  return (
    <div className="min-h-screen bg-slate-100 flex flex-col font-sans">
      {/* Admin Navbar */}
      <nav className="bg-slate-900 text-white px-6 py-4 flex items-center justify-between shadow-md z-10">
        <div className="flex items-center gap-3">
          <ShieldAlert className="text-blue-400" />
          <h1 className="text-xl font-bold tracking-wide">Plum Ops Center</h1>
        </div>
        <div className="flex items-center gap-4 text-sm font-medium">
          <span className="bg-slate-800 px-3 py-1 rounded-full text-slate-300">Logged in as: Claims Admin</span>
        </div>
      </nav>

      <div className="flex flex-1 overflow-hidden">
        {/* Left Pane: Claims Queue */}
        <div className="w-1/3 bg-white border-r border-slate-200 flex flex-col overflow-y-auto">
          <div className="p-4 border-b border-slate-200 bg-slate-50 sticky top-0">
            <h2 className="font-bold text-slate-800 mb-3 flex items-center gap-2"><BriefcaseMedical size={18}/> Claims Queue</h2>
            <div className="relative">
              <Search className="absolute left-3 top-2.5 text-slate-400" size={16} />
              <input type="text" placeholder="Search Case ID..." className="w-full pl-9 pr-3 py-2 border rounded-lg text-sm bg-white text-slate-900 focus:ring-2 outline-none" />
            </div>
          </div>

          <div className="divide-y divide-slate-100">
            {claims.map((claim) => (
              <div
                key={claim.case_id}
                onClick={() => setSelectedClaim(claim)}
                className={`p-4 cursor-pointer hover:bg-blue-50 transition-colors ${selectedClaim?.case_id === claim.case_id ? 'bg-blue-50 border-l-4 border-blue-600' : 'border-l-4 border-transparent'}`}
              >
                <div className="flex justify-between items-start mb-1">
                  <span className="font-bold text-slate-800 text-sm">{claim.case_id}</span>
                  <span className={`text-xs px-2 py-0.5 rounded font-bold border ${getStatusColor(claim.actual)}`}>
                    {claim.actual || "PENDING"}
                  </span>
                </div>
                <p className="text-xs text-slate-500 line-clamp-2 mt-2">{claim.description}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Right Pane: Claim Inspector */}
        <div className="flex-1 bg-slate-50 p-6 overflow-y-auto">
          {selectedClaim ? (
            <div className="max-w-4xl mx-auto space-y-6">

              {/* Header */}
              <div className="bg-white p-6 rounded-xl border shadow-sm flex items-center justify-between">
                <div>
                  <h2 className="text-2xl font-black text-slate-800">{selectedClaim.case_id}</h2>
                  <p className="text-slate-500 mt-1">{selectedClaim.description}</p>
                </div>
                <div className={`px-4 py-2 rounded-lg border-2 font-bold text-lg ${getStatusColor(selectedClaim.actual)}`}>
                  AI Decision: {selectedClaim.actual || "UNKNOWN"}
                </div>
              </div>

              {/* Explainability Trace */}
              <div className="bg-white rounded-xl border shadow-sm overflow-hidden">
                <div className="bg-slate-900 text-white p-4 flex items-center gap-2 font-bold">
                  <FileText size={18} /> System Reasoning Trace (Explainability)
                </div>
                <div className="p-6">
                  <p className="text-slate-700 leading-relaxed whitespace-pre-wrap font-mono text-sm bg-slate-50 p-4 border rounded-lg">
                    {selectedClaim.trace}
                  </p>
                </div>
              </div>

              {/* Manual Override Action Area */}
              <div className="bg-white rounded-xl border shadow-sm overflow-hidden border-blue-100">
                <div className="bg-blue-50 text-blue-900 p-4 flex items-center gap-2 font-bold border-b border-blue-100">
                  <User size={18} /> Human-in-the-Loop Override
                </div>
                <div className="p-6">
                  <p className="text-sm text-slate-500 mb-4">
                    If the AI's decision requires a manual correction or if this case was flagged for MANUAL_REVIEW, provide your reasoning below and execute an override.
                  </p>

                  <textarea
                    className="w-full p-3 border rounded-lg bg-slate-50 text-slate-900 focus:ring-2 focus:ring-blue-500 outline-none min-h-[100px] text-sm mb-4"
                    placeholder="Enter notes for member communication and compliance audit..."
                    value={adminNotes}
                    onChange={(e) => setAdminNotes(e.target.value)}
                  />

                  <div className="flex gap-4">
                    <button
                      onClick={() => handleOverride("APPROVED")}
                      disabled={isSubmitting || !adminNotes}
                      className="flex-1 bg-green-600 hover:bg-green-700 text-white font-bold py-3 rounded-lg flex items-center justify-center gap-2 transition-all disabled:opacity-50"
                    >
                      <CheckCircle size={18}/> Approve Override
                    </button>
                    <button
                      onClick={() => handleOverride("REJECTED")}
                      disabled={isSubmitting || !adminNotes}
                      className="flex-1 bg-red-600 hover:bg-red-700 text-white font-bold py-3 rounded-lg flex items-center justify-center gap-2 transition-all disabled:opacity-50"
                    >
                      <XCircle size={18}/> Reject Override
                    </button>
                  </div>
                </div>
              </div>

            </div>
          ) : (
            <div className="h-full flex flex-col items-center justify-center text-slate-400">
              <ShieldAlert size={48} className="mb-4 opacity-50" />
              <p className="font-medium text-lg">Select a claim from the queue to review.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}