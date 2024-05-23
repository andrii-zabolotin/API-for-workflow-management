from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import StreamingResponse

from src.database import get_async_session
from src.repositories.workflow import WorkFlowRepository
from src.schemas.workflow import WorkflowRead, WorkflowGet

router = APIRouter(
    prefix="/workflow",
    tags=["workflow"]
)


@router.get("/list", response_model=List[WorkflowRead])
async def list_workflows(
        session: AsyncSession = Depends(get_async_session)
):
    return await WorkFlowRepository(session=session).list()


@router.get("/{workflow_id}", response_model=WorkflowGet)
async def get_workflow(
        workflow_id: int,
        session: AsyncSession = Depends(get_async_session)
):
    return await WorkFlowRepository(session=session).get(model_object_id=workflow_id)


@router.get("/{workflow_id}/path")
async def start_workflow(
        workflow_id: int,
        session: AsyncSession = Depends(get_async_session)
):
    return await WorkFlowRepository(session=session).get_path(workflow_id=workflow_id)


@router.get("/{workflow_id}/path/image")
async def start_workflow(
        workflow_id: int,
        session: AsyncSession = Depends(get_async_session)
):
    buf = await WorkFlowRepository(session=session).get_path_image(workflow_id=workflow_id)
    return StreamingResponse(buf, media_type="image/png")


@router.post("/create", status_code=201)
async def create_workflow(
        session: AsyncSession = Depends(get_async_session)
):
    return await WorkFlowRepository(session=session).add(values=None)


@router.delete("/delete/{workflow_id}", status_code=204)
async def delete_workflow(
        workflow_id: int,
        session: AsyncSession = Depends(get_async_session)
):
    return await WorkFlowRepository(session=session).delete(model_object_id=workflow_id)
