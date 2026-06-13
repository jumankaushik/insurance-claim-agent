import base64
from typing import List
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

# Importing our strict contracts
from models.claims import ExtractedMedicalData, DocumentUpload

load_dotenv()

# We use Gemini 2.5-flash here specifically because its massive context window
# and native multimodal capabilities are best-in-class for messy handwriting.
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.0, # Zero creativity, maximum precision
    max_retries=2
)

extraction_agent = llm.with_structured_output(ExtractedMedicalData)

def encode_image(image_path: str) -> str:
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

async def extract_medical_data(documents: List[DocumentUpload]) -> ExtractedMedicalData:
    """
    Agent 2: Extraction
    Reads validated medical documents and extracts structured JSON data.
    """

    prompt_text = """
    You are an expert medical claims data extraction agent.
    Your job is to read the provided medical documents (prescriptions, hospital bills, etc.)
    and extract the information into a strict, structured JSON format.

    INSTRUCTIONS & RULES:
    1. Patient Names: Look for the patient name on EVERY document. Return a list of all unique names found. This is critical for catching mismatched documents.
    2. Line Items: Extract every individual charge from the bills.
       - If a line item appears to be for a cosmetic procedure (e.g., teeth whitening), experimental treatment, or something typically excluded by standard policies, set 'is_cosmetic_or_excluded' to True.
    3. Total Billed: Calculate or extract the grand total billed across all documents.
    4. Readability & Confidence:
       - If a specific document is completely unreadable or extremely blurry, add its file_name to the 'unreadable_documents' list.
       - Assign an 'extraction_confidence' score (0.0 to 1.0). Lower this score if handwriting is messy, parts are cut off, or text is obscured by stamps.

    Extract the data accurately despite messy handwriting, rubber stamps, or poor lighting.
    """

    message_content = [{"type": "text", "text": prompt_text}]

    # Attach images, but also tell the LLM which file is which so it can populate 'unreadable_documents' accurately
    for doc in documents:
        if doc.content_path:
            try:
                base64_image = encode_image(doc.content_path)
                message_content.append({"type": "text", "text": f"--- Document: {doc.file_name} ---"})
                message_content.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                })
            except Exception as e:
                print(f"Warning: Could not load image {doc.content_path}: {e}")

    message = HumanMessage(content=message_content)

    print("Agent 2 (Extraction): Mining data from documents...")
    try:
        result = await extraction_agent.ainvoke([message])
        return result

    except Exception as e:
        # GRACEFUL DEGRADATION (TC011 Requirement)
        # If the LangChain call fails, times out, or crashes, we DO NOT crash the app.
        # We return a "degraded" state that the downstream Adjudicator agent will interpret as a failure requiring manual review.
        print(f"Extraction Pipeline Failure Caught: {e}")
        return ExtractedMedicalData(
            patient_name_on_documents=[],
            extraction_confidence=0.1,
            unreadable_documents=[doc.file_name for doc in documents]
        )