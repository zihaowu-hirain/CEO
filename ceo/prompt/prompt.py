import abc

from langchain_core.language_models import BaseChatModel


class Prompt:
    def __init__(self, prompt: str, ext_context: str = ''):
        self.seperator = f'\n{'-'*5}You are my assistant{'-'*5}\n'
        self.ext_context = ext_context
        self.prompt = f'{self.ext_context}{self.seperator}{prompt}'

    @abc.abstractmethod
    def invoke(self, model: BaseChatModel):
        pass
