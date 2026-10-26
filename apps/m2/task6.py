import sys
import time

from bs4 import BeautifulSoup, SoupReplacer
from common import output_path, parser_for


def main():
    if len(sys.argv) != 2:
        sys.exit("usage: python task6.py <file>")
    path = sys.argv[1]
    start = time.perf_counter()
    # <b> becomes <blockquote> while the tree is built; no second traversal.
    b_to_blockquote = SoupReplacer("b", "blockquote")
    with open(path, "rb") as f:
        soup = BeautifulSoup(f, parser_for(path), replacer=b_to_blockquote)
    out = output_path(path, "task6")
    with open(out, "w", encoding="utf-8") as f:
        f.write(soup.prettify())
    print(f"Replaced <b> with <blockquote> during parsing; wrote {out} "
          f"in {time.perf_counter() - start:.2f}s")


if __name__ == "__main__":
    main()
