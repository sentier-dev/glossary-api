"""Database classes for the dds_glossary package."""

from sqlalchemy import ForeignKey, create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship
from sqlalchemy_utils import create_database, database_exists, drop_database

from .model import RelationshipTuple


class Base(DeclarativeBase):  # pylint: disable=too-few-public-methods
    """Base class for database classes."""


class Concept(Base):  # pylint: disable=too-few-public-methods
    """Concept class.

    Attributes:
        id (int): The primary key.
        name (str): The name of the concept.
        scheme_id (int): The foreign key to the concept scheme.
        scheme (ConceptScheme): The relationship to the concept scheme.
    """

    __tablename__ = "concepts"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    scheme_id = mapped_column(ForeignKey("concept_schemes.id"))
    scheme: Mapped["ConceptScheme"] = relationship(back_populates="concepts")


class ConceptScheme(Base):  # pylint: disable=too-few-public-methods
    """Concept scheme class.

    Attributes:
        id (int): The primary key.
        name (str): The name of the concept scheme.
        concepts (list[Concept]): The relationship to the concepts.
    """

    __tablename__ = "concept_schemes"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    concepts: Mapped[list["Concept"]] = relationship(
        order_by=Concept.id,
        back_populates="scheme",
    )


class Relationship(Base):  # pylint: disable=too-few-public-methods
    """Relationship class.

    Attributes:
        id (int): The primary key.
        source_concept_id (int): The foreign key to the source concept.
        destination_concept_id (int): The foreign key to the destination
            concept.
        relationship_type (str): The type of relationship.
        source_concept (Concept): The relationship to the source concept.
        destination_concept (Concept): The relationship to the destination
            concept.
    """

    __tablename__ = "relationships"
    id: Mapped[int] = mapped_column(primary_key=True)
    source_concept_id: Mapped[int] = mapped_column(ForeignKey("concepts.id"))
    destination_concept_id: Mapped[int] = mapped_column(ForeignKey("concepts.id"))
    relationship_type: Mapped[str]
    source_concept: Mapped["Concept"] = relationship(foreign_keys=[source_concept_id])
    destination_concept: Mapped["Concept"] = relationship(
        foreign_keys=[destination_concept_id]
    )


def init_engine(database_url: str, drop_database_flag: bool = True) -> Engine:
    """
    Initialize the database engine for the given `database_url`. If the
    database does not exist, it will be created. If it does exist, it will be
    dropped and recreated if the `drop_database_flag` argument is set to
    `True`. The database schema will also be created.

    Args:
        database_url (str): The database URL.
        drop_database_flag (bool): Whether to drop the database before
            creating it.

    Returns:
        Engine: The database engine.
    """
    if database_exists(database_url) and drop_database_flag:
        drop_database(database_url)
    if not database_exists(database_url):
        create_database(database_url)
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    return engine


def save_concept_scheme_file(
    engine: Engine,
    concept_scheme_name: str,
    concepts_names: list[str],
    relationship_tuples: list[RelationshipTuple],
) -> None:
    """
    Save a concept scheme, concepts, and relationships to the database.

    Args:
        engine (Engine): The database engine.
        concept_scheme_name (str): The name of the concept scheme.
        concepts_names (list[str]): The names of the concepts.
        relationship_tuples (list[RelationshipTuple]): The relationship tuples.

    Returns:
        None
    """
    with Session(engine) as session:
        concept_scheme = ConceptScheme(name=concept_scheme_name)
        session.add(concept_scheme)

        concept_map: dict[str, int] = {}
        for concept_name in concepts_names:
            concept = Concept(name=concept_name, scheme_id=concept_scheme.id)
            session.add(concept)
            session.flush()
            concept_map[concept_name] = concept.id

        for relationship_tuple in relationship_tuples:
            relation = Relationship(
                source_concept_id=concept_map[relationship_tuple.source_concept],
                destination_concept_id=concept_map[
                    relationship_tuple.destination_concept
                ],
                relationship_type=relationship_tuple.relationship_type,
            )
            session.add(relation)
        session.commit()
