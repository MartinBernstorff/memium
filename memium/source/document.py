import datetime
import re
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Document:
    content: str
    source_path: Path
    last_modified: datetime.datetime

    @property
    def tags(self) -> Sequence[str]:
        tag_strings: list[str] = list(re.findall(r"#[\w\/]+", self.content))
        return [tag_string.replace("#", "") for tag_string in tag_strings]

    @property
    def title(self) -> str:
        return self.source_path.stem

    def __repr__(self) -> str:
        return f"{self.title}: {self.content[0:10]}..."

    @classmethod
    def fake(
        cls: type["Document"],
        content: str = "Fake content with #fake/tag",
        source_path: Path = Path("/fake/document.txt"),
        last_modified: datetime.datetime = datetime.datetime.now(),  # noqa: B008
    ) -> "Document":
        return cls(content=content, source_path=source_path, last_modified=last_modified)
