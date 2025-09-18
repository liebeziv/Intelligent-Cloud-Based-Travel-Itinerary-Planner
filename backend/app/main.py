import app
import uuid
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse
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


@app.on_event("startup")
async def startup_event():
    # Database initialization
    db.init_db()

    # Initialize recommendation system
    try:
        from .api.routes.recommendations import recommendation_service
        from .data.sample_attractions import SAMPLE_NZ_ATTRACTIONS
        await recommendation_service.initialize(SAMPLE_NZ_ATTRACTIONS)
        print("Recommendation system initialized successfully")
    except Exception as e:
        print(f"Recommendation system initialization failed: {e}")

@app.post("/api/auth/register")
def register(payload: dict, dbs: Session = Depends(db.SessionLocal)):
    email = payload.get("email"); password = payload.get("password"); name = payload.get("name")
    if not email or not password:
        return JSONResponse({"detail":"email+password required"}, status_code=400)
    if dbs.query(models.User).filter_by(email=email).first():
        return JSONResponse({"detail":"email exists"}, status_code=400)
    user = auth.create_user(dbs, email, password, name)
    return {"id": user.id, "email": user.email}

@app.post("/api/auth/login")
def login(payload: dict, dbs: Session = Depends(db.SessionLocal)):
    email = payload.get("email"); password = payload.get("password")
    user = auth.authenticate_user(dbs, email, password)
    if not user:
        return JSONResponse({"detail":"invalid credentials"}, status_code=401)
    token = auth.create_access_token({"sub": user.id, "email": user.email})
    return {"access_token": token, "token_type": "bearer"}

@app.post("/api/itineraries")
def create_itinerary(payload: dict, current_user=Depends(auth.get_current_user), dbs: Session = Depends(db.SessionLocal)):
    import datetime
    it_id = str(uuid.uuid4())
    key = f"itineraries/{current_user.id}/{it_id}.json"
    obj = {"id": it_id, "owner": current_user.id, "title": payload.get("title"), "items": payload.get("items", []), "createdAt": datetime.datetime.utcnow().isoformat()}
    s3utils.put_json_object(key, obj)
    it = models.Itinerary(id=it_id, owner_id=current_user.id, title=payload.get("title"), s3_key=key)
    dbs.add(it); dbs.commit()
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

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "travel-planner-api"}
