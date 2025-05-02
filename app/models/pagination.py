from typing import Optional, List, TypeVar, Generic
from sqlmodel import SQLModel

T = TypeVar("T")

class PaginatedResponse(SQLModel, Generic[T]):
    items: List[T]
    total_count: int

class PaginatedUsersRequest(SQLModel):
    search: Optional[str] = None
    sort: str = "user_id"
    order: str = "ASC"
    page: int = 1
    size: int = 10
    role: Optional[str] = None 