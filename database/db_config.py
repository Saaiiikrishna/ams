from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Example: DATABASE_URL = "postgresql://user:password@host:port/database"
# For SQLite (testing purposes):
DATABASE_URL = "sqlite:///./test.db"
# In a production environment, get this from environment variables or a config file

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
