CREATE TABLE IF NOT EXISTS card_type (
    name VARCHAR PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS attribute (
    name VARCHAR PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS race (
    name VARCHAR PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS archetype (
    name VARCHAR PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS card_set (
    name VARCHAR PRIMARY KEY,
    release_year SMALLINT
);

CREATE TABLE IF NOT EXISTS rarity (
    name VARCHAR PRIMARY KEY,
    code VARCHAR
);

CREATE TABLE IF NOT EXISTS ban_format (
    name VARCHAR PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS ban_status_type (
    name VARCHAR PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS deck_section (
    name VARCHAR PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS price_source (
    name VARCHAR PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS role_tag (
    name VARCHAR PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS card (
    id BIGINT PRIMARY KEY,
    name VARCHAR NOT NULL UNIQUE,
    card_type VARCHAR NOT NULL REFERENCES card_type(name),
    frame_type VARCHAR,
    attribute VARCHAR REFERENCES attribute(name),
    race VARCHAR REFERENCES race(name),
    level TINYINT,
    atk SMALLINT,
    def SMALLINT,
    description TEXT,
    is_extra_deck BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS card_archetype (
    card_id BIGINT NOT NULL REFERENCES card(id),
    archetype_name VARCHAR NOT NULL REFERENCES archetype(name),
    PRIMARY KEY (card_id, archetype_name)
);

CREATE TABLE IF NOT EXISTS card_set_entry (
    id BIGINT PRIMARY KEY,
    card_id BIGINT NOT NULL REFERENCES card(id),
    set_name VARCHAR NOT NULL REFERENCES card_set(name),
    set_code VARCHAR,
    rarity VARCHAR REFERENCES rarity(name),
    set_price DECIMAL(10, 2),
    UNIQUE (card_id, set_code, rarity)
);

CREATE TABLE IF NOT EXISTS ban_status (
    card_id BIGINT NOT NULL REFERENCES card(id),
    format VARCHAR NOT NULL REFERENCES ban_format(name),
    status VARCHAR NOT NULL REFERENCES ban_status_type(name),
    PRIMARY KEY (card_id, format)
);

CREATE TABLE IF NOT EXISTS card_price (
    card_id BIGINT NOT NULL REFERENCES card(id),
    source_name VARCHAR NOT NULL REFERENCES price_source(name),
    price DECIMAL(10, 2),
    PRIMARY KEY (card_id, source_name)
);

CREATE TABLE IF NOT EXISTS card_image (
    image_id BIGINT PRIMARY KEY,
    card_id BIGINT NOT NULL REFERENCES card(id),
    image_url TEXT,
    image_small TEXT,
    image_cropped TEXT
);

CREATE TABLE IF NOT EXISTS deck (
    id BIGINT PRIMARY KEY,
    name VARCHAR NOT NULL,
    memo TEXT,
    ban_format VARCHAR NOT NULL DEFAULT 'TCG' REFERENCES ban_format(name),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS deck_card (
    deck_id BIGINT NOT NULL REFERENCES deck(id),
    card_id BIGINT NOT NULL REFERENCES card(id),
    section VARCHAR NOT NULL REFERENCES deck_section(name),
    quantity TINYINT NOT NULL,
    PRIMARY KEY (deck_id, card_id, section),
    CHECK (quantity BETWEEN 1 AND 3)
);

CREATE TABLE IF NOT EXISTS deck_card_role (
    deck_id BIGINT NOT NULL,
    card_id BIGINT NOT NULL,
    section VARCHAR NOT NULL,
    role_name VARCHAR NOT NULL REFERENCES role_tag(name),
    PRIMARY KEY (deck_id, card_id, section, role_name),
    FOREIGN KEY (deck_id) REFERENCES deck(id),
    FOREIGN KEY (card_id) REFERENCES card(id),
    FOREIGN KEY (section) REFERENCES deck_section(name)
);

CREATE TABLE IF NOT EXISTS seed_meta (
    key VARCHAR PRIMARY KEY,
    value VARCHAR NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_card_name ON card(name);
CREATE INDEX IF NOT EXISTS idx_card_type ON card(card_type);
CREATE INDEX IF NOT EXISTS idx_card_race ON card(race);
CREATE INDEX IF NOT EXISTS idx_card_attribute ON card(attribute);
CREATE INDEX IF NOT EXISTS idx_card_level ON card(level);
CREATE INDEX IF NOT EXISTS idx_card_archetype_name ON card_archetype(archetype_name);
CREATE INDEX IF NOT EXISTS idx_deck_card_card ON deck_card(card_id);
CREATE INDEX IF NOT EXISTS idx_card_set_release_year ON card_set(release_year);
CREATE INDEX IF NOT EXISTS idx_deck_card_role_name ON deck_card_role(role_name);

INSERT OR IGNORE INTO deck_section (name) VALUES ('MAIN'), ('EXTRA'), ('SIDE');
INSERT OR IGNORE INTO price_source (name) VALUES
    ('cardmarket'),
    ('tcgplayer'),
    ('ebay'),
    ('amazon'),
    ('coolstuffinc');
INSERT OR IGNORE INTO ban_format (name) VALUES ('TCG'), ('OCG'), ('GOAT');
INSERT OR IGNORE INTO ban_status_type (name) VALUES
    ('Forbidden'),
    ('Limited'),
    ('Semi-Limited'),
    ('Unlimited');
INSERT OR IGNORE INTO role_tag (name) VALUES
    ('Starter'),
    ('Searcher'),
    ('Interaction'),
    ('Brick'),
    ('Extender');
