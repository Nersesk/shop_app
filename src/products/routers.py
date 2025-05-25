import asyncio
import json
from typing import Annotated, Optional

from fastapi import APIRouter, HTTPException, Form, UploadFile, File, Body, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse
from .schemas import ProductRead, ProductCreateForm, ProductFilter, CategoryRead, GenderEnum, ProductSpecificationCreate
from .repository import ProductCategoryRepository, ProductRepository
from ..unit_of_work import UnitOfWork, get_async_session
from ..utils import save_image, delete_image
import os

from starlette import status
products_router = APIRouter(
    prefix="/products",
    tags=["products"],
)


@products_router.get("/categories/{_id}", response_model=CategoryRead)
async def get_category(_id: int):
    async with UnitOfWork() as session:
        repository = ProductCategoryRepository(session.session)
        category = await repository.get(_id)
        return category.model_validate(CategoryRead)


@products_router.post("/categories", response_model=CategoryRead)
async def create_category(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    file: Annotated[UploadFile | None, File()],
    name: str = Form(...),

):
    image_path = None
    if file:
        image_path = await save_image("categories", file)
    repository = ProductCategoryRepository(session)
    category = await repository.create({
        "name": name,
        "image": image_path
    })
    try:
        await session.commit()
        await session.flush()
    except Exception as e:
        await session.rollback()
        await delete_image(image_path)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"details: {e}"
        )
    return category


@products_router.get("/categories", response_model=list[CategoryRead| None])
async def get_categories():
    async with UnitOfWork() as session:
        repository = ProductCategoryRepository(session.session)
        categories = await repository.list()
    return categories


@products_router.put("/categories/{id}", response_model=CategoryRead)
async def update_category(_id: int,
                          file: Annotated[UploadFile | None, File()],
                          name: str = Form(...),
                          ):
    async with UnitOfWork() as session:
        repository = ProductCategoryRepository(session.session)
        category =  await repository.update(_id, {
            "name": name,
            "image": file
        })
        session.session.commit()
        session.session.flush(category)
    return category.model_validate(CategoryRead)

@products_router.delete("/categories/{_id}",)
async def delete_category(_id: int) -> JSONResponse:
    async with UnitOfWork() as session:
        repository = ProductCategoryRepository(session.session)
        await repository.delete(_id)
    return JSONResponse(status_code=status.HTTP_200_OK, content={"status": "success"})

@products_router.get("/products")
async def get_products(filters: Annotated[ProductFilter, Depends()]) -> list[ProductRead]:
    async with UnitOfWork() as session:
        repository = ProductRepository(session.session)
        products = await repository.list(filters)
        return products

@products_router.post("/products", response_model=ProductRead)
async def create_product(
        form_data: ProductCreateForm = Depends(),
        product_images: Annotated[list[UploadFile] | None, File()] = None,
):
    product_data = {
        "name": form_data.name,
        "description": form_data.description,
        "price": form_data.price,
        "gender": form_data.gender,
        "category_id": form_data.category_id,
    }
    async with UnitOfWork() as session:
        repository = ProductRepository(session.session)
        product = await repository.create(product_data)
        await session.session.flush()  # Ensure ID is populated

        if product_images:
            product_images_folder = os.path.join("products", f"product_{product.id}")
            images = [save_image(product_images_folder, image) for image in product_images]
            image_list = await asyncio.gather(*images)
            await repository.create_images(image_list, product.id)

        if form_data.specifications:
            await repository.add_specifications(form_data.specifications, product.id)
        product = await repository.get(product.id)
        return product


@products_router.get("/products/{_id}", response_model=ProductRead)
async def get_product(_id: int):
    async with UnitOfWork() as session:
        repository = ProductRepository(session.session)
        product = await repository.get(_id)
        return product


@products_router.post("/products/{_id}", response_model=ProductRead)
async def update_product(_id: int ,
                      form_data: ProductCreateForm = Depends(),
                      product_images: Annotated[list[UploadFile] | None, File()] = None
                      ):
    async with UnitOfWork() as session:
        repository = ProductRepository(session.session)
        product_data = {
            "name": form_data.name,
            "description": form_data.description,
            "price": form_data.price,
            "gender": form_data.gender,
            "category_id": form_data.category_id,
        }
        product = await repository.update(_id, product_data)
        await repository.update_product_images(product, product_images)
        await repository.update_product_specifications(product, form_data.specifications)
        await session.session.flush()
        return product


@products_router.delete("/products/{_id}")
async def delete_product(_id: int):
    async with UnitOfWork() as session:
        repository = ProductRepository(session.session)
        await repository.delete(_id)



