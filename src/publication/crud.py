from typing import Annotated, Sequence

from fastapi import Depends, HTTPException, status
from pydantic import UUID4
from src.auth.models import AuthUser
from src.publication.models import Publication, Rating

from src.database import get_async_session

from sqlalchemy import Update, delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.publication.schemas import (
    BasePublication,
    LikePublication,
)


class PublicationCrud:
    def __init__(
        self, session: Annotated[AsyncSession, Depends(get_async_session)]
    ) -> None:
        self.session = session

    async def create_publication(self, text: str, author_id: UUID4) -> dict:
        stmt = (
            insert(Publication)
            .values(BasePublication(text=text, author_id=author_id).model_dump())
            .returning(Publication)
        )
        result = await self.session.execute(stmt)
        publication = result.scalar_one()
        await self.session.commit()
        return publication

    async def get_publications(self) -> Sequence[Publication]:
        query = (
            select(Publication)
            .order_by(Publication.publication_rating.desc())
            .limit(10)
        )
        res = await self.session.execute(query)
        posts = res.scalars().all()
        return posts


class LikePublicationCrud(PublicationCrud):
    async def update_like(
        self, rating_from_user: LikePublication, verified_user: AuthUser
    ) -> dict[str, Publication]:
        query = select(Publication).where(
            Publication.id == rating_from_user.publication_id
        )
        publication = await self.session.execute(query)
        fetched_publication = publication.scalar()
        if fetched_publication is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Publication was not found (id: {rating_from_user.publication_id})",
            )
        if fetched_publication.author_id == verified_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="you can't rate your own publication",
            )
        query = select(Rating).where(
            Rating.publication_id == rating_from_user.publication_id,
            Rating.user_id == verified_user.id,
        )
        vote = await self.session.execute(query)
        fetched_vote = vote.scalar()
        if fetched_vote is None and rating_from_user.like_is_toggeled:
            stmt = insert(Rating).values(
                **rating_from_user.model_dump(),
                user_id=verified_user.id,
            )
            await self.session.execute(stmt)
            stmt = await self.update_publication_rating(fetched_publication, [1, 1])
            await self.session.execute(stmt)
        elif fetched_vote is None and not rating_from_user.like_is_toggeled:
            stmt = insert(Rating).values(
                **rating_from_user.model_dump(),
                user_id=verified_user.id,
            )
            await self.session.execute(stmt)
            stmt = await self.update_publication_rating(fetched_publication, [1, -1])
            await self.session.execute(stmt)
        else:
            if rating_from_user.like_is_toggeled and fetched_vote.like_is_toggeled:
                stmt = await self.update_publication_rating(
                    fetched_publication, [-1, -1]
                )
                await self.session.execute(stmt)
                stmt = delete(Rating).where(
                    Rating.publication_id == fetched_publication.id
                )
                await self.session.execute(stmt)
            elif (
                not rating_from_user.like_is_toggeled
                and not fetched_vote.like_is_toggeled
            ):
                stmt = await self.update_publication_rating(
                    fetched_publication, [-1, 1]
                )
                await self.session.execute(stmt)
                stmt = delete(Rating).where(
                    Rating.publication_id == fetched_publication.id
                )
                await self.session.execute(stmt)
            elif (
                rating_from_user.like_is_toggeled and not fetched_vote.like_is_toggeled
            ):
                stmt = await self.update_publication_rating(fetched_publication, [0, 2])
                await self.session.execute(stmt)
                stmt = (
                    update(Rating)
                    .values(like_is_toggeled=rating_from_user.like_is_toggeled)
                    .where(Rating.publication_id == fetched_publication.id)
                )
                await self.session.execute(stmt)
            elif (
                not rating_from_user.like_is_toggeled and fetched_vote.like_is_toggeled
            ):
                stmt = await self.update_publication_rating(
                    fetched_publication, [0, -2]
                )
                await self.session.execute(stmt)
                stmt = (
                    update(Rating)
                    .values(like_is_toggeled=rating_from_user.like_is_toggeled)
                    .where(Rating.publication_id == fetched_publication.id)
                )
                await self.session.execute(stmt)
        await self.session.commit()
        return {"data": fetched_publication}

    async def update_publication_rating(
        self, fetched_publication: Publication, how_much_increase: list[int]
    ) -> Update:
        stmt = (
            update(Publication)
            .values(
                counter_of_votes=fetched_publication.counter_of_votes
                + how_much_increase[0],
                publication_rating=fetched_publication.publication_rating
                + how_much_increase[1],
            )
            .where(Publication.id == fetched_publication.id)
        )
        return stmt
