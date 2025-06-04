from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Date, Time, Boolean
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
import datetime # Required for default values like func.now()

Base = declarative_base()

class Entity(Base):
    __tablename__ = 'entities'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    address = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    creation_date = Column(DateTime(timezone=True), server_default=func.now())
    contact_person_name = Column(String)
    contact_person_mobile = Column(String)
    email = Column(String, unique=True, index=True) # Entity's email
    total_registered_subscribers = Column(Integer, default=0)

    admins = relationship("EntityAdmin", back_populates="entity")
    subscribers = relationship("Subscriber", back_populates="entity")
    # Relationship to AttendanceSession
    attendance_sessions = relationship("AttendanceSession", back_populates="entity", cascade="all, delete-orphan")


    def __repr__(self):
        return f"<Entity(id={self.id}, name='{self.name}')>"

class EntityAdmin(Base):
    __tablename__ = 'entity_admins'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    entity_id = Column(Integer, ForeignKey('entities.id'), nullable=False)

    entity = relationship("Entity", back_populates="admins")

    def __repr__(self):
        return f"<EntityAdmin(id={self.id}, username='{self.username}')>"

class Subscriber(Base):
    __tablename__ = 'subscribers'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    nfc_card_id = Column(String, unique=True, index=True, nullable=False) # For Card UID
    email = Column(String, unique=True, nullable=True)
    mobile = Column(String, nullable=True)
    photo_filename = Column(String, nullable=True)
    entity_id = Column(Integer, ForeignKey('entities.id'), nullable=False)
    registration_date = Column(DateTime(timezone=True), server_default=func.now())

    entity = relationship("Entity", back_populates="subscribers")
    # Relationship to AttendanceRecord
    attendance_records = relationship("AttendanceRecord", back_populates="subscriber", cascade="all, delete-orphan")


    def __repr__(self):
        return f"<Subscriber(id={self.id}, name='{self.name}', nfc_card_id='{self.nfc_card_id}')>"

class AttendanceSession(Base):
    __tablename__ = 'attendance_sessions'

    id = Column(Integer, primary_key=True, index=True)
    entity_id = Column(Integer, ForeignKey('entities.id'), nullable=False)
    date = Column(Date, nullable=False, default=datetime.date.today) # Default to today's date
    start_time = Column(Time, nullable=False, default=datetime.datetime.now().time) # Default to current time
    purpose = Column(String, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False) # Is the session currently active for scanning?
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    entity = relationship("Entity", back_populates="attendance_sessions")
    # Relationship to AttendanceRecord
    attendance_records = relationship("AttendanceRecord", back_populates="session", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<AttendanceSession(id={self.id}, purpose='{self.purpose}', date='{self.date}')>"

class AttendanceRecord(Base):
    __tablename__ = 'attendance_records'

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey('attendance_sessions.id'), nullable=False)
    subscriber_id = Column(Integer, ForeignKey('subscribers.id'), nullable=False)
    scan_time = Column(DateTime(timezone=True), server_default=func.now()) # Timestamp of when the card was scanned

    session = relationship("AttendanceSession", back_populates="attendance_records")
    subscriber = relationship("Subscriber", back_populates="attendance_records")

    def __repr__(self):
        return f"<AttendanceRecord(id={self.id}, session_id={self.session_id}, subscriber_id={self.subscriber_id})>"


DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL)

def create_db_and_tables():
    Base.metadata.create_all(bind=engine)
    print("Database and tables checked/created/updated for attendance models.")

if __name__ == "__main__":
    create_db_and_tables()
