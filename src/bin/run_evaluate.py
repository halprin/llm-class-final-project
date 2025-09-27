from unittest.mock import Mock

from evaluator import Evaluator
from llm import Llm
from rag.database import Database


def main():
    mock_model = Mock(spec=Llm)
    mock_database = Mock(spec=Database)

    mock_model.stream.side_effect = [iter(["Nothing"]), iter(["Three things"])]

    dataset = [{
        "prompt": "What did I accomplish on March 6, 2023?",
        "expected": "You did nothing",
    }, {
        "prompt": "What kind of tasks did I with halprin?",
        "expected": "There are three things you did with halprin.  "
                    "March 7, 2023: You reviewed their PR.  "
                    "March 8, 2023: You collaborated with them writing some Terraform.  "
                    "March 9, 2023: halprin asked for you help on a PoC.",
    }]

    evaluator = Evaluator(mock_model, dataset, mock_database)

    evaluator.evaluate()


if __name__ == '__main__':
    main()
