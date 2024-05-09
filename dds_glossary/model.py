"""Model classes for the dds_glossary package."""

from enum import Enum
from typing import ClassVar

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class SemanticRelationType(Enum):
    """Enum class for the types of semantic relations.

    Attributes:
        BROADER (str): The broader semantic relation.
        NARROWER (str): The narrower semantic relation.
        RELATED (str): The related semantic relation.
        BROADER_TRANSITIVE (str): The transitive broader semantic relation
        NARROWER_TRANSITIVE (str): The transitive narrower semantic relation.
    """

    BROADER: str = "broader"
    NARROWER: str = "narrower"
    RELATED: str = "related"
    BROADER_TRANSITIVE: str = "broaderTransitive"
    NARROWER_TRANSITIVE: str = "narrowerTransitive"


class Base(DeclarativeBase):  # pylint: disable=too-few-public-methods
    """Base class for all models."""

    type_annotation_map: ClassVar[dict] = {dict[str, str]: JSONB}
    xml_namespace: ClassVar[str] = "{http://www.w3.org/XML/1998/namespace}"

    @staticmethod
    def get_sub_element_text(element, tag: str, default_value: str = "") -> str:
        """
        Get a sub element text from the XML element if tag exists, else return
        default_value.

        Args:
            element (ElementBase): The XML element to parse.
            tag (str): The tag to search for.
            default_value (str): The default value to return if the tag does not exist.

        Returns:
            str: The sub element text if the tag exists, else the default value.
        """
        sub_element = element.find(tag, namespaces=element.nsmap)
        return sub_element.text if sub_element is not None else default_value


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
            use the `get_pref_label` method.
        concepts (List[Concept]): The concepts of the concept scheme.
    """

    __tablename__ = "concept_schemes"

    iri: Mapped[str] = mapped_column(primary_key=True)
    notation: Mapped[str] = mapped_column()
    scopeNote: Mapped[str] = mapped_column()
    prefLabels: Mapped[dict[str, str]] = mapped_column()

    concepts: Mapped[list["Concept"]] = relationship(back_populates="scheme")

    @classmethod
    def from_xml_element(cls, element) -> "ConceptScheme":
        """
        Return a ConceptScheme instance from an XML element.

        Args:
            element (ElementBase): The XML element to parse.

        Returns:
            ConceptScheme: The parsed ConceptScheme instance.
        """
        return ConceptScheme(
            iri=element.get(f"{{{element.nsmap['rdf']}}}about"),
            notation=cls.get_sub_element_text(element, "core:notation"),
            scopeNote=cls.get_sub_element_text(element, "core:scopeNote"),
            prefLabels={
                label.get(f"{cls.xml_namespace}lang"): label.text
                for label in element.findall("core:prefLabel", namespaces=element.nsmap)
            },
        )

    def get_pref_label(self, lang: str = "en") -> str:
        """
        Return the preferred label in the specified language. If the preferred label is
        not available in the specified language, return the preferred label in English.
        If the preferred label is not available in English, return an empty string.

        Args:
            lang (str): The language code of the preferred label. Defaults to English
                ("en").

        Returns:
            str: The preferred label in the specified language if available, otherwise
                in English.
        """
        return self.prefLabels.get(lang, self.prefLabels.get("en", ""))

    def to_dict(self, lang: str) -> dict:
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
            "prefLabel": self.get_pref_label(lang=lang),
        }


class Concept(Base):
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
        notation (str): The notation of the concept.
        prefLabels (dict[str, str]): The preferred labels of the concept. This is a
            dictionary where the key is the language code and the value is the label in
            that language. To get the preferred label in a specific language, use the
            `get_pref_label` method.
        altLabels (dict[str, str]): The alternative labels of the concept. This is a
            dictionary where the key is the language code and the value is the label in
            that language. To get the alternative label in a specific language, use the
            `get_alt_label` method.
        scopeNotes (dict[str, str]): The scope notes of the concept.
            This is a dictionary where the key is the language code and the value is the
            note in that language. To get the scope note in a specific language, use the
            `get_scope_note` method.
        scheme_iri (str): The Internationalized Resource Identifier of the concept
            scheme to which the concept belongs.
        scheme (ConceptScheme): The concept scheme to which the concept belongs.
    """

    __tablename__ = "concepts"

    iri: Mapped[str] = mapped_column(primary_key=True)
    identifier: Mapped[str] = mapped_column()
    notation: Mapped[str] = mapped_column()
    prefLabels: Mapped[dict[str, str]] = mapped_column()
    altLabels: Mapped[dict[str, str]] = mapped_column()
    scopeNotes: Mapped[dict[str, str]] = mapped_column()

    scheme_iri: Mapped[str] = mapped_column(ForeignKey("concept_schemes.iri"))
    scheme: Mapped[ConceptScheme] = relationship(back_populates="concepts")

    @classmethod
    def from_xml_element(cls, element) -> "Concept":
        """
        Return a Concept instance from an XML element.

        Args:
            element (ElementBase): The XML element to parse.

        Returns:
            Concept: The parsed Concept instance.
        """

        return Concept(
            iri=element.get(f"{{{element.nsmap['rdf']}}}about"),
            identifier=cls.get_sub_element_text(element, "x_1.1:identifier"),
            notation=cls.get_sub_element_text(element, "core:notation"),
            prefLabels={
                label.get(f"{cls.xml_namespace}lang"): label.text
                for label in element.findall("core:prefLabel", namespaces=element.nsmap)
            },
            altLabels={
                label.get(f"{cls.xml_namespace}lang"): label.text
                for label in element.findall("core:altLabel", namespaces=element.nsmap)
            },
            scopeNotes={
                note.get(f"{cls.xml_namespace}lang"): note.text
                for note in element.findall("core:scopeNote", namespaces=element.nsmap)
            },
            scheme_iri=element.find("core:inScheme", namespaces=element.nsmap).get(
                f"{{{element.nsmap['rdf']}}}resource"
            ),
        )

    def get_pref_label(self, lang: str = "en") -> str:
        """
        Return the preferred label in the specified language. If the preferred label is
        not available in the specified language, return the preferred label in English.
        If the preferred label is not available in English, return an empty string.

        Args:
            lang (str): The language code of the preferred label. Defaults to English
                ("en").

        Returns:
            str: The preferred label in the specified language if available, otherwise
                in English.
        """
        return self.prefLabels.get(lang, self.prefLabels.get("en", ""))

    def get_alt_label(self, lang: str = "en") -> str:
        """
        Return the alternative label in the specified language. If the alternative label
        is not available in the specified language, return the alternative label in
        English. If the alternative label is not available in English, return an empty
        string.

        Args:
            lang (str): The language code of the alternative label. Defaults to English
                ("en").

        Returns:
            str: The alternative label in the specified language if available, otherwise
                in English.
        """
        return self.altLabels.get(lang, self.altLabels.get("en", ""))

    def get_scope_note(self, lang: str = "en") -> str:
        """
        Return the scope note in the specified language. If the scope note is not
        available in the specified language, return the scope note in English. If the
        scope note is not available in English, return an empty string.

        Args:
            lang (str): The language code of the scope note. Defaults to English
                ("en").

        Returns:
            str: The scope note in the specified language if available, otherwise in
                English.
        """
        return self.scopeNotes.get(lang, self.scopeNotes.get("en", ""))

    def to_dict(self, lang: str) -> dict:
        """
        Return the Concept instance as a dictionary.

        Args:
            lang (str): The language code of the preferred label.

        Returns:
            dict: The Concept instance as a dictionary.
        """
        return {
            "iri": self.iri,
            "identifier": self.identifier,
            "notation": self.notation,
            "prefLabel": self.get_pref_label(lang=lang),
            "altLabel": self.get_alt_label(lang=lang),
            "scopeNote": self.get_scope_note(lang=lang),
            "scheme_iri": self.scheme_iri,
        }


