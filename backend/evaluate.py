import json
import os
import asyncio
from models.claims import ClaimInput
from agents.workflow import app as claim_workflow

async def run_eval():
    print("Starting evaluation of 12 test cases...\n")

    # 1. Setup paths
    # 2. Setup paths - adjust backtracking if 'data' is at the project root
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    TEST_CASES_PATH = os.path.join(ROOT_DIR, "..", "data", "test_cases.json") # <-- ADDED ".." TO BACKTRACK
    RESULTS_PATH = os.path.join(ROOT_DIR, "eval_results.json")

    # 2. Load the test cases
    try:
        with open(TEST_CASES_PATH, "r") as f:
            data = json.load(f)
            cases = data.get("test_cases", [])
    except Exception as e:
        print(f"Error loading test_cases.json: {e}")
        return

    results = []

    # 3. Process each case
    for i, case in enumerate(cases):
        print(f"Running Case {i+1}: {case['description']}...")

        # THE FIX: Correctly read the 'expected' block
        expected_block = case.get('expected', {})
        expected_decision = expected_block.get('decision')

        try:
            # Run the agent pipeline
            payload = ClaimInput(**case['input'])
            result = await claim_workflow.ainvoke({"claim_input": payload})

            final = result['final_decision']
            actual_decision = final.decision
            trace = final.notes

            # THE FIX: Handle JSON 'null' decisions (TC001, TC002, TC003 want early stops)
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

        # 4. Save the detailed results
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

        # 5 second buffer to respect the Google Free Tier Rate Limit
        print("  [Rate Limit Buffer] Pausing for 5 seconds...")
        await asyncio.sleep(5)

    # 5. Write the final results to the file for the frontend to read
    with open(RESULTS_PATH, "w") as f:
        json.dump(results, f, indent=2)

    print("\n✅ All test cases evaluated. Results saved to eval_results.json")

if __name__ == "__main__":
    asyncio.run(run_eval())