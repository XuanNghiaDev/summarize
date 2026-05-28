# 🎓 AI Quiz + Article Summarization System

A production-ready full-stack application for AI-powered article summarization and quiz generation with advanced learning analytics and global leaderboard.

## 🌟 Features

### Core Features
- ✅ **User Authentication** - Secure JWT-based auth with refresh tokens
- ✅ **Article Summarization** - Extractive algorithms (TextRank, BiLSTM)
- ✅ **AI Quiz Generation** - Automatic multiple-choice quiz creation from summaries
- ✅ **Quiz History** - Track all quiz attempts with detailed statistics
- ✅ **Learning Analytics** - Comprehensive dashboard with performance metrics
- ✅ **Global Leaderboard** - Real-time rankings by score and activity
- ✅ **Bookmarks & Favorites** - Save articles and important quizzes
- ✅ **User Profiles** - Customizable user accounts with statistics

### Advanced Features
- 📊 Daily progress tracking
- 📈 Category-wise performance analysis  
- 🎯 Difficulty-level metrics
- 🔔 Learning streak tracking
- 💾 Summary export functionality
- 🌍 Multi-language support (Vietnamese, English)
- 📱 Responsive SaaS-style UI

---

## 🏗️ Architecture

### Tech Stack

```
Frontend:
├── React 18+ (with Vite)
├── React Router for navigation
├── Tailwind CSS for styling
└── Axios for API calls

Backend:
├── FastAPI (Python async framework)
├── SQLAlchemy ORM
├── PostgreSQL database
├── JWT authentication
└── Pydantic for validation

ML/NLP:
├── PyTorch for deep learning
├── Scikit-learn for ML utilities
├── TextRank for extractive summarization
├── ROUGE for evaluation
└── Underthesea for Vietnamese NLP
```

### Database Schema

```
Users
├── id (PK)
├── email (unique)
├── password_hash
├── full_name
├── avatar_url
└── created_at

QuizHistory
├── id (PK)
├── user_id (FK)
├── article_text
├── summary_text
├── quiz_json (JSONB)
├── score
├── percentage_score
├── time_taken_seconds
├── difficulty
├── category
└── created_at

Summaries
├── id (PK)
├── user_id (FK)
├── article_text
├── summary_text
├── algorithm_used
├── word_count_original
├── word_count_summary
├── compression_ratio
├── is_favorite
└── created_at

UserAnalytics
├── id (PK)
├── user_id (FK, unique)
├── total_quizzes
├── average_score
├── total_reading_time_seconds
├── best_category
├── weakest_category
└── updated_at

Leaderboard
├── id (PK)
├── user_id (FK, unique)
├── email
├── full_name
├── average_score
├── total_quizzes
├── rank
└── updated_at

Bookmarks
├── id (PK)
├── user_id (FK)
├── article_title
├── article_url
├── notes
├── tags (JSON array)
└── created_at
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+
- PostgreSQL 12+
- Git

### Backend Setup

```bash
# Navigate to AI core directory
cd ai_core

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
# Edit .env file with your PostgreSQL credentials
cp .env.example .env

# Initialize database
python -c "from database import init_db; init_db()"

# Run FastAPI server
python main.py
```

Server runs at: `http://localhost:8000`
API Docs: `http://localhost:8000/api/docs`

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Configure API base URL (optional)
# Create .env.local:
VITE_API_BASE_URL=http://localhost:8000

# Run development server
npm run dev
```

Frontend runs at: `http://localhost:5173`

---

## 🔐 Authentication Flow

### Registration
```bash
POST /auth/register
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "full_name": "John Doe"
}

Response:
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

### Login
```bash
POST /auth/login
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

### Token Refresh
```bash
POST /auth/refresh
{
  "refresh_token": "eyJhbGc..."
}
```

### Authorization
All protected endpoints require:
```
Authorization: Bearer <access_token>
```

---

## 📚 API Endpoints

### Authentication (`/auth`)
- `POST /auth/register` - Register new user
- `POST /auth/login` - User login
- `POST /auth/refresh` - Refresh access token
- `POST /auth/logout` - User logout

### User Profile (`/user`)
- `GET /user/profile` - Get current user profile
- `PUT /user/profile` - Update user profile
- `GET /user/profile/{user_id}` - Get public user profile

### Quizzes (`/quiz`)
- `POST /quiz/submit` - Submit quiz answers
- `GET /quiz/history` - Get quiz history (paginated)
- `GET /quiz/history/{quiz_id}` - Get quiz details
- `DELETE /quiz/history/{quiz_id}` - Delete quiz record

### Summaries (`/summary`)
- `POST /summary/save` - Save generated summary
- `GET /summary/list` - Get user's summaries (paginated)
- `GET /summary/{summary_id}` - Get summary details
- `PUT /summary/{summary_id}/favorite` - Toggle favorite
- `DELETE /summary/{summary_id}` - Delete summary

### Analytics (`/analytics`)
- `GET /analytics/dashboard` - Complete dashboard data
- `GET /analytics/user` - User analytics summary
- `GET /analytics/performance/by-category` - Category performance
- `GET /analytics/performance/by-difficulty` - Difficulty stats
- `GET /analytics/performance/daily` - Daily progress
- `GET /analytics/streak` - Quiz streak info

### Leaderboard (`/leaderboard`)
- `GET /leaderboard/` - Global leaderboard
- `GET /leaderboard/by-score` - Ranked by average score
- `GET /leaderboard/by-quizzes` - Ranked by quiz count
- `POST /leaderboard/rebuild` - Rebuild rankings

