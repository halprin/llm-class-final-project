from pathlib import Path
import logging


from rag.database import Database
from rag.parser import DiaryParser


def main():
    database = Database()

    if database.has_data():
        logging.info("Data already loaded database.  Done.")
        return

    logging.info("No data found in database.  Adding documents.")
    parser = DiaryParser(Path("data"))
    documents = parser.parse()
    database.add_documents(documents)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
