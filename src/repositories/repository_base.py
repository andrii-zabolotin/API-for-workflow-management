from typing import Type

from fastapi import HTTPException
from sqlalchemy import select, insert, update, delete, Insert, and_

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.selectable import Select

from src.models import Base


class BaseRepository:
    def __init__(self, session: AsyncSession, model: Type[Base]):
        self._session = session
        self._model = model

    def construct_get_stmt(self, id: int) -> Select:
        stmt = select(self._model).where(self._model.id == id)
        return stmt

    async def get(self, model_object_id: int):
        query = self.construct_get_stmt(id=model_object_id)
        result = await self._session.execute(query)
        model_object = result.scalar_one_or_none()
        if not model_object:
            raise HTTPException(status_code=404, detail=f"{self._model.__name__} with the specified id was not found")
        return model_object

    def construct_list_stmt(self, filters) -> Select:
        stmt = select(self._model)
        where_clauses = []
        for c, v in filters.items():
            if not hasattr(self._model, c):
                raise ValueError(f"Invalid column name {c}")
            if v:
                where_clauses.append(getattr(self._model, c) == v)

        if len(where_clauses) == 1:
            stmt = stmt.where(where_clauses[0])
        elif len(where_clauses) > 1:
            stmt = stmt.where(and_(*where_clauses))

        return stmt

    async def list(self, **filters):
        query = self.construct_list_stmt(filters)
        result = await self._session.execute(query)
        return result.scalars().all()

    def construct_add_stmt(self, values: dict) -> Insert:
        stmt = insert(self._model).values(**values).returning(self._model)
        return stmt

    async def add(self, values: dict):
        stmt = self.construct_add_stmt(values=values)
        result = await self._session.execute(stmt)
        await self._session.commit()
        return result.scalar_one()

    def construct_update_stmt(self, values: dict, id: int):
        stmt = update(self._model).where(self._model.id == id).values(**values).returning(self._model)
        return stmt

    async def update(self, values: dict, model_object_id: int):
        stmt = self.construct_update_stmt(values=values, id=model_object_id)
        result = await self._session.execute(stmt)
        model_object = result.scalar_one_or_none()
        if not model_object:
            raise HTTPException(status_code=404, detail=f"{self._model.__name__} with the specified id was not found")
        await self._session.commit()
        return model_object

    def construct_delete_stmt(self, id: int):
        stmt = delete(self._model).where(self._model.id == id)
        return stmt

    async def delete(self, model_object_id: int):
        result = await self._session.execute(self.construct_get_stmt(id=model_object_id))
        node = result.scalar_one_or_none()
        if not node:
            raise HTTPException(status_code=404, detail=f"{self._model.__name__} with the specified id was not found")
        await self._session.delete(node)
        await self._session.commit()
