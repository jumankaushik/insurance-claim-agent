from pydantic import BaseModel, Field
from typing import List, Optional, Literal

# ---------------------------------------------------------
# 1. Input Schemas (What the UI sends to the backend)
# ---------------------------------------------------------

class DocumentUpload(BaseModel):
    file_id: str = Field(description="Unique identifier for the file.")
    file_name: Optional[str] = Field(default="test_doc", description="Original name of the uploaded file.")
    content_path: Optional[str] = Field(default=None, description="Local path (used for mock testing).")
    base64_data: Optional[str] = Field(default=None, description="Base64 encoded string of the file.")

    # --- New fields to support automated test_cases.json ---
    actual_type: Optional[str] = Field(default=None, description="The document type defined in test cases.")
    content: Optional[dict] = Field(default=None, description="Pre-extracted text data from test cases.")
    quality: Optional[str] = Field(default=None, description="Document quality flag from test cases.")

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
    description: str = Field(description="Name of the medicine, lab test, or billing charge.")
    amount: float = Field(default=0.0, description="Cost amount. Set to 0 if it's a prescription/lab report with no prices.")
    # --- New fields for Prescription & Lab Reports ---
    dosage_or_quantity: Optional[str] = Field(default=None, description="e.g., '1-1-1 x 5 days', '15 tabs', or batch numbers.")
    test_result: Optional[str] = Field(default=None, description="Lab results (e.g., '13.2 g/dL', 'NEGATIVE', '185,000 /μL').")
    is_cosmetic_or_excluded: bool = Field(default=False, description="Flag if the item sounds like a cosmetic or excluded procedure.")

class ExtractedMedicalData(BaseModel):
    # --- Patient Demographics ---
    patient_name_on_documents: List[str] = Field(description="List of all patient names found across all documents to check for mismatches.")
    patient_age_gender: Optional[str] = Field(default=None, description="Extracted age and gender (e.g., '39 / Male').")
    document_dates: List[str] = Field(default=[], description="All dates found on bills, prescriptions, or lab reports.")

    # --- Provider Details (Doctor, Hospital, Lab, Pharmacy) ---
    provider_name: Optional[str] = Field(default=None, description="Name of the Hospital, Clinic, Lab, or Pharmacy.")
    provider_identifiers: List[str] = Field(default=[], description="Any GSTIN, NABL Lab ID, or Drug License numbers found.")
    doctor_name: Optional[str] = None
    doctor_registration_number: Optional[str] = Field(default=None, description="State medical registration number (e.g., KA/45678/2015).")

    # --- Medical Details ---
    diagnosis: Optional[str] = Field(default=None, description="Expand medical shorthand if detected (e.g., convert 'T2DM' to 'Type 2 Diabetes').")
    line_items: List[LineItem] = []
    total_billed: float = 0.0

    # --- Quality & Fraud Metadata ---
    extraction_confidence: float = Field(ge=0.0, le=1.0, description="Overall confidence. Lower if handwriting is messy or stamps obscure text.")
    unreadable_documents: List[str] = Field(default=[], description="List of file_ids that were too blurry to read.")
    fraud_flags: List[str] = Field(default=[], description="List of suspicious markers like 'DOCUMENT_ALTERATION', 'DUPLICATE_STAMP', etc.")
    regional_language_detected: bool = Field(default=False, description="True if Hindi, Tamil, Telugu, or other regional languages are mixed with English.")

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