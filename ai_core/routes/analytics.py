from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from database import get_db
from models import User, UserAnalytics, QuizHistory
from schemas import (
    DashboardResponse, UserProfile, UserAnalyticsResponse,
    QuizHistoryItem, CategoryPerformance, DailyScore
)
from auth import get_current_user

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get complete user dashboard."""
    
    # User profile
    user_profile = UserProfile(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        avatar_url=current_user.avatar_url,
        bio=current_user.bio,
        created_at=current_user.created_at
    )
    
    # User analytics
    analytics = db.query(UserAnalytics).filter(UserAnalytics.user_id == current_user.id).first()
    if not analytics:
        analytics = UserAnalytics(user_id=current_user.id)
        db.add(analytics)
        db.commit()
    
    analytics_data = UserAnalyticsResponse(
        total_quizzes=analytics.total_quizzes,
        average_score=analytics.average_score,
        total_reading_time_seconds=analytics.total_reading_time_seconds,
        best_category=analytics.best_category,
        weakest_category=analytics.weakest_category,
        best_score=analytics.best_score,
        worst_score=analytics.worst_score,
        total_summaries_generated=analytics.total_summaries_generated,
        last_quiz_date=analytics.last_quiz_date
    )
    
    # Recent quizzes
    recent_quizzes = db.query(QuizHistory).filter(
        QuizHistory.user_id == current_user.id
    ).order_by(desc(QuizHistory.created_at)).limit(5).all()
    
    recent_quizzes_data = [
        QuizHistoryItem(
            id=q.id,
            article_title=q.article_title,
            percentage_score=q.percentage_score,
            score=q.score,
            total_questions=q.total_questions,
            difficulty=q.difficulty,
            category=q.category,
            time_taken_seconds=q.time_taken_seconds,
            created_at=q.created_at
        )
        for q in recent_quizzes
    ]
    
    # Category performance
    category_stats = db.query(
        QuizHistory.category,
        func.avg(QuizHistory.percentage_score).label("avg_score"),
        func.count(QuizHistory.id).label("count")
    ).filter(
        QuizHistory.user_id == current_user.id,
        QuizHistory.category != None
    ).group_by(QuizHistory.category).all()
    
    category_performance = [
        CategoryPerformance(
            category=stat[0],
            average_score=float(stat[1]) if stat[1] else 0.0,
            total_quizzes=stat[2],
            trend=0.0  # Calculate trend based on recent vs older quizzes
        )
        for stat in category_stats
    ]
    
    # Daily progress (last 7 days)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    daily_stats = db.query(
        func.date(QuizHistory.created_at).label("date"),
        func.avg(QuizHistory.percentage_score).label("avg_score"),
        func.count(QuizHistory.id).label("quiz_count")
    ).filter(
        QuizHistory.user_id == current_user.id,
        QuizHistory.created_at >= seven_days_ago
    ).group_by(func.date(QuizHistory.created_at)).all()
    
    daily_progress = [
        DailyScore(
            date=str(stat[0]),
            average_score=float(stat[1]) if stat[1] else 0.0,
            quiz_count=stat[2]
        )
        for stat in daily_stats
    ]
    
    return DashboardResponse(
        user_profile=user_profile,
        analytics=analytics_data,
        recent_quizzes=recent_quizzes_data,
        category_performance=category_performance,
        daily_progress=daily_progress
    )


@router.get("/user", response_model=UserAnalyticsResponse)
async def get_user_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user analytics summary."""
    
    analytics = db.query(UserAnalytics).filter(UserAnalytics.user_id == current_user.id).first()
    
    if not analytics:
        analytics = UserAnalytics(user_id=current_user.id)
        db.add(analytics)
        db.commit()
    
    return UserAnalyticsResponse(
        total_quizzes=analytics.total_quizzes,
        average_score=analytics.average_score,
        total_reading_time_seconds=analytics.total_reading_time_seconds,
        best_category=analytics.best_category,
        weakest_category=analytics.weakest_category,
        best_score=analytics.best_score,
        worst_score=analytics.worst_score,
        total_summaries_generated=analytics.total_summaries_generated,
        last_quiz_date=analytics.last_quiz_date
    )


