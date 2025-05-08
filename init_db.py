# init_db.py
from database import engine
from app.models import Base

Base.metadata.create_all(bind=engine)