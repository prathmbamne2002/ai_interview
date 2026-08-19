import os
import json
import random
from fastapi import FastAPI, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import motor.motor_asyncio
from google import genai
from google.genai import types

load_dotenv()

app = FastAPI()

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

# In-memory storage for session state
sessions = {}

QUESTION_1_POOL = [
    {
        "title": "Two Sum",
        "difficulty": "Easy",
        "html": '''<h2 class="problemTitle">Question 1: Two Sum</h2>
<div class="problemText">
    <p>Given an array of integers <span class="codeBlock">nums</span> and an integer <span class="codeBlock">target</span>, return indices of the two numbers such that they add up to <span class="codeBlock">target</span>.</p>
    <p>You may assume that each input would have <strong>exactly one solution</strong>, and you may not use the same element twice.</p>
    <p>You can return the answer in any order.</p>
    <h3>Sample Input 1:</h3>
    <div class="sampleBox">nums = [2,7,11,15], target = 9</div>
    <h3>Expected Output 1:</h3>
    <div class="sampleBox">[0,1]</div>
</div>''',
        "starter_code": {
            "cpp": "#include <bits/stdc++.h>\nusing namespace std;\n\nvector<int> twoSum(vector<int>& nums, int target) {\n    // Write your solution here\n    return {};\n}",
            "java": "import java.util.*;\n\nclass Solution {\n    public int[] twoSum(int[] nums, int target) {\n        // Write your solution here\n        return new int[]{};\n    }\n}",
            "python": "class Solution:\n    def twoSum(self, nums: list[int], target: int) -> list[int]:\n        # Write your solution here\n        return []"
        }
    },
    {
        "title": "Stable Subarrays With Equal Boundary",
        "difficulty": "Medium",
        "html": '''<h2 class="problemTitle">Question 1: Stable Subarrays With Equal Boundary</h2>
<div class="problemText">
    <p>You are given an integer array <span class="codeBlock">capacity</span>.</p>
    <p>A subarray is considered <strong>stable</strong> if:</p>
    <ul>
        <li>Its length is at least <span class="codeBlock">3</span>, and</li>
        <li>The <strong>first</strong> and <strong>last</strong> elements are each equal to the <strong>sum of all elements strictly between them</strong>.</li>
    </ul>
    <p>Your task is to return the total number of stable subarrays in the given array.</p>
    <h3>Sample Input 1:</h3>
    <div class="sampleBox">9 3 3 3 9</div>
    <h3>Expected Output 1:</h3>
    <div class="sampleBox">2</div>
</div>''',
        "starter_code": {
            "cpp": "#include <bits/stdc++.h>\nusing namespace std;\n\nlong long countStableSubarrays(vector<long long>& capacity) {\n    // Write your code here.\n    return 0;\n}",
            "java": "class Solution {\n    public long countStableSubarrays(int[] capacity) {\n        // Write your code here.\n        return 0;\n    }\n}",
            "python": "class Solution:\n    def countStableSubarrays(self, capacity: list[int]) -> int:\n        # Write your code here.\n        return 0"
        }
    }
]

QUESTION_2_POOL = [
    {
        "title": "Merge Intervals",
        "difficulty": "Medium",
        "html": '''<h2 class="problemTitle">Question 2: Merge Intervals</h2>
<div class="problemText">
    <p>Given an array of <span class="codeBlock">intervals</span> where <span class="codeBlock">intervals[i] = [start_i, end_i]</span>, merge all overlapping intervals, and return an array of the non-overlapping intervals that cover all the intervals in the input.</p>
    <h3>Sample Input 1:</h3>
    <div class="sampleBox">intervals = [[1,3],[2,6],[8,10],[15,18]]</div>
    <h3>Expected Output 1:</h3>
    <div class="sampleBox">[[1,6],[8,10],[15,18]]</div>
</div>''',
        "starter_code": {
            "cpp": "#include <bits/stdc++.h>\nusing namespace std;\n\nvector<vector<int>> merge(vector<vector<int>>& intervals) {\n    // Write your solution here\n    return {};\n}",
            "java": "import java.util.*;\n\nclass Solution {\n    public int[][] merge(int[][] intervals) {\n        // Write your solution here\n        return new int[][]{};\n    }\n}",
            "python": "class Solution:\n    def merge(self, intervals: list[list[int]]) -> list[list[int]]:\n        # Write your solution here\n        return []"
        }
    },
    {
        "title": "Longest Substring Without Repeating Characters",
        "difficulty": "Medium",
        "html": '''<h2 class="problemTitle">Question 2: Longest Substring Without Repeating Characters</h2>
<div class="problemText">
    <p>Given a string <span class="codeBlock">s</span>, find the length of the <strong>longest substring</strong> without repeating characters.</p>
    <h3>Sample Input 1:</h3>
    <div class="sampleBox">s = "abcabcbb"</div>
    <h3>Expected Output 1:</h3>
    <div class="sampleBox">3</div>
    <p>Explanation: The answer is "abc", with the length of 3.</p>
</div>''',
        "starter_code": {
            "cpp": "#include <bits/stdc++.h>\nusing namespace std;\n\nint lengthOfLongestSubstring(string s) {\n    // Write your solution here\n    return 0;\n}",
            "java": "import java.util.*;\n\nclass Solution {\n    public int lengthOfLongestSubstring(String s) {\n        // Write your solution here\n        return 0;\n    }\n}",
            "python": "class Solution:\n    def lengthOfLongestSubstring(self, s: str) -> int:\n        # Write your solution here\n        return 0"
        }
    }
]

class InterviewSession:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.current_phase = "Intro"
        self.q1 = random.choice(QUESTION_1_POOL)
        self.q2 = random.choice(QUESTION_2_POOL)
        self.history = [] # Stores {"role": "user"|"model", "content": text}

