FROM ghcr.io/astral-sh/uv:python3.12-alpine

ADD . /app
WORKDIR /app

RUN uv sync --locked

WORKDIR ./src
ENV PYTHONPATH=.
ENV PINECONE_API_KEY=""

EXPOSE 8501

ENTRYPOINT ["uv", "run", "streamlit", "run", "./bin/run_ui.py", "--server.headless", "true"]
