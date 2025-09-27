import pytest
from unittest.mock import Mock, patch, MagicMock

from src.evaluator import Evaluator
from src.llm import Llm
from src.rag.database import Database


class TestEvaluator:
    @pytest.fixture
    def mock_model(self):
        """Create a mock Llm model."""
        mock_model = Mock(spec=Llm)
        return mock_model

    @pytest.fixture
    def mock_database(self):
        """Create a mock Database."""
        mock_database = Mock(spec=Database)
        return mock_database

    @pytest.fixture
    def sample_dataset(self):
        """Create a sample dataset for testing."""
        return [
            {
                "prompt": "What are my goals for this week?",
                "expected": "Your goals include completing the project and exercising daily."
            },
            {
                "prompt": "What did I accomplish yesterday?", 
                "expected": "You finished the documentation and attended two meetings."
            }
        ]

    @pytest.fixture
    def mock_metric(self):
        """Create a mock metric object."""
        mock_metric = Mock()
        mock_metric.compute.return_value = {"rougeL": 0.85}
        return mock_metric

    @patch('src.evaluator.load')
    def test_evaluator_init(self, mock_load, mock_model, mock_database, sample_dataset, mock_metric):
        """Test Evaluator initialization."""
        mock_load.return_value = mock_metric
        
        evaluator = Evaluator(mock_model, sample_dataset, mock_database)
        
        assert evaluator._model == mock_model
        assert evaluator._database == mock_database
        assert evaluator._dataset == sample_dataset
        mock_load.assert_called_once_with("rouge")
        assert evaluator._metric == mock_metric

    @patch('src.evaluator.load')
    def test_evaluate_single_datapoint(self, mock_load, mock_model, mock_database, mock_metric):
        """Test evaluation with a single datapoint."""
        mock_load.return_value = mock_metric
        
        # Setup mocks
        mock_database.retrieve_documents.return_value = [
            {"text": "sample document", "category": "goals"}
        ]
        mock_model.stream.return_value = iter(["Your ", "goals ", "are ", "important."])
        
        dataset = [{"prompt": "What are my goals?", "expected": "Your goals are important."}]
        evaluator = Evaluator(mock_model, dataset, mock_database)
        
        # Execute
        result = evaluator.evaluate()
        
        # Verify
        assert result == 0.85
        mock_database.retrieve_documents.assert_called_once_with("What are my goals?")
        mock_model.stream.assert_called_once_with("What are my goals?", [{"text": "sample document", "category": "goals"}])
        mock_metric.compute.assert_called_once_with(
            predictions=["Your goals are important."],
            references=["Your goals are important."]
        )

    @patch('src.evaluator.load')
    def test_evaluate_multiple_datapoints(self, mock_load, mock_model, mock_database, sample_dataset, mock_metric):
        """Test evaluation with multiple datapoints."""
        mock_load.return_value = mock_metric
        
        # Setup mocks
        mock_database.retrieve_documents.side_effect = [
            [{"text": "goals doc", "category": "goals"}],
            [{"text": "accomplishments doc", "category": "tasks"}]
        ]
        mock_model.stream.side_effect = [
            iter(["Your ", "goals ", "include ", "project."]),
            iter(["You ", "finished ", "documentation."])
        ]
        
        evaluator = Evaluator(mock_model, sample_dataset, mock_database)
        
        # Execute
        result = evaluator.evaluate()
        
        # Verify
        assert result == 0.85
        assert mock_database.retrieve_documents.call_count == 2
        assert mock_model.stream.call_count == 2
        
        # Check specific calls
        expected_calls_db = [
            (("What are my goals for this week?",), {}),
            (("What did I accomplish yesterday?",), {})
        ]
        actual_calls_db = [call for call in mock_database.retrieve_documents.call_args_list]
        assert actual_calls_db == expected_calls_db
        
        mock_metric.compute.assert_called_once_with(
            predictions=["Your goals include project.", "You finished documentation."],
            references=["Your goals include completing the project and exercising daily.", 
                       "You finished the documentation and attended two meetings."]
        )

    @patch('src.evaluator.load')
    def test_evaluate_empty_dataset(self, mock_load, mock_model, mock_database, mock_metric):
        """Test evaluation with empty dataset."""
        mock_load.return_value = mock_metric
        
        dataset = []
        evaluator = Evaluator(mock_model, dataset, mock_database)
        
        # Execute
        result = evaluator.evaluate()
        
        # Verify
        assert result == 0.85
        mock_database.retrieve_documents.assert_not_called()
        mock_model.stream.assert_not_called()
        mock_metric.compute.assert_called_once_with(predictions=[], references=[])

    @patch('src.evaluator.load')
    def test_evaluate_empty_stream_response(self, mock_load, mock_model, mock_database, mock_metric):
        """Test evaluation when model returns empty stream."""
        mock_load.return_value = mock_metric
        
        # Setup mocks
        mock_database.retrieve_documents.return_value = [{"text": "sample doc"}]
        mock_model.stream.return_value = iter([])  # Empty stream
        
        dataset = [{"prompt": "test prompt", "expected": "expected response"}]
        evaluator = Evaluator(mock_model, dataset, mock_database)
        
        # Execute
        result = evaluator.evaluate()
        
        # Verify
        assert result == 0.85
        mock_metric.compute.assert_called_once_with(
            predictions=[""],  # Empty string from empty stream
            references=["expected response"]
        )

    @patch('src.evaluator.load')
    def test_evaluate_single_chunk_response(self, mock_load, mock_model, mock_database, mock_metric):
        """Test evaluation when model returns single chunk."""
        mock_load.return_value = mock_metric
        
        # Setup mocks
        mock_database.retrieve_documents.return_value = [{"text": "sample doc"}]
        mock_model.stream.return_value = iter(["Complete response in one chunk"])
        
        dataset = [{"prompt": "test prompt", "expected": "expected response"}]
        evaluator = Evaluator(mock_model, dataset, mock_database)
        
        # Execute
        result = evaluator.evaluate()
        
        # Verify
        assert result == 0.85
        mock_metric.compute.assert_called_once_with(
            predictions=["Complete response in one chunk"],
            references=["expected response"]
        )

    @patch('src.evaluator.load')
    def test_evaluate_preserves_order(self, mock_load, mock_model, mock_database, mock_metric):
        """Test that evaluation preserves order of dataset."""
        mock_load.return_value = mock_metric
        
        # Setup mocks with different responses for each call
        mock_database.retrieve_documents.side_effect = [
            [{"text": "first doc"}],
            [{"text": "second doc"}],
            [{"text": "third doc"}]
        ]
        mock_model.stream.side_effect = [
            iter(["first response"]),
            iter(["second response"]),
            iter(["third response"])
        ]
        
        dataset = [
            {"prompt": "first prompt", "expected": "first expected"},
            {"prompt": "second prompt", "expected": "second expected"},
            {"prompt": "third prompt", "expected": "third expected"}
        ]
        evaluator = Evaluator(mock_model, dataset, mock_database)
        
        # Execute
        result = evaluator.evaluate()
        
        # Verify order is preserved
        assert result == 0.85
        mock_metric.compute.assert_called_once_with(
            predictions=["first response", "second response", "third response"],
            references=["first expected", "second expected", "third expected"]
        )

    @patch('src.evaluator.load')
    def test_stream_concatenation(self, mock_load, mock_model, mock_database, mock_metric):
        """Test that stream chunks are properly concatenated."""
        mock_load.return_value = mock_metric
        
        # Setup mocks
        mock_database.retrieve_documents.return_value = [{"text": "sample doc"}]
        mock_model.stream.return_value = iter(["Hello", " ", "world", "!", " ", "How", " ", "are", " ", "you?"])
        
        dataset = [{"prompt": "test", "expected": "Hello world! How are you?"}]
        evaluator = Evaluator(mock_model, dataset, mock_database)
        
        # Execute
        result = evaluator.evaluate()
        
        # Verify concatenation
        assert result == 0.85
        mock_metric.compute.assert_called_once_with(
            predictions=["Hello world! How are you?"],
            references=["Hello world! How are you?"]
        )
