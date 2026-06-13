import os
import base64
from typing import List
from dotenv import load_dotenv

# LangChain imports
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

# Our strict Pydantic contract
from models.claims import DocumentVerification, DocumentUpload

# Load environment variables (API Key)
load_dotenv()

# Initialize the Gemini 1.5 Pro model
# We set temperature to 0.0 because we want highly deterministic categorization, not creative writing.
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.0,
    max_retries=2
)

# Bind our Pydantic model to the LLM.
# This forces Gemini to output a valid DocumentVerification JSON object.
triage_agent = llm.with_structured_output(DocumentVerification)

def encode_image(image_path: str) -> str:
    """Helper function to convert local image to base64 for LangChain."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

async def verify_documents(
    claim_category: str,
    required_doc_types: List[str],
    documents: List[DocumentUpload]
) -> DocumentVerification:
    """
    Agent 1: Triage
    Analyzes uploaded images to ensure they match the required document types.
    """

    # 1. Prepare the precise instruction prompt based on the policy rules
    prompt_text = f"""
    You are the Intake & Triage Agent for a health insurance claims system.
    The user is submitting a '{claim_category}' claim.

    According to the policy, this claim type REQUIRES the following documents: {required_doc_types}.

    Look carefully at the uploaded documents and determine:
    1. What is the actual document type of each image? (e.g., PRESCRIPTION, HOSPITAL_BILL, LAB_REPORT, PHARMACY_BILL)
    2. Are ALL the required document types present?

    CRITICAL INSTRUCTION:
    If a wrong document was uploaded (for example, the user uploaded two prescriptions instead of a prescription and a hospital bill),
    you must set 'is_valid' to False and write a highly specific, actionable 'error_message'.

    Do NOT use generic errors. The message MUST explicitly name the wrong document type the user uploaded,
    and clearly state the exact document type they are missing and need to provide.
    """

    # 2. Build the multimodal message payload
    message_content = [{"type": "text", "text": prompt_text}]

    # Attach all uploaded images to the same message
    # Attach all uploaded images to the same message
    for doc in documents:
        # Pull base64 if it came from the UI, otherwise encode the local file path
        base64_image = doc.base64_data if doc.base64_data else encode_image(doc.content_path)

        # Clean the string if it came from the browser
        if "base64," in base64_image:
            base64_image = base64_image.split("base64,")[1]

        message_content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
        })

    message = HumanMessage(content=message_content)

    # 3. Invoke Gemini and automatically parse the response into our Pydantic class
    print("Agent 1 (Triage): Analyzing documents...")
    result = await triage_agent.ainvoke([message])

    return result