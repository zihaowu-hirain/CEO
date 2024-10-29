import abc

from langchain_core.language_models import BaseChatModel


class Prompt:
    def __init__(self, prompt: str, ext_context: str = ''):
        self.ext_context = ext_context
        self.prompt = f'{self.ext_context}\n{'-'*5}You are my assistant{'-'*5}\n{prompt}'

    @abc.abstractmethod
    def invoke(self, model: BaseChatModel):
        pass
