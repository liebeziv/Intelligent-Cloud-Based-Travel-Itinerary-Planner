import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=== 简化验证开始 ===")

# 测试基本导入
try:
    import fastapi
    print("✅ FastAPI imported")
except ImportError as e:
    print(f"❌ FastAPI: {e}")

try:
    import boto3
    print("✅ Boto3 imported")
except ImportError as e:
    print(f"❌ Boto3: {e}")

try:
    import pydantic
    print("✅ Pydantic imported")
except ImportError as e:
    print(f"❌ Pydantic: {e}")

# 测试简化配置
print("\n=== 测试简化配置 ===")
try:
    class SimpleSettings:
        AWS_REGION = "us-east-1"
        AWS_ACCOUNT_ID = "849354442724"
        SECRET_KEY = "test-key"
        cors_origins = '["https://d35vyyonooyid7.cloudfront.net"]'
        DEBUG = True
        assets_bucket = "travel-planner-assets-849354442724"
    
    settings = SimpleSettings()
    print("✅ Simple settings created")
    print(f"AWS Region: {settings.AWS_REGION}")
    print(f"CORS Origins: {settings.cors_origins}")
    
    # 检查localhost
    config_str = str(settings.__dict__)
    if "localhost" in config_str.lower():
        print("❌ Warning: localhost found in config")
    else:
        print("✅ No localhost references found")
        
except Exception as e:
    print(f"❌ Simple settings failed: {e}")

print("\n=== 验证完成 ===")