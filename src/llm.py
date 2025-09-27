from typing import Any

import iterator_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_aws import ChatBedrockConverse
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate


class Llm:
    def __init__(self, model_name="global.anthropic.claude-sonnet-4-20250514-v1:0"):
        basle_llm = ChatBedrockConverse(
            model=model_name,
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
            template="content: {page_content}, category: {Category}, day: {Day of Week} , filename: {filename}",
            input_variables=["page_content", "Category", "Day of Week", "filename"],
            partial_variables={"Day of Week": ""},
        )

        self._llm = create_stuff_documents_chain(
            basle_llm, prompt, document_prompt=document_prompt
        )

    def stream(self, query: str, context: list[dict[str, Any]]):
        langchain_context = self._convert_pinecone_to_langchain(context)
        return self._llm.stream({"context": langchain_context, "input": query})

    def _convert_pinecone_to_langchain(
        self,
        pinecone_dictionaries: list[dict[str, Any]],
    ) -> list[Document]:
        return (
            iterator_chain.from_iterable(pinecone_dictionaries)
            .map(self._convert_single_pinecone_to_langchain)
            .list()
        )

    def _convert_single_pinecone_to_langchain(
        self,
        pinecone_dictionary: dict[str, Any],
    ) -> Document:
        page_content = pinecone_dictionary["fields"]["text"]
        metadata = pinecone_dictionary["fields"]
        del metadata["text"]

        return Document(page_content=page_content, metadata=metadata)
