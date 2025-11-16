from __future__ import annotations
import logging
from typing import Iterable
from app.core.config import settings

logger = logging.getLogger(__name__)


# Pevně daný seznam "tajemných" jmen/slov (case-insensitive)
DEFAULT_SECRET_TOKENS: tuple[str, ...] = (
	"neo",
	"trinity",
	"morpheus",
	"jan",      # příklad českého jména
	"pavla",
	"matrix",
)


def _normalize(value: str | None) -> str:
	return (value or "").strip().lower()


def _get_active_tokens() -> set[str]:
	if settings.SECRET_TOKENS:
		return {t.strip().lower() for t in settings.SECRET_TOKENS.split(",") if t.strip()}
	return {t for t in DEFAULT_SECRET_TOKENS}


def evaluate_text_for_game(text: str, tokens: Iterable[str] | None = None) -> tuple[bool, str | None]:
	"""Vyhodnotí vstupní text vůči seznamu tajných tokenů.

	Vrací (matched, message). Při shodě vrátí pozitivní hlášku, jinak (False, None).
	"""
	cand = _normalize(text)
	effective = tokens if tokens is not None else _get_active_tokens()
	tokenset = {t.strip().lower() for t in effective if t}
	matched = cand in tokenset
	if matched:
		message = f"🎉 Tajemství odhaleno: '{cand}'! Máš oko sokola."
		logger.info("Mini hra: shoda pro text '%s'", cand)
		return True, message
	logger.debug("Mini hra: bez shody pro text '%s'", cand)
	return False, None


def build_easter_egg_from_names(first_name: str, last_name: str) -> tuple[bool, str | None]:
	"""Zkusí shodu pro křestní i příjmení a vrací (easter_egg, message)."""
	for val in (first_name, last_name):
		matched, message = evaluate_text_for_game(val)
		if matched:
			return True, message
	return False, None
