from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
# from database.models import Base # Assuming a shared Base model from the database directory
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base() # Or use shared Base

class Entity(Base):
    __tablename__ = 'entities'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(String(255))
    # Add other relevant fields

    def __repr__(self):
        return f"<Entity {self.name}>"

# class EntityData(Base):
#     __tablename__ = 'entity_data'
#     id = Column(Integer, primary_key=True)
#     entity_id = Column(Integer, ForeignKey('entities.id'))
#     data_point = Column(String(100))
#     value = Column(String(255))
#     timestamp = Column(DateTime, default=datetime.utcnow)

#     entity = relationship("Entity")

    def __repr__(self):
        return f"<EntityData {self.data_point} for entity {self.entity_id}>"