@app.get("/")
def read_root():
    return {"message": "AI Interview Backend is running"}

def construct_system_prompt(session: InterviewSession, code: str, language: str, is_final: bool) -> str:
    """Builds the system prompt for a realistic 2-question technical DSA interview."""
    if is_final:
        return f"""You are Sanjay, a Senior Technical Interviewer concluding the interview.
Current Phase: Wrap-up
Candidate Language: {language}
Final Code in Editor:
```{language}
{code}
```

Provide a comprehensive, encouraging evaluation report analyzing the candidate's performance across:
1. Problem Solving & Algorithms (Accuracy, Optimization)
2. Code Quality & Syntax (Cleanliness, Modularity)
3. Communication & Complexity Analysis (Clarity, Edge Cases)
4. Overall Recommendation (Strong Hire / Hire / Lean Hire / No Hire)

Output your response strictly as JSON:
{{
    "ai_response": "Full detailed final evaluation report text...",
    "current_phase": "Wrap-up",
    "editor_unlocked": false,
    "problem_html": null,
    "starter_code": null
}}
"""

    return f"""You are Sanjay, a Senior Technical Interviewer conducting a realistic, interactive live DSA technical interview.

INTERVIEW SPECIFICATION & TIMELINE:
You MUST follow this exact 5-stage interview pipeline:
1. Intro Phase:
   - Greet the candidate warmly and ask EXACTLY ONE brief background question (e.g., their background, tech stack, or favorite project).
   - As soon as the candidate answers, acknowledge it warmly and IMMEDIATELY transition to "Question 1".

2. Question 1 Phase: Problem: "{session.q1['title']}"
   - Introduce Question 1 and ask the candidate to explain their high-level approach before/while writing code.
   - Unlock the editor.
   - Once the candidate writes the solution or explains a valid approach, acknowledge it and transition to "Question 1 Follow-up".

3. Question 1 Follow-up Phase:
   - Ask about Time Complexity, Space Complexity (Big-O), and edge cases (e.g. negative numbers, empty arrays, duplicates).
   - Once the candidate answers the follow-up questions, acknowledge their answer and IMMEDIATELY transition to "Question 2".

4. Question 2 Phase: Problem: "{session.q2['title']}"
   - Present Question 2 and invite the candidate to solve it in the editor.
   - Once solved or discussed, transition to "Question 2 Follow-up".

5. Question 2 Follow-up Phase:
   - Ask a scaling or optimization question (e.g., memory limits, streaming inputs, alternative data structures).
   - Once answered or if candidate is ready, transition to "Wrap-up".

6. Wrap-up Phase:
   - Conclude the interview professionally. Provide clear, structured feedback on Problem Solving, Code Quality, and Communication.

CURRENT STATE:
- Current Phase: {session.current_phase}
- Candidate Language: {language}
- Current Code in Editor:
```{language}
{code}
```

CONVERSATIONAL RULES:
- Speak like a REAL HUMAN interviewer in a live call.
- Keep your 'ai_response' SHORT and natural (1 to 3 sentences maximum).
- Never output huge monologues. Ask one question or prompt at a time.
- Be encouraging, professional, and clear.

OUTPUT SCHEMA:
You MUST output ONLY a valid JSON object matching this schema:
{{
    "ai_response": "The spoken words for the candidate (1-3 conversational sentences)",
    "current_phase": "Intro" | "Question 1" | "Question 1 Follow-up" | "Question 2" | "Question 2 Follow-up" | "Wrap-up",
    "editor_unlocked": true/false,
    "problem_html": "HTML problem statement if introducing Question 1 or Question 2, otherwise null",
    "starter_code": "Starter code string if introducing Question 1 or Question 2 for the chosen language, otherwise null"
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
    
    # Handle initial vs ongoing user message
    user_message = transcription.strip()
    if not session.history and not user_message:
        user_message = "Hi, I am ready to start the interview."
        
    if user_message:
        session.history.append({"role": "user", "content": user_message})
    
    # Construct Gemini contents array (limit to last 10 messages for ultra-fast latency)
    contents = []
    recent_history = session.history[-10:] if len(session.history) > 10 else session.history
    for msg in recent_history:
        contents.append(
            types.Content(
                role="user" if msg["role"] == "user" else "model", 
                parts=[types.Part.from_text(text=msg["content"])]
            )
        )
    
    is_final_flag = is_final is True or str(is_final).lower() in ["true", "1"]
    
    system_prompt = construct_system_prompt(session, code, language, is_final_flag)
    
    # Fast Gemini generation with thinking_budget=0
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
            spoken_response = parsed_response.get("ai_response", "Let's continue with the problem.")
            break
        except Exception as e:
            print(f"Error with model {model_name}: {e}")
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
            parsed_response["problem_html"] = session.q1["html"]
            parsed_response["starter_code"] = session.q1["starter_code"].get(language, session.q1["starter_code"]["python"])
            
        # When entering Question 2
        elif new_phase == "Question 2" and prev_phase != "Question 2":
            parsed_response["editor_unlocked"] = True
            parsed_response["problem_html"] = session.q2["html"]
            parsed_response["starter_code"] = session.q2["starter_code"].get(language, session.q2["starter_code"]["python"])
            
        # During any active coding or follow-up phase, ensure editor stays unlocked
        if new_phase in ["Question 1", "Question 1 Follow-up", "Question 2", "Question 2 Follow-up"]:
            parsed_response["editor_unlocked"] = True
        elif new_phase in ["Intro", "Wrap-up"]:
            parsed_response["editor_unlocked"] = False

    # Store AI response in history
    session.history.append({"role": "model", "content": spoken_response})
    
    return parsed_response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
