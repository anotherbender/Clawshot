# Round 19 — UI startup deadline dependency (cs19h)

Agent/model: `cs19h`, `openai-codex/gpt-6.1-sol`; branch `r19/ui-startup`, base `d9514c4`.
Scope: saved-seed test setup and the existing production publication path. No gameplay, settings,
locations, fill or output-format change; no game started and no player seed/save opened.

## Ground truth and diagnosis

Claude reported two round-19 gate setup errors: the saved-seed Play test's `deleted` case and the
unsafe-extra-mod case. Both waited20s for `_listen` with job status `running`, all stages including
`validate` still `pending`. Reported stage load: CPU69%, Defender52%. Round18 had the same family.
Those reports are accepted; no unchanged gate was rerun to confirm them.

This is **not an HTTP-server startup timeout or a required background dump check**:

- `tests/test_app_play.py::made_ui_seed` originally started `Jobs(synthetic_run)` for every consumer,
  then used `tests/test_app.py::wait_job` to join the monitor thread for20s.
- `Jobs.start` selects multiprocessing **spawn**, initializes all stages pending, starts a new process,
  then starts `_listen`. The listener waits on the pipe/process sentinel until a result/error/exit,
  joins the worker and publishes the completed seed.
- `synthetic_run` reports `validate` as its **first statement**, before its settings validation.
  A pending validation stage therefore means the parent has not consumed even that first report.
  It does not show the validator spending20s. Spawn bootstrap, imports, OS/Defender scheduling and
  parent-monitor scheduling all precede that observation; their individual contributions are not
  separately established by the failed snapshots.
- The saved-seed Play, library, export and first-run tests need real completed files and a manifest,
  not another process-lifecycle experiment. Repeated cold spawns create an unnecessary load-sensitive
  dependency for each parametrized consumer.

**[INFERENCE]** contention/Defender amplifies cold-spawn/import/report latency. The source and printed
pending-stage state locate the unnecessary dependency; they do not prove a native deadlock or attribute
all elapsed time to Defender.

## Change and Claude's additional condition

The fixture still runs the existing synthetic fill through the real production seed writer. It now
runs synchronously, then calls **the same `app.jobs.publish_seed` used by `Jobs._publish`**.

Publication was previously in the parent, not the child worker. Its existing body is extracted without
changing the protocol: hash completed seed files, exclusively reserve the absent output directory,
rename the seed, write the production manifest with `output_sha256`, roll back only the reserved output
on failure, and return the same result fields. `Jobs` retains its request/path recheck and serialization
with cancellation under its lock. The fixture has no hand-written manifest or copied publication code.

New test `test_saved_fixture_and_job_publish_identical_manifests` compares parsed **complete manifests**
from the synchronous fixture and a real spawned job: equality checks keys and values, including digest,
version/build, settings and counts. The existing worker success/failure/cancellation and HTTP responsiveness,
concurrent-output protection and sharing tests remain spawned.

**Claude's final decision:** only `tests/test_app.py::wait_job` changes its test-only monitor join from20s
to60s. Its comment cites the measured20.2–21.2s setups at100% CPU plus Defender. After removing the fixture
spawns, only the nine genuine lifecycle test functions use it. It is a bounded hang detector, not a product
timeout or a responsiveness promise. No app timeout, HTTP deadline, retry, mock publication or fallback changes.
No group marks, scheduler hooks/flags, pytest pin or dependency changes remain.

## Measured diagnosis and baseline

A one-job synthetic timing probe, no artificial load, measured:

| Work | Seconds |
|---|---:|
| Parent imports | 3.308 |
| Spawned job: first validation report consumed | 0.986 |
| Spawned job: source report consumed | 2.266 |
| Spawned job: publication begins | 2.552 |
| Spawned job: total completion | 2.583 |
| Initial synchronous prototype: generation plus digest/manifest | 0.368 |

The prototype produced an identical seed digest and byte-identical manifest. This was a single diagnostic,
not a reproduction of the20s failure and not final-helper performance. Initial machine sampling reported
CPU100%; its first Defender WQL query was invalid and returned null, **not evidence of idle Defender**.
The later baseline/candidate sampler uses a corrected query.

The initial prototype focus passed **76 tests in30.15s**, `-n4`, `CLAWSHOT_WORKERS=1`. This predates the
shared-publication extraction and new parity test; it is not the final implementation's acceptance result.

### Frozen baseline timing

To answer Claude's speed request, `git archive d9514c4` supplied an independent read-only source snapshot
under `E:/OOTRemake/work/r19-ui-startup/baseline/`. No other branch/worktree was edited. Both timing stages
use the same Python environment and explicit source paths, with imported `app/jobs.py` path checked.

The baseline focus ran once at `-n4`, internal workers1, on these eight files:

```text
tests/test_app.py tests/test_app_play.py tests/test_app_library.py tests/test_app_emulator.py
tests/test_ui.py tests/test_ui_first_run.py tests/test_ui_games.py tests/test_ui_sharing.py
```

Observed **72 passed,4 setup errors in81.35s**. Every error prints the same `made_ui_seed -> wait_job`
monitor-join failure with validation pending. Error cases: unsafe-seed `[seed]`, emulator exclusive-copy,
manifest-authority `[note_available]`, and registered-result document access. Their setup durations were
20.24–21.16s. Baseline stage sampling: CPU100%, Defender raw `PercentProcessorTime=63`, no game process.
This is a **failed baseline timing**, not a clean pass-to-pass benchmark. It is retained and is not rerun.
The driver stopped before candidate on that nonzero exit; candidate verification is a separate invocation
selecting only the changed implementation, not an unchanged retry of the baseline.

