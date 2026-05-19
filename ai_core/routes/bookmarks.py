from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from database import get_db
from models import User, Bookmark, Summary
from schemas import BookmarkCreate, BookmarkResponse
from auth import get_current_user

router = APIRouter(prefix="/bookmarks", tags=["Bookmarks"])


@router.post("/", response_model=BookmarkResponse, status_code=status.HTTP_201_CREATED)
async def create_bookmark(
    bookmark_data: BookmarkCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new bookmark."""
    
    # Check if bookmark already exists
    if bookmark_data.article_url:
        existing = db.query(Bookmark).filter(
            Bookmark.user_id == current_user.id,
            Bookmark.article_url == bookmark_data.article_url
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This article is already bookmarked"
            )
    
    # Create bookmark
    bookmark = Bookmark(
        user_id=current_user.id,
        summary_id=bookmark_data.summary_id,
        article_title=bookmark_data.article_title,
        article_url=bookmark_data.article_url,
        article_text=bookmark_data.article_text,
        notes=bookmark_data.notes,
        tags=bookmark_data.tags or []
    )
    
    db.add(bookmark)
    db.commit()
    db.refresh(bookmark)
    
    return BookmarkResponse(
        id=bookmark.id,
        article_title=bookmark.article_title,
        article_url=bookmark.article_url,
        notes=bookmark.notes,
        tags=bookmark.tags,
        created_at=bookmark.created_at
    )


@router.get("/", response_model=list[BookmarkResponse])
async def get_bookmarks(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    tag: str = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's bookmarks."""
    
    query = db.query(Bookmark).filter(Bookmark.user_id == current_user.id)
    
    # Filter by tag if provided
    if tag:
        query = query.filter(Bookmark.tags.contains([tag]))
    
    # Pagination
    skip = (page - 1) * page_size
    bookmarks = query.order_by(desc(Bookmark.created_at)).offset(skip).limit(page_size).all()
    
    return [
        BookmarkResponse(
            id=b.id,
            article_title=b.article_title,
            article_url=b.article_url,
            notes=b.notes,
            tags=b.tags,
            created_at=b.created_at
        )
        for b in bookmarks
    ]


@router.get("/{bookmark_id}", response_model=BookmarkResponse)
async def get_bookmark(
    bookmark_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific bookmark."""
    
    bookmark = db.query(Bookmark).filter(
        Bookmark.id == bookmark_id,
        Bookmark.user_id == current_user.id
    ).first()
    
    if not bookmark:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bookmark not found"
        )
    
    return BookmarkResponse(
        id=bookmark.id,
        article_title=bookmark.article_title,
        article_url=bookmark.article_url,
        notes=bookmark.notes,
        tags=bookmark.tags,
        created_at=bookmark.created_at
    )


@router.put("/{bookmark_id}", response_model=BookmarkResponse)
async def update_bookmark(
    bookmark_id: int,
    bookmark_data: BookmarkCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a bookmark."""
    
    bookmark = db.query(Bookmark).filter(
        Bookmark.id == bookmark_id,
        Bookmark.user_id == current_user.id
    ).first()
    
    if not bookmark:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bookmark not found"
        )
    
    if bookmark_data.article_title is not None:
        bookmark.article_title = bookmark_data.article_title
    
    if bookmark_data.notes is not None:
        bookmark.notes = bookmark_data.notes
    
    if bookmark_data.tags is not None:
        bookmark.tags = bookmark_data.tags
    
    db.commit()
    db.refresh(bookmark)
    
    return BookmarkResponse(
        id=bookmark.id,
        article_title=bookmark.article_title,
        article_url=bookmark.article_url,
        notes=bookmark.notes,
        tags=bookmark.tags,
        created_at=bookmark.created_at
    )


@router.delete("/{bookmark_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_bookmark(
    bookmark_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a bookmark."""
    
    bookmark = db.query(Bookmark).filter(
        Bookmark.id == bookmark_id,
        Bookmark.user_id == current_user.id
    ).first()
    
    if not bookmark:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bookmark not found"
        )
    
    db.delete(bookmark)
    db.commit()
