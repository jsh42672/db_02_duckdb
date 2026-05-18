-- 1. Card search with filters.
SELECT
    c.id,
    c.name,
    c.card_type,
    c.attribute,
    c.race,
    c.level,
    c.atk,
    c.def
FROM card c
LEFT JOIN card_archetype ca ON ca.card_id = c.id
WHERE c.name ILIKE '%dragon%'
  AND (c.attribute = 'LIGHT' OR c.attribute IS NULL)
ORDER BY c.name
LIMIT 50;

-- 2. Card detail screen query: more than three tables joined with LEFT JOIN.
SELECT
    c.id,
    c.name,
    ct.name AS card_type,
    r.name AS race,
    a.name AS attribute,
    c.level,
    c.atk,
    c.def,
    c.description,
    p.cardmarket,
    p.tcgplayer,
    img.image_url,
    tcg.status AS tcg_status,
    ocg.status AS ocg_status
FROM card c
LEFT JOIN card_type ct ON ct.name = c.card_type
LEFT JOIN race r ON r.name = c.race
LEFT JOIN attribute a ON a.name = c.attribute
LEFT JOIN card_price p ON p.card_id = c.id
LEFT JOIN (
    SELECT card_id, MIN(image_url) AS image_url
    FROM card_image
    GROUP BY card_id
) img ON img.card_id = c.id
LEFT JOIN ban_status tcg ON tcg.card_id = c.id AND tcg.format = 'TCG'
LEFT JOIN ban_status ocg ON ocg.card_id = c.id AND ocg.format = 'OCG'
WHERE c.id = 89631139;

-- 3. Deck detail query: deck, relationship table, card, type, ban status.
SELECT
    d.name AS deck_name,
    dc.section,
    dc.quantity,
    c.name AS card_name,
    c.card_type,
    c.is_extra_deck,
    b.status AS ban_status
FROM deck d
JOIN deck_card dc ON dc.deck_id = d.id
JOIN card c ON c.id = dc.card_id
LEFT JOIN card_type ct ON ct.name = c.card_type
LEFT JOIN ban_status b ON b.card_id = c.id AND b.format = d.ban_format
WHERE d.id = 1
ORDER BY dc.section, c.name;

-- 4. Ban list lookup by format and status.
SELECT
    c.name,
    c.card_type,
    b.format,
    b.status
FROM ban_status b
JOIN card c ON c.id = b.card_id
WHERE b.format = 'TCG'
  AND b.status IN ('Forbidden', 'Limited', 'Semi-Limited')
ORDER BY b.status, c.name;
