import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from unittest.mock import AsyncMock, patch

from src.products.models import Category, Product
from src.products.repository import ProductCategoryRepository, ProductRepository
from src.products.schemas import GenderEnum, ProductFilter

test_cat_data = {"name": "some_new_Test",
                "image": "../assets/test_image.jpg"}

test_product_data  = {
        "name": "test_product",
        "description": "some_test_description",
        "price": "50",
        "gender": GenderEnum.man,
}

async def create_test_category(session: AsyncSession,
                               cat_repository: ProductCategoryRepository,
                               temp_data: dict = test_cat_data) ->Category:
    category = await cat_repository.create(temp_data)
    await session.commit()
    return category

async def delete_test_category(session: AsyncSession,
                               cat_repository: ProductCategoryRepository,
                               cat_id: int) ->None:
    await cat_repository.delete(cat_id)
    await session.commit()


async def create_test_product(session: AsyncSession,
                              product_repository: ProductRepository,
                              cat_repository: ProductCategoryRepository,
                              temp_data: dict = test_product_data) ->Product:
    category = await create_test_category(session, cat_repository, test_cat_data)
    temp_data["category_id"] = category.id
    product = await product_repository.create(temp_data)
    await session.commit()
    return product

async def delete_test_product(session: AsyncSession,
                              product_repository: ProductRepository,
                              cat_repository: ProductCategoryRepository,
                              product: Product) ->None:
    await product_repository.delete(product.id)
    await cat_repository.delete(product.category_id)
    await session.commit()


async def test_product_categories_create(session, cat_repository):
    category = await create_test_category(session, cat_repository)
    assert category is not None
    assert category.name == "some_new_Test"
    assert category.image == test_cat_data["image"]
    await delete_test_category(session, cat_repository, category.id)


async def test_existing_product_category_create(session, cat_repository):
    cat = await create_test_category(session, cat_repository)
    await session.commit()
    await session.flush()
    with pytest.raises(HTTPException) as exc_info:
        await create_test_category(session, cat_repository)
    assert exc_info.value.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "already exists" in exc_info.value.detail
    await delete_test_category(session, cat_repository, cat.id)


async def test_list_product_categories(session, cat_repository):
    data1 = {"name": "test_cat",
            "image": "../assets/test_image.jpg"}
    data2 = {"name": "test_cat2",
             "image": "../assets/test_image.jpg"}
    await create_test_category(session, cat_repository, data1)
    await create_test_category(session, cat_repository, data2)
    cat_list = await cat_repository.list()
    assert len(cat_list) == 2
    assert cat_list[0].name == data1["name"]
    assert cat_list[1].name == data2["name"]
    await delete_test_category(session, cat_repository, cat_list[0].id)
    await delete_test_category(session, cat_repository, cat_list[1].id)

async def test_delete_product_category(session, cat_repository):
    cat_to_create = await create_test_category(session, cat_repository)
    await session.commit()
    cat = await cat_repository.get(cat_to_create.id)
    assert cat.name == test_cat_data["name"]
    await cat_repository.delete(cat_to_create.id)
    await session.commit()
    with pytest.raises(HTTPException) as exc_info:
        await cat_repository.get(cat_to_create.id)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

@patch("src.products.repository.save_image", new_callable=AsyncMock)
async def test_product_category_edit(mock_save_image, session, cat_repository):
    mock_save_image.return_value = "../assets/test_image.jpg"
    cat = await create_test_category(session, cat_repository)
    await session.commit()
    data_to_edit = {"name": "test_cat__2"}
    cat_to_update = await cat_repository.update(cat.id, data_to_edit)
    await session.commit()
    assert cat_to_update.name == data_to_edit["name"]
    assert cat_to_update.id == cat.id
    await delete_test_category(session, cat_repository, cat.id)

async def test_create_product(session, product_repository, cat_repository):
    product = await create_test_product(session, product_repository, cat_repository)
    assert product.name == test_product_data["name"]
    assert product.description == test_product_data["description"]
    assert product.price == test_product_data["price"]
    assert product.category_id == test_product_data["category_id"]
    await delete_test_product(session, product_repository, cat_repository, product)

async def test_product_delete(session, product_repository, cat_repository):
    product = await create_test_product(session, product_repository, cat_repository)
    await delete_test_product(session, product_repository,cat_repository, product)
    with pytest.raises(HTTPException) as exc_info:
        await product_repository.get(product.id)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

async def test_list_product(session, product_repository, cat_repository):
    product = await create_test_product(session, product_repository, cat_repository)
    filters = ProductFilter(category_id=product.category_id,
                            gender=GenderEnum.man,
                            min_price=20,
                            max_price=55,
                            )
    products = await product_repository.list(filters)
    assert len(products) == 1
    assert products[0].name == product.name
    assert 20<=int(product.price)<=55
    await delete_test_product(session, product_repository, cat_repository, product)

async def test_product_change(session, product_repository, cat_repository):
    product = await create_test_product(session, product_repository, cat_repository)
    update_data = {
        "name": "new_name",
        "description": "some_test_description",
        "price": "55",
        "gender": GenderEnum.man,
    }
    product = await product_repository.update(product.id, update_data)
    assert product.name == "new_name"
    assert int(product.price) == 55
    await delete_test_product(session, product_repository, cat_repository, product)