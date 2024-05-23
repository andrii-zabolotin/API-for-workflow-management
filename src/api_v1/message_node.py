from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.repositories.message_node import MessageNodeRepository
from src.schemas.message_node import *

router = APIRouter(
    prefix="/node/message",
    tags=["message-nodes"]
)


@router.get("/list", response_model=List[MessageNodeRead])
async def list_nodes(
        workflow_id: int = None,
        out_edge: bool = None,
        status: Status = None,
        session: AsyncSession = Depends(get_async_session)
):
    filters = MessageNodeKwargs(workflow_id=workflow_id, has_out_edge=out_edge, status=status)
    return await MessageNodeRepository(session=session).list(**filters.model_dump())


@router.get("/{node_id}", response_model=MessageNodeRead)
async def get_node(
        node_id: int,
        session: AsyncSession = Depends(get_async_session)
):
    return await MessageNodeRepository(session=session).get(model_object_id=node_id)


@router.post("/create", status_code=201)
async def create_node(
        node_in: MessageNodeCreate,
        session: AsyncSession = Depends(get_async_session)
):
    return await MessageNodeRepository(session=session).add(values=node_in.model_dump())


@router.patch("/update/{node_id}")
async def update_node(
        node_id: int,
        node_in_data: MessageNodeUpdate,
        session: AsyncSession = Depends(get_async_session)
):
    return await MessageNodeRepository(session=session).update(model_object_id=node_id, values=node_in_data.model_dump())


@router.delete("/delete/{node_id}", status_code=204)
async def delete_node(
        node_id: int,
        session: AsyncSession = Depends(get_async_session)
):
    return await MessageNodeRepository(session=session).delete(model_object_id=node_id)
