from pydantic import BaseModel


class EndNodeManage(BaseModel):
    workflow_id: int


class EndNodeRead(BaseModel):
    id: int
    workflow_id: int
