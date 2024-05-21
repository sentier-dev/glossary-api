# pylint: disable=invalid-name
"""update_alt_labels_to_list

Revision ID: 5233d5762475
Revises: 658cfadcf600
Create Date: 2024-05-20 16:28:24.278434

"""

from typing import Callable, Sequence, Union

from sqlalchemy import CursorResult, MetaData, Table, select, update

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "5233d5762475"
down_revision: Union[str, None] = "658cfadcf600"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def update_rows(update_func: Callable) -> None:
    """Update the altLabels column in the concepts table."""
    column_name = "altLabels"
    pk_name = "iri"
    connection = op.get_bind()  # pylint: disable=no-member
    metadata = MetaData()
    metadata.reflect(bind=connection)
    table = Table("concepts", metadata, autoload_with=connection)

    results: CursorResult = connection.execute(
        select(table.c[pk_name], table.c[column_name])
    )
    for row in results:
        row_dict = dict(row)
        if row_dict[column_name] != {}:
            new_alt_labels = update_func(row_dict[column_name])
            connection.execute(
                update(table)
                .where(table.c[pk_name] == row_dict[pk_name])
                .values({column_name: new_alt_labels})
            )


def upgrade() -> None:
    """upgrade the altLabels column to dict[str, list[str]]."""

    def _to_list(x: dict[str, str]) -> dict[str, list[str]]:
        return {key: [value] for key, value in x.items()}

    update_rows(_to_list)


def downgrade() -> None:
    """downgrade the altLabels column to dict[str, str]."""

    def _from_list(x: dict[str, list[str]]) -> dict[str, str]:
        return {key: value[0] for key, value in x.items()}

    update_rows(_from_list)
