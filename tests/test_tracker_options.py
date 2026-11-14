"""Exercise the shipped JS fragment parser; Node is optional and is not an app dependency."""

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
