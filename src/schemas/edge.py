from typing import Optional

from pydantic import BaseModel

from src.models import EdgeType


class EdgeKwargs(BaseModel):
    workflow_id: Optional[int] = None


class EdgeRead(BaseModel):
    id: int
    start_node_id: int
    end_node_id: int
    workflow_id: int
    edge_type: EdgeType


class EdgeCreate(BaseModel):
    workflow_id: int
    start_node_id: int
    end_node_id: int
    edge_type: EdgeType


class EdgeUpdate(BaseModel):
    start_node_id: Optional[int] = None
    end_node_id: Optional[int] = None
    edge_type: Optional[EdgeType] = None
