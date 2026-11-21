"""Audited New Game inventory choices; no arbitrary save fields or story completion.

Native grant/field evidence: plans/rounds/r20-start.md. Concrete upgrade choices
mean the complete prefix of a progressive family, not additive fixed tiers.
"""

from collections import Counter
from collections.abc import Iterable

from clawshot.progressive import CHAINS, FAMILY_BY_ITEM, MAGIC_SOURCES

DUNGEONS = {
    "Deku Tree": "InsideTheDekuTree",
    "Dodongos Cavern": "DodongoCavern",
    "Jabu Jabus Belly": "InsideJabuJabuBelly",
    "Forest Temple": "ForestTemple",
    "Fire Temple": "FireTemple",
    "Water Temple": "WaterTemple",
    "Shadow Temple": "ShadowTemple",
    "Spirit Temple": "SpiritTemple",
    "Bottom of the Well": "BottomOfTheWell",
    "Ice Cavern": "IceCavern",
}
SONGS = (
    "Zeldas Lullaby",
    "Eponas Song",
    "Sarias Song",
    "Suns Song",
    "Song of Time",
    "Song of Storms",
    "Minuet of Forest",
    "Bolero of Fire",
    "Serenade of Water",
    "Requiem of Spirit",
    "Nocturne of Shadow",
    "Prelude of Light",
)
EQUIPMENT = (
    "Kokiri Sword",
    "Master Sword",
    "Biggoron Sword",
    "Deku Shield",
    "Hylian Shield",
    "Mirror Shield",
    "Boomerang",
    "Megaton Hammer",
    "Iron Boots",
    "Hover Boots",
    "Goron Tunic",
    "Zora Tunic",
    "Fairy Ocarina",
    "Ocarina of Time",
    "Dins Fire",
    "Farores Wind",
    "Nayrus Love",
    "Ice Arrows",
    "Light Arrows",
    "Double Defense",
    "Stone of Agony",
    "Scrub Business Seed",
    "Deku Nut Capacity",
    "Deku Stick Capacity",
)
MAP_FLAGS = {
    f"{kind} ({dungeon})": f"DungeonInfo.{target}.IsGet{kind}"
    for dungeon, target in DUNGEONS.items()
    for kind in ("Map", "Compass")
}
CHOICES = tuple(
    dict.fromkeys((*EQUIPMENT, *(tier.item for tiers in CHAINS.values() for tier in tiers), *SONGS, *MAP_FLAGS))
)
JUNK = "Rupees (20)"


def validate(items: Iterable[str], hearts: int, full_wallet: bool) -> None:
    if unsupported := sorted(set(items) - set(CHOICES)):
        raise ValueError(
            f"Unsupported starting items: {unsupported}. Choose audited equipment, upgrades, songs, maps or compasses; "
            "trade items, bottles, masks, Lens, keys, tokens and dungeon rewards are not supported starts."
        )
    if type(hearts) is not int or not 0 <= hearts <= 17:
        raise ValueError("starting_hearts must be an integer from 0 to 17 extra hearts")
    if type(full_wallet) is not bool:
        raise ValueError("starting_full_wallet must be a boolean")


def prefixes(items: Iterable[str]) -> tuple[str, ...]:
    """Canonical fixed inventory, each family expanded once through its highest chosen tier."""
    chosen = set(items)
    out = [item for item in CHOICES if item in chosen and item not in FAMILY_BY_ITEM]
    for tiers in CHAINS.values():
        count = max((index + 1 for index, tier in enumerate(tiers) if tier.item in chosen), default=0)
        out.extend(tier.item for tier in tiers[:count])
    return tuple(out)


def copies(items: Iterable[str]) -> Counter[str]:
    result = Counter(FAMILY_BY_ITEM[item] for item in prefixes(items) if item in FAMILY_BY_ITEM)
    # A spell/arrow's native MPMaxUP opens single magic even without the MP item.
    if set(items).intersection(MAGIC_SOURCES):
        result["Progressive Magic"] = max(1, result["Progressive Magic"])
    return result


def wallet(items: Iterable[str]) -> tuple[str, int]:
    chosen = set(items)
    if "Giant Wallet" in chosen:
        return "Item_Wallet_Large", 1000
    if "Adult Wallet" in chosen:
        return "Item_Wallet_Medium", 500
    return "Item_Wallet_Small", 200


def ocarina(items: Iterable[str]) -> str | None:
    chosen = set(items)
    if "Ocarina of Time" in chosen:
        return "Item_Ocarina_Time"
    return "Item_Ocarina_Fairy" if "Fairy Ocarina" in chosen else None
