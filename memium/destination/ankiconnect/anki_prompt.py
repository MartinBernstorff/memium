from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass

import genanki  # type: ignore

from memium.utils.markdown_parser import to_html


@dataclass(frozen=True)
class AnkiPrompt(ABC):
    base_deck: str
    tags: Sequence[str]
    uuid: int  # UUID is a unique identifier for the prompt, used for scheduling. If a new prompt is added with the same uuid, it will be treated as an update to the existing prompt. Otherwise, they will be interpreted as separate prompts.
    edit_url: str | None

    def _to_html(self, field: str) -> str:
        return to_html(field)

    @property
    @abstractmethod
    def genanki_model(self) -> genanki.Model: ...

    @abstractmethod
    def to_genanki_note(self) -> genanki.Note: ...

    @property
    def deck(self) -> str:
        deck_prefix = "anki/deck/"
        deck_in_tags = (
            tag.replace(deck_prefix, "").replace("/", "::")
            for tag in self.tags
            if tag.startswith(deck_prefix)
        )
        subdeck = next(deck_in_tags, None)

        if subdeck is None:
            return self.base_deck

        return f"{self.base_deck}::{subdeck}"
