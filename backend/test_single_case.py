import asyncio
import json
from models.claims import ClaimInput
from agents.workflow import app as claim_workflow

async def run_single_test():
    print("--- 🔬 Testing TC010: Network Hospital Math Logic ---\n")

    # 1. The exact test case payload you provided
    test_case_data = {
        "member_id": "EMP010",
        "policy_id": "PLUM_GHI_2024",
        "claim_category": "CONSULTATION",
        "treatment_date": "2024-11-03",
        "claimed_amount": 4500,
        "hospital_name": "Apollo Hospitals",
        "ytd_claims_amount": 8000,
        "documents": [
            {
                "file_id": "F019",
                "actual_type": "PRESCRIPTION",
                "content": {
                    "doctor_name": "Dr. S. Iyer",
                    "doctor_registration": "TN/56789/2013",
                    "patient_name": "Deepak Shah",
                    "diagnosis": "Acute Bronchitis",
                    "medicines": ["Amoxicillin 500mg", "Salbutamol Inhaler"]
                }
            },
            {
                "file_id": "F020",
                "actual_type": "HOSPITAL_BILL",
                "content": {
                    "hospital_name": "Apollo Hospitals",
                    "patient_name": "Deepak Shah",
                    "line_items": [
                        { "description": "Consultation Fee", "amount": 1500 },
                        { "description": "Medicines", "amount": 3000 }
                    ],
                    "total": 4500
                }
            }
        ]
    }

    # 2. Convert to Pydantic and run through the graph
    try:
        payload = ClaimInput(**test_case_data)
        result = await claim_workflow.ainvoke({"claim_input": payload})

        final = result['final_decision']

        # 3. Print the comparative output
        print("✅ Pipeline Execution Complete!\n")
        print("==================================================")
        print("🎯 EXPECTED OUTCOME")
        print("==================================================")
        print("Decision:  APPROVED")
        print("Amount:    ₹3240.0")
        print("Reasoning: Network discount (20%) applied first on ₹4,500 = ₹3,600. Co-pay (10%) applied on ₹3,600 = ₹360 deducted. Final: ₹3,240.")

        print("\n==================================================")
        print("🤖 ACTUAL SYSTEM OUTCOME")
        print("==================================================")
        print(f"Decision:  {final.decision}")
        print(f"Amount:    ₹{final.approved_amount}")
        print(f"Confidence:{final.confidence_score}")
        print(f"Notes:     {final.notes}")

        # Determine Pass/Fail based on the math
        if final.decision == "APPROVED" and float(final.approved_amount) == 3240.0:
            print("\n🌟 TEST PASSED: The Adjudicator nailed the complex math!")
        else:
            print("\n❌ TEST FAILED: The Adjudicator math or decision does not match expected output.")

    except Exception as e:
        print(f"\n🚨 System Crash: {e}")

if __name__ == "__main__":
    asyncio.run(run_single_test())