Evidence outside the repo: `E:/OOTRemake/work/r19-ui-startup/` contains `timing.json`, `focused.log`
(initial prototype), `baseline-d9514c4-focused.log`, and `comparison.json` (failed baseline receipt).

### Intermediate fixture-only result

Before the final hang-detector decision, the shared-publication candidate had **69 passed,8 failed
in165.53s**: seven genuine lifecycle joins still stopped before their first validation report, plus one
HTTP request deadline. CPU sampling100%, Defender raw26, no game. Even synchronous fixture setup took22.07s
and an HTTP library case39.17s. This printed evidence broadened the diagnosis from unnecessary fixture
spawns to the remaining test-only cold-spawn hang detector; it is retained, not reclassified as a pass.

### Discarded xdist grouping investigation

The group alternative was tested and then explicitly withdrawn by Claude. The current environment has
pytest9.2.0 and pytest-xdist3.8.0. Diagnostic hooks printed `loadgroup=true`, group marks present and the
worker collection hook registered, yet no grouped node suffix and different workers for the two marked
tests. Executed grouping bytecode writes `item._nodeid`; pytest9.2's `Node.nodeid` getter reads `_id`.
That explains why even the supported grouping flag silently failed to group here. A controller
`LoadGroupScheduling` banner alone was not proof. The interim77-pass runs (18.37s,14.50s,14.06s) were
followed by failed explicit grouping assertions; none is represented as grouping acceptance.

Dependency finding: `pyproject.toml` dev dependencies are `pytest>=8` and Ruff, **not pytest-xdist**.
The current PyPI pytest-xdist metadata also lists3.8.0 as latest
(<https://pypi.org/pypi/pytest-xdist/json>). No third-party patch or compatibility shim is retained.
The contributor command remains `uv run --with pytest-xdist pytest -n auto`, with no grouping flag;
the focused proof bounds it to `-n4`. `CONTRIBUTING.md` now explains that optional command and the distinction
between xdist workers and nested generator pools. Existing serial gate notes and tool commands need no
flag update under Claude's final decision; historical receipts are not rewritten.

## Final focused acceptance

Final code has the synchronous fixture, shared production publisher, full-manifest parity test and
the approved60s **test-helper-only** hang detector. Group marks, marker registration and experimental
configuration hooks were removed; `pyproject.toml`, `uv.lock`, the UI HTTP request deadline and every
product timeout remain unchanged.

```sh
CLAWSHOT_WORKERS=1 uv run --with pytest-xdist pytest \
  tests/test_app.py tests/test_app_play.py tests/test_app_library.py tests/test_app_emulator.py \
  tests/test_ui.py tests/test_ui_first_run.py tests/test_ui_games.py tests/test_ui_sharing.py \
  -n 4 -q --durations=12 --tb=short
CLAWSHOT_WORKERS=1 uv run pytest \
  tests/test_app.py::test_job_writes_beatable_synthetic_seed_and_preserves_source -q
uv run ruff format --check src/clawshot/app/jobs.py tests/test_app.py tests/test_app_play.py
uv run ruff check src/clawshot/app/jobs.py tests/test_app.py tests/test_app_play.py
```

The timing harness invokes the first pytest command with the same uv-supplied Python and explicit
source paths. **77 passed in11.09s** (11.597s subprocess wall), including both original reported Play
cases and full fixture/job manifest equality. The slowest genuine lifecycle call took2.30s;
the new parity test took0.84s. Plain serial pytest, with no xdist/grouping flag: **1 passed in1.11s**.
Scoped Ruff: **3 files already formatted; all checks passed**. No test assertion was removed or narrowed.

| Timing stage | Outcome | Pytest seconds | Sampled CPU load | Defender raw process counter |
|---|---|---:|---:|---:|
| Frozen d9514c4 | 72 passed,4 setup errors | 81.35 | 100 | 63 |
| Final candidate | 77 passed | 11.09 | 77 | 12 |

Observed elapsed reduction: **70.26s (86.4%)**, while adding one test. This is **not a controlled
pass-to-pass throughput benchmark**: the baseline failed and machine load changed. The stronger causal
claim is narrower: every saved-seed consumer no longer depends on a cold subprocess; the retained real
jobs still exercise their actual lifecycle and production output. The single-job probe independently
showed the avoidable setup overhead, without claiming a stable speed factor for a whole gate.

Final external receipts: `candidate-final-focused.log`, `comparison-candidate-final.json`; earlier
failed/experimental receipts remain distinct. The throwaway timing/probe scripts are removed after
recording their results. No browser surface, game output or runtime behavior changed.

## Gate ownership and limits

No gate lock acquired and no lock waiter started. Claude's order puts this track **sixth**, after cs19c's
sword remainder; it must not acquire the lock before the predecessor releases and this track is next.
Only focused checks, at most four xdist workers with internal workers1, belong to this receipt.
No sweep is required: no placements, logic, destinations or output resources change. Claude queues the
full gate after the current tracks; focused results alone are not a full-gate pass.
