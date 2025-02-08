from collections.abc import Mapping

import pytest

from ..source.prompts.prompt_cloze import ClozeWithoutDoc
from ..source.prompts.prompt_qa import QAWithoutDoc
from .ankiconnect.anki_converter import AnkiPromptConverter
from .ankiconnect.ankiconnect_gateway import (
    AnkiField,
    FakeAnkiCommand,
    ImportPackage,
    SpieAnkiconnectGateway,
    UpdateModel,
)
from .ankiconnect.test_ankiconnect_gateway import MockNoteInfo
from .destination import PushPrompts
from .destination_ankiconnect import AnkiConnectDestination


@pytest.mark.parametrize(
    ("fields"),
    [
        ({"Text": AnkiField(value="MockText", order=0)}),
        (
            {
                "Question": AnkiField(value="MockQuestion", order=0),
                "Answer": AnkiField(value="MockAnswer", order=1),
            }
        ),
        pytest.param(
            ({"UnknownField": AnkiField(value="MockText", order=0)}), marks=pytest.mark.xfail
        ),
    ],
)
def test_ankiconnect_get_all_prompts(fields: Mapping[str, AnkiField]):
    dest = AnkiConnectDestination(
        gateway=SpieAnkiconnectGateway(note_infos=[MockNoteInfo(fields=fields)]),
        prompt_converter=AnkiPromptConverter(base_deck="FakeDeck", card_css="FakeCSS"),
    )
    prompts = dest.get_all_prompts()

    assert len(prompts) == 1


def test_ankiconnect_push_prompts():
    gateway = SpieAnkiconnectGateway()
    dest = AnkiConnectDestination(
        gateway=gateway,
        prompt_converter=AnkiPromptConverter(base_deck="FakeDeck", card_css="FakeCSS"),
    )
    dest.update(
        [
            PushPrompts(
                prompts=[
                    QAWithoutDoc(
                        question="FakeQuestion",
                        answer="FakeAnswer",
                        add_tags=["anki/deck/FakeSubdeck/FakeSubSubdeck"],
                    ),
                    ClozeWithoutDoc(text="FakeText", add_tags=["FakeTag"]),
                ]
            )
        ]
    )

    expected_commands: list[tuple[type[FakeAnkiCommand], int]] = [
        (ImportPackage, 1),
        (UpdateModel, 2),
    ]
    import_package_command = next(
        c for c in gateway.executed_commands if isinstance(c, ImportPackage)
    )
    assert (
        import_package_command.package.decks[0].name  # type: ignore
        == "FakeDeck::FakeSubdeck::FakeSubSubdeck"
    )
    assert len(import_package_command.package.decks) == 2  # type: ignore

    for command in expected_commands:
        assert (
            len([c for c in gateway.executed_commands if isinstance(c, command[0])]) == command[1]
        )
