"""Tests for SoupReplacer, which renames tags during parsing."""

import pytest

from bs4 import BeautifulSoup, SoupReplacer, SoupStrainer

HTML = "<p>one <b>bold <i>and italic</i></b> two <b class='x'>again</b></p><a>link</a>"


@pytest.mark.parametrize("parser", ["html.parser", "lxml"])
def test_replaces_og_tag_with_alt_tag(parser):
    replacer = SoupReplacer("b", "blockquote")
    soup = BeautifulSoup(HTML, parser, replacer=replacer)

    assert soup.find("b") is None
    quotes = soup.find_all("blockquote")
    assert len(quotes) == 2
    # Contents, nesting and attributes survive the rename.
    assert quotes[0].find("i").string == "and italic"
    assert quotes[1]["class"] == ["x"]
    assert "</b>" not in str(soup)
    assert "</blockquote>" in str(soup)


def test_other_tags_unchanged_and_default_is_noop():
    plain = BeautifulSoup(HTML, "html.parser")
    untouched = BeautifulSoup(HTML, "html.parser", replacer=SoupReplacer("u", "em"))
    assert str(untouched) == str(plain)

    combined = BeautifulSoup(
        HTML,
        "html.parser",
        parse_only=SoupStrainer("b"),
        replacer=SoupReplacer("b", "blockquote"),
    )
    assert [t.name for t in combined.find_all(True)] == ["blockquote", "i", "blockquote"]


@pytest.mark.parametrize("parser", ["html.parser", "lxml"])
def test_adds_or_replaces_attributes(parser):
    html = "<p>one</p><p class='old' id='keep'>two</p><div>three</div>"
    replacer = SoupReplacer("p", attrs={"class": "test"})
    soup = BeautifulSoup(html, parser, replacer=replacer)

    paragraphs = soup.find_all("p")
    assert [p["class"] for p in paragraphs] == [["test"], ["test"]]
    # Existing attributes survive, and other tags are untouched.
    assert paragraphs[1]["id"] == "keep"
    assert soup.find("div").attrs == {}
