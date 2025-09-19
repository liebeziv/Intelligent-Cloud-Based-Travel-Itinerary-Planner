import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base

# 本地开发使用SQLite
DATABASE_URL = "sqlite:///./travel_planner_local.db"

# Create Engine - SQLite配置
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite特定配置
    echo=True  # 开发时显示SQL语句
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """初始化数据库表"""
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")

def get_db():
    """数据库会话依赖"""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        raise
    finally:
        db.close()