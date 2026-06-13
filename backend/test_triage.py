import asyncio
import json
from agents.triage import verify_documents

async def run_triage_test():
    print("--- Testing Agent 1: Triage (TC001 Simulation) ---")

    # We are simulating a 'CONSULTATION' claim.
    # The policy says this requires a PRESCRIPTION and a HOSPITAL_BILL.
    category = "CONSULTATION"
    required_docs = ["PRESCRIPTION", "HOSPITAL_BILL"]

    # Point this to the dummy image you just saved
    # We are passing the same image twice to simulate the user uploading two of the same wrong documents
    uploaded_images = [
        "data/dummy_doc.jpg",
        "data/dummy_doc.jpg"
    ]

    try:
        # Call the agent
        result = await verify_documents(
            claim_category=category,
            required_doc_types=required_docs,
            image_paths=uploaded_images
        )

        # Print the structured Pydantic output
        print("\n✅ Triage Agent Execution Complete!")
        print(result.model_dump_json(indent=2))

    except Exception as e:
        print(f"\n❌ Error connecting to Gemini: {e}")

if __name__ == "__main__":
    # Because our agent uses async/await, we run it via asyncio
    asyncio.run(run_triage_test())