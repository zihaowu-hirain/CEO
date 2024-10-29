import abc

from langchain_core.language_models import BaseChatModel


class Prompt:
    def __init__(self, prompt: str, ext_context: str = ''):
        self.ext_context = ext_context
        self.prompt = self.ext_context + prompt

    @abc.abstractmethod
    def invoke(self, model: BaseChatModel):
        pass
