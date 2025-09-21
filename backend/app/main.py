import os
import uuid
import datetime
from fastapi import FastAPI, Depends, HTTPException
from starlette.responses import JSONResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from . import auth, s3utils, sns_utils

IS_LOCAL_DEV = os.getenv("DEBUG", "False").lower() == "true"

if IS_LOCAL_DEV:
    from .local_utils import local_s3 as s3utils, local_sns as sns_utils
    print("🏠 Running in LOCAL DEVELOPMENT mode")
else:
    from . import s3utils, sns_utils
    print("☁️ Running in PRODUCTION mode")

# Importing recommender system routes
try:
    from .api.routes.recommendations import router as recommendation_router
    HAS_RECOMMENDATIONS = True
except ImportError:
    HAS_RECOMMENDATIONS = False
    print("⚠️ Recommendations module not available")

# FastAPI Instance
app = FastAPI(
    title="Intelligent cloud-based travel itinerary planner",
    description="AI-powered travel itinerary planner focused on New Zealand tourism",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include recommendation router if available
if HAS_RECOMMENDATIONS:
    app.include_router(recommendation_router)

# Pydantic Models
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
    
 
    if HAS_RECOMMENDATIONS:
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
def register(payload: RegisterRequest):
   
    try:
        existing_user = auth.authenticate_user(payload.email, "dummy_password")
        if existing_user:
            return JSONResponse({"detail": "email exists"}, status_code=400)
    except:
        pass  

    user = auth.create_user(payload.email, payload.password, payload.name)
    return {"id": user["id"], "email": user["email"], "name": user.get("name")}

@app.post("/api/auth/login")
def login(payload: LoginRequest):
    user = auth.authenticate_user(payload.email, payload.password)
    if not user:
        return JSONResponse({"detail": "invalid credentials"}, status_code=401)

    token = auth.create_access_token({"sub": user["id"], "email": user["email"]})
    return {"access_token": token, "token_type": "bearer"}

# Itinerary Endpoints
@app.post("/api/itineraries")
def create_itinerary(payload: ItineraryRequest, current_user=Depends(auth.get_current_user)):
    it_id = str(uuid.uuid4())
    key = f"itineraries/{current_user['id']}/{it_id}.json"
    obj = {
        "id": it_id,
        "owner": current_user['id'],
        "title": payload.title,
        "items": payload.items,
        "createdAt": datetime.datetime.utcnow().isoformat()
    }
    
    try:
        # Upload to S3
        s3utils.put_json_object(key, obj)
        # Send SNS notification
        sns_utils.publish(f"New itinerary {it_id} by {current_user['email']}", subject="Itinerary Created")
        return {"id": it_id, "s3_key": key}
    except Exception as e:
        print(f"Error creating itinerary: {e}")
        raise HTTPException(status_code=500, detail="Failed to create itinerary")

@app.get("/api/itineraries")
def get_itineraries(current_user=Depends(auth.get_current_user)):
    try:
    
        user_itineraries_prefix = f"itineraries/{current_user['id']}/"
        # itineraries = s3utils.list_objects_with_prefix(user_itineraries_prefix)
    
        return []
    except Exception as e:
        print(f"Error getting itineraries: {e}")
        return []

@app.get("/api/upload-url")
def upload_url(filename: str, current_user=Depends(auth.get_current_user)):
    try:
        key = f"uploads/{current_user['id']}/{uuid.uuid4()}_{filename}"
        url = s3utils.get_presigned_put_url(key)
        return {"url": url, "key": key}
    except Exception as e:
        print(f"Error generating upload URL: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate upload URL")

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