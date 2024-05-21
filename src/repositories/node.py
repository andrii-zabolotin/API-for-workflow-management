from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.repository_base import BaseRepository


class NodeRepository(BaseRepository):
    def __init__(self, session: AsyncSession, model):
        super().__init__(session=session, model=model)

    async def add(self, values: dict):
        try:
            node = self._model(**values)
            self._session.add(node)
            await self._session.commit()
            return node
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Specified workflow ID doesn't exist")

    async def update(self, values: dict, model_object_id: int):
        try:
            node = await self._session.execute(select(self._model).where(self._model.id == model_object_id))
            node = node.scalar_one_or_none()
            if not node:
                raise HTTPException(status_code=404, detail=f"{self._model.__name__} with the specified id was not found")
            for c, v in values.items():
                if not hasattr(self._model, c):
                    raise ValueError(f"Invalid column name {c}")
                setattr(node, c, v)

            await self._session.commit()
            return node
        except IntegrityError:
            raise HTTPException(status_code=404, detail="Workflow with specified id was not found")
