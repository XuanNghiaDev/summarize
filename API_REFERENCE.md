# 📚 Complete API Reference

Comprehensive documentation of all API endpoints with request/response examples.

---

## Authentication Endpoints

### Register User
Create a new user account.

```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "full_name": "John Doe"
}
```

**Response (201 Created):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

**Error (409 Conflict):**
```json
{
  "detail": "Email already registered"
}
```

---

### Login User
Authenticate and receive JWT tokens.

```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

**Error (401 Unauthorized):**
```json
{
  "detail": "Invalid email or password"
}
```

---

### Refresh Token
Get a new access token using refresh token.

```http
POST /auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

---

### Logout
Invalidate current session (client-side token removal).

```http
POST /auth/logout
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "message": "Logged out successfully. Please discard tokens client-side."
}
```

---

## User Profile Endpoints

### Get Current User Profile
Retrieve authenticated user's profile information.

```http
GET /user/profile
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "avatar_url": "https://example.com/avatar.jpg",
  "bio": "AI enthusiast and learner",
  "created_at": "2024-01-15T10:00:00"
}
```

---

### Update User Profile
Update user's profile information.

```http
PUT /user/profile
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "full_name": "John Updated",
  "avatar_url": "https://example.com/new-avatar.jpg",
  "bio": "Updated bio"
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Updated",
  "avatar_url": "https://example.com/new-avatar.jpg",
  "bio": "Updated bio",
  "created_at": "2024-01-15T10:00:00"
}
```

---

### Get Public User Profile
View another user's public profile.

```http
GET /user/profile/{user_id}
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "id": 2,
  "email": "other@example.com",
  "full_name": "Jane Doe",
  "avatar_url": null,
  "bio": null,
  "created_at": "2024-01-20T15:30:00"
}
```

---

## Quiz Endpoints

### Submit Quiz
Submit quiz answers and save attempt.

```http
POST /quiz/submit
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "article_title": "Understanding AI",
  "article_text": "Artificial intelligence is...",
  "summary_text": "AI is a technology...",
  "questions": [
    {
      "id": 1,
      "question": "What does AI stand for?",
      "options": ["Artificial Intelligence", "Applied Innovation", "Advanced Interconnect", "Active Internet"],
      "correct_answer": 0,
      "user_answer": 0,
      "is_correct": true
    },
    {
      "id": 2,
      "question": "What is machine learning?",
      "options": ["Learning from machines", "Teaching AI to learn", "Automated algorithm design", "Computer learning paradigm"],
      "correct_answer": 3,
      "user_answer": 2,
      "is_correct": false
    }
  ],
  "time_taken_seconds": 300,
  "difficulty": "medium",
  "category": "Technology",
  "language": "en"
}
```

**Response (201 Created):**
```json
{
  "id": 42,
  "score": 1,
  "total_questions": 2,
  "percentage_score": 50.0,
  "time_taken_seconds": 300,
  "difficulty": "medium",
  "category": "Technology",
  "created_at": "2024-01-21T14:30:00",
  "questions": [...]
}
```

---

### Get Quiz History
Retrieve user's quiz attempt history with pagination.

```http
GET /quiz/history?page=1&page_size=10&difficulty=medium&category=Technology
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "total": 25,
  "page": 1,
  "page_size": 10,
  "items": [
    {
      "id": 42,
      "article_title": "Understanding AI",
      "percentage_score": 80.0,
      "score": 8,
      "total_questions": 10,
      "difficulty": "medium",
      "category": "Technology",
      "time_taken_seconds": 420,
      "created_at": "2024-01-21T14:30:00"
    }
  ]
}
```

---

### Get Quiz Details
Retrieve full details of a specific quiz attempt.

```http
GET /quiz/history/{quiz_id}
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "id": 42,
  "score": 8,
  "total_questions": 10,
  "percentage_score": 80.0,
  "time_taken_seconds": 420,
  "difficulty": "medium",
  "category": "Technology",
  "created_at": "2024-01-21T14:30:00",
  "questions": [
    {
      "id": 1,
      "question": "What is AI?",
      "options": ["..."],
      "correct_answer": 0,
      "user_answer": 0,
      "is_correct": true
    }
  ]
}
```

---

### Delete Quiz Record
Remove a quiz from history.

```http
DELETE /quiz/history/{quiz_id}
Authorization: Bearer <access_token>
```

**Response (204 No Content)**

