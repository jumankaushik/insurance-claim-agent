import { useState } from "react";
import axios from "axios";
import { PipelineResult } from "../types/claim";

export function usePipeline() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<PipelineResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const runPipeline = async (payload: any) => {
    setLoading(true);
    setResult(null);
    setError(null);
    try {
      // FIX: Use the environment variable for the backend URL
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await axios.post<PipelineResult>(`${API_URL}/api/process-claim`, payload);
      setResult(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || "An error occurred connecting to the backend.");
    } finally {
      setLoading(false);
    }
  };

  return { loading, result, error, runPipeline };
}