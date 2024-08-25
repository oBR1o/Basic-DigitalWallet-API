from httpx import AsyncClient
from digimon import models
from digimon.models.users import DBUser, Token
import pytest


# @pytest.mark.asyncio
# async def test_create_item_for_merchant(
#     client: AsyncClient, token_user1: Token, merchant_user1: models.DBMerchant
# ):
#     headers = {"Authorization": f"{token_user1.token_type} {token_user1.access_token}"}
#     payload = {
#         "name": "item1",
#         "description": "item1 description",
#         "price": 100.00,
#         "meerchant_id": str(merchant_user1.id),
#         "user_id": str(token_user1.user_id),
#         "tax" : 5.00,
#         "quantity" : 10,
#     }

#     response = await client.post( f"/items/{merchant_user1.id}", json=payload, headers=headers)
#     data = response.json()

#     assert response.status_code == 200
#     assert data["id"] > 0
#     assert data["name"] == payload["name"]
#     assert data["description"] == payload["description"]
#     assert data["price"] == payload["price"]
#     assert data["tax"] == payload["tax"]
#     assert data["merchant_id"] == merchant_user1.id
#     assert data["user_id"] == token_user1.user_id
#     assert data["quantity"] == payload["quantitiy"]

@pytest.mark.asyncio
async def test_delete_item(
    client: AsyncClient, item_user1: models.DBItem, token_user1: Token
):
    headers = {"Authorization": f"{token_user1.token_type} {token_user1.access_token}"}

    response = await client.delete(f"/items/{item_user1.id}", headers=headers)

    assert response.status_code == 200
    assert response.json() == {"message": "delete success"}

@pytest.mark.asyncio
async def test_list_items(client: AsyncClient, item_user1: models.DBItem):

    response = await client.get("/items")

    data = response.json()

    assert response.status_code == 200
    assert len(data["items"]) > 0
    check_items = None

    for item in data["items"]:
        if item["name"] == item_user1.name:
            check_item = item
            break

    assert check_item["id"] == item_user1.id
    assert check_item["name"] == item_user1.name

