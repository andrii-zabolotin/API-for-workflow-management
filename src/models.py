from datetime import datetime
import enum

from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, declared_attr, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    __abstract__ = True

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return f"{cls.__name__.lower()}"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)

    repr_cols_num = 3
    repr_cols = tuple()

    def __repr__(self):
        cols = []
        for idx, col in enumerate(self.__table__.columns.keys()):
            if col in self.repr_cols or idx < self.repr_cols_num:
                cols.append(f"{col}={getattr(self, col)}")

        return f"<{self.__class__.__name__} {', '.join(cols)}>"


class WorkFlow(Base):
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)

    start_nodes: Mapped[list["StartNode"]] = relationship(back_populates="start_node_workflow", cascade="all, delete-orphan")
    message_nodes: Mapped[list["MessageNode"]] = relationship(back_populates="message_node_workflow", cascade="all, delete-orphan")
    condition_nodes: Mapped[list["ConditionNode"]] = relationship(back_populates="condition_node_workflow", cascade="all, delete-orphan")
    end_nodes: Mapped[list["EndNode"]] = relationship(back_populates="end_node_workflow", cascade="all, delete-orphan")
    edges: Mapped[list["Edge"]] = relationship(back_populates="edge_workflow", cascade="all, delete-orphan")

    repr_cols_num = 2
    repr_cols = tuple()


class EdgeType(enum.Enum):
    DEFAULT = "default"
    YES = "yes"
    NO = "no"


class Edge(Base):
    start_node_id: Mapped[int] = mapped_column(ForeignKey("nodeinterface.id", ondelete="CASCADE"))
    end_node_id: Mapped[int] = mapped_column(ForeignKey("nodeinterface.id", ondelete="CASCADE"))
    workflow_id: Mapped[int] = mapped_column(ForeignKey("workflow.id", ondelete="CASCADE"))
    edge_type: Mapped[EdgeType]

    start_node = relationship('NodeInterface', foreign_keys=[start_node_id])
    end_node = relationship('NodeInterface', foreign_keys=[end_node_id])
    edge_workflow: Mapped[WorkFlow] = relationship(back_populates="edges")

    repr_cols_num = 3
    repr_cols = tuple()


class NodeInterface(Base):
    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    discriminator: Mapped[str] = mapped_column()

    repr_cols_num = 3
    repr_cols = tuple()

    in_edges: Mapped[list["Edge"]] = relationship('Edge', foreign_keys=[Edge.start_node_id], back_populates="start_node", cascade="all, delete-orphan")
    out_edges: Mapped[list["Edge"]] = relationship('Edge', foreign_keys=[Edge.end_node_id], back_populates="end_node", cascade="all, delete-orphan")

    __mapper_args__ = {"polymorphic_on": discriminator}


class Status(enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    OPENED = "opened"


class StartNode(NodeInterface):
    id: Mapped[int] = mapped_column(ForeignKey("nodeinterface.id"), primary_key=True, index=True)
    has_out_edge: Mapped[bool] = mapped_column(default=False)
    workflow_id: Mapped[int] = mapped_column(ForeignKey("workflow.id", ondelete="CASCADE"))

    repr_cols_num = 3
    repr_cols = tuple()

    start_node_workflow = relationship('WorkFlow', back_populates='start_nodes')

    __mapper_args__ = {"polymorphic_identity": "startnode", "inherit_condition": (id == NodeInterface.id)}


class MessageNode(NodeInterface):
    id: Mapped[int] = mapped_column(ForeignKey("nodeinterface.id"), primary_key=True, index=True)
    status: Mapped[Status]
    message: Mapped[str]
    has_out_edge: Mapped[bool] = mapped_column(default=False)
    workflow_id: Mapped[int] = mapped_column(ForeignKey("workflow.id", ondelete="CASCADE"))

    repr_cols_num = 3
    repr_cols = tuple()

    message_node_workflow = relationship('WorkFlow', back_populates='message_nodes')

    __mapper_args__ = {"polymorphic_identity": "messagenode", "inherit_condition": (id == NodeInterface.id)}


class ConditionNode(NodeInterface):
    id: Mapped[int] = mapped_column(ForeignKey("nodeinterface.id"), primary_key=True, index=True)
    status_condition: Mapped[Status]
    yes_edge_count: Mapped[bool] = mapped_column(default=False)
    no_edge_count: Mapped[bool] = mapped_column(default=False)
    workflow_id: Mapped[int] = mapped_column(ForeignKey("workflow.id", ondelete="CASCADE"))

    repr_cols_num = 3
    repr_cols = tuple()

    condition_node_workflow = relationship('WorkFlow', back_populates='condition_nodes')

    __mapper_args__ = {"polymorphic_identity": "conditionnode", "inherit_condition": (id == NodeInterface.id)}


class EndNode(NodeInterface):
    id: Mapped[int] = mapped_column(ForeignKey("nodeinterface.id"), primary_key=True, index=True)
    workflow_id: Mapped[int] = mapped_column(ForeignKey("workflow.id", ondelete="CASCADE"))

    repr_cols_num = 3
    repr_cols = tuple()

    end_node_workflow = relationship('WorkFlow', back_populates='end_nodes')

    __mapper_args__ = {"polymorphic_identity": "endnode", "inherit_condition": (id == NodeInterface.id)}
