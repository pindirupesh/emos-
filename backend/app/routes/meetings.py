from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from datetime import datetime
from ..database import get_db
from ..models.db_models import User, Meeting, Commitment
from ..services.ai_service import extract_meeting_data
from ..services.commitment_service import update_overdue_status

router = APIRouter(prefix="/meetings", tags=["Meetings"])

# ---- Upload a Meeting Transcript ----
@router.post("/upload")
async def upload_meeting(
    user_id: int,
    title: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # 1. Check if user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # 2. Read the uploaded file content
    content = await file.read()
    transcript_text = content.decode("utf-8")
    
    # 3. Call Fireworks AI to extract structured data
    structured_data = await extract_meeting_data(transcript_text)
    
    # 4. Extract the summary from the AI response
    summary = structured_data.get("summary", "No summary generated.")
    
    # 5. Save the meeting to the database
    meeting = Meeting(
        user_id=user_id,
        title=title,
        transcript_text=transcript_text,
        summary=summary,
        structured_data=structured_data
    )
    db.add(meeting)
    db.commit()
    db.refresh(meeting)
    
    # 6. Save commitments from the AI output
    commitments_list = structured_data.get("commitments", [])
    for comm in commitments_list:
        deadline_str = comm.get("by_when", "")
        deadline = None
        if deadline_str and deadline_str != "No deadline specified":
            try:
                deadline = datetime.strptime(deadline_str, "%Y-%m-%d")
            except:
                deadline = None
        
        new_commitment = Commitment(
            meeting_id=meeting.id,
            task=comm.get("what", "Unnamed task"),
            owner=comm.get("who", "Unknown"),
            deadline=deadline,
            priority="Medium",
            status="Pending",
            dependencies=[]
        )
        db.add(new_commitment)
    
    db.commit()
    
    return {
        "meeting_id": meeting.id,
        "summary": summary,
        "structured_data": structured_data,
        "message": "Meeting uploaded and processed successfully!"
    }

# ---- Get All Commitments for a User ----
@router.get("/commitments/{user_id}")
def get_commitments(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update overdue status first
    update_overdue_status(db)
    
    # Find commitments where the user is the owner (case-insensitive partial match)
    commitments = db.query(Commitment).filter(Commitment.owner.ilike(f"%{user.name}%")).all()
    
    result = []
    for c in commitments:
        meeting = db.query(Meeting).filter(Meeting.id == c.meeting_id).first()
        result.append({
            "id": c.id,
            "task": c.task,
            "owner": c.owner,
            "deadline": c.deadline.isoformat() if c.deadline else None,
            "status": c.status,
            "priority": c.priority,
            "meeting_title": meeting.title if meeting else "Unknown",
            "dependencies": c.dependencies
        })
    
    return result

# ---- Full Dashboard Data for a User ----
@router.get("/dashboard/{user_id}")
def get_dashboard(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update overdue status
    update_overdue_status(db)
    
    # Get all commitments for this user
    all_commits = db.query(Commitment).filter(Commitment.owner.ilike(f"%{user.name}%")).all()
    
    pending = [c for c in all_commits if c.status == "Pending"]
    overdue = [c for c in all_commits if c.status == "Overdue"]
    done = [c for c in all_commits if c.status == "Done"]
    
    # Get recent meetings (last 5)
    recent_meetings = db.query(Meeting).filter(Meeting.user_id == user_id).order_by(Meeting.meeting_date.desc()).limit(5).all()
    
    return {
        "user_name": user.name,
        "stats": {
            "pending": len(pending),
            "overdue": len(overdue),
            "done": len(done),
            "total": len(all_commits)
        },
        "pending_commitments": [
            {"id": c.id, "task": c.task, "deadline": c.deadline.isoformat() if c.deadline else None}
            for c in pending[:5]
        ],
        "overdue_commitments": [
            {"id": c.id, "task": c.task, "deadline": c.deadline.isoformat() if c.deadline else None}
            for c in overdue
        ],
        "recent_meetings": [
            {"id": m.id, "title": m.title, "date": m.meeting_date.isoformat()}
            for m in recent_meetings
        ]
    }