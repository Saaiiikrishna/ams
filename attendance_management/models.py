from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
# from database.models import Base # Assuming a shared Base model
# from subscriber_management.models import Subscriber # Link to Subscriber
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base() # Or use shared Base

class AttendanceRecord(Base):
    __tablename__ = 'attendance_records'
    id = Column(Integer, primary_key=True)
    subscriber_id = Column(Integer, ForeignKey('subscribers.id')) # Foreign key to Subscriber table
    timestamp = Column(DateTime, default=datetime.utcnow)
    event_type = Column(String(50)) # e.g., 'entry', 'exit'

    # subscriber = relationship("Subscriber") # Relationship to Subscriber model

    def __repr__(self):
        return f"<AttendanceRecord {self.subscriber_id} at {self.timestamp}>"
