from pathlib import Path

DOIT_CONFIG = {"backend": "json", "dep_file": "doit-db.json"}

code_files = [Path("pyproject.toml"), Path("uv.lock")] + [
    p for p in Path("memium").rglob("*") if not p.is_dir()
]


# refactor: this duplicates a lot of the functionality in the `tasks.py` file
# Ideally, I would want to remove that, and to change the CI to use pydoit
# However, this is not at all a high priority right now


def github_signoff(name: str) -> str:
    return f'~/Git/dotfiles/scripts/signoff.sh $PWD "{name}"'


def task_smoketest_docker():
    return {"actions": ["inv smoketest-docker"], "file_dep": [*code_files, Path("readme.md")]}


def task_smoketest_cli():
    return {"actions": ["inv smoketest-cli"], "file_dep": [*code_files, Path("readme.md")]}


def task_git_clean():
    return {"actions": ["git status --porcelain"]}


def task_types():
    return {"actions": ["uv run pyright memium"], "file_dep": code_files}


def task_test():
    return {"actions": ["uv run pytest memium"], "file_dep": code_files}


def task_lint():
    return {"actions": ["ruff check memium --fix"], "file_dep": code_files}


def task_validate():
    return {
        "actions": ["git push", github_signoff("local/mergeable")],
        "task_dep": ["lint", "types", "test", "git_clean", "smoketest_docker", "smoketest_cli"],
    }


dockerfiles = list(Path().rglob("**/Dockerfile*"))


def task_image():
    return {
        "actions": ["docker build . -t ghcr.io/martinbernstorff/memium:latest -f Dockerfile"],
        "file_dep": code_files + dockerfiles,
    }


def task_run_image():
    return {
        "actions": ["docker compose -f ~/Git/dotfiles/containers/memium/docker-compose.yml up -d"],
        "task_dep": ["image", "validate"],
        "file_dep": code_files + dockerfiles,
    }
