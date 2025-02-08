# helper for creating anki connect requests
import datetime
import json
import logging
import traceback
import urllib.request
from collections.abc import Iterator, Mapping, Sequence
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from time import sleep
from typing import Any

from memium.environment import in_docker

log = logging.getLogger(__name__)

import genanki  # type: ignore
import pydantic

log = logging.getLogger(__name__)

import shutil
from contextlib import contextmanager


@contextmanager
def tempdir(tmp_path: Path) -> Iterator[Path]:
    """Context manager for a temporary directory that is deleted after use."""
    try:
        tmp_path.mkdir(parents=True, exist_ok=True)
        yield tmp_path
    except:
        # If there's an error, ensure the directory is deleted before the error is propagated.
        shutil.rmtree(str(tmp_path))
        raise
    else:
        shutil.rmtree(str(tmp_path))


class AnkiField(pydantic.BaseModel):
    value: str
    order: int


class NoteInfo(pydantic.BaseModel):
    noteId: int
    tags: Sequence[str]
    fields: Mapping[str, AnkiField]
    modelName: str
    cards: Sequence[int]


class AnkiConnectCommand(Enum):
    CARDS_TO_NOTES = "cardsToNotes"
    DELETE_NOTES = "deleteNotes"
    FIND_CARDS = "findCards"
    GET_NOTE_INFOS = "notesInfo"
    IMPORT_PACKAGE = "importPackage"

    # Models
    CREATE_MODEL = "createModel"
    UPDATE_MODEL_TEMPLATES = "updateModelTemplates"
    UPDATE_MODEL_STYLING = "updateModelStyling"
    GET_MODEL_NAMES = "modelNames"


@dataclass(frozen=True)
class AnkiConnectGateway:
    ankiconnect_url: str
    base_deck: str
    tmp_read_dir: Path
    tmp_write_dir: Path
    max_deletions_per_run: int
    max_wait_seconds: int

    def __post_init__(self) -> None:
        seconds_waited = 0
        while not anki_connect_is_live(ankiconnect_url=self.ankiconnect_url):
            if seconds_waited >= self.max_wait_seconds:
                raise ConnectionError(f"Could not connect to AnkiConnect at {self.ankiconnect_url}")

            poll_seconds = 10
            log.info(f"AnkiConnect is not live, waiting {poll_seconds} seconds...")
            seconds_waited += poll_seconds
            sleep(poll_seconds)

    def update_model(self, model: genanki.Model) -> None:
        existing_model_names = self._invoke(AnkiConnectCommand.GET_MODEL_NAMES)

        if model.name in existing_model_names:  # type: ignore
            self._invoke(
                AnkiConnectCommand.UPDATE_MODEL_TEMPLATES,
                model={
                    "name": model.name,  # type: ignore
                    "templates": {
                        t["name"]: {"qfmt": t["qfmt"], "afmt": t["afmt"]}
                        for t in model.templates  # type: ignore
                    },
                },
            )
            self._invoke(
                AnkiConnectCommand.UPDATE_MODEL_STYLING,
                model={"name": model.name, "css": model.css},  # type: ignore
            )
        else:
            self._invoke(
                AnkiConnectCommand.CREATE_MODEL,
                modelName=model.name,  # type: ignore
                inOrderFields=[field["name"] for field in model.fields],  # type: ignore
                css=model.css,  # type: ignore
                cardTemplates=[
                    {"Name": t["name"], "Front": t["qfmt"], "Back": t["afmt"]}
                    for t in model.templates  # type: ignore
                ],
            )

    def import_package(self, package: genanki.Package) -> None:
        subdir = "tmp_apkg_dir"
        with tempdir(self.tmp_write_dir / subdir) as tmp_write_subdir:
            apkg_name = f"{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.apkg"
            package.write_to_file(tmp_write_subdir / apkg_name)  # type: ignore

            read_path = self.tmp_read_dir / subdir / apkg_name
            try:
                self._invoke(AnkiConnectCommand.IMPORT_PACKAGE, path=str(read_path))
                log.info(f"Imported from {read_path}!")
            except Exception as e:
                log.error(f"""Unable to sync from {read_path}, {e}""")
                traceback.print_exc()

    def delete_notes(self, note_ids: Sequence[int]) -> None:
        if len(note_ids) > self.max_deletions_per_run:
            raise ValueError(
                f"""{len(note_ids)} are scheduled for deletion,
                which is more than the allowed of {self.max_deletions_per_run}.

                Change the option for the AnkiConnectGateway if you wish to proceed.
                """
            )

        self._invoke(AnkiConnectCommand.DELETE_NOTES, notes=note_ids)

    def get_all_note_infos(self) -> Sequence[NoteInfo]:
        anki_card_ids: list[int] = self._invoke(
            AnkiConnectCommand.FIND_CARDS, query=f'"deck:{self.base_deck}"'
        )

        # get a list of anki notes in the deck
        anki_note_ids: list[int] = self._invoke(
            AnkiConnectCommand.CARDS_TO_NOTES, cards=anki_card_ids
        )

        # get the note info for the notes in the deck
        anki_notes_info: list[dict[str, Any]] = self._invoke(
            AnkiConnectCommand.GET_NOTE_INFOS, notes=anki_note_ids
        )

        return [NoteInfo(**info) for info in anki_notes_info]

    def _request(self, action: Any, **params: Any) -> dict[str, Any]:
        return {"action": action, "params": params, "version": 6}

    def _invoke(self, action: AnkiConnectCommand, **params: Any) -> Any:
        """Helper for invoking actions with anki-connect
        Args:
            action (string): the action to invoke
        Raises:
            Exception: invalid fields provided
        Returns:
            Any: the response from anki connect
        """
        requestJson = json.dumps(self._request(action.value, **params)).encode("utf-8")
        response = json.load(
            urllib.request.urlopen(urllib.request.Request(self.ankiconnect_url, requestJson))
        )
        if len(response) != 2:
            raise Exception("response has an unexpected number of fields")
        if response["error"] is not None:
            raise Exception(response["error"])
        return response["result"]


@dataclass(frozen=True)
class FakeAnkiCommand: ...


@dataclass(frozen=True)
class ImportPackage(FakeAnkiCommand):
    package: genanki.Package


@dataclass(frozen=True)
class UpdateModel(FakeAnkiCommand):
    model: genanki.Model


class SpieAnkiconnectGateway(AnkiConnectGateway):
    def __init__(self, note_infos: Sequence[NoteInfo] = ()) -> None:
        self.deck_name = "FakeDeck"
        self.note_infos: list[NoteInfo] = list(note_infos)
        self.executed_commands: list[FakeAnkiCommand] = []

    def update_model(self, model: genanki.Model) -> None:
        self.executed_commands.append(UpdateModel(model=model))

    def get_all_note_infos(self) -> Sequence[NoteInfo]:
        return self.note_infos

    def import_package(self, package: genanki.Package) -> None:
        self.executed_commands.append(ImportPackage(package=package))


ANKICONNECT_URL = "http://host.docker.internal:8765" if in_docker() else "http://localhost:8765"
# On host machine, port is 8765


def anki_connect_is_live(ankiconnect_url: str = ANKICONNECT_URL) -> bool:
    try:
        if urllib.request.urlopen(ankiconnect_url).getcode() == 200:
            return True
        raise Exception
    except Exception as err:
        log.info(f"Attempted connection on {ankiconnect_url}")
        log.info(
            "Unable to reach anki connect. Make sure anki is running and the Anki Connect addon is installed."
        )
        log.error(f"Error was {err}")

    return False
