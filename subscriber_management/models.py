from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
# from database.models import Base # Assuming a shared Base model
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base() # Or use shared Base

class Subscriber(Base):
    __tablename__ = 'subscribers'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    nfc_tag_id = Column(String(50), unique=True, nullable=True) # Assuming NFC ID is a string
    is_active = Column(Boolean, default=True)
    registration_date = Column(DateTime, default=datetime.utcnow)

    # entity_id = Column(Integer, ForeignKey('entities.id')) # If subscriber is linked to an entity
    # entity = relationship("Entity")

    def __repr__(self):
        return f"<Subscriber {self.name}>"
