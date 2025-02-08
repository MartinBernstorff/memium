import os
from unittest.mock import patch

import pytest

from memium.source.transformers import question_rephraser  # type: ignore

from .question_rephraser import _rephrase_question, get_ttl_hash  # type: ignore


@pytest.mark.skipif(
    not os.getenv("ANTHROPIC_API_KEY"), reason="ANTHROPIC_API_KEY environment variable is not set"
)
@pytest.mark.parametrize(
    ("question", "answer", "note_title"),
    [
        (
            "What is the term for unhelpful _Thinking_ with negative affect?",
            "Rumination",
            "Thinking",
        ),
        (
            "What programming language is _Python_?",
            "Python is a high-level programming language",
            "Python",
        ),
        (
            "If a _Kubernetes Job_ fails to start up a job, what can you find in _K9s_?",
            "The job resource exists as a failure, the pod does not.",
            "Kubernetes",
        ),
    ],
)
def test_rephrase_question(question: str, answer: str, note_title: str):
    result = _rephrase_question(
        question=question,
        answer=answer,
        note_title=note_title,
        ttl="ttl-hash",
        prompt=question_rephraser.PROMPT,
        version="1.0",
    )

    assert len(result) > 0
    assert result.endswith("?")
    assert result != question


def test_get_ttl_hash():
    with patch("time.time") as mock_time:
        # Test same hash within time window
        mock_time.return_value = 0
        hash1 = get_ttl_hash(60)

        mock_time.return_value = 59
        hash2 = get_ttl_hash(60)
        assert hash1 == hash2  # Should return same hash within 60 seconds

        # Test different hash across time window
        mock_time.return_value = 60
        hash3 = get_ttl_hash(60)
        assert hash1 != hash3  # Should return different hash after 60 seconds
