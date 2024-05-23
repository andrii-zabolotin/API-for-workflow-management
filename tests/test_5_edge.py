from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import MessageNode, EdgeType
from src.repositories.condition_node import ConditionNodeRepository
from src.repositories.edge import EdgeRepository
from src.repositories.message_node import MessageNodeRepository
from src.repositories.start_node import StartNodeRepository


class TestEdge:
    edge = None
    message_node_edge = None
    condition_no_node_edge = None
    condition_yes_node_edge = None

    async def test_create_edge(
            self, ac: AsyncClient,
            get_or_create_workflow_id: int,
            get_or_create_message_node_id: int,
            get_or_create_start_node_id: int,
            session: AsyncSession
    ):
        response = await ac.post(
            "/edge/create",
            json={
                "workflow_id": get_or_create_workflow_id,
                "start_node_id": get_or_create_start_node_id,
                "end_node_id": get_or_create_message_node_id,
                "edge_type": "default"
            }
        )

        assert response.status_code == 201
        assert response.json()["edge_type"] == "default"
        assert response.json()["start_node_id"] == get_or_create_start_node_id
        assert response.json()["end_node_id"] == get_or_create_message_node_id
        assert response.json()["workflow_id"] == get_or_create_workflow_id

        start_node = await StartNodeRepository(session).get(model_object_id=get_or_create_start_node_id)
        assert start_node is not None
        assert start_node.has_out_edge is True

        TestEdge.edge = response.json()

    async def test_cycle_edge_error(
            self,
            ac: AsyncClient,
            get_or_create_workflow_id: int,
            get_or_create_message_node_id: int
    ):
        response = await ac.post(
            "/edge/create",
            json={
                "workflow_id": get_or_create_workflow_id,
                "start_node_id": get_or_create_message_node_id,
                "end_node_id": get_or_create_message_node_id,
                "edge_type": EdgeType.DEFAULT.value
            }
        )

        assert response.status_code == 400

    async def test_condition_default_edge_type_error(
            self,
            ac: AsyncClient,
            get_or_create_workflow_id: int,
            get_or_create_condition_node_id: int,
            get_or_create_message_node_id: int,
    ):
        response = await ac.post(
            "/edge/create",
            json={
                "workflow_id": get_or_create_workflow_id,
                "start_node_id": get_or_create_condition_node_id,
                "end_node_id": get_or_create_message_node_id,
                "edge_type": EdgeType.DEFAULT.value
            }
        )

        assert response.status_code == 400

    async def test_count_edge_change(
            self,
            ac: AsyncClient,
            get_or_create_workflow_id: int,
            get_or_create_start_node_id: int,
            get_or_create_message_node_id: int,
            get_or_create_end_node_id: int,
            get_or_create_condition_node_id: int,
            session: AsyncSession
    ):
        message_node = await MessageNodeRepository(session).get(model_object_id=get_or_create_message_node_id)
        assert message_node is not None
        assert message_node.has_out_edge is not True

        response = await ac.post(
            "/edge/create",
            json={
                "workflow_id": get_or_create_workflow_id,
                "start_node_id": get_or_create_message_node_id,
                "end_node_id": get_or_create_end_node_id,
                "edge_type": EdgeType.DEFAULT.value
            }
        )

        assert response.status_code == 201
        await session.refresh(message_node)
        assert message_node.has_out_edge is True
        TestEdge.message_node_edge = response.json()

        condition_node = await ConditionNodeRepository(session).get(model_object_id=get_or_create_condition_node_id)
        assert condition_node is not None
        assert condition_node.yes_edge_count is not True
        assert condition_node.no_edge_count is not True

        response = await ac.post(
            "/edge/create",
            json={
                "workflow_id": get_or_create_workflow_id,
                "start_node_id": get_or_create_condition_node_id,
                "end_node_id": get_or_create_message_node_id,
                "edge_type": EdgeType.NO.value
            }
        )

        assert response.status_code == 201
        await session.refresh(condition_node)
        assert condition_node.no_edge_count is True
        TestEdge.condition_no_node_edge = response.json()

        response = await ac.post(
            "/edge/create",
            json={
                "workflow_id": get_or_create_workflow_id,
                "start_node_id": get_or_create_condition_node_id,
                "end_node_id": get_or_create_end_node_id,
                "edge_type": EdgeType.YES.value
            }
        )

        assert response.status_code == 201
        await session.refresh(condition_node)
        assert condition_node.yes_edge_count is True
        TestEdge.condition_yes_node_edge = response.json()

    async def test_out_edge_limit(
            self,
            ac: AsyncClient,
            get_or_create_workflow_id: int,
            get_or_create_message_node_id: int,
            get_or_create_condition_node_id: int,
            get_or_create_end_node_id: int,
            get_or_create_start_node_id: int,
            session: AsyncSession
    ):
        response = await ac.post(
            "/edge/create",
            json={
                "workflow_id": get_or_create_workflow_id,
                "start_node_id": get_or_create_message_node_id,
                "end_node_id": get_or_create_end_node_id,
                "edge_type": EdgeType.DEFAULT.value
            }
        )

        assert response.status_code == 400

        response = await ac.post(
            "/edge/create",
            json={
                "workflow_id": get_or_create_workflow_id,
                "start_node_id": get_or_create_start_node_id,
                "end_node_id": get_or_create_end_node_id,
                "edge_type": EdgeType.DEFAULT.value
            }
        )

        assert response.status_code == 400

        response = await ac.post(
            "/edge/create",
            json={
                "workflow_id": get_or_create_workflow_id,
                "start_node_id": get_or_create_condition_node_id,
                "end_node_id": get_or_create_end_node_id,
                "edge_type": EdgeType.YES.value
            }
        )

        assert response.status_code == 400

        response = await ac.post(
            "/edge/create",
            json={
                "workflow_id": get_or_create_workflow_id,
                "start_node_id": get_or_create_condition_node_id,
                "end_node_id": get_or_create_end_node_id,
                "edge_type": EdgeType.NO.value
            }
        )

        assert response.status_code == 400

    async def test_get_edge(self, ac: AsyncClient, get_or_create_workflow_id: int):
        response = await ac.get(f"/edge/{TestEdge.edge['id']}")

        assert response.status_code == 200
        assert response.json()["id"] == TestEdge.edge["id"]
        assert response.json()["edge_type"] == TestEdge.edge["edge_type"]
        assert response.json()["start_node_id"] == TestEdge.edge["start_node_id"]
        assert response.json()["end_node_id"] == TestEdge.edge["end_node_id"]
        assert response.json()["workflow_id"] == TestEdge.edge["workflow_id"]

    async def test_list_edge(self, ac: AsyncClient):
        response = await ac.get("/edge/list")

        assert response.status_code == 200

    async def test_list_filters_edge(self, ac: AsyncClient, get_or_create_workflow_id: int):
        response = await ac.get("/edge/list?workflow_id=30")

        assert response.status_code == 200
        assert response.json() == []

        response = await ac.get(f"/edge/list?workflow_id={get_or_create_workflow_id}")

        assert response.status_code == 200
        assert response.json() != []

    async def test_update_edge(self, ac: AsyncClient, get_or_create_condition_node_id):
        response = await ac.patch(
            f"/edge/update/{TestEdge.edge['id']}",
            json={
                "end_node_id": get_or_create_condition_node_id,
            }
        )

        assert response.status_code == 200
        assert response.json()["end_node_id"] == get_or_create_condition_node_id

    async def test_delete_edge(
            self,
            ac: AsyncClient,
            get_or_create_workflow_id: int,
            get_or_create_message_node_id: int,
            get_or_create_condition_node_id: int,
            get_or_create_end_node_id: int,
            get_or_create_start_node_id: int,
            session: AsyncSession
    ):
        start_node = await StartNodeRepository(session).get(model_object_id=get_or_create_start_node_id)
        message_node = await MessageNodeRepository(session).get(model_object_id=get_or_create_message_node_id)
        condition_node = await ConditionNodeRepository(session).get(model_object_id=get_or_create_condition_node_id)

        assert start_node.has_out_edge is True
        assert message_node.has_out_edge is True
        assert condition_node.yes_edge_count is True
        assert condition_node.no_edge_count is True

        response = await ac.delete(f"/edge/delete/{TestEdge.edge['id']}")

        assert response.status_code == 204
        await session.refresh(start_node)
        assert start_node.has_out_edge is False

        response = await ac.delete(f"/edge/delete/{TestEdge.message_node_edge['id']}")

        assert response.status_code == 204
        await session.refresh(message_node)
        assert message_node.has_out_edge is False

        response = await ac.delete(f"/edge/delete/{TestEdge.condition_no_node_edge['id']}")

        assert response.status_code == 204
        await session.refresh(condition_node)
        assert condition_node.no_edge_count is False

        response = await ac.delete(f"/edge/delete/{TestEdge.condition_yes_node_edge['id']}")

        assert response.status_code == 204
        await session.refresh(condition_node)
        assert condition_node.yes_edge_count is False

    async def test_delete_node_edge_cascade(
            self,
            ac: AsyncClient,
            session: AsyncSession,
            get_or_create_workflow_id: int,
            get_or_create_message_node_id: int,
            get_or_create_start_node_id: int
    ):
        edge = await EdgeRepository(session).add(
            {
                "workflow_id": get_or_create_workflow_id,
                "start_node_id": get_or_create_start_node_id,
                "end_node_id": get_or_create_message_node_id,
                "edge_type": EdgeType.DEFAULT
            }
        )

        assert edge is not None

        start_node = await StartNodeRepository(session).get(model_object_id=get_or_create_start_node_id)

        assert start_node is not None
        assert start_node.has_out_edge is True

        await MessageNodeRepository(session).delete(model_object_id=get_or_create_message_node_id)

        await session.refresh(start_node)

        assert start_node.has_out_edge is False