@router.get("/performance/by-category")
async def get_performance_by_category(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get performance statistics by category."""
    
    stats = db.query(
        QuizHistory.category,
        func.count(QuizHistory.id).label("total"),
        func.avg(QuizHistory.percentage_score).label("avg_score"),
        func.max(QuizHistory.percentage_score).label("best_score"),
        func.min(QuizHistory.percentage_score).label("worst_score")
    ).filter(
        QuizHistory.user_id == current_user.id,
        QuizHistory.category != None
    ).group_by(QuizHistory.category).all()
    
    result = [
        {
            "category": stat[0],
            "total_quizzes": stat[1],
            "average_score": float(stat[2]) if stat[2] else 0.0,
            "best_score": float(stat[3]) if stat[3] else 0.0,
            "worst_score": float(stat[4]) if stat[4] else 0.0
        }
        for stat in stats
    ]
    
    return {"categories": result}


@router.get("/performance/by-difficulty")
async def get_performance_by_difficulty(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get performance statistics by difficulty level."""
    
    stats = db.query(
        QuizHistory.difficulty,
        func.count(QuizHistory.id).label("total"),
        func.avg(QuizHistory.percentage_score).label("avg_score"),
        func.max(QuizHistory.percentage_score).label("best_score"),
        func.min(QuizHistory.percentage_score).label("worst_score")
    ).filter(
        QuizHistory.user_id == current_user.id
    ).group_by(QuizHistory.difficulty).all()
    
    result = [
        {
            "difficulty": stat[0],
            "total_quizzes": stat[1],
            "average_score": float(stat[2]) if stat[2] else 0.0,
            "best_score": float(stat[3]) if stat[3] else 0.0,
            "worst_score": float(stat[4]) if stat[4] else 0.0
        }
        for stat in stats
    ]
    
    return {"difficulties": result}


@router.get("/performance/daily")
async def get_daily_performance(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get daily performance history."""
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    stats = db.query(
        func.date(QuizHistory.created_at).label("date"),
        func.count(QuizHistory.id).label("quiz_count"),
        func.avg(QuizHistory.percentage_score).label("avg_score"),
        func.sum(QuizHistory.time_taken_seconds).label("total_time_seconds")
    ).filter(
        QuizHistory.user_id == current_user.id,
        QuizHistory.created_at >= start_date
    ).group_by(func.date(QuizHistory.created_at)).order_by(func.date(QuizHistory.created_at)).all()
    
    result = [
        {
            "date": str(stat[0]),
            "quiz_count": stat[1],
            "average_score": float(stat[2]) if stat[2] else 0.0,
            "total_time_seconds": stat[3] or 0
        }
        for stat in stats
    ]
    
    return {"daily_stats": result}


@router.get("/streak")
async def get_quiz_streak(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Calculate current quiz streak."""
    
    # Get quizzes ordered by date (most recent first)
    quizzes = db.query(QuizHistory.created_at).filter(
        QuizHistory.user_id == current_user.id
    ).order_by(desc(QuizHistory.created_at)).all()
    
    if not quizzes:
        return {"current_streak": 0, "longest_streak": 0}
    
    # Calculate streak
    current_streak = 0
    longest_streak = 0
    current_date = datetime.utcnow().date()
    
    for quiz in quizzes:
        quiz_date = quiz[0].date()
        if quiz_date == current_date or quiz_date == current_date - timedelta(days=1):
            current_streak += 1
            current_date = quiz_date
        else:
            break
    
    # Get longest streak (simplified)
    all_quizzes = db.query(QuizHistory).filter(
        QuizHistory.user_id == current_user.id
    ).order_by(QuizHistory.created_at).all()
    
    longest_streak = len(all_quizzes)  # Simplified; can be optimized
    
    return {
        "current_streak": current_streak,
        "longest_streak": longest_streak
    }
