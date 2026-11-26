"""Exercise the shipped tracker.js under Node: its fragment parser, and its rendering of a tracker snapshot in a
minimal stand-in DOM. Node is optional and is not an app dependency."""

import json
import shutil
import subprocess

import pytest

from clawshot.ui.server import ASSETS

NODE = shutil.which("node")
pytestmark = pytest.mark.skipif(NODE is None, reason="Node is needed only for frontend fragment-parser tests")
DEFAULT = ["dungeons", "collection", "items", "rewards"]
QUEST = ["collection", "songs", "rewards"]


def parse_sections(tmp_path, fragments, parser="parseTrackerSections"):
    # The renderer exits without a root; the actual pure parser runs with Node's URLSearchParams.
    script = """
const fs = require('node:fs');
const vm = require('node:vm');
const context = {document: {getElementById: () => null}, URLSearchParams};
vm.runInNewContext(fs.readFileSync(process.argv[2], 'utf8'), context);
const [parser, fragments] = JSON.parse(fs.readFileSync(0, 'utf8'));
console.log(JSON.stringify(fragments.map(value => context[parser](value))));
"""
    runner = tmp_path / "tracker-options.cjs"
    runner.write_text(script, encoding="utf-8")
    result = subprocess.run(
        [NODE, str(runner), str(ASSETS / "tracker.js")],
        input=json.dumps([parser, fragments]),
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )
    assert result.returncode == 0, {"stdout": result.stdout, "stderr": result.stderr}
    return json.loads(result.stdout)


