import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "m2"))

from bs4 import BeautifulSoup, SoupReplacer
from common import output_path, parser_for


def add_test_class(tag):
    # xformer: side effects on the tag, no return value.
    if tag.name == "p":
        tag["class"] = "test"


def main():
    if len(sys.argv) != 2:
        sys.exit("usage: python task7.py <file>")
    path = sys.argv[1]
    start = time.perf_counter()
    # Every <p> gets class="test" while the tree is built; no second traversal.
    p_gets_class = SoupReplacer(xformer=add_test_class)
    with open(path, "rb") as f:
        soup = BeautifulSoup(f, parser_for(path), replacer=p_gets_class)
    out = output_path(path, "task7_m3")
    with open(out, "w", encoding="utf-8") as f:
        f.write(soup.prettify())
    print(f"Set class=\"test\" on <p> tags during parsing via xformer; wrote {out} "
          f"in {time.perf_counter() - start:.2f}s")


if __name__ == "__main__":
    main()
