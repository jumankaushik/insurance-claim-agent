from models.claims import ClaimInput, DocumentUpload, FinalDecision
from pydantic import ValidationError

def test_contracts():
    print("--- Testing ClaimInput Validation ---")
    try:
        # Simulating the UI sending a payload for TC004
        mock_ui_payload = ClaimInput(
            member_id="EMP001",
            policy_id="PLUM_GHI_2024",
            claim_category="CONSULTATION", # Must match the Literal exactly
            treatment_date="2024-11-01",
            claimed_amount=1500.00,
            documents=[
                DocumentUpload(file_id="F007", file_name="prescription.jpg", content_path="/tmp/presc.jpg"),
                DocumentUpload(file_id="F008", file_name="bill.jpg", content_path="/tmp/bill.jpg")
            ]
        )
        print("✅ ClaimInput created successfully!")
        print(mock_ui_payload.model_dump_json(indent=2))

    except ValidationError as e:
        print("❌ ClaimInput Validation Failed:")
        print(e)

    print("\n--- Testing FinalDecision Validation ---")
    try:
        # Simulating Agent 4 outputting the final decision
        mock_agent_output = FinalDecision(
            claim_id="CLM-998877",
            decision="APPROVED",
            approved_amount=1350.00,
            rejection_reasons=[],
            notes="10% co-pay applied on consultation category (₹150 deducted)",
            confidence_score=0.92
        )
        print("✅ FinalDecision created successfully!")
        print(mock_agent_output.model_dump_json(indent=2))

    except ValidationError as e:
        print("❌ FinalDecision Validation Failed:")
        print(e)

if __name__ == "__main__":
    test_contracts()