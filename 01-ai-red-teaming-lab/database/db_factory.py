# database/db_factory.py
import os
from dotenv import load_dotenv

load_dotenv()


def get_repository():
    db_type = os.getenv("DB_TYPE", "sqlite").lower().strip()
    print(f"\n  Database backend: {db_type.upper()}")

    if db_type == "sqlite":
        from database.sqlite_repository import SQLiteRepository
        return SQLiteRepository(db_path=os.getenv("SQLITE_DB_PATH", "results/redteam.db"))

    elif db_type in ("postgresql", "postgres", "pg"):
        from database.postgres_repository import PostgreSQLRepository
        url = os.getenv("POSTGRES_URL")
        if not url:
            raise ValueError("POSTGRES_URL must be set in .env when DB_TYPE=postgresql")
        return PostgreSQLRepository(
            connection_url=url,
            ssl_mode=os.getenv("POSTGRES_SSL_MODE", "require")
        )

    elif db_type in ("mongodb", "mongo"):
        from database.mongodb_repository import MongoDBRepository
        url = os.getenv("MONGODB_URL")
        if not url:
            raise ValueError("MONGODB_URL must be set in .env when DB_TYPE=mongodb")
        return MongoDBRepository(
            connection_url=url,
            db_name=os.getenv("MONGODB_DB_NAME", "redteam_db")
        )

    else:
        raise ValueError(f"Unknown DB_TYPE: '{db_type}'. Choose: sqlite | postgresql | mongodb")


def test_connection() -> bool:
    try:
        with get_repository() as repo:
            print("  Database connection test passed")
            return True
    except Exception as e:
        print(f"  Database connection test FAILED: {e}")
        return False
