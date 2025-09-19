import os
import uuid
import datetime
from fastapi import FastAPI, Depends, HTTPException
from starlette.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from . import db, auth, s3utils, sns_utils, models
from fastapi.middleware.cors import CORSMiddleware

IS_LOCAL_DEV = os.getenv("DEBUG", "False").lower() == "true"

if IS_LOCAL_DEV:
    from .local_utils import local_s3 as s3utils, local_sns as sns_utils
    print("🏠 Running in LOCAL DEVELOPMENT mode")
else:
    from . import s3utils, sns_utils
    print("☁️ Running in PRODUCTION mode")

# Importing recommender system routes
from .api.routes.recommendations import router as recommendation_router
# FastAPI Instance
app = FastAPI(
    title="Intelligent cloud-based travel itinerary planner",
    description="AI-powered travel itinerary planner focused on New Zealand tourism",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)



# Recommended System Route
app.include_router(recommendation_router)

# Startup

class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str = None  

class LoginRequest(BaseModel):
    email: str
    password: str

class ItineraryRequest(BaseModel):
    title: str
    items: list = []  


@app.on_event("startup")
async def startup_event():
    print("🚀 Starting Travel Planner API...")
    
    db.init_db()
    
    try:
        from app.api.routes.recommendations import recommendation_service
        from app.data.sample_attractions import SAMPLE_NZ_ATTRACTIONS
        await recommendation_service.initialize(SAMPLE_NZ_ATTRACTIONS)
        print("✅ Recommendation system initialized")
    except Exception as e:
        print(f"⚠️ Recommendation system failed: {e}")
    
    print("✅ API startup completed")
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

@app.get("/api/itineraries")
def get_itineraries(current_user=Depends(auth.get_current_user), dbs: Session = Depends(db.get_db)):
    # Get all itineraries for the current user from DB
    itineraries = dbs.query(models.Itinerary).filter(models.Itinerary.owner_id == current_user.id).all()
    
    result = []
    for it in itineraries:
        try:
            # Get the full itinerary data from S3
            data = s3utils.get_json_object(it.s3_key)
            if data:
                result.append({
                    "id": it.id,
                    "title": it.title,
                    "items": data.get("items", []),
                    "createdAt": data.get("createdAt")
                })
        except Exception as e:
            print(f"Error loading itinerary {it.id}: {e}")
            # Include basic info even if S3 fetch fails
            result.append({
                "id": it.id,
                "title": it.title,
                "items": [],
                "createdAt": None
            })
    
    return result

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


