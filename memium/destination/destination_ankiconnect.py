import logging
import warnings
from collections.abc import Sequence

import genanki  # type: ignore
from iterpy import Iter

from ..source.prompts.prompt import DestinationPrompt
from ..utils.hash_cleaned_str import clean_str, hash_str_to_int
from .ankiconnect.anki_converter import AnkiPromptConverter
from .ankiconnect.anki_prompt import AnkiPrompt
from .ankiconnect.ankiconnect_gateway import AnkiConnectGateway
from .destination import DeletePrompts, PromptDestination, PromptDestinationCommand, PushPrompts

log = logging.getLogger(__name__)


class AnkiConnectDestination(PromptDestination):
    def __init__(self, gateway: AnkiConnectGateway, prompt_converter: AnkiPromptConverter) -> None:
        self.gateway = gateway
        self.prompt_converter = prompt_converter

        # Don't care about genanki warnings, have our own tests
        warnings.filterwarnings(
            "ignore", module="genanki", message="^Field contained the following invalid HTML tags"
        )

    def get_all_prompts(self) -> Sequence[DestinationPrompt]:
        return (
            Iter(self.gateway.get_all_note_infos())
            .map(self.prompt_converter.note_info_to_prompt)
            .to_list()
        )

    def _delete_prompts(self, prompts: Sequence[DestinationPrompt]) -> None:
        prompt_ids = {int(remote_prompt.destination_id) for remote_prompt in prompts}
        self.gateway.delete_notes(list(prompt_ids))

    def _grouped_cards_to_deck(
        self, grouped_cards: tuple[str, Sequence[AnkiPrompt]]
    ) -> genanki.Deck:
        deck_name = grouped_cards[0]
        deck = genanki.Deck(name=deck_name, deck_id=hash_str_to_int(clean_str(deck_name)))

        for card in grouped_cards[1]:
            deck.add_note(card.to_genanki_note())  # type: ignore

        return deck

    def _create_package(self, cards: Sequence[AnkiPrompt]) -> genanki.Package:
        decks = (
            Iter(cards).groupby(lambda card: card.deck).map(self._grouped_cards_to_deck).to_list()
        )

        return genanki.Package(deck_or_decks=decks)

    def _push_prompts(self, command: PushPrompts) -> None:
        cards = [self.prompt_converter.prompt_to_card(e) for e in command.prompts]

        models = [card.genanki_model for card in cards]
        unique_models: dict[int, genanki.Model] = {
            model.model_id: model  # type: ignore
            for model in models  # type: ignore
        }

        for model in unique_models.values():
            self.gateway.update_model(model)

        package = self._create_package(cards)

        log.info(f"Pushing {len(cards)} cards to Anki")
        self.gateway.import_package(package)

    def update(self, commands: Sequence[PromptDestinationCommand]) -> None:
        for command in commands:
            match command:
                case DeletePrompts(prompts):
                    self._delete_prompts(prompts)
                case PushPrompts(prompts):
                    self._push_prompts(command)
