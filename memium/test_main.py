import logging
from pathlib import Path

import pytest

from memium.core import main

from .destination.ankiconnect.ankiconnect_gateway import anki_connect_is_live


@pytest.mark.skipif(
    not anki_connect_is_live() or not Path("/output").exists(),
    reason="Tests require a running AnkiConnect server and an output directory. Use the Docker container to run the tests.",
)
def test_main(caplog: pytest.LogCaptureFixture, base_deck: str = "Main Integration Test"):
    caplog.set_level(logging.INFO)

    # Clear and delete output path
    test_input_path = Path("/output")

    if test_input_path.exists():
        for entity in test_input_path.iterdir():
            if not entity.is_dir():
                entity.unlink()
    else:
        test_input_path.mkdir(parents=True)

    with (test_input_path / "test.md").open("w") as f:
        f.write(
            """Q. What are [[Trees]]?
A. å
"""
        )

    main(
        base_deck=base_deck,
        input_dir=test_input_path,
        max_deletions_per_run=2,
        dry_run=False,
        push_all=False,
        rephrase_if_younger_than_days=None,
        rephrase_cache_days=None,
        config_dir=Path(),
    )
    assert "Pushing 1 cards to Anki" in caplog.text

    # Test idempotency
    main(
        base_deck=base_deck,
        input_dir=test_input_path,
        max_deletions_per_run=0,  # 0 deletions allowed to test idempotency
        dry_run=False,
        push_all=False,
        rephrase_if_younger_than_days=None,
        rephrase_cache_days=None,
        config_dir=Path(),
    )
