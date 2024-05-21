# pylint: disable=invalid-name
"""Initial migration

Revision ID: 658cfadcf600
Revises:
Create Date: 2024-05-20 16:28:13.920963

"""

from typing import Sequence, Union

from sqlalchemy import Column, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "658cfadcf600"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# pylint: disable=no-member
def upgrade() -> None:
    """Initial migration."""
    # Create table for ConceptScheme
    op.create_table(
        "concept_schemes",
        Column("iri", String(), primary_key=True),
        Column("notation", String(), nullable=False),
        Column("scopeNote", String(), nullable=False),
        Column("prefLabels", JSONB(), nullable=False),
    )

    # Create table for Member
    op.create_table(
        "collection_members",
        Column("iri", String(), primary_key=True),
        Column("notation", String(), nullable=False),
        Column("prefLabels", JSONB(), nullable=False),
        Column(
            "member_type",
            Enum(
                "collection_member",
                "concept",
                "collection",
                name="membertype",
            ),
            nullable=False,
        ),
    )

    # Create table for Collection
    op.create_table(
        "collections",
        Column(
            "iri",
            String(),
            ForeignKey("collection_members.iri"),
            primary_key=True,
        ),
    )

    # Create table for Concept
    op.create_table(
        "concepts",
        Column(
            "iri",
            String(),
            ForeignKey("collection_members.iri"),
            primary_key=True,
        ),
        Column("identifier", String(), nullable=False),
        Column("altLabels", JSONB(), nullable=False),
        Column("scopeNotes", JSONB(), nullable=False),
    )

    # Create table for SemanticRelation
    op.create_table(
        "semantic_relations",
        Column(
            "type",
            Enum(
                "broader",
                "narrower",
                "related",
                "broaderTransitive",
                "narrowerTransitive",
                name="semanticrelationtype",
            ),
            nullable=False,
        ),
        Column(
            "source_concept_iri",
            String(),
            ForeignKey("concepts.iri"),
            primary_key=True,
        ),
        Column(
            "target_concept_iri",
            String(),
            ForeignKey("concepts.iri"),
            primary_key=True,
        ),
    )

    # Create many-to-many relationship tables
    op.create_table(
        "in_scheme",
        Column(
            "scheme_iri",
            String(),
            ForeignKey("concept_schemes.iri"),
            primary_key=True,
        ),
        Column(
            "member_iri",
            String(),
            ForeignKey("collection_members.iri"),
            primary_key=True,
        ),
    )

    op.create_table(
        "in_collection",
        Column(
            "collection_iri",
            String(),
            ForeignKey("collections.iri"),
            primary_key=True,
        ),
        Column(
            "member_iri",
            String(),
            ForeignKey("collection_members.iri"),
            primary_key=True,
        ),
    )


# pylint: disable=no-member
def downgrade():
    """Initial migration."""
    # Drop many-to-many relationship tables first
    op.drop_table("in_collection")
    op.drop_table("in_scheme")

    # Drop tables in reverse order of creation
    op.drop_table("semantic_relations")
    op.drop_table("concepts")
    op.drop_table("collections")
    op.drop_table("collection_members")
    op.drop_table("concept_schemes")

    # Drop enums
    op.execute("DROP TYPE semanticrelationtype")
    op.execute("DROP TYPE membertype")
