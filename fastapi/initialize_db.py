import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from src.database import engine, Base, UserDB
from passlib.context import CryptContext

load_dotenv()

# Initialisation de la base de données
Base.metadata.create_all(bind=engine)

# Création de la session
session = Session(bind=engine)

# Configuration de bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hachage du mot de passe admin
hashed_password = pwd_context.hash("admin")

# Création de l'utilisateur admin
admin_user = UserDB(
    username="admin",
    full_name="Administrator",
    email="admin@example.com",
    hashed_password=hashed_password,
    disabled=False,
    user_role="admin"  # Ajout du champ user_role
)

# Ajout de l'utilisateur à la session
session.add(admin_user)

# Validation de la transaction
session.commit()

# Fermeture de la session
session.close()

print("Base de données initialisée avec l'utilisateur admin.")
