from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from src.core import BudgetRange, Category, Gender
from src.core.models import Product


@dataclass(frozen=True)
class ProductFilters:
    category: Category | None = None
    gender: Gender | None = None
    budget: BudgetRange | None = None
    min_rating: float | None = None
    preferred_brands: list[str] = field(default_factory=list)

    attributes: dict[str, list[str]] = field(default_factory=dict)

    excluded_ingredients: list[str] = field(default_factory=list)

    limit: int = 20


class ProductRepository(ABC):
    @abstractmethod
    async def search(self, filters: ProductFilters) -> list[Product]: ...

    @abstractmethod
    async def update_tg_file_id(
        self,
        product_id: int,
        file_id: str,
    ) -> None: ...

    @abstractmethod
    async def get_by_id(self, product_id: int) -> Product | None: ...

    @abstractmethod
    async def get_by_ids(self, product_ids: list[int]) -> list[Product]: ...
