import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import your Pydantic schemas and the compiled LangGraph workflow
from models.claims import ClaimInput
from agents.workflow import app as claim_workflow

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

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)