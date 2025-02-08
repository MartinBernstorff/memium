from collections.abc import Sequence
from dataclasses import dataclass

from ...utils.hash_cleaned_str import clean_str, hash_str_to_int
from .prompt import BasePrompt
from .prompt_from_doc import PromptFromDocMixin


@dataclass(frozen=True)
class QAPrompt(BasePrompt):
    question: str
    answer: str

    @property
    def scheduling_uid_str(self) -> str:
        """Str used for generating the update_uid. Super helpful for debugging."""
        return f"{clean_str(self.question)}_{clean_str(self.answer)}"

    @property
    def scheduling_uid(self) -> int:
        return hash_str_to_int(self.scheduling_uid_str)

    @property
    def update_uid_str(self) -> str:
        """Str used for generating the update_uid. Super helpful for debugging."""
        return f"{self.question}_{self.answer}_{self.tags}"

    @property
    def update_uid(self) -> int:
        return hash_str_to_int(self.update_uid_str)

    @property
    def tags(self) -> Sequence[str]:
        return ()


@dataclass(frozen=True)
class QAWithoutDoc(QAPrompt):
    add_tags: Sequence[str]

    @property
    def tags(self) -> Sequence[str]:
        return self.add_tags

    @property
    def edit_url(self) -> str | None:
        return None


@dataclass(frozen=True)
class QAFromDoc(QAPrompt, PromptFromDocMixin):
    @property
    def tags(self) -> Sequence[str]:
        return self.parent_doc.tags


@dataclass(frozen=True)
class RephrasedQAFromDoc(QAPrompt, PromptFromDocMixin):
    rephrased_question: str

    @property
    def tags(self) -> Sequence[str]:
        return self.parent_doc.tags
