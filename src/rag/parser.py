from pathlib import Path

import iterator_chain
from langchain_core.documents import Document
from langchain_text_splitters import MarkdownHeaderTextSplitter


class DiaryParser:
    def __init__(self, diary_folder: Path):
        self._diary_folder = diary_folder
        self._splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=[
                ("#", "Category"),
                ("##", "Day of Week"),
                ("- [ ]", "todo"),
                ("- [x]", "completed todo"),
                ("-", "accomplishment"),
            ],
            strip_headers=True,
        )

    def parse(self) -> list[Document]:
        files = self._diary_folder.iterdir()
        return (
            iterator_chain.from_iterable(files)
            .filter(lambda file: file.suffix == ".md")
            .map(lambda file: self._parse_file(file))
            .flatten()
            .list()
        )

    def _parse_file(self, diary_file_path: Path) -> list[Document]:
        diary_file_content = diary_file_path.read_text()
        return self._splitter.split_text(diary_file_content)
