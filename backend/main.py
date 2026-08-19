import os
import json
import random
import time
from fastapi import FastAPI, Form, HTTPException, WebSocket, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import motor.motor_asyncio
from google import genai
from google.genai import types

from sandbox import execute_code_piston, evaluate_test_cases
from problems_db import PROBLEMS, COMPANY_TRACKS, get_track_problems
from live_gateway import handle_live_interview_ws

load_dotenv()

app = FastAPI(title="AI Mock Interview Platform Backend")

# Allow CORS for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB setup
MONGODB_URI = os.getenv("MONGODB_URI")
if MONGODB_URI:
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URI)
    db = client.get_database("mockAiInterview")
    reports_collection = db.get_collection("reports")
else:
    print("Warning: MONGODB_URI not found. Reports will not be saved.")
    reports_collection = None

# Gemini setup
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai_client = genai.Client(api_key=GEMINI_API_KEY)
else:
    print("Warning: GEMINI_API_KEY not found. AI responses will fail.")
    genai_client = None

# In-memory storage for active sessions
sessions = {}

class InterviewSession:
    def __init__(self, session_id: str, track: str = "general", candidate_name: str = "Candidate", resume_summary: str = ""):
        self.session_id = session_id
        self.track = track
        self.candidate_name = candidate_name
        self.resume_summary = resume_summary
        self.current_phase = "Intro"
        self.active_problem_id = None
        
        q1, q2, track_cfg = get_track_problems(track)
        self.q1 = q1
        self.q2 = q2
        self.track_name = track_cfg["name"]
        
        self.history = [] # Stores {"role": "user"|"model", "content": text}
        self.q1_code = ""
        self.q2_code = ""
        self.test_stats = {"q1_passed": 0, "q1_total": 0, "q2_passed": 0, "q2_total": 0}
        self.start_time = time.time()

@app.get("/")
def read_root():
    return {"message": "AI Interview Backend is running", "live_api": True, "sandbox": True}

@app.get("/api/tracks")
def get_tracks():
    """Returns available company interview tracks."""
    return {
        "tracks": [
            {
                "id": k,
                "name": v["name"],
                "description": v["description"]
            }
            for k, v in COMPANY_TRACKS.items()
        ]
    }

@app.post("/api/setup-interview")
def setup_interview(
    session_id: str = Form(...),
    track: str = Form("general"),
    candidate_name: str = Form("Candidate"),
    resume_summary: str = Form("")
):
    """Initializes or resets a tailored interview session."""
    session = InterviewSession(
        session_id=session_id,
        track=track,
        candidate_name=candidate_name,
        resume_summary=resume_summary
    )
    sessions[session_id] = session
    
    return {
        "status": "success",
        "session_id": session_id,
        "track": track,
        "track_name": session.track_name,
        "q1_title": session.q1["title"],
        "q2_title": session.q2["title"]
    }

@app.post("/api/run-code")
def run_code(
    session_id: str = Form(...),
    language: str = Form("python"),
    code: str = Form(...),
    problem_id: str = Form(...)
):
    """Runs candidate code against visible sample test cases."""
    problem = PROBLEMS.get(problem_id)
    if not problem:
        # Fallback to direct execution
        return execute_code_piston(language, code)
        
    test_cases = problem.get("sample_test_cases", [])
    results = evaluate_test_cases(language, code, test_cases, problem_id)
    return results

@app.post("/api/submit-solution")
def submit_solution(
    session_id: str = Form(...),
    language: str = Form("python"),
    code: str = Form(...),
    problem_id: str = Form(...)
):
    """Runs candidate code against hidden test cases for evaluation."""
    session = sessions.get(session_id)
    problem = PROBLEMS.get(problem_id)
    if not problem:
        return {"error": "Problem not found"}
        
    all_tests = problem.get("sample_test_cases", []) + problem.get("hidden_test_cases", [])
    results = evaluate_test_cases(language, code, all_tests, problem_id)
    
    if session:
        if problem_id == session.q1["id"]:
            session.q1_code = code
            session.test_stats["q1_passed"] = results["total_passed"]
            session.test_stats["q1_total"] = results["total_tests"]
        elif problem_id == session.q2["id"]:
            session.q2_code = code
            session.test_stats["q2_passed"] = results["total_passed"]
            session.test_stats["q2_total"] = results["total_tests"]
            
    return results

