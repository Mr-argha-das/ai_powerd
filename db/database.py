from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# DATABASE_URL = "mysql+pymysql://root:@localhost:3306/ai_powerd"
# Encode special characters in password
DATABASE_URL = "mysql+pymysql://rajveerf_new:2Br%40zK03fWwb@rajveerfacility.in:3306/rajveerf_new"
engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,       # Fixes MySQL server has gone away
    pool_recycle=280,         # Prevents idle timeout issues
    pool_size=10,             # DB pool size
    max_overflow=20           # Extra connections under load
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False    # Prevents stale session issues
)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
