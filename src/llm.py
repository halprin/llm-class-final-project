from langchain_aws import ChatBedrock, ChatBedrockConverse


class Llm:
    def __init__(self):
        self._llm = ChatBedrockConverse(
            model="anthropic.claude-sonnet-4-20250514-v1:0",
            temperature=0.1,
            region_name="us-east-1",
        )

    def inference(self, prompt: str) -> str:
        return self._llm.invoke(prompt)