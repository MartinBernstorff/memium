import json
from collections.abc import Sequence
from dataclasses import dataclass
from time import sleep

import invoke as inv

from .str_parsing import get_letter_alphabet_position, get_letter_from_alphabet_position


@dataclass(frozen=True)
class GithubIssue:
    number: int
    title: str


def get_issues_assigned_to_me(c: inv.Context) -> Sequence[GithubIssue] | None:
    """Get issues assigned to current user on current repo"""
    my_issues_cmd = c.run("gh issue list --assignee='@me' --json number,title", hide="out")

    if my_issues_cmd is None:
        return None

    parsed_output = [GithubIssue(**value) for value in json.loads(my_issues_cmd.stdout)]
    return parsed_output


def issue_dialog(my_issues: Sequence[GithubIssue]) -> int:
    issue_strings = [
        f"[{get_letter_from_alphabet_position(i + 1)}] #{issue.number} {issue.title}"
        for i, issue in enumerate(my_issues)
    ]

    n_issues = len(my_issues)
    if n_issues == 1:
        print(f"Only one issue found, selecting:\n\t{issue_strings[0]}\nin ")
        for i in range(1 * 10, 0, -1):
            interval = 0.1
            print(f"{round(i * interval, 1)}...")
            sleep(interval)
        return 0

    terminal_output = "\n".join(reversed(issue_strings))
    print(f"\n{terminal_output}\n")

    print(f"Latest [a] is: \n\t {my_issues[0].title}\n")
    print("I found these issues for you. Which do you want to work on?\n")

    issue_index = (
        get_letter_alphabet_position(input(f"[a-{get_letter_from_alphabet_position(n_issues)}]: "))
        - 1
    )

    return issue_index


def sanitise_issue_title(issue_title: str) -> str:
    characters_to_replace = [" ", ":", ",", "'", '"', "(", ")", "[", "]", "`"]

    for character in characters_to_replace:
        issue_title = issue_title.replace(character, "-")

    issue_title = issue_title.replace("--", "-")
    return issue_title
