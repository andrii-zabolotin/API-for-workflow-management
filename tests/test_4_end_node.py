from httpx import AsyncClient


class TestEndNode:
    end_node_id = None

    async def test_end_node_create(self, ac: AsyncClient, get_or_create_workflow_id: int):
        response = await ac.post(
            "/node/end/create",
            json={
                "workflow_id": get_or_create_workflow_id,
            }
        )

        assert response.status_code == 201
        TestEndNode.end_node_id = response.json()["id"]

    async def test_end_node_limit_error(self, ac: AsyncClient, get_or_create_workflow_id: int):
        response = await ac.post(
            "/node/end/create",
            json={
                "workflow_id": get_or_create_workflow_id,
            }
        )

        assert response.status_code == 400

    async def test_get_end_node(self, ac: AsyncClient, get_or_create_workflow_id: int):
        response = await ac.get(f"/node/end/{TestEndNode.end_node_id}")

        assert response.status_code == 200
        assert response.json()["workflow_id"] == get_or_create_workflow_id

    async def test_list_end_nodes(self, ac: AsyncClient):
        response = await ac.get("/node/end/list")

        assert response.status_code == 200

    async def test_delete_end_node(self, ac: AsyncClient):
        response = await ac.delete(f"/node/end/delete/{TestEndNode.end_node_id}")

        assert response.status_code == 204
