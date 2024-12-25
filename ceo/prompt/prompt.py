import abc

from langchain_core.language_models import BaseChatModel


class Prompt:
    def __init__(self, prompt: str, ext_context: str = ''):
        self.__seperator = f"\n{'-'*6}\n"
        self.ext_context = ext_context
        self.prompt = prompt
        if len(self.ext_context) > 0:
            self.prompt = f'{self.ext_context}{self.__seperator}{prompt}'

    @abc.abstractmethod
    def invoke(self, model: BaseChatModel):
        pass

    @property
    def seperator(self) -> str:
        return self.__seperator
