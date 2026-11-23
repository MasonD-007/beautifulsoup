"""Tests for iterating over a BeautifulSoup object, which visits every node."""

import types

import pytest

from bs4 import BeautifulSoup, NavigableString, Tag

HTML = "<p>one <b>bold <i>italic</i></b> two</p><a href='x'>link</a>"


def describe(node):
    return node.name if isinstance(node, Tag) else str(node)


@pytest.mark.parametrize("parser", ["html.parser", "lxml"])
def test_iteration_visits_every_node_in_document_order(parser):
    soup = BeautifulSoup(HTML, parser)
    visited = [describe(node) for node in soup]
    # Parents come before their children, siblings left to right.
    assert visited.index("p") < visited.index("b") < visited.index("i")
    assert visited.index("italic") < visited.index(" two") < visited.index("a")


def test_iteration_matches_descendants_and_includes_nested_nodes():
    soup = BeautifulSoup(HTML, "html.parser")
    assert [id(n) for n in soup] == [id(n) for n in soup.descendants]
    kinds = [type(n) for n in soup]
    assert Tag in kinds and NavigableString in kinds
    # Nested nodes are reached, not just the top-level children.
    assert soup.find("i") in list(soup)
    assert len(list(soup)) > len(soup.contents)


def test_iteration_is_lazy_and_not_a_list():
    soup = BeautifulSoup(HTML, "html.parser")
    iterator = iter(soup)
    assert isinstance(iterator, types.GeneratorType)
    assert iter(iterator) is iterator
    first = next(iterator)
    assert first is soup.contents[0]
    # The generator is resumable: nodes arrive one at a time.
    assert next(iterator) is first.next_element


def test_empty_document_and_independent_iterators():
    assert list(BeautifulSoup("", "html.parser")) == []

    soup = BeautifulSoup("<a>x</a>", "html.parser")
    one, two = iter(soup), iter(soup)
    assert next(one) is next(two)
    assert next(one) == "x"
    assert next(two) == "x"
    assert list(soup) == list(soup)  # re-iterable, no consumed state on the soup


def test_other_tags_still_iterate_over_their_children_only():
    soup = BeautifulSoup(HTML, "html.parser")
    p = soup.p
    assert list(p) == p.contents
    assert len(list(p)) < len(list(p.descendants))
    # The soup itself is still the regular soup object.
    assert isinstance(soup, BeautifulSoup) and soup.find("a")["href"] == "x"
