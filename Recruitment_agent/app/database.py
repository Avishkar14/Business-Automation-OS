import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL) #used for connection to DB - manages connection

# ====== #create factory use to create DB sessions connected
SessionLocal = sessionmaker( 
    autocommit=False, #need explicity to commit - ctrl over transactions
    autoflush=False,
    bind=engine     #actual connection of session to db engine
)
# ====== #Base class used by models: later they inherit from base.
# ====== #create ORM base 
Base = declarative_base()


# ====== used for testing connection :

# def test_connection():
#     with engine.connect() as connection:
#         result = connection.execute(text("SELECT 1"))
#         print("Database connection successful:", result.scalar())