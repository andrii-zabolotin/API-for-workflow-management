from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.repositories.start_node import StartNodeRepository
from src.schemas.start_node import StartNodeKwargs, StartNodeManage, StartNodeRead

router = APIRouter(
    prefix="/node/start",
    tags=["start-nodes"]
)


@router.get("/list", response_model=List[StartNodeRead])
async def list_nodes(
        workflow_id: int = None,
        out_edge: bool = None,
        session: AsyncSession = Depends(get_async_session)
):
    filters = StartNodeKwargs(workflow_id=workflow_id, out_edge_count=out_edge)
    return await StartNodeRepository(session=session).list(**filters.model_dump())


@router.get("/{node_id}", response_model=StartNodeRead)
async def get_node(
        node_id: int,
        session: AsyncSession = Depends(get_async_session)
):
    return await StartNodeRepository(session=session).get(model_object_id=node_id)


@router.post("/create")
async def create_node(
        node_in: StartNodeManage,
        session: AsyncSession = Depends(get_async_session)
):
    return await StartNodeRepository(session=session).add(values=node_in.model_dump())


@router.delete("/delete/{node_id}")
async def delete_node(
        node_id: int,
        session: AsyncSession = Depends(get_async_session)
):
    return await StartNodeRepository(session=session).delete(model_object_id=node_id)
