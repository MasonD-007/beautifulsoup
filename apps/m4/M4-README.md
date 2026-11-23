# Milestone-4

`BeautifulSoup` objects are now iterable over every node of the document.

```python
soup = BeautifulSoup(html_doc, "html.parser")
for node in soup:
    print(node)
```

## Changes

- `bs4/__init__.py`: `BeautifulSoup.__iter__` is a generator. It starts at the first child and
  follows each node's `next_element` link (the parser's document-order chain) until it runs
  out. It yields tags and strings, parents before children, left to right.
- `bs4/tests/test_soup_iteration.py`: five test functions (document order, agreement with
  `descendants` and nested nodes, laziness, empty document and independent iterators, other
  tags unchanged). With the `lxml` parametrization that is 6 test cases, all passing. The rest of
  the suite shows the same 4 failures as on the untouched source.
- `apps/m4/task_iterate.py`: counts the tags and strings of a file with `for node in soup`.
  Run: `python task_iterate.py <file>`.

## Technical brief

**No list is built.** The generator holds one reference, `current`. It reads
`current.next_element` *before* yielding, so memory is O(1) regardless of document size, and a
caller may modify or even `extract()` the node it was just handed without breaking the walk. This
is the same trick `Tag.descendants` uses; I did not call `descendants` because that computes the
last descendant up front, and the root has no `next_element` of its own to stop at.

**It changes what `for x in soup` means.** `Tag.__iter__` yields direct children, and
`BeautifulSoup` is a `Tag`, so before this change `for x in soup` visited only top-level nodes.
Now it visits everything, while `len(soup)`, `x in soup` and `soup.contents` still describe direct
children. That inconsistency is the main cost: `list(soup)` and `len(soup)` no longer agree. The
alternative is a separate explicit method, which is clearer but is not what the milestone asked
for. Every other tag keeps the old behaviour, so only the root differs. Nothing inside bs4 relied
on iterating the root (the full suite is unchanged).

**Limits.** The soup itself is not yielded. Mutating the tree ahead of the cursor (inserting
nodes after the current one) is reflected in the walk; removing the *next* node before it is
reached can skip it, since the successor was already read.

**Recommendation.** Keep root iteration as a pre-order walk, but I would document the
`len`/iteration mismatch and, for upstreaming, expose the same generator under a name
(`soup.descendants` already exists) so that code which needs the old child iteration or the new
full walk can say so explicitly.
