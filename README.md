# readme-ci

## What it is
A tiny Python CLI that finds `README.md` files in this repo and checks them with `readme-doctor`.

## Why it exists
To keep README files consistently structured (and CI-friendly) as you add new daily projects.

## How to run
```bash
python projects/2026-05-21-readme-ci/src/readme_ci.py --strict .
```

### Common options

Skip folders by name (repeatable):

```bash
python projects/2026-05-21-readme-ci/src/readme_ci.py --strict . --exclude-dir automations --exclude-dir tools
```

Only check a subset of README paths (globs are relative to `root`):

```bash
python projects/2026-05-21-readme-ci/src/readme_ci.py --strict . --include "projects/2026-*/README.md"
```

Skip some README paths:

```bash
python projects/2026-05-21-readme-ci/src/readme_ci.py --strict . --exclude "projects/*/docs/**"
```

## Example
Input:
- A repo root `README.md` and `projects/*/README.md`

Output:
- A per-file report, then a non-zero exit code if any README is missing required sections.

## Next steps
- [ ] Add a `--changed-only` mode for PRs.
