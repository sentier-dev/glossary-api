"""Database classes for the dds_glossary package."""

from os import getenv
from typing import Optional

from sqlalchemy import ForeignKey, create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Session,
    mapped_column,
    relationship,
    selectinload,
)
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


def init_engine(
    database_url: Optional[str] = None,
    drop_database_flag: bool = False,
) -> Engine:
    """
    Initialize the database engine. If the database does not exist, create it.
    If the drop_database_flag is set, drop the database if it exists. Create the
    tables if they do not exist.

    Args:
        database_url (Optional[str]): The database URL. If None, use the
            DATABASE_URL environment variable.
        drop_database_flag (bool): Flag to drop the database if it exists.

    Returns:
        Engine: The database engine.

    Raises:
        ValueError: If the DATABASE_URL environment variable is not set.
    """
    if database_url is None:
        database_url = getenv("DATABASE_URL")

    if not database_url:
        raise ValueError("DATABASE_URL environment variable not set.")

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


def get_concept_schemes(engine: Engine) -> list[ConceptScheme]:
    """
    Get the concept schemes from the database.

    Args:
        engine (Engine): The database engine.

    Returns:
        list[ConceptScheme]: The concept schemes.
    """
    with Session(engine) as session:
        return session.query(ConceptScheme).all()


def get_concepts_for_scheme(engine: Engine, scheme_name: str) -> list[Concept]:
    """
    Get the concepts for a scheme from the database.

    Args:
        engine (Engine): The database engine.
        scheme_name (str): The name of the scheme.

    Returns:
        list[Concept]: The concepts for the scheme.

    Raises:
        NoResultFound: If the scheme does not exist in the database.
    """
    with Session(engine) as session:
        return session.query(ConceptScheme).filter_by(name=scheme_name).one().concepts


def get_relationships_for_concept(
    engine: Engine, concept_name: str
) -> list[Relationship]:
    """
    Get the relationships for a concept from the database.

    Args:
        engine (Engine): The database engine.
        concept_name (str): The name of the concept.

    Returns:
        list[Relationship]: The relationships for the concept.

    Raises:
        NoResultFound: If the concept does not exist in the database.
    """
    with Session(engine) as session:
        concept = session.query(Concept).filter_by(name=concept_name).one()
        return (
            session.query(Relationship)
            .options(selectinload(Relationship.source_concept))
            .options(selectinload(Relationship.destination_concept))
            .where(
                (Relationship.source_concept_id == concept.id)
                | (Relationship.destination_concept_id == concept.id)
            )
            .all()
        )
