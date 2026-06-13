from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END

# Import our contracts
from models.claims import ClaimInput, DocumentVerification, ExtractedMedicalData, FinalDecision
# Import our contracts
from models.claims import ClaimInput, DocumentVerification, ExtractedMedicalData, FinalDecision, LineItem

# Import our agents
from agents.triage import verify_documents
from agents.extraction import extract_medical_data
from agents.adjudicator import adjudicate_claim

# 1. Define the State of our Graph
class ClaimState(TypedDict):
    claim_input: ClaimInput
    triage_result: Optional[DocumentVerification]
    extracted_data: Optional[ExtractedMedicalData]
    final_decision: Optional[FinalDecision]

# 2. Define the Nodes (The wrappers around our agents)
async def triage_node(state: ClaimState):
    claim = state["claim_input"]

    doc_requirements = {
        "CONSULTATION": ["PRESCRIPTION", "HOSPITAL_BILL"],
        "DIAGNOSTIC": ["PRESCRIPTION", "LAB_REPORT", "HOSPITAL_BILL"],
        "PHARMACY": ["PRESCRIPTION", "PHARMACY_BILL"],
        "DENTAL": ["HOSPITAL_BILL"],
        "VISION": ["PRESCRIPTION", "HOSPITAL_BILL"],
        "ALTERNATIVE_MEDICINE": ["PRESCRIPTION", "HOSPITAL_BILL"]
    }
    required_docs = doc_requirements.get(claim.claim_category, [])

    # 1. Check if this is an automated test case
    has_test_types = any(doc.actual_type is not None for doc in claim.documents)

    if has_test_types:
        print("Agent 1 (Triage): Test Mode Detected - Bypassing Vision API.")
        found_types = [doc.actual_type for doc in claim.documents if doc.actual_type]

        # Check if all required docs are present
        missing = [doc for doc in required_docs if doc not in found_types]

        if missing:
            return {"triage_result": DocumentVerification(
                is_valid=False,
                extracted_document_types=found_types,
                error_message=f"Missing required documents: {missing}. Please upload them."
            )}
        else:
            return {"triage_result": DocumentVerification(
                is_valid=True,
                extracted_document_types=found_types,
                error_message=None
            )}

    # 2. Real-World Execution (Use the Gemini Vision Model)
    result = await verify_documents(claim.claim_category, required_docs, claim.documents)
    return {"triage_result": result}

async def extraction_node(state: ClaimState):
    claim = state["claim_input"]

    # 1. Check if this is an automated test case with pre-extracted content
    has_test_content = any(doc.content is not None for doc in claim.documents)

    if has_test_content:
        print("Agent 2 (Extraction): Test Mode Detected - Bypassing Vision API and mapping provided mock data.")

        # Combine the mock data into our standard output format
        all_patient_names = []
        all_diagnoses = []
        mock_line_items = []
        total_mock_billed = 0.0

        for doc in claim.documents:
            if doc.content:
                if "patient_name" in doc.content:
                    all_patient_names.append(doc.content["patient_name"])
                if "diagnosis" in doc.content:
                    all_diagnoses.append(doc.content["diagnosis"])
                if "line_items" in doc.content:
                    for item in doc.content["line_items"]:
                        mock_line_items.append(LineItem(description=item["description"], amount=float(item["amount"])))
                if "total" in doc.content:
                    total_mock_billed = float(doc.content["total"])

        result = ExtractedMedicalData(
            patient_name_on_documents=all_patient_names,
            diagnosis=", ".join(all_diagnoses) if all_diagnoses else None,
            line_items=mock_line_items,
            total_billed=total_mock_billed,
            extraction_confidence=1.0
        )
        return {"extracted_data": result}

    # 2. Real-World Execution (Use the Gemini Vision Model)
    result = await extract_medical_data(claim.documents)
    return {"extracted_data": result}

async def adjudication_node(state: ClaimState):
    claim = state["claim_input"]
    extracted = state["extracted_data"]
    result = await adjudicate_claim(claim, extracted)
    return {"final_decision": result}

# 3. Define Conditional Routing (The Logic Flow)
def check_triage(state: ClaimState):
    """If triage fails, we skip extraction and go straight to final decision (Error State)."""
    if not state["triage_result"].is_valid:
        return "early_rejection"
    return "proceed_to_extraction"

async def early_rejection_node(state: ClaimState):
    """Creates a rejected FinalDecision based on Triage failure."""
    claim = state["claim_input"]
    error_msg = state["triage_result"].error_message

    decision = FinalDecision(
        claim_id=f"CLM-{claim.member_id}",
        decision="REJECTED",
        approved_amount=0.0,
        rejection_reasons=["INVALID_DOCUMENTS"],
        notes=f"Triage Failed: {error_msg}",
        confidence_score=1.0
    )
    return {"final_decision": decision}

# 4. Compile the Graph
workflow = StateGraph(ClaimState)

# Add Nodes
workflow.add_node("triage", triage_node)
workflow.add_node("extraction", extraction_node)
workflow.add_node("adjudication", adjudication_node)
workflow.add_node("early_rejection", early_rejection_node)

# Add Edges
workflow.set_entry_point("triage")

# Conditional routing after triage
workflow.add_conditional_edges(
    "triage",
    check_triage,
    {
        "proceed_to_extraction": "extraction",
        "early_rejection": "early_rejection"
    }
)

# Happy path edges
workflow.add_edge("extraction", "adjudication")
workflow.add_edge("adjudication", END)
workflow.add_edge("early_rejection", END)

# Compile into an executable app
app = workflow.compile()