"""A non-bottle purchase must reach a real offer and refusal message at a potion seller."""

import pytest

from clawshot.formats import msbt, sarc
from clawshot.patch import shops


def messages():
    files = {"untouched.bin": b"untouched"}
    for actor, labels in shops.POTION_MESSAGE_DONORS.items():
        files[f"EventFlowMsg/{actor}.msbt"] = msbt.write(
            msbt.Msbt({label: [f"Synthetic {actor} {label}"] for label in labels}, 31)
        )
    files[shops.POTION_MESSAGES] = msbt.write(
        msbt.Msbt({"Shop_01": ["Native potion offer"], "Shop_07": ["Native bottle thank-you"]}, 31)
    )
    return files


@pytest.mark.parametrize(
    "label,donor,source_label",
    [
        ("Shop_01_Shield_Adult", "Npc_Kokiri_001_Shop_Child", "Shop_01_Shield_Adult"),
        ("Shop_04", "Npc_Kokiri_001_Shop_Child", "Shop_04"),
        ("Shop_06", "Npc_Kokiri_001_Shop_Child", "Shop_06"),
        ("Shop_16", "Npc_Hylia_018_Shop_Child", "Shop_16"),
        ("Shop_31", "Npc_Hylia_018_Shop_Child", "Shop_31"),
        ("Shop_32", "Npc_Goron_011_Shop_Child", "Shop_32"),
        ("Shop_09", "Npc_Hylia_018_Shop_Child", "Shop_09_04"),
    ],
)
def test_remapped_nonbottle_offer_and_refusal_resolve_without_changing_bottle_dialogue(label, donor, source_label):
    before = messages()
    result = sarc.read(shops.potion_messages(sarc.write(before)))
    target = msbt.read(result[shops.POTION_MESSAGES]).messages
    source = msbt.read(before[f"EventFlowMsg/{donor}.msbt"]).messages
    assert target[label] == source[source_label]
    assert target["Shop_01"] == ["Native potion offer"]
    assert target["Shop_07"] == ["Native bottle thank-you"]
    del result[shops.POTION_MESSAGES], before[shops.POTION_MESSAGES]
    assert result == before
