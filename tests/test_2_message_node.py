from httpx import AsyncClient


class TestMessageNode:
    message_node_id = None

    async def test_message_node_create(self, ac: AsyncClient, get_or_create_workflow_id: int):
        response = await ac.post(
            "/node/message/create",
            json={
                "status": "pending",
                "message": "Hello world",
                "workflow_id": get_or_create_workflow_id
            }
        )

        assert response.status_code == 201
        assert response.json()["message"] == "Hello world"
        assert response.json()["status"] == "pending"
        assert response.json()["workflow_id"] == get_or_create_workflow_id

        TestMessageNode.message_node_id = response.json()["id"]

    async def test_get_message_node(self, ac: AsyncClient, get_or_create_workflow_id: int):
        response = await ac.get(f"/node/message/{TestMessageNode.message_node_id}")

        assert response.status_code == 200
        assert response.json()["id"] == TestMessageNode.message_node_id

    async def test_list_message_node(self, ac: AsyncClient, get_or_create_workflow_id: int):
        response = await ac.get(f"/node/message/list")

        assert response.status_code == 200

    async def test_list_filters_message_node(self, ac: AsyncClient, get_or_create_workflow_id: int):
        response = await ac.get(f"/node/message/list?out_edge=true&workflow_id={get_or_create_workflow_id}")

        assert response.status_code == 200
        assert response.json() == []

        response = await ac.get(f"/node/message/list?workflow_id=30")

        assert response.status_code == 200
        assert response.json() == []

        response = await ac.get(f"/node/message/list?status=sent&workflow_id={get_or_create_workflow_id}")

        assert response.status_code == 200
        assert response.json() == []

        response = await ac.get(f"/node/message/list?status=pending&workflow_id={get_or_create_workflow_id}")

        assert response.status_code == 200
        assert response.json() != []

    async def test_update_message_node(self, ac: AsyncClient):
        response = await ac.patch(
            f"/node/message/update/{TestMessageNode.message_node_id}",
            json={
                "message": "Hello world UPDATED"
            }
        )

        assert response.status_code == 200
        assert response.json()["message"] == "Hello world UPDATED"

    async def test_delete_message_node(self, ac: AsyncClient):
        response = await ac.delete(f"/node/message/delete/{TestMessageNode.message_node_id}")

        assert response.status_code == 204
