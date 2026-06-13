import json
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

from models.claims import ClaimInput, ExtractedMedicalData, FinalDecision

load_dotenv()

# We use Flash again for lightning-fast rule processing
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.0, # Zero creativity, strict adherence to rules
    max_retries=2
)

adjudicator_agent = llm.with_structured_output(FinalDecision)

def load_policy_terms():
    with open("data/policy_terms.json", "r") as f:
        return json.load(f)

async def adjudicate_claim(claim: ClaimInput, extracted_data: ExtractedMedicalData) -> FinalDecision:
    """
    Agent 3: Adjudicator
    Evaluates extracted data against policy terms to make a final decision.
    """

    # 1. Graceful Degradation Check (Requirement #6)
    # If the extraction agent flagged the document as completely unreadable,
    # we bypass the AI and immediately route to a human.
    if extracted_data.extraction_confidence < 0.30:
        return FinalDecision(
            claim_id=f"CLM-{claim.member_id}",
            decision="MANUAL_REVIEW",
            approved_amount=0.0,
            rejection_reasons=["LOW_EXTRACTION_CONFIDENCE"],
            notes="Routed to manual review. Documents were too blurry or messy to extract data reliably.",
            confidence_score=1.0,
            routing_flag="UNREADABLE_DOCUMENTS"
        )

    # 2. Load policy and find the specific member
    policy = load_policy_terms()
    member = next((m for m in policy["members"] if m["member_id"] == claim.member_id), None)

    # 3. Build the highly specific prompt
    prompt_text = f"""
    You are the Lead Adjudication Agent for Plum Health Insurance.
    Your job is to make a final claim decision based on the extracted medical data and the strict policy terms.

    --- MEMBER DATA ---
    {json.dumps(member)}

    --- CLAIM INPUT (What the user submitted) ---
    Category: {claim.claim_category}
    Claimed Amount: {claim.claimed_amount}
    Treatment Date: {claim.treatment_date}
    Hospital Name: {claim.hospital_name}

    --- EXTRACTED MEDICAL DATA (From AI Extraction) ---
    {extracted_data.model_dump_json()}

    --- POLICY RULES ---
    General Limits: {json.dumps(policy['coverage'])}
    Category Rules: {json.dumps(policy['opd_categories'].get(claim.claim_category.lower(), {}))}
    Waiting Periods: {json.dumps(policy['waiting_periods'])}
    Exclusions: {json.dumps(policy['exclusions'])}
    Network Hospitals: {json.dumps(policy['network_hospitals'])}

    --- INSTRUCTIONS ---
    1. Compare the patient name on the documents to the member's name. If they do not match, REJECT.
    2. Check the treatment date against 'waiting_periods'. If not met, REJECT.
    3. Look at the 'line_items'. Remove any that are 'is_cosmetic_or_excluded' or match the policy exclusions.
    4. Calculate the financial payout.
       - FIRST: Apply the 'network_discount_percent' if the hospital is in the 'network_hospitals' list.
       - SECOND: Apply the 'copay_percent' to the remaining amount.
       - THIRD: Cap the final amount at the specific category 'sub_limit'.

    DECISION LOGIC:
    - APPROVED: Fully valid, payout calculated.
    - PARTIAL: Valid, but some line items excluded or sub-limits reached.
    - REJECTED: Policy violation, waiting period, or explicit exclusion.

    EXPLAINABILITY REQUIREMENT (CRITICAL):
    Your 'notes' field MUST be a human-readable trace explaining exactly how you arrived at the decision.
    If you calculated math, show the step-by-step math (e.g., "Total: $100 -> 20% Network Discount = $80 -> 10% Copay = $72").
    """

    message = HumanMessage(content=[{"type": "text", "text": prompt_text}])

    print("Agent 3 (Adjudicator): Evaluating rules and calculating payouts...")
    result = await adjudicator_agent.ainvoke([message])

    # Ensure claim ID is populated
    result.claim_id = f"CLM-{claim.member_id}"

    return result