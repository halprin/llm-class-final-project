from unittest.mock import Mock

import iterator_chain

from evaluator import Evaluator
from llm import Llm
from rag.database import Database


def main():
    model_names = ["global.anthropic.claude-sonnet-4-20250514-v1:0", "something else"]
    iterator_chain.from_iterable(model_names).for_each(_evaluate_model)


def _evaluate_model(model_name: str):
    llm = Llm(model_name)
    database = Database()
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

    evaluator = Evaluator(llm, dataset, database)

    evaluation = evaluator.evaluate()

    print(f"{model_name} evaluation result: {evaluation}")


def demo():
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

    evaluation = evaluator.evaluate()

    print(f"Evaluation score: {evaluation}")


if __name__ == '__main__':
    demo()
