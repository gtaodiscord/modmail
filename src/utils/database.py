from datetime import datetime
from os import getenv, walk
from traceback import format_exc
from typing import Optional, Type, TypeVar
from uuid import uuid4

from asyncpg import Record, create_pool
from loguru import logger

from .models import Thread, ThreadMessage, User

T = TypeVar("T")


def model(cls: Type[T], record: Record) -> T:
    return cls(**dict(record))


class Database:
    """A database interface for the bot to connect to Postgres."""

    def __init__(self):
        pass

    async def setup(self):
        logger.info("Setting up database...")
        self.pool = await create_pool(
            dsn=getenv("DB_DSN", "postgres://root:password@postgres:5432/modmail")
        )
        logger.info("Database setup complete.")

        await self.automigrate()

    async def automigrate(self):
        allow = getenv("AUTOMIGRATE", "false")

        if allow != "true":
            logger.info("Automigrating is disabled, skipping migration attempt.")
            return

        try:
            migration = await self.fetchrow(
                "SELECT id FROM Migrations ORDER BY id DESC LIMIT 1;"
            )
        except Exception as e:
            print(e)
            migration = None

        migration = migration["id"] if migration else 0

        fs = []

        for root, dirs, files in walk("./src/data/"):
            for file in files:
                mnum = int(file[0:4])
                fs.append((mnum, file))

        fs.sort()
        fs = [f for f in fs if f[0] > migration]

        if not fs:
            return

        logger.info("Running automigrate...")

        for file in fs:
            res = await self.run_migration(file[1], file[0])
            if not res:
                break

        logger.info("Finished automigrate.")

    async def run_migration(self, filename: str, num: int):
        logger.info(f"Running migration {filename}...")
        try:
            with open(f"./src/data/{filename}") as f:
                await self.execute(f.read())
            await self.execute("INSERT INTO Migrations VALUES ($1);", num)
        except Exception as e:
            logger.error(f"Failed to run migration {filename}: {e}: {format_exc()}")
            return False
        else:
            logger.info(f"Successfully ran migration {filename}.")
            return True

    async def execute(self, query: str, *args):
        async with self.pool.acquire() as conn:  # type: ignore
            await conn.execute(query, *args)

    async def fetchrow(self, query: str, *args):
        async with self.pool.acquire() as conn:  # type: ignore
            return await conn.fetchrow(query, *args)

    async def fetch(self, query: str, *args):
        async with self.pool.acquire() as conn:  # type: ignore
            return await conn.fetch(query, *args)

    async def create_user(self, id: int, dm_id: int, username: str) -> User:
        user = await self.fetchrow(
            "INSERT INTO Users (id, dm_id, username) VALUES ($1, $2, $3) RETURNING *;",
            id,
            dm_id,
            username,
        )

        return model(User, user)

    async def fetch_user(self, id: int) -> Optional[User]:
        user = await self.fetchrow("SELECT * FROM Users WHERE id = $1;", id)

        if not user:
            return

        return model(User, user)

    async def create_thread(self, channel_id: int, member_id: int) -> Thread:
        id = uuid4()

        thread = await self.fetchrow(
            "INSERT INTO Threads (id, channel_id, member_id, created_at) VALUES ($1, $2, $3, $4) RETURNING *;",
            id,
            channel_id,
            member_id,
            datetime.utcnow(),
        )

        return model(Thread, thread)

    async def fetch_thread(self, id: str) -> Optional[Thread]:
        thread = await self.fetchrow("SELECT * FROM Threads WHERE id = $1;", id)

        if not thread:
            return

        return model(Thread, thread)

    async def fetch_threads(self, member_id: int) -> list[Thread]:
        threads = await self.fetchrow(
            "SELECT * FROM Threads WHERE member_id = $1;", member_id
        )

        return [model(Thread, thread) for thread in threads]

    async def suspend_thread(self, id: str) -> None:
        await self.execute("UPDATE Threads SET active = FALSE WHERE id = $1;", id)

    async def unsuspend_thread(self, id: str) -> None:
        await self.execute("UPDATE Threads SET active = TRUE WHERE id = $1;", id)

    async def close_thread(self, id: str) -> None:
        await self.execute("UPDATE Threads SET closed = TRUE WHERE id = $1;", id)

    async def create_message(self, thread_id: str, message_id: int, content: str, dm_message_id: Optional[int] = None) -> ThreadMessage:
        message = await self.fetchrow("INSERT INTO ThreadMessages (thread_id, message_id, content, dm_message_id, created_at) VALUES ($1, $2, $3, $4, $5) RETURNING *;", thread_id, message_id, content, dm_message_id, datetime.utcnow())

        return model(ThreadMessage, message)

    async def update_message(self, thread_id: str, message_id: int, content: str) -> ThreadMessage:
        message = await self.fetchrow("UPDATE ThreadMessage SET content = $1 WHERE thread_id = $2 AND message_id = $3 RETRUNING *;", content, thread_id, message_id)

        return model(ThreadMessage, message)

    async def fetch_messages(self, thread_id: str) -> list[ThreadMessage]:
        messages = await self.fetch("SELECT * FROM ThreadMessage WHERE thread_id = $1;", thread_id)

        return [model(ThreadMessage, messages) for messages in messages]
