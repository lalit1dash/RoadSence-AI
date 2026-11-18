from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from config import settings
import logging

logger = logging.getLogger(__name__)

client: AsyncIOMotorClient = None
database: AsyncIOMotorDatabase = None


async def connect_db():
    global client, database
    try:
        client = AsyncIOMotorClient(
            settings.MONGODB_URL, serverSelectionTimeoutMS=5000
        )
        database = client[settings.DB_NAME]
        await client.admin.command("ping")
        logger.info(f"✅ Connected to MongoDB: {settings.DB_NAME}")
    except Exception as e:
        logger.warning(
            f"⚠️ MongoDB connection failed: {e}. App will run with limited functionality."
        )
        client = None
        database = None


async def disconnect_db():
    global client
    if client:
        client.close()
        logger.info("MongoDB connection closed.")


# Aliases for compatibility
connect_to_mongo = connect_db
close_mongo_connection = disconnect_db



def get_database() -> AsyncIOMotorDatabase:
    return database


def get_collection(name: str):
    if database is None:
        return None
    return database[name]


async def check_connection() -> bool:
    """Return True if MongoDB is reachable."""
    if client is None:
        return False
    try:
        await client.admin.command("ping")
        return True
    except Exception:
        return False
