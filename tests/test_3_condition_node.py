from httpx import AsyncClient


class TestConditionNode:
    condition_node_id = None

    async def test_create_condition_node(self, ac: AsyncClient, get_or_create_workflow_id: int):
        response = await ac.post(
            "/node/condition/create",
            json={
                "status_condition": "pending",
                "workflow_id": get_or_create_workflow_id
            }
        )

        assert response.status_code == 201
        assert response.json()["status_condition"] == "pending"
        assert response.json()["workflow_id"] == get_or_create_workflow_id

        TestConditionNode.condition_node_id = response.json()["id"]

    async def test_get_condition_node(self, ac: AsyncClient, get_or_create_workflow_id: int):
        response = await ac.get(f"/node/condition/{TestConditionNode.condition_node_id}")

        assert response.status_code == 200

    async def test_list_condition_node(self, ac: AsyncClient):
        response = await ac.get("/node/condition/list")

        assert response.status_code == 200

    async def test_list_filters_condition_node(self, ac: AsyncClient, get_or_create_workflow_id: int):
        response = await ac.get("/node/condition/list?workflow_id=30")

        assert response.status_code == 200
        assert response.json() == []

        response = await ac.get(f"/node/condition/list?workflow_id={get_or_create_workflow_id}")

        assert response.status_code == 200
        assert response.json() != []

        response = await ac.get("/node/condition/list?status_condition=sent")

        assert response.status_code == 200
        assert response.json() == []

        response = await ac.get("/node/condition/list?status_condition=pending")

        assert response.status_code == 200
        assert response.json() != []

        response = await ac.get("/node/condition/list?yes_edge_count=false")

        assert response.status_code == 200
        assert response.json() != []

        response = await ac.get("/node/condition/list?no_edge_count=false")

        assert response.status_code == 200
        assert response.json() != []
    
    async def test_update_condition_node(self, ac: AsyncClient):
        response = await ac.patch(
            f"/node/condition/update/{TestConditionNode.condition_node_id}",
            json={
                "status_condition": "sent",
            }
        )

        assert response.status_code == 200
        assert response.json()["status_condition"] == "sent"

    async def test_delete_condition_node(self, ac: AsyncClient):
        response = await ac.delete(f"/node/condition/delete/{TestConditionNode.condition_node_id}")

        assert response.status_code == 204
