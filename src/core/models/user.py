from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class User:
    telegram_id: int
    first_name: str
    username: str | None = None
    language_code: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