def construct_system_prompt(session: InterviewSession, code: str, language: str, is_final: bool) -> str:
    """Builds the comprehensive system prompt for the 2-question interview."""
    if is_final:
        return f"""You are Sanjay, a Senior Technical Interviewer at a top tech company concluding the interview.
Track: {session.track_name}
Candidate Name: {session.candidate_name}
Candidate Language: {language}
Final Code in Editor:
```{language}
{code}
```

Test Cases Stats:
- Question 1 ({session.q1['title']}): {session.test_stats['q1_passed']}/{session.test_stats['q1_total']} passed
- Question 2 ({session.q2['title']}): {session.test_stats['q2_passed']}/{session.test_stats['q2_total']} passed

Evaluate their full interview performance across:
1. Problem Solving & Algorithmic Optimization (Score /100)
2. Code Quality, Syntax & Modularity (Score /100)
3. Communication, Complexity Analysis & Edge Cases (Score /100)
4. Final Hiring Recommendation (Strong Hire / Hire / Lean Hire / No Hire)

Output ONLY valid JSON:
{{
    "ai_response": "Detailed, encouraging performance evaluation summary...",
    "current_phase": "Wrap-up",
    "editor_unlocked": false,
    "problem_html": null,
    "starter_code": null,
    "scores": {{
        "problem_solving": 85,
        "code_quality": 80,
        "communication": 90,
        "overall": 85
    }},
    "recommendation": "Hire"
}}
"""

    active_problem = session.q2 if session.current_phase in ["Question 2", "Question 2 Follow-up"] else session.q1
    session.active_problem_id = active_problem["id"]

    return f"""You are Sanjay, an expert Senior Technical Interviewer conducting a realistic live DSA interview on the {session.track_name} track.
Candidate Name: {session.candidate_name}
Candidate Background / Resume: {session.resume_summary or 'Computer Science / Software Engineering'}

INTERVIEW TIMELINE:
1. Intro Phase: Greet candidate by name, ask 1 brief background question (e.g. favorite projects or experience). When answered, acknowledge and transition to "Question 1".
2. Question 1 ({session.q1['title']}): Present problem 1, ask candidate to explain their high-level approach before/while writing code. Unlock editor.
3. Question 1 Follow-up: Ask about Time & Space Complexity (Big-O) and edge cases. When answered, transition to "Question 2".
4. Question 2 ({session.q2['title']}): Present problem 2, guide candidate to solve it.
5. Question 2 Follow-up: Ask scaling, streaming, or optimization follow-up. When answered, transition to "Wrap-up".
6. Wrap-up: Conclude with encouraging high-level feedback.

CURRENT STATE:
- Phase: {session.current_phase}
- Language: {language}
- Editor Code:
```{language}
{code}
```

CONVERSATIONAL RULES:
- Speak naturally like a real human interviewer (1-3 sentences maximum per turn).
- Be supportive, clear, and focused.

OUTPUT SCHEMA (JSON ONLY):
{{
    "ai_response": "Spoken text for the candidate (1-3 sentences)",
    "current_phase": "Intro" | "Question 1" | "Question 1 Follow-up" | "Question 2" | "Question 2 Follow-up" | "Wrap-up",
    "editor_unlocked": true/false,
    "problem_id": "{session.q1['id']}" | "{session.q2['id']}" | null,
    "problem_html": "HTML if presenting Q1 or Q2, otherwise null",
    "starter_code": "Starter code if presenting Q1 or Q2, otherwise null"
}}
"""

