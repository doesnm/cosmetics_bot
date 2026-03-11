from dataclasses import dataclass, field
from decimal import Decimal

from src.core.enums import Gender, Category


@dataclass
class Product:
    id: int
    name: str
    brand: str
    category: Category
    price: Decimal
    currency: str = "KZT"
    rating: float = 0.0
    description: str = ""
    gender: Gender = Gender.UNISEX
    image_url: str | None = None
    tg_file_id: str | None = None

    attributes: dict[str, list[str]] = field(default_factory=dict)
