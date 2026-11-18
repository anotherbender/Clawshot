"""Exercise the shipped tracker.js under Node: its fragment parser, and its rendering of a tracker snapshot in a
minimal stand-in DOM. Node is optional and is not an app dependency."""

import json
import shutil
import subprocess

import pytest

from clawshot.ui.server import ASSETS

NODE = shutil.which("node")
pytestmark = pytest.mark.skipif(NODE is None, reason="Node is needed only for frontend fragment-parser tests")
ALL = ["items", "quest", "dungeons"]


def parse_sections(tmp_path, fragments):
    # The renderer exits without a root; the actual pure parser runs with Node's URLSearchParams.
    script = """
const fs = require('node:fs');
const vm = require('node:vm');
const context = {document: {getElementById: () => null}, URLSearchParams};
vm.runInNewContext(fs.readFileSync(process.argv[2], 'utf8'), context);
const fragments = JSON.parse(fs.readFileSync(0, 'utf8'));
console.log(JSON.stringify(fragments.map(value => context.parseTrackerSections(value))));
"""
    runner = tmp_path / "tracker-options.cjs"
    runner.write_text(script, encoding="utf-8")
    result = subprocess.run(
        [NODE, str(runner), str(ASSETS / "tracker.js")],
        input=json.dumps(fragments),
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
const {fragment, obs, snapshot} = JSON.parse(fs.readFileSync(0, 'utf8'));

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
  addEventListener() {}
  focus() {}
  select() {}
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
const document = {
  body, documentElement,
  getElementById: (id) => (id === 'tracker-root' ? root : null),
  createElement: (tag) => new Element(tag),
  createTextNode: (text) => new Element('#text', text),
};
const requested = [];
async function fetch(url) {
  const route = url.slice(url.lastIndexOf('/api/') + 5);
  requested.push(route);
  const data = route === 'schema' ? {dialogs_available: false} : snapshot;
  return {ok: true, json: async () => data};
}
const location = {
  pathname: obs ? '/s/secret/tracker.html' : '/s/secret/', hash: fragment, origin: 'http://127.0.0.1:9',
};
const context = {
  document, location, fetch, URL, URLSearchParams, Option, console, navigator: {},
  window: {addEventListener() {}, confirm: () => false}, setInterval: () => 1, clearInterval() {},
};
(async () => {
  vm.runInNewContext(fs.readFileSync(process.argv[2], 'utf8'), context);
  for (let turn = 0; turn < 100 && documentElement.dataset.trackerReady !== 'true'; turn++) {
    await new Promise((resolve) => setImmediate(resolve));
  }
  const text = (name) => root.descendants().filter((el) => el.classList.contains(name)).map((el) => el.textContent);
  console.log(JSON.stringify({
    ready: documentElement.dataset.trackerReady === 'true',
    requested,
    compact: body.classList.contains('tracker-no-labels'),
    status: text('tracker-status'),  // a render error lands here, so a failed render prints its cause
    counts: text('tracker-counts'),
    areas: text('tracker-area'),
  }));
})();
"""


def render_tracker(tmp_path, snapshot, *, obs, fragment=""):
    """The shipped renderer drawing one tracker ``snapshot``: the app tab, or (``obs``) the OBS page opened with URL
    ``fragment``. Returns the rendered text by element class (``status``, ``counts``, ``areas``) and the routes it
    polled."""
    runner = tmp_path / "tracker-render.cjs"
    runner.write_text(RENDER, encoding="utf-8")
    result = subprocess.run(
        [NODE, str(runner), str(ASSETS / "tracker.js")],
        input=json.dumps({"fragment": fragment, "obs": obs, "snapshot": snapshot}),
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
    assert parse_sections(tmp_path, fragments) == [["dungeons"], ["items", "quest"], ["items", "quest"], ["quest"]]


def test_missing_empty_or_unknown_section_selection_falls_back_to_all(tmp_path):
    fragments = [
        "#labels=0",
        "#sections=",
        "#sections=unknown",
        "#sections=items,unknown",
        "#sections=items,,quest",
        "#sections=%20%20",
    ]
    assert parse_sections(tmp_path, fragments) == [ALL for _ in fragments]
