"""Default-off bag-bomb lift bypass; no inventory or Bomb Flower changes.

The native pre-lift compares required <= PlayerStatus.LiftGrade (plans/03-game-data.md section 30).
Use a private component name: Bomb Flower packs also contain the native Item_Bomb lift resource.
Leaving that resource untouched avoids sharing its new grade through the runtime's resource cache.
"""

from clawshot.formats import byml, sarc
from clawshot.formats.byml import U32
from clawshot.patch.plan import PatchError
from clawshot.patch.write import FileChanges

PACK = "Pack/Actor/Item_Bomb.pack.zs"
ACTOR = "Actor/Item_Bomb.engine__actor__ActorParam.bgyml"
NATIVE_LIFT = "Component/LiftableParam/Item_Bomb.game__component__LiftableParam.bgyml"
BAG_LIFT = "Component/LiftableParam/Clawshot_BagBomb.game__component__LiftableParam.bgyml"
LOW = 3655598229
NONE = 3069107721


def transform(data: bytes) -> bytes:
    pack = sarc.read(data)
    if ACTOR not in pack or NATIVE_LIFT not in pack or BAG_LIFT in pack:
        raise PatchError("Item_Bomb: missing native actor/lift component or bag-bomb component already present")
    actor = byml.load(pack[ACTOR])
    components = actor.root.get("Components", {})
    if components.get("LiftableRef") != "?" + NATIVE_LIFT:
        raise PatchError(f"Item_Bomb: stale lift reference {components.get('LiftableRef')!r}")
    lift = byml.load(pack[NATIVE_LIFT])
    if lift.root.get("LiftGrade") != LOW:
        raise PatchError(f"Item_Bomb: stale required lift grade {lift.root.get('LiftGrade')!r}")
    lift.root["LiftGrade"] = U32(NONE)
    components["LiftableRef"] = "?" + BAG_LIFT
    for name, document in ((ACTOR, actor), (BAG_LIFT, lift)):
        written = byml.dump(document)
        if difference := byml.difference(document.root, byml.read(written)):
            raise PatchError(f"Item_Bomb: {name} failed read-back: {difference}")
        pack[name] = written
    result = sarc.write(pack)
    if sarc.read(result) != pack:
        raise PatchError("Item_Bomb: patched pack failed read-back")
    return result


def changes(*, enabled: bool) -> FileChanges:
    return {PACK: transform} if enabled else {}
