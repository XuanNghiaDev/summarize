from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from database import get_db
from models import User, Summary, UserAnalytics
from schemas import SummarySaveRequest, SummaryResponse, SummaryListResponse
from auth import get_current_user

router = APIRouter(prefix="/summary", tags=["Summary"])


@router.post("/save", response_model=SummaryResponse, status_code=status.HTTP_201_CREATED)
async def save_summary(
    summary_data: SummarySaveRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Save generated summary."""
    
    # Calculate compression ratio
    word_count_original = len(summary_data.article_text.split())
    word_count_summary = len(summary_data.summary_text.split())
    compression_ratio = (word_count_original - word_count_summary) / word_count_original if word_count_original > 0 else 0
    
    # Create summary record
    summary = Summary(
        user_id=current_user.id,
        article_text=summary_data.article_text,
        article_title=summary_data.article_title,
        summary_text=summary_data.summary_text,
        source_url=summary_data.source_url,
        source_type=summary_data.source_type,
        language=summary_data.language,
        algorithm_used=summary_data.algorithm_used,
        word_count_original=word_count_original,
        word_count_summary=word_count_summary,
        compression_ratio=compression_ratio
    )
    
    db.add(summary)
    db.commit()
    db.refresh(summary)
    
    # Update user analytics
    analytics = db.query(UserAnalytics).filter(UserAnalytics.user_id == current_user.id).first()
    if analytics:
        analytics.total_summaries_generated += 1
        db.commit()
    
    return SummaryResponse(
        id=summary.id,
        article_title=summary.article_title,
        article_text=summary.article_text,
        summary_text=summary.summary_text,
        algorithm_used=summary.algorithm_used,
        word_count_original=summary.word_count_original,
        word_count_summary=summary.word_count_summary,
        compression_ratio=summary.compression_ratio,
        is_favorite=summary.is_favorite,
        created_at=summary.created_at
    )


@router.get("/list", response_model=SummaryListResponse)
async def get_summaries(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    language: str = Query(None),
    algorithm: str = Query(None),
    is_favorite: bool = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's saved summaries with filters."""
    
    query = db.query(Summary).filter(Summary.user_id == current_user.id)
    
    # Apply filters
    if language:
        query = query.filter(Summary.language == language)
    
    if algorithm:
        query = query.filter(Summary.algorithm_used == algorithm)
    
    if is_favorite is not None:
        query = query.filter(Summary.is_favorite == is_favorite)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    skip = (page - 1) * page_size
    summaries = query.order_by(desc(Summary.created_at)).offset(skip).limit(page_size).all()
    
    items = [
        SummaryResponse(
            id=s.id,
            article_title=s.article_title,
            article_text=s.article_text,
            summary_text=s.summary_text,
            algorithm_used=s.algorithm_used,
            word_count_original=s.word_count_original,
            word_count_summary=s.word_count_summary,
            compression_ratio=s.compression_ratio,
            is_favorite=s.is_favorite,
            created_at=s.created_at
        )
        for s in summaries
    ]
    
    return SummaryListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=items
    )


@router.get("/{summary_id}", response_model=SummaryResponse)
async def get_summary(
    summary_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific summary."""
    
    summary = db.query(Summary).filter(
        Summary.id == summary_id,
        Summary.user_id == current_user.id
    ).first()
    
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Summary not found"
        )
    
    return SummaryResponse(
        id=summary.id,
        article_title=summary.article_title,
        article_text=summary.article_text,
        summary_text=summary.summary_text,
        algorithm_used=summary.algorithm_used,
        word_count_original=summary.word_count_original,
        word_count_summary=summary.word_count_summary,
        compression_ratio=summary.compression_ratio,
        is_favorite=summary.is_favorite,
        created_at=summary.created_at
    )


@router.put("/{summary_id}/favorite", response_model=SummaryResponse)
async def toggle_favorite(
    summary_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Toggle summary favorite status."""
    
    summary = db.query(Summary).filter(
        Summary.id == summary_id,
        Summary.user_id == current_user.id
    ).first()
    
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Summary not found"
        )
    
    summary.is_favorite = not summary.is_favorite
    db.commit()
    db.refresh(summary)
    
    return SummaryResponse(
        id=summary.id,
        article_title=summary.article_title,
        article_text=summary.article_text,
        summary_text=summary.summary_text,
        algorithm_used=summary.algorithm_used,
        word_count_original=summary.word_count_original,
        word_count_summary=summary.word_count_summary,
        compression_ratio=summary.compression_ratio,
        is_favorite=summary.is_favorite,
        created_at=summary.created_at
    )


@router.delete("/{summary_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_summary(
    summary_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a summary."""
    
    summary = db.query(Summary).filter(
        Summary.id == summary_id,
        Summary.user_id == current_user.id
    ).first()
    
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Summary not found"
        )
    
    db.delete(summary)
    db.commit()
