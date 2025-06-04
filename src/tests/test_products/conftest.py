import random
import string

import pytest
from sqlalchemy import delete
from src.products.models import Product, Category
from src.products.repository import ProductCategoryRepository, ProductRepository
from src.tests.test_products.test_repositories import create_test_category, test_product_data


@pytest.fixture
def cat_repository(session):
    return ProductCategoryRepository(session)

@pytest.fixture
def product_repository(session):
    return ProductRepository(session)

@pytest.fixture
async def cleanup_categories(session):
    stmt = delete(Category)
    await session.execute(stmt)


@pytest.fixture
async def cleanup_product(session, cleanup_categories):
    stmt = delete(Product)
    await session.execute(stmt)

@pytest.fixture
async def create_product_category(session, cleanup_categories, cat_repository):
    random_name = ''.join(random.choices(string.ascii_letters + string.digits, k=5))
    tmp_data = {
        "name": random_name,
        "image": "../assets/test_image.jpg"
    }
    return await create_test_category(session, cat_repository, tmp_data)

@pytest.fixture
async def create_product(session, product_repository, create_product_category):
    cat_id = create_product_category.id
    tmp_data = test_product_data
    tmp_data['category_id'] = cat_id
    product = await product_repository.create(tmp_data)
    await session.commit()
    return product