from fastapi import HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import EndNode
from src.repositories.node import NodeRepository


class EndNodeRepository(NodeRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, model=EndNode)

    async def add(self, values: dict):
        query = select(func.count(EndNode.id)).where(EndNode.workflow_id == values["workflow_id"])
        result = await self._session.execute(query)
        count = result.scalar_one()
        if count >= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot create more than one {self._model.__name__}s in this workflow")
        else:
            return await super().add(values=values)
