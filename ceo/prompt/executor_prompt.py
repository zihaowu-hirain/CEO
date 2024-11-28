import json
import logging
from collections.abc import Iterator

from langchain_core.language_models import BaseChatModel

from ceo.ability.ability import Ability
from ceo.prompt.prompt import Prompt

log = logging.getLogger('ceo.prompt')


class ExecutorPrompt(Prompt):
    def __init__(self, params: dict, action: Ability, ext_context: str = ''):
        self.action = action
        self.params = params
        prompt = json.dumps({
            "precondition": "Below is a tool and your choice (params) for using this tool.",
            "task": "Explain what you are going to do.",
            "output_format": "text",
            "output_example": "I am trying to open calculator.",
            "tool": action.__repr__(),
            "params (choice)": params
        }, ensure_ascii=False)
        super().__init__(prompt, ext_context)
        log.debug(f'ExecutorPrompt (before): {self.prompt}')

    def explain(self, model: BaseChatModel, stream: bool = False) -> str | Iterator:
        if stream:
            return model.stream(self.prompt)
        return model.invoke(self.prompt).content

    def invoke(self, model: BaseChatModel, stream: bool = False) -> str | Iterator:
        result = self.action.function(**self.params)
        prompt = json.dumps({
            "precondition": "Below is a tool, your choice (params) for the tool, "
                            "and the result of your using of this tool.",
            "task": "Explain what you have done, and write down the result detailed. "
                    "The result is shown below at [result].",
            "output_format": "text",
            "output_contains": [
                "{the_tool(ability)_you_used}",
                "{the_choice_you_made}",
                "{what_you_have_done}"
            ],
            "hint_for_output": 'When you give the response, say "ability" instead of "tool".',
            "output_example": "I wrote a wechat message which says 'Bonjour'. The result is 'success'.",
            "tool": self.action,
            "params (choice)": self.params,
            "result": result
        }, ensure_ascii=False)
        prompt = f'{self.ext_context}{self.seperator}{prompt}'
        log.debug(f'ExecutorPrompt (after): {prompt}')
        if stream:
            return model.stream(prompt)
        return model.invoke(prompt).content
