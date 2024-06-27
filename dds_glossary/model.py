"""Model classes for the dds_glossary package."""

from abc import abstractmethod
from dataclasses import dataclass, field
from typing import ClassVar

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, Relationship, mapped_column
from sqlmodel import ForeignKey, SQLModel

from .enums import MemberType, SemanticRelationType


class Dataset(SQLModel):
    """
    Base class for the datasets.

    Attributes:
        name (str): The name of the dataset.
        url (str): The URL of the dataset.
    """

    name: str
    url: str


class FailedDataset(Dataset):
    """
    Class for the failed datasets.

    Attributes:
        error (str): The error message for the failed dataset.
    """

    error: str


@dataclass
class ParsedDataset:
    """
    Class for the parsed datasets.

    Attributes:
        concept_schemes (list[ConceptScheme]): The concept schemes of the dataset.
        concepts (list[Concept]): The concepts of the dataset.
        collections (list[Collection]): The collections of the dataset.
        semantic_relations (list[SemanticRelation]): The semantic relations of the
            dataset.
        in_schemes (list[InScheme]): The in schemes of the dataset.
        in_collections (list[InCollection]): The in collections of the dataset.
    """

    concept_schemes: list["ConceptScheme"] = field(default_factory=list)
    concepts: list["Concept"] = field(default_factory=list)
    collections: list["Collection"] = field(default_factory=list)
    semantic_relations: list["SemanticRelation"] = field(default_factory=list)
    in_schemes: list["InScheme"] = field(default_factory=list)
    in_collections: list["InCollection"] = field(default_factory=list)


class Base(DeclarativeBase):
    """Base class for all models."""

    type_annotation_map: ClassVar[dict] = {
        dict[str, str]: JSONB,
        dict[str, list[str]]: JSONB,
    }

    def __eq__(self, other: object) -> bool:
        return self.to_dict() == other.to_dict()  # type: ignore

    @staticmethod
    def get_in_language(attribute: dict, lang: str = "en") -> str:
        """
        Get the value of the attribute in the specified language. If the attribute is
        not available in the specified language, return the attribute in English. If the
        attribute is not available in English, return an empty string.

        Args:
            attribute (dict): The attribute to search for.
            lang (str): The language code of the attribute. Defaults to English ("en").

        Returns:
            str: The attribute in the specified language if available, otherwise in
                English.
        """
        return attribute.get(lang, attribute.get("en", ""))

    @staticmethod
    def get_in_language_list(attribute: dict, lang: str = "en") -> list[str]:
        """
        Get the value of the attribute in the specified language. If the attribute is
        not available in the specified language, return the attribute in English. If the
        attribute is not available in English, return an empty list.

        Args:
            attribute (dict): The attribute to search for.
            lang (str): The language code of the attribute. Defaults to English ("en").

        Returns:
            list[str]: The attribute in the specified language if available,
                otherwise in English.
        """
        return attribute.get(lang, attribute.get("en", []))

    @abstractmethod
    def to_dict(self) -> dict:
        """
        Return the model instance as a dictionary.

        Returns:
            dict: The model instance as a dictionary.
        """


class ConceptScheme(Base):
    """
    A SKOS concept scheme can be viewed as an aggregation of one or more SKOS concepts.
    Semantic relationships (links) between those concepts may also be viewed as part of
    a concept scheme. This definition is, however, meant to be suggestive rather than
    restrictive, and there is some flexibility in the formal data model.

    The notion of a concept scheme is useful when dealing with data from an unknown
    source, and when dealing with data that describes two or more different knowledge
    organization systems.

    For more information, check: https://www.w3.org/TR/skos-reference/#schemes.

    Attributes:
        iri (str): The Internationalized Resource Identifier of the concept scheme.
        notation (str): The notation of the concept scheme.
        scopeNote (str): The scope note of the concept scheme.
        prefLabels (dict[str, str]): The preferred labels of the concept scheme. This
            is a dictionary where the key is the language code and the value is the
            label in that language. To get the preferred label in a specific language,
            use the `get_in_language` method.
        members (list[Member]): The members of the concept scheme.
    """

    __tablename__ = "concept_schemes"

    iri: Mapped[str] = mapped_column(primary_key=True)
    notation: Mapped[str]
    scopeNote: Mapped[str]
    prefLabels: Mapped[dict[str, str]]

    members: Mapped[list["Member"]] = Relationship(
        secondary="in_scheme",
        back_populates="concept_schemes",
    )

    def to_dict(self, lang: str = "en") -> dict:
        """
        Return the ConceptScheme instance as a dictionary.

        Args:
            lang (str): The language code of the preferred label.

        Returns:
            dict: The ConceptScheme instance as a dictionary.
        """
        return {
            "iri": self.iri,
            "notation": self.notation,
            "scopeNote": self.scopeNote,
            "prefLabel": self.get_in_language(self.prefLabels, lang=lang),
        }


