# Task Manager

A full-stack Task Manager web application built with **FastAPI** (backend) and plain **HTML/CSS/JavaScript** (frontend).

## Features

- User registration and login with JWT authentication
- Password hashing using bcrypt
- Create, view, update, and delete tasks
- Mark tasks as completed
- Filter tasks by status (`?completed=true/false`)
- Pagination support
- SQLite database (easily switchable to PostgreSQL)
- Interactive API docs at `/docs`

---

## Project Structure

```
task-manager/
├── backend/
│   ├── main.py            # FastAPI app entry point
│   ├── database.py        # DB engine and session
│   ├── models.py          # SQLAlchemy models
│   ├── schemas.py         # Pydantic schemas
│   ├── auth.py            # JWT + bcrypt utilities
│   ├── routers/
│   │   ├── auth.py        # /register, /login
│   │   └── tasks.py       # /tasks CRUD
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── index.html         # Landing page
│   ├── register.html      # Registration form
│   ├── login.html         # Login form
│   ├── tasks.html         # Task dashboard
│   ├── api.js             # Shared fetch helper
│   └── style.css          # Styles
├── tests/
│   └── test_api.py        # pytest test suite
├── Dockerfile
└── README.md
```

---

## Environment Variables

Create a `.env` file inside the `backend/` folder based on `.env.example`:

```
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DATABASE_URL=sqlite:///./taskmanager.db
```

> **Never commit `.env` to version control.**

---

## Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/task-manager.git
cd task-manager
```

### 2. Set up the backend

```bash
cd backend
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env           # Edit SECRET_KEY
uvicorn main:app --reload
```

Backend runs at: http://localhost:8000  
API docs at: http://localhost:8000/docs

### 3. Open the frontend

The frontend is served by FastAPI at `http://localhost:8000/`.  
Or open `frontend/index.html` directly in your browser.

---

## Run Tests

```bash
cd backend
pytest ../tests/test_api.py -v
```

---

## Run with Docker

```bash
docker build -t task-manager .
docker run -p 8000:8000 --env-file backend/.env task-manager
```

---

## API Endpoints

| Method | Endpoint        | Auth | Description            |
|--------|-----------------|------|------------------------|
| POST   | /register       | No   | Register a new user    |
| POST   | /login          | No   | Login, get JWT token   |
| POST   | /tasks          | Yes  | Create a task          |
| GET    | /tasks          | Yes  | List tasks (paginated) |
| GET    | /tasks/{id}     | Yes  | Get a single task      |
| PUT    | /tasks/{id}     | Yes  | Update a task          |
| DELETE | /tasks/{id}     | Yes  | Delete a task          |
| GET    | /health         | No   | Health check           |

Query parameters for `GET /tasks`:
- `?completed=true` – filter completed tasks
- `?completed=false` – filter pending tasks
- `?page=1&page_size=10` – pagination

---

## Deployment (Render)

1. Push this repo to GitHub
2. Go to [render.com](https://render.com) → New Web Service
3. Connect your repo, set:
   - **Build command**: `pip install -r backend/requirements.txt`
   - **Start command**: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables in Render dashboard
5. Deploy!

Live demo: _your-render-link-here_
