import databases
import sqlalchemy

from app.core.config import settings

DATABASE_URL = settings.DATABASE_URL

# Databases (Async)
database = databases.Database(DATABASE_URL)

# SQLAlchemy (Sync - for schema definitions)
metadata = sqlalchemy.MetaData()
