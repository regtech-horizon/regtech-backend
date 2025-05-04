from decouple import config
from sqlalchemy.engine import URL, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Read raw values from .env
DB_USER = config('DB_USER')           # e.g. "regtechuser"
DB_PASS = config('DB_PASSWORD')           # e.g. "Regtech@25"
DB_HOST = config('DB_HOST', default='db')
DB_PORT = config('DB_PORT', cast=int, default=5432)
DB_NAME = config('DB_NAME', default='regtech')

# Build a safe URL; URL.create handles percent-encoding internally
db_url = URL.create(
    drivername="postgresql+psycopg2",
    username=DB_USER,
    password=DB_PASS,
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME,
)

# Create engine and session factory
engine = create_engine(db_url, pool_pre_ping=True)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for ORM models
Base = declarative_base()

def get_db():
    """
    FastAPI dependency: yield a database session, then close it.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize all tables (call at startup or in migrations).
    """
    Base.metadata.create_all(bind=engine)

