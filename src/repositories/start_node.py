from sqlalchemy.ext.asyncio import AsyncSession

from src.models import StartNode
from src.repositories.signle_node import SingleInstanceNodeRepository


class StartNodeRepository(SingleInstanceNodeRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, model=StartNode)
