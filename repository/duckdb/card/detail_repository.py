from __future__ import annotations

from domain.card.dto import CardDetailDTO, CardPriceDTO, CardSetEntryDTO
from repository.duckdb.base import BaseDuckDbRepository


class DuckDbCardDetailRepository(BaseDuckDbRepository):
    def get_card_detail(self, card_id: int) -> CardDetailDTO | None:
        row = self.con.execute(
            """
            SELECT
                c.id,
                c.name,
                c.card_type,
                c.frame_type,
                c.attribute,
                c.race,
                c.level,
                c.atk,
                c.def,
                c.description,
                c.is_extra_deck,
                MAX(CASE WHEN p.source_name = 'cardmarket' THEN p.price END) AS cardmarket,
                MAX(CASE WHEN p.source_name = 'tcgplayer' THEN p.price END) AS tcgplayer,
                MAX(CASE WHEN p.source_name = 'ebay' THEN p.price END) AS ebay,
                MAX(CASE WHEN p.source_name = 'amazon' THEN p.price END) AS amazon,
                MAX(CASE WHEN p.source_name = 'coolstuffinc' THEN p.price END) AS coolstuffinc,
                img.image_url,
                img.image_small,
                img.image_cropped,
                string_agg(DISTINCT ca.archetype_name, ', ') AS archetypes
            FROM card c
            LEFT JOIN card_price p ON p.card_id = c.id
            LEFT JOIN (
                SELECT
                    card_id,
                    MIN(image_url) AS image_url,
                    MIN(image_small) AS image_small,
                    MIN(image_cropped) AS image_cropped
                FROM card_image
                GROUP BY card_id
            ) img ON img.card_id = c.id
            LEFT JOIN card_archetype ca ON ca.card_id = c.id
            WHERE c.id = ?
            GROUP BY
                c.id, c.name, c.card_type, c.frame_type, c.attribute, c.race,
                c.level, c.atk, c.def, c.description, c.is_extra_deck,
                img.image_url, img.image_small, img.image_cropped
            """,
            [card_id],
        ).fetchone()
        if row is None:
            return None

        sets = self.con.execute(
            """
            SELECT e.set_name, e.set_code, e.rarity, r.code AS rarity_code, e.set_price
            FROM card_set_entry e
            LEFT JOIN rarity r ON r.name = e.rarity
            WHERE e.card_id = ?
            ORDER BY e.set_name, e.set_code
            LIMIT 20
            """,
            [card_id],
        ).fetchall()
        bans = self.con.execute(
            """
            SELECT format, status
            FROM ban_status
            WHERE card_id = ?
            ORDER BY format
            """,
            [card_id],
        ).fetchall()

        return CardDetailDTO(
            id=row[0],
            name=row[1],
            card_type=row[2],
            frame_type=row[3],
            attribute=row[4],
            race=row[5],
            level=row[6],
            atk=row[7],
            def_=row[8],
            description=row[9],
            is_extra_deck=row[10],
            prices=CardPriceDTO(
                cardmarket=row[11],
                tcgplayer=row[12],
                ebay=row[13],
                amazon=row[14],
                coolstuffinc=row[15],
            ),
            image_url=row[16],
            image_small=row[17],
            image_cropped=row[18],
            archetypes=row[19],
            sets=[
                CardSetEntryDTO(
                    set_name=item[0],
                    set_code=item[1],
                    rarity=item[2],
                    rarity_code=item[3],
                    set_price=item[4],
                )
                for item in sets
            ],
            bans={item[0]: item[1] for item in bans},
        )
