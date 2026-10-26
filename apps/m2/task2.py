import sys
import time

from bs4 import BeautifulSoup, SoupStrainer
from common import parser_for


def main():
    if len(sys.argv) != 2:
        sys.exit("usage: python task2.py <file>")
    path = sys.argv[1]
    start = time.perf_counter()
    with open(path, "rb") as f:
        # Only <a> tags are built; everything else is skipped while parsing.
        soup = BeautifulSoup(f, parser_for(path), parse_only=SoupStrainer("a"))
    links = soup.find_all("a")
    for link in links:
        print(link.get("href"))
    print(f"{len(links)} hyperlinks in {time.perf_counter() - start:.2f}s")


if __name__ == "__main__":
    main()
