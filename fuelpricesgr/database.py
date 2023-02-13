"""The database module
"""
import sqlalchemy.orm

from fuelpricesgr import settings

engine = sqlalchemy.create_engine(
    f"sqlite:///{(settings.DATA_PATH / 'db.sqlite')}", connect_args={"check_same_thread": False}, echo=settings.SHOW_SQL
)

SessionLocal = sqlalchemy.orm.sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = sqlalchemy.orm.declarative_base()
