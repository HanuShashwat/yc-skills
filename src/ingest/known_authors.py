"""
Known authors mapping for OpenYC Skills.
"""

import re
from urllib.parse import urlparse, unquote

KNOWN_AUTHORS: dict[str, tuple[str, str]] = {
    "paul graham": ("Paul Graham", "Founder of YC"),
    "paul-graham": ("Paul Graham", "Founder of YC"),
    "sam altman": ("Sam Altman", "Former President of YC"),
    "sam-altman": ("Sam Altman", "Former President of YC"),
    "michael seibel": ("Michael Seibel", "Partner at YC"),
    "michael-seibel": ("Michael Seibel", "Partner at YC"),
    "garry tan": ("Garry Tan", "CEO of YC"),
    "garry-tan": ("Garry Tan", "CEO of YC"),
    "jessica livingston": ("Jessica Livingston", "Founding Partner of YC"),
    "jessica-livingston": ("Jessica Livingston", "Founding Partner of YC"),
    "dalton caldwell": ("Dalton Caldwell", "Managing Director of YC"),
    "dalton-caldwell": ("Dalton Caldwell", "Managing Director of YC"),
    "kevin hale": ("Kevin Hale", "Partner at YC"),
    "kevin-hale": ("Kevin Hale", "Partner at YC"),
    "gustaf alstromer": ("Gustaf Alstromer", "Partner at YC"),
    "gustaf-alstromer": ("Gustaf Alstromer", "Partner at YC"),
    "anu hariharan": ("Anu Hariharan", "Partner at YC"),
    "anu-hariharan": ("Anu Hariharan", "Partner at YC"),
    "harj taggar": ("Harj Taggar", "Partner at YC"),
    "harj-taggar": ("Harj Taggar", "Partner at YC"),
    "jared friedman": ("Jared Friedman", "Partner at YC"),
    "jared-friedman": ("Jared Friedman", "Partner at YC"),
    "aaron epstein": ("Aaron Epstein", "Partner at YC"),
    "aaron-epstein": ("Aaron Epstein", "Partner at YC"),
    "brad flora": ("Brad Flora", "Partner at YC"),
    "brad-flora": ("Brad Flora", "Partner at YC"),
    "nicolas dessaigne": ("Nicolas Dessaigne", "Partner at YC"),
    "nicolas-dessaigne": ("Nicolas Dessaigne", "Partner at YC"),
    "kat manalac": ("Kat Mañalac", "Partner at YC"),
    "kat-manalac": ("Kat Mañalac", "Partner at YC"),
    "y combinator": ("Y Combinator", "Startup Accelerator"),
    "y-combinator": ("Y Combinator", "Startup Accelerator"),
    "yc": ("Y Combinator", "Startup Accelerator"),
    "pg": ("Paul Graham", "Founder of YC"),
    "sama": ("Sam Altman", "Former President of YC"),
}


def lookup_author(url: str) -> tuple[str | None, str | None]:
    """
    Looks up a known author and their designation from a URL.

    Args:
        url: The URL to check for author information.

    Returns:
        A tuple of (author_name, designation). Both will be None if the author is not found.
    """
    try:
        parsed_url = urlparse(url)
        path = unquote(parsed_url.path).lower()

        # Order keys by length descending to match longest possible names first
        keys_by_length = sorted(KNOWN_AUTHORS.keys(), key=len, reverse=True)

        for key in keys_by_length:
            # Use word boundaries to prevent partial matches like 'pg' in 'page'
            pattern = r"\b" + re.escape(key) + r"\b"
            if re.search(pattern, path):
                return KNOWN_AUTHORS[key]

        return None, None
    except Exception:
        return None, None
