from sqlalchemy.ext.asyncio import AsyncSession

from src.models import EndNode
from src.repositories.signle_node import SingleInstanceNodeRepository


class EndNodeRepository(SingleInstanceNodeRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, model=EndNode)
