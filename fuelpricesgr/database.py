"""The database module
"""
import os

import sqlalchemy.orm

from fuelpricesgr import settings

os.makedirs(settings.DATA_PATH, exist_ok=True)

engine = sqlalchemy.create_engine(
    f"sqlite:///{(settings.DATA_PATH / 'db.sqlite')}", connect_args={"check_same_thread": False}, echo=settings.SHOW_SQL
)

SessionLocal = sqlalchemy.orm.sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = sqlalchemy.orm.declarative_base()
