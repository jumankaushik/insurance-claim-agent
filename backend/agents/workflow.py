from typing import TypedDict, Optional
from models.claims import ClaimInput, DocumentVerification, ExtractedMedicalData, FinalDecision

class ClaimState(TypedDict):
    # The initial input
    claim_input: ClaimInput

    # State populated by Agent 1
    triage_result: Optional[DocumentVerification]

    # State populated by Agent 2
    extracted_data: Optional[ExtractedMedicalData]

    # State populated by Agent 3/4
    final_decision: Optional[FinalDecision]

    # System metadata
    component_failed: bool