"""Controller classes for the dds_glossary package."""

from pathlib import Path
from typing import ClassVar

from appdirs import user_data_dir
from defusedxml.lxml import parse as parse_xml
from requests import RequestException
from requests import get as get_request

from .database import get_concept_schemes, get_concepts, init_engine, save_dataset
from .model import Concept, ConceptScheme, SemanticRelation


class GlossaryController:
    """
    Controller for the glossary.

    Attributes:
        engine (Engine): The database engine.
        data_dir (Path): The data directory for saving the datasets.
    """

    base_url: ClassVar[str] = "http://publications.europa.eu/resource/distribution/"
    datasets: ClassVar[dict[str, str]] = {
        "ESTAT-CN2024.rdf": (
            "combined-nomenclature-2024/20240425-0/rdf/skos_core/ESTAT-CN2024.rdf"
        ),
        "ESTAT-LoW2015.rdf": "low2015/20240425-0/rdf/skos_core/ESTAT-LoW2015.rdf",
    }

    def __init__(
        self,
        data_dir_path: str | Path = user_data_dir("dds_glossary", "dds_glossary"),
    ) -> None:
        self.engine = init_engine()
        self.data_dir = Path(data_dir_path)

    def parse_dataset(
        self,
        dataset_path: Path,
    ) -> tuple[list[ConceptScheme], list[Concept], list[SemanticRelation]]:
        """
        Parse a dataset.

        Args:
            dataset_path (Path): The dataset path.

        Returns:
            tuple[list[ConceptScheme], list[Concept], list[SemanticRelation]]: The
                concept schemes, concepts, and semantic relations.
        """
        root = parse_xml(dataset_path).getroot()
        concept_scheme_elements = root.findall("core:ConceptScheme", root.nsmap)
        concept_elements = root.findall("core:Concept", root.nsmap)
        concept_schemes = [
            ConceptScheme.from_xml_element(concept_scheme_element)
            for concept_scheme_element in concept_scheme_elements
        ]
        concepts = [
            Concept.from_xml_element(concept_element)
            for concept_element in concept_elements
        ]
        semantic_relations: list[SemanticRelation] = []
        for concept_element in concept_elements:
            semantic_relations.extend(
                SemanticRelation.from_xml_element(concept_element)
            )
        return concept_schemes, concepts, semantic_relations

    def init_datasets(
        self,
        timeout: int = 10,
        reload: bool = False,
    ) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
        """
        Download and save the datasets, if they do not exist or if the reload flag is
        set.

        Args:
            timeout (int): The request timeout. Defaults to 10.
            reload (bool): Flag to reload the datasets. Defaults to False.

        Returns:
            tuple[list[dict[str, str]], list[dict[str, str]]]: The saved datasets and
                the failed datasets.
        """
        saved_datasets: list[dict[str, str]] = []
        failed_datasets: list[dict[str, str]] = []
        self.engine = init_engine(drop_database_flag=True)
        for dataset_file, dataset_url in self.datasets.items():
            dataset_path = self.data_dir / dataset_file
            try:
                if not dataset_path.exists() or reload:
                    response = get_request(dataset_url, timeout=timeout)
                    response.raise_for_status()
                    with open(dataset_path, "wb") as file:
                        file.write(response.content)
                save_dataset(self.engine, *self.parse_dataset(dataset_path))
                saved_datasets.append(
                    {
                        "dataset": dataset_file,
                        "dataset_url": dataset_url,
                    }
                )
            except RequestException as error:
                failed_datasets.append(
                    {
                        "dataset": dataset_file,
                        "dataset_url": dataset_url,
                        "error": str(error),
                    }
                )
        return saved_datasets, failed_datasets

    def get_concept_schemes(self, lang: str = "en") -> list[dict]:
        """
        Get the concept schemes.

        Args:
            lang (str): The language. Defaults to "en".

        Returns:
            list[dict]: The concept schemes.
        """
        return [
            concept_scheme.to_dict(lang=lang)
            for concept_scheme in get_concept_schemes(self.engine)
        ]

    def get_concepts(self, concept_scheme_iri: str, lang: str = "en") -> list[dict]:
        """
        Get the concepts.

        Args:
            concept_scheme_iri (str): The concept scheme IRI.
            lang (str): The language. Defaults to "en".

        Returns:
            list[dict]: The concepts.
        """
        return [
            concept.to_dict(lang=lang)
            for concept in get_concepts(self.engine, concept_scheme_iri)
        ]
