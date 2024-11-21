import logging

from langchain_core.language_models import BaseChatModel

from ceo.ability.ability import Ability
from ceo.prompt.prompt import Prompt

log = logging.getLogger('ceo.prompt')


class SchedulerPrompt(Prompt):
    def __init__(self, query: str, actions: list[Ability], ext_context: str = ''):
        self.actions = actions
        prompt = dict()
        for action in self.actions:
            prompt[action.name] = str(action)
        prompt = ('Precondition: Below are the tools you can use (you can only use the following tools). '
                  f'Now there is a user query: "{query}"\n'
                  'Task: What you need to do is to plan your workflow based on the tools and user query.\n'
                  '(User query might contains many steps, '
                  'think carefully about every step and plan your workflow based on your tools)\n'
                  "(User's query might need to use one tool more than once, "
                  'but think carefully about how many times a tool needs to be used based on practical query, '
                  'do not abuse or overuse!)\n'
                  "(Sometimes some of the tools are irrelevant to user's query. Make sure to use tools properly.)\n"
                  'Output format: [{tool1.name}, {tool2.name}, ...] sequential and well-organized with no additional redundant information\n'
                  'Example output: [do_step_one, do_step_two, do_step_three]\n'
                  f'Tools: {prompt}\n')
        super().__init__(prompt, ext_context)
        log.debug(f'SchedulerPrompt: {self.prompt}')

    def invoke(self, model: BaseChatModel) -> list[Ability]:
        results = model.invoke(self.prompt).content
        if not results.startswith('['):
            results = results[results.find('['):]
        if not results.endswith(']'):
            results = results[:results.find(']') + 1]
        results = results[1:-1].split(',')
        _fin_results = list()
        for _a_result in results:
            for action in self.actions:
                if action.name == _a_result.strip():
                    _fin_results.append(action)
        return _fin_results
