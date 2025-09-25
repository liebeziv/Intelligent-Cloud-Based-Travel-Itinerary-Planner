import os
import sys
import uuid
import datetime
import logging
import traceback
from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette.responses import JSONResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

from app.api.routes.recommendations import init_recommendation_service, recommendation_service
from app.aws_services import aws_services
from app.schemas.itinerary import ItineraryPlanRequest, ItineraryPlan
from app.schemas.recommendation import RecommendationRequest
from app.services.dynamodb_repository import itinerary_repository
from app.services.itinerary_planner import itinerary_planner
from app.services.notification_service import notification_service
from app.services.attraction_service import attraction_service


log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(
    level=logging.INFO,
    format=log_format,
    handlers=[
        logging.StreamHandler(sys.stdout),  
        logging.FileHandler('/tmp/app.log', mode='w')  
    ]
)

logger = logging.getLogger(__name__)


logger.info("="*60)
logger.info("TRAVEL PLANNER API STARTUP")
logger.info("="*60)
logger.info(f"Python version: {sys.version}")
logger.info(f"Current working directory: {os.getcwd()}")
logger.info(f"Environment variables: PORT={os.environ.get('PORT', 'not set')}")
logger.info(f"Python path: {sys.path}")


sys.path.append(os.path.dirname(os.path.abspath(__file__)))
logger.info("Added current directory to Python path")

print("Starting Travel Planner API in production mode")
logger.info("Starting Travel Planner API in production mode")


auth = None
s3utils = None
sns_utils = None

try:
    # Use absolute package imports to ensure correctness under Gunicorn/EB
    from app import auth
    from app import s3utils
    from app import sns_utils
    logger.info("? Core modules loaded successfully")
    print("Core modules loaded successfully")
except ImportError as e:
    logger.error(f"? Failed to import core modules: {e}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    print(f"Warning: Failed to import core modules: {e}")
  
    class MockAuth:
        def authenticate_user(self, email, password): 
            logger.info(f"MockAuth: authenticate_user called for {email}")
            return None
        def create_user(self, email, password, name): 
            logger.info(f"MockAuth: create_user called for {email}")
            return {"id": "mock", "email": email, "name": name}
        def create_access_token(self, data): 
            logger.info("MockAuth: create_access_token called")
            return "mock_token"
        def get_current_user(self): 
            logger.info("MockAuth: get_current_user called")
            return {"id": "mock", "email": "mock@test.com"}
    
    class MockS3:
        def put_json_object(self, key, obj): 
            logger.info(f"MockS3: put_json_object called with key {key}")
            pass
        def get_presigned_put_url(self, key): 
            logger.info(f"MockS3: get_presigned_put_url called with key {key}")
            return "mock_url"
    
    class MockSNS:
        def publish(self, message, subject=""): 
            logger.info(f"MockSNS: publish called with message: {message}")
            pass
    
    auth = MockAuth()
    s3utils = MockS3()
    sns_utils = MockSNS()
    logger.info("? Mock modules created successfully")

optional_security = HTTPBearer(auto_error=False)

async def get_optional_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(optional_security)):
    if not credentials:
        return None
    try:
        return auth.get_current_user(credentials)
    except HTTPException:
        return None



HAS_RECOMMENDATIONS = False
try:
    from app.api.routes.recommendations import router as recommendation_router
    HAS_RECOMMENDATIONS = True
    logger.info("? Recommendations module loaded successfully")
    print("Recommendations module loaded successfully")
except ImportError as e:
    HAS_RECOMMENDATIONS = False
    logger.warning(f"Recommendations module not available: {e}")
    print(f"Warning: Recommendations module not available: {e}")


logger.info("Creating FastAPI instance...")
app = FastAPI(
    title="Intelligent cloud-based travel itinerary planner",
    description="AI-powered travel itinerary planner focused on New Zealand tourism",
    version="1.0.0"
)
logger.info("? FastAPI instance created")


