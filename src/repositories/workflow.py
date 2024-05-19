from sqlalchemy import Insert, insert, Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models import WorkFlow
from src.repositories.repository_base import BaseRepository


class WorkFlowRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(model=WorkFlow, session=session)

    def construct_add_stmt(self, values) -> Insert:
        stmt = insert(self._model).returning(self._model)
        return stmt

    def construct_get_stmt(self, id: int) -> Select:
        stmt = select(self._model).where(self._model.id == id).options(selectinload(self._model.start_nodes)).options(selectinload(self._model.message_nodes)).options(selectinload(self._model.condition_nodes)).options(selectinload(self._model.end_nodes)).options(selectinload(self._model.edges))
        return stmt
