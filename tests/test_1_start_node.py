from httpx import AsyncClient


class TestStartNode:
    start_node_id = None

    async def test_create_start_node(self, ac: AsyncClient, get_or_create_workflow_id: int):
        response = await ac.post(
            "/node/start/create",
            json={
                "workflow_id": get_or_create_workflow_id
            }
        )
        print(response.json())
        assert response.status_code == 201
        TestStartNode.start_node_id = response.json()["id"]

    async def test_get_start_node(self, ac: AsyncClient, get_or_create_workflow_id: int):
        response = await ac.get(f"/node/start/{TestStartNode.start_node_id}")

        assert response.status_code == 200
        assert response.json()["workflow_id"] == get_or_create_workflow_id

    async def test_list_start_nodes(self, ac: AsyncClient):
        response = await ac.get("/node/start/list")

        assert response.status_code == 200

    async def test_list_filters_start_nodes(self, ac: AsyncClient, get_or_create_workflow_id: int):
        response = await ac.get(f"/node/start/list?workflow_id={get_or_create_workflow_id}")

        assert response.status_code == 200
        assert response.json() != []

        response = await ac.get(f"/node/start/list?workflow_id={get_or_create_workflow_id}&out_edge=true")
        assert response.status_code == 200
        assert response.json() == []

        response = await ac.get(f"/node/start/list?workflow_id=30")
        assert response.status_code == 200
        assert response.json() == []

    async def test_delete_start_node(self, ac: AsyncClient):
        response = await ac.delete(f"/node/start/delete/{TestStartNode.start_node_id}")

        assert response.status_code == 204
