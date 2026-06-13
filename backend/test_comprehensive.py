import asyncio
import json
from models.claims import ClaimInput, DocumentUpload
from agents.workflow import app as claim_workflow

async def test_full_pipeline():
    print("--- 🚀 Testing Full Multi-Agent Pipeline ---")
    print("Simulating a 'DIAGNOSTIC' claim requiring 3 documents...")

    # 1. Construct the complex claim
    # Rajesh Kumar is an active member in policy_terms.json
    claim_payload = ClaimInput(
        member_id="EMP001",
        policy_id="PLUM_GHI_2024",
        claim_category="DIAGNOSTIC",
        treatment_date="2024-11-10",
        claimed_amount=1350.0,
        documents=[
            DocumentUpload(
                file_id="DOC_001",
                file_name="prescription.jpg",
                content_path="data/mock_prescription_v2.jpg"
            ),
            DocumentUpload(
                file_id="DOC_002",
                file_name="lab_report.jpg",
                content_path="data/mock_lab_report.jpg"
            ),
            DocumentUpload(
                file_id="DOC_003",
                file_name="hospital_bill.jpg",
                content_path="data/mock_hospital_bill_v2.jpg"
            )
        ]
    )

    try:
        # 2. Feed the claim into the LangGraph state machine
        initial_state = {"claim_input": claim_payload}
        final_state = await claim_workflow.ainvoke(initial_state)

        # 3. Print the Extracted Data to verify our new Pydantic schemas caught everything
        print("\n--- 🧠 EXTRACTION AGENT OUTPUT ---")
        extracted = final_state.get("extracted_data")
        if extracted:
            print(extracted.model_dump_json(indent=2))
        else:
            print("Extraction failed or was skipped.")

        # 4. Print the Final Adjudication Decision
        print("\n--- ⚖️ FINAL ADJUDICATOR DECISION ---")
        decision = final_state.get("final_decision")
        if decision:
            print(decision.model_dump_json(indent=2))

    except Exception as e:
        print(f"❌ Pipeline Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_full_pipeline())