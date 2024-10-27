import abc

from langchain_core.language_models import BaseChatModel


class Prompt:
    def __init__(self, prompt: str):
        self.prompt = prompt

    @abc.abstractmethod
    def invoke(self, model: BaseChatModel):
        pass
