from collections.abc import Iterator

from langchain_core.language_models import BaseChatModel

from ceo.action.action import Action
from ceo.prompt.prompt import Prompt


class ExecutorPrompt(Prompt):
    def __init__(self, params: dict, action: Action):
        self.action = action
        self.params = params
        prompt = ('Precondition: Below is a tool and your choice(params) for the tool.\n'
                  'Task: Explain what you are going to do.\n'
                  'Output format: text.\n'
                  'Example output: I am trying to open calculator.\n'
                  f'Tool: {action}\n'
                  f'Params(choice): {params}\n')
        super().__init__(prompt)

    def explain(self, model: BaseChatModel, stream: bool = False) -> str | Iterator:
        if stream:
            return model.stream(self.prompt)
        return model.invoke(self.prompt).content

    def invoke(self, model: BaseChatModel, stream: bool = False) -> str | Iterator:
        result = self.action.function(**self.params)
        prompt = ('Precondition: Below is a tool and the result of your using the tool.\n'
                  'Task: Explain what have you done.\n'
                  'Output format: text.\n'
                  'Example output: I just opened calculator for you.\n'
                  f'Tool: {self.action}\n'
                  f'Result: {result}\n')
        if stream:
            return model.stream(prompt)
        return model.invoke(prompt).content
