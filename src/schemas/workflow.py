from datetime import datetime

from pydantic import BaseModel

from src.schemas.condition_node import ConditionNodeRead
from src.schemas.edge import EdgeRead
from src.schemas.end_node import EndNodeRead
from src.schemas.message_node import MessageNodeRead
from src.schemas.start_node import StartNodeRead


class WorkflowRead(BaseModel):
    id: int
    created_at: datetime


class WorkflowGet(BaseModel):
    id: int
    created_at: datetime
    start_nodes: list[StartNodeRead]
    message_nodes: list[MessageNodeRead]
    condition_nodes: list[ConditionNodeRead]
    end_nodes: list[EndNodeRead]
    edges: list[EdgeRead]
