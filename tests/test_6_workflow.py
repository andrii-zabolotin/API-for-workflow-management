from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Status, EdgeType
from src.repositories.condition_node import ConditionNodeRepository
from src.repositories.edge import EdgeRepository
from src.repositories.end_node import EndNodeRepository
from src.repositories.message_node import MessageNodeRepository
from src.repositories.start_node import StartNodeRepository


class TestWorkflow:
    workflow_id = None

    async def test_create_workflow(
            self,
            ac: AsyncClient
    ):
        response = await ac.post("/workflow/create")

        assert response.status_code == 201
        TestWorkflow.workflow_id = response.json()["id"]

    async def test_get_workflow(
            self,
            ac: AsyncClient
    ):
        response = await ac.get(f"/workflow/{TestWorkflow.workflow_id}")

        assert response.status_code == 200
        assert response.json()["id"] == TestWorkflow.workflow_id

    async def test_list_workflow(
            self,
            ac: AsyncClient,
    ):
        response = await ac.get("/workflow/list")

        assert response.status_code == 200
        assert response.json() != []

    async def test_path_workflow(
            self,
            ac: AsyncClient,
            session: AsyncSession,
    ):
        start_node = await StartNodeRepository(session=session).add({
            "workflow_id": TestWorkflow.workflow_id
        })
        end_node = await EndNodeRepository(session=session).add({
            "workflow_id": TestWorkflow.workflow_id
        })
        message_node_1 = await MessageNodeRepository(session=session).add({
            "status": Status.SENT,
            "message": "Hello, i'm fine",
            "workflow_id": TestWorkflow.workflow_id
        })
        message_node_2 = await MessageNodeRepository(session=session).add({
                "status": Status.PENDING,
                "message": "How are you?",
                "workflow_id": TestWorkflow.workflow_id
            })
        condition_node = await ConditionNodeRepository(session=session).add({
                "status_condition": Status.SENT,
                "workflow_id": TestWorkflow.workflow_id
            })
        await EdgeRepository(session=session).add({
                "workflow_id": TestWorkflow.workflow_id,
                "start_node_id": start_node.id,
                "end_node_id": message_node_1.id,
                "edge_type": EdgeType.DEFAULT
            })
        await EdgeRepository(session=session).add({
                "workflow_id": TestWorkflow.workflow_id,
                "start_node_id": message_node_1.id,
                "end_node_id": condition_node.id,
                "edge_type": EdgeType.DEFAULT
            })
        await EdgeRepository(session=session).add({
                "workflow_id": TestWorkflow.workflow_id,
                "start_node_id": condition_node.id,
                "end_node_id": message_node_2.id,
                "edge_type": EdgeType.NO
            })
        await EdgeRepository(session=session).add({
                "workflow_id": TestWorkflow.workflow_id,
                "start_node_id": condition_node.id,
                "end_node_id": end_node.id,
                "edge_type": EdgeType.YES
            })

        response = await ac.get(f"/workflow/{TestWorkflow.workflow_id}/path")
        assert response.status_code == 200
        assert response.json() == [start_node.id, message_node_1.id, condition_node.id, end_node.id]

    async def test_delete_workflow(
            self,
            ac: AsyncClient,
    ):
        response = await ac.delete(f"/workflow/delete/{TestWorkflow.workflow_id}")

        assert response.status_code == 204
