from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

QUIZZES_DATABASE_URL = "sqlite:///./data/lexiloop.db"
TEXTS_DATABASE_URL = "sqlite:///./data/texts.db"
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

engine = create_engine(
    QUIZZES_DATABASE_URL, 
    connect_args={"check_same_thread": False} # sqlite only
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

texts_engine = create_engine(
    TEXTS_DATABASE_URL, 
    connect_args={"check_same_thread": False} # sqlite only
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
TextsSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=texts_engine)

Base = declarative_base()