from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field, field_validator


# ==================== Auth Schemas ====================
class UserRegister(BaseModel):
    """User registration request."""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    """User login request."""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenRefresh(BaseModel):
    """Token refresh request."""
    refresh_token: str


# ==================== User Schemas ====================
class UserProfile(BaseModel):
    """User profile response."""
    id: int
    email: str
    full_name: Optional[str]
    avatar_url: Optional[str]
    bio: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserProfileUpdate(BaseModel):
    """Update user profile."""
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None


# ==================== Quiz Schemas ====================
class QuizQuestion(BaseModel):
    """Single quiz question."""
    id: int
    question: str
    options: List[str]
    correct_answer: int
    user_answer: Optional[int] = None
    is_correct: Optional[bool] = None


class QuizSubmission(BaseModel):
    """Submit quiz answers."""
    article_title: Optional[str]
    article_text: str
    summary_text: Optional[str]
    questions: List[QuizQuestion]
    time_taken_seconds: int
    difficulty: str = "medium"
    category: Optional[str] = None
    language: str = "vi"


class QuizResult(BaseModel):
    """Quiz result response."""
    id: int
    score: int
    total_questions: int
    percentage_score: float
    time_taken_seconds: int
    difficulty: str
    category: Optional[str]
    created_at: datetime
    questions: List[QuizQuestion]
    
    class Config:
        from_attributes = True


class QuizHistoryItem(BaseModel):
    """Single quiz history item."""
    id: int
    article_title: Optional[str]
    percentage_score: float
    score: int
    total_questions: int
    difficulty: str
    category: Optional[str]
    time_taken_seconds: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class QuizHistoryList(BaseModel):
    """List of quiz histories."""
    total: int
    page: int
    page_size: int
    items: List[QuizHistoryItem]


# ==================== Summary Schemas ====================
class SummarySaveRequest(BaseModel):
    """Save summary request."""
    article_text: str
    article_title: Optional[str]
    summary_text: str
    source_url: Optional[str]
    source_type: str = "text"
    language: str = "vi"
    algorithm_used: str = "bilstm"


class SummaryResponse(BaseModel):
    """Summary response."""
    id: int
    article_title: Optional[str]
    article_text: str
    summary_text: str
    algorithm_used: str
    word_count_original: Optional[int]
    word_count_summary: Optional[int]
    compression_ratio: Optional[float]
    is_favorite: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class SummaryListResponse(BaseModel):
    """List of summaries."""
    total: int
    page: int
    page_size: int
    items: List[SummaryResponse]


# ==================== Bookmark Schemas ====================
class BookmarkCreate(BaseModel):
    """Create bookmark."""
    summary_id: Optional[int]
    article_title: Optional[str]
    article_url: Optional[str]
    article_text: Optional[str]
    notes: Optional[str]
    tags: Optional[List[str]]


class BookmarkResponse(BaseModel):
    """Bookmark response."""
    id: int
    article_title: Optional[str]
    article_url: Optional[str]
    notes: Optional[str]
    tags: Optional[List[str]]
    created_at: datetime
    
    class Config:
        from_attributes = True


# ==================== Analytics Schemas ====================
class DailyScore(BaseModel):
    """Daily average score."""
    date: str
    average_score: float
    quiz_count: int


class CategoryPerformance(BaseModel):
    """Category performance."""
    category: str
    average_score: float
    total_quizzes: int
    trend: float  # Positive = improving


class UserAnalyticsResponse(BaseModel):
    """User analytics response."""
    total_quizzes: int
    average_score: float
    total_reading_time_seconds: int
    best_category: Optional[str]
    weakest_category: Optional[str]
    best_score: float
    worst_score: float
    total_summaries_generated: int
    last_quiz_date: Optional[datetime]


class DashboardResponse(BaseModel):
    """Dashboard response."""
    user_profile: UserProfile
    analytics: UserAnalyticsResponse
    recent_quizzes: List[QuizHistoryItem]
    category_performance: List[CategoryPerformance]
    daily_progress: List[DailyScore]
    
    class Config:
        from_attributes = True


# ==================== Leaderboard Schemas ====================
class LeaderboardEntry(BaseModel):
    """Single leaderboard entry."""
    rank: int
    email: str
    full_name: Optional[str]
    avatar_url: Optional[str]
    average_score: float
    total_quizzes: int
    total_summaries: int
    
    class Config:
        from_attributes = True


class LeaderboardResponse(BaseModel):
    """Leaderboard response."""
    total_users: int
    entries: List[LeaderboardEntry]
    user_rank: Optional[int]


# ==================== Error Schemas ====================
class ErrorResponse(BaseModel):
    """Error response."""
    detail: str
    error_code: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
