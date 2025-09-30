# llm-class-final-project

Final Project for the LLM Class.

## Usage

### Requirements

There are a few things you need to run this project.

1. Python 3.12.
2. [uv](https://docs.astral.sh/uv/).

### Install

Before you can run the project, you need to install the dependencies.

```shell
uv sync
```

### Run

Finally, to run the project...

```shell
cd ./src/
export PINECONE_API_KEY="{your Pinecone API key}"
PYTHONPATH=. uv run streamlit run ./bin/run_ui.py
```

Notice `{your Pincene API key}`.  You'll need to provide your own Pincene API key.  You can get one for free
[here](https://www.pinecone.io).  In addition to Pinecone, you need access to AWS Bedrock with the
`us.meta.llama3-2-90b-instruct-v1:0` model.  Ensure the AWS credentials are set-up correctly.

## Development

You'll need a few more dependencies to develop this project.

```shell
uv sync --group dev
```

You'll also need [Terraform](https://www.terraform.io/) installed to work with the IaC.

### Python

The primary folder with all the code is `./src/`.

There's a special folder under `./src/` called `./bin/`.  This folder contains all the entrypoints for the project.

- `run_ui.py`: Runs the GUI.  This is the primary entrypoint for the project.
- `load_rag.py`: Loads the data  in `./data/` into the Pinecone vector database.
- `run_evaluate.py`: Evaluates different models.  It depends on a file `./data/evaluation.csv` that contains two
  columns: `prompt` and `expected`.  It is missing from this project because it currently has sensitive information.  At
  some point, it may be converted to use the public, fake data that is currently in `./data`.

### Testing

Unit tests are located in `./tests/`.  They are written using [pytest](https://pytest.org/).

To run the tests, run the following command...

```shell
uv run pytest
```

### DevOps

The Terraform code is located in `./iac/`.  It is written using [Terraform](https://www.terraform.io/).

Make sure you have AWS credentials set-up correctly.  Then, run the following command...

```shell
cd ./iac/
terraform init
terraform apply -var 'pinecone_api_key={your Pinecone API key}'
```

The GitHub Actions are located in `./.github/workflows/`.  There's a workflow for continuous integration and continuous
deployment.
