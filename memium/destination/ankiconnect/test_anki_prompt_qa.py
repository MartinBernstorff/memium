from collections.abc import Sequence
from dataclasses import dataclass, field

import genanki  # type: ignore

from .anki_prompt_cloze import AnkiCloze
from .anki_prompt_qa import AnkiQA


def fake_tag_factory() -> Sequence[str]:
    return ["FakeTag"]


@dataclass(frozen=True)
class FakeAnkiCloze(AnkiCloze):
    text: str = "FakeText"
    base_deck: str = "FakeBaseDeck"
    tags: Sequence[str] = field(default_factory=fake_tag_factory)
    css: str = "FakeCSS"
    uuid: int = 0
    edit_url: str = "FakeEditURL"


@dataclass(frozen=True)
class FakeAnkiQA(AnkiQA):
    base_deck: str = "FakeBaseDeck"
    tags: Sequence[str] = field(default_factory=fake_tag_factory)
    question: str = "FakeQuestion"
    answer: str = "FakeAnswer"
    css: str = "FakeCSS"
    uuid: int = 0
    edit_url: str = "FakeEditURL"


from dataclasses import dataclass

import pytest


@dataclass(frozen=True)
class QAExample:
    card: AnkiQA
    deck: str


@pytest.mark.parametrize(
    ("example"),
    [
        QAExample(FakeAnkiQA(tags=["anki/deck/Subdeck"]), "FakeBaseDeck::Subdeck"),
        QAExample(
            FakeAnkiQA(tags=["anki/deck/Subdeck"], question="What are _Wikilinks_ on _Wikipedia_?"),
            "FakeBaseDeck::Subdeck::Wikilinks-Wikipedia",
        ),
        QAExample(
            FakeAnkiQA(question="On _Wikipedia_, what are _Wikilinks_?"),
            "FakeBaseDeck::Wikilinks-Wikipedia",
        ),
        QAExample(FakeAnkiQA(question="Without wikilinks?"), "FakeBaseDeck"),
    ],
)
def test_ankiqa_deck_inference(example: QAExample):
    assert example.card.deck == example.deck


def test_formatting(snapshot: genanki.Note):
    card = FakeAnkiQA(question="Q. This is a _question_?")
    note = card.to_genanki_note()
    assert snapshot == note.fields  # type: ignore
