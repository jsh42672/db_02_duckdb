from domain.common.enums import BanFormat, DeckSection

BAN_FORMATS = tuple(item.value for item in BanFormat)
SECTIONS = tuple(item.value for item in DeckSection)
SECTION_LABELS = {
    DeckSection.MAIN.value: "Main",
    DeckSection.EXTRA.value: "Extra",
    DeckSection.SIDE.value: "Side",
}