# A stand-in for the few DOM calls tracker.js makes; fetch answers every tracker poll with one snapshot.
RENDER = r"""
const fs = require('node:fs');
const vm = require('node:vm');
const input = JSON.parse(fs.readFileSync(0, 'utf8'));
const {fragment, obs, snapshot, actions = [], storage = {}, confirm = false, after = null} = input;

class Element {
  constructor(tag, text = '') {
    this.tagName = tag.toUpperCase();
    this.childNodes = [];
    this.parentElement = null;
    this.className = '';
    this.dataset = {};
    this.attributes = {};
    this.style = {setProperty() {}};
    this.hidden = false;
    this.ownText = text;
    this.listeners = {};
  }
  get classList() {
    const names = () => this.className.split(/\s+/).filter(Boolean);
    const set = (list) => { this.className = [...new Set(list)].join(' '); };
    return {
      add: (...add) => set([...names(), ...add]),
      remove: (...drop) => set(names().filter((name) => !drop.includes(name))),
      toggle: (name, force = !names().includes(name)) => {
        set(force ? [...names(), name] : names().filter((other) => other !== name));
        return force;
      },
      contains: (name) => names().includes(name),
    };
  }
  append(...nodes) {
    for (const child of nodes) {
      const el = typeof child === 'string' ? new Element('#text', child) : child;
      el.remove();
      el.parentElement = this;
      this.childNodes.push(el);
    }
  }
  replaceChildren(...nodes) {
    for (const child of this.childNodes) child.parentElement = null;
    this.childNodes = [];
    this.append(...nodes);
  }
  remove() {
    if (!this.parentElement) return;
    const siblings = this.parentElement.childNodes;
    siblings.splice(siblings.indexOf(this), 1);
    this.parentElement = null;
  }
  get textContent() { return this.ownText + this.childNodes.map((child) => child.textContent).join(''); }
  set textContent(value) { this.replaceChildren(); this.ownText = String(value); }
  setAttribute(name, value) { this.attributes[name] = String(value); }
  addEventListener(type, listener) { (this.listeners[type] ||= []).push(listener); }
  dispatch(type) { for (const listener of this.listeners[type] || []) listener({preventDefault() {}}); }
  focus() {}
  select() {}
  get options() { return this.childNodes.filter((child) => child.tagName === 'OPTION'); }
  descendants() { return this.childNodes.flatMap((child) => [child, ...child.descendants()]); }
  querySelector(selector) { return this.querySelectorAll(selector)[0] ?? null; }
  querySelectorAll(selector) {
    const data = /^\[data-([a-z-]+)\]$/.exec(selector);
    const key = data && data[1].replace(/-([a-z])/g, (_, letter) => letter.toUpperCase());
    return this.descendants().filter((el) => data ? key in el.dataset : el.tagName === selector.toUpperCase());
  }
}
class Option extends Element {
  constructor(text = '', value = text) { super('option', text); this.value = value; }
}

const root = new Element('div');
const body = new Element('body');
if (obs) body.dataset.tracker = 'obs';
const documentElement = new Element('html');
// The app page's Checks tab and side panel (absent on the OBS page); the Checks screen is the shown one.
const checksRoot = new Element('div');
const panelIds = ['checks', 'description-title', 'description-text', 'description-note', 'check-details'];
const panel = Object.fromEntries(panelIds.map((id) => [id, new Element(id === 'check-details' ? 'div' : 'p')]));
const byPageId = {'tracker-root': root, ...(obs ? {} : {'checks-root': checksRoot, ...panel})};
const document = {
  body, documentElement,
  getElementById: (id) => byPageId[id] ?? null,
  createElement: (tag) => new Element(tag),
  createTextNode: (text) => new Element('#text', text),
};
const requested = [], posts = [];
async function fetch(url, init = {}) {
  const route = url.slice(url.lastIndexOf('/api/') + 5);
  requested.push(route);
  if (init.method === 'POST') posts.push({route, body: JSON.parse(init.body)});
  const data = route === 'schema' ? {dialogs_available: false} : init.method === 'POST' && after ? after : snapshot;
  return {ok: true, json: async () => data};
}
// localStorage: a plain store, or (storage null) one whose every access throws, as in a private window.
const stored = storage === null ? null : {...storage};
const localStorage = {
  getItem(key) { if (!stored) throw new Error('storage unavailable'); return key in stored ? stored[key] : null; },
  setItem(key, value) { if (!stored) throw new Error('storage unavailable'); stored[key] = String(value); },
  removeItem(key) { if (!stored) throw new Error('storage unavailable'); delete stored[key]; },
};
const location = {
  pathname: obs ? '/s/secret/tracker.html' : '/s/secret/', hash: fragment, origin: 'http://127.0.0.1:9',
};
const context = {
  document, location, fetch, URL, URLSearchParams, Option, console, navigator: {},
  window: {addEventListener() {}, confirm: () => confirm, localStorage}, setInterval: () => 1, clearInterval() {},
};
(async () => {
  vm.runInNewContext(fs.readFileSync(process.argv[2], 'utf8'), context);
  for (let turn = 0; turn < 100 && documentElement.dataset.trackerReady !== 'true'; turn++) {
    await new Promise((resolve) => setImmediate(resolve));
  }
  const settle = async () => {
    for (let turn = 0; turn < 20; turn++) await new Promise((resolve) => setImmediate(resolve));
  };
  const all = () => [...root.descendants(), ...checksRoot.descendants()];
  const byId = (id) => all().find((el) => el.id === id);
  for (const action of actions) {
    const target = action.id
      ? byId(action.id)
      : action.check
        ? all().find((el) => el.dataset.check === action.check)
        : all().filter((el) => el.classList.contains(action.class))[action.index || 0];
    if ('value' in action) target.value = action.value;
    if ('checked' in action) target.checked = action.checked;
    target.dispatch(action.event);
    await settle();
  }
  const text = (name) => all().filter((el) => el.classList.contains(name)).map((el) => el.textContent);
  const shown = (el) => { for (let at = el; at; at = at.parentElement) if (at.hidden) return false; return true; };
  const control = (id) => {
    const el = byId(id);
    return el ? {value: el.value, checked: el.checked, disabled: !!el.disabled} : null;
  };
  console.log(JSON.stringify({
    checks: all().filter((el) => el.classList.contains('tracker-check')).map((el) => ({
      id: el.dataset.check, text: el.textContent, className: el.className, shown: shown(el),
      disabled: el.attributes['aria-disabled'] === 'true',
    })),
    // Each area's counts, with its name and the ready and after-event notes beside them in its heading.
    areaHeads: all().filter((el) => el.classList.contains('tracker-area-counts')).map((el) => {
      const beside = (name) => el.parentElement.childNodes.filter((child) => child.classList.contains(name))
        .map((child) => child.textContent);
      return {
        name: el.parentElement.childNodes.find((child) => child.tagName === 'STRONG')?.textContent ?? null,
        text: el.textContent, shown: shown(el),
        ready: beside('tracker-area-ready'), after: beside('tracker-area-after'),
      };
    }),
    notes: text('tracker-logic-note'),
    warnings: text('tracker-warnings'),
    controls: {
      age: control('tracker-age'), show: control('tracker-show'), finished: control('tracker-hide-finished'),
      vanilla: control('tracker-vanilla'), clear: control('tracker-clear-marks'),
    },
    showOptions: (byId('tracker-show')?.options || []).map((option) => ({
      value: option.value, disabled: !!option.disabled,
    })),
    legend: all().filter((el) => el.classList.contains('tracker-legend')).map((el) => ({
      text: el.textContent, shown: shown(el),
    })),
    details: obs ? null : {
      title: panel['description-title'].textContent, text: panel['description-text'].textContent,
      body: panel['check-details'].textContent, shown: !panel['check-details'].hidden,
      // The side panel's rows, term to value.
      rows: Object.fromEntries(panel['check-details'].descendants().filter((el) => el.tagName === 'DT').map((term) => {
        const siblings = term.parentElement.childNodes;
        return [term.textContent, siblings[siblings.indexOf(term) + 1]?.textContent ?? ''];
      })),
    },
    posts,
    storage: stored,
    ready: documentElement.dataset.trackerReady === 'true',
    requested,
    compact: body.classList.contains('tracker-no-labels'),
    status: text('tracker-status'),  // a render error lands here, so a failed render prints its cause
    checksStatus: text('tracker-checks-status'),
    noSave: text('tracker-no-save'),
    counts: text('tracker-counts'),
    areas: text('tracker-area'),
    cells: root.descendants().filter((el) => el.classList.contains('tracker-cell')).map((el) => ({
      className: el.className, label: el.attributes['aria-label'] || '',
      captions: el.childNodes.filter((child) => child.tagName === 'SMALL').map((child) => child.textContent),
      badges: el.descendants().filter((child) => child.classList.contains('tracker-badge')).map((child) =>
        child.textContent),
    })),
    // Per OBS dungeon row: 'name:<shown name>', the item name of each drawn cell, '' for an empty slot.
    dungeonRows: root.descendants().filter((el) => el.classList.contains('tracker-dungeon-row')).map((row) =>
      row.childNodes.map((cell) => cell.classList.contains('tracker-dungeon-name') ? 'name:' + cell.textContent
        : cell.classList.contains('tracker-dungeon-none') ? '' : cell.attributes['aria-label'].split(' · ')[1])),
  }));
})();
"""


