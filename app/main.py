from fastapi import FastAPI
from app.database import get_connection
from app.routers import users
from app.routers import auth
from app.routers import admin_auth

app = FastAPI(
    title="Technical QA Lab",
    description="Technical QA 포트폴리오용 테스트 API",
    version="0.1.0"
    
)
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(admin_auth.router)

@app.get("/db-health")
def db_health_check():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT current_database(), current_user;")
            database, user = cursor.fetchone()

    return {
        "status": "ok",
        "database": database,
        "user": user,
    }

