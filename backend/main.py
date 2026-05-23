from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from database import engine
import models
from routers import auth, tasks

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Task Manager API",
    description="A simple Task Manager REST API with JWT authentication",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(tasks.router)

frontend_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "frontend")
)

if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")

    @app.get("/", include_in_schema=False)
    def serve_index():
        return FileResponse(os.path.join(frontend_path, "index.html"))

    @app.get("/register.html", include_in_schema=False)
    def serve_register():
        return FileResponse(os.path.join(frontend_path, "register.html"))

    @app.get("/login.html", include_in_schema=False)
    def serve_login():
        return FileResponse(os.path.join(frontend_path, "login.html"))

    @app.get("/tasks.html", include_in_schema=False)
    def serve_tasks():
        return FileResponse(os.path.join(frontend_path, "tasks.html"))

    @app.get("/style.css", include_in_schema=False)
    def serve_css():
        return FileResponse(os.path.join(frontend_path, "style.css"))

    @app.get("/api.js", include_in_schema=False)
    def serve_js():
        return FileResponse(os.path.join(frontend_path, "api.js"))


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}
