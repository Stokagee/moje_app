from sqlalchemy import Column, Integer, String
from app.database import Base

class FormData(Base):
    __tablename__ = "form_data"
    
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, index=True, nullable=False)
    last_name = Column(String, index=True, nullable=False)
    phone = Column(String, index=True, nullable=False)
    gender = Column(String, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)