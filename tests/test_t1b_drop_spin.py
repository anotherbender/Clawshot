"""T1-b (ocarina-song-drops-everywhere plan 19): a Skulltula drop of an ocarina or song spins like a token.

The native token spins because its ASInfo autoplays ``Rotate_Obj`` (``Obj_Token_Gold``'s ASInfo; its AI never asks
for it). The ocarina and song world pickups use ``Item_Obj``, which autoplays nothing (their floor AI, ``DropItem``,
starts ``Rotate_Obj``), so a drop with the token's AI and their ASInfo stood still, and the song effect, triggered by
``Rotate_Obj``, never showed (BBender, run T1, 2026-11-24). The drop of such a donor takes the token's ASInfo, which
is ``Item_Obj`` plus that autoplay, over the donor's own ``Item_Common`` animation set. Synthetic packs from
``test_tokens`` (hard rule 1).
"""

import pytest
from test_tokens import (
    ALLOWED,
    GENERATED,
    GENERATED_REWARDS,
    ITEM_OBJ,
    SHIELD_PICKUP,
    TOKEN_COMPONENTS,
    TOWER,
    census,
    generated_donor,
    member,
    raw,
    ref,
    w,
    world,  # noqa: F401  (fixture)
)

from clawshot.formats import byml, sarc
from clawshot.patch import actor_packs, tokens
from clawshot.patch.plan import PatchError

TOKEN_ASINFO = TOKEN_COMPONENTS["ASInfoRef"]


def drop_components(delivery, donor):
    pickup = delivery.pickups[donor]
    pack = sarc.read(delivery.new_files[tokens.pack_path(pickup)].data)
    return pack, actor_packs.closure([pack], pickup).components


def test_the_spin_rule_covers_the_ocarina_and_generated_donors_only():
    assert tokens.spins("Obj_Ocarina_Time")
    assert tokens.spins("Obj_Clawshot_Ocarina_Fairy") and tokens.spins("Obj_Clawshot_Melody_LightPrelude")
    assert not tokens.spins("Obj_Shield_Hylian") and not tokens.spins("Item_Boomerang")


def test_a_generated_donors_drop_autoplays_the_tokens_spin(world):  # noqa: F811 (the imported fixture)
    donor = generated_donor()
    delivery = tokens.build(
        world, {TOWER: GENERATED}, census(), rewards=GENERATED_REWARDS, generated={GENERATED: donor}
    )
    pack, components = drop_components(delivery, GENERATED)
    assert components["ASInfoRef"] == TOKEN_ASINFO
    assert byml.read(pack[member(TOKEN_ASINFO)])["AutoPlayASName"] == tokens.SPIN
    # The rest of the display stays the donor's: its animation set and effect user.
    donor_components = actor_packs.closure([sarc.read(donor.file.data)], GENERATED).components
    for key in ("ASRef", "ELinkRef", "SLinkRef", "AnimationRef", "ModelInfoRef"):
        assert components.get(key) == donor_components.get(key), key
    # The token's ASInfo is copied byte-identical from the token pack.
    file = delivery.new_files[tokens.pack_path(delivery.pickups[GENERATED])]
    assert file.copied[member(TOKEN_ASINFO)] == tokens.pack_path(tokens.TOKEN)
    assert sarc.read(raw(world, tokens.TOKEN_PACK))[member(TOKEN_ASINFO)] == pack[member(TOKEN_ASINFO)]


def test_played_native_drops_keep_their_own_display(world):  # noqa: F811 (the imported fixture)
    delivery = tokens.build(world, {TOWER: "Obj_Shield_Hylian"}, census(), rewards=ALLOWED)
    assert delivery.pickups["Obj_Shield_Hylian"] == SHIELD_PICKUP
    _, components = drop_components(delivery, "Obj_Shield_Hylian")
    assert components["ASInfoRef"] == ref(ITEM_OBJ)


OWN_ASINFO = "Component/ASInfo/Generated_Obj.engine__component__ASInfo.bgyml"


def with_own_asinfo(tree: dict):
    """The generated donor with an ASInfo member of its own (``tree``)."""
    donor = generated_donor()
    pack = sarc.read(donor.file.data)
    param = byml.read(pack[f"Actor/{GENERATED}.engine__actor__ActorParam.bgyml"])
    param["Components"]["ASInfoRef"] = ref(OWN_ASINFO)
    pack[f"Actor/{GENERATED}.engine__actor__ActorParam.bgyml"] = w(param)
    pack[OWN_ASINFO] = w(tree)
    copied = {name: source for name, source in donor.file.copied.items() if name != ITEM_OBJ}
    return tokens.GeneratedDonor(type(donor.file)(sarc.write(pack), copied=copied), donor.rows)


def test_a_donor_asinfo_that_differs_beyond_the_autoplay_is_refused(world):  # noqa: F811 (the imported fixture)
    changed = with_own_asinfo({"AutoPlayASName": "", "NumController": 9})
    with pytest.raises(PatchError, match="differs from the token's beyond AutoPlayASName"):
        tokens.build(world, {TOWER: GENERATED}, census(), rewards=GENERATED_REWARDS, generated={GENERATED: changed})


def test_a_donor_that_already_autoplays_keeps_its_asinfo(world):  # noqa: F811 (the imported fixture)
    changed = with_own_asinfo({"AutoPlayASName": "Rotate_Obj"})
    delivery = tokens.build(
        world, {TOWER: GENERATED}, census(), rewards=GENERATED_REWARDS, generated={GENERATED: changed}
    )
    _, components = drop_components(delivery, GENERATED)
    assert components["ASInfoRef"] == ref(OWN_ASINFO)
