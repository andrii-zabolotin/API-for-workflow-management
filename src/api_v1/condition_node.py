from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.repositories.condition_node import ConditionNodeRepository
from src.schemas.condition_node import *

router = APIRouter(
    prefix="/node/condition",
    tags=["condition-nodes"]
)


@router.get("/list", response_model=List[ConditionNodeRead])
async def list_nodes(
        workflow_id: int = None,
        status_condition: Status = None,
        yes_edge_count: bool = None,
        no_edge_count: bool = None,
        session: AsyncSession = Depends(get_async_session)
):
    filters = ConditionNodeKwargs(
        workflow_id=workflow_id,
        yes_edge_count=yes_edge_count,
        no_edge_count=no_edge_count,
        status_condition=status_condition,

    )
    return await ConditionNodeRepository(session=session).list(**filters.model_dump())


@router.get("/{node_id}", response_model=ConditionNodeRead)
async def get_node(
        node_id: int,
        session: AsyncSession = Depends(get_async_session)
):
    return await ConditionNodeRepository(session=session).get(model_object_id=node_id)


@router.post("/create", status_code=201)
async def create_node(
        node_in: ConditionNodeCreate,
        session: AsyncSession = Depends(get_async_session)
):
    return await ConditionNodeRepository(session=session).add(values=node_in.model_dump())


@router.patch("/update/{node_id}")
async def update_node(
        node_id: int,
        node_in_data: ConditionNodeUpdate,
        session: AsyncSession = Depends(get_async_session)
):
    return await ConditionNodeRepository(session=session).update(model_object_id=node_id, values=node_in_data.model_dump())


@router.delete("/delete/{node_id}", status_code=204)
async def delete_node(
        node_id: int,
        session: AsyncSession = Depends(get_async_session)
):
    return await ConditionNodeRepository(session=session).delete(model_object_id=node_id)
