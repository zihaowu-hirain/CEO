import logging
from collections.abc import Iterator

from langchain_core.language_models import BaseChatModel

from ceo.action.action import Action
from ceo.prompt.prompt import Prompt

log = logging.getLogger('ceo.prompt')


class ExecutorPrompt(Prompt):
    def __init__(self, params: dict, action: Action, ext_context: str = ''):
        self.action = action
        self.params = params
        prompt = ('Precondition: Below is a tool and your choice(params) for the tool.\n'
                  'Task: Explain what you are going to do.\n'
                  'Output format: text.\n'
                  'Example output: I am trying to open calculator.\n'
                  f'Tool: {action}\n'
                  f'Params(choice): {params}\n')
        super().__init__(prompt, ext_context)
        log.debug(f'Executor prompt(before): {self.prompt}')

    def explain(self, model: BaseChatModel, stream: bool = False) -> str | Iterator:
        if stream:
            return model.stream(self.prompt)
        return model.invoke(self.prompt).content

    def invoke(self, model: BaseChatModel, stream: bool = False) -> str | Iterator:
        result = self.action.function(**self.params)
        prompt = ('Precondition: Below is a tool, your choice(params) for the tool, '
                  'and the result of your using the tool.\n'
                  'Task: Explain what you have done, and write down the result detailed. '
                  '(The result is shown below at [Result])\n'
                  'Output format: text.\n'
                  'Output contains: {the_choice_you_made}, {what_you_have_done}\n'
                  'Output example: I wrote a wechat message which says "Bonjour". The result is "success"\n'
                  f'Tool: {self.action}\n'
                  f'Params(choice): {self.params}\n'
                  f'Result: {result}\n')
        prompt = f'{self.ext_context}{self.seperator}{prompt}'
        log.debug(f'Executor prompt(after): {prompt}')
        if stream:
            return model.stream(prompt)
        return model.invoke(prompt).content
