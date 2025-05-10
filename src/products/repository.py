import asyncio
import json
import os
from typing import Optional

from fastapi import HTTPException
from starlette import status
from .models import Category, Product, ProductImage, ProductSpecification
from .schemas import CategoryRead, ProductRead, ProductFilter
from ..interfaces.abs_repository import Repository
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, exists, and_, delete, update
from sqlalchemy.orm import selectinload
from ..utils import delete_image, save_image


class ProductCategoryRepository(Repository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, _id):
        cat = await self._get(_id)
        if cat:
            return CategoryRead.model_validate(cat)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with id {_id} not found"
        )

    async def _get(self, _id):
        return await self.session.get(Category, _id)


    async def list(self):
        results =  await self.session.execute(select(Category))
        categories = results.scalars().all()
        return [CategoryRead.model_validate(cat) for cat in categories]

    async def create(self, payload: dict):
        category_name = payload.get("name")
        stmt = select(exists().where(Category.name == category_name))
        result = await self.session.execute(stmt)
        exists_ = result.scalar()

        if exists_:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Category with provided name already exists!"
            )
        category = Category(**payload)
        self.session.add(category)
        return category

    async def update(self, _id, payload):
        cat = await self._get(_id)
        if cat:
            for(key, value) in payload.items():
                if key == "image":
                    image_path = None
                    if cat.image:
                        await delete_image(cat.image)
                    if value:
                        image_path = await save_image("categories", value)
                    setattr(cat, key, image_path)
                else:
                    setattr(cat, key, value)
            return CategoryRead.model_validate(cat)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Category with id {_id} not found"
        )
    async def delete(self, _id):
        cat = await self._get(_id)
        if cat:
            if cat.image:
                await delete_image(cat.image)
            await self.session.delete(cat)
            return True
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Category with id {_id} not found"
        )

class ProductRepository(Repository):
    def __init__(self, session):
        self.session: AsyncSession = session
    async def get(self, _id):
        product = await self._get(_id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Product not found")
        return ProductRead.model_validate(product)

    async def _get(self, _id):
        stmt = (
            select(Product).where(Product.id == _id).options(selectinload(Product.images),
                                                             selectinload(Product.specifications))
        )
        product = await self.session.execute(stmt)
        return product.scalars().first()

    async def list(self, filters: Optional[ProductFilter]):
        stmt = (
            select(Product)
            .options(
                selectinload(Product.images),
                selectinload(Product.specifications)
            )
        )

        conditions = []
        if filters.category_id:
            conditions.append(Product.category_id == filters.category_id)
        if filters.gender:
            conditions.append(Product.gender == filters.gender)
        if filters.min_price :
            conditions.append(Product.price >= filters.min_price)
        if filters.max_price:
            conditions.append(Product.price <= filters.max_price)
        if filters.search:
            search_term = f"%{filters.search.lower()}%"
            conditions.append(Product.name.ilike(search_term))  # assumes Product has 'name'

        if conditions:
            stmt = stmt.where(and_(*conditions))

        products = await self.session.execute(stmt)
        result = products.scalars()
        return [ProductRead.model_validate(product) for product in result]

    async def create(self, payload: dict):
        product = Product(**payload)
        self.session.add(product)
        return product

    async def create_images(self, images, product_id):
        for image in images:
            self.session.add(ProductImage(image_url=image, product_id=product_id))

    async def add_specifications(self, specs, product_id):
        parsed_specs = json.loads(specs)
        for key, value in parsed_specs.items():
            self.session.add(ProductSpecification(key=key, value=value, product_id=product_id))

    async def update(self, _id, payload):
        product = await self.get(_id)
        if product:
            for (key, value) in payload.items():
                setattr(product, key, value)
            return product
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Product with id {_id} not found")

    async def update_product_images(self, product: Product, images):
        for image in product.images:
            await delete_image(image.image_url)
        stmt = (delete(ProductImage).where(Product.id == product.id))
        await self.session.execute(stmt)
        if images:
            product_images_folder = os.path.join("products", f"product_{product.id}")
            images = [save_image(product_images_folder, image) for image in images]
            image_list = await asyncio.gather(*images)
            await self.create_images(image_list, product.id)


    async def add_product_image(self, image_url, product_id):
        self.session.add(ProductImage(image_url=image_url, product_id =product_id))


    async def delete(self, _id):
        product = await self._get(_id)
        if product:
            await self.update_product_images(product, [])
            await self.update_product_specifications(product)
            await self.session.delete(product)
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Product with id {_id} not found")


    async def update_product_specifications(self, product: Product, specs=""):
        stmt = (delete(ProductSpecification).where(Product.id == product.id))
        await self.session.execute(stmt)
        if specs:
            await self.add_specifications(specs, product.id)
