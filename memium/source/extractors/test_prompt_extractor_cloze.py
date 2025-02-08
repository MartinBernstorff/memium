from datetime import datetime
from pathlib import Path

from ..document import Document
from .extractor_cloze import ClozePromptExtractor


def test_cloze_prompt_extractor(tmpdir: Path):
    doc = Document(
        content=r"""

What is the meaning of life? {42}


This is another block without any cloze prompts.

#anki/tag/test_tag

""",
        source_path=tmpdir / "test.md",
        last_modified=datetime.now(),
    )

    extractor = ClozePromptExtractor().extract_prompts(doc)

    assert len(extractor) == 1
    assert extractor[0].text == r"What is the meaning of life? {{c734::42}}"
    assert extractor[0].tags == ["anki/tag/test_tag"]


import pytest


@pytest.mark.parametrize(
    ("content", "skipped"),
    [
        (
            """```html
         {Code block}
         ```""",
            True,
        ),
        ("""<!-- {HTML comment} -->""", True),
        ("""{Cloze}""", False),
        (
            """```html
Some content

Content in another {block}
        ```""",
            True,
        ),
    ],
)
def test_ignore_block_types(content: str, skipped: bool):
    doc = Document.fake(content=content)
    extractor = ClozePromptExtractor().extract_prompts(doc)

    if skipped:
        assert len(extractor) == 0
    else:
        assert len(extractor) == 1
