import logging
from collections.abc import Iterator

from langchain_core.language_models import BaseChatModel

from ceo.prompt.prompt import Prompt

log = logging.getLogger('ceo.prompt')


class SelfIntroducePrompt(Prompt):
    def __init__(self, agent: any, ext_context: str = ''):
        prompt = ('Task: Introduce yourself briefly base on below information.\n'
                  f'Information: {agent.__repr__()}\n'
                  f'Output format: My name is <name>. What can i do: ...\n')
        super().__init__(prompt, ext_context)
        log.debug(f'SelfIntroducePrompt: {self.prompt}')

    def invoke(self, model: BaseChatModel, stream: bool = False) -> str | Iterator:
        if stream:
            return model.stream(self.prompt)
        return model.invoke(self.prompt).content
