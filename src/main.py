from pathlib import Path
import logging
from typing import Any

import iterator_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_aws import ChatBedrockConverse
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate

from rag.database import Database
from rag.parser import DiaryParser


def main():
    database = Database()
    if not database.has_data():
        logging.info("No data found in database. Adding documents.")
        parser = DiaryParser(Path("data"))
        documents = parser.parse()
        database.add_documents(documents)

    llm = ChatBedrockConverse(
        model="global.anthropic.claude-sonnet-4-20250514-v1:0",
        temperature=0.1,
        region_name="us-east-1",
    )

    system_prompt = (
        "You are providing answers to questions about goals, accomplishments, and tasks in a diary.  "
        "Use only the following entries to answer the question.  Provide which entries, their category, their day of week, and filename you used to answer the question."
        "Diary entries: {context}"
    )
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", "Question: {input}"),
        ]
    )

    document_prompt = PromptTemplate(
        template="content: {page_content}, category: {Category}, day: {Day of Week}, filename: {filename}",
        input_variables=["page_content", "Category", "Day of Week", "filename"],
    )

    question_answer_chain = create_stuff_documents_chain(
        llm, prompt, document_prompt=document_prompt
    )

    query = "What did I do that involved Ganba?"

    logging.info(f"Query: {query}")
    logging.info("Retrieving documents...")
    retrieved_docs = database.retrieve_documents(query)

    retrieved_docs = convert_pinecone_to_langchain(retrieved_docs)

    logging.info("Running inference...")
    output = question_answer_chain.invoke({"context": retrieved_docs, "input": query})
    print(output)
    print()


def convert_pinecone_to_langchain(
    pinecone_dictionaries: list[dict[str, Any]],
) -> list[Document]:
    return (
        iterator_chain.from_iterable(pinecone_dictionaries)
        .map(convert_single_pinecone_to_langchain)
        .list()
    )


def convert_single_pinecone_to_langchain(
    pinecone_dictionary: dict[str, Any],
) -> Document:
    page_content = pinecone_dictionary["fields"]["text"]
    metadata = pinecone_dictionary["fields"]
    del metadata["text"]

    return Document(page_content=page_content, metadata=metadata)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