def render_tracker(tmp_path, snapshot, *, obs, fragment="", **page):
    """The shipped renderer drawing one tracker ``snapshot``: the app tab, or (``obs``) the OBS page opened with URL
    ``fragment``. Returns the rendered text by element class (``status``, ``counts``, ``areas``) and the routes it
    polled; for the in-logic controls also ``checks``, ``areaHeads`` (each with its ``name`` and ``ready`` and
    ``after`` note texts), ``notes``, ``controls``, ``details`` (with its ``rows``, term to value), ``posts`` and
    ``storage``. ``page`` may give ``actions`` (``{id, check (a row's check ID) or class with index, value/checked,
    event}``, dispatched in order after the first render), ``storage`` (localStorage's contents; None makes every
    access throw), ``confirm`` (what ``window.confirm`` answers) and ``after`` (the snapshot a POST answers)."""
    runner = tmp_path / "tracker-render.cjs"
    runner.write_text(RENDER, encoding="utf-8")
    result = subprocess.run(
        [NODE, str(runner), str(ASSETS / "tracker.js")],
        input=json.dumps({"fragment": fragment, "obs": obs, "snapshot": snapshot, **page}),
        capture_output=True,
        encoding="utf-8",  # the rendered text has non-ASCII separators; Windows' locale default would garble them
        timeout=10,
        check=False,
    )
    assert result.returncode == 0, {"stdout": result.stdout, "stderr": result.stderr}
    rendered = json.loads(result.stdout)
    assert rendered["ready"], rendered
    return rendered


