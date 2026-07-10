from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from ..database import get_db
from ..models.db_models import User, Meeting, Commitment
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/chat", tags=["Chat"])

# ---- Request Model ----
class ChatRequest(BaseModel):
    user_id: int
    question: str

# ---- Chat Endpoint ----
@router.post("/ask")
async def ask_question(request: ChatRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == request.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # 1. Fetch all meetings for this user
    meetings = db.query(Meeting).filter(Meeting.user_id == request.user_id).all()
    if not meetings:
        return {"answer": "You haven't uploaded any meetings yet. Upload a meeting transcript to get started!"}
    
    # 2. Build a text context from all meetings and commitments
    context = ""
    for m in meetings:
        context += f"Meeting: {m.title} (Date: {m.meeting_date})\n"
        context += f"Summary: {m.summary}\n"
        commitments = db.query(Commitment).filter(Commitment.meeting_id == m.id).all()
        if commitments:
            context += "Commitments made in this meeting:\n"
            for c in commitments:
                context += f"  - {c.task} | Owner: {c.owner} | Status: {c.status} | Deadline: {c.deadline}\n"
        context += "\n---\n"
    
    # 3. Prepare the prompt for Fireworks AI
    prompt = f"""
You are EMOS, an AI assistant that helps organizations remember commitments and decisions.

Here is the user's complete meeting history:
{context}

The user asks: "{request.question}"

Instructions:
- Answer the question based ONLY on the meeting history above.
- If the information is not present, say "I don't have that information in your meeting records."
- Be concise, professional, and helpful.
- If the user asks about pending tasks, list them clearly.
- If the user asks about deadlines, show the dates.
"""

    # 4. Call Fireworks AI
    FIREWORKS_API_KEY = os.getenv("FIREWORKS_API_KEY")
    FIREWORKS_MODEL = os.getenv("FIREWORKS_MODEL", "accounts/fireworks/models/deepseek-v3")
    
    if not FIREWORKS_API_KEY:
        return {"answer": "⚠️ Fireworks API key is missing. Please set FIREWORKS_API_KEY in your .env file."}
    
    headers = {
        "Authorization": f"Bearer {FIREWORKS_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": FIREWORKS_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,
        "max_tokens": 1000
    }
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://api.fireworks.ai/inference/v1/chat/completions",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            answer = data["choices"][0]["message"]["content"]
            return {"answer": answer}
    except Exception as e:
        return {"answer": f"⚠️ Error calling AI: {str(e)}. Please check your API key."}