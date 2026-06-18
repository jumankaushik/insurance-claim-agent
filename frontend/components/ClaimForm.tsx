import { useState, useEffect } from "react";
import { Play, Clock, Upload, Trash2, FileImage, FileJson, User } from "lucide-react";

interface ClaimFormProps {
  onRun: (payload: any) => void;
  isLoading: boolean;
}

export default function ClaimForm({ onRun, isLoading }: ClaimFormProps) {
  const [activeTab, setActiveTab] = useState<"MANUAL" | "TEST_CASE">("MANUAL");

  // --- Manual Entry State ---
  const [memberId, setMemberId] = useState("EMP001");
  const [claimCategory, setClaimCategory] = useState("CONSULTATION");
  const [claimedAmount, setClaimedAmount] = useState<number | "">("");
  const [hospitalName, setHospitalName] = useState("");
  const [treatmentDate, setTreatmentDate] = useState("");
  const [uploadedFiles, setUploadedFiles] = useState<{ name: string; base64: string }[]>([]);

  // --- Test Case State ---
  const [testCases, setTestCases] = useState<any[]>([]);
  const [selectedTestCaseId, setSelectedTestCaseId] = useState<string>("");

  // Fetch test cases on load
  //Localhost to production
  useEffect(() => {
    fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/test-cases`)
      .then(res => res.json())
      .then(data => {
        setTestCases(data);
        if (data.length > 0) setSelectedTestCaseId(data[0].case_id);
      })
      .catch(err => console.error("Failed to load test cases:", err));
  }, []);

  // --- Helpers ---
  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const filesArray = Array.from(e.target.files);
      const newFiles = await Promise.all(
        filesArray.map(async (file) => {
          const base64 = await convertToBase64(file);
          return { name: file.name, base64: base64 as string };
        })
      );
      setUploadedFiles([...uploadedFiles, ...newFiles]);
    }
  };

  const convertToBase64 = (file: File) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => resolve(reader.result);
      reader.onerror = (error) => reject(error);
    });
  };

  const handleSubmit = () => {
    if (activeTab === "MANUAL") {
      const payload = {
        member_id: memberId,
        policy_id: "PLUM_GHI_2024",
        claim_category: claimCategory,
        treatment_date: treatmentDate || new Date().toISOString().split('T')[0],
        claimed_amount: Number(claimedAmount),
        hospital_name: hospitalName || "Unknown",
        documents: uploadedFiles.map((f, index) => ({
          file_id: `DOC_${Date.now()}_${index}`,
          file_name: f.name,
          content_path: null,
          base64_data: f.base64
        }))
      };
      onRun(payload);
    } else {
      const selectedCase = testCases.find(tc => tc.case_id === selectedTestCaseId);
      if (selectedCase) onRun(selectedCase.input);
    }
  };

  const selectedTestCaseData = testCases.find(tc => tc.case_id === selectedTestCaseId);

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 h-fit overflow-hidden flex flex-col">
      {/* Tabs */}
      <div className="flex border-b border-slate-200 bg-slate-50">
        <button
          onClick={() => setActiveTab("MANUAL")}
          className={`flex-1 py-3 text-sm font-bold flex items-center justify-center gap-2 transition-colors ${activeTab === "MANUAL" ? "bg-white text-blue-600 border-b-2 border-blue-600" : "text-slate-500 hover:text-slate-700"}`}
        >
          <User size={16} /> Member Upload
        </button>
        <button
          onClick={() => setActiveTab("TEST_CASE")}
          className={`flex-1 py-3 text-sm font-bold flex items-center justify-center gap-2 transition-colors ${activeTab === "TEST_CASE" ? "bg-white text-blue-600 border-b-2 border-blue-600" : "text-slate-500 hover:text-slate-700"}`}
        >
          <FileJson size={16} /> Select Test Case
        </button>
      </div>

      <div className="p-6 space-y-5">

        {/* --- MANUAL MODE UI --- */}
        {activeTab === "MANUAL" && (
          <div className="space-y-4 animate-in fade-in slide-in-from-bottom-2 duration-300">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-1">Member ID</label>
                <input type="text" className="w-full p-2.5 border rounded-lg bg-slate-50 focus:ring-2 outline-none" value={memberId} onChange={(e) => setMemberId(e.target.value.toUpperCase())} placeholder="EMP001" />
              </div>
              <div>
                <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-1">Category</label>
                <select className="w-full p-2.5 border rounded-lg bg-slate-50 focus:ring-2 outline-none" value={claimCategory} onChange={(e) => setClaimCategory(e.target.value)}>
                  <option value="CONSULTATION">Consultation (OPD)</option>
                  <option value="DIAGNOSTIC">Diagnostic & Labs</option>
                  <option value="PHARMACY">Pharmacy</option>
                  <option value="DENTAL">Dental</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-1">Date</label>
                <input type="date" className="w-full p-2.5 border rounded-lg bg-slate-50 focus:ring-2 outline-none" value={treatmentDate} onChange={(e) => setTreatmentDate(e.target.value)} />
              </div>
              <div>
                <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-1">Amount (₹)</label>
                <input type="number" className="w-full p-2.5 border rounded-lg bg-slate-50 focus:ring-2 outline-none" value={claimedAmount} onChange={(e) => setClaimedAmount(e.target.value === "" ? "" : Number(e.target.value))} placeholder="0.00" />
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-1">Hospital Name</label>
              <input type="text" className="w-full p-2.5 border rounded-lg bg-slate-50 focus:ring-2 outline-none" value={hospitalName} onChange={(e) => setHospitalName(e.target.value)} placeholder="Apollo Hospitals" />
            </div>

            <div className="mt-4">
              <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Documents</label>
              <label className="flex flex-col items-center justify-center w-full h-28 border-2 border-slate-300 border-dashed rounded-lg cursor-pointer bg-slate-50 hover:bg-blue-50 transition-colors">
                <Upload className="w-6 h-6 text-blue-500 mb-1" />
                <p className="text-sm text-slate-600 font-semibold">Click to upload files</p>
                <input type="file" className="hidden" multiple accept="image/*" onChange={handleFileChange} />
              </label>
            </div>

            {uploadedFiles.length > 0 && (
              <div className="space-y-2 max-h-32 overflow-y-auto">
                {uploadedFiles.map((file, index) => (
                  <div key={index} className="flex items-center justify-between bg-slate-100 p-2 rounded text-sm border border-slate-200">
                    <div className="flex items-center gap-2 overflow-hidden"><FileImage size={14} className="text-slate-500"/> <span className="truncate w-40">{file.name}</span></div>
                    <button onClick={() => setUploadedFiles(uploadedFiles.filter((_, i) => i !== index))} className="text-red-400 hover:text-red-600"><Trash2 size={14} /></button>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* --- TEST CASE MODE UI --- */}
        {activeTab === "TEST_CASE" && (
          <div className="space-y-4 animate-in fade-in slide-in-from-bottom-2 duration-300">
            <div>
              <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Select Ground-Truth Scenario</label>
              <select
                className="w-full p-3 border border-slate-300 rounded-lg bg-slate-50 focus:ring-2 focus:ring-blue-500 outline-none shadow-sm"
                value={selectedTestCaseId}
                onChange={(e) => setSelectedTestCaseId(e.target.value)}
              >
                {testCases.map(tc => (
                  <option key={tc.case_id} value={tc.case_id}>{tc.case_id}: {tc.case_name}</option>
                ))}
              </select>
            </div>

            {selectedTestCaseData && (
              <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
                <p className="text-xs text-blue-300 font-mono mb-2 uppercase tracking-wider flex items-center gap-2"><FileJson size={14}/> Test Case Payload Preview</p>
                <p className="text-sm text-slate-300 mb-3 italic">"{selectedTestCaseData.description}"</p>
                <div className="bg-slate-950 p-3 rounded text-xs font-mono text-green-400 overflow-y-auto max-h-48 scrollbar-thin">
                  <pre>{JSON.stringify(selectedTestCaseData.input, null, 2)}</pre>
                </div>
              </div>
            )}
          </div>
        )}

        <button
          onClick={handleSubmit}
          disabled={isLoading || (activeTab === "MANUAL" && (!claimedAmount || uploadedFiles.length === 0))}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3.5 px-4 rounded-lg flex items-center justify-center gap-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-md mt-4"
        >
          {isLoading ? <Clock className="animate-spin" /> : <Play fill="currentColor" />}
          {isLoading ? "Agents Processing Data..." : "Run Multi-Agent Pipeline"}
        </button>
      </div>
    </div>
  );
}