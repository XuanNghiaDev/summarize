from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, ForeignKey, JSON, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    """User account model."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    quiz_histories = relationship("QuizHistory", back_populates="user", cascade="all, delete-orphan")
    summaries = relationship("Summary", back_populates="user", cascade="all, delete-orphan")
    bookmarks = relationship("Bookmark", back_populates="user", cascade="all, delete-orphan")
    favorite_quizzes = relationship("FavoriteQuiz", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User {self.email}>"


class QuizHistory(Base):
    """Quiz attempt history for each user."""
    __tablename__ = "quiz_histories"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    article_title = Column(String(500), nullable=True)
    article_text = Column(Text, nullable=False)
    summary_text = Column(Text, nullable=True)
    quiz_json = Column(JSON, nullable=False)  # Store questions and user answers
    score = Column(Integer, nullable=False)  # e.g., 8 out of 10
    total_questions = Column(Integer, nullable=False)  # Total questions
    percentage_score = Column(Float, nullable=False)  # e.g., 80.0
    time_taken_seconds = Column(Integer, nullable=False)  # Time in seconds
    difficulty = Column(String(50), default="medium", index=True)  # easy, medium, hard
    category = Column(String(100), nullable=True, index=True)  # Technology, Law, etc.
    language = Column(String(10), default="vi")  # vi, en
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User", back_populates="quiz_histories")
    
    __table_args__ = (
        UniqueConstraint('user_id', 'created_at', name='unique_user_quiz_timestamp'),
    )
    
    def __repr__(self):
        return f"<QuizHistory user_id={self.user_id} score={self.percentage_score}%>"


class Summary(Base):
    """Saved summaries for users."""
    __tablename__ = "summaries"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    article_text = Column(Text, nullable=False)
    article_title = Column(String(500), nullable=True)
    summary_text = Column(Text, nullable=False)
    source_url = Column(String(500), nullable=True)
    source_type = Column(String(50), default="text")  # text, url, file
    language = Column(String(10), default="vi")
    algorithm_used = Column(String(50), default="bilstm")  # textrank, bilstm
    is_favorite = Column(Boolean, default=False)
    word_count_original = Column(Integer, nullable=True)
    word_count_summary = Column(Integer, nullable=True)
    compression_ratio = Column(Float, nullable=True)  # (original - summary) / original
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="summaries")
    
    def __repr__(self):
        return f"<Summary id={self.id} user_id={self.user_id}>"


class Bookmark(Base):
    """User bookmarked articles."""
    __tablename__ = "bookmarks"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    summary_id = Column(Integer, ForeignKey("summaries.id"), nullable=True)
    article_title = Column(String(500), nullable=True)
    article_url = Column(String(500), nullable=True)
    article_text = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    tags = Column(JSON, nullable=True)  # List of tags
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User", back_populates="bookmarks")
    
    __table_args__ = (
        UniqueConstraint('user_id', 'article_url', name='unique_user_bookmark_url'),
    )
    
    def __repr__(self):
        return f"<Bookmark user_id={self.user_id}>"


class FavoriteQuiz(Base):
    """User favorite quizzes."""
    __tablename__ = "favorite_quizzes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    quiz_history_id = Column(Integer, ForeignKey("quiz_histories.id"), nullable=True)
    quiz_title = Column(String(500), nullable=True)
    quiz_json = Column(JSON, nullable=False)  # Store quiz structure
    difficulty = Column(String(50), default="medium")
    category = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User", back_populates="favorite_quizzes")
    
    def __repr__(self):
        return f"<FavoriteQuiz user_id={self.user_id}>"


class UserAnalytics(Base):
    """Pre-computed analytics for quick dashboard queries."""
    __tablename__ = "user_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True)
    total_quizzes = Column(Integer, default=0)
    average_score = Column(Float, default=0.0)
    total_reading_time_seconds = Column(Integer, default=0)
    best_category = Column(String(100), nullable=True)
    weakest_category = Column(String(100), nullable=True)
    best_score = Column(Float, default=0.0)
    worst_score = Column(Float, default=0.0)
    total_summaries_generated = Column(Integer, default=0)
    last_quiz_date = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<UserAnalytics user_id={self.user_id}>"


class Leaderboard(Base):
    """Leaderboard rankings (updated periodically)."""
    __tablename__ = "leaderboard"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True)
    email = Column(String(255), nullable=False, index=True)
    full_name = Column(String(255), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    average_score = Column(Float, default=0.0, index=True)
    total_quizzes = Column(Integer, default=0, index=True)
    total_summaries = Column(Integer, default=0)
    rank = Column(Integer, default=0, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Leaderboard rank={self.rank} user_id={self.user_id}>"
