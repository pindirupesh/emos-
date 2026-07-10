EXTRACTION_PROMPT = """
You are an AI assistant that extracts structured information from business meeting transcripts.

Given the meeting transcript below, output ONLY a valid JSON object with this exact structure:

{
  "summary": "A 2-3 sentence executive summary of the entire meeting",
  "decisions": ["Decision 1 made", "Decision 2 made"],
  "action_items": [
    {
      "task": "Specific task description",
      "owner": "Person responsible",
      "deadline": "YYYY-MM-DD or 'No deadline specified'",
      "priority": "High/Medium/Low"
    }
  ],
  "commitments": [
    {
      "who": "Person making the commitment",
      "what": "What they committed to",
      "by_when": "YYYY-MM-DD or 'No deadline specified'"
    }
  ],
  "risks": ["Risk 1", "Risk 2"],
  "dependencies": ["Task A depends on Task B", ...],
  "questions": ["Unanswered question 1", ...]
}

RULES:
- If a field has no data, use an empty array [] or empty string "".
- Use "No deadline specified" if a deadline is not mentioned.
- Use "Unknown" for owner if not clear.
- Output ONLY valid JSON. No extra text, no markdown, no explanations.

Transcript:
{transcript_text}

Output ONLY valid JSON:
"""