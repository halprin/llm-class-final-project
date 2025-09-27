import logging

import streamlit as st

from rag.database import Database
from llm import Llm


@st.cache_resource
def initialize_llm_components():
    """Initialize and cache the database and LLM components."""
    database = Database()

    llm = Llm()

    return database, llm


def main():
    st.title("📓 Diary Chat Assistant TEST!")
    st.write(
        "Ask questions about goals, accomplishments, and tasks from your diary entries."
    )

    # Initialize components
    database, llm = initialize_llm_components()

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

                # Stream the response
                with st.spinner("Generating response..."):
                    response_stream = llm.stream(prompt, retrieved_docs)

                    for chunk in response_stream:
                        full_response += chunk
                        message_placeholder.markdown(full_response + "▌")

                    message_placeholder.markdown(full_response)

            except Exception as e:
                error_message = f"Sorry, I encountered an error: {str(e)}"
                message_placeholder.markdown(error_message)
                logging.exception(e)
                full_response = error_message

        # Add assistant response to chat history
        st.session_state.messages.append(
            {"role": "assistant", "content": full_response}
        )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
