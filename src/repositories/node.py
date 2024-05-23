from fastapi import HTTPException, status

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
