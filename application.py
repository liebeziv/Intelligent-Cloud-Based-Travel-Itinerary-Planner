import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app.main import create_app

# Elastic Beanstalk entry point expects this name
application = create_app()

if __name__ == '__main__':
    import uvicorn

    port = int(os.environ.get('PORT', '8000'))
    uvicorn.run(application, host='0.0.0.0', port=port)
