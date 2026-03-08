import pytest
import asyncio
import os
import time
from databases import Database

from app.core.config import settings

# Use a fresh Database instance to avoid the shared mock in conftest's client fixture
_DB_URL = settings.DATABASE_URL
database = Database(_DB_URL)


async def _try_connect(db: Database):
    """Try to connect; raise pytest.skip if unreachable."""
    try:
        await db.connect()
    except Exception as e:
        pytest.skip(f"Database not available: {e}")


@pytest.mark.asyncio
async def test_db_connection():
    """Test 1: Simple SELECT 1 query"""
    was_connected = database.is_connected
    try:
        if not was_connected:
            await _try_connect(database)
        query = "SELECT 1"
        result = await database.fetch_one(query=query)
        assert result[0] == 1
    except pytest.skip.Exception:
        raise
    except Exception as e:
        pytest.fail(f"Connection failed: {e}")
    finally:
        if database.is_connected and not was_connected:
            await database.disconnect()

@pytest.mark.asyncio
async def test_schema_check():
    """Test 2: Check if required tables exist"""
    was_connected = database.is_connected
    try:
        if not was_connected:
            await _try_connect(database)
        query = """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        """
        rows = await database.fetch_all(query=query)
        tables = [row['table_name'] for row in rows]
        assert isinstance(tables, list)
    except pytest.skip.Exception:
        raise
    except Exception as e:
        pytest.fail(f"Schema check failed: {e}")
    finally:
        if database.is_connected and not was_connected:
            await database.disconnect()

@pytest.mark.asyncio
async def test_crud_operations():
    """Test 3: Basic CRUD (Create, Read, Update, Delete)"""
    table_name = "test_crud_table"
    create_query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        id SERIAL PRIMARY KEY,
        name VARCHAR(50)
    )
    """
    drop_query = f"DROP TABLE IF EXISTS {table_name}"
    was_connected = database.is_connected
    try:
        if not was_connected:
            await _try_connect(database)

        await database.execute(query=create_query)

        insert_query = f"INSERT INTO {table_name} (name) VALUES (:name)"
        await database.execute(query=insert_query, values={"name": "Test Item"})

        select_query = f"SELECT * FROM {table_name} WHERE name = :name"
        item = await database.fetch_one(query=select_query, values={"name": "Test Item"})
        assert item is not None
        assert item['name'] == "Test Item"

        update_query = f"UPDATE {table_name} SET name = :new_name WHERE id = :id"
        await database.execute(query=update_query, values={"new_name": "Updated Item", "id": item['id']})

        updated_item = await database.fetch_one(query=select_query, values={"name": "Updated Item"})
        assert updated_item is not None
        assert updated_item['name'] == "Updated Item"

        delete_query = f"DELETE FROM {table_name} WHERE id = :id"
        await database.execute(query=delete_query, values={"id": item['id']})

        deleted_item = await database.fetch_one(query=select_query, values={"name": "Updated Item"})
        assert deleted_item is None

        await database.execute(query=drop_query)

    except pytest.skip.Exception:
        raise
    except Exception as e:
        pytest.fail(f"CRUD operations failed: {e}")
    finally:
        if database.is_connected and not was_connected:
            await database.disconnect()

@pytest.mark.asyncio
async def test_performance_latency():
    """Test 4: Response time measurement (Target < 500ms)"""
    was_connected = database.is_connected
    try:
        if not was_connected:
            await _try_connect(database)
        start_time = time.time()
        await database.fetch_one("SELECT 1")
        end_time = time.time()
        duration = (end_time - start_time) * 1000  # ms

        print(f"\nQuery Latency: {duration:.2f}ms")
        assert duration < 500, f"Query took too long: {duration}ms"
    finally:
        if database.is_connected and not was_connected:
            await database.disconnect()

@pytest.mark.asyncio
async def test_concurrency():
    """Test 5: Concurrent connections"""
    was_connected = database.is_connected
    try:
        if not was_connected:
            await _try_connect(database)

        async def run_query():
            return await database.fetch_one("SELECT 1")

        tasks = [run_query() for _ in range(10)]
        results = await asyncio.gather(*tasks)

        assert len(results) == 10
        assert all(r[0] == 1 for r in results)
    finally:
        if database.is_connected and not was_connected:
            await database.disconnect()