---

## Summary Endpoints

### Save Summary
Save a generated summary.

```http
POST /summary/save
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "article_text": "Long article content here...",
  "article_title": "Article Title",
  "summary_text": "Short summarized version...",
  "source_url": "https://example.com/article",
  "source_type": "url",
  "language": "en",
  "algorithm_used": "bilstm"
}
```

**Response (201 Created):**
```json
{
  "id": 15,
  "article_title": "Article Title",
  "article_text": "Long article content here...",
  "summary_text": "Short summarized version...",
  "algorithm_used": "bilstm",
  "word_count_original": 500,
  "word_count_summary": 100,
  "compression_ratio": 0.8,
  "is_favorite": false,
  "created_at": "2024-01-21T14:30:00"
}
```

---

### Get Saved Summaries
Retrieve user's saved summaries with filters.

```http
GET /summary/list?page=1&page_size=10&language=en&algorithm=bilstm&is_favorite=false
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "total": 42,
  "page": 1,
  "page_size": 10,
  "items": [
    {
      "id": 15,
      "article_title": "Article Title",
      "article_text": "...",
      "summary_text": "...",
      "algorithm_used": "bilstm",
      "word_count_original": 500,
      "word_count_summary": 100,
      "compression_ratio": 0.8,
      "is_favorite": false,
      "created_at": "2024-01-21T14:30:00"
    }
  ]
}
```

---

### Get Summary Details
Retrieve a specific summary.

```http
GET /summary/{summary_id}
Authorization: Bearer <access_token>
```

**Response (200 OK):** (Same as individual summary object above)

---

### Toggle Summary Favorite
Mark/unmark a summary as favorite.

```http
PUT /summary/{summary_id}/favorite
Authorization: Bearer <access_token>
```

**Response (200 OK):** (Summary object with updated is_favorite)

---

### Delete Summary
Remove a saved summary.

```http
DELETE /summary/{summary_id}
Authorization: Bearer <access_token>
```

**Response (204 No Content)**

---

## Analytics Endpoints

### Get Dashboard
Complete dashboard data with all analytics.

```http
GET /analytics/dashboard
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "user_profile": {
    "id": 1,
    "email": "user@example.com",
    "full_name": "John Doe",
    "avatar_url": null,
    "bio": null,
    "created_at": "2024-01-15T10:00:00"
  },
  "analytics": {
    "total_quizzes": 25,
    "average_score": 82.5,
    "total_reading_time_seconds": 3600,
    "best_category": "Technology",
    "weakest_category": "Law",
    "best_score": 100.0,
    "worst_score": 60.0,
    "total_summaries_generated": 15,
    "last_quiz_date": "2024-01-21T14:30:00"
  },
  "recent_quizzes": [...],
  "category_performance": [...],
  "daily_progress": [...]
}
```

---

### Get User Analytics
Summary of user's performance metrics.

```http
GET /analytics/user
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "total_quizzes": 25,
  "average_score": 82.5,
  "total_reading_time_seconds": 3600,
  "best_category": "Technology",
  "weakest_category": "Law",
  "best_score": 100.0,
  "worst_score": 60.0,
  "total_summaries_generated": 15,
  "last_quiz_date": "2024-01-21T14:30:00"
}
```

---

### Get Category Performance
Performance breakdown by category.

```http
GET /analytics/performance/by-category
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "categories": [
    {
      "category": "Technology",
      "total_quizzes": 12,
      "average_score": 85.0,
      "best_score": 100.0,
      "worst_score": 70.0
    },
    {
      "category": "Science",
      "total_quizzes": 8,
      "average_score": 78.0,
      "best_score": 95.0,
      "worst_score": 60.0
    }
  ]
}
```

---

### Get Difficulty Performance
Performance breakdown by difficulty level.

```http
GET /analytics/performance/by-difficulty
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "difficulties": [
    {
      "difficulty": "easy",
      "total_quizzes": 10,
      "average_score": 92.0,
      "best_score": 100.0,
      "worst_score": 80.0
    },
    {
      "difficulty": "medium",
      "total_quizzes": 10,
      "average_score": 80.0,
      "best_score": 95.0,
      "worst_score": 65.0
    },
    {
      "difficulty": "hard",
      "total_quizzes": 5,
      "average_score": 70.0,
      "best_score": 85.0,
      "worst_score": 55.0
    }
  ]
}
```

---

