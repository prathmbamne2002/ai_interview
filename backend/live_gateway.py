import asyncio
import json
import base64
from fastapi import WebSocket, WebSocketDisconnect
from google import genai
from google.genai import types

async def handle_live_interview_ws(websocket: WebSocket, session_id: str, genai_client: genai.Client, session_store: dict):
    """Bridges client WebSocket with Gemini 3.1 Flash Live API."""
    await websocket.accept()
    
    session = session_store.get(session_id)
    if not session:
        await websocket.send_json({"type": "error", "message": "Session not found"})
        await websocket.close()
        return

    track_name = getattr(session, "track_name", "General SDE")
    q1_title = session.q1["title"]
    q2_title = session.q2["title"]
    
    live_system_instruction = f"""You are Sanjay, an expert Senior Technical Interviewer conducting a realistic live technical DSA interview on the {track_name} track.
Your goal is to conduct a natural, spoken, real-time interview following this exact timeline:
1. Warm Intro: Greet candidate, ask 1 brief background question.
2. Question 1 ({q1_title}): Present problem, invite candidate to explain approach and write code.
3. Question 1 Follow-up: Ask about Time & Space Complexity and edge cases.
4. Question 2 ({q2_title}): Transition to problem 2, guide candidate.
5. Question 2 Follow-up: Ask about scaling or optimization.
6. Wrap-up: Conclude with encouraging, constructive feedback.

Keep your spoken responses SHORT (1-3 sentences), warm, and conversational.
"""

    config = types.LiveConnectConfig(
        response_modalities=[types.Modality.AUDIO],
        system_instruction=types.Content(
            parts=[types.Part.from_text(text=live_system_instruction)]
        ),
        thinking_config=types.ThinkingConfig(thinking_budget=0)
    )

    try:
        async with genai_client.aio.live.connect(model="gemini-3.1-flash-live-preview", config=config) as live_session:
            await websocket.send_json({"type": "status", "status": "connected", "message": "Connected to Sanjay (Live Voice)"})

            # Task 1: Receive from Gemini Live and stream to browser
            async def receive_from_gemini():
                try:
                    async for response in live_session.receive():
                        content = response.server_content
                        if content:
                            # Audio chunks
                            if content.model_turn:
                                for part in content.model_turn.parts:
                                    if part.inline_data:
                                        audio_b64 = base64.b64encode(part.inline_data.data).decode("utf-8")
                                        await websocket.send_json({
                                            "type": "audio",
                                            "data": audio_b64
                                        })
                            # Transcripts
                            if content.output_transcription:
                                await websocket.send_json({
                                    "type": "transcript",
                                    "role": "model",
                                    "text": content.output_transcription.text
                                })
                            if content.input_transcription:
                                await websocket.send_json({
                                    "type": "transcript",
                                    "role": "user",
                                    "text": content.input_transcription.text
                                })
                            # Interruption event
                            if content.interrupted is True:
                                await websocket.send_json({"type": "interrupted"})
                except Exception as e:
                    print(f"Error receiving from Gemini Live: {e}")

            # Task 2: Receive from browser and stream to Gemini Live
            async def receive_from_browser():
                try:
                    while True:
                        msg = await websocket.receive_text()
                        data = json.loads(msg)
                        msg_type = data.get("type")

                        if msg_type == "audio":
                            raw_pcm = base64.b64decode(data.get("data", ""))
                            await live_session.send_realtime_input(
                                audio=types.Blob(data=raw_pcm, mime_type="audio/pcm;rate=16000")
                            )
                        elif msg_type == "text":
                            await live_session.send_realtime_input(text=data.get("text", ""))
                        elif msg_type == "code_update":
                            code_snippet = data.get("code", "")
                            lang = data.get("language", "python")
                            await live_session.send_realtime_input(
                                text=f"[Candidate updated code in {lang}:\n```{lang}\n{code_snippet}\n```]"
                            )
                except WebSocketDisconnect:
                    pass
                except Exception as e:
                    print(f"Error receiving from browser: {e}")

            # Run both streaming tasks concurrently
            await asyncio.gather(receive_from_gemini(), receive_from_browser())

    except Exception as e:
        print(f"Live Gateway connection error: {e}")
        await websocket.send_json({"type": "error", "message": f"Live voice connection failed: {str(e)}"})
