import sys
sys.path.append('.')

modules_to_test = [
    'app.config',
    'app.main',
    'app.auth', 
    'app.s3utils',
    'app.sns_utils',
    'app.aws_services'
]

for module in modules_to_test:
    try:
        __import__(module)
        print(f"✅ {module} imports successfully")
    except Exception as e:
        print(f"❌ {module} failed: {e}")