class Member(Base):
    """
    Base classe for the collection members.

    Attributes:
        iri (str): The Internationalized Resource Identifier of the collection member.
        notation (str): The notation of the collection member.
        prefLabels (dict[str, str]): The preferred labels of the collection member. This
            is a dictionary where the key is the language code and the value is the
            label in that language. To get the preferred label in a specific language,
            use the `get_in_language` method.
        member_type (MemberType): The type of the collection member.
        concept_schemes (list[ConceptScheme]): The concept schemes to which the member
            belongs.
        collections (list[Collection]): The collections to which the member belongs.
    """

    __tablename__ = "collection_members"

    iri: Mapped[str] = mapped_column(primary_key=True)
    notation: Mapped[str]
    prefLabels: Mapped[dict[str, str]]
    member_type: Mapped[MemberType]

    __mapper_args__ = {
        "polymorphic_identity": MemberType.COLLECTION_MEMBER,
        "polymorphic_on": "member_type",
    }

    concept_schemes: Mapped[list[ConceptScheme]] = Relationship(
        secondary="in_scheme",
        back_populates="members",
    )
    collections: Mapped[list["Collection"]] = Relationship(
        secondary="in_collection",
        back_populates="members",
    )

    def to_dict(self, lang: str = "en") -> dict:
        """
        Return the Member instance as a dictionary.

        Args:
            lang (str): The language code of the prefLabel.

        Returns:
            dict: The Member instance as a dictionary.
        """
        return {
            "iri": self.iri,
            "notation": self.notation,
            "prefLabel": self.get_in_language(self.prefLabels, lang),
        }


class Collection(Member):
    """
    SKOS concept collections are labeled and/or ordered groups of SKOS concepts.

    Collections are useful where a group of concepts shares something in common, and it
    is convenient to group them under a common label, or where some concepts can be
    placed in a meaningful order.

    For more information, check: https://www.w3.org/TR/skos-reference/#collections.

    Attributes:
        iri (str): The Internationalized Resource Identifier of the collection.
    """

    __tablename__ = "collections"

    iri: Mapped[str] = mapped_column(ForeignKey(Member.iri), primary_key=True)

    members: Mapped[list[Member]] = Relationship(
        secondary="in_collection",
        back_populates="collections",
    )

    __mapper_args__ = {
        "polymorphic_identity": MemberType.COLLECTION,
    }


class Concept(Member):
    """
    A SKOS concept can be viewed as an idea or notion; a unit of thought. However, what
    constitutes a unit of thought is subjective, and this definition is meant to be
    suggestive, rather than restrictive.

    The notion of a SKOS concept is useful when describing the conceptual or
    intellectual structure of a knowledge organization system, and when referring to
    specific ideas or meanings established within a KOS.

    Note that, because SKOS is designed to be a vehicle for representing semi-formal
    KOS, such as thesauri and classification schemes, a certain amount of flexibility
    has been built in to the formal definition of this class.

    For more information, check: https://www.w3.org/TR/skos-reference/#concepts.

    Attributes:
        iri (str): The Internationalized Resource Identifier of the concept.
        identifier (str): The identifier of the concept.
        altLabels (dict[str, list[str]]): The alternative labels of the concept. This is
            a dictionary where the key is the language code and the value is a list of
            labels in that language. To get the alternative labels in a specific
            language, use the `get_in_language_list` method.
        scopeNotes (dict[str, str]): The scope notes of the concept.
            This is a dictionary where the key is the language code and the value is the
            note in that language. To get the scope note in a specific language, use the
            `get_in_language` method.
    """

    __tablename__ = "concepts"

    iri: Mapped[str] = mapped_column(ForeignKey(Member.iri), primary_key=True)
    identifier: Mapped[str]
    altLabels: Mapped[dict[str, list[str]]]
    scopeNotes: Mapped[dict[str, str]]

    __mapper_args__ = {
        "polymorphic_identity": MemberType.CONCEPT,
    }

    def to_dict(self, lang: str = "en") -> dict:
        """
        Return the Concept instance as a dictionary.

        Args:
            lang (str): The language code of the prefLabel, altLabels
                and scopeNote.

        Returns:
            dict: The Concept instance as a dictionary.
        """
        return {
            "iri": self.iri,
            "identifier": self.identifier,
            "notation": self.notation,
            "prefLabel": self.get_in_language(self.prefLabels, lang=lang),
            "altLabels": self.get_in_language_list(self.altLabels, lang=lang),
            "scopeNote": self.get_in_language(self.scopeNotes, lang=lang),
        }


