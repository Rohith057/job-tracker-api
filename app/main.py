from fastapi import FastAPI
from app.database import Base, engine
from app.routes import users, applications

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Job Application Tracker API")

app.include_router(users.router)
app.include_router(applications.router)


@app.get("/")
def root():
    return {"message": "Job Application Tracker API is running"}