from evaluate import load

from llm import Llm
from rag.database import Database


class Evaluator:
    def __init__(self, model: Llm, dataset: list[dict[str, str]], database: Database):
        self._model = model
        self._database = database
        self._dataset = dataset
        self._metric = load("rouge")

    def evaluate(self):
        expecteds = []
        actuals = []

        for datapoint in self._dataset:
            expecteds.append(datapoint["expected"])

            prompt = datapoint["prompt"]
            retrieved_docs = self._database.retrieve_documents(prompt)

            full_response = ""
            response_stream = self._model.stream(prompt, retrieved_docs)
            for chunk in response_stream:
                full_response += chunk

            actuals.append(full_response)

        metric = self._metric.compute(predictions=actuals, references=expecteds)

        return metric["rougeL"]
