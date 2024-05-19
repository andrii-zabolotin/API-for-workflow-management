from sqlalchemy.ext.asyncio import AsyncSession

from src.models import MessageNode
from src.repositories.node import NodeRepository


class MessageNodeRepository(NodeRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, model=MessageNode)
