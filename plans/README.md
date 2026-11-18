# plans/: the maintainers' working notes

You do not need anything here to play a seed or to contribute; start with the repository's `README.md` and
`CONTRIBUTING.md`. This folder is the project's design record and the evidence behind its logic: the data files under
`src/clawshot/data/` cite these notes as the source of a rule.

| File or folder | What it is |
|---|---|
| `00-roadmap.md` | Roadmap index: milestones, standing backlog and one status/link per round; read it plus your round's file |
| `01-architecture.md` | How the generator is put together |
| `02-orchestration.md` | How the maintainers run and review parallel agent rounds |
| `03-game-data.md` | What was learned about the remake's data, numbered by section |
| `04-world-format.md` | The logic data format and the remake's overrides |
| `decisions.md` | Decisions, with who proposed each |
| `playtest/` | In-game questions and the answers from play |
| `rounds/` | `r<N>-overview.md`: round brief and outcome; `r<N>-<track>.md`: each track's implementation, evidence and handoff |

Paths such as `E:\OOTRemake\...` and names in these notes are from the maintainers' machines. Nothing here is
generated from the game: no game files, decoded data or seeds are kept in the repository.
