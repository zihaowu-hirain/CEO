import json
import logging
from collections.abc import Iterator

from langchain_core.language_models import BaseChatModel

from ceo.prompt.prompt import Prompt

log = logging.getLogger('ceo.prompt')


class SelfIntroducePrompt(Prompt):
    def __init__(self, agent: any, ext_context: str = ''):
        prompt = json.dumps({
            "task": "Introduce yourself briefly based on the information provided. "
                    "Only tell what you exactly can do based on your abilities.",
            "information": agent.__repr__(),
            "output_format": "My name is <name>. What can I do: ..."
        }, ensure_ascii=False)
        super().__init__(prompt, ext_context)
        log.debug(f'SelfIntroducePrompt: {self.prompt}')

    def invoke(self, model: BaseChatModel, stream: bool = False) -> str | Iterator:
        if stream:
            return model.stream(self.prompt)
        return model.invoke(self.prompt).content
