"""The song floor pickups are built exactly when the settings could place a song as one (ocarina-song-drops-everywhere
record I14): Kareem's rule that they are written only once a feature places them (rounds/r21-pr41.md finding 4), as
a settings rule like the other get-display steps (PR #41, the maintainers' option 2). Synthetic world (hard rule 1).
"""

from types import SimpleNamespace

import pytest

from clawshot.patch import getitem, songs

SONG = next(iter(getitem.SONG_MODELS))


@pytest.mark.parametrize(
    ("shuffle", "songs_setting", "expected"),
    [
        (("Chest", "Gift", "Token"), "anywhere", True),
        (("Gift", "BossHeart"), "anywhere", True),
        (("Gift", "Freestanding"), "anywhere", True),
        (("Chest", "Gift"), "anywhere", False),  # no Skulltula or floor kind: Kareem's song seed writes none
        (("Chest", "Gift", "Token"), "song", False),  # songs stay at song locations
        (("Chest", "Token", "Freestanding"), "anywhere", False),  # no Gift kind: the song step does not run
    ],
)
def test_pickups_follow_the_settings(shuffle, songs_setting, expected):
    assert songs.pickups_possible(shuffle, songs_setting) is expected


def test_placed_pickups_lists_songs_at_skulltula_and_floor_kinds_only():
    world = SimpleNamespace(
        locations={
            "GS": SimpleNamespace(type="Token", vanilla="Gold Skulltula Token"),
            "Heart": SimpleNamespace(type="BossHeart", vanilla="Heart Container"),
            "Chest": SimpleNamespace(type="Chest", vanilla="Rupees (5)"),
            "Floor": SimpleNamespace(type="Freestanding", vanilla="Piece of Heart"),
        }
    )
    actors = SimpleNamespace(actors={"Song": SONG, "Rupees (5)": "Obj_Rupee_Blue"})
    placements = {"GS": "Song", "Heart": "Song", "Chest": "Song", "Floor": "Rupees (5)"}
    assert songs.placed_pickups(placements, world, actors) == ["GS", "Heart"]
