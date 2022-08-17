import asyncio

from model.models import metadata, engine, database

if __name__ == '__main__':

    asyncio.get_event_loop().run_until_complete(database.connect())
    metadata.create_all(engine)
