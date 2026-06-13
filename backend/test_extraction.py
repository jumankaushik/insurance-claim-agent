import asyncio
from agents.extraction import extract_medical_data
from models.claims import DocumentUpload

async def run_extraction_test():
    print("--- Testing Agent 2: Extraction ---")

    # We are going to pass the dummy image you already have.
    # To really see the power of this agent later, you can replace dummy_doc.jpg
    # with a downloaded picture of a real, messy hospital bill.
    docs_to_process = [
        DocumentUpload(file_id="F001", file_name="bill.jpg", content_path="data/dummy_doc.jpg")
    ]

    try:
        # Run the extraction agent
        result = await extract_medical_data(docs_to_process)

        print("\n✅ Extraction Agent Execution Complete!")
        print(result.model_dump_json(indent=2))

    except Exception as e:
        print(f"\n❌ Error during extraction: {e}")

if __name__ == "__main__":
    asyncio.run(run_extraction_test())