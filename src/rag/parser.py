import itertools
import logging
from pathlib import Path
import re
from typing import Optional

import iterator_chain
from langchain_core.documents import Document


class DiaryParser:
    def __init__(self, diary_folder: Path):
        self._diary_folder = diary_folder

    def parse(self) -> list[Document]:
        logging.info(f"Parsing diary from {self._diary_folder}")

        files = self._diary_folder.iterdir()
        list_of_list_of_documents = (
            iterator_chain.from_iterable(files)
            .filter(lambda file: file.suffix == ".md")
            .map(lambda file: self._parse_file(file))
            .list()
        )

        # flatten
        return list(itertools.chain.from_iterable(list_of_list_of_documents))

    def _parse_file(self, diary_file_path: Path) -> list[Document]:
        logging.info(f"Parsing file {diary_file_path}")

        text = diary_file_path.read_text()
        lines = text.splitlines()

        docs: list[Document] = []
        current_category: Optional[str] = None  # H1
        current_day: Optional[str] = None  # H2
        content = ""

        h1_re = re.compile(r"^#\s+(.*)$")
        h2_re = re.compile(r"^##\s+(.*)$")

        for raw_line in lines:
            line = raw_line.rstrip("\n")
            # Header tracking
            m1 = h1_re.match(line)
            if m1:
                current_category = m1.group(1).strip()
                current_day = None  # reset day when a new category starts
                continue
            m2 = h2_re.match(line)
            if m2:
                current_day = m2.group(1).strip()
                continue

            if line.startswith("- "):
                # we're starting a new item, finish the previous one
                if content:
                    metadata = {"filename": diary_file_path.name}
                    if current_category:
                        metadata["Category"] = current_category
                    if current_day:
                        metadata["Day of Week"] = current_day
                    # trim whitespace
                    content = content.strip()
                    docs.append(Document(page_content=content, metadata=metadata))
                content = ""

            content += f"{line}\n"

        if content:
            metadata = {"filename": diary_file_path.name}
            if current_category:
                metadata["Category"] = current_category
            if current_day:
                metadata["Day of Week"] = current_day
            # trim whitespace
            content = content.strip()
            docs.append(Document(page_content=content, metadata=metadata))

        return docs
