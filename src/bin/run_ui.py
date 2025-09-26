import logging
import os
import sys
from typing import Any

# add the current working directory to the Python path
cwd = os.getcwd()
if cwd not in sys.path:
    sys.path.insert(0, cwd)

import streamlit as st
import iterator_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_aws import ChatBedrockConverse
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate

from rag.database import Database


@st.cache_resource
def initialize_llm_components():
    """Initialize and cache the database and LLM components."""
    database = Database()

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

    return database, question_answer_chain


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


def main():
    st.title("📓 Diary Chat Assistant")
    st.write("Ask questions about goals, accomplishments, and tasks from your diary entries.")

    # Initialize components
    database, question_answer_chain = initialize_llm_components()

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # React to user input
    if prompt := st.chat_input("What would you like to know about your diary entries?"):
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            try:
                # Retrieve documents
                with st.spinner("Retrieving relevant diary entries..."):
                    retrieved_docs = database.retrieve_documents(prompt)
                    retrieved_docs = convert_pinecone_to_langchain(retrieved_docs)

                # Stream the response
                with st.spinner("Generating response..."):
                    response_stream = question_answer_chain.stream({
                        "context": retrieved_docs, 
                        "input": prompt
                    })
                    
                    for chunk in response_stream:
                        full_response += chunk
                        message_placeholder.markdown(full_response + "▌")
                    
                    message_placeholder.markdown(full_response)
                    
            except Exception as e:
                error_message = f"Sorry, I encountered an error: {str(e)}"
                message_placeholder.markdown(error_message)
                full_response = error_message
            
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": full_response})


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
