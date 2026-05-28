from __future__ import annotations

from domain.card.dto import CardSearchFilterDTO, CardSummaryDTO
from repository.duckdb.base import BaseDuckDbRepository
from provider.ygoprodeck.mapper import to_int


class DuckDbCardQueryRepository(BaseDuckDbRepository):
    def card_count(self) -> int:
        return self.con.execute("SELECT COUNT(*) FROM card").fetchone()[0]

    def search_cards(self, filters: CardSearchFilterDTO) -> list[CardSummaryDTO]:
        conditions: list[str] = []
        params: list[object] = []

        if filters.keyword.strip():
            term = f"%{filters.keyword.strip()}%"
            conditions.append("(c.name ILIKE ? OR c.description ILIKE ?)")
            params.extend([term, term])
        if filters.card_type:
            conditions.append("c.card_type = ?")
            params.append(filters.card_type)
        if filters.attribute:
            conditions.append("c.attribute = ?")
            params.append(filters.attribute)
        if filters.race:
            conditions.append("c.race = ?")
            params.append(filters.race)
        if filters.archetype:
            conditions.append(
                """
                EXISTS (
                    SELECT 1
                    FROM card_archetype ca2
                    WHERE ca2.card_id = c.id
                      AND ca2.archetype_name = ?
                )
                """
            )
            params.append(filters.archetype)

        numeric_filters = (
            ("c.level = ?", filters.level),
            ("c.atk >= ?", filters.atk_min),
            ("c.atk <= ?", filters.atk_max),
            ("c.def >= ?", filters.def_min),
            ("c.def <= ?", filters.def_max),
        )
        for expression, raw_value in numeric_filters:
            value = to_int(raw_value)
            if value is not None:
                conditions.append(expression)
                params.append(value)

        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
        params.append(filters.limit)
        rows = self.con.execute(
            f"""
            SELECT
                c.id,
                c.name,
                c.card_type,
                c.attribute,
                c.race,
                c.level,
                c.atk,
                c.def,
                c.is_extra_deck,
                img.image_small,
                string_agg(DISTINCT ca.archetype_name, ', ') AS archetypes
            FROM card c
            LEFT JOIN card_archetype ca ON ca.card_id = c.id
            LEFT JOIN (
                SELECT card_id, MIN(image_small) AS image_small
                FROM card_image
                GROUP BY card_id
            ) img ON img.card_id = c.id
            {where_clause}
            GROUP BY
                c.id, c.name, c.card_type, c.attribute, c.race, c.level,
                c.atk, c.def, c.is_extra_deck, img.image_small
            ORDER BY c.name
            LIMIT ?
            """,
            params,
        ).fetchall()

        return [
            CardSummaryDTO(
                id=row[0],
                name=row[1],
                card_type=row[2],
                attribute=row[3],
                race=row[4],
                level=row[5],
                atk=row[6],
                def_=row[7],
                is_extra_deck=row[8],
                image_small=row[9],
                archetypes=row[10],
            )
            for row in rows
        ]
