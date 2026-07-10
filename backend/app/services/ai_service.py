import httpx
import os
import json
from .prompts import EXTRACTION_PROMPT
from dotenv import load_dotenv

load_dotenv()

FIREWORKS_API_KEY = os.getenv("FIREWORKS_API_KEY")
FIREWORKS_MODEL = os.getenv("FIREWORKS_MODEL", "accounts/fireworks/models/deepseek-v3")

async def extract_meeting_data(transcript_text: str):
    """
    Sends the meeting transcript to Fireworks AI and returns structured JSON data.
    """
    if not FIREWORKS_API_KEY:
        return {
            "error": "FIREWORKS_API_KEY not set in environment variables.",
            "summary": "AI service unavailable. Please set your API key.",
            "decisions": [],
            "action_items": [],
            "commitments": [],
            "risks": [],
            "dependencies": [],
            "questions": []
        }
    
    # Fill the prompt with the transcript
    prompt = EXTRACTION_PROMPT.format(transcript_text=transcript_text)
    
    headers = {
        "Authorization": f"Bearer {FIREWORKS_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": FIREWORKS_MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1,  # Low temperature = consistent, predictable output
        "max_tokens": 2500
    }
    
    try:
        async with httpx.AsyncClient(timeout=90.0) as client:
            response = await client.post(
                "https://api.fireworks.ai/inference/v1/chat/completions",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            
            # Clean the content: remove markdown code blocks if present
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            # Parse JSON
            parsed = json.loads(content.strip())
            
            # Ensure all keys exist
            default = {
                "summary": "",
                "decisions": [],
                "action_items": [],
                "commitments": [],
                "risks": [],
                "dependencies": [],
                "questions": []
            }
            # Merge parsed data with defaults (so missing keys don't break the app)
            for key in default:
                if key not in parsed:
                    parsed[key] = default[key]
            
            return parsed
            
    except json.JSONDecodeError as e:
        return {
            "error": f"JSON parse error: {str(e)}",
            "summary": "AI returned invalid JSON. Please check the transcript format.",
            "decisions": [],
            "action_items": [],
            "commitments": [],
            "risks": [],
            "dependencies": [],
            "questions": []
        }
    except Exception as e:
        return {
            "error": f"API error: {str(e)}",
            "summary": "AI service temporarily unavailable.",
            "decisions": [],
            "action_items": [],
            "commitments": [],
            "risks": [],
            "dependencies": [],
            "questions": []
        }