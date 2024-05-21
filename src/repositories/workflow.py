import io
from typing import List

from fastapi import HTTPException, status
from matplotlib import pyplot as plt
from sqlalchemy import Insert, insert, Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

import networkx as nx

from src.models import WorkFlow, EdgeType
from src.repositories.repository_base import BaseRepository


class WorkFlowRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(model=WorkFlow, session=session)

    def construct_add_stmt(self, values) -> Insert:
        stmt = insert(self._model).returning(self._model)
        return stmt

    def construct_get_stmt(self, id: int) -> Select:
        stmt = select(self._model).where(self._model.id == id).options(selectinload(self._model.start_nodes)).options(
            selectinload(self._model.message_nodes)).options(selectinload(self._model.condition_nodes)).options(
            selectinload(self._model.end_nodes)).options(selectinload(self._model.edges))
        return stmt

    @staticmethod
    def add_nodes_to_graph(workflow: WorkFlow, graph: nx.DiGraph):
        nodes = workflow.start_nodes + workflow.message_nodes + workflow.condition_nodes + workflow.end_nodes
        for node in nodes:
            node_data = {col.name: getattr(node, col.name) for col in node.__table__.columns}
            graph.add_node(node.id, type=node.discriminator, **node_data)

    @staticmethod
    def add_edges_to_graph(workflow: WorkFlow, graph: nx.DiGraph):
        edges = workflow.edges
        for edge in edges:
            graph.add_edge(edge.start_node_id, edge.end_node_id, edge_type=edge.edge_type, edge_id=edge.id)

    @staticmethod
    def define_node_color(graph: nx.DiGraph, path):
        node_colors = []
        for node in graph.nodes():
            if node in path:
                node_colors.append('red')  # Color nodes in the path green
            else:
                node_colors.append('lightblue')

    @staticmethod
    def define_edge_color(graph: nx.DiGraph, path):
        edge_colors = []
        for edge in graph.edges():
            if edge[0] in path and edge[1] in path and path.index(edge[1]) == path.index(edge[0]) + 1:
                edge_colors.append('red')  # Color edges in the path green
            else:
                edge_colors.append('gray')

    @staticmethod
    def save_graph_image(graph: nx.DiGraph, path: List):
        abbreviation = {
            "startnode": "st",
            "messagenode": "msg",
            "conditionnode": "cond",
            "endnode": "end",
        }

        pos = nx.spring_layout(graph)
        plt.figure()

        nx.draw(graph, pos, with_labels=True,
                labels={node: f"{node}: {abbreviation[data['type']]}" for node, data in graph.nodes(data=True)},
                edge_color=WorkFlowRepository.define_node_color(graph=graph, path=path))

        nx.draw_networkx_edges(graph, pos, edgelist=graph.edges(),
                               edge_color=WorkFlowRepository.define_node_color(graph=graph, path=path))
        nx.draw_networkx_edge_labels(
            graph,
            pos,
            edge_labels={
                (u, v): f"{d['edge_id']}" if d[
                                                 "edge_type"].value == "default" else f"{d['edge_id']}: {d['edge_type'].value}"
                for u, v, d in graph.edges(data=True)
            }
        )

        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plt.close()
        return buf

    @staticmethod
    def get_start_and_end_node(graph: nx.DiGraph):
        start_node = next((node_id for node_id, data in graph.nodes(data=True) if data['type'] == 'startnode'), None)
        end_node = next((node_id for node_id, data in graph.nodes(data=True) if data['type'] == 'endnode'), None)
        if not start_node:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"No start node in workflow")
        if not end_node:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"No end node in workflow")
        return start_node, end_node

    @staticmethod
    def process_condition_node(graph: nx.DiGraph, current_node, edge_type, stack, successor, current_path):
        predecessors = list(graph.predecessors(current_node))
        if not predecessors:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"Condition node (ID: {current_node}) has no predecessor")

        message_status = None
        for predecessor in predecessors:
            print(graph.nodes[predecessor]['type'])
            if graph.nodes[predecessor]['type'] == 'messagenode':
                print("ПРЕДЫДУЩАЯ MESSAGE")
                message_status = graph.nodes[predecessor]['status']
            elif graph.nodes[predecessor]['type'] == 'conditionnode':
                print("ПРЕДЫДУЩАЯ CONDITION")
                continue
            else:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail=f"Condition node (ID: {current_node}) should have Message node before it")

        if message_status == graph.nodes[current_node]['status_condition']:
            print("УМОВА ДОРІВНЮЄ")
            if edge_type == EdgeType.YES:
                print("УМОВА ДОРІВНЮЄ і ребро YES")
                stack.append((successor, current_path))
        else:
            print("УМОВА НЕ ДОРІВНЮЄ")
            if edge_type == EdgeType.NO:
                print("УМОВА ДОРІВНЮЄ і ребро NO")
                stack.append((successor, current_path))

    @staticmethod
    def build_condition_based_path(graph: nx.DiGraph):
        start_node, end_node = WorkFlowRepository.get_start_and_end_node(graph=graph)
        stack = [(start_node, [])]
        visited = set()

        while stack:
            current_node, current_path = stack.pop()
            if current_node in visited:
                continue

            print(f"___________________________Зараз нода: {current_node}___________________________")

            visited.add(current_node)
            current_path = current_path + [current_node]

            if current_node == end_node:
                return current_path

            for successor in graph.successors(current_node):
                edge_data = graph.get_edge_data(current_node, successor)
                edge_type = edge_data['edge_type']
                node_type = graph.nodes[current_node]['type']
                print(edge_type, node_type)
                print(f"Наступний: {successor}")
                print(graph.successors(current_node))

                if node_type == 'conditionnode':
                    WorkFlowRepository.process_condition_node(
                        graph=graph,
                        current_node=current_node,
                        current_path=current_path,
                        stack=stack,
                        edge_type=edge_type,
                        successor=successor
                    )
                else:
                    print("ДОбавка в STACK")
                    stack.append((successor, current_path))

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No path found between start and end nodes")

    async def start(self, workflow_id: int):
        graph = nx.DiGraph()

        result = await self._session.execute(self.construct_get_stmt(id=workflow_id))
        workflow = result.scalar_one_or_none()

        if not workflow:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")

        self.add_nodes_to_graph(workflow=workflow, graph=graph)
        self.add_edges_to_graph(workflow=workflow, graph=graph)

        try:
            path = self.build_condition_based_path(graph=graph)
        except HTTPException as e:
            return {"error": e.detail}

        return self.save_graph_image(graph=graph, path=path)
