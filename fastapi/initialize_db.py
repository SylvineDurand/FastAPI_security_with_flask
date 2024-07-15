import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from src.database import engine, Base, UserDB
from passlib.context import CryptContext

load_dotenv()


Base.metadata.create_all(bind=engine)
session = Session(bind=engine)

# bcrypt config
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# creating user admin
hashed_password = pwd_context.hash("admin")

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
