from sqlalchemy.ext.asyncio import AsyncSession

from src.models import ConditionNode
from src.repositories.node import NodeRepository


class ConditionNodeRepository(NodeRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, model=ConditionNode)
