from typing import Optional

from pydantic import BaseModel


class StartNodeKwargs(BaseModel):
    workflow_id: Optional[int] = None
    has_out_edge: Optional[bool] = None


class StartNodeManage(BaseModel):
    workflow_id: int


class StartNodeRead(BaseModel):
    id: int
    workflow_id: int
    has_out_edge: bool
