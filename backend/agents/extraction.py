import base64
from typing import List
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_vertexai import ChatVertexAI
from langchain_core.messages import HumanMessage

# Importing our strict contracts
from models.claims import ExtractedMedicalData, DocumentUpload

load_dotenv()

# We use Gemini 2.5-flash here specifically because its massive context window
# and native multimodal capabilities are best-in-class for messy handwriting.
llm = ChatVertexAI(
    model_name="gemini-2.5-flash", # Note: LangChain uses 'model_name' here instead of 'model'
    project="juman-gen-ai-project", # ⚠️ Replace with your actual GCP Project ID
    location="us-central1",              # ⚠️ Ensure this matches your project location
    temperature=0.0,
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
    You are an expert Indian medical claims data extraction AI.
    Your job is to read unstructured, messy medical documents (handwritten prescriptions, phone photos of bills, rubber-stamped invoices) and extract data into a strict JSON format.

    --- INDIAN MEDICAL CONTEXT & RULES ---
    1. Doctor Registration: Extract the doctor's registration number. Note that Indian formats vary by state (e.g., KA/XXXXX/YYYY, MH/XXXXX/YYYY, DL/XXXXX/YYYY, AYUR/KL/XXXXX).
    2. Diagnosis Shorthand: Expand common Indian medical shorthand.
       - HTN -> Hypertension
       - T2DM -> Type 2 Diabetes Mellitus
       - URI -> Upper Respiratory Infection

    --- HANDLING DOCUMENT QUALITY VARIATIONS ---
    1. Multilingual Text: If you detect Hindi, Tamil, Telugu, or other regional languages mixed with English, extract the English fields as best as possible and set 'regional_language_detected' to True.
    2. Obscured Text (Rubber Stamps/Shadows): If a stamp covers an amount or registration number, do your best to extract it but REDUCE the 'extraction_confidence' score. Do not fail the whole document.
    3. Document Alterations: If you see amounts crossed out and rewritten by hand, add "DOCUMENT_ALTERATION" to the 'fraud_flags' list.
    4. Duplicate Stamps: If you see stamps stating "DUPLICATE" or "COPY", add "DUPLICATE_STAMP" to the 'fraud_flags' list.
    5. Patient Name Mismatch: Look for the patient name on EVERY document page. Return a list of all unique names found to help downstream agents catch mismatched documents.

    Extract the data meticulously.
    """

    message_content = [{"type": "text", "text": prompt_text}]

    # THE FIX: Safely pull the image from either the UI base64 data OR the local test path
    for doc in documents:
        try:
            base_img = None
            if doc.base64_data:
                base_img = doc.base64_data
            elif doc.content_path:
                base_img = encode_image(doc.content_path)

            if not base_img:
                continue

            # Strip the HTML data URI prefix sent by the browser
            if "base64," in base_img:
                base_img = base_img.split("base64,")[1]

            message_content.append({"type": "text", "text": f"--- Document: {doc.file_name} ---"})
            message_content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{base_img}"}
            })
        except Exception as e:
            print(f"Warning: Could not load image {doc.file_name}: {e}")

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