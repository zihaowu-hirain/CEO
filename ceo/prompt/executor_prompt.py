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
            "precondition": "Below is an ability shown at <ability> "
                            "and your choice(params) for using the <ability> is shown at <params(choice)>.",
            "task": "Explain what you are going to do.",
            "output_datatype": "text",
            "output_example": "I am trying to open calculator.",
            "ability": self.action.to_dict(),
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
            "precondition": "Below is an ability shown at <ability>, "
                            "your choice(params) for the <ability> is shown at <params(choice)>, "
                            "result of your using of this <ability> is shown at <result>.",
            "task": "Explain what you have done according to <ability>, <result>, and <params(choice)> "
                    "accurately, comprehensively, and briefly.",
            "output_data_type": "text",
            "output_includes": [
                "{ability_just_used}",
                "{choice_just_made}",
                "{result_just_received}"
            ],
            "output_example": "I used the wechat_sender to wrote a wechat message which says 'Bonjour', "
                              "the result shows 'success' which indicates success of wechat message sending.",
            "ability": self.action.to_dict(),
            "params(choice)": self.params,
            "result": str(result)
        }, ensure_ascii=False)
        if len(self.ext_context) > 0:
            prompt = f'{self.ext_context}{self.seperator}{prompt}'
        log.debug(f'ExecutorPrompt (after): {prompt}')
        if stream:
            return model.stream(prompt)
        return model.invoke(prompt).content
