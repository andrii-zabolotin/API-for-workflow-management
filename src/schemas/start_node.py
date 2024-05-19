from typing import Optional

from pydantic import BaseModel


class StartNodeKwargs(BaseModel):
    workflow_id: Optional[int] = None
    out_edge_count: Optional[bool] = None


class StartNodeManage(BaseModel):
    workflow_id: int


class StartNodeRead(BaseModel):
    id: int
    workflow_id: int
    out_edge_count: bool