@app.post("/api/submit")
def submit_text(
    session_id: str = Form(...),
    language: str = Form("python"),
    code: str = Form(""),
    transcription: str = Form(""),
    is_final: bool = Form(False)
):
    if not genai_client:
        raise HTTPException(status_code=500, detail="Gemini API key not configured")
        
    if session_id not in sessions:
        sessions[session_id] = InterviewSession(session_id)
        
    session = sessions[session_id]
    is_final_flag = is_final is True or str(is_final).lower() in ["true", "1"]
    
    # Handle initial vs ongoing user message
    user_message = transcription.strip()
    if not session.history and not user_message:
        user_message = f"Hi Sanjay, I am {session.candidate_name} and I am ready to start the interview."
        
    if user_message:
        session.history.append({"role": "user", "content": user_message})
    
    # Keep last 10 messages for low latency
    contents = []
    recent_history = session.history[-10:] if len(session.history) > 10 else session.history
    for msg in recent_history:
        contents.append(
            types.Content(
                role="user" if msg["role"] == "user" else "model", 
                parts=[types.Part.from_text(text=msg["content"])]
            )
        )
    
    system_prompt = construct_system_prompt(session, code, language, is_final_flag)
    
    models_to_try = ['gemini-3.1-flash-lite', 'gemini-3-flash-preview', 'gemini-3.5-flash']
    parsed_response = None
    spoken_response = ""
    
    for model_name in models_to_try:
        try:
            config = types.GenerateContentConfig(
                system_instruction=system_prompt,
                thinking_config=types.ThinkingConfig(thinking_budget=0),
                temperature=0.7,
                response_mime_type="application/json"
            )
            response = genai_client.models.generate_content(
                model=model_name,
                contents=contents,
                config=config
            )
            parsed_response = json.loads(response.text)
            spoken_response = parsed_response.get("ai_response", "Let's continue.")
            break
        except Exception as e:
            print(f"Model {model_name} error: {e}")
            continue
            
    if not parsed_response:
        spoken_response = "I had a momentary glitch. Could you please repeat that?"
        parsed_response = {
            "ai_response": spoken_response,
            "current_phase": session.current_phase,
            "editor_unlocked": session.current_phase not in ["Intro", "Wrap-up"],
            "problem_html": None,
            "starter_code": None
        }

    # State update logic
    new_phase = parsed_response.get("current_phase")
    valid_phases = ["Intro", "Question 1", "Question 1 Follow-up", "Question 2", "Question 2 Follow-up", "Wrap-up"]
    
    if new_phase and new_phase in valid_phases:
        prev_phase = session.current_phase
        session.current_phase = new_phase
        
        # When entering Question 1
        if new_phase == "Question 1" and prev_phase != "Question 1":
            parsed_response["editor_unlocked"] = True
            parsed_response["problem_id"] = session.q1["id"]
            parsed_response["problem_html"] = session.q1["html"]
            parsed_response["starter_code"] = session.q1["starter_code"].get(language, session.q1["starter_code"]["python"])
            parsed_response["sample_test_cases"] = session.q1.get("sample_test_cases", [])
            
        # When entering Question 2
        elif new_phase == "Question 2" and prev_phase != "Question 2":
            parsed_response["editor_unlocked"] = True
            parsed_response["problem_id"] = session.q2["id"]
            parsed_response["problem_html"] = session.q2["html"]
            parsed_response["starter_code"] = session.q2["starter_code"].get(language, session.q2["starter_code"]["python"])
            parsed_response["sample_test_cases"] = session.q2.get("sample_test_cases", [])
            
        # Ensure active coding phases keep editor unlocked
        if new_phase in ["Question 1", "Question 1 Follow-up", "Question 2", "Question 2 Follow-up"]:
            parsed_response["editor_unlocked"] = True
        elif new_phase in ["Intro", "Wrap-up"]:
            parsed_response["editor_unlocked"] = False

    session.history.append({"role": "model", "content": spoken_response})
    
    # If final or wrap-up, save report to MongoDB
    if (is_final_flag or new_phase == "Wrap-up") and reports_collection:
        try:
            report_doc = {
                "session_id": session_id,
                "candidate_name": session.candidate_name,
                "track": session.track,
                "track_name": session.track_name,
                "q1_title": session.q1["title"],
                "q2_title": session.q2["title"],
                "q1_code": session.q1_code or code,
                "q2_code": session.q2_code,
                "test_stats": session.test_stats,
                "evaluation_report": spoken_response,
                "scores": parsed_response.get("scores", {"problem_solving": 85, "code_quality": 80, "communication": 85, "overall": 83}),
                "recommendation": parsed_response.get("recommendation", "Hire"),
                "duration_seconds": int(time.time() - session.start_time),
                "created_at": time.time()
            }
            # Asynchronously save to MongoDB
            import asyncio
            asyncio.create_task(reports_collection.update_one(
                {"session_id": session_id},
                {"$set": report_doc},
                upsert=True
            ))
        except Exception as e:
            print(f"Failed to save MongoDB report: {e}")

    return parsed_response

@app.get("/api/reports/{session_id}")
async def get_report(session_id: str):
    """Retrieves saved evaluation report from MongoDB."""
    if not reports_collection:
        raise HTTPException(status_code=404, detail="Database not configured")
        
    doc = await reports_collection.find_one({"session_id": session_id}, {"_id": 0})
    if not doc:
        raise HTTPException(status_code=404, detail="Report not found")
    return doc

@app.websocket("/ws/live-interview")
async def live_interview_ws(websocket: WebSocket, session_id: str = "default"):
    """WebSocket endpoint for live bidirectional voice interaction."""
    if not genai_client:
        await websocket.close(code=1008)
        return
    await handle_live_interview_ws(websocket, session_id, genai_client, sessions)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
