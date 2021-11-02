from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class User:
    id: int
    dm_id: int
    username: str
    blocked_until: Optional[datetime] = None
