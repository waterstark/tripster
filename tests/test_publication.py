from dirty_equals import IsUUID, IsDatetime

from httpx import AsyncClient, Response


async def test_create_piblication(
    ac: AsyncClient,
    default_user_registration: Response,
    auth_user: Response,
    create_piblication: Response,
):
    assert create_piblication.json() == {
        "text": "Privet",
        "author_id": IsUUID(4),
        "id": IsUUID(4),
        "created_at": IsDatetime(iso_string=True),
        "counter_of_votes": 0,
        "publication_rating": 0,
    }
    assert create_piblication.status_code == 201


async def test_get_ten_most_popular_piblications(
    ac: AsyncClient, default_user_registration: Response, auth_user: Response
):
    response = await ac.get("publication/")
    assert response.json() == [
        {
            "text": "Privet",
            "author_id": IsUUID(4),
            "id": IsUUID(4),
            "created_at": IsDatetime(iso_string=True),
            "counter_of_votes": 0,
            "publication_rating": 0,
        }
    ]
    assert response.status_code == 200


async def test_rating_piblication(
    ac: AsyncClient,
    default_user_registration: Response,
    auth_user: Response,
    create_piblication: Response,
):
    publication_id = create_piblication.json()["id"]
    response: Response = await ac.post(
        "publication/rating",
        json={
            "publication_id": publication_id,
            "like_is_toggeled": True,
        },
    )
    assert response.json() == {"detail": "you can't rate your own publication"}
    assert response.status_code == 403