class SemanticRelation(Base):
    """
    SKOS semantic relations are links between SKOS concepts, where the link is
    inherent in the meaning of the linked concepts.

    The Simple Knowledge Organization System distinguishes between two basic categories
    of semantic relation: hierarchical and associative. A hierarchical link between two
    concepts indicates that one is in some way more general ("broader") than the other
    ("narrower"). An associative link between two concepts indicates that the two are
    inherently "related", but that one is not in any way more general than the other.

    The properties skos:broader and skos:narrower are used to assert a direct
    hierarchical link between two SKOS concepts. A triple <A> skos:broader <B> asserts
    that <B>, the object of the triple, is a broader concept than <A>, the subject of
    the triple. Similarly, a triple <C> skos:narrower <D> asserts that <D>, the object
    of the triple, is a narrower concept than <C>, the subject of the triple.

    By convention, skos:broader and skos:narrower are only used to assert a direct
    (i.e., immediate) hierarchical link between two SKOS concepts. This provides
    applications with a convenient and reliable way to access the direct broader and
    narrower links for any given concept. Note that, to support this usage convention,
    the properties skos:broader and skos:narrower are not declared as transitive
    properties.

    Some applications need to make use of both direct and indirect hierarchical links
    between concepts, for instance to improve search recall through query expansion.
    For this purpose, the properties skos:broaderTransitive and skos:narrowerTransitive
    are provided. A triple <A> skos:broaderTransitive <B> represents a direct or
    indirect hierarchical link, where <B> is a broader "ancestor" of <A>. Similarly a
    triple <C> skos:narrowerTransitive <D> represents a direct or indirect hierarchical
    link, where <D> is a narrower "descendant" of <C>.

    By convention, the properties skos:broaderTransitive and skos:narrowerTransitive
    are not used to make assertions. Rather, these properties are used to infer the
    transitive closure of the hierarchical links, which can then be used to access
    direct or indirect hierarchical links between concepts.

    The property skos:related is used to assert an associative link between two SKOS
    concepts.

    For more information, check:
    https://www.w3.org/TR/skos-reference/#semantic-relations.

    Attributes:
        type (SemanticRelationType): The type of the semantic relation.
        source_concept_iri (str): The Internationalized Resource Identifier of the
            source concept.
        target_concept_iri (str): The Internationalized Resource Identifier of the
            target concept.
        source_concept (Concept): The source concept of the semantic relation.
        target_concept (Concept): The target concept of the semantic relation.
    """

    __tablename__ = "semantic_relations"

    type: Mapped[SemanticRelationType]

    source_concept_iri: Mapped[str] = mapped_column(
        ForeignKey(Concept.iri),
        primary_key=True,
    )
    target_concept_iri: Mapped[str] = mapped_column(
        ForeignKey(Concept.iri),
        primary_key=True,
    )
    source_concept: Mapped[Concept] = Relationship(foreign_keys=[source_concept_iri])
    target_concept: Mapped[Concept] = Relationship(foreign_keys=[target_concept_iri])

    def to_dict(self) -> dict:
        """
        Return the SemanticRelation instance as a dictionary.

        Returns:
            dict: The SemanticRelation instance as a dictionary.
        """
        return {
            "type": self.type.value,
            "source_concept_iri": self.source_concept_iri,
            "target_concept_iri": self.target_concept_iri,
        }


class InScheme(Base):
    """
    Association table for the concept schemes and the members.

    Attributes:
        scheme_iri (str): The Internationalized Resource Identifier of the concept
            scheme.
        member_iri (str): The Internationalized Resource Identifier of the member.
    """

    __tablename__ = "in_scheme"

    scheme_iri: Mapped[str] = mapped_column(
        ForeignKey(ConceptScheme.iri),
        primary_key=True,
    )
    member_iri: Mapped[str] = mapped_column(
        ForeignKey(Member.iri),
        primary_key=True,
    )

    def to_dict(self) -> dict:
        """
        Return the InScheme instance as a dictionary.

        Returns:
            dict: The InScheme instance as a dictionary.
        """
        return {
            "scheme_iri": self.scheme_iri,
            "member_iri": self.member_iri,
        }


class InCollection(Base):
    """
    Association table for the collections and the members.

    Attributes:
        collection_iri (str): The Internationalized Resource Identifier of the
            collection.
        member_iri (str): The Internationalized Resource Identifier of the member.
    """

    __tablename__ = "in_collection"

    collection_iri: Mapped[str] = mapped_column(
        ForeignKey(Collection.iri),
        primary_key=True,
    )
    member_iri: Mapped[str] = mapped_column(
        ForeignKey(Member.iri),
        primary_key=True,
    )

    def to_dict(self) -> dict:
        """
        Return the InCollection instance as a dictionary.

        Returns:
            dict: The InCollection instance as a dictionary.
        """
        return {
            "collection_iri": self.collection_iri,
            "member_iri": self.member_iri,
        }
