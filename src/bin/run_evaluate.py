from unittest.mock import Mock
import csv
import os

import iterator_chain

from evaluator import Evaluator
from llm import Llm
from rag.database import Database


def _load_dataset_from_csv():
    """Load dataset from evaluation.csv file."""
    # csv_path = os.path.join(
    #     os.path.dirname(__file__), "..", "..", "data", "evaluation.csv"
    # )

    csv_path = os.path.join("data", "evaluation.csv")

    dataset = []

    with open(csv_path, "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["prompt"].strip():  # Skip empty rows
                dataset.append({"prompt": row["prompt"], "expected": row["expected"]})

    return dataset


def main():
    model_names = [
        "us.anthropic.claude-sonnet-4-20250514-v1:0",
        "us.anthropic.claude-opus-4-1-20250805-v1:0",
    ]
    iterator_chain.from_iterable_parallel(model_names).for_each(_evaluate_model)


def _evaluate_model(model_name: str):
    print(f"Evaluating model: {model_name}")
    llm = Llm(model_name)
    database = Database()
    dataset = _load_dataset_from_csv()

    evaluator = Evaluator(llm, dataset, database)

    evaluation = evaluator.evaluate()

    print(f"{model_name} evaluation result: {evaluation}")


def demo():
    mock_model = Mock(spec=Llm)
    mock_database = Mock(spec=Database)

    mock_model.stream.side_effect = [iter(["Nothing"]), iter(["Three things"])]

    dataset = [
        {
            "prompt": "What did I accomplish on March 6, 2023?",
            "expected": "You did nothing",
        },
        {
            "prompt": "What kind of tasks did I with halprin?",
            "expected": "There are three things you did with halprin.  "
            "March 7, 2023: You reviewed their PR.  "
            "March 8, 2023: You collaborated with them writing some Terraform.  "
            "March 9, 2023: halprin asked for you help on a PoC.",
        },
    ]

    evaluator = Evaluator(mock_model, dataset, mock_database)

    evaluation = evaluator.evaluate()

    print(f"Evaluation score: {evaluation}")


if __name__ == "__main__":
    main()
