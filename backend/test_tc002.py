import asyncio
from models.claims import ClaimInput
from agents.workflow import app as claim_workflow

async def run_tc002_test():
    print("--- 🔬 Testing TC002: Unreadable Document Handling ---\n")

    # 1. Payload representing a good prescription but a completely unreadable bill
    test_case_data = {
        "member_id": "EMP004",
        "policy_id": "PLUM_GHI_2024",
        "claim_category": "PHARMACY",
        "treatment_date": "2024-10-25",
        "claimed_amount": 800,
        "documents": [
            {
                "file_id": "F003",
                "file_name": "prescription.jpg",
                "actual_type": "PRESCRIPTION",
                "quality": "GOOD"
            },
            {
                "file_id": "F004",
                "file_name": "blurry_bill.jpg",
                "actual_type": "PHARMACY_BILL",
                "quality": "UNREADABLE"
            }
        ]
    }

    try:
        payload = ClaimInput(**test_case_data)
        result = await claim_workflow.ainvoke({"claim_input": payload})

        final = result['final_decision']

        # 2. Print Comparative Output
        print("✅ Pipeline Execution Complete!\n")
        print("==================================================")
        print("🎯 EXPECTED OUTCOME")
        print("==================================================")
        print("Decision:  None / PENDING / RE-UPLOAD_REQUESTED (Should not be REJECTED)")
        print("System Must: Identify 'blurry_bill.jpg' as unreadable and request a re-upload.")

        print("\n==================================================")
        print("🤖 ACTUAL SYSTEM OUTCOME")
        print("==================================================")
        print(f"Decision:  {final.decision}")
        print(f"Amount:    ₹{final.approved_amount}")
        print(f"Confidence:{final.confidence_score}")
        print(f"Notes:     {final.notes}")

        # Validation Check
        # Ensure it doesn't blindly reject, and ensures it calls out the unreadable file
        is_rejected = final.decision == "REJECTED"
        mentions_blurry = "blurry_bill.jpg" in final.notes or "unreadable" in final.notes.lower()

        if not is_rejected and mentions_blurry:
            print("\n🌟 TEST PASSED: System gracefully handled the unreadable document without rejecting the claim!")
        elif is_rejected:
            print("\n❌ TEST FAILED: System rejected the claim outright. It should flag for re-upload instead.")
        else:
            print("\n❌ TEST FAILED: System failed to clearly identify the unreadable document in the notes.")

    except Exception as e:
        print(f"\n🚨 System Crash: {e}")

if __name__ == "__main__":
    asyncio.run(run_tc002_test())