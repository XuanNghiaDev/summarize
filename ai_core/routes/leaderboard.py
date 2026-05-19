from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from database import get_db
from models import User, Leaderboard, UserAnalytics, QuizHistory
from schemas import LeaderboardResponse, LeaderboardEntry
from auth import get_current_user

router = APIRouter(prefix="/leaderboard", tags=["Leaderboard"])


def update_leaderboard(db: Session):
    """Rebuild leaderboard rankings."""
    
    # Get user analytics with rankings
    rankings = db.query(
        User.id,
        User.email,
        User.full_name,
        User.avatar_url,
        UserAnalytics.average_score,
        UserAnalytics.total_quizzes,
        UserAnalytics.total_summaries_generated
    ).join(
        UserAnalytics,
        User.id == UserAnalytics.user_id
    ).filter(
        User.is_active == True
    ).order_by(
        desc(UserAnalytics.average_score),
        desc(UserAnalytics.total_quizzes)
    ).all()
    
    # Clear old leaderboard
    db.query(Leaderboard).delete()
    db.commit()
    
    # Insert new rankings
    for rank, (user_id, email, full_name, avatar_url, avg_score, total_quizzes, total_summaries) in enumerate(rankings, 1):
        leaderboard_entry = Leaderboard(
            user_id=user_id,
            email=email,
            full_name=full_name,
            avatar_url=avatar_url,
            average_score=avg_score or 0.0,
            total_quizzes=total_quizzes or 0,
            total_summaries=total_summaries or 0,
            rank=rank
        )
        db.add(leaderboard_entry)
    
    db.commit()


@router.get("/", response_model=LeaderboardResponse)
async def get_leaderboard(
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get global leaderboard rankings."""
    
    # Update leaderboard if needed
    existing_entries = db.query(Leaderboard).count()
    if existing_entries == 0:
        update_leaderboard(db)
    
    # Get top entries
    entries = db.query(Leaderboard).order_by(Leaderboard.rank).limit(limit).all()
    
    leaderboard_entries = [
        LeaderboardEntry(
            rank=entry.rank,
            email=entry.email,
            full_name=entry.full_name,
            avatar_url=entry.avatar_url,
            average_score=entry.average_score,
            total_quizzes=entry.total_quizzes,
            total_summaries=entry.total_summaries
        )
        for entry in entries
    ]
    
    # Get user's rank
    user_rank_entry = db.query(Leaderboard).filter(Leaderboard.user_id == current_user.id).first()
    user_rank = user_rank_entry.rank if user_rank_entry else None
    
    # Total users
    total_users = db.query(User).filter(User.is_active == True).count()
    
    return LeaderboardResponse(
        total_users=total_users,
        entries=leaderboard_entries,
        user_rank=user_rank
    )


@router.get("/by-score", response_model=LeaderboardResponse)
async def get_leaderboard_by_score(
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get leaderboard sorted by average score."""
    
    # Update first
    update_leaderboard(db)
    
    entries = db.query(Leaderboard).order_by(
        desc(Leaderboard.average_score),
        desc(Leaderboard.total_quizzes)
    ).limit(limit).all()
    
    leaderboard_entries = [
        LeaderboardEntry(
            rank=rank,
            email=entry.email,
            full_name=entry.full_name,
            avatar_url=entry.avatar_url,
            average_score=entry.average_score,
            total_quizzes=entry.total_quizzes,
            total_summaries=entry.total_summaries
        )
        for rank, entry in enumerate(entries, 1)
    ]
    
    # Get user's rank
    user_rank_entry = db.query(Leaderboard).filter(Leaderboard.user_id == current_user.id).first()
    user_rank = user_rank_entry.rank if user_rank_entry else None
    
    total_users = db.query(User).filter(User.is_active == True).count()
    
    return LeaderboardResponse(
        total_users=total_users,
        entries=leaderboard_entries,
        user_rank=user_rank
    )


@router.get("/by-quizzes", response_model=LeaderboardResponse)
async def get_leaderboard_by_quizzes(
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get leaderboard sorted by quiz count."""
    
    # Update first
    update_leaderboard(db)
    
    entries = db.query(Leaderboard).order_by(
        desc(Leaderboard.total_quizzes),
        desc(Leaderboard.average_score)
    ).limit(limit).all()
    
    leaderboard_entries = [
        LeaderboardEntry(
            rank=rank,
            email=entry.email,
            full_name=entry.full_name,
            avatar_url=entry.avatar_url,
            average_score=entry.average_score,
            total_quizzes=entry.total_quizzes,
            total_summaries=entry.total_summaries
        )
        for rank, entry in enumerate(entries, 1)
    ]
    
    total_users = db.query(User).filter(User.is_active == True).count()
    
    user_rank_entry = db.query(Leaderboard).filter(Leaderboard.user_id == current_user.id).first()
    user_rank = user_rank_entry.rank if user_rank_entry else None
    
    return LeaderboardResponse(
        total_users=total_users,
        entries=leaderboard_entries,
        user_rank=user_rank
    )


@router.post("/rebuild", status_code=status.HTTP_200_OK)
async def rebuild_leaderboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Rebuild leaderboard (admin only - simplified)."""
    
    update_leaderboard(db)
    return {"message": "Leaderboard rebuilt successfully"}
