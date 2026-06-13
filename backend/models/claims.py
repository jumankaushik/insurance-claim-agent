from pydantic import BaseModel, Field
from typing import List, Optional, Literal

# ---------------------------------------------------------
# 1. Input Schemas (What the UI sends to the backend)
# ---------------------------------------------------------

class DocumentUpload(BaseModel):
    file_id: str
    file_name: str
    # In a real system, this would be a URL or base64 string.
    # For this assignment, we might mock the OCR or pass the path.
    content_path: Optional[str] = None

class ClaimInput(BaseModel):
    member_id: str
    policy_id: str
    claim_category: Literal["CONSULTATION", "DIAGNOSTIC", "PHARMACY", "DENTAL", "VISION", "ALTERNATIVE_MEDICINE"]
    treatment_date: str
    claimed_amount: float
    hospital_name: Optional[str] = None
    documents: List[DocumentUpload]

# ---------------------------------------------------------
# 2. Agent 1: Triage Output Contract
# ---------------------------------------------------------

class DocumentVerification(BaseModel):
    is_valid: bool = Field(description="True if the uploaded documents match the required types for the claim category.")
    extracted_document_types: List[str] = Field(description="The actual document types detected by vision AI (e.g., PRESCRIPTION, PHARMACY_BILL).")
    error_message: Optional[str] = Field(description="Specific, actionable error message if is_valid is false. Must name the missing/wrong document.")

# ---------------------------------------------------------
# 3. Agent 2: Extraction Output Contract
# ---------------------------------------------------------

class LineItem(BaseModel):
    description: str
    amount: float
    is_cosmetic_or_excluded: bool = Field(default=False, description="Flag if the item sounds like a cosmetic or excluded procedure.")

class ExtractedMedicalData(BaseModel):
    patient_name_on_documents: List[str] = Field(description="List of all patient names found across all documents to check for mismatches.")
    doctor_name: Optional[str] = None
    diagnosis: Optional[str] = None
    line_items: List[LineItem] = []
    total_billed: float = 0.0
    extraction_confidence: float = Field(ge=0.0, le=1.0, description="Overall confidence in the extraction. Lower if handwriting is messy.")
    unreadable_documents: List[str] = Field(default=[], description="List of file_ids that were too blurry to read.")

# ---------------------------------------------------------
# 4. Agent 3 & 4: Adjudication Final Contract
# ---------------------------------------------------------

class FinalDecision(BaseModel):
    claim_id: str
    decision: Literal["APPROVED", "PARTIAL", "REJECTED", "MANUAL_REVIEW"]
    approved_amount: float = 0.0
    rejection_reasons: List[str] = Field(default=[], description="Specific reasons like WAITING_PERIOD, EXCLUDED_CONDITION, PER_CLAIM_EXCEEDED.")
    notes: str = Field(description="Detailed trace explaining math: discounts, copays, and sub-limits applied.")
    confidence_score: float = Field(ge=0.0, le=1.0)
    routing_flag: Optional[str] = Field(default=None, description="Used to flag same-day claim limits or fraud thresholds for manual review.")