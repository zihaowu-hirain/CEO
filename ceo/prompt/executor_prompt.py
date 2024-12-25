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
            "precondition": "Below is a tool(ability) shown at <tool(ability)> "
                            "and your choice(params) for using the <tool(ability)> is shown at <params(choice)>.",
            "task": "Explain what you are going to do.",
            "output_format": "text",
            "output_example": "I am trying to open calculator.",
            "tool(ability)": self.action.to_dict(),
            "params(choice)": self.params
        }, ensure_ascii=False)
        super().__init__(prompt, ext_context)
        log.debug(f'ExecutorPrompt (before): {self.prompt}')

    def explain(self, model: BaseChatModel, stream: bool = False) -> str | Iterator:
        if stream:
            return model.stream(self.prompt)
        return model.invoke(self.prompt).content

    def invoke(self, model: BaseChatModel, stream: bool = False) -> str | Iterator:
        result = self.action.__call__(**self.params)
        prompt = json.dumps({
            "precondition": "Below is a tool(ability) shown at <tool(ability)>, "
                            "and your choice(params) for the <tool(ability)> is shown at <params(choice)>, "
                            "and the <result> of your using of this <tool(ability)>.",
            "task": "Explain what you have done, and write down the result detailed. "
                    "The result is shown below at <result>.",
            "output_format": "text",
            "output_contains": [
                "{the_tool(ability)_you_used}",
                "{the_choice_you_made}",
                "{what_you_have_done}"
            ],
            "hint_for_output": 'When you give the response, say "ability" instead of "tool".',
            "output_example": "I wrote a wechat message which says 'Bonjour'. The result is 'success'.",
            "tool(ability)": self.action.to_dict(),
            "params(choice)": self.params,
            "result": str(result)
        }, ensure_ascii=False)
        if len(self.ext_context) > 0:
            prompt = f'{self.ext_context}{self.seperator}{prompt}'
        log.debug(f'ExecutorPrompt (after): {prompt}')
        if stream:
            return model.stream(prompt)
        return model.invoke(prompt).content