class SemanticRelation(Base):  # pylint: disable=too-few-public-methods
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

    type: Mapped[SemanticRelationType] = mapped_column()

    source_concept_iri: Mapped[str] = mapped_column(
        ForeignKey("concepts.iri"), primary_key=True
    )
    target_concept_iri: Mapped[str] = mapped_column(
        ForeignKey("concepts.iri"), primary_key=True
    )
    source_concept: Mapped["Concept"] = relationship(foreign_keys=[source_concept_iri])
    target_concept: Mapped["Concept"] = relationship(foreign_keys=[target_concept_iri])

    @classmethod
    def from_xml_element(cls, element) -> list["SemanticRelation"]:
        """
        Return a list of SemanticRelation instances from an XML element.

        Args:
            element (ElementBase): The XML element to parse.

        Returns:
            list[SemanticRelation]: The parsed list of SemanticRelation instances.
        """
        return [
            SemanticRelation(
                type=relation_type,
                source_concept_iri=element.get(f"{{{element.nsmap['rdf']}}}about"),
                target_concept_iri=relation.get(f"{{{element.nsmap['rdf']}}}resource"),
            )
            for relation_type in SemanticRelationType
            for relation in element.findall(
                f"core:{relation_type.value}", namespaces=element.nsmap
            )
        ]