### Get Daily Performance
Daily progress over specified period.

```http
GET /analytics/performance/daily?days=30
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "daily_stats": [
    {
      "date": "2024-01-01",
      "quiz_count": 2,
      "average_score": 85.0,
      "total_time_seconds": 600
    },
    {
      "date": "2024-01-02",
      "quiz_count": 1,
      "average_score": 75.0,
      "total_time_seconds": 300
    }
  ]
}
```

---

### Get Quiz Streak
Current and longest quiz streaks.

```http
GET /analytics/streak
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "current_streak": 5,
  "longest_streak": 12
}
```

---

## Leaderboard Endpoints

### Get Global Leaderboard
Top users ranked by default criteria.

```http
GET /leaderboard/?limit=50
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "total_users": 156,
  "user_rank": 12,
  "entries": [
    {
      "rank": 1,
      "email": "top@example.com",
      "full_name": "Top Learner",
      "avatar_url": "https://example.com/avatar.jpg",
      "average_score": 95.5,
      "total_quizzes": 150,
      "total_summaries": 120
    }
  ]
}
```

---

### Get Leaderboard by Score
Ranked by average score.

```http
GET /leaderboard/by-score?limit=50
Authorization: Bearer <access_token>
```

**Response (200 OK):** (Same structure as above)

---

### Get Leaderboard by Quiz Count
Ranked by number of quizzes completed.

```http
GET /leaderboard/by-quizzes?limit=50
Authorization: Bearer <access_token>
```

**Response (200 OK):** (Same structure as above)

---

## Bookmark Endpoints

### Create Bookmark
Save an article to bookmarks.

```http
POST /bookmarks
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "article_title": "Interesting Article",
  "article_url": "https://example.com/article",
  "notes": "Great read about AI",
  "tags": ["AI", "Learning", "Favorite"]
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "article_title": "Interesting Article",
  "article_url": "https://example.com/article",
  "notes": "Great read about AI",
  "tags": ["AI", "Learning", "Favorite"],
  "created_at": "2024-01-21T14:30:00"
}
```

---

### Get Bookmarks
Retrieve user's bookmarks with pagination.

```http
GET /bookmarks?page=1&page_size=20&tag=AI
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "article_title": "Interesting Article",
    "article_url": "https://example.com/article",
    "notes": "Great read about AI",
    "tags": ["AI", "Learning"],
    "created_at": "2024-01-21T14:30:00"
  }
]
```

---

### Update Bookmark
Modify bookmark details.

```http
PUT /bookmarks/{bookmark_id}
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "article_title": "Updated Title",
  "notes": "Updated notes",
  "tags": ["AI", "NewTag"]
}
```

**Response (200 OK):** (Updated bookmark object)

---

### Delete Bookmark
Remove a bookmark.

```http
DELETE /bookmarks/{bookmark_id}
Authorization: Bearer <access_token>
```

**Response (204 No Content)**

---

## Health & Status

### Health Check
System health status.

```http
GET /health
```

**Response (200 OK):**
```json
{
  "status": "healthy",
  "app": "AI Quiz & Summarization System",
  "version": "1.0.0"
}
```

---

## Error Responses

All errors follow this format:

```json
{
  "detail": "Error description",
  "error_code": "OPTIONAL_CODE",
  "timestamp": "2024-01-21T14:30:00"
}
```

### Common Error Codes

| Status | Code | Meaning |
|--------|------|---------|
| 400 | VALIDATION_ERROR | Invalid request data |
| 401 | UNAUTHORIZED | Missing or invalid token |
| 403 | FORBIDDEN | Insufficient permissions |
| 404 | NOT_FOUND | Resource not found |
| 409 | CONFLICT | Resource already exists |
| 500 | INTERNAL_ERROR | Server error |

---

## Request Headers

All requests should include:

```
Content-Type: application/json
Authorization: Bearer <access_token>  (for protected endpoints)
```

---

## Rate Limiting

Current implementation does not have rate limiting. For production, add:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@limiter.limit("100/minute")
@app.get("/endpoint")
async def endpoint():
    pass
```

---

## Pagination

Endpoints supporting pagination use:
- `page` (default: 1)
- `page_size` (default: 10, max: 100)

Response includes:
- `total` - Total number of items
- `page` - Current page number
- `page_size` - Items per page
- `items` - Array of items

---

**Last Updated:** January 2024  
**API Version:** 1.0.0
