import sys
import time

from bs4 import BeautifulSoup, SoupStrainer
from common import parser_for


def main():
    if len(sys.argv) != 2:
        sys.exit("usage: python task3.py <file>")
    path = sys.argv[1]
    start = time.perf_counter()
    with open(path, "rb") as f:
        # name=True matches every tag; text nodes outside tags are skipped.
        soup = BeautifulSoup(f, parser_for(path), parse_only=SoupStrainer(True))
    tags = soup.find_all(True)
    for tag in tags:
        print(tag.name)
    print(f"{len(tags)} tags in {time.perf_counter() - start:.2f}s")


if __name__ == "__main__":
    main()
