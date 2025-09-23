from pathlib import Path

import iterator_chain

from rag.parser import DiaryParser


def main():
    parser = DiaryParser(Path("data"))
    documents = parser.parse()
    iterator_chain.from_iterable(documents).for_each(print)


if __name__ == "__main__":
    main()
