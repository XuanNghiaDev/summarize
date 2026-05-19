# ⚡ Quick Reference Card

## 🚀 Quick Start

### Start Backend
```bash
cd ai_core
source venv/bin/activate  
python main.py
```

### Start Frontend
```bash
cd frontend
npm run dev
```

### URLs
- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000`
- API Docs: `http://localhost:8000/api/docs`

---

## 🔑 Common API Patterns

### Get Token
```bash
# Register
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"Pass123!","full_name":"User"}'

# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"Pass123!"}'
```

### Use Token
```bash
curl -X GET http://localhost:8000/user/profile \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🗄️ Database Queries

### Connect
```bash
psql -U summarization_user -d summarization_db
```

### Useful Queries
```sql
-- Check users
SELECT id, email, full_name, created_at FROM users;

-- Check quiz history
SELECT id, user_id, percentage_score, difficulty, created_at FROM quiz_histories;

-- Check user stats
SELECT user_id, total_quizzes, average_score FROM user_analytics;

-- Top users
SELECT * FROM leaderboard ORDER BY rank LIMIT 10;
```

---

## 📁 Project Structure

```
summarization/
├── ai_core/          # Backend FastAPI
├── frontend/         # React Vite
├── data/            # Data files
├── models/          # ML models
├── outputs/         # Results
├── .env             # Config
├── setup.sh         # Linux setup
└── setup.bat        # Windows setup
```

---

## 📝 Key Files

| File | Purpose |
|------|---------|
| `ai_core/main.py` | FastAPI app entry |
| `ai_core/models.py` | Database models |
| `ai_core/auth.py` | JWT + password |
| `ai_core/routes/*.py` | API endpoints |
| `frontend/src/services/api.js` | API client |
| `frontend/src/pages/*.jsx` | React pages |
| `.env` | Configuration |

---

## 🔐 Authentication

### Token Expiry
- Access token: 24 hours
- Refresh token: 30 days

### Reset Password (Manual)
```python
from auth import AuthService
from models import User
from database import SessionLocal

db = SessionLocal()
user = db.query(User).filter(User.email == "test@test.com").first()
user.password_hash = AuthService.hash_password("NewPassword123!")
db.commit()
```

---

## 🐛 Common Issues

### Issue: "Module not found"
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: Database connection failed
```bash
# Check PostgreSQL
sudo systemctl status postgresql

# Check connection
psql -U summarization_user -d summarization_db
```

### Issue: Port already in use
```bash
# Find and kill process
lsof -i :8000
kill -9 <PID>
```

### Issue: CORS error
```python
# Update CORS_ORIGINS in .env
CORS_ORIGINS=http://localhost:5173
```

---

## 📊 API Endpoints by Category

### Auth (4)
- POST `/auth/register`
- POST `/auth/login`
- POST `/auth/refresh`
- POST `/auth/logout`

### User (3)
- GET `/user/profile`
- PUT `/user/profile`
- GET `/user/profile/{id}`

### Quiz (5)
- POST `/quiz/submit`
- GET `/quiz/history`
- GET `/quiz/history/{id}`
- DELETE `/quiz/history/{id}`

### Summary (5)
- POST `/summary/save`
- GET `/summary/list`
- GET `/summary/{id}`
- PUT `/summary/{id}/favorite`
- DELETE `/summary/{id}`

### Analytics (7)
- GET `/analytics/dashboard`
- GET `/analytics/user`
- GET `/analytics/performance/by-category`
- GET `/analytics/performance/by-difficulty`
- GET `/analytics/performance/daily`
- GET `/analytics/streak`

### Leaderboard (4)
- GET `/leaderboard/`
- GET `/leaderboard/by-score`
- GET `/leaderboard/by-quizzes`
- POST `/leaderboard/rebuild`

### Bookmarks (5)
- POST `/bookmarks`
- GET `/bookmarks`
- GET `/bookmarks/{id}`
- PUT `/bookmarks/{id}`
- DELETE `/bookmarks/{id}`

---

## 🛠️ Development Commands

### Backend
```bash
cd ai_core

# Activate venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run server
python main.py

# Initialize database
python -c "from database import init_db; init_db()"

# Create migration
alembic revision --autogenerate -m "Description"

# Apply migration
alembic upgrade head
```

### Frontend
```bash
cd frontend

# Install
npm install

# Dev server
npm run dev

# Build
npm run build

# Preview build
npm run preview
```

---

## 🔍 Debugging

### Backend Debugging
```python
# In FastAPI route
import logging
logger = logging.getLogger(__name__)
logger.info("User login: %s", user_id)
logger.error("Error: %s", str(e))
```

### Frontend Debugging
```javascript
// Browser console
console.log("Data:", data);
console.error("Error:", error);

// React DevTools
// Install extension and inspect components
```

### Database Debugging
```bash
# Enable query logging
# In config.py, set DEBUG=True
# In database.py, set echo=True

# View slow queries
# In PostgreSQL
SELECT query, mean_time FROM pg_stat_statements 
WHERE mean_time > 100 
ORDER BY mean_time DESC;
```

---

## 📊 Sample Data for Testing

### Test User
```json
{
  "email": "test@example.com",
  "password": "TestPass123!",
  "full_name": "Test User"
}
```

### Test Quiz
```json
{
  "article_title": "Test Article",
  "article_text": "This is test content...",
  "questions": [{
    "id": 1,
    "question": "What is this?",
    "options": ["A", "B", "C", "D"],
    "correct_answer": 0,
    "user_answer": 0,
    "is_correct": true
  }],
  "time_taken_seconds": 300,
  "difficulty": "medium",
  "category": "Test"
}
```

---

## 🌐 Environment Variables

```env
# Must Set
DATABASE_URL=postgresql://user:pass@host/db
JWT_SECRET_KEY=min-32-character-secret-key

# Optional (Defaults Below)
DEBUG=False
APP_NAME=AI Quiz & Summarization System
JWT_EXPIRATION_HOURS=24
CORS_ORIGINS=http://localhost:5173
```

---

## 📈 Performance Tips

### Database
- Use pagination (max 100)
- Add indexes on frequent filters
- Use JSONB for complex data
- Vacuum regularly

### Backend
- Use async routes
- Cache frequently accessed data
- Limit query results
- Use connection pooling

### Frontend
- Code splitting with lazy()
- Memoize expensive calculations
- Debounce API calls
- Cache API responses

---

## 🚀 Deployment Checklist

- [ ] Change JWT_SECRET_KEY
- [ ] Set DEBUG=False
- [ ] Update DATABASE_URL
- [ ] Configure CORS_ORIGINS
- [ ] Update API_BASE_URL in frontend
- [ ] Enable HTTPS
- [ ] Set up database backups
- [ ] Enable monitoring
- [ ] Configure error tracking
- [ ] Set up logging

---

## 📞 Getting Help

1. Check **SYSTEM_DOCS.md** - Architecture overview
2. Check **IMPLEMENTATION_GUIDE.md** - Setup guide
3. Check **API_REFERENCE.md** - API documentation
4. Check browser console for frontend errors
5. Check `journalctl -u summarization-api` for backend errors
6. Check PostgreSQL logs for database errors

---

## 🎯 Common Tasks

### Add New API Endpoint
1. Create function in `routes/*.py`
2. Add Pydantic schema in `schemas.py`
3. Import and include router in `main.py`
4. Test with curl or Swagger UI

### Add New Database Field
1. Update model in `models.py`
2. Create Alembic migration
3. Update related schemas in `schemas.py`
4. Update API endpoint if needed

### Create New React Page
1. Create component in `pages/`
2. Add route in `App.jsx`
3. Import API functions from `services/api.js`
4. Use `useAuth()` for authentication
5. Style with Tailwind

---

## 🔗 Useful Links

- FastAPI Docs: https://fastapi.tiangolo.com/
- SQLAlchemy: https://docs.sqlalchemy.org/
- React Docs: https://react.dev/
- PostgreSQL: https://www.postgresql.org/docs/
- JWT: https://jwt.io/
- Bcrypt: https://github.com/pyca/bcrypt

---

**Last Updated:** January 2024  
**Version:** 1.0.0

*Keep this as a quick reference while developing!*
