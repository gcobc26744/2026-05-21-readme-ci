# readme-ci

## What it is
A tiny Python CLI that finds `README.md` files in this repo and checks them with `readme-doctor`.

## Why it exists
To keep README files consistently structured (and CI-friendly) as you add new daily projects.

## How to run
```bash
python projects/2026-05-21-readme-ci/src/readme_ci.py --strict .
```

## Example
Input:
- A repo root `README.md` and `projects/*/README.md`

Output:
- A per-file report, then a non-zero exit code if any README is missing required sections.

## Next steps
- [ ] Add `--all` filters to skip specific folders by name.
- [ ] Add `--include/--exclude` globs (beyond directory skipping).
- [ ] Add a `--changed-only` mode for PRs.