def _populate_app_state(fastapi_app: FastAPI) -> None:
    fastapi_app.state.aws_region = os.environ.get("AWS_REGION", "us-east-1")
    fastapi_app.state.users_table = os.environ.get("DDB_USERS_TABLE")
    fastapi_app.state.itineraries_table = os.environ.get("DDB_ITINS_TABLE")
    fastapi_app.state.assets_bucket = os.environ.get("ASSETS_BUCKET")
    fastapi_app.state.aws_services = aws_services
    fastapi_app.state.dynamodb = getattr(aws_services, "dynamodb", None)
    fastapi_app.state.s3 = getattr(aws_services, "s3", None)
    fastapi_app.state.sns = getattr(aws_services, "sns", None)


_populate_app_state(app)


allowed_origins = [
    "https://d35vyyonooyid7.cloudfront.net",
    "http://localhost:3000",
    "http://localhost:5173",
    "*"  # Allow all origins during testing - remove in production
]

logger.info("Adding CORS middleware...")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logger.info("? CORS middleware added")



@app.get("/api/attractions")
def list_attractions_api(
    region: Optional[str] = Query(None, description="Filter by region"),
    category: Optional[str] = Query(None, description="Filter by category"),
    limit: Optional[int] = Query(None, ge=1, le=50, description="Maximum number of results")
):
    """Return curated attraction data for the frontend."""
    items = attraction_service.list_attractions(region=region, category=category, limit=limit)
    return items


@app.get("/api/attractions/{attraction_id}")
def get_attraction_api(attraction_id: str):
    item = attraction_service.get_attraction(attraction_id)
    if not item:
        raise HTTPException(status_code=404, detail="Attraction not found")
    return item


