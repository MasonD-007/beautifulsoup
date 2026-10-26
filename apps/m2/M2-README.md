# Milestone-2

Run the apps from `apps/m2/` (Python 3.10+, `pip install -e . lxml` from the repo root; lxml is needed for the XML files):

```
python task2.py <file>   # hyperlinks, SoupStrainer("a")
python task3.py <file>   # all tags, SoupStrainer(True)
python task4.py <file>   # tags with id, SoupStrainer(id=True)
python task6.py <file>   # <b> -> <blockquote> during parsing, SoupReplacer
```

## Part 1: SoupStrainer timings (M1 data, Python 3.13, macOS)

| file | size | task2 (`a`) | task3 (all tags) | task4 (`id`) |
|---|---|---|---|---|
| python_org.html | 52 KB | 0.01s | 0.01s | 0.01s |
| nasa.xml | 25 MB | 1.43s | 5.05s | 1.55s |
| whatwg_html_spec.html | 15.7 MB | 2.15s | 8.48s | 2.62s |
| treebank_e.xml | 86 MB | 6.99s | 28.04s | 8.16s |

Task 3 keeps every tag, so the strainer saves little there; tasks 2 and 4 keep only a small
subset of nodes and are much cheaper. `dblp.xml` (5.3 GB) was not tried with these apps.

## Part 2: Where the API is defined (original, unmodified source)

Line numbers refer to the original source as downloaded, before any Milestone-2 changes.

| API used | File | Line |
|---|---|---|
| `BeautifulSoup(...)` constructor | `bs4/__init__.py` | 209 (`class BeautifulSoup` at 133) |
| `parse_only=` argument (handled in constructor) | `bs4/__init__.py` | 214 (stored at 437) |
| `SoupStrainer` class / `__init__` | `bs4/filter.py` | 313 / 345 |
| `SoupStrainer.allow_tag_creation` (used while parsing) | `bs4/filter.py` | 580 |
| `SoupStrainer.allow_string_creation` | `bs4/filter.py` | 621 |
| `ElementFilter` (base class of `SoupStrainer`) | `bs4/filter.py` | 43 |
| `soup.prettify()` | `bs4/element.py` | 2601 (`Tag.prettify`) |
| `soup.find_all(...)` | `bs4/element.py` | 2715 (`Tag.find_all`, calls `_find_all` at 1079) |
| `find_parent(...)` | `bs4/element.py` | 992 (`PageElement.find_parent`) |
| `tag.parents` | `bs4/element.py` | 1215 (`PageElement.parents`) |
| `tag.get("href")` | `bs4/element.py` | 2160 (`Tag.get`) |
| `tag["id"]` (read) | `bs4/element.py` | 2203 (`Tag.__getitem__`) |
| `p["class"] = ...` (write) | `bs4/element.py` | 2223 (`Tag.__setitem__`) |
| `tag.name` (set in `Tag.__init__`; renamed by assignment) | `bs4/element.py` | 1648 (`Tag.__init__` at 1618; `class Tag` at 1569) |
| `soup.get_text(...)` | `bs4/element.py` | 524 (`PageElement.get_text`) |

Parse-time hooks `SoupReplacer` plugs into (original lines): `BeautifulSoup.handle_starttag`
`bs4/__init__.py:987`, `BeautifulSoup.handle_endtag` `bs4/__init__.py:1053`.

## Part 3: SoupReplacer

`SoupReplacer(og_tag, alt_tag)` lives in `bs4/filter.py` next to `SoupStrainer` and is exported
from `bs4`. Usage:

```python
b_to_blockquote = SoupReplacer("b", "blockquote")
print(BeautifulSoup(html_doc, replacer=b_to_blockquote).prettify())
```

Changes:
- `bs4/filter.py`: new `SoupReplacer` class (`replace(name)` returns `alt_tag` for `og_tag`).
- `bs4/__init__.py`: new `replacer=` constructor argument, stored as `self.replacer`;
  `handle_starttag` renames the tag before creating it, and `handle_endtag` applies the same
  rename so the end tag pops the renamed tag. Supported builders: `html.parser`, `lxml` (HTML)
  and `xml`, because they all call `handle_starttag`/`handle_endtag`. `html5lib` is **not**
  supported: it builds its own tree and hands it over, so the replacer has no effect. If `parse_only` is also given, the strainer matches on
  the original name and the replacer renames afterward.
- Tests: `bs4/tests/test_soup_replacer.py` (2 test functions; one runs under `html.parser` and `lxml`).
  The full suite (with lxml and html5lib installed) has 7 failures
  (3 in `test_fuzz.py`, `test_rejected_input`, `test_real_xhtml_document`,
  `test_processing_instruction`, `test_out_of_range_entity`); the same 7 fail on the untouched
  source, and the 3 new tests pass (825 passed vs 822 before).
- App: `task6.py` (M1 task 6 via `SoupReplacer`). On `whatwg_html_spec.html` it produced
  1067 `<blockquote>` and no `<b>` in 10.99s.
