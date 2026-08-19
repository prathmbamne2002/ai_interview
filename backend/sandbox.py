import subprocess
import tempfile
import os
import time
import requests
import json

PISTON_URL = "https://emkc.org/api/v2/piston/execute"

LANGUAGE_CONFIG = {
    "python": {
        "piston_lang": "python",
        "piston_version": "3.10.0",
        "file_ext": ".py"
    },
    "cpp": {
        "piston_lang": "cpp",
        "piston_version": "10.2.0",
        "file_ext": ".cpp"
    },
    "java": {
        "piston_lang": "java",
        "piston_version": "15.0.2",
        "file_ext": ".java"
    }
}

def execute_code_piston(language: str, code: str, stdin: str = "", timeout_ms: int = 3000) -> dict:
    """Executes code via the free Piston API."""
    cfg = LANGUAGE_CONFIG.get(language, LANGUAGE_CONFIG["python"])
    
    payload = {
        "language": cfg["piston_lang"],
        "version": cfg["piston_version"],
        "files": [{"content": code}],
        "stdin": stdin,
        "run_timeout": timeout_ms
    }
    
    try:
        start_time = time.time()
        res = requests.post(PISTON_URL, json=payload, timeout=5)
        elapsed_ms = int((time.time() - start_time) * 1000)
        
        if res.status_code == 200:
            data = res.json()
            run_data = data.get("run", {})
            return {
                "success": run_data.get("code", 0) == 0,
                "stdout": run_data.get("stdout", "").strip(),
                "stderr": run_data.get("stderr", "").strip(),
                "output": run_data.get("output", "").strip(),
                "exit_code": run_data.get("code", 0),
                "execution_time_ms": elapsed_ms,
                "source": "piston"
            }
    except Exception as e:
        print(f"Piston API execution failed, falling back to local runner: {e}")
        
    return execute_code_local(language, code, stdin)

def execute_code_local(language: str, code: str, stdin: str = "") -> dict:
    """Fallback local subprocess execution."""
    cfg = LANGUAGE_CONFIG.get(language, LANGUAGE_CONFIG["python"])
    start_time = time.time()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        filename = "Solution" + cfg["file_ext"] if language == "java" else "main" + cfg["file_ext"]
        filepath = os.path.join(tmpdir, filename)
        
        with open(filepath, "w") as f:
            f.write(code)
            
        try:
            if language == "python":
                proc = subprocess.run(
                    ["python3", filepath],
                    input=stdin,
                    text=True,
                    capture_output=True,
                    timeout=3
                )
            elif language == "cpp":
                bin_path = os.path.join(tmpdir, "out")
                compile_proc = subprocess.run(
                    ["g++", "-std=c++17", filepath, "-o", bin_path],
                    capture_output=True,
                    text=True,
                    timeout=3
                )
                if compile_proc.returncode != 0:
                    return {
                        "success": False,
                        "stdout": "",
                        "stderr": compile_proc.stderr,
                        "output": compile_proc.stderr,
                        "exit_code": compile_proc.returncode,
                        "execution_time_ms": int((time.time() - start_time) * 1000),
                        "source": "local"
                    }
                proc = subprocess.run(
                    [bin_path],
                    input=stdin,
                    text=True,
                    capture_output=True,
                    timeout=3
                )
            elif language == "java":
                compile_proc = subprocess.run(
                    ["javac", filepath],
                    capture_output=True,
                    text=True,
                    timeout=3
                )
                if compile_proc.returncode != 0:
                    return {
                        "success": False,
                        "stdout": "",
                        "stderr": compile_proc.stderr,
                        "output": compile_proc.stderr,
                        "exit_code": compile_proc.returncode,
                        "execution_time_ms": int((time.time() - start_time) * 1000),
                        "source": "local"
                    }
                proc = subprocess.run(
                    ["java", "-cp", tmpdir, "Solution"],
                    input=stdin,
                    text=True,
                    capture_output=True,
                    timeout=3
                )
            else:
                return {"success": False, "stderr": f"Unsupported language: {language}"}
                
            elapsed_ms = int((time.time() - start_time) * 1000)
            return {
                "success": proc.returncode == 0,
                "stdout": proc.stdout.strip(),
                "stderr": proc.stderr.strip(),
                "output": (proc.stdout + proc.stderr).strip(),
                "exit_code": proc.returncode,
                "execution_time_ms": elapsed_ms,
                "source": "local"
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": "Execution timed out (Time Limit Exceeded - 3.0s)",
                "output": "Time Limit Exceeded",
                "exit_code": -1,
                "execution_time_ms": 3000,
                "source": "local"
            }
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "output": str(e),
                "exit_code": -1,
                "execution_time_ms": int((time.time() - start_time) * 1000),
                "source": "local"
            }

def build_test_runner_code(language: str, user_code: str, test_case: dict, problem_id: str) -> str:
    """Wraps user code with a test harness for test case execution."""
    raw_input = test_case.get("input", "")
    
    if language == "python":
        if problem_id == "two_sum":
            return f"""{user_code}

import json

try:
    data = json.loads('''{raw_input}''')
    sol = Solution()
    res = sol.twoSum(data['nums'], data['target'])
    print(json.dumps(res))
except Exception as e:
    print(f"Error: {{e}}")
"""
        elif problem_id == "merge_intervals":
            return f"""{user_code}

import json

try:
    data = json.loads('''{raw_input}''')
    sol = Solution()
    res = sol.merge(data['intervals'])
    print(json.dumps(res))
except Exception as e:
    print(f"Error: {{e}}")
"""
        elif problem_id == "longest_substring":
            return f"""{user_code}

import json

try:
    data = json.loads('''{raw_input}''')
    sol = Solution()
    res = sol.lengthOfLongestSubstring(data['s'])
    print(json.dumps(res))
except Exception as e:
    print(f"Error: {{e}}")
"""
        elif problem_id == "stable_subarrays":
            return f"""{user_code}

import json

try:
    data = json.loads('''{raw_input}''')
    sol = Solution()
    res = sol.countStableSubarrays(data['capacity'])
    print(json.dumps(res))
except Exception as e:
    print(f"Error: {{e}}")
"""
        else:
            return f"""{user_code}
# Generic execution
print("Executed successfully")
"""
    return user_code

def evaluate_test_cases(language: str, user_code: str, test_cases: list, problem_id: str) -> dict:
    """Runs and verifies multiple test cases."""
    results = []
    total_passed = 0
    
    for idx, tc in enumerate(test_cases):
        test_code = build_test_runner_code(language, user_code, tc, problem_id)
        exec_res = execute_code_piston(language, test_code, stdin=tc.get("stdin", ""))
        
        actual_output = exec_res["stdout"].strip()
        expected_output = str(tc.get("expected_output", "")).strip()
        
        # Normalize JSON strings for comparison if possible
        passed = False
        try:
            passed = json.loads(actual_output) == json.loads(expected_output)
        except Exception:
            passed = actual_output == expected_output
            
        if passed:
            total_passed += 1
            
        results.append({
            "test_id": idx + 1,
            "name": tc.get("name", f"Test Case {idx + 1}"),
            "input": tc.get("input_display", tc.get("input", "")),
            "expected_output": expected_output,
            "actual_output": actual_output if exec_res["success"] else (exec_res["stderr"] or "Runtime Error"),
            "passed": passed,
            "execution_time_ms": exec_res["execution_time_ms"],
            "error": exec_res["stderr"] if not exec_res["success"] else None
        })
        
    return {
        "total_tests": len(test_cases),
        "total_passed": total_passed,
        "all_passed": total_passed == len(test_cases) and len(test_cases) > 0,
        "results": results
    }
