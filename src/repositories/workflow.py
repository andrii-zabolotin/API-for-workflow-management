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
    def _add_nodes_to_graph(workflow: WorkFlow, graph: nx.DiGraph):
        """
        Adds nodes from the workflow to the graph.

        Args:
            workflow: The workflow that contains the nodes.
            graph: The graph where nodes will be added.
        """
        nodes = workflow.start_nodes + workflow.message_nodes + workflow.condition_nodes + workflow.end_nodes
        for node in nodes:
            node_data = {col.name: getattr(node, col.name) for col in node.__table__.columns}
            graph.add_node(node.id, type=node.discriminator, **node_data)

    @staticmethod
    def _add_edges_to_graph(workflow: WorkFlow, graph: nx.DiGraph):
        """
        Adds edges from the workflow to the graph.

        Args:
            workflow: The workflow that contains the nodes.
            graph: The graph where nodes will be added.
        """
        edges = workflow.edges
        for edge in edges:
            graph.add_edge(edge.start_node_id, edge.end_node_id, edge_type=edge.edge_type, edge_id=edge.id)

    @staticmethod
    def _define_node_edge_color(graph: nx.DiGraph, path):
        """
        Defines node's edge color.

        Args:
            path: Path from start node to end node.
            graph: The graph where nodes will be added.
        """
        node_colors = []
        if path:
            for node in graph.nodes():
                if node in path:
                    node_colors.append('red')
                else:
                    node_colors.append('lightblue')
            return node_colors
        else:
            return ['lightblue'] * len(graph.nodes())

    @staticmethod
    def _define_edge_color(graph: nx.DiGraph, path):
        """
        Defines edge's color.

        Args:
            path: Path from start node to end node.
            graph: The graph where nodes will be added.
        """
        edge_colors = []
        if path:
            for u, v in graph.edges():
                if (u, v) in zip(path, path[1:]):
                    edge_colors.append('red')
                else:
                    edge_colors.append('gray')
            return edge_colors
        else:
            return ['gray'] * len(graph.edges())

    @staticmethod
    def _save_graph_image(graph: nx.DiGraph, path: List):
        """
        Illustration of the graph.

        Args:
            path: Path from start node to end node.
            graph: The graph where nodes will be added.
        """
        abbreviation = {
            "startnode": "st",
            "messagenode": "msg",
            "conditionnode": "cond",
            "endnode": "end",
        }

        pos = nx.spring_layout(graph)
        plt.figure()

        nx.draw(
            graph,
            pos,
            with_labels=True,
            labels={node: f"{node}: {abbreviation[data['type']]}" for node, data in graph.nodes(data=True)},
            edgecolors=WorkFlowRepository._define_node_edge_color(graph=graph, path=path)
        )

        nx.draw_networkx_edges(
            graph,
            pos,
            edgelist=graph.edges(),
            edge_color=WorkFlowRepository._define_edge_color(graph=graph, path=path)
        )

        nx.draw_networkx_edge_labels(
            graph,
            pos,
            edge_labels={
                (u, v): f"{d['edge_id']}" if d["edge_type"].value == "default" else f"{d['edge_id']}: {d['edge_type'].value}"
                for u, v, d in graph.edges(data=True)
            }
        )

        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plt.close()
        return buf

    @staticmethod
    def _get_start_and_end_node(graph: nx.DiGraph):
        """
        Finds the start and end nodes in the graph.

        Args:
            graph: The graph where nodes will be added.
        """
        start_node = next((node_id for node_id, data in graph.nodes(data=True) if data['type'] == 'startnode'), None)
        end_node = next((node_id for node_id, data in graph.nodes(data=True) if data['type'] == 'endnode'), None)
        if not start_node:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"No start node in workflow")
        if not end_node:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"No end node in workflow")
        return start_node, end_node

    @staticmethod
    def _process_condition_node(graph: nx.DiGraph, current_node, edge_type, stack, successor, current_path):
        """
        Processes a condition node and updates the stack with the next nodes to visit.
        Checks if message node exists before condition node.

        Args:
            graph: The graph containing the nodes and edges.
            current_node: The ID of the current node being processed.
            edge_type: The type of the edge leading to the successor node.
            stack: The stack of nodes to visit.
            successor: The ID of the successor node.
            current_path: The current path of node IDs.

        Raises:
            HTTPException: If the condition node has no predecessor or has an invalid predecessor.
        """
        predecessors = list(graph.predecessors(current_node))
        if not predecessors:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"Condition node (ID: {current_node}) has no predecessor")

        message_status = None
        for predecessor in predecessors:
            if graph.nodes[predecessor]['type'] == 'messagenode':
                message_status = graph.nodes[predecessor]['status']
            elif graph.nodes[predecessor]['type'] == 'conditionnode':
                continue
            else:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail=f"Condition node (ID: {current_node}) should have Message node before it")

        if message_status == graph.nodes[current_node]['status_condition']:
            if edge_type == EdgeType.YES:
                stack.append((successor, current_path))
        else:
            if edge_type == EdgeType.NO:
                stack.append((successor, current_path))

    @staticmethod
    def _build_condition_based_path(graph: nx.DiGraph):
        """
        Builds a path through the graph.

        Args:
            graph: The graph containing the nodes and edges.

        Returns:
            List: A list of node IDs representing the path from start to end node.

        Raises:
            HTTPException: If no path is found between the start and end nodes.
        """
        start_node, end_node = WorkFlowRepository._get_start_and_end_node(graph=graph)
        stack = [(start_node, [])]
        visited = set()

        while stack:
            current_node, current_path = stack.pop()
            if current_node in visited:
                continue

            visited.add(current_node)
            current_path = current_path + [current_node]

            if current_node == end_node:
                return current_path

            for successor in graph.successors(current_node):
                edge_data = graph.get_edge_data(current_node, successor)
                edge_type = edge_data['edge_type']
                node_type = graph.nodes[current_node]['type']

                if node_type == 'conditionnode':
                    WorkFlowRepository._process_condition_node(
                        graph=graph,
                        current_node=current_node,
                        current_path=current_path,
                        stack=stack,
                        edge_type=edge_type,
                        successor=successor
                    )
                else:
                    stack.append((successor, current_path))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No path found between start and end nodes")
    
    async def _build_graph_and_path(self, workflow_id: int):
        """
        Builds the graph and finds the path for the given workflow ID.

        Args:
            workflow_id: The ID of the workflow.

        Returns:
            nx.DiGraph, List[int]: The constructed graph and the path as a list of node IDs.

        Raises:
            HTTPException: If the workflow is not found.
        """
        graph = nx.DiGraph()

        result = await self._session.execute(self.construct_get_stmt(id=workflow_id))
        workflow = result.scalar_one_or_none()

        if not workflow:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")

        self._add_nodes_to_graph(workflow=workflow, graph=graph)
        self._add_edges_to_graph(workflow=workflow, graph=graph)

        path = self._build_condition_based_path(graph=graph)

        return graph, path

    async def get_path_image(self, workflow_id: int):
        graph, path = await self._build_graph_and_path(workflow_id=workflow_id)
        return self._save_graph_image(graph=graph, path=path)

    async def get_path(self, workflow_id: int):
        _,  path = await self._build_graph_and_path(workflow_id=workflow_id)
        return path
    