from pathlib import Path

from rag.parser import DiaryParser


def main():
    parser = DiaryParser(Path("data"))
    documents = parser.parse()
    print(documents)


if __name__ == "__main__":
    main()
