# Round 16 Track C: NUP file expansion cap (#31)

Agent: cs16c (`openai-codex/gpt-6.1-sol`). Branch: `r16/nup`, based on
`dd3b4537204cab9f81ccf45d5d590d7fb517c04b`. Read issue #31 with `gh issue view 31`
(read-only), and read reference commit `4617fb5b30b36c8c19007164aba1f7fc443669ba`.

## Implementation and decisions

- Each declared NUP file is limited to 512 MiB during authenticated TOC parsing;
  `read_file` checks again so direct/mutated records cannot bypass the limit.
- NUP uses one raw or Zstandard extent per file, not NX's block-reference layout.
  Raw chunks and native Zstandard blocks are decoded and SHA256-hashed before
  assembly. Output beyond the declared size is refused before retaining it.
- The limit is shared with NX in `pack/_limits.py`; NX's behavior is unchanged.
  No shared decoding abstraction: the wire formats differ.
- SHA256 moves into `NupReader.read_file`; the adapter no longer rehashes a
  completely allocated file. Empty files receive the same integrity check.
- Zstandard blocks are at most 128 KiB decoded (RFC 8878, section 3.1.1.2).
  Feed complete blocks to the native decoder, which validates compressed content
  and checksums; require its EOF. Check frame size/window before decoding.
  This preserves truncated-frame refusal without an unbounded decompressor call.
  Source: <https://www.rfc-editor.org/rfc/rfc8878#section-3.1.1.2>.
- Agent-proposed mechanism: use block framing rather than `stream_reader`.
  An isolated probe showed `stream_reader` returning all 100,000 decoded bytes
  from a frame missing its last checksum byte, without an error. Also, a closed
  reader retains its buffer export until destroyed. Neither behavior is used by
  the implementation.
- No product decisions, new dependency, version bump, settings change, working-set
  addition, or new layered-dump fixture. No generated seed content changes intended.

## Regression evidence

Failing-before command:

```sh
CLAWSHOT_WORKERS=4 uv run pytest tests/test_pack_nup.py -k "oversized_declared or direct_read or file_limit_boundary or tampered_file" -q
```

Five failures exposed the missing guards: a 2 GiB declaration reached member
access; a direct 536,870,913-byte declaration reached the ordinary size-mismatch
check; reducing the limit by one byte did not refuse opening; both raw and
compressed tampered members were returned by the low-level reader.

After the fix, the first focused run had 43 passes and one test-context failure:
`NupError: size mismatch ... 131072 > 1024` is translated to `PackError` only
when exiting `open_nup`. Moved the expected-error context outside the source
context; no implementation suppression or unchanged failing rerun.

The corrected focused run passed 45 NUP/NX tests. Four further frame round trips
cover known/unknown content sizes, checksums, and mixed raw and compressed blocks.
`uv run pytest tests/test_pack_nup.py -k streamed_frames -q`: 4 passed,
23 deselected. These cases are also included in the final gates.

Allocation measurements (standalone invocation of the regression cases,
`tracemalloc`, allocation tracing starts after payload construction):

| Case | Peak Python allocation, bytes | Asserted bound |
|---|---:|---:|
| Authenticated sub-1-KiB NUP declaring 2 GiB | 13,537 | < 1 MiB |
| Tampered raw 8 MiB member | 8,393,993 | < 12 MiB |
| Tampered compressed 8 MiB member | 8,524,060 | < 12 MiB |
| Unknown-size frame expanding past a 1 KiB declaration | 274,811 | < 1 MiB |
| Known-size frame exceeding a 1 KiB declaration | 13,849 | < 1 MiB |

The oversized-entry case rejects during open, before any payload decoder is
created. The tamper bounds exclude allocating both chunks and an assembled
8 MiB result. Both native codecs' payload bytes are actually changed, not just
an error-message expectation. Additional coverage checks the inclusive limit,
direct-read bypass, checksum truncation, and handle closure on rejected open.

## Runtime smoke

No `longshot.exe` or `hookshot.exe` was running at the stage start (`tasklist`).
Ran the actual preflight CLI against the read-only real NUP:

```sh
uv run python -m clawshot.pack.source "E:/Games/Hookshot/The Legend of Zelda Ocarina of Time [0400486024DEC000][v131072].nup" --expected fc09c4af707a0ca092188cf014f6fdf3d40514def773f097b798f52f9f28bc93
```

Exit 0: `Verified dump: fc09c4af707a0ca092188cf014f6fdf3d40514def773f097b798f52f9f28bc93`.
This exercises real metadata parsing, streaming reads, file integrity and the
supported-build fingerprint outside pytest.

## Final gates

Full gates are serialized under `E:/OOTRemake/work/rounds/r16/gate.lock`;
cs16a held it at the initial acquisition attempts. No foreign lock was removed.
At Claude's queue instruction, cancelled the automatic acquisition waiter:
cs16a's sweep, then cs16b's 15-minute #32 window, then cs16c's full gates.
The replacement waiter observed cs16b hold and release the lock before acquiring it.
Every final stage's runtime check found no game running; `CLAWSHOT_WORKERS=4`.

- `uv run ruff format --check`: 404 files already formatted, exit 0.
- `uv run ruff check`: all checks passed, exit 0.
- `uv run pytest` (OOT_ROMFS/OOT_NUP/OOT_DUMP unset, no `-n`):
  2867 passed, 206 skipped in 695.45 seconds, exit 0.
- `uv run pytest -m dump`, with the following environment; its complete result is
  recorded in `E:/OOTRemake/work/r16-nup/dump.log` and the final Bermuda handoff.

```sh
OOT_ROMFS=E:/Games/Hookshot/romfs
OOT_NUP="E:/Games/Hookshot/The Legend of Zelda Ocarina of Time [0400486024DEC000][v131072].nup"
OOT_DUMP=E:/OOTRemake/work/r15-token-impl/final-families-layered-dump
```

All stage logs (exact commands, runtime checks, worker counts, outputs and exits)
are in `E:/OOTRemake/work/r16-nup/{format,lint,synthetic,dump}.log`, outside the
repository. The lock is released immediately after the dump command exits.

At Claude's provenance request, the tracked tree was frozen during the final
dump gate and captured with `git write-tree`; its tree ID is recorded outside the
repository in `E:/OOTRemake/work/r16-nup/gated-tree.txt`. No source/test changes
were made during the gates. Gate evidence documentation was finalized before
this snapshot; later results are recorded externally to keep the tree frozen.
The handoff includes the committed head and the empty diff against this snapshot.

The existing `tests/test_pack_nup_dump.py` oracle is retained: `OOT_NUP` and
`OOT_DUMP` working caches compare byte-for-byte with `OOT_ROMFS`, then cache-only
and full-RomFS generation compare every output path/digest for every resource
mode. It also verifies source size/mtime and temporary-cache removal.

## In-game boundary

No game was started, no save or played seed opened, and nothing was written to
Hookshot or Longshot folders. No in-game check is staged: this is archive input
validation only, not a game-data/runtime transform. Byte/output identity is the
offline acceptance gate; no new in-game claim is made. Kareem's play time needed
for this track: none.
