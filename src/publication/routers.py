from typing import Annotated
from fastapi import APIRouter, Depends, status
from src.auth.models import AuthUser

from src.publication.schemas import (
    LikePublication,
    ResponsePublication,
    ResponsePublications,
)
from src.publication.crud import LikePublicationCrud, PublicationCrud

from src.auth.base_config import current_user

publication_router = APIRouter(
    prefix="/publication",
    tags=["publication"],
)


@publication_router.post(
    "/", response_model=ResponsePublication, status_code=status.HTTP_201_CREATED
)
async def add_publication(
    text: str,
    new_publication: Annotated[PublicationCrud, Depends()],
    verified_user: AuthUser = Depends(current_user),
):
    return await new_publication.create_publication(
        text=text, author_id=verified_user.id
    )


@publication_router.get(
    "/", response_model=ResponsePublications, status_code=status.HTTP_200_OK
)
async def get_ten_most_popular_posts(
    publications: Annotated[PublicationCrud, Depends()],
    verified_user: AuthUser = Depends(current_user),
):
    return await publications.get_publications()


@publication_router.post("/rating", status_code=status.HTTP_200_OK)
async def rate_post(
    rating_from_user: LikePublication,
    like: Annotated[LikePublicationCrud, Depends()],
    verified_user: AuthUser = Depends(current_user),
):
    return await like.update_like(rating_from_user, verified_user)
