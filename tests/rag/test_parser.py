import pytest
from pathlib import Path
import tempfile
import shutil

from rag.parser import DiaryParser


class TestDiaryParser:
    """Test suite for DiaryParser class."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def sample_diary_content(self):
        """Sample diary content for testing."""
        return """# Goals
- [ ] Complete project documentation
- [x] Review code changes

# Notes
## Monday
- Had team meeting
- Discussed project requirements
- Started implementation

## Tuesday
- Fixed critical bugs
- Updated dependencies

# Tasks
- Update README file
- Prepare presentation slides
"""

    @pytest.fixture
    def parser_with_data(self, temp_dir, sample_diary_content):
        """Create DiaryParser with sample data."""
        # Create test markdown file
        diary_file = temp_dir / "test_diary.md"
        diary_file.write_text(sample_diary_content)

        # Create non-markdown file (should be ignored)
        text_file = temp_dir / "notes.txt"
        text_file.write_text("This should be ignored")

        return DiaryParser(temp_dir)

    def test_init_valid_path(self, temp_dir):
        """Test DiaryParser initialization with valid path."""
        parser = DiaryParser(temp_dir)
        assert parser._diary_folder == temp_dir

    def test_init_with_string_path(self, temp_dir):
        """Test DiaryParser initialization with string path."""
        parser = DiaryParser(temp_dir)
        # Should work since Path() accepts strings
        assert isinstance(parser._diary_folder, (Path, str))

    def test_parse_empty_directory(self, temp_dir):
        """Test parsing an empty directory returns empty list."""
        parser = DiaryParser(temp_dir)
        result = parser.parse()
        assert result == []

    def test_parse_directory_no_markdown_files(self, temp_dir):
        """Test parsing directory with no markdown files returns empty list."""
        # Create non-markdown files
        (temp_dir / "notes.txt").write_text("Some text")
        (temp_dir / "data.json").write_text("{}")

        parser = DiaryParser(temp_dir)
        result = parser.parse()
        assert result == []

    def test_parse_single_markdown_file(self, parser_with_data):
        """Test parsing a single markdown file."""
        result = parser_with_data.parse()

        # Should return list of dict objects
        assert isinstance(result, list)
        assert all(isinstance(doc, dict) for doc in result)
        assert len(result) > 0

    def test_parse_documents_contain_metadata(self, parser_with_data):
        """Test that parsed documents contain proper metadata."""
        result = parser_with_data.parse()

        for doc in result:
            assert "filename" in doc
            assert doc["filename"] == "test_diary.md"

    def test_parse_documents_with_categories(self, parser_with_data):
        """Test that documents contain category metadata from H1 headers."""
        result = parser_with_data.parse()

        # Find documents with categories
        docs_with_categories = [doc for doc in result if "Category" in doc]
        assert len(docs_with_categories) > 0

        # Check that we have expected categories
        categories = {doc["Category"] for doc in docs_with_categories}
        expected_categories = {"Goals", "Notes", "Tasks"}
        assert categories.intersection(expected_categories)

    def test_parse_documents_with_days(self, parser_with_data):
        """Test that documents contain day metadata from H2 headers."""
        result = parser_with_data.parse()

        # Find documents with days
        docs_with_days = [doc for doc in result if "Day of Week" in doc]
        assert len(docs_with_days) > 0

        # Check that we have expected days
        days = {doc["Day of Week"] for doc in docs_with_days}
        expected_days = {"Monday", "Tuesday"}
        assert days.intersection(expected_days)

    def test_parse_content_structure(self, parser_with_data):
        """Test that document content is properly structured."""
        result = parser_with_data.parse()

        # All documents should have non-empty content
        assert all(doc["text"].strip() for doc in result)

    def test_parse_multiple_markdown_files(self, temp_dir):
        """Test parsing multiple markdown files."""
        # Create multiple markdown files
        file1_content = """# Category1
- Item 1
- Item 2"""

        file2_content = """# Category2
## Monday
- Different item
"""

        (temp_dir / "diary1.md").write_text(file1_content)
        (temp_dir / "diary2.md").write_text(file2_content)

        parser = DiaryParser(temp_dir)
        result = parser.parse()

        # Should have documents from both files
        filenames = {doc["filename"] for doc in result}
        assert "diary1.md" in filenames
        assert "diary2.md" in filenames

    def test_parse_file_with_mixed_content(self, temp_dir):
        """Test parsing file with mixed content (headers, bullets, regular text)."""
        content = """# Work
## Monday
Regular text without bullet
- Bullet point item
More regular text
- Another bullet point

## Tuesday
- Tuesday item
Final text
"""

        (temp_dir / "mixed.md").write_text(content)
        parser = DiaryParser(temp_dir)
        result = parser.parse()

        assert len(result) > 0
        # Should have documents with both Category and Day metadata
        docs_with_both = [
            doc
            for doc in result
            if "Category" in doc and "Day of Week" in doc
        ]
        assert len(docs_with_both) > 0

    def test_parse_file_with_no_headers(self, temp_dir):
        """Test parsing file with no headers."""
        content = """- Just some bullet points
- Without any headers
Regular text here too
"""

        (temp_dir / "no_headers.md").write_text(content)
        parser = DiaryParser(temp_dir)
        result = parser.parse()

        assert len(result) > 0
        # Documents should have filename but no Category or Day metadata
        for doc in result:
            assert "filename" in doc
            assert "Category" not in doc
            assert "Day of Week" not in doc

    def test_parse_empty_markdown_file(self, temp_dir):
        """Test parsing an empty markdown file."""
        (temp_dir / "empty.md").write_text("")
        parser = DiaryParser(temp_dir)
        result = parser.parse()

        # Should handle empty file gracefully
        assert isinstance(result, list)

    def test_parse_handles_whitespace_in_headers(self, temp_dir):
        """Test that parser handles extra whitespace in headers."""
        content = """#   Goals   
- Item with spaced header

##   Monday   
- Item with spaced day header
"""

        (temp_dir / "spaced.md").write_text(content)
        parser = DiaryParser(temp_dir)
        result = parser.parse()

        # Should strip whitespace from metadata
        categories = {doc.get("Category") for doc in result}
        days = {doc.get("Day of Week") for doc in result}

        assert "Goals" in categories
        assert "Monday" in days
