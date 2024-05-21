from typing import Optional

from pydantic import BaseModel

from src.models import Status


class MessageNodeKwargs(BaseModel):
    workflow_id: Optional[int] = None
    has_out_edge: Optional[bool] = None
    status: Optional[Status] = None


class MessageNodeUpdate(BaseModel):
    status: Optional[str] = None
    message: Optional[str] = None


class MessageNodeCreate(BaseModel):
    status: Status
    message: str
    workflow_id: int


class MessageNodeRead(BaseModel):
    id: int
    status: str
    message: str
    workflow_id: int
    has_out_edge: bool
