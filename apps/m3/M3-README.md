# Milestone-3

`SoupReplacer` now has a second interface: transformer functions that receive each tag while it
is being built.

```python
b_to_blockquote = SoupReplacer(name_xformer=lambda tag: "blockquote" if tag.name == "b" else tag.name)
print(BeautifulSoup(html_doc, replacer=b_to_blockquote).prettify())

def remove_class_attr(tag):
    if "class" in tag.attrs:
        del tag.attrs["class"]

class_deleter = SoupReplacer(xformer=remove_class_attr)
print(BeautifulSoup(html_doc, replacer=class_deleter).prettify())
```

## Changes

- `bs4/filter.py`: `SoupReplacer.__init__(og_tag=None, alt_tag=None, attrs=None, name_xformer=None,
  attrs_xformer=None, xformer=None)`. The M2 positional/`attrs=` form is unchanged. New
  `transform(tag)` applies the functions: `name_xformer` and `attrs_xformer` both see the tag as
  parsed and their results are assigned together; then `xformer(tag)` runs and sees the result.
- `bs4/__init__.py`:
  - `handle_starttag` builds the tag, runs the transformers (`_apply_xformers`) *before* the tag is
    pushed on the stack, so everything downstream (open-tag counters, whitespace/string-container
    handling) sees the final name. After a transformer runs, `can_be_empty_element` and list-valued
    attributes (`class`) are recomputed for the new name and attributes.
  - `handle_endtag`: an end tag carries the name the parser saw, and a function of the tag
    cannot be inverted, so the M2 trick of renaming the end tag no longer works. The soup now
    remembers each open tag's parsed name (`_parsed_names`) and closes the innermost open tag
    parsed under that name. This also fixes `<b>..<i>..</i>..</b>` when `b` is renamed to `i`.
- Builders: `html.parser`, `lxml` and `xml` (they call `handle_starttag`/`handle_endtag`). `html5lib`
  builds its own tree and is not affected, as in M2.
- Tests: six new functions in `bs4/tests/test_soup_replacer.py` (name, attrs, xformer, ordering,
  nesting/closing, combination with pairs and void tags). With the 3 M2 tests, 14 pass; the rest of
  the suite shows the same 7 failures as on the untouched source.
- App: `task7.py` (M1 task 7, `<p>` gets `class="test"`) using `SoupReplacer(xformer=...)`.
  Run from `apps/m3/` (needs `apps/m2/common.py`): `python task7.py <file>`.

## Technical brief: M2 `SoupReplacer(og, alt)` vs. M3 transformers

**M2 (pairs).** Trivially easy to learn and to implement: a dictionary lookup on the name at
start and end tags. It is also cheap to run and easy to reason about, because the replacer sees
only strings. The cost is expressiveness: one tag name to one tag name (plus a fixed attribute
dict). "Rename every `b` *that has a class*", "delete an attribute", "rename based on a parent" are
impossible. Because the input is a name, it never needs a tag object, so it could run before any
construction work.

**M3 (functions of a tag).** Strictly more powerful: the tag gives access to name, attributes,
and (via `tag.parent`) the part of the tree built so far, so conditions, deletion and
computed values all work. The pair form is just sugar for
`name_xformer=lambda t: alt if t.name == og else t.name`. The price:

1. *Closing tags.* With a name-only replacer the end tag could be renamed by the same function.
   With arbitrary functions it cannot, so the soup has to remember each tag's parsed name. This
   is the main implementation cost and a source of subtle bugs (renaming `b` to `i` beside real
   `i` tags).
2. *Derived state.* A tag's `can_be_empty_element`, list-valued attributes and string-container
   status are computed from its name at construction. After a rename they must be recomputed, so
   the transform hook has to know the builder's internals. Anything else added to `Tag.__init__`
   later must be remembered here too.
3. *Mutation timing.* `xformer` can do anything, including `tag.decompose()` or reparenting while the
   parser is mid-stream. Those effects are not defined. The tag is also incomplete when it is seen: it has no children
   yet, so a transformer cannot depend on its contents. I'd document that `xformer` may change
   the tag's name and attributes only.
4. *Cost.* One Python call per tag per function, even for tags the user does not care about; the
   M2 lookup is a dict probe.

**Recommendation.** Ship the M3 shape as the real API and keep the M2 pair as a convenience
constructor over it. Reasons: it covers the cases people actually ask for (attribute cleanup,
conditional renames) without growing the constructor by one flag per use case; the pair form
remains the readable one-liner for the common case. Keep three entry points rather than just
`xformer`: `name_xformer` and `attrs_xformer` are declarative (their effects are known, and
nothing can go wrong beyond the returned value), while `xformer` is the escape hatch. Before upstreaming I would:
(a) restrict `xformer` to name/attrs changes in the docs, or run it after the tag is closed if
children are needed; (b) make `html5lib` fail loudly instead of silently ignoring a replacer;
(c) move the "recompute derived state" step into `Tag` (a `Tag._renamed()` method) so it lives
beside the code that computed the state in the first place.
