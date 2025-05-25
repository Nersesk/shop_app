import pytest

from src.products.repository import ProductCategoryRepository, ProductRepository


@pytest.fixture
def cat_repository(session):
    return ProductCategoryRepository(session)

@pytest.fixture
def product_repository(session):
    return ProductRepository(session)