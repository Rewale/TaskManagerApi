import databases
import sqlalchemy

import settings

metadata = sqlalchemy.MetaData()
database = databases.Database(settings.POSTGRES_URL)
engine = sqlalchemy.create_engine(settings.POSTGRES_URL)
