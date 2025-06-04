from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
import datetime

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
    email = Column(String, unique=True, index=True)
    total_registered_subscribers = Column(Integer, default=0)

    admins = relationship("EntityAdmin", back_populates="entity")
    subscribers = relationship("Subscriber", back_populates="entity")

    def __repr__(self):
        return f"<Entity(id={self.id}, name='{self.name}')>"

class EntityAdmin(Base):
    __tablename__ = 'entity_admins'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    entity_id = Column(Integer, ForeignKey('entities.id'))

    entity = relationship("Entity", back_populates="admins")

    def __repr__(self):
        return f"<EntityAdmin(id={self.id}, username='{self.username}')>"

class Subscriber(Base):
    __tablename__ = 'subscribers'

    id = Column(Integer, primary_key=True, index=True)
    nfc_card_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    entity_id = Column(Integer, ForeignKey('entities.id'))
    registration_date = Column(DateTime(timezone=True), server_default=func.now())

    entity = relationship("Entity", back_populates="subscribers")

    def __repr__(self):
        return f"<Subscriber(id={self.id}, name='{self.name}', nfc_card_id='{self.nfc_card_id}')>"

# Example: DATABASE_URL = "postgresql://user:password@host:port/database"
# For SQLite (testing purposes):
DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(DATABASE_URL)

def create_db_and_tables():
    Base.metadata.create_all(bind=engine)
    print("Database and tables created (if they didn't exist).")

if __name__ == "__main__":
    # This allows running this script directly to create tables
    # In a real app, you might use Alembic for migrations
    create_db_and_tables()