if HAS_RECOMMENDATIONS:
    try:
        app.include_router(recommendation_router)
        logger.info("? Recommendation router included")
        print("Recommendation router included")
    except Exception as e:
        logger.error(f"? Failed to include recommendation router: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        print(f"Failed to include recommendation router: {e}")


@app.post("/api/itineraries/plan", response_model=ItineraryPlan)
async def plan_itinerary_endpoint(
    request: ItineraryPlanRequest,
    current_user=Depends(get_optional_user),
):
    try:
        recommendation_request = RecommendationRequest(**request.model_dump(exclude={"save"}))
        await init_recommendation_service()
        recommendation_response = await recommendation_service.get_recommendations(recommendation_request)

        recommendation_dicts = [rec.model_dump() for rec in recommendation_response.recommendations]
        plan_payload = itinerary_planner.build_itinerary(recommendation_request, recommendation_dicts)

        context_message = (
            recommendation_response.context.get("message")
            if isinstance(recommendation_response.context, dict)
            else None
        )
        plan_payload["context"] = context_message
        plan_payload["recommendations"] = recommendation_response.recommendations

        itinerary_plan = ItineraryPlan(**plan_payload)

        if request.save and current_user:
            stored_payload = itinerary_plan.model_dump()
            stored_payload["user_id"] = current_user["id"]
            itinerary_repository.save_itinerary(current_user["id"], stored_payload)
            notification_service.send_itinerary_notification(
                current_user.get("email"), itinerary_plan.itinerary_id
            )

        return itinerary_plan
    except Exception as exc:
        logger.error(f"Itinerary planning failed: {exc}")
        raise HTTPException(status_code=500, detail="Failed to generate itinerary")


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
    metadata: Optional[dict] = None


@app.on_event("startup")
async def startup_event():
    logger.info("="*50)
    logger.info("API STARTUP EVENT")
    logger.info("="*50)
    logger.info(f"Python path: {sys.path}")
    logger.info(f"Current working directory: {os.getcwd()}")
    
    print("Starting Travel Planner API initialization...")
    print(f"Python path: {sys.path}")
    print(f"Current working directory: {os.getcwd()}")
    
    if HAS_RECOMMENDATIONS:
        try:
            from app.api.routes.recommendations import recommendation_service
            from app.data.sample_attractions import SAMPLE_NZ_ATTRACTIONS
            await recommendation_service.initialize(SAMPLE_NZ_ATTRACTIONS)
            logger.info("? Recommendation system initialized successfully")
            print("Recommendation system initialized successfully")
        except Exception as e:
            logger.error(f"? Recommendation system initialization failed: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            print(f"Warning: Recommendation system initialization failed: {e}")
    
    logger.info("? API startup completed successfully")
    print("API startup completed successfully")


@app.get("/")
def read_root():
    logger.info("Root endpoint accessed")
    return {
        "message": "Intelligent cloud-based travel itinerary planner API",
        "version": "1.0.0",
        "status": "running",
        "features": ["User Authentication", "Itinerary Management", "AI Recommendation System", "File Upload"],
        "docs": "/docs",
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "log_file": "/tmp/app.log"
    }


@app.get("/health")
def health_check():
    logger.info("Health check endpoint accessed")
    
    
    health_status = {
        "status": "healthy", 
        "service": "travel-planner-api",
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "environment": os.environ.get("ENV", "production"),
        "components": {
            "auth": "available" if auth else "unavailable",
            "s3utils": "available" if s3utils else "unavailable", 
            "sns_utils": "available" if sns_utils else "unavailable",
            "recommendations": "available" if HAS_RECOMMENDATIONS else "unavailable"
        }
    }
    
    logger.info(f"Health check result: {health_status}")
    return health_status


@app.get("/api/logs")
def get_logs():
   
    try:
        with open('/tmp/app.log', 'r') as f:
            logs = f.read()
        logger.info("Logs endpoint accessed - returning log content")
        return {"logs": logs, "timestamp": datetime.datetime.utcnow().isoformat()}
    except Exception as e:
        logger.error(f"Failed to read logs: {e}")
        return {"error": "Could not read logs", "detail": str(e)}


@app.get("/api/test")
def test_endpoint():
    logger.info("Test endpoint accessed")
    return {
        "message": "API is working",
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "test_passed": True
    }


@app.get("/api/debug")
def debug_info():
    
    logger.info("Debug endpoint accessed")
    return {
        "python_version": sys.version,
        "working_directory": os.getcwd(),
        "python_path": sys.path,
        "environment_variables": dict(os.environ),
        "modules": {
            "auth": str(type(auth)),
            "s3utils": str(type(s3utils)),
            "sns_utils": str(type(sns_utils)),
            "recommendations": HAS_RECOMMENDATIONS
        }
    }


@app.post("/api/auth/register")
def register(payload: RegisterRequest):
    logger.info(f"Register attempt for email: {payload.email}")
    try:
        if auth.user_exists(payload.email):
            logger.warning(f"Registration failed - email exists: {payload.email}")
            return JSONResponse({"detail": "email exists"}, status_code=400)
    except Exception as e:
        logger.error(f"Auth check error: {e}")
        print(f"Auth check error: {e}")

    try:
        user = auth.create_user(payload.email, payload.password, payload.name)
        logger.info(f"User created successfully: {payload.email}")
        return {"id": user["id"], "email": user["email"], "name": user.get("name")}
    except Exception as e:
        logger.error(f"User creation error: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        print(f"User creation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to create user")

@app.post("/api/auth/login")
def login(payload: LoginRequest):
    logger.info(f"Login attempt for email: {payload.email}")
    try:
        user = auth.authenticate_user(payload.email, payload.password)
        if not user:
            logger.warning(f"Login failed - invalid credentials: {payload.email}")
            return JSONResponse({"detail": "invalid credentials"}, status_code=401)

        token = auth.create_access_token({"sub": user["id"], "email": user["email"]})
        user_payload = {"id": user.get("id"), "email": user.get("email"), "name": user.get("name")}
        logger.info(f"Login successful: {payload.email}")
        return {"access_token": token, "token_type": "bearer", "user": user_payload}
    except Exception as e:
        logger.error(f"Login error: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        print(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Login failed")


@app.post("/api/itineraries")
def create_itinerary(payload: ItineraryRequest, current_user=Depends(auth.get_current_user)):
    logger.info(f"Creating itinerary: {payload.title} for user: {current_user}")
    try:
        it_id = str(uuid.uuid4())
        key = f"itineraries/{current_user['id']}/{it_id}.json"
        obj = {
            "id": it_id,
            "owner": current_user['id'],
            "title": payload.title,
            "items": payload.items,
            "metadata": payload.metadata or {},
            "createdAt": datetime.datetime.utcnow().isoformat()
        }

        itinerary_repository.save_itinerary(current_user['id'], obj.copy())

        # Upload to S3
        if s3utils:
            try:
                s3utils.put_json_object(key, obj)
            except Exception as exc:
                logger.warning("Failed to upload itinerary archive %s: %s", key, exc)
        # Send SNS notification
        if sns_utils:
            sns_utils.publish(f"New itinerary {it_id} by {current_user['email']}", subject="Itinerary Created")
        logger.info(f"Itinerary created successfully: {it_id}")
        return {"id": it_id, "s3_key": key}
    except Exception as e:
        logger.error(f"Error creating itinerary: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        print(f"Error creating itinerary: {e}")
        raise HTTPException(status_code=500, detail="Failed to create itinerary")

@app.get("/api/itineraries")
def get_itineraries(current_user=Depends(auth.get_current_user)):
    logger.info(f"Getting itineraries for user: {current_user}")
    try:
        itineraries = itinerary_repository.list_itineraries(current_user['id'])
        logger.info("Itineraries retrieved successfully")
        return itineraries
    except Exception as e:
        logger.error(f"Error getting itineraries: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        print(f"Error getting itineraries: {e}")
        return []



@app.get("/api/itineraries/me")
def get_my_itineraries(current_user=Depends(auth.get_current_user)):
    logger.info(f"Fetching itineraries for current user {current_user['id']}")
    return itinerary_repository.list_itineraries(current_user['id'])


@app.get("/api/itineraries/user/{user_id}")
def get_user_itineraries(user_id: str, current_user=Depends(auth.get_current_user)):
    if current_user['id'] != user_id:
        raise HTTPException(status_code=403, detail="Not authorised to access these itineraries")
    return itinerary_repository.list_itineraries(user_id)


@app.delete("/api/itineraries/{itinerary_id}")
def delete_itinerary(itinerary_id: str, current_user=Depends(auth.get_current_user)):
    logger.info(f"Deleting itinerary {itinerary_id} for user {current_user['id']}")
    deleted = itinerary_repository.delete_itinerary(current_user['id'], itinerary_id)
    if deleted and s3utils:
        key = f"itineraries/{current_user['id']}/{itinerary_id}.json"
        try:
            s3utils.delete_object(key)
        except Exception as exc:
            logger.warning(f"Failed to delete itinerary archive {key}: {exc}")
    if not deleted:
        raise HTTPException(status_code=404, detail="Itinerary not found")
    return {"status": "deleted", "itinerary_id": itinerary_id}


@app.delete("/api/itineraries")
def delete_all_itineraries(current_user=Depends(auth.get_current_user)):
    logger.info(f"Deleting all itineraries for user {current_user['id']}")
    removed = itinerary_repository.delete_all_itineraries(current_user['id'])
    if s3utils and removed:
        prefix = f"itineraries/{current_user['id']}/"
        for obj in s3utils.list_objects_with_prefix(prefix):
            key = obj.get('Key')
            if key:
                try:
                    s3utils.delete_object(key)
                except Exception as exc:
                    logger.warning(f"Failed to delete itinerary archive {key}: {exc}")
    return {"status": "deleted", "count": removed}

@app.get("/api/upload-url")
def upload_url(filename: str, current_user=Depends(auth.get_current_user)):
    logger.info(f"Generating upload URL for file: {filename}, user: {current_user}")
    try:
        key = f"uploads/{current_user['id']}/{uuid.uuid4()}_{filename}"
        url = s3utils.get_presigned_put_url(key)
        logger.info(f"Upload URL generated successfully for key: {key}")
        return {"url": url, "key": key}
    except Exception as e:
        logger.error(f"Error generating upload URL: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        print(f"Error generating upload URL: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate upload URL")


application = app
logger.info("? Application object created for AWS EB")


def create_app() -> FastAPI:
    """Factory used by Elastic Beanstalk and local runners."""
    return app


handler = Mangum(create_app())


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"Starting server on port {port}")
    print(f"Starting server on port {port}")
    uvicorn.run(
        "main:app", 
        host="0.0.0.0",
        port=port,
        reload=False  
    )

    