### Bookmarks (`/bookmarks`)
- `POST /bookmarks` - Create bookmark
- `GET /bookmarks` - Get user's bookmarks
- `GET /bookmarks/{bookmark_id}` - Get bookmark details
- `PUT /bookmarks/{bookmark_id}` - Update bookmark
- `DELETE /bookmarks/{bookmark_id}` - Delete bookmark

---

## 🎯 Frontend Routes

```
/                    - Home page
/login               - Login page
/register            - Registration page
/dashboard           - User dashboard (protected)
/quiz                - Take quiz
/quiz/:id            - Quiz detail
/quiz-history        - Quiz history
/summaries           - Saved summaries
/leaderboard         - Global leaderboard
/profile             - User profile (protected)
/bookmarks           - Saved bookmarks (protected)
```

---

## 💾 Database Migration

Using Alembic for migrations:

```bash
# Create migration
alembic revision --autogenerate -m "Add new column"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

---

## 📊 Example Responses

### Dashboard Response
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
    "best_score": 95,
    "worst_score": 65,
    "total_summaries_generated": 15,
    "last_quiz_date": "2024-01-20T14:30:00"
  },
  "recent_quizzes": [...],
  "category_performance": [...],
  "daily_progress": [...]
}
```

### Quiz Submission Response
```json
{
  "id": 42,
  "score": 8,
  "total_questions": 10,
  "percentage_score": 80.0,
  "time_taken_seconds": 180,
  "difficulty": "medium",
  "category": "Technology",
  "created_at": "2024-01-20T14:35:00",
  "questions": [...]
}
```

### Leaderboard Response
```json
{
  "total_users": 156,
  "user_rank": 12,
  "entries": [
    {
      "rank": 1,
      "email": "top@example.com",
      "full_name": "Top Learner",
      "avatar_url": "https://...",
      "average_score": 95.2,
      "total_quizzes": 127,
      "total_summaries": 89
    }
  ]
}
```

---

## 🔧 Configuration

### Environment Variables (`.env`)

```env
# FastAPI
DEBUG=True
APP_NAME="AI Quiz & Summarization System"
APP_VERSION="1.0.0"

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/summarization_db

# JWT
JWT_SECRET_KEY=your-super-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
JWT_REFRESH_EXPIRATION_DAYS=30

# Summarization
SUMMARY_MAX_SENTENCES=5
DEFAULT_LANGUAGE=vi

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

---

## 🧪 Testing

### Backend Tests
```bash
# Install pytest
pip install pytest pytest-asyncio

# Run tests
pytest ai_core/tests/

# With coverage
pytest --cov=ai_core/
```

### Frontend Tests
```bash
# Run tests
npm run test

# With coverage
npm run test:coverage
```

---

## 📈 Performance Optimization

### Backend
- Database indexes on `user_id`, `created_at`, `category`
- Query pagination (limit 100 records max)
- Connection pooling (pool_size=10, max_overflow=20)
- JWT caching (short-lived access tokens)

### Frontend
- Code splitting with React.lazy()
- Image optimization
- CSS minification (Tailwind purge)
- API response caching

---

## 🔒 Security Checklist

- ✅ JWT secret key in environment variables
- ✅ Password hashing with bcrypt (salt rounds: 10+)
- ✅ CORS properly configured
- ✅ SQL injection prevention (SQLAlchemy ORM)
- ✅ Rate limiting (implement with FastAPI middleware)
- ✅ HTTPS in production
- ✅ Database backups
- ✅ Dependency updates

---

## 📝 Logging

### Backend Logging
```python
import logging

logger = logging.getLogger(__name__)
logger.info("User login: %s", user_id)
logger.error("Quiz submission failed: %s", error)
```

### Frontend Error Tracking
```javascript
// Implement Sentry or similar service
import * as Sentry from "@sentry/react";

Sentry.init({
  dsn: "YOUR_SENTRY_DSN"
});
```

---

## 🚢 Deployment

### Docker Deployment

#### Backend Dockerfile
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Docker Compose
```yaml
version: '3.8'
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: password
  
  backend:
    build: ./ai_core
    ports:
      - "8000:8000"
    depends_on:
      - db
  
  frontend:
    build: ./frontend
    ports:
      - "5173:5173"
```

### Production Checklist
- [ ] SSL/TLS certificates
- [ ] Environment secrets management
- [ ] Database backups scheduled
- [ ] Monitoring & alerting
- [ ] Log aggregation
- [ ] CDN for static assets
- [ ] Load balancing
- [ ] Rate limiting

---

## 🐛 Troubleshooting

### Backend Issues

**PostgreSQL Connection Error**
```bash
# Check database running
psql -U user -d summarization_db -c "SELECT 1"

# Reset database
alembic downgrade base
alembic upgrade head
```

**JWT Token Invalid**
- Ensure JWT_SECRET_KEY is the same across restarts
- Check token expiration: `JWT_EXPIRATION_HOURS`

### Frontend Issues

**API Connection Failed**
- Check backend is running: `http://localhost:8000/health`
- Verify CORS settings in backend
- Check browser console for details

**Auth Token Lost**
- Clear browser localStorage
- Logout and login again

---

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)
- [PostgreSQL Docs](https://www.postgresql.org/docs/)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)

---

## 📄 License

MIT License - Free for personal and commercial use

---

## 👥 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

---

## 📞 Support

For issues and questions:
- GitHub Issues: [Create issue]
- Email: support@example.com
- Discord: [Join community]

---

**Built with ❤️ for learners everywhere** 🎓
