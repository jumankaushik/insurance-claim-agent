import asyncio
from agents.adjudicator import adjudicate_claim
from models.claims import ClaimInput, ExtractedMedicalData, LineItem

async def run_adjudicator_test():
    print("--- Testing Agent 3: Adjudicator (TC010 Simulation) ---")

    # 1. Mock what the UI sent
    ui_input = ClaimInput(
        member_id="EMP010", # Deepak Shah
        policy_id="PLUM_GHI_2024",
        claim_category="CONSULTATION",
        treatment_date="2024-11-03",
        claimed_amount=4500.0,
        hospital_name="Apollo Hospitals", # This is a Network Hospital!
        documents=[]
    )

    # 2. Mock what the Extraction Agent just found
    extracted = ExtractedMedicalData(
        patient_name_on_documents=["Deepak Shah"],
        doctor_name="Dr. S. Iyer",
        diagnosis="Acute Bronchitis",
        line_items=[
            LineItem(description="Consultation Fee", amount=1500.0),
            LineItem(description="Medicines", amount=3000.0)
        ],
        total_billed=4500.0,
        extraction_confidence=0.99
    )

    try:
        result = await adjudicate_claim(claim=ui_input, extracted_data=extracted)
        print("\n✅ Adjudicator Execution Complete!")
        print(result.model_dump_json(indent=2))
    except Exception as e:
        print(f"\n❌ Error during adjudication: {e}")

if __name__ == "__main__":
    asyncio.run(run_adjudicator_test())