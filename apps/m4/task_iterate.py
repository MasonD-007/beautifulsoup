import sys

from bs4 import BeautifulSoup, Tag


def main():
    if len(sys.argv) != 2:
        sys.exit("usage: python task_iterate.py <file>")
    with open(sys.argv[1], "rb") as f:
        soup = BeautifulSoup(f, "html.parser")
    tags = strings = 0
    for node in soup:
        if isinstance(node, Tag):
            tags += 1
        else:
            strings += 1
    print(f"visited {tags} tags and {strings} strings")


if __name__ == "__main__":
    main()
