from datetime import datetime

from pydantic import BaseModel, RootModel
from pydantic.types import UUID4


class BasePublication(BaseModel):
    text: str
    author_id: UUID4

    class Config:
        from_attributes = True


class ResponsePublication(BasePublication):
    id: UUID4
    created_at: datetime
    counter_of_votes: int
    publication_rating: int


class LikePublication(BaseModel):
    publication_id: UUID4
    like_is_toggeled: bool | None

    class Config:
        from_attributes = True


ResponsePublications = RootModel[list[ResponsePublication]]
