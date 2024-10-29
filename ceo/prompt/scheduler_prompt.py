from langchain_core.language_models import BaseChatModel

from ceo.action.action import Action
from ceo.prompt.prompt import Prompt


class SchedulerPrompt(Prompt):
    def __init__(self, query: str, actions: list[Action]):
        self.actions = actions
        prompt = dict()
        for action in self.actions:
            prompt[action.name] = str(action)
        prompt = ('Precondition: Below are the tools you can use (you can only use the following tools). '
                  f'Now there is a user query: "{query}"\n'
                  'Task: What you need to do is to plan your workflow based on the tools you have to accomplish the user query '
                  '(make sure your use of tools is appropriate)\n'
                  'Output format: [{tool1.name}, {tool2.name}, ...] sequential and well-organized with no additional redundant information\n'
                  'Example output: [do_step_one, do_step_two, do_step_three]\n'
                  f'Tools: {prompt}\n')
        super().__init__(prompt)

    def invoke(self, model: BaseChatModel) -> list[Action]:
        results = model.invoke(self.prompt)
        results = results.content[1:-1].split(',')
        _fin_results = list()
        for _a_result in results:
            for action in self.actions:
                if action.name == _a_result.strip():
                    _fin_results.append(action)
        return _fin_results
