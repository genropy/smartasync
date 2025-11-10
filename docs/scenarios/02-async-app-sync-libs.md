# Scenario A2: Async App → Sync Legacy Library

**Target Audience**: Web developers, async framework users
**Difficulty**: Intermediate
**Keywords**: FastAPI, Django, aiohttp, legacy, database, psycopg2, sqlite3

---

## 📋 The Problem

You're building a modern async web application (FastAPI, aiohttp, etc.) but need to integrate with:
- Legacy synchronous database drivers (psycopg2, MySQLdb, sqlite3)
- Sync third-party libraries without async support
- CPU-intensive blocking operations
- Legacy business logic code

**The Challenge**: Calling sync blocking code from async context blocks the event loop, freezing your entire application.

---

## 🔴 Without SmartAsync

### Naive Approach (WRONG!)

```python
from fastapi import FastAPI
import sqlite3

app = FastAPI()

@app.get("/users")
async def get_users():
    # ⚠️ BLOCKS EVENT LOOP!
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    conn.close()
    return {"users": users}
```

**Problem**: `sqlite3.connect()` and `cursor.execute()` are blocking I/O operations that freeze the event loop. No other requests can be processed!

### Manual Threading (VERBOSE!)

```python
from fastapi import FastAPI
import asyncio
import sqlite3

app = FastAPI()

def _query_db():
    """Blocking database query."""
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    conn.close()
    return [{"id": u[0], "name": u[1]} for u in users]

@app.get("/users")
async def get_users():
    # Manual threading - verbose and repetitive
    users = await asyncio.to_thread(_query_db)
    return {"users": users}

# Must create wrapper function for EVERY database call!
def _insert_user(name: str, email: str):
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (name, email) VALUES (?, ?)", (name, email))
    conn.commit()
    conn.close()
    return cursor.rowcount

@app.post("/users")
async def create_user(name: str, email: str):
    rowcount = await asyncio.to_thread(_insert_user, name, email)
    return {"created": rowcount}
```

**Problems**:
- ❌ Boilerplate for every database method
- ❌ Wrapper functions clutter codebase
- ❌ Hard to maintain
- ❌ Error handling duplicated

---

## 🟢 With SmartAsync

### Clean Solution

```python
from fastapi import FastAPI
from smartasync import smartasync
import sqlite3
from typing import List, Dict, Any

class DatabaseManager:
    """Sync database with async-friendly interface."""

    def __init__(self, db_path: str):
        self.db_path = db_path

    @smartasync
    def query(self, sql: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Execute query - auto-threaded in async context."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        try:
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    @smartasync
    def execute(self, sql: str, params: tuple = ()) -> int:
        """Execute write operation - auto-threaded in async context."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute(sql, params)
            conn.commit()
            return cursor.rowcount
        finally:
            conn.close()

# FastAPI application
app = FastAPI()
db = DatabaseManager("app.db")

@app.get("/users")
async def get_users():
    """Async endpoint - database call is auto-threaded."""
    users = await db.query("SELECT * FROM users")
    return {"users": users}

@app.post("/users")
async def create_user(name: str, email: str):
    """Async endpoint with database write."""
    rowcount = await db.execute(
        "INSERT INTO users (name, email) VALUES (?, ?)",
        (name, email)
    )
    return {"created": rowcount}

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    """Parameterized query."""
    users = await db.query(
        "SELECT * FROM users WHERE id = ?",
        (user_id,)
    )
    if not users:
        return {"error": "User not found"}, 404
    return {"user": users[0]}
```

**Benefits**:
- ✅ No boilerplate wrapper functions
- ✅ Clean class-based API
- ✅ Automatic threading in async context
- ✅ Event loop never blocked
- ✅ Can still use in sync CLI tools (no `await` needed)

---

## 💡 Complete Example: FastAPI + Legacy Database

### Full Application

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from smartasync import smartasync
import sqlite3
from typing import List, Dict, Any, Optional
from contextlib import contextmanager

class User(BaseModel):
    """User model."""
    name: str
    email: str

class UserResponse(BaseModel):
    """User response model."""
    id: int
    name: str
    email: str

