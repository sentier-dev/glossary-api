"""Database classes for the dds_glossary package."""

from os import getenv

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session
from sqlalchemy_utils import create_database, database_exists, drop_database

from .model import Base, Concept, ConceptScheme, SemanticRelation


def init_engine(
    database_url: str | None = None,
    drop_database_flag: bool = False,
) -> Engine:
    """
    Initialize the database engine. If the database does not exist, create it.
    If the drop_database_flag is set, drop the database if it exists. Create the
    tables if they do not exist.

    Args:
        database_url (str, optional): The database URL. If None, use the
            `DATABASE_URL` environment variable.
        drop_database_flag (bool): Flag to drop the database if it exists.

    Returns:
        Engine: The database engine.

    Raises:
        ValueError: If the DATABASE_URL environment variable is not set, in case the
            the `database_url` argument is None.
    """
    if database_url is None:
        database_url = getenv("DATABASE_URL")

    if not database_url:
        raise ValueError("DATABASE_URL environment variable is not set.")

    if database_exists(database_url) and drop_database_flag:
        drop_database(database_url)
    if not database_exists(database_url):
        create_database(database_url)

    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    return engine


def save_dataset(
    engine: Engine,
    concept_schemes: list[ConceptScheme],
    concepts: list[Concept],
    semantic_relations: list[SemanticRelation],
) -> None:
    """
    Save a dataset in the database.

    Args:
        engine (Engine): The database engine.
        concept_schemes (list[ConceptScheme]): The concept schemes.
        concepts (list[Concept]): The concepts.
        semantic_relations (list[SemanticRelation]): The semantic relations.
    """
    with Session(engine) as session:
        session.add_all(concept_schemes)
        session.add_all(concepts)
        session.add_all(semantic_relations)
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
