"""Utilities for working with the bundled TMDB movie dataset."""
from __future__ import annotations

import csv
import logging
from functools import lru_cache
from pathlib import Path
from typing import Dict, Optional

_DATASET_FILENAME = "TMDB_movie_dataset_v11.csv"


def _dataset_path() -> Path:
    """Return the path to the bundled TMDB dataset."""
    return Path(__file__).resolve().parents[1] / _DATASET_FILENAME


@lru_cache(maxsize=1)
def _load_dataset() -> Dict[str, Dict[str, str]]:
    """Load the TMDB dataset into memory and cache the results."""
    dataset_path = _dataset_path()
    if not dataset_path.exists():
        logging.warning("TMDB dataset not found at %s", dataset_path)
        return {}

    records: Dict[str, Dict[str, str]] = {}
    try:
        with dataset_path.open("r", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            if reader.fieldnames:
                reader.fieldnames = [field.strip() for field in reader.fieldnames]
            for row in reader:
                imdb_id = (row.get("imdb_id") or "").strip().lower()
                if not imdb_id:
                    continue
                # Normalise values by stripping whitespace while keeping raw strings.
                normalised_row = {key: (value.strip() if isinstance(value, str) else value)
                                  for key, value in row.items()}
                records[imdb_id] = normalised_row
    except Exception as exc:
        logging.error("Failed to load TMDB dataset: %s", exc, exc_info=True)
        return {}

    logging.debug("Loaded %d entries from TMDB dataset", len(records))
    return records


def get_movie_by_imdb(imdb_id: Optional[str]) -> Optional[Dict[str, str]]:
    """Return the dataset row for the provided IMDb ID if available."""
    if not imdb_id:
        return None
    imdb_key = imdb_id.strip().lower()
    if not imdb_key:
        return None
    dataset = _load_dataset()
    return dataset.get(imdb_key)


def clear_dataset_cache() -> None:
    """Clear the cached dataset contents (primarily for tests)."""
    _load_dataset.cache_clear()
