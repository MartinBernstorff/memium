from collections.abc import Mapping, Sequence
from pathlib import Path

import genanki  # type: ignore
import pytest

from ...environment import get_host_home_dir
from .ankiconnect_gateway import (
    ANKICONNECT_URL,
    AnkiConnectGateway,
    AnkiField,
    NoteInfo,
    anki_connect_is_live,
)


class MockNoteInfo(NoteInfo):
    noteId: int = 1
    tags: Sequence[str] = ["MockTag"]
    fields: Mapping[str, AnkiField] = {"Text": AnkiField(value="MockText", order=0)}
    modelName: str = "MockModel"
    cards: Sequence[int] = [1]


@pytest.mark.skipif(
    not anki_connect_is_live() or not Path("/output").exists(),
    reason="Tests require a running AnkiConnect server and an output directory. Use the Docker container to run the tests.",
)
class TestAnkiConnectGateway:
    output_path = Path("/output")

    def test_import_get_delete_happy_path(self):
        # Delete all .apkg in the output directory
        for f in self.output_path.glob("*.apkg"):
            f.unlink()

        deck = genanki.Deck(deck_id=1, name="Test deck")
        model = genanki.Model(
            model_id=1,
            name="Test model",
            fields=[{"name": "Question"}, {"name": "Answer"}],
            templates=[
                {
                    "name": "Card 1",
                    "qfmt": "{{Question}}",
                    "afmt": "{{FrontSide}}<hr id=answer>{{Answer}}",
                }
            ],
        )

        deck.add_model(model)  # type: ignore
        deck.add_note(  # type: ignore
            genanki.Note(
                model=model, fields=["Capital of Argentina", "Buenos Aires"], tags=["TestTag"]
            )
        )

        tmp_read_dir = get_host_home_dir() / "ankidecks"
        gateway = AnkiConnectGateway(
            ankiconnect_url=ANKICONNECT_URL,
            base_deck="Test deck",
            tmp_read_dir=tmp_read_dir,
            tmp_write_dir=self.output_path,
            max_deletions_per_run=1,
            max_wait_seconds=0,
        )

        # Phase 1: Importing
        package = genanki.Package(deck_or_decks=deck)
        gateway.import_package(package=package)
        assert self.output_path.is_dir()
        assert len(list(Path("/output").glob("*.apkg"))) == 0

        # Phase 2: Getting
        all_notes = gateway.get_all_note_infos()
        note = all_notes[0]
        assert note.tags == ["TestTag"]

        # Phase 3: Deleting
        gateway.delete_notes(note_ids=[n.noteId for n in all_notes])
        assert len(gateway.get_all_note_infos()) == 0

    def test_error_if_deleting_more_than_allowed(self):
        gateway = AnkiConnectGateway(
            ankiconnect_url=ANKICONNECT_URL,
            base_deck="Test deck",
            tmp_read_dir=Path("/tmp"),
            tmp_write_dir=Path("/tmp"),
            max_deletions_per_run=0,
            max_wait_seconds=0,
        )
        with pytest.raises(ValueError, match="are scheduled for deletion"):
            gateway.delete_notes(note_ids=[1])


def test_error_if_not_running():
    with pytest.raises(ConnectionError, match="Could not connect to Anki"):
        AnkiConnectGateway(
            ankiconnect_url="http://localhost:1234",
            base_deck="Test deck",
            tmp_read_dir=Path("/tmp"),
            tmp_write_dir=Path("/tmp"),
            max_deletions_per_run=0,
            max_wait_seconds=0,
        )