def test_sections_select_groups_without_reordering_or_duplicate_groups(tmp_path):
    fragments = [
        "#columns=4&labels=0&sections=dungeons",
        "#sections=items%2Cquest",
        "#sections=quest,items,quest",
        "#sections=%20quest%20",
    ]
    assert parse_sections(tmp_path, fragments) == [
        ["dungeons"],
        ["collection", "items", "songs", "rewards"],
        ["collection", "items", "songs", "rewards"],
        QUEST,
    ]


def test_missing_empty_or_unknown_section_selection_falls_back_to_all(tmp_path):
    fragments = [
        "#labels=0",
        "#sections=",
        "#sections=unknown",
        "#sections=items,unknown",
        "#sections=items,,quest",
        "#sections=%20%20",
    ]
    assert parse_sections(tmp_path, fragments) == [DEFAULT for _ in fragments]


def test_dungeon_names_default_to_short(tmp_path):
    fragments = ["#names=full", "#names=none", "#names=short", "#labels=0", "#names=", "#names=Full"]
    assert parse_sections(tmp_path, fragments, "parseDungeonNames") == [
        "full",
        "none",
        "short",
        "short",
        "short",
        "short",
    ]


def obs_snapshot(status="ok", held=False):
    """Two dungeons: the Deku Tree (no small keys or boss key in this seed) and the Forest Temple (all four)."""

    def dungeon(name, struct, *, keys, boss):
        return {
            "name": name,
            "id": struct,
            "small_keys": {"held": None if held is None else 0, "found": None if held is None else 0, "total": keys},
            "boss_key": held,
            "map": held,
            "compass": held,
            "has_boss_key": boss,
            "has_map": True,
            "has_compass": True,
        }

    state = {
        "seed": {"seed": 1},
        "dungeons": [
            dungeon("Deku Tree", "InsideTheDekuTree", keys=0, boss=False),
            dungeon("Forest Temple", "ForestTemple", keys=5, boss=True),
        ],
        "items": [
            {"id": "hookshot", "group": "upgrades", "label": "Hookshot", "held": held, "max_tier": 2, "tier": 0},
            {"id": "bow", "group": "items", "label": "Bow", "held": held, "max_tier": 1},
        ],
        "songs": [],
        "rewards": [],
        "hearts": {},
        "tokens": None,
        "skulltula_checks": {"collected": 0, "total": 0, "unknown": 0},
        "areas": [],
        "show_locations": False,
        "warnings": [],
    }
    return {"status": status, "state": state, "revision": 1, "warnings": []}


def test_obs_dungeon_rows_draw_only_the_items_a_dungeon_has_with_short_full_or_no_names(tmp_path):
    rows = {
        mode: render_tracker(tmp_path, obs_snapshot(), obs=True, fragment=f"#labels=0&names={mode}")["dungeonRows"]
        for mode in ("short", "full", "none")
    }
    items = [["", "", "Map", "Compass"], ["Small keys", "Boss key", "Map", "Compass"]]
    assert rows["short"] == [["name:Deku", *items[0]], ["name:Forest", *items[1]]]
    assert rows["full"] == [["name:Deku Tree", *items[0]], ["name:Forest Temple", *items[1]]]
    assert rows["none"] == items


