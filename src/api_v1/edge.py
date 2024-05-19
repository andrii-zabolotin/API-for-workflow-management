from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.repositories.edge import EdgeRepository
from src.schemas.edge import EdgeRead, EdgeCreate, EdgeUpdate, EdgeKwargs

router = APIRouter(
    prefix="/edge",
    tags=["edge"]
)


@router.get("/list", response_model=List[EdgeRead])
async def list_edges(
        workflow_id: int = None,
        session: AsyncSession = Depends(get_async_session)
):
    filters = EdgeKwargs(workflow_id=workflow_id)
    return await EdgeRepository(session=session).list(**filters.model_dump())


@router.get("{edge_id}", response_model=EdgeRead)
async def get_edge(
        edge_id: int,
        session: AsyncSession = Depends(get_async_session)
):
    return await EdgeRepository(session=session).get(model_object_id=edge_id)


@router.post("/create")
async def create_edge(
        edge_in: EdgeCreate,
        session: AsyncSession = Depends(get_async_session)
):
    return await EdgeRepository(session=session).add(values=edge_in.model_dump())


@router.patch("/update/{edge_id}")
async def update_edge(
        edge_id: int,
        edge_in_data: EdgeUpdate,
        session: AsyncSession = Depends(get_async_session)
):
    return await EdgeRepository(session=session).update(model_object_id=edge_id, values=edge_in_data.model_dump())


@router.delete("/delete/{edge_id}")
async def delete_edge(
        edge_id: int,
        session: AsyncSession = Depends(get_async_session)
):
    return await EdgeRepository(session=session).delete(model_object_id=edge_id)
