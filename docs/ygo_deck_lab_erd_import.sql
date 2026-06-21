CREATE TABLE card_type (
    name VARCHAR PRIMARY KEY
);

CREATE TABLE attribute (
    name VARCHAR PRIMARY KEY
);

CREATE TABLE race (
    name VARCHAR PRIMARY KEY
);

CREATE TABLE archetype (
    name VARCHAR PRIMARY KEY
);

CREATE TABLE card_set (
    name VARCHAR PRIMARY KEY
);

CREATE TABLE rarity (
    name VARCHAR PRIMARY KEY,
    code VARCHAR
);

CREATE TABLE ban_format (
    name VARCHAR PRIMARY KEY
);

CREATE TABLE ban_status_type (
    name VARCHAR PRIMARY KEY
);

CREATE TABLE deck_section (
    name VARCHAR PRIMARY KEY
);

CREATE TABLE price_source (
    name VARCHAR PRIMARY KEY
);

CREATE TABLE card (
    id BIGINT PRIMARY KEY,
    name VARCHAR NOT NULL UNIQUE,
    card_type VARCHAR NOT NULL,
    frame_type VARCHAR,
    attribute VARCHAR,
    race VARCHAR,
    level TINYINT,
    atk SMALLINT,
    def SMALLINT,
    description TEXT,
    is_extra_deck BOOLEAN NOT NULL DEFAULT FALSE,
    CONSTRAINT fk_card_card_type FOREIGN KEY (card_type) REFERENCES card_type(name),
    CONSTRAINT fk_card_attribute FOREIGN KEY (attribute) REFERENCES attribute(name),
    CONSTRAINT fk_card_race FOREIGN KEY (race) REFERENCES race(name)
);

CREATE TABLE card_archetype (
    card_id BIGINT NOT NULL,
    archetype_name VARCHAR NOT NULL,
    PRIMARY KEY (card_id, archetype_name),
    CONSTRAINT fk_card_archetype_card FOREIGN KEY (card_id) REFERENCES card(id),
    CONSTRAINT fk_card_archetype_archetype FOREIGN KEY (archetype_name) REFERENCES archetype(name)
);

CREATE TABLE card_set_entry (
    id BIGINT PRIMARY KEY,
    card_id BIGINT NOT NULL,
    set_name VARCHAR NOT NULL,
    set_code VARCHAR,
    rarity VARCHAR,
    set_price DECIMAL(10, 2),
    CONSTRAINT fk_card_set_entry_card FOREIGN KEY (card_id) REFERENCES card(id),
    CONSTRAINT fk_card_set_entry_set FOREIGN KEY (set_name) REFERENCES card_set(name),
    CONSTRAINT fk_card_set_entry_rarity FOREIGN KEY (rarity) REFERENCES rarity(name),
    CONSTRAINT uq_card_set_entry_print UNIQUE (card_id, set_code, rarity)
);

CREATE TABLE ban_status (
    card_id BIGINT NOT NULL,
    format VARCHAR NOT NULL,
    status VARCHAR NOT NULL,
    PRIMARY KEY (card_id, format),
    CONSTRAINT fk_ban_status_card FOREIGN KEY (card_id) REFERENCES card(id),
    CONSTRAINT fk_ban_status_format FOREIGN KEY (format) REFERENCES ban_format(name),
    CONSTRAINT fk_ban_status_type FOREIGN KEY (status) REFERENCES ban_status_type(name)
);

CREATE TABLE card_price (
    card_id BIGINT NOT NULL,
    source_name VARCHAR NOT NULL,
    price DECIMAL(10, 2),
    PRIMARY KEY (card_id, source_name),
    CONSTRAINT fk_card_price_card FOREIGN KEY (card_id) REFERENCES card(id),
    CONSTRAINT fk_card_price_source FOREIGN KEY (source_name) REFERENCES price_source(name)
);

CREATE TABLE card_image (
    image_id BIGINT PRIMARY KEY,
    card_id BIGINT NOT NULL,
    image_url TEXT,
    image_small TEXT,
    image_cropped TEXT,
    CONSTRAINT fk_card_image_card FOREIGN KEY (card_id) REFERENCES card(id)
);

CREATE TABLE deck (
    id BIGINT PRIMARY KEY,
    name VARCHAR NOT NULL,
    memo TEXT,
    ban_format VARCHAR NOT NULL DEFAULT 'TCG',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_deck_ban_format FOREIGN KEY (ban_format) REFERENCES ban_format(name)
);

CREATE TABLE deck_card (
    deck_id BIGINT NOT NULL,
    card_id BIGINT NOT NULL,
    section VARCHAR NOT NULL,
    quantity TINYINT NOT NULL,
    PRIMARY KEY (deck_id, card_id, section),
    CONSTRAINT fk_deck_card_deck FOREIGN KEY (deck_id) REFERENCES deck(id),
    CONSTRAINT fk_deck_card_card FOREIGN KEY (card_id) REFERENCES card(id),
    CONSTRAINT fk_deck_card_section FOREIGN KEY (section) REFERENCES deck_section(name)
);
