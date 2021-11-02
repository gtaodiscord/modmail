from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Thread:
    id: int
    channel_id: int
    member_id: int
    created_at: datetime
    active: bool
    closed: bool
    alerts: str


@dataclass
class ThreadMessage:
    id: int
    thread_id: str
    message_id: int
    created_at: datetime
    deleted: bool
    content: str
    dm_message_id: Optional[int] = None
