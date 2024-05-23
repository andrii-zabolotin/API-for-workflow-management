from fastapi import FastAPI
from sqlalchemy import event

from src.api_v1.routers import all_routers
from src.models import Edge, MessageNode, StartNode, ConditionNode, EdgeType

app = FastAPI(
    title="Workflow management"
)


for router in all_routers:
    app.include_router(router)


@app.get("/ping")
async def ping():
    return {"message": "pong"}


@event.listens_for(Edge, 'after_delete')
def update_edge_counts(mapper, connection, target):
    """
    Updates the node's edge counts when edge is deleted.

    Params:
        target: Deleted edge.
    """
    start_node = target.start_node

    if start_node:
        if isinstance(start_node, MessageNode):
            connection.execute(
                start_node.__table__.update()
                .where(start_node.__table__.c.id == start_node.id)
                .values(has_out_edge=False)
            )
        elif isinstance(start_node, StartNode):
            connection.execute(
                start_node.__table__.update()
                .where(start_node.__table__.c.id == start_node.id)
                .values(has_out_edge=False)
            )

        elif isinstance(start_node, ConditionNode):
            if target.edge_type == EdgeType.YES:
                connection.execute(
                    start_node.__table__.update()
                    .where(start_node.__table__.c.id == start_node.id)
                    .values(yes_edge_count=False)
                )
            elif target.edge_type == EdgeType.NO:
                connection.execute(
                    start_node.__table__.update()
                    .where(start_node.__table__.c.id == start_node.id)
                    .values(no_edge_count=False)
                )
