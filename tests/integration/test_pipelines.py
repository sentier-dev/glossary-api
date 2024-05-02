"""Test for running the downloading and saving pipelines."""

from typing import Optional

from pandas import read_csv
from sqlalchemy.orm import Session
from sqlalchemy.sql import ColumnExpressionArgument, exists

from dds_glossary.controllers import PipelinesController
from dds_glossary.database import Concept, ConceptScheme, Relationship
from dds_glossary.model import DownloadableFile, HSFile


def entry_exists(session: Session, clause: ColumnExpressionArgument) -> bool:
    """Return True if the entry exists in the database.

    Args:
        session (Session): The database session.
        clause (ClauseElement): The clause to check.
    """
    return session.query(exists().where(clause)).scalar()


def get_concept_by_name(session: Session, name: str) -> Optional[Concept]:
    """
    Retrieve a concept from the session by its name.

    Args:
        session (Session): The SQLAlchemy session object.
        name (str): The name of the concept to retrieve.

    Returns:
        Optional[Base]: The concept object if found, otherwise None.
    """
    return session.query(Concept).filter_by(name=name).one_or_none()


def test_run_pipelines(tmp_path, engine) -> None:
    """Test the run_pipelines function."""
    hs_file = HSFile("harmonized-system", "csv", output_dir=tmp_path)
    downloadable_files: list[DownloadableFile] = [hs_file]

    controller = PipelinesController(
        engine=engine,
        downloadable_files=downloadable_files,
    )
    controller.run_pipelines()

    assert hs_file.file_path.exists()

    engine = controller.engine
    number_of_samples = 10
    df = read_csv(hs_file.file_path)
    samples_df = df.sample(n=number_of_samples)

    with Session(engine) as session:
        assert entry_exists(session, ConceptScheme.name == hs_file.concept_scheme_name)
        for _, sample in samples_df.iterrows():
            source_concept = get_concept_by_name(session, sample.description)
            assert source_concept

            destination_concept = get_concept_by_name(
                session,
                df[df.hscode == sample.parent].iloc[0].description,
            )
            assert destination_concept

            assert entry_exists(
                session,
                (
                    Relationship.source_concept_id == source_concept.id
                    and Relationship.destination_concept == destination_concept.id
                ),
            )
