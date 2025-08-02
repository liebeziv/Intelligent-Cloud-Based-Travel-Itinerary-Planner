from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI(
    title="Travel Planner API",
    description="Intelligent Cloud-Based Travel Itinerary Planner",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Travel Planner API", 
        "version": "1.0.0", 
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/api/attractions")
async def get_attractions():
    return {
        "attractions": [
            {
                "id": 1,
                "name": "Milford Sound",
                "description": "Famous fiord in Fiordland National Park",
                "category": "nature",
                "rating": 4.8
            },
            {
                "id": 2,
                "name": "Queenstown Skyline Gondola",
                "description": "Scenic gondola ride",
                "category": "adventure", 
                "rating": 4.6
            }
        ]
    }

@app.post("/api/auth/login")
async def login():
    return {"access_token": "fake-token", "token_type": "bearer"}

@app.post("/api/auth/register")
async def register():
    return {"message": "User registered successfully"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
