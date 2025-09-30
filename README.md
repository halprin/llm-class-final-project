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

## Decisions

Outlined below are some of the decisions that I made during the development of this project.

### Over Project Idea

I spent a lot of time this year looking over my engineering diary to remember what I did to fill out the PGP.  So, I
decided to make that easier next year by creating a RAG-based LLM project.

### Using Pinecone for Vector Database

I've had good success with Pinecone in the past, so that was the first reason for using it again here.

One interesting experiment I tried was using Llama 3.1 8B model for embedding.  I had used the Llama 3.2 1B model for
embedding in a previous homework assignment to great effect, but this time the results were subpar with the larger
model.  I would embed a request to send to Pinecone, and the matching results were of low quality.  I switched to using
Pinecone's built-in support for embedding models by using the `llama-text-embed-v2` model, and I got much better
results.

In addition to the embedding model, I also used the `bge-reranker-v2-m3` reranking model.  I decided to fetch a total of
20 documents with reranking returning the 15 best documents.  Given the general size of each document, this doesn't
overflow the model contexts, and gives me the opportunity to ask questions that may require returning many documents. 

Overall, the choice to use Pinecone has worked out well.  Pinecone is straightforward to use, and the ability to have it
do the embedding, along with the reranking, has been a boon to me.

### Using Rouge for Evaluation

I used the rouge evaluation metric because the basis of my project is to summarize entries of my engineering diary.
Rouge is the best fit for this task because it measures the overlap between the generated summary and the original text.

There is no canonical summarization given my evaluation prompts, so I made them up.  Normally I wouldn't put too much
credence behind the rouge1 metric because it just counts whether a single word overlaps, but decided to use it this time
around given the fact that my expected output that I manually generated included the metadata of the entries (e.g.,
filename, day of the week, etc.).  I also used rouge2, rougeL, and rougeLsum because I wanted to see how the model would
perform on different levels of overlap.

You can see the evaluation results in [PR 18](https://github.com/halprin/llm-class-final-project/pull/18).

### Using AWS Bedrock for Model Hosting

I needed access to a number of models, and AWS Bedrock supplies easy access to them in a unified API.  By using AWS
Bedrock, I didn't need to sign-up for a number of different services.  We also already had access to an AWS account for
the class, so this was a natural choice.

### Using Streamlit for GUI

I had a good time using Streamlit for another project and for one of the homework assignments.  I decided to continue my success by using it for this project.

Streamlit makes it straightforward to make a website that automatically interacts with a backend.

### Using Terraform for IaC

I find Terraform to be the best tool for defining infrastructure.  I also have a lot of experience with Terraform.  AWS
CDK has a couple of nicer features but falls down in many more areas.  One of the main reasons being that it doesn't fix
drift, meaning that CDK does not put a resource back to its predefined state in CDK if there are any manual changes
made. 

### Using `us.meta.llama3-2-90b-instruct-v1:0` as the Model

I ended up going with the Llama 3.2 90B model because it did the best in my
[rouge-based evaluation](https://github.com/halprin/llm-class-final-project/pull/18).  It did the best out of seven
models.

- Anthropic Claude Sonnet 4.
- Anthropic Claude Opus 4.1.
- Anthropic Claude Haiku 3.5.
- Deepseek R1.
- Meta Llama 3.2 90B.
- Meta Llama 3.1 8B.
- OpenAI GPT OSS 120B.

See [Using a Different Model](#using-a-different-model) below.

### Using Fake Data

While there is nothing secret in my own engineering diary, it is personal in nature.  I decided to generate some fake
data to fill the vector database.  Some of it is [absolutely wild](./data/2025-08%20(week%2029).md), and I kept it for
comedic sake.  You can view all the fake data in [`./data/`](./data).

## If I Had More Time

### Using a Different Model Through Better Evaluation

I see why the Meta Llama 3.2 90B model won.  It does best at purely parroting out the original documents that came back
from the vector database.  My expected output from the evaluation dataset was mostly filled with the raw data, hence
this model doing best.  Next time, I'd do a better job at making my evaluation dataset.

### Larger Evaluation Dataset

Speaking of the evaluation dataset, I'd make it larger.  Right now it has only three questions/expected output pairs.
The more I add, the more generalized the evaluation would be, and therefore the evaluation would cover more questions of
the data.

### Use the Previous Chat History for Context

Currently, the solution doesn't send back the previous chat history as part of the context.  Each question is its own,
brand-new chat.  Therefore, you can't ask follow-up questions based on the previous chat.  I'd add this next.
