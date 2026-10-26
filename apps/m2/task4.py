import sys
import time

from bs4 import BeautifulSoup, SoupStrainer
from common import parser_for


def main():
    if len(sys.argv) != 2:
        sys.exit("usage: python task4.py <file>")
    path = sys.argv[1]
    start = time.perf_counter()
    with open(path, "rb") as f:
        # Only tags carrying an id attribute are built.
        soup = BeautifulSoup(f, parser_for(path), parse_only=SoupStrainer(id=True))
    tags = soup.find_all(id=True)
    for tag in tags:
        print(tag.name, tag["id"])
    print(f"{len(tags)} tags with an id in {time.perf_counter() - start:.2f}s")


if __name__ == "__main__":
    main()
