import os
import sys
sys.path.append('.')

# 设置环境变量模拟AWS环境
os.environ["AWS_REGION"] = "us-east-1"
os.environ["AWS_ACCOUNT_ID"] = "849354442724"

try:
    from app.config import settings
    print("✅ Config loaded successfully")
    print(f"AWS Region: {settings.AWS_REGION}")
    print(f"AWS Account: {settings.AWS_ACCOUNT_ID}")
    print(f"Assets Bucket: {settings.assets_bucket}")
    print(f"CORS Origins: {settings.cors_origins}")
    print(f"Debug Mode: {settings.DEBUG}")
    
    # 验证没有localhost
    config_str = str(settings.__dict__)
    if "localhost" in config_str.lower():
        print("❌ Warning: localhost found in config")
    else:
        print("✅ No localhost references found")
        
except Exception as e:
    print(f"❌ Config error: {e}")
    import traceback
    traceback.print_exc()