import asyncio
import json
from typing import Annotated, Optional

from fastapi import APIRouter, HTTPException, Form, UploadFile, File, Body, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse
from .schemas import ProductRead, ProductCreateForm, ProductFilter, CategoryRead, GenderEnum, ProductSpecificationCreate
from .repository import ProductCategoryRepository, ProductRepository
from ..session_create import  get_async_session
from ..utils import save_image, delete_image
import os

from starlette import status
products_router = APIRouter(
    prefix="/products",
    tags=["products"],
)


@products_router.get("/categories/{_id}", response_model=CategoryRead)
async def get_category(_id: int,
                       session: Annotated[AsyncSession, Depends(get_async_session)]):
    repository = ProductCategoryRepository(session)
    category = await repository.get(_id)
    return category.model_validate(category)


@products_router.post("/categories", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
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
async def get_categories(session: Annotated[AsyncSession, Depends(get_async_session)],):
    repository = ProductCategoryRepository(session)
    categories = await repository.list()
    return categories


@products_router.put("/categories/{_id}", response_model=CategoryRead)
async def update_category(_id: int,
                          session: Annotated[AsyncSession, Depends(get_async_session)],
                          file: Annotated[UploadFile | None, File()],
                          name: str = Form(...),
                          ):
    repository = ProductCategoryRepository(session)
    category =  await repository.update(_id, {
        "name": name,
        "image": file
    })
    try:
        await session.commit()
        await session.flush()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"details: {e}"
        )
    return category.model_validate(category)

@products_router.delete("/categories/{_id}",)
async def delete_category(_id: int,
                          session: Annotated[AsyncSession, Depends(get_async_session)]) -> JSONResponse:
    repository = ProductCategoryRepository(session)
    try:
        await repository.delete(_id)
        await session.commit()
        return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content={"status": "success"})
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"details: {e}"
        )
@products_router.get("/products")
async def get_products(filters: Annotated[ProductFilter, Depends()],
                       session: Annotated[AsyncSession, Depends(get_async_session)]) -> list[ProductRead]:
    repository = ProductRepository(session)
    products = await repository.list(filters)
    return products

@products_router.post("/products", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
async def create_product(
        session: Annotated[AsyncSession, Depends(get_async_session)],
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
    repository = ProductRepository(session)
    product = await repository.create(product_data)
    await session.flush()

    if product_images:
        product_images_folder = os.path.join("products", f"product_{product.id}")
        images = [save_image(product_images_folder, image) for image in product_images]
        image_list = await asyncio.gather(*images)
        await repository.create_images(image_list, product.id)

    if form_data.specifications:
        await repository.add_specifications(form_data.specifications, product.id)
    try:
        await session.commit()
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"details: {e}"
        )
    product = await repository.get(product.id)

    return product


@products_router.get("/products/{_id}", response_model=ProductRead)
async def get_product(_id: int,
                      session: Annotated[AsyncSession, Depends(get_async_session)],
                      ):
    repository = ProductRepository(session)
    product = await repository.get(_id)
    return product


@products_router.put("/products/{_id}", response_model=ProductRead)
async def update_product(
                 _id: int ,
                 session: Annotated[AsyncSession, Depends(get_async_session)],
                 form_data: ProductCreateForm = Depends(),
                 product_images: Annotated[list[UploadFile] | None, File()] = None
                      ):
    repository = ProductRepository(session)
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
    try:
        await session.commit()
        await session.flush()
        return product
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"details: {e}"
        )


@products_router.delete("/products/{_id}")
async def delete_product(_id: int,
                         session: Annotated[AsyncSession, Depends(get_async_session)]):
    repository = ProductRepository(session)
    try:
        await repository.delete(_id)
        await session.commit()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"details: {e}"
        )
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content={"status": "success"})



