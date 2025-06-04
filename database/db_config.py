from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Example: DATABASE_URL = "postgresql://user:password@host:port/database"
# For SQLite (testing purposes):
DATABASE_URL = "sqlite:///./test.db"
# In a production environment, get this from environment variables or a config file

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# The get_db() generator function was not used by either admin_panel or entity_dashboard directly.
# admin_panel uses SessionLocal() directly.
# entity_dashboard uses SessionLocal() via g.db and a teardown_app_request.
# So, this function can be removed to avoid confusion.
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()
