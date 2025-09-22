import sys
import os

# 添加路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app.main import app
    application = app
    print("Successfully imported app from app.main")
except ImportError as e:
    print(f"Import error: {e}")
    # 备用导入
    from main import app
    application = app

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(application, host="0.0.0.0", port=port)

