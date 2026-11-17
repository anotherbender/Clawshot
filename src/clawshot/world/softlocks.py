"""Graph return diagnostics and evidenced-region certificates, without save-warp assumptions."""

from collections import defaultdict, deque
from collections.abc import Collection, Mapping
from dataclasses import dataclass

from clawshot.world.model import World
from clawshot.world.rules import AGES, DAY, NIGHT
from clawshot.world.search import Search


@dataclass(frozen=True)
class Trap:
    sphere: int
    age: str
    region: str
    time: str


def reachable_traps(search: Search, sphere: int = 0, *, regions: Collection[str] | None = None) -> list[Trap]:
    """Reverse the currently usable graph, retaining age and arrival time.

    A graph failure is a diagnostic candidate, not proof of a physical game trap.
    ``regions`` limits a certificate to explicitly evidenced physical regions.
    Ordinary missing returns and unverified song permissions remain audit debt.

    Root is OoTR's abstract spawn/song dispatcher, not a physical return location.
    Native worlds name the actual spawn rooms as their per-age return anchors.
    Farore's Wind is not an escape certificate: ownership proves no saved point.
    """
    search.update()
    world = search.world
    anchors = world.settings.get("softlock_anchors", {}) if world.start == "Root" else {}
    ignored = set(world.settings.get("softlock_virtual_regions", ())) if anchors else set()
    result = []
    for age in AGES:
        counts = search.inventory(age)
        reached = search.reached[age]
        if regions is not None and not any(name in reached for name in regions):
            continue
        anchor = anchors.get(age, world.start)
        targets = (anchor,) if isinstance(anchor, str) else anchor
        reverse = defaultdict(list)
        for name, region in world.regions.items():
            if region.time_passes:
                reverse[(name, NIGHT)].append((name, DAY))
                reverse[(name, DAY)].append((name, NIGHT))
            for tod in (DAY, NIGHT):
                node = (name, tod)
                for exit in region.exits:
                    if exit.target not in world.regions or exit.target == "Farores Wind Warp":
                        continue
                    if not exit.rule.fn(counts, age, tod):
                        continue
                    target = world.regions[exit.target]
                    times = DAY | NIGHT if target.time_passes else (target.provides_time or tod)
                    for bit in (DAY, NIGHT):
                        if times & bit:
                            reverse[(target.name, bit)].append(node)
        safe = {(target, tod) for target in targets for tod in (DAY, NIGHT)}
        queue = deque(safe)
        while queue:
            for node in reverse[queue.popleft()]:
                if node not in safe:
                    safe.add(node)
                    queue.append(node)
        for name in world.regions:
            if name in ignored or regions is not None and name not in regions:
                continue
            for tod, label in ((DAY, "day"), (NIGHT, "night")):
                if reached.get(name, 0) & tod and (name, tod) not in safe:
                    result.append(Trap(sphere, age, name, label))
    return result


def audit(world: World, placements: Mapping[str, str], *, regions: Collection[str] | None = None) -> list[Trap]:
    """Inspect the initial frontier and every full sphere, including fixed rewards."""
    findings = []
    Search(world).collect_spheres(
        placements,
        observe=lambda search, index: findings.extend(reachable_traps(search, index, regions=regions)),
    )
    return findings
