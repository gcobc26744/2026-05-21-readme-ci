from __future__ import annotations

import argparse
import fnmatch
import os
import pathlib
import subprocess
import sys


def _repo_root() -> pathlib.Path:
    # .../projects/YYYY-MM-DD-name/src/readme_ci.py -> repo root
    return pathlib.Path(__file__).resolve().parents[3]


def _posix_relpath(path: pathlib.Path, root: pathlib.Path) -> str:
    try:
        rel = path.resolve().relative_to(root.resolve())
    except Exception:
        rel = path
    return rel.as_posix()


def _matches_any_glob(path: pathlib.Path, root: pathlib.Path, globs: list[str]) -> bool:
    if not globs:
        return False
    rel = _posix_relpath(path, root)
    return any(fnmatch.fnmatch(rel, g) for g in globs)


def _iter_workspace_readmes(
    repo_root: pathlib.Path,
    *,
    exclude_dirs: set[str],
    include_globs: list[str],
    exclude_globs: list[str],
) -> list[pathlib.Path]:
    readmes: list[pathlib.Path] = []

    root_readme = repo_root / "README.md"
    if root_readme.exists():
        if (not include_globs or _matches_any_glob(root_readme, repo_root, include_globs)) and (
            not _matches_any_glob(root_readme, repo_root, exclude_globs)
        ):
            readmes.append(root_readme)

    projects_dir = repo_root / "projects"
    if projects_dir.exists():
        for child in projects_dir.iterdir():
            if not child.is_dir():
                continue
            if child.name in exclude_dirs:
                continue
            readme = child / "README.md"
            if readme.exists():
                if include_globs and not _matches_any_glob(readme, repo_root, include_globs):
                    continue
                if _matches_any_glob(readme, repo_root, exclude_globs):
                    continue
                readmes.append(readme)

    return sorted(set(readmes))


def _iter_all_readmes(
    root: pathlib.Path,
    *,
    exclude_dirs: set[str],
    include_globs: list[str],
    exclude_globs: list[str],
) -> list[pathlib.Path]:
    exclude_dir_parts = set(exclude_dirs) | {
        ".git",
        ".venv",
        "__pycache__",
        ".pytest_cache",
        "node_modules",
        "dist",
        "build",
    }

    readmes: list[pathlib.Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dir_path = pathlib.Path(dirpath)

        # Prune excluded dirs in-place for faster walking.
        dirnames[:] = [d for d in dirnames if d not in exclude_dir_parts]

        if "README.md" in filenames:
            readme = dir_path / "README.md"
            if include_globs and not _matches_any_glob(readme, root, include_globs):
                continue
            if _matches_any_glob(readme, root, exclude_globs):
                continue
            readmes.append(readme)
    return sorted(set(readmes))


def _run_readme_doctor(doctor_py: pathlib.Path, readme: pathlib.Path, strict: bool) -> int:
    cmd = [sys.executable, str(doctor_py)]
    if strict:
        cmd.append("--strict")
    cmd.append(str(readme))

    proc = subprocess.run(cmd, text=True)
    return proc.returncode


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run readme-doctor over README.md files in this workspace."
    )
    parser.add_argument(
        "root",
        nargs="?",
        default=".",
        help="Repo root folder (default: .).",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat missing required sections as CI-fail (exit code 2).",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Scan every README.md under root (includes non-project folders).",
    )
    parser.add_argument(
        "--exclude-dir",
        action="append",
        default=[],
        metavar="NAME",
        help="Skip directories with this name (repeatable).",
    )
    parser.add_argument(
        "--include",
        action="append",
        default=[],
        metavar="GLOB",
        help="Only check README paths matching this glob (repeatable; relative to root).",
    )
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        metavar="GLOB",
        help="Skip README paths matching this glob (repeatable; relative to root).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = pathlib.Path(args.root).expanduser().resolve()

    doctor_py = _repo_root() / "projects/2026-05-14-readme-doctor/src/readme_doctor.py"
    if not doctor_py.exists():
        print(f"readme-doctor not found: {doctor_py}", file=sys.stderr)
        return 2

    exclude_dirs = {d for d in (args.exclude_dir or []) if d}
    include_globs = [g for g in (args.include or []) if g]
    exclude_globs = [g for g in (args.exclude or []) if g]

    if args.all:
        readmes = _iter_all_readmes(
            root,
            exclude_dirs=exclude_dirs,
            include_globs=include_globs,
            exclude_globs=exclude_globs,
        )
    else:
        readmes = _iter_workspace_readmes(
            root,
            exclude_dirs=exclude_dirs,
            include_globs=include_globs,
            exclude_globs=exclude_globs,
        )
    if not readmes:
        print(f"No README.md files found under: {root}")
        return 0

    worst = 0
    for readme in readmes:
        code = _run_readme_doctor(doctor_py, readme, strict=args.strict)
        worst = max(worst, code)

    return worst


if __name__ == "__main__":
    raise SystemExit(main())
