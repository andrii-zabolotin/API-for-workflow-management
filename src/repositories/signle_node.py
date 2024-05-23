from fastapi import HTTPException, status

from sqlalchemy import select, func

from src.repositories.node import NodeRepository


class SingleInstanceNodeRepository(NodeRepository):
    async def add(self, values: dict):
        query = select(func.count(self._model.id)).where(self._model.workflow_id == values["workflow_id"])
        result = await self._session.execute(query)
        count = result.scalar_one()
        if count >= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot create more than one {self._model.__name__}s in this workflow")
        else:
            return await super().add(values=values)