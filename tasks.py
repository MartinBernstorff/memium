import invoke as inv

from memium.tasks.github import get_issues_assigned_to_me, issue_dialog
from memium.tasks.graphite import (
    create_branch_from_issue,
    submit_pr,  # noqa: F401 # type: ignore
)
from memium.tasks.smoketest import (
    smoketest_cli,  # noqa: F401 # type: ignore
    smoketest_docker,  # noqa: F401 # type: ignore
)

PYTEST_CMD = "pytest --testmon --durations=5 --cov=memium memium --cov-report xml:.coverage.xml --cov-report lcov:.coverage.lcov"


@inv.task  # type: ignore
def install_dev(c: inv.Context):
    print("--- Installing development dependencies ---")
    c.run("pip install --upgrade .[dev]")
    print("✅✅✅ Development dependencies installed ✅✅✅")


@inv.task  # type: ignore
def install_test(c: inv.Context):
    print("--- Installing development dependencies ---")
    c.run("pip install --upgrade .[dev,tests]")
    print("✅✅✅ Development dependencies installed ✅✅✅")


@inv.task  # type: ignore
def install(c: inv.Context):
    print("--- Installing dependencies ---")
    c.run("pip install --upgrade .")
    print("✅✅✅ Installed package ✅✅✅")


@inv.task  # type: ignore
def generate_coverage(c: inv.Context):
    c.run(PYTEST_CMD)


@inv.task  # type: ignore
def test(c: inv.Context):
    print("--- Testing ---")
    generate_coverage(c)

    coverage_report = c.run("diff-cover .coverage.xml", hide=True)
    if coverage_report is None:
        print("No coverage report generated")
        return

    lines = coverage_report.stdout.split("\n")
    try:
        coverage_line = next(line for line in lines if "Coverage: " in line)
    except StopIteration:
        print("No lines affected by coverage")
        return

    missing_lines = [line for line in lines if "Missing lines" in line]
    coverage_percent = int(coverage_line.split(" ")[1][:-1])

    if coverage_percent < 80:
        print("\n=== Lines with missing coverage ===")
        for line in missing_lines:
            print(line)

    print("✅✅✅ Tests passed ✅✅✅")


@inv.task  # type: ignore
def lint(c: inv.Context):
    print("--- Linting ---")
    c.run("ruff format .")
    c.run("ruff check memium --fix --extend-select F401 --extend-select F841")
    print("✅✅✅ Lint ✅✅✅")


@inv.task  # type: ignore
def types(c: inv.Context):
    print("--- Type-checking ---")
    c.run("pyright memium")
    print("✅✅✅ Types ✅✅✅")


@inv.task(aliases=("next",))  # type: ignore
def branch_from_next_issue(c: inv.Context):
    my_issues = get_issues_assigned_to_me(c)

    if not my_issues:
        print("No issues found")
        return

    selected_issue_index = issue_dialog(my_issues)
    create_branch_from_issue(c=c, selected_issue=my_issues[selected_issue_index])


@inv.task  # type: ignore
def validate_ci(c: inv.Context):
    print("--- Validating CI ---")
    lint(c)
    types(c)
    generate_coverage(c)
    print("✅✅✅ CI valid ✅✅✅")


@inv.task(aliases=("new",))  # type: ignore
def new_branch_from_issue(c: inv.Context):
    my_issues = get_issues_assigned_to_me(c)

    if not my_issues:
        print("No issues assigned to you found")
        return

    selected_issue_index = issue_dialog(my_issues)
    c.run("git checkout main")
    c.run("git pull")
    create_branch_from_issue(c=c, selected_issue=my_issues[selected_issue_index])