class DatabaseManager:
    """Production-ready database manager."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize database schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    @contextmanager
    def _get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    @smartasync
    def get_all_users(self) -> List[Dict[str, Any]]:
        """Get all users."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, email FROM users ORDER BY id")
            return [dict(row) for row in cursor.fetchall()]

    @smartasync
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, name, email FROM users WHERE id = ?",
                (user_id,)
            )
            row = cursor.fetchone()
            return dict(row) if row else None

    @smartasync
    def create_user(self, name: str, email: str) -> int:
        """Create new user, return ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "INSERT INTO users (name, email) VALUES (?, ?)",
                    (name, email)
                )
                conn.commit()
                return cursor.lastrowid
            except sqlite3.IntegrityError:
                raise ValueError(f"Email {email} already exists")

    @smartasync
    def update_user(self, user_id: int, name: str, email: str) -> bool:
        """Update user, return success."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET name = ?, email = ? WHERE id = ?",
                (name, email, user_id)
            )
            conn.commit()
            return cursor.rowcount > 0

    @smartasync
    def delete_user(self, user_id: int) -> bool:
        """Delete user, return success."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()
            return cursor.rowcount > 0

# FastAPI application
app = FastAPI(title="User API with Legacy DB")
db = DatabaseManager("users.db")

@app.get("/users", response_model=List[UserResponse])
async def list_users():
    """List all users."""
    users = await db.get_all_users()
    return users

@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    """Get specific user."""
    user = await db.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/users", response_model=UserResponse, status_code=201)
async def create_user(user: User):
    """Create new user."""
    try:
        user_id = await db.create_user(user.name, user.email)
        created_user = await db.get_user_by_id(user_id)
        return created_user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/users/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user: User):
    """Update user."""
    success = await db.update_user(user_id, user.name, user.email)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    updated_user = await db.get_user_by_id(user_id)
    return updated_user

@app.delete("/users/{user_id}", status_code=204)
async def delete_user(user_id: int):
    """Delete user."""
    success = await db.delete_user(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return None

# Can also use in CLI tools!
if __name__ == "__main__":
    # Sync usage for admin scripts
    print("Creating test users...")
    db.create_user("Alice", "alice@example.com")
    db.create_user("Bob", "bob@example.com")

    print("\nAll users:")
    for user in db.get_all_users():
        print(f"  - {user['name']} <{user['email']}>")
```

### Run the API

```bash
# Install dependencies
pip install fastapi uvicorn smartasync

# Run server
uvicorn main:app --reload

# Test endpoints
curl http://localhost:8000/users
curl -X POST http://localhost:8000/users \
     -H "Content-Type: application/json" \
     -d '{"name": "Charlie", "email": "charlie@example.com"}'
```

---

## ⚠️ Important Considerations

### 1. Connection Pooling

For production, consider connection pooling:

```python
from queue import Queue
import sqlite3

class PooledDatabaseManager:
    """Database manager with connection pool."""

    def __init__(self, db_path: str, pool_size: int = 5):
        self.db_path = db_path
        self.pool = Queue(maxsize=pool_size)

        # Initialize pool
        for _ in range(pool_size):
            conn = sqlite3.connect(db_path, check_same_thread=False)
            self.pool.put(conn)

    @contextmanager
    def _get_connection(self):
        """Get connection from pool."""
        conn = self.pool.get()
        try:
            yield conn
        finally:
            self.pool.put(conn)

    @smartasync
    def query(self, sql: str, params: tuple = ()) -> List[Dict]:
        """Query using pooled connection."""
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(sql, params)
            return [dict(row) for row in cursor.fetchall()]
```

### 2. Transaction Management

For complex transactions:

```python
@smartasync
def transfer_funds(self, from_id: int, to_id: int, amount: float):
    """Atomic transaction."""
    with self._get_connection() as conn:
        try:
            cursor = conn.cursor()

            # Debit
            cursor.execute(
                "UPDATE accounts SET balance = balance - ? WHERE id = ?",
                (amount, from_id)
            )

            # Credit
            cursor.execute(
                "UPDATE accounts SET balance = balance + ? WHERE id = ?",
                (amount, to_id)
            )

            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            raise
```

### 3. Thread Safety

SQLite `check_same_thread=False` may be needed:

```python
conn = sqlite3.connect(db_path, check_same_thread=False)
```

But be careful: SQLite itself is thread-safe, but Python's wrapper has restrictions.

### 4. Performance

For high-load scenarios:
- Consider async-native drivers when available (asyncpg for PostgreSQL)
- Use connection pooling
- Monitor thread pool size (`asyncio.to_thread` uses default pool)

---

## 🔗 Related Resources

- **Example Code**: [examples/scenario_a2_async_calls_sync.py](../../examples/scenario_a2_async_calls_sync.py)
- **Test**: [tests/test_smartasync.py::test_bidirectional_scenario_a2](../../tests/test_smartasync.py)
- **Alternative Solutions**: [Comparison with Alternatives](../advanced/comparison.md)

---

## 📚 Database Driver Compatibility

| Driver | Type | SmartAsync Support | Notes |
|--------|------|-------------------|-------|
| **sqlite3** | Sync | ✅ Yes | Built-in, works great |
| **psycopg2** | Sync | ✅ Yes | PostgreSQL sync driver |
| **psycopg** (v3) | Both | ⚠️ Use native async | Has async support |
| **MySQLdb** | Sync | ✅ Yes | MySQL sync driver |
| **PyMySQL** | Sync | ✅ Yes | Pure Python MySQL |
| **asyncpg** | Async | ⚠️ Already async | No need for SmartAsync |
| **motor** | Async | ⚠️ Already async | MongoDB async driver |

**Rule of Thumb**: If the driver is sync-only, SmartAsync helps. If it has native async support, use that directly.

---

**Next Steps**:
- Explore [01: Sync App → Async Libraries](01-sync-app-async-libs.md) for sync usage
- See [04: Unified Library API](04-unified-library-api.md) for library design
- Check [03: Testing Async Code](03-testing-async-code.md) for testing strategies
