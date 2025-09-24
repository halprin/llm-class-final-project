from pathlib import Path

from rag.database import Database
from rag.parser import DiaryParser


def main():
    parser = DiaryParser(Path("data"))
    documents = parser.parse()

    database = Database()
    database.add_documents(documents)


if __name__ == "__main__":
    main()
