import pytest
from app.services.form_data import evaluate_text_for_game, build_easter_egg_from_names


def test_evaluate_text_for_game_match():
    matched, message = evaluate_text_for_game("Neo")
    assert matched is True
    assert message and "Tajemství" in message


def test_evaluate_text_for_game_no_match():
    matched, message = evaluate_text_for_game("random")
    assert matched is False
    assert message is None


def test_build_easter_egg_from_names_first_name():
    egg, msg = build_easter_egg_from_names("Jan", "Nepasuje")
    assert egg is True
    assert msg is not None


def test_build_easter_egg_from_names_last_name():
    egg, msg = build_easter_egg_from_names("Nepasuje", "Trinity")
    assert egg is True
    assert msg is not None
