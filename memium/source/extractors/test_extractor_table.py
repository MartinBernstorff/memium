from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import pytest

from memium.source.extractors.test_prompt import FakeQAPrompt

from ..document import Document
from .extractor_table import TableExtractor
from .to_line_blocks import LineBlock, to_line_blocks


@dataclass(frozen=True)
class TableExtractorExample:
    table_prompt: str  # What the example is testing
    expectation: Sequence[FakeQAPrompt]  # Expected prompts


@pytest.mark.parametrize(
    ("example"),
    [
        TableExtractorExample(
            table_prompt="Descending // |Column one|? // |Column two|.",
            expectation=[FakeQAPrompt(question="11?", answer="22.")],
        ),
        TableExtractorExample(
            table_prompt="Ascending // |Column one|? // |Column two|.",
            expectation=[
                FakeQAPrompt(question="21?", answer="12."),
                FakeQAPrompt(question="31?", answer="22."),
            ],
        ),
        TableExtractorExample(
            table_prompt="Rowwise // |Column one|? // |Column two|.",
            expectation=[
                FakeQAPrompt(question="11?", answer="12."),
                FakeQAPrompt(question="21?", answer="22."),
            ],
        ),
    ],
    ids=lambda x: x.table_prompt,
)
def test_table_extractor(example: TableExtractorExample):
    input_doc = Document(
        content=f"""
    Block one

| Column one | Column two |
| --- | --- |
| 11 | 12 |
| 21 | 22 |
| 31 |      |
{example.table_prompt}""",
        source_path=Path(__file__),
        last_modified=datetime.now(),
    )

    assert {
        example.to_qa_from_doc(doc=input_doc, line_nr=len(input_doc.content.split("\n")) - 1)
        for example in example.expectation
    } == set(TableExtractor().extract_prompts(input_doc))


def test_line_block_extractor():
    document = """Block 1

Block 2
With multiline"""
    assert to_line_blocks(document) == [
        LineBlock(starting_line=0, lines=["Block 1"]),
        LineBlock(starting_line=2, lines=["Block 2", "With multiline"]),
    ]
