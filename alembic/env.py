"""
Full alembic/env.py: loads .env via Decouple, percent‑encodes + escapes password, dynamically imports all model modules, and configures offline/online migrations.
"""
import pkgutil
import importlib
import urllib.parse
from logging.config import fileConfig

from decouple import config as decouple_config
from sqlalchemy import engine_from_config, pool
from alembic import context

# ── 1) Alembic Config & Logging ─────────────────────────────────────────────
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ── 2) Load environment variables via python‑decouple ─────────────────────────
DB_USER = decouple_config('DB_USER')
DB_PASS = decouple_config('DB_PASSWORD')
DB_HOST = decouple_config('DB_HOST', default='db')
DB_PORT = decouple_config('DB_PORT', cast=int, default=5432)
DB_NAME = decouple_config('DB_NAME', default='regtech')

# ── 3) Percent‑encode and escape password for ConfigParser ───────────────────
enc_pass = urllib.parse.quote_plus(DB_PASS)     # "Regtech%4025"
safe_pass = enc_pass.replace('%', '%%')          # "Regtech%%4025"

# Build full SQLAlchemy URL and override alembic.ini
DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{safe_pass}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
config.set_main_option('sqlalchemy.url', DATABASE_URL)

# ── 4) Dynamically import all model modules ─────────────────────────────────
from api.v1.models.associations import Base
import api.v1.models
for _, module_name, _ in pkgutil.iter_modules(api.v1.models.__path__):
    importlib.import_module(f"api.v1.models.{module_name}")

# set metadata for autogenerate
target_metadata = Base.metadata

# ── 5) Offline migrations ────────────────────────────────────────────────────
def run_migrations_offline() -> None:
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

# ── 6) Online migrations ─────────────────────────────────────────────────────
def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()

# ── 7) Entrypoint ─────────────────────────────────────────────────────────────
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

