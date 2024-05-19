"""Controller classes for the dds_glossary package."""

from http import HTTPStatus
from pathlib import Path
from typing import ClassVar

from appdirs import user_data_dir
from defusedxml.lxml import parse as parse_xml
from fastapi import HTTPException
from owlready2 import get_ontology, onto_path

from .database import (
    get_collection,
    get_concept,
    get_concept_scheme,
    get_concept_schemes,
    get_relations,
    init_engine,
    save_dataset,
    search_database,
)
from .model import Collection, Concept, ConceptScheme, SemanticRelation


class GlossaryController:
    """
    Controller for the glossary.

    Attributes:
        engine (Engine): The database engine.
        data_dir (Path): The data directory for saving the datasets.
    """

    europa_url: ClassVar[str] = "http://publications.europa.eu/resource/distribution/"
    fao_url: ClassVar[str] = (
        "https://storage.googleapis.com/fao-datalab-caliper/Downloads/"
    )
    datasets: ClassVar[dict[str, str]] = {
        "ESTAT-CN2024.rdf": (
            europa_url
            + "combined-nomenclature-2024/20240425-0/rdf/skos_core/ESTAT-CN2024.rdf"
        ),
        "ESTAT-LoW2015.rdf": (
            europa_url + "low2015/20240425-0/rdf/skos_core/ESTAT-LoW2015.rdf"
        ),
        "ESTAT-NACE2.1.rdf": (
            europa_url + "nace2.1/20240425-0/rdf/skos_core/ESTAT-NACE2.1.rdf"
        ),
        "ESTAT-ICST-COM.rdf": (
            europa_url + "icst-com/20240425-0/rdf/skos_core/ESTAT-ICST-COM.rdf"
        ),
        "ESTAT-PRODCOM2023.rdf": (
            europa_url + "prodcom2023/20240425-0/rdf/skos_core/ESTAT-PRODCOM2023.rdf"
        ),
        "ISIC4.rdf": fao_url + "ISICRev4/ISIC4.rdf",
    }

    def __init__(
        self,
        data_dir_path: str | Path = user_data_dir("dds_glossary", "dds_glossary"),
    ) -> None:
        self.engine = init_engine()
        self.data_dir = Path(data_dir_path)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        onto_path.append(str(self.data_dir))

    def parse_dataset(
        self,
        dataset_path: Path,
    ) -> tuple[
        list[ConceptScheme],
        list[Concept],
        list[Collection],
        list[SemanticRelation],
    ]:
        """
        Parse a dataset.

        Args:
            dataset_path (Path): The dataset path.

        Returns:
            tuple[list[ConceptScheme], list[Concept], list[Collection],
                list[SemanticRelation]]: The concept schemes, concepts, collections,
                and semantic relations.
        """
        root = parse_xml(dataset_path).getroot()
        concept_scheme_elements = root.findall("core:ConceptScheme", root.nsmap)
        collection_elements = root.findall("core:Collection", root.nsmap)
        concept_elements = root.findall("core:Concept", root.nsmap)
        concept_schemes = [
            ConceptScheme.from_xml_element(concept_scheme_element)
            for concept_scheme_element in concept_scheme_elements
        ]
        concepts = [
            Concept.from_xml_element(concept_element, concept_schemes)
            for concept_element in concept_elements
        ]
        collections = [
            Collection.from_xml_element(collection_element, concept_schemes)
            for collection_element in collection_elements
        ]
        semantic_relations: list[SemanticRelation] = []
        for concept_element in concept_elements:
            semantic_relations.extend(
                SemanticRelation.from_xml_element(concept_element)
            )
        return concept_schemes, concepts, collections, semantic_relations

    def init_datasets(
        self,
        reload: bool = False,
    ) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
        """
        Download and save the datasets, if they do not exist or if the reload flag is
        set.

        Args:
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
                ontology = get_ontology(dataset_url).load(reload=reload)
                ontology.save(file=str(dataset_path), format="rdfxml")
                save_dataset(self.engine, *self.parse_dataset(dataset_path))
                saved_datasets.append(
                    {
                        "dataset": dataset_file,
                        "dataset_url": dataset_url,
                    }
                )
            except Exception as error:  # pylint: disable=broad-except
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
            list[dict]: The concepts as dictionaries.

        Raises:
            HTTPException: If the concept scheme is not found.
        """
        concept_scheme = get_concept_scheme(self.engine, concept_scheme_iri)

        if concept_scheme:
            return [concept.to_dict(lang=lang) for concept in concept_scheme.members]
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f"Concept scheme {concept_scheme_iri} not found.",
        )

    def get_collection(self, collection_iri: str, lang: str = "en") -> dict:
        """
        Get the collection.

        Args:
            collection_iri (str): The collection IRI.
            lang (str): The language. Defaults to "en".

        Returns:
            dict: The collection.

        Raises:
            HTTPException: If the collection is not found.
        """
        collection = get_collection(self.engine, collection_iri)

        if collection:
            return {
                **collection.to_dict(lang=lang),
                "members": [member.to_dict(lang=lang) for member in collection.members],
            }
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f"Collection {collection_iri} not found.",
        )

    def get_concept(self, concept_iri: str, lang: str = "en") -> dict:
        """
        Get the concept and al its relations.

        Args:
            concept_iri (str): The concept IRI.
            lang (str): The language. Defaults to "en".

        Returns:
            dict: The concept.

        Raises:
            HTTPException: If the concept is not found.
        """
        concept = get_concept(self.engine, concept_iri)

        if concept:
            return {
                **concept.to_dict(lang=lang),
                "concept_schemes": [scheme.iri for scheme in concept.concept_schemes],
                "relations": [
                    relation.to_dict()
                    for relation in get_relations(self.engine, concept_iri)
                ],
            }
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f"Concept {concept_iri} not found.",
        )

    def search_database(self, search_term: str, lang: str = "en") -> list[dict]:
        """
        Search the database for concepts that match the `search_term` in the
        selected `lang`.

        Args:
            search_term (str): The search term to match against.
            lang (str): The language to use for matching. Defaults to "en".

        Returns:
            list[dict]: The result concepts as dictionaries.
        """
        return [
            concept.to_dict(lang=lang)
            for concept in search_database(self.engine, search_term, lang=lang)
        ]
