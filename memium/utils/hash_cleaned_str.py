import hashlib
import re

import unidecode
from bs4 import BeautifulSoup


def replace_whitespace(text: str) -> str:
    return "_".join(text.split())


def remove_non_content_html_tags(text: str) -> str:
    """Remove non-content html tags from a string."""
    soup = BeautifulSoup(text, "html.parser")

    for img in soup.find_all("img"):
        if img.get("src"):  # type: ignore
            img.replace_with(img["src"])  # type: ignore
        else:
            img.delete()  # type: ignore

    return soup.text


def remove_punctuation(text: str) -> str:
    """Clean string before hashing, so changes to spacing, punctuation, newlines etc. do not affect the hash."""
    lowered = text.lower()

    punctuation = r"""!"#$%&'()*+,-./:;<=>?@[\]^_`|~"""
    cleaned = lowered.translate(str.maketrans("", "", punctuation))

    return cleaned


def remove_markdown_links(text: str) -> str:
    """Get the text from markdown links, e.g. '[link text](link url)' -> 'link text'"""
    return re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)


def decode_unicode(text: str) -> str:
    """Standardise accents in a string."""
    return unidecode.unidecode(text)


def remove_list_markup(text: str) -> str:
    """Remove markdown list markup, including '1. Item', '*' and '-'."""
    without_list_numbers = re.sub(r"^\s*\d+\. ", "", text, flags=re.MULTILINE)
    without_bullets = re.sub(r"^\s\* ", "", without_list_numbers, flags=re.MULTILINE)
    without_dashes = re.sub(r"^\s- ", "", without_bullets, flags=re.MULTILINE)
    return without_dashes


def clean_str(input_str: str) -> str:
    """Clean string before hashing, so changes to spacing, punctuation, newlines etc. do not affect the hash."""
    cleaned = input_str

    for cleaner in [
        remove_non_content_html_tags,
        remove_markdown_links,
        remove_list_markup,
        remove_punctuation,
        decode_unicode,
        replace_whitespace,
    ]:
        cleaned = cleaner(cleaned)

    return cleaned


def hash_str_to_int(input_string: str, max_length: int = 10) -> int:
    # Convert the string to bytes
    bytes_string = input_string.encode()

    # Create a SHA256 hash object
    hash_object = hashlib.sha256(bytes_string)

    # Hex digest the hash and convert it to an integer
    unique_int = int(hash_object.hexdigest(), 16)
    shortened = unique_int % 10**max_length

    return shortened
