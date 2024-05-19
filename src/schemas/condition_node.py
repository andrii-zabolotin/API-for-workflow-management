from typing import Optional

from pydantic import BaseModel

from src.models import Status


class ConditionNodeKwargs(BaseModel):
    workflow_id: Optional[int] = None
    yes_edge_count: Optional[bool] = None
    no_edge_count: Optional[bool] = None
    status_condition: Optional[Status] = None


class ConditionNodeUpdate(BaseModel):
    status_condition: Optional[Status] = None


class ConditionNodeCreate(BaseModel):
    status_condition: Status
    workflow_id: int


class ConditionNodeRead(BaseModel):
    id: int
    workflow_id: int
    yes_edge_count: bool
    no_edge_count: bool
    status_condition: Status
