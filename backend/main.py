import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import your Pydantic schemas and the compiled LangGraph workflow
from models.claims import ClaimInput
from agents.workflow import app as claim_workflow

import time
# In-memory database to hold claims submitted from the UI
live_manual_claims = []

# Initialize the FastAPI application
app = FastAPI(title="Plum AI Claims Adjudicator", version="1.0.0")

# Enable CORS so your Next.js frontend running on localhost:3000 can talk to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For production, lock this down to your Vercel/frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health_check():
    return {"status": "online", "message": "Plum Claims Multi-Agent Pipeline is ready."}

@app.post("/api/process-claim")
async def process_claim_endpoint(claim: ClaimInput):
    """
    Receives the claim from the Next.js UI, feeds it into the LangGraph state machine,
    and returns the final decision alongside the full agent trace for observability.
    """
    try:
        print(f"\n🚀 --- New Claim Received: {claim.member_id} ---")

        # 1. Feed the data into the LangGraph state machine
        initial_state = {"claim_input": claim}
        final_state = await claim_workflow.ainvoke(initial_state)

        # 2. Extract the final decision
        if "final_decision" in final_state and final_state["final_decision"] is not None:
            decision = final_state["final_decision"]

            # --- NEW: Save live UI tests to the Admin Queue ---
            live_manual_claims.insert(0, {
                "case_id": f"LIVE-{claim.member_id}-{int(time.time())}",
                "description": f"Live UI Submission - {claim.claim_category} at {claim.hospital_name}",
                "actual": decision.decision,
                "trace": decision.notes,
                "is_manual": True
            })

            # 3. Package the final decision WITH the full trace for the UI
            return {
                "status": "success",
                "final_decision": decision.model_dump(),
                "agent_trace": {
                    "triage": final_state.get("triage_result").model_dump() if final_state.get("triage_result") else None,
                    "extraction": final_state.get("extracted_data").model_dump() if final_state.get("extracted_data") else None
                }
            }
        else:
            raise HTTPException(status_code=500, detail="Graph executed but no final decision was produced.")

    except Exception as e:
        print(f"❌ API Error: {str(e)}")
        # If the graph completely crashes, return a 500
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/test-cases")
def get_test_cases():
    import os
    import json

    ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    TEST_CASES_PATH = os.path.join(ROOT_DIR, "data", "test_cases.json")

    with open(TEST_CASES_PATH, "r") as f:
        data = json.load(f)
        # Ensure we always return the list of cases, regardless of JSON shape
        if isinstance(data, dict) and "test_cases" in data:
            return data["test_cases"]
        return list(data.values()) if isinstance(data, dict) else data

@app.get("/api/eval-results")
def get_eval_results():
    import os
    import json
    from fastapi import HTTPException

    # Backtrack exactly once to point to the 'backend/' directory
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    RESULTS_PATH = os.path.join(ROOT_DIR, "eval_results.json")

    if not os.path.exists(RESULTS_PATH):
        raise HTTPException(status_code=404, detail="Evaluation results not found. Run evaluate.py first.")

    with open(RESULTS_PATH, "r") as f:
        return json.load(f)

# Import the run_eval function from your evaluate script

import asyncio
from evaluate import run_eval, EVAL_STATE

@app.post("/api/run-evaluations")
async def trigger_evaluations():
    try:
        # Trigger the LangGraph evaluation script in the background without blocking the API
        asyncio.create_task(run_eval())
        return {"status": "success", "message": "Evaluation sequence started in the background."}
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")

from pydantic import BaseModel

class AdminOverride(BaseModel):
    decision: str
    admin_notes: str

@app.put("/api/admin/claims/{case_id}/override")
async def override_claim_decision(case_id: str, payload: AdminOverride):
    """
    Simulates an Admin manually overriding a claim decision.
    In a production system, this would update the claims database and trigger an email to the member.
    """
    # For the assignment demo, we just print to the server console and return success.
    print(f"👮 ADMIN OVERRIDE on {case_id}: Changed to {payload.decision}. Reason: {payload.admin_notes}")

    return {
        "status": "success",
        "message": f"Claim {case_id} successfully updated to {payload.decision}.",
        "updated_decision": payload.decision
    }

@app.get("/api/admin/claims")
def get_admin_queue():
    import json
    import os
    eval_data = []
    try:
        # Load the automated 12 test cases
        ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
        EVAL_PATH = os.path.join(ROOT_DIR, "eval_results.json")
        with open(EVAL_PATH, "r") as f:
            eval_data = json.load(f)
    except Exception:
        pass

    # Return the live UI claims FIRST, followed by the automated eval cases
    return live_manual_claims + eval_data

@app.get("/api/eval-status")
def get_eval_status():
    """Exposes the internal live run state of the evaluation suite."""
    return EVAL_STATE

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)