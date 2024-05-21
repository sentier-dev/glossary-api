"""Utils for dds_glossary integration tests."""

from enum import Enum
from http import HTTPStatus
from pathlib import Path
from typing import Mapping

from fastapi.testclient import TestClient
from pydantic import BaseModel

from dds_glossary.model import Concept, ConceptScheme, Dataset, FailedDataset
from dds_glossary.schema import (
    CollectionResponse,
    ConceptResponse,
    ConceptSchemeResponse,
    EntityResponse,
    FullConceptResponse,
    FullConceptSchemeResponse,
    InitDatasetsResponse,
    RelationResponse,
)
from dds_glossary.services import GlossaryController


class RequestType(Enum):
    """Request types for the API."""

    GET = "get"
    POST = "post"


class Endpoint(Enum):
    """Endpoints for the API."""

    VERSION = "version"
    INIT_DATASETS = "init_datasets"
    SCHEMES = "schemes"
    SCHEME = "scheme"
    COLLECIONS = "collections"
    COLLECION = "collection"
    CONCEPTS = "concepts"
    CONCEPT = "concept"


def not_found_response(
    entity_name: str,
    entity_iri: str,
) -> dict[str, str]:
    """
    Return a not found response.

    Args:
        entity_name (str): The name of the entity.
        entity_iri (str): The IRI of the entity.

    Returns:
        dict[str, str]: The not found response.
    """

    return {"detail": f"{entity_name} {entity_iri} not found."}


def assert_response(
    _client: TestClient,
    endpoint: str,
    https_status: HTTPStatus,
    response_model: BaseModel | list[BaseModel] | dict[str, str],
    request_type: RequestType = RequestType.GET,
    headers: Mapping[str, str] | None = None,
) -> None:
    """
    Assert the response from the API.

    Args:
        _client (TestClient): The test client.
        endpoint (str): The endpoint to test.
        https_status (HTTPStatus): The expected status code.
        response_model (BaseModel | list[BaseModel]): The expected
            response model.
        request_type (RequestType): The request type.
        headers (Mapping[str, str]): The headers to send with the request.
    """
    if headers is None:
        headers = {}

    if request_type == RequestType.POST:
        response = _client.post(f"/latest/{endpoint}", headers=headers)
    else:
        response = _client.get(f"/latest/{endpoint}", headers=headers)

    assert response.status_code == https_status, (
        f"Expected status code {https_status}, but got {response.status_code}."
        f"Response: {response.text} for endpoint {endpoint}."
    )

    assert response.headers["content-type"] == "application/json", (
        "Expected content type 'application/json', but got "
        f"{response.headers['content-type']}."
        f"Response: {response.text}."
    )

    if isinstance(response_model, list):
        expected_response = [model.model_dump() for model in response_model]
        assert response.json() == expected_response, (
            f"Expected response {expected_response}, but got "
            f"{response.json()} for endpoint {endpoint}."
        )
    elif isinstance(response_model, dict):
        assert response.json() == response_model, (
            f"Expected response {response_model}, but got "
            f"{response.json()} for endpoint {endpoint}."
        )
    else:
        assert response.json() == response_model.model_dump(), (
            f"Expected response {response_model.model_dump()}, but got "
            f"{response.json()} for endpoint {endpoint}."
        )


def setup_fresh_start(
    _dir_data: Path,
    _concept_scheme: ConceptScheme,
    _concept: Concept,
    lang: str = "sk",
) -> dict[Endpoint, BaseModel | list]:
    """
    Setup a fresh start for the integration tests.

    Args:
        _dir_data (Path): The path to the data directory.
        _concept_scheme (ConceptScheme): The first concept scheme
            in `sample.rdf`.
        _concept (Concept): The first concept in `sample.rdf`.
        lang (str): The language for labels.

    Returns:
        dict[Endpoint, BaseModel | list]: The expected responses.
    """
    saved_dataset = Dataset(
        name="sample.rdf",
        url=str(_dir_data / "sample.rdf"),
    )
    failed_dataset = FailedDataset(
        name="failed_dataset.rdf",
        url="",
        error="[Errno 2] No such file or directory: ''",
    )
    GlossaryController.datasets = [saved_dataset, failed_dataset]

    concept_scheme_response = ConceptSchemeResponse(
        **_concept_scheme.to_dict(lang=lang)
    )
    collection_responses = [
        EntityResponse(
            iri=f"https://example.org/collection{i}",
            notation=f"Collection{i}Notation",
            prefLabel=f"Collection{i}PrefLabel",
        )
        for i in range(1, 3)
    ]
    concept_responses = [
        ConceptResponse(**_concept.to_dict(lang=lang)),
        ConceptResponse(
            iri="http://data.europa.eu/xsp/cn2024/020321000010",
            identifier="020321000010",
            notation="",
            prefLabel="- Mrazené",
            altLabels=["- Frozen"],
            scopeNote="",
        ),
    ]

    responses: dict[Endpoint, BaseModel | list] = {
        Endpoint.INIT_DATASETS: InitDatasetsResponse(
            saved_datasets=[saved_dataset],
            failed_datasets=[failed_dataset],
        ),
        Endpoint.SCHEMES: [concept_scheme_response],
        Endpoint.SCHEME: FullConceptSchemeResponse(
            **concept_scheme_response.model_dump(),
            collections=collection_responses,
            concepts=concept_responses,
        ),
        Endpoint.COLLECIONS: collection_responses,
        Endpoint.COLLECION: CollectionResponse(
            **collection_responses[0].model_dump(),
            collections=[collection_responses[1]],
            concepts=[concept_responses[0]],
        ),
        Endpoint.CONCEPTS: concept_responses,
        Endpoint.CONCEPT: FullConceptResponse(
            **concept_responses[0].model_dump(),
            concept_schemes=[concept_scheme_response.iri],
            relations=[
                RelationResponse(
                    type="broader",
                    source_concept_iri=concept_responses[0].iri,
                    target_concept_iri=concept_responses[1].iri,
                )
            ],
        ),
    }

    return responses
