import asyncio
from models.claims import DocumentUpload
from agents.triage import verify_documents

async def run_triage_test():
    print("--- 🛡️ Testing Agent 1: Triage ONLY ---")

    # 1. Define what the policy requires for this test
    claim_category = "CONSULTATION"
    required_docs = ["PRESCRIPTION", "HOSPITAL_BILL"]

    # 2. Mock the documents the user uploaded (using local paths)
    docs_to_process = [
        DocumentUpload(
            file_id="DOC_001",
            file_name="rx.jpg",
            content_path="data/mock_prescription_v2.jpg" # Make sure this file exists!
        ),
        DocumentUpload(
            file_id="DOC_002",
            file_name="bill.jpg",
            content_path="data/mock_hospital_bill_v2.jpg" # Make sure this file exists!
        )
    ]

    try:
        # 3. Call the Triage Agent directly, bypassing the rest of the graph
        result = await verify_documents(claim_category, required_docs, docs_to_process)

        print("\n✅ Triage Agent Execution Complete!")
        print(result.model_dump_json(indent=2))

    except Exception as e:
        print(f"\n❌ Error during triage: {e}")

if __name__ == "__main__":
    asyncio.run(run_triage_test())