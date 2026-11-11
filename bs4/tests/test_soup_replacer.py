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


# Milestone 3: transformer functions.

XFORM_HTML = (
    "<p class='a b'>one <b>bold <i>it</i></b> <b id='x'>again</b></p>"
    "<div class='c'>two<br/></div>"
)


@pytest.mark.parametrize("parser", ["html.parser", "lxml"])
def test_name_xformer_renames_tags(parser):
    replacer = SoupReplacer(
        name_xformer=lambda tag: "blockquote" if tag.name == "b" else tag.name
    )
    soup = BeautifulSoup(XFORM_HTML, parser, replacer=replacer)

    assert soup.find("b") is None
    quotes = soup.find_all("blockquote")
    assert len(quotes) == 2
    assert quotes[0].find("i").string == "it"
    assert quotes[1]["id"] == "x"
    assert "</b>" not in str(soup)
    assert soup.find("p")["class"] == ["a", "b"]


@pytest.mark.parametrize("parser", ["html.parser", "lxml"])
def test_attrs_xformer_replaces_attributes(parser):
    def add_data_name(tag):
        return {**tag.attrs, "data-name": tag.name}

    soup = BeautifulSoup(
        XFORM_HTML, parser, replacer=SoupReplacer(attrs_xformer=add_data_name)
    )

    assert soup.find("i")["data-name"] == "i"
    assert soup.find("div")["data-name"] == "div"
    # Existing attributes are kept, and list-valued ones are still lists.
    assert soup.find("p")["class"] == ["a", "b"]
    assert soup.find("p")["data-name"] == "p"


@pytest.mark.parametrize("parser", ["html.parser", "lxml"])
def test_xformer_can_modify_tag_in_place(parser):
    def remove_class_attr(tag):
        if "class" in tag.attrs:
            del tag.attrs["class"]

    soup = BeautifulSoup(
        XFORM_HTML, parser, replacer=SoupReplacer(xformer=remove_class_attr)
    )

    assert not soup.find_all(class_=True)
    assert soup.find("b", id="x") is not None
    assert "class" not in str(soup)


def test_xformer_runs_after_name_and_attrs_xformers():
    seen = []

    def spy(tag):
        seen.append((tag.name, dict(tag.attrs)))
        tag.attrs["seen"] = "yes"

    replacer = SoupReplacer(
        name_xformer=lambda tag: tag.name.upper(),
        attrs_xformer=lambda tag: {"n": tag.name},
        xformer=spy,
    )
    soup = BeautifulSoup("<a href='u'>x</a>", "html.parser", replacer=replacer)

    # name_xformer and attrs_xformer both saw the tag as parsed ("a"),
    # and xformer saw the result of both.
    assert seen == [("A", {"n": "a"})]
    assert str(soup) == '<A n="a" seen="yes">x</A>'


def test_renamed_tags_nest_and_close_correctly():
    # Every <b> becomes an <i>, next to genuine <i> tags. Closing tags must
    # close the tag they belong to, not whichever tag has the new name.
    replacer = SoupReplacer(
        name_xformer=lambda tag: "i" if tag.name == "b" else tag.name
    )
    soup = BeautifulSoup(
        "<p><b>1<i>2</i>3</b>4<i>5</i></p>", "html.parser", replacer=replacer
    )

    assert str(soup) == "<p><i>1<i>2</i>3</i>4<i>5</i></p>"
    assert soup.p.contents[1] == "4"


def test_xformers_combine_with_pairs_and_void_tags():
    replacer = SoupReplacer(
        "b",
        "strong",
        xformer=lambda tag: tag.attrs.update(seen="1"),
        name_xformer=lambda tag: "span" if tag.name == "br" else tag.name,
    )
    soup = BeautifulSoup("<b>x</b><br/>y", "html.parser", replacer=replacer)

    assert soup.find("strong")["seen"] == "1"
    # br was renamed, so it is no longer a self-closing tag.
    assert str(soup.find("span")) == '<span seen="1"></span>'
    assert soup.find("br") is None
