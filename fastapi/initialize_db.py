import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session, sessionmaker
from src.database import engine, Base, UserDB
from passlib.context import CryptContext
from sqlalchemy import create_engine

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
ADMIN_PWD = os.getenv("ADMIN_PWD")

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = SessionLocal()


Base.metadata.create_all(bind=engine)

# bcrypt config
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# creating user admin
hashed_password = pwd_context.hash(ADMIN_PWD)

admin_user = UserDB(
    username="admin",
    full_name="Administrator",
    email="admin@example.com",
    hashed_password=hashed_password,
    user_role="admin"  
)

session.add(admin_user)
session.commit()
session.close()

print("Database initialized with user 'admin'")
