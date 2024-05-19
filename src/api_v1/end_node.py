from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.repositories.end_node import EndNodeRepository
from src.schemas.end_node import *

router = APIRouter(
    prefix="/node/end",
    tags=["end-nodes"]
)


@router.get("/list", response_model=List[EndNodeRead])
async def list_nodes(
        session: AsyncSession = Depends(get_async_session)
):
    return await EndNodeRepository(session=session).list()


@router.get("/{node_id}", response_model=EndNodeRead)
async def get_node(
        node_id: int,
        session: AsyncSession = Depends(get_async_session)
):
    return await EndNodeRepository(session=session).get(model_object_id=node_id)


@router.post("/create")
async def create_node(
        node_in: EndNodeManage,
        session: AsyncSession = Depends(get_async_session)
):
    return await EndNodeRepository(session=session).add(values=node_in.model_dump())


@router.delete("/delete/{node_id}")
async def delete_node(
        node_id: int,
        session: AsyncSession = Depends(get_async_session)
):
    return await EndNodeRepository(session=session).delete(model_object_id=node_id)
