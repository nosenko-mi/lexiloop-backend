import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from app.utils.aws_secrets import get_aws_secret 

# for local development
load_dotenv()

if os.environ.get("USE_AWS_SECRETS") == "true":
    
    print("Using AWS RDS and Secrets Manager")
    
    db_creds = get_aws_secret("DB_SECRET_NAME")
    
    DB_USER = db_creds['username']
    DB_PASS = db_creds['password']
    DB_HOST = db_creds['host']
    DB_PORT = db_creds.get('port', 5432)
    DB_NAME = db_creds['dbname']
    
    SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

else:
    
    print("Using local Docker PostgreSQL database")
    
    DB_USER = os.environ.get("DB_USER")
    DB_PASS = os.environ.get("DB_PASS")
    DB_HOST = os.environ.get("DB_HOST")
    DB_PORT = os.environ.get("DB_PORT", 5432)
    DB_NAME = os.environ.get("DB_NAME")

    if not all([DB_USER, DB_PASS, DB_HOST, DB_NAME]):
        raise ValueError("Missing local database environment variables. Did you create .env?")

    SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    engine = create_engine(SQLALCHEMY_DATABASE_URL)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()