def test_obs_before_any_save_draws_an_empty_inventory_not_unknown_tiles(tmp_path):
    waiting = render_tracker(tmp_path, obs_snapshot("waiting", held=None), obs=True, fragment="#labels=0")
    assert waiting["status"] == ["No save yet"]
    assert all(
        "tracker-missing" in cell["className"] and "tracker-unknown" not in cell["className"]
        for cell in waiting["cells"]
    )
    assert [badge for cell in waiting["cells"] for badge in cell["badges"]] == []
    # With a save read, a field the save lacks stays unknown (dashed, "?"); a missing item shows no tier or count.
    unknown = render_tracker(tmp_path, obs_snapshot("ok", held=None), obs=True, fragment="#labels=0")
    assert all("tracker-unknown" in cell["className"] for cell in unknown["cells"])
    assert "?" in [badge for cell in unknown["cells"] for badge in cell["badges"]]
    missing = render_tracker(tmp_path, obs_snapshot("ok", held=False), obs=True, fragment="#labels=0")
    assert [badge for cell in missing["cells"] for badge in cell["badges"]] == []


def test_each_obs_section_switches_on_its_own_and_checks_by_area_is_opt_in(tmp_path):
    snap = obs_snapshot()
    snap["state"]["songs"] = [{"id": "zeldas_lullaby", "group": "songs", "label": "Zelda's Lullaby", "held": True}]
    snap["state"]["areas"] = [{"name": "Field", "collected": 1, "total": 3}]
    fragments = ["", "#sections=songs", "#sections=areas", "#sections=dungeons,collection,items,songs,rewards,areas"]
    shown = {}
    for fragment in fragments:
        rendered = render_tracker(tmp_path, snap, obs=True, fragment=fragment)
        shown[fragment] = (
            bool(rendered["dungeonRows"]),
            bool(rendered["counts"]),
            len(rendered["cells"]),
            rendered["areas"],
        )
    assert shown[""] == (True, True, 2 + 6, [])  # 2 items + 6 drawn dungeon cells; no songs, no areas
    assert shown["#sections=songs"] == (False, False, 1, [])
    assert shown["#sections=areas"] == (False, False, 0, ["Field1 / 3"])
    assert shown["#sections=dungeons,collection,items,songs,rewards,areas"] == (True, True, 2 + 6 + 1, ["Field1 / 3"])


def test_the_obs_view_is_compact_unless_labels_are_asked_for(tmp_path):
    assert render_tracker(tmp_path, obs_snapshot(), obs=True, fragment="")["compact"] is True
    assert render_tracker(tmp_path, obs_snapshot(), obs=True, fragment="#labels=1")["compact"] is False


def test_tiles_carry_captions_only_for_tiers_and_counts(tmp_path):
    snap = obs_snapshot(held=True)
    snap["state"]["items"] = [
        {"id": "hookshot", "group": "upgrades", "label": "Hookshot", "held": True, "max_tier": 2, "tier": 1},
        {"id": "bow", "group": "items", "label": "Bow", "held": True, "max_tier": 1, "count": 30},
        {"id": "lens", "group": "items", "label": "Lens", "held": True, "max_tier": 1},
        {"id": "boots", "group": "items", "label": "Boots", "held": False, "max_tier": 1},
    ]
    rendered = render_tracker(tmp_path, snap, obs=True, fragment="#labels=1&sections=items")
    assert [cell["captions"] for cell in rendered["cells"]] == [["Tier 1"], ["30"], [], []]
    assert "Not held" in rendered["cells"][3]["label"]  # the tooltip and accessible name keep the state
