from sqlalchemy.orm import Session
from ..models.db_models import Commitment
from datetime import datetime

def update_overdue_status(db: Session):
    """
    Finds all commitments where the deadline has passed and status is not 'Done',
    and marks them as 'Overdue'.
    """
    now = datetime.utcnow()
    overdue_commits = db.query(Commitment).filter(
        Commitment.deadline < now,
        Commitment.status != "Done"
    ).all()
    
    for c in overdue_commits:
        c.status = "Overdue"
    
    if overdue_commits:
        db.commit()
    
    return len(overdue_commits)

def get_user_commitments(db: Session, user_name: str):
    """
    Returns all commitments where the owner name contains the given user_name.
    (Case-insensitive partial match)
    """
    return db.query(Commitment).filter(Commitment.owner.ilike(f"%{user_name}%")).all()

def get_blocked_commitments(db: Session):
    """
    Finds commitments that are blocked because their dependencies are not yet done.
    Returns a list of (blocked_commitment, blocking_commitment) pairs.
    """
    all_commits = db.query(Commitment).all()
    blocked = []
    
    for c in all_commits:
        if c.dependencies and len(c.dependencies) > 0:
            for dep_id in c.dependencies:
                dep = db.query(Commitment).filter(Commitment.id == dep_id).first()
                if dep and dep.status != "Done":
                    blocked.append({
                        "blocked_task": c.task,
                        "blocked_owner": c.owner,
                        "blocked_id": c.id,
                        "blocking_task": dep.task,
                        "blocking_owner": dep.owner,
                        "blocking_id": dep.id
                    })
                    break  # Only need to show one blocker per task
    
    return blocked

def get_commitment_summary(db: Session, user_name: str):
    """
    Returns a summary of commitments for a specific user (counts by status).
    """
    commits = get_user_commitments(db, user_name)
    
    pending = [c for c in commits if c.status == "Pending"]
    overdue = [c for c in commits if c.status == "Overdue"]
    done = [c for c in commits if c.status == "Done"]
    
    return {
        "total": len(commits),
        "pending": len(pending),
        "overdue": len(overdue),
        "done": len(done)
    }