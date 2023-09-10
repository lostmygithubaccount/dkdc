import requests

from html2text import html2text

from dkdc.tools import tool
from dkdc.bots.summarize.models import Summary
from dkdc.bots.summarize.functions import *


@tool
def url_to_str(url: str = "https://dkdc.dev") -> str:
    """Reads a webpage via URL into a string."""
    response = requests.get(url)
    text = html2text(response.text)
    return text


@tool
def summarize_text(text: str) -> Summary:
    """Summarizes a text."""
    return Summary(text)
