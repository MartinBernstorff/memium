import importlib.metadata
import logging
import sys
import time
from datetime import datetime
from functools import partial
from pathlib import Path
from typing import Annotated, Optional

import typer

from memium.core import main

log = logging.getLogger(__name__)

app = typer.Typer()


@app.command()
def cli(
    input_dir: Annotated[
        Path,
        typer.Option(
            help="Where to extract prompts from.",
            dir_okay=True,
            file_okay=False,
            exists=True,
            readable=True,
            writable=True,
        ),
    ],
    watch_seconds: Annotated[
        Optional[int],  # noqa: UP007
        typer.Option(help="Keep running, updating Anki deck every [ARG] seconds"),
    ] = None,
    deck_name: Annotated[
        str, typer.Option(help="Anki path to deck, e.g. 'Parent deck::Child deck'")
    ] = "Memium",
    max_deletions_per_run: Annotated[
        int,
        typer.Option(
            help="Maximum number of cards to delete per sync to avoid unintentional deletions. If exceeded, raises error."
        ),
    ] = 50,
    push_all: Annotated[
        bool,
        typer.Option(
            help="Push all prompts to Anki, not just the diff. Useful if you have e.g. changed your CSS template. Note that this does not change scheduling, nor delete prompts that no longer exist in your markdown."
        ),
    ] = False,
    dry_run: Annotated[
        bool, typer.Option(help="Don't update via AnkiConnect, just log what would happen")
    ] = False,
    skip_sync: Annotated[
        bool, typer.Option(help="Skip all syncing, useful for smoketesting of the interface")
    ] = False,
    rephrase_if_younger_than_days: Annotated[
        int | None,
        typer.Option(
            help="Rephrase prompts whose documents have been modified within the last N days."
        ),
    ] = None,
    rephrase_cache_days: Annotated[
        int | None, typer.Option(help="Cache the rephrased prompts for N days.")
    ] = None,
):
    rephrase_is_none = [rephrase_if_younger_than_days is None, rephrase_cache_days is None]
    if not all(rephrase_is_none) and any(rephrase_is_none):
        raise ValueError(
            "Both rephrase_cache_days and rephrase_if_younger_than_days must be set or unset"
        )

    start_time = datetime.now()
    config_dir = input_dir / ".memium"
    config_dir.mkdir(exist_ok=True)

    logging.basicConfig(
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(config_dir / "memium.log"),
        ],
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y/%m/%d %H:%M:%S",
    )

    log.info(f"Starting Memium version {importlib.metadata.version('memium')}")

    if skip_sync:
        log.info("Skipping sync")
        return

    main_fn = partial(
        main,
        base_deck=deck_name,
        input_dir=input_dir,
        max_deletions_per_run=max_deletions_per_run,
        dry_run=dry_run,
        push_all=push_all,
        rephrase_if_younger_than_days=rephrase_if_younger_than_days,
        rephrase_cache_days=rephrase_cache_days,
        config_dir=config_dir,
    )
    main_fn()

    if watch_seconds:
        log.info(
            f"Sync complete in {round((datetime.now() - start_time).total_seconds(), 0)} seconds, sleeping for {watch_seconds} seconds"
        )
        time.sleep(watch_seconds)
        main_fn()


if __name__ == "__main__":
    app()
