from pathlib import Path
import logging

from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama

from rag.database import Database
from rag.parser import DiaryParser


def main():
    parser = DiaryParser(Path("data"))
    documents = parser.parse()

    database = Database()
    if not database.has_data():
        logging.info("No data found in database. Adding documents.")
        database.add_documents(documents)

    llm = ChatOllama(model="llama3.1:8b", temperature=0.1)
    system_prompt = (
        "You are providing answers to questions about goals, accomplishments, and tasks in a diary.  "
        "Use only the following entries to answer the question.  Provide which entries you used to answer the question."
        "Diary entries: {context}"
    )
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", "Question: {input}"),
        ]
    )

    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    chain = create_retrieval_chain(database.retriever(), question_answer_chain)

    output = chain.invoke({"input": "Ganba"})
    print(f"Answer: {output['answer']}")
    print()


if __name__ == "__main__":
    main()
