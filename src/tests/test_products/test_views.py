import io
import json

import httpx
from unittest.mock import patch, AsyncMock

from starlette import status

from src.main import app
from httpx import AsyncClient

async def test_create_category(session):
    files = {
        "file": ("test_image.jpg", io.BytesIO(b"dummy content"), "image/jpeg"),
        "name": (None, "some_new_name")
    }
    with patch("src.products.routers.save_image", new_callable=AsyncMock) as mock_save_image:
        mock_save_image.return_value = "../assets/test_image.jpg"

        async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(f"/products/categories", files=files)

            assert response.status_code == status.HTTP_201_CREATED
            res_ = response.json()
            assert res_["name"] == "some_new_name"
            assert res_["image"] == "../assets/test_image.jpg"

async def test_get_category(create_product_category, cleanup_categories):
    _id = create_product_category.id
    async with AsyncClient( transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response  = await client.get(f"/products/categories/{_id}")
        assert response.status_code == status.HTTP_200_OK
        assert create_product_category.name == response.json()["name"]

async def test_get_test_categories(create_product_category, cleanup_categories):
    _id = create_product_category.id
    async with AsyncClient( transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/products/categories")
        result = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert type(result) == list
        assert len(result) == 1
        assert result[0]["id"] == _id

async def test_get_test_category_update(cleanup_categories, create_product_category):
    _id = create_product_category.id

    file_content = b"dummy content"
    files = {
        "file": ("test_image.jpg", io.BytesIO(file_content), "image/jpeg"),
        "name": (None, "some_new_name")
    }

    with patch("src.products.repository.save_image", new_callable=AsyncMock) as mock_save_image:
        mock_save_image.return_value = "../assets/test_image.jpg"

        async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            response = await client.put(f"/products/categories/{_id}", files=files)

            assert response.status_code == status.HTTP_200_OK
            res_ = response.json()
            assert res_["name"] == "some_new_name"
            assert res_["image"] == "../assets/test_image.jpg"


async def test_delete_category(create_product_category, cleanup_categories):
    _id = create_product_category.id
    async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        with patch("src.products.repository.delete_image") as mock_delete_image:
            mock_delete_image.return_value = None
            response = await client.delete(f"/products/categories/{_id}")
            assert response.status_code == status.HTTP_204_NO_CONTENT
            assert response.json()["status"] == "success"

async def test_create_product(cleanup_categories,  create_product_category):
    test_form = {
        "name": "Test Product",
        "description": "Test description",
        "price": "19.99",
        "gender": "unisex",
        "category_id": create_product_category.id,
        "specifications": json.dumps({"color": "red", "size": "M"})
    }
    test_file = io.BytesIO(b"fake image data")
    test_file.name = "test.jpg"

    with patch("src.products.repository.save_image", new_callable=AsyncMock) as mock_save_image:
        mock_save_image.return_value = "../assets/test_image.jpg"
        async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(f"/products/products",
                                 data=test_form,
                                 files={"product_images": ("test.jpg", test_file, "image/jpeg")})
            assert response.status_code == status.HTTP_201_CREATED
            resp_data = response.json()
            assert resp_data["name"] ==  "Test Product"
            assert resp_data["category_id"] == test_form.get("category_id")


async def test_get_products(cleanup_product, create_product):
    async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(f"/products/products")
        products = response.json()
        assert response.status_code == status.HTTP_200_OK
        assert len(products) == 1
        assert products[0]["id"] == create_product.id
        assert products[0]["name"] == create_product.name

async def test_get_product_details(cleanup_product, create_product):
    product_id = create_product.id
    async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(f"/products/products/{product_id}")
        products = response.json()
        assert response.status_code == status.HTTP_200_OK
        assert products["id"] == create_product.id
        assert products["name"] == create_product.name

async def test_product_update( create_product):
    product = create_product
    test_form = {
        "name": "new Product",
        "description": "Test description",
        "price": "19.99",
        "gender": "unisex",
        "category_id": product.category_id,
        "specifications": json.dumps({"color": "red", "size": "M"})
    }
    test_file = io.BytesIO(b"fake image data")
    test_file.name = "test.jpg"
    with patch("src.products.repository.save_image", new_callable=AsyncMock) as mock_save_image:
        mock_save_image.return_value = "../assets/test_image.jpg"
        async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            response = await client.put(url=f"/products/products/{product.id}",
                                         data=test_form,
                                         files={"product_images": ("test.jpg", test_file, "image/jpeg")})
            assert response.status_code == status.HTTP_200_OK
            resp_data = response.json()
            assert resp_data["name"] == test_form["name"]
            assert resp_data["category_id"] == test_form.get("category_id")

async def test_product_delete(create_product):
    async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.delete(f"/products/products/{create_product.id}")
        data = response.json()
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert data["status"] == "success"
