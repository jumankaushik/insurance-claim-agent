import json
import os
import asyncio
from models.claims import ClaimInput
from agents.workflow import app as claim_workflow

# --- NEW: Shared memory tracking variable ---
EVAL_STATE = {"is_running": False}

async def run_eval():
    global EVAL_STATE
    EVAL_STATE["is_running"] = True # Set to True immediately when triggered
    print("Starting evaluation of 12 test cases...\n")

    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    TEST_CASES_PATH = os.path.join(ROOT_DIR, "..", "data", "test_cases.json")
    RESULTS_PATH = os.path.join(ROOT_DIR, "eval_results.json")

    try:
        with open(TEST_CASES_PATH, "r") as f:
            data = json.load(f)
            cases = data.get("test_cases", [])

        results = []

        for i, case in enumerate(cases):
            print(f"Running Case {i+1}: {case['description']}...")
            expected_block = case.get('expected', {})
            expected_decision = expected_block.get('decision')

            try:
                payload = ClaimInput(**case['input'])
                result = await claim_workflow.ainvoke({"claim_input": payload})

                final = result['final_decision']
                actual_decision = final.decision
                trace = final.notes

                if expected_decision is None:
                    passed = actual_decision in ["REJECTED", "MANUAL_REVIEW", "PENDING"]
                    expected_str = "REJECTED / MANUAL_REVIEW"
                else:
                    passed = actual_decision == expected_decision
                    expected_str = expected_decision

            except Exception as e:
                passed = False
                actual_decision = "ERROR"
                expected_str = expected_decision if expected_decision else "REJECTED / MANUAL_REVIEW"
                trace = f"System Error: {str(e)}"

            results.append({
                "case_id": case.get("case_id", f"TC{i+1:03d}"),
                "description": case.get('description', 'Unknown Case'),
                "passed": passed,
                "actual": actual_decision,
                "expected": expected_str,
                "trace": trace
            })

            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"  Result: {status} (Expected: {expected_str}, Got: {actual_decision})\n")
            await asyncio.sleep(2)

        with open(RESULTS_PATH, "w") as f:
            json.dump(results, f, indent=2)

        print("\n✅ All test cases evaluated. Results saved to eval_results.json")

    finally:
        # --- NEW: Guarantees status resets to False when done ---
        EVAL_STATE["is_running"] = False