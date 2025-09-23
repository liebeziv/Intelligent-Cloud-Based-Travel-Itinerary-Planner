import sys
import os


sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

os.environ.setdefault('AWS_REGION', 'us-east-1')
os.environ.setdefault('AWS_DEFAULT_REGION', 'us-east-1')

from app.main import app


application = app

