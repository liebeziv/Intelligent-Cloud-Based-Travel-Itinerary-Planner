#!/usr/bin/env python3
import sys
import os
import uvicorn


sys.path.insert(0, os.path.dirname(__file__))


os.environ["DEBUG"] = "True"
os.environ["SECRET_KEY"] = "local-dev-key"

if __name__ == "__main__":

    uvicorn.run(
        "app.main:app",
        host="127.0.0.1", 
        port=8000,
        reload=False  
    )