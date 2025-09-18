import app
import uuid
import datetime
from fastapi import FastAPI, Depends, HTTPException
from starlette.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from . import db, auth, s3utils, sns_utils, models

# Importing recommender system routes
from .api.routes.recommendations import router as recommendation_router
# FastAPI Instance
app = FastAPI(
    title="Intelligent cloud-based travel itinerary planner",
    description="AI-powered travel itinerary planner focused on New Zealand tourism",
    version="1.0.0"
)

# Recommended System Route
app.include_router(recommendation_router)

# Startup
@app.on_event("startup")
def startup_event():
    db.init_db()

# Pydantic Models
class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str | None = None

class LoginRequest(BaseModel):
    email: str
    password: str

class ItineraryRequest(BaseModel):
    title: str
    items: list[str] = []

# Auth Endpoints
@app.post("/api/auth/register")
def register(payload: RegisterRequest, dbs: Session = Depends(db.get_db)):
    existing_user = dbs.query(models.User).filter(models.User.email == payload.email).first()
    if existing_user:
        return JSONResponse({"detail": "email exists"}, status_code=400)

    user = auth.create_user(dbs, payload.email, payload.password, payload.name)
    return {"id": user.id, "email": user.email, "name": user.name}

@app.post("/api/auth/login")
def login(payload: LoginRequest, dbs: Session = Depends(db.get_db)):
    user = auth.authenticate_user(dbs, payload.email, payload.password)
    if not user:
        return JSONResponse({"detail": "invalid credentials"}, status_code=401)

    token = auth.create_access_token({"sub": user.id, "email": user.email})
    return {"access_token": token, "token_type": "bearer"}

# Itinerary Endpoints
@app.post("/api/itineraries")
def create_itinerary(payload: ItineraryRequest, current_user=Depends(auth.get_current_user), dbs: Session = Depends(db.get_db)):
    it_id = str(uuid.uuid4())
    key = f"itineraries/{current_user.id}/{it_id}.json"
    obj = {
        "id": it_id,
        "owner": current_user.id,
        "title": payload.title,
        "items": payload.items,
        "createdAt": datetime.datetime.utcnow().isoformat()
    }
    # Upload to S3
    s3utils.put_json_object(key, obj)
    # Save metadata to DB
    it = models.Itinerary(id=it_id, owner_id=current_user.id, title=payload.title, s3_key=key)
    dbs.add(it)
    dbs.commit()
    # Send SNS notification
    sns_utils.publish(f"New itinerary {it_id} by {current_user.email}", subject="Itinerary Created")
    return {"id": it_id, "s3_key": key}

@app.get("/api/upload-url")
def upload_url(filename: str, current_user=Depends(auth.get_current_user)):
    key = f"uploads/{current_user.id}/{uuid.uuid4()}_{filename}"
    url = s3utils.get_presigned_put_url(key)
    return {"url": url, "key": key}

@app.get("/")
def read_root():
    return {
        "message": "Intelligent cloud-based travel itinerary planner API",
        "version": "1.0.0",
        "features": ["User Authentication", "Itinerary Management", "AI Recommendation System", "File Upload"],
        "docs": "/docs"
    }

#Health Check
@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "travel-planner-api"}
