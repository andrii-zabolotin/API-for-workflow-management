from src.api_v1.workflow import router as workflow_router
from src.api_v1.start_node import router as start_node_router
from src.api_v1.edge import router as edge_router
from src.api_v1.end_node import router as end_node_router
from src.api_v1.message_node import router as message_node_router
from src.api_v1.condition_node import router as condition_node_router

all_routers = [
    workflow_router,
    start_node_router,
    message_node_router,
    condition_node_router,
    end_node_router,
    edge_router,
]
