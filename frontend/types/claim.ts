export type DecisionType = "APPROVED" | "PARTIAL" | "REJECTED" | "MANUAL_REVIEW";

export interface FinalDecision {
  claim_id: string;
  decision: DecisionType;
  approved_amount: number;
  rejection_reasons: string[];
  notes: string;
  confidence_score: number;
}

export interface AgentTrace {
  triage?: any;
  extraction?: any;
}

export interface PipelineResult {
  status: string;
  final_decision: FinalDecision;
  agent_trace: AgentTrace;
}