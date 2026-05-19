from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from database import get_db
from models import User, QuizHistory, UserAnalytics
from schemas import QuizSubmission, QuizResult, QuizHistoryList, QuizHistoryItem
from auth import get_current_user
import json

router = APIRouter(prefix="/quiz", tags=["Quiz"])


@router.post("/submit", response_model=QuizResult, status_code=status.HTTP_201_CREATED)
async def submit_quiz(
    quiz_data: QuizSubmission,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit quiz answers and save to history."""
    
    # Calculate score
    total = len(quiz_data.questions)
    correct = sum(1 for q in quiz_data.questions if q.is_correct)
    percentage = (correct / total * 100) if total > 0 else 0
    
    # Store quiz as JSON
    quiz_json = {
        "questions": [
            {
                "id": q.id,
                "question": q.question,
                "options": q.options,
                "correct_answer": q.correct_answer,
                "user_answer": q.user_answer,
                "is_correct": q.is_correct
            }
            for q in quiz_data.questions
        ]
    }
    
    # Create quiz history record
    quiz_record = QuizHistory(
        user_id=current_user.id,
        article_title=quiz_data.article_title,
        article_text=quiz_data.article_text,
        summary_text=quiz_data.summary_text,
        quiz_json=quiz_json,
        score=correct,
        total_questions=total,
        percentage_score=percentage,
        time_taken_seconds=quiz_data.time_taken_seconds,
        difficulty=quiz_data.difficulty,
        category=quiz_data.category,
        language=quiz_data.language
    )
    
    db.add(quiz_record)
    db.commit()
    db.refresh(quiz_record)
    
    # Update analytics
    update_user_analytics(current_user.id, db, correct, total, quiz_data.time_taken_seconds, quiz_data.category)
    
    return QuizResult(
        id=quiz_record.id,
        score=correct,
        total_questions=total,
        percentage_score=percentage,
        time_taken_seconds=quiz_data.time_taken_seconds,
        difficulty=quiz_data.difficulty,
        category=quiz_data.category,
        created_at=quiz_record.created_at,
        questions=quiz_data.questions
    )


@router.get("/history", response_model=QuizHistoryList)
async def get_quiz_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    difficulty: str = Query(None),
    category: str = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get quiz history with pagination and filters."""
    
    query = db.query(QuizHistory).filter(QuizHistory.user_id == current_user.id)
    
    # Apply filters
    if difficulty:
        query = query.filter(QuizHistory.difficulty == difficulty)
    
    if category:
        query = query.filter(QuizHistory.category == category)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    skip = (page - 1) * page_size
    records = query.order_by(desc(QuizHistory.created_at)).offset(skip).limit(page_size).all()
    
    items = [
        QuizHistoryItem(
            id=r.id,
            article_title=r.article_title,
            percentage_score=r.percentage_score,
            score=r.score,
            total_questions=r.total_questions,
            difficulty=r.difficulty,
            category=r.category,
            time_taken_seconds=r.time_taken_seconds,
            created_at=r.created_at
        )
        for r in records
    ]
    
    return QuizHistoryList(
        total=total,
        page=page,
        page_size=page_size,
        items=items
    )


@router.get("/history/{quiz_id}", response_model=QuizResult)
async def get_quiz_detail(
    quiz_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed quiz result."""
    
    record = db.query(QuizHistory).filter(
        QuizHistory.id == quiz_id,
        QuizHistory.user_id == current_user.id
    ).first()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz record not found"
        )
    
    # Parse quiz JSON and reconstruct questions
    quiz_data = record.quiz_json
    questions = [
        QuizQuestion(
            id=q["id"],
            question=q["question"],
            options=q["options"],
            correct_answer=q["correct_answer"],
            user_answer=q["user_answer"],
            is_correct=q["is_correct"]
        )
        for q in quiz_data.get("questions", [])
    ]
    
    return QuizResult(
        id=record.id,
        score=record.score,
        total_questions=record.total_questions,
        percentage_score=record.percentage_score,
        time_taken_seconds=record.time_taken_seconds,
        difficulty=record.difficulty,
        category=record.category,
        created_at=record.created_at,
        questions=questions
    )


@router.delete("/history/{quiz_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_quiz_record(
    quiz_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a quiz record."""
    
    record = db.query(QuizHistory).filter(
        QuizHistory.id == quiz_id,
        QuizHistory.user_id == current_user.id
    ).first()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz record not found"
        )
    
    db.delete(record)
    db.commit()


def update_user_analytics(
    user_id: int,
    db: Session,
    score: int,
    total: int,
    time_taken: int,
    category: str = None
):
    """Update or create user analytics."""
    
    analytics = db.query(UserAnalytics).filter(UserAnalytics.user_id == user_id).first()
    
    if not analytics:
        analytics = UserAnalytics(user_id=user_id)
        db.add(analytics)
    
    # Update metrics
    analytics.total_quizzes += 1
    
    # Update average score
    old_avg = analytics.average_score
    new_avg = (old_avg * (analytics.total_quizzes - 1) + (score / total * 100)) / analytics.total_quizzes
    analytics.average_score = new_avg
    
    # Track best and worst
    percentage = score / total * 100 if total > 0 else 0
    if percentage > analytics.best_score:
        analytics.best_score = percentage
    if analytics.worst_score == 0 or percentage < analytics.worst_score:
        analytics.worst_score = percentage
    
    # Add reading time
    analytics.total_reading_time_seconds += time_taken
    
    # Update best/weakest category (simplified - in production use aggregation)
    if category:
        category_scores = db.query(QuizHistory).filter(
            QuizHistory.user_id == user_id,
            QuizHistory.category == category
        ).all()
        
        if category_scores:
            cat_avg = sum(q.percentage_score for q in category_scores) / len(category_scores)
            if not analytics.best_category:
                analytics.best_category = category
            elif cat_avg > 70:  # High performing
                analytics.best_category = category
    
    # Update last quiz date
    from datetime import datetime
    analytics.last_quiz_date = datetime.utcnow()
    
    db.commit()


# Import for type hints
from schemas import QuizQuestion
