from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from ..prompts.base_prompt import BasePrompt


@dataclass(frozen=True)
class DeletePrompts:
    prompts: Sequence[BasePrompt]


@dataclass(frozen=True)
class PushPrompts:
    prompts: Sequence[BasePrompt]
    tmp_write_dir: Path
    tmp_read_dir: Path


PromptDestinationCommand = DeletePrompts | PushPrompts