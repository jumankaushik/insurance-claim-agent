import os
import json
import asyncio
from agents.workflow import app as claim_workflow
from models.claims import ClaimInput

# --- Dynamic Path Setup ---
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEST_CASES_PATH = os.path.join(ROOT_DIR, "data", "test_cases.json")
RESULTS_PATH = os.path.join(ROOT_DIR, "data", "eval_results.json")

async def run_eval():
    if not os.path.exists(TEST_CASES_PATH):
        print(f"❌ Error: Cannot find {TEST_CASES_PATH}")
        return

    with open(TEST_CASES_PATH, 'r') as f:
        raw_cases = json.load(f)

    # --- THE FIX: Flatten the JSON into a list ---
    if isinstance(raw_cases, dict):
        if "test_cases" in raw_cases:
            cases = raw_cases["test_cases"] # Handles {"test_cases": [...]}
        else:
            cases = list(raw_cases.values()) # Handles {"TC001": {...}, "TC002": {...}}
    else:
        cases = raw_cases

    results = []
    print(f"🚀 Starting evaluation of {len(cases)} test cases...\n")

    for i, case in enumerate(cases):
        print(f"Running Case {i+1}: {case['description']}...")

        try:
            payload = ClaimInput(**case['input'])
            result = await claim_workflow.ainvoke({"claim_input": payload})

            actual_decision = result['final_decision'].decision
            expected_decision = case['expected_output']['decision']
            passed = actual_decision == expected_decision
            trace = result['final_decision'].notes

        except Exception as e:
            passed = False
            actual_decision = "ERROR"
            expected_decision = case.get('expected_output', {}).get('decision', 'UNKNOWN')
            trace = f"System Error: {str(e)}"

        results.append({
            "case_id": i + 1,
            "description": case.get('description', 'Unknown Case'),
            "passed": passed,
            "actual": actual_decision,
            "expected": expected_decision,
            "trace": trace
        })

        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  Result: {status} (Expected: {expected_decision}, Got: {actual_decision})\n")

        # --- THE FIX: Add a 5-second pause to respect the free tier rate limit ---
        print("  [Rate Limit Buffer] Pausing for 5 seconds...")
        await asyncio.sleep(5)

        
    # Save results to the data folder
    with open(RESULTS_PATH, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"✅ Evaluation complete. Results saved to {RESULTS_PATH}")

if __name__ == "__main__":
    asyncio.run(run_